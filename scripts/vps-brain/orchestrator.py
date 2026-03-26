#!/usr/bin/env python3
"""
EGOS Multi-Provider Orchestrator
Roteia tarefas para o modelo mais barato/adequado disponível:

  ROTA 1 → Alibaba Qwen (grátis, 1M tokens/dia)
    - Análises, resumos, pesquisas, código simples
    - Modelos: qwen-max, qwen-plus, qwen-turbo, qwen-long
    - Imagens: qwen-image-plus (grátis), qwen-image-max

  ROTA 2 → OpenRouter (modelos free tier)
    - google/gemini-2.0-flash-exp:free
    - meta-llama/llama-3.1-70b-instruct:free
    - google/gemini-flash-1.5-8b:free

  ROTA 3 → Claude Code (via credenciais Pro - sem custo extra)
    - Tarefas complexas, arquitetura, code review
    - Usa quota Pro da sessão
    - Comandos claude --print direto

  ROTA 4 → Claude RemoteTrigger (cloud agent)
    - Tasks agendadas que rodam sem VPS online

Uso:
  python3 orchestrator.py --status
  python3 orchestrator.py --run [task_id]
  python3 orchestrator.py --run-loop
  python3 orchestrator.py --image "descrição da imagem"
  python3 orchestrator.py --test-all
"""

import os
import json
import subprocess
import time
import argparse
import http.client
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

BASE_DIR = Path(__file__).parent
JOBS_FILE = BASE_DIR / "jobs" / "pending-tasks.json"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"

# ─── Configuração de Providers ──────────────────────────────────────────────

PROVIDERS: dict[str, Any] = {
    "alibaba": {
        "name": "Alibaba DashScope",
        "api_key_env": "ALIBABA_DASHSCOPE_API_KEY",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "models": {
            "nano":   "qwen-turbo",           # Mais rápido, tarefas triviais
            "fast":   "qwen-plus",            # Rápido, ótimo custo-benefício
            "medium": "qwen-max",             # Forte, balanceado
            "long":   "qwen-long",            # Contexto 10M tokens
            "code":   "qwen-coder-plus",      # Especialista em código
            "vision": "qwen-vl-max",          # Visão + texto
            "math":   "qwen-max-latest",       # Qwen-Max latest (melhor Alibaba 2026)
        },
        "image_models": {
            "fast":    "wanx-v2",             # Geração rápida
            "quality": "wanx-v2-1",           # Alta qualidade
            "edit":    "wanx-sketch-to-image-lite",  # Edição
        },
        "free_daily_tokens": 1_000_000,
        "cost": "free new-user quota / cheap after"
    },
    "openrouter_free": {
        "name": "OpenRouter (Free Tier) — Verified Mar 2026",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            # Verificados funcionando em 2026-03-26
            "nano":   "liquid/lfm-2.5-1.2b-instruct:free",          # Menor, sempre disponível
            "fast":   "google/gemma-3-4b-it:free",                  # Gemma 4B ✅ rápido
            "medium": "google/gemma-3-12b-it:free",                  # Gemma 12B ✅ ★ melhor free
            "smart":  "meta-llama/llama-3.3-70b-instruct:free",      # Llama 70B (rate-limit ~)
            "code":   "google/gemma-3-12b-it:free",                  # Fallback até Qwen3-coder estabilizar
            "reason": "meta-llama/llama-3.3-70b-instruct:free",      # Melhor raciocínio free disponível
            "vision": "nvidia/nemotron-nano-12b-v2-vl:free",         # Vision (Nemotron VL)
            "long":   "google/gemma-3-12b-it:free",                  # Long context fallback
        },
        "cost": "free (rate-limited por modelo)"
    },
    "openrouter_paid": {
        "name": "OpenRouter (Paid — Premium)",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            "fast":   "google/gemini-2.5-flash",                      # Melhor custo/perf pago
            "medium": "deepseek/deepseek-v3",                         # DeepSeek V3 (baratíssimo)
            "code":   "qwen/qwen3-coder-480b-a35b-instruct",          # QWen3 Coder pago
            "smart":  "anthropic/claude-sonnet-4-6",                  # Claude Sonnet via OR
            "genius": "anthropic/claude-opus-4-6",                    # Opus para arquitetura
        },
        "cost": "pay-per-token (muito barato: DeepSeek ~$0.001/1K)"
    },
    "groq": {
        "name": "Groq (Transcription-only — local/residential IPs)",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "models": {
            "nano":   "llama-3.1-8b-instant",     # 750 tok/s, ultra rápido
            "fast":   "llama-3.3-70b-versatile",  # 250 tok/s, forte
            "code":   "llama3-70b-8192",           # Código
            "reason": "deepseek-r1-distill-llama-70b",  # Raciocínio rápido
            # Audio transcription (Whisper) — principal use case
            "transcribe": "whisper-large-v3",
            "transcribe_fast": "whisper-large-v3-turbo",
        },
        "cost": "free tier: 14.4K req/dia — ⚠️ 403 from VPS/datacenter IPs. Use for audio transcription from local/residential only."
    },
    "claude_cli": {
        "name": "Claude Code CLI (Pro quota)",
        "models": {
            "fast":    "claude-haiku-4-5-20251001",
            "medium":  "claude-sonnet-4-6",
            "smart":   "claude-opus-4-6",
        },
        "cost": "Pro subscription (no extra cost)"
    }
}

# ─── Roteamento por complexidade ─────────────────────────────────────────────

ROUTING_RULES = {
    # Por hint de modelo na task
    # NOTE: Groq removed from routing — blocks VPS/datacenter IPs (403). Groq = transcription-only (local use).
    "haiku":  {"provider": "openrouter_free","model": "fast"},    # Gemma-3-4B (fast free)
    "sonnet": {"provider": "openrouter_free","model": "smart"},   # Llama-3.3-70B free
    "opus":   {"provider": "claude_cli",     "model": "smart"},   # Claude Opus local
    # Por complexidade de código
    "code":   {"provider": "openrouter_free","model": "code"},    # Gemma-3-12B (code)
    "reason": {"provider": "openrouter_free","model": "reason"},  # Llama-70B reason
    "vision": {"provider": "openrouter_free","model": "vision"},  # Nemotron VL
    # Defaults por prioridade
    "default_p1": {"provider": "claude_cli",      "model": "medium"},
    "default_p2": {"provider": "openrouter_free", "model": "smart"},
    "default_p3": {"provider": "alibaba",         "model": "fast"},   # was: groq (blocked on VPS)
    "default_p4": {"provider": "alibaba",         "model": "nano"},
}


def get_api_key(provider_name: str) -> str | None:
    env_key = PROVIDERS[provider_name].get("api_key_env")
    if not env_key:
        return None
    return os.environ.get(env_key)


def call_alibaba(prompt: str, model_key: str = "medium") -> dict:
    """Chama Alibaba DashScope via OpenAI-compatible API"""
    api_key = get_api_key("alibaba")
    if not api_key:
        return {"error": "ALIBABA_DASHSCOPE_API_KEY not set", "success": False}

    model = PROVIDERS["alibaba"]["models"][model_key]
    base_url = PROVIDERS["alibaba"]["base_url"]

    try:
        import urllib.request
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }).encode()

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "model": model, "provider": "alibaba"}
    except Exception as e:
        return {"error": str(e), "success": False}


def call_openrouter(prompt: str, model_key: str = "medium") -> dict:
    """Chama OpenRouter free tier"""
    api_key = get_api_key("openrouter_free")
    if not api_key:
        return {"error": "OPENROUTER_API_KEY not set", "success": False}

    model = PROVIDERS["openrouter_free"]["models"][model_key]

    try:
        import urllib.request
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/enioxt/egos",
                "X-Title": "EGOS Orchestrator",
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "model": model, "provider": "openrouter"}
    except Exception as e:
        return {"error": str(e), "success": False}


def call_openrouter_model(prompt: str, model_id: str, provider_key: str = "openrouter_free") -> dict:
    """Chama qualquer modelo OpenRouter por ID completo"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "OPENROUTER_API_KEY not set", "success": False}
    try:
        import urllib.request
        payload = json.dumps({
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/enioxt/egos",
                "X-Title": "EGOS Orchestrator",
            }
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "model": model_id, "provider": "openrouter"}
    except Exception as e:
        return {"error": str(e), "success": False}


def call_groq(prompt: str, model_key: str = "fast") -> dict:
    """Chama Groq — inferência ultra-rápida (750 tok/s), free tier generoso"""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set", "success": False}
    groq_models: dict = PROVIDERS["groq"]["models"]  # type: ignore[index]
    model: str = groq_models[model_key]
    try:
        import urllib.request
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }).encode()
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "model": model, "provider": "groq"}
    except Exception as e:
        return {"error": str(e), "success": False}


def call_claude_cli(prompt: str, model_key: str = "medium", cwd: Optional[str] = None) -> dict:
    """Chama claude CLI usando credenciais Pro (sem custo extra)"""
    model = PROVIDERS["claude_cli"]["models"][model_key]
    try:
        result = subprocess.run(
            ["claude", "--model", model, "--print", prompt],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=cwd
        )
        if result.returncode == 0:
            return {"success": True, "content": result.stdout, "model": model, "provider": "claude_cli"}
        else:
            return {"error": result.stderr, "success": False}
    except FileNotFoundError:
        return {"error": "claude CLI not found", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def generate_image_alibaba(description: str, model: str = "qwen-image-plus") -> dict:
    """Gera imagem via Alibaba Qwen Image API"""
    api_key = get_api_key("alibaba")
    if not api_key:
        return {"error": "ALIBABA_DASHSCOPE_API_KEY not set", "success": False}

    try:
        import urllib.request
        payload = json.dumps({
            "model": model,
            "input": {"prompt": description},
            "parameters": {"size": "1024*1024", "n": 1}
        }).encode()

        req = urllib.request.Request(
            "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            task_id = data.get("output", {}).get("task_id")
            return {"success": True, "task_id": task_id, "status": "queued"}
    except Exception as e:
        return {"error": str(e), "success": False}


def route_task(task: dict) -> dict:
    """Roteia task para o provider correto e executa"""
    model_hint = task.get("model", "sonnet")
    priority = task.get("priority", 5)
    prompt = task.get("prompt", "")
    cwd = task.get("cwd", str(BASE_DIR))
    task_id = task.get("id", "?")

    # Determina rota
    if model_hint in ROUTING_RULES:
        route = ROUTING_RULES[model_hint]
    elif priority <= 2:
        route = ROUTING_RULES["default_p1"]
    elif priority <= 4:
        route = ROUTING_RULES["default_p2"]
    else:
        route = ROUTING_RULES["default_p3"]

    provider = route["provider"]
    model_key = route["model"]

    provider_info: dict = PROVIDERS[provider]  # type: ignore[index]
    model_name: str = provider_info["models"][model_key]
    print(f"  Provider: {provider_info['name']}")
    print(f"  Model: {model_name}")

    # Executa na rota escolhida com fallback em cascata
    if provider == "groq":
        result = call_groq(prompt, model_key)
        if not result["success"]:
            print("  ⚠️  Groq failed, fallback → Alibaba...")
            result = call_alibaba(prompt, "fast")
    elif provider == "alibaba":
        result = call_alibaba(prompt, model_key)
        if not result["success"]:
            print("  ⚠️  Alibaba failed, fallback → OpenRouter...")
            result = call_openrouter(prompt, "fast")
    elif provider == "openrouter_free":
        result = call_openrouter(prompt, model_key)
        if not result["success"]:
            print("  ⚠️  OpenRouter failed, fallback → Alibaba...")
            result = call_alibaba(prompt, "fast")
    elif provider == "openrouter_paid":
        result = call_openrouter_model(prompt, model_name)
        if not result["success"]:
            print("  ⚠️  OpenRouter paid failed, fallback → Claude CLI...")
            result = call_claude_cli(prompt, "medium", cwd)
    elif provider == "claude_cli":
        result = call_claude_cli(prompt, model_key, cwd)
        if not result["success"]:
            print("  ⚠️  Claude CLI failed, fallback → OpenRouter...")
            result = call_openrouter(prompt, "smart")
    else:
        result = {"error": f"Unknown provider: {provider}", "success": False}

    return result


def run_task(task_id: Optional[str] = None) -> bool:
    """Executa próxima task pendente (ou task específica)"""
    if not JOBS_FILE.exists():
        print("❌ jobs/pending-tasks.json não encontrado")
        return False

    with open(JOBS_FILE) as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    pending = [t for t in tasks if t.get("status") == "pending"]

    if not pending:
        print("✅ Nenhuma task pendente")
        return True

    if task_id:
        task = next((t for t in pending if t["id"] == task_id), None)
        if not task:
            print(f"❌ Task {task_id} não encontrada ou não pendente")
            return False
    else:
        pending.sort(key=lambda x: (x.get("priority", 99), x.get("id", "")))
        task = pending[0]

    print(f"\n▶ Task: [{task['id']}] {task['title']}")
    print(f"  Priority: P{task.get('priority','?')}")

    start = time.time()
    result = route_task(task)
    elapsed = time.time() - start

    # Salva resultado
    RESULTS_DIR.mkdir(exist_ok=True)
    result_file = RESULTS_DIR / f"{task['id']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    result_data = {
        "task_id": task["id"],
        "task_title": task["title"],
        "executed_at": datetime.now().isoformat(),
        "elapsed_seconds": float(f"{elapsed:.2f}"),
        **result
    }
    result_file.write_text(json.dumps(result_data, indent=2, ensure_ascii=False))

    # Atualiza status
    for t in tasks:
        if t["id"] == task["id"]:
            t["status"] = "completed" if result["success"] else "failed"
            t["completed_at"] = datetime.now().isoformat()
            t["provider_used"] = result.get("provider", "unknown")
            t["model_used"] = result.get("model", "unknown")

    with open(JOBS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if result["success"]:
        print(f"\n✅ Concluída em {elapsed:.1f}s via {result.get('provider','?')}")
        print(f"   Resultado salvo: {result_file.name}")
        # Preview do output
        content = result.get("content", "")
        if content:
            preview = content[:200].replace('\n', ' ')
            print(f"   Preview: {preview}...")
    else:
        print(f"\n❌ Falhou: {result.get('error', 'unknown error')}")

    return result["success"]


def show_status():
    """Mostra status dos providers e tasks"""
    print("\n" + "="*60)
    print("EGOS Orchestrator — Status")
    print("="*60)

    print("\n📡 PROVIDERS:")
    for name, info in PROVIDERS.items():
        key_env = info.get("api_key_env")
        if key_env:
            has_key = "✅" if os.environ.get(key_env) else "❌ sem key"
        else:
            has_key = "🔐 cred file"
        print(f"  {info['name']:35} {has_key}")

    if JOBS_FILE.exists():
        with open(JOBS_FILE) as f:
            tasks = json.load(f).get("tasks", [])
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        done = sum(1 for t in tasks if t.get("status") == "completed")
        print(f"\n📋 TASKS: {pending} pendentes, {done} concluídas")
    else:
        print("\n📋 TASKS: arquivo não encontrado")

    print("="*60)


def test_all_providers():
    """Benchmark completo — todos os modelos 2026"""
    test_prompt = "Responda em 1 linha: qual seu nome e para que serve?"

    TESTS = [
        # (label, fn, args)
        # Groq: ultra-rápido, mas 403 de VPS/datacenter IPs
        ("Groq / Llama-3.3-70B",               call_groq,            ("fast",)),
        ("Groq / DeepSeek-R1-distil",           call_groq,            ("reason",)),
        # Alibaba: confiável, funciona de VPS
        ("Alibaba / Qwen-Plus",                 call_alibaba,         ("fast",)),
        ("Alibaba / Qwen-Max",                  call_alibaba,         ("medium",)),
        ("Alibaba / Qwen-Max-latest (melhor)",  call_alibaba,         ("math",)),
        # OpenRouter free: Gemma 4B/12B verificados
        ("OpenRouter / Gemma-3-4B (fast free)", call_openrouter,      ("fast",)),
        ("OpenRouter / Gemma-3-12B (mid free)", call_openrouter,      ("medium",)),
        ("OpenRouter / Gemma-3-12B (code)",     call_openrouter,      ("code",)),
        ("OpenRouter / Llama-3.3-70B (reason)", call_openrouter,      ("reason",)),
        ("OpenRouter / Llama-3.3-70B (smart)",  call_openrouter,      ("smart",)),
        ("OpenRouter / Nemotron-VL (vision)",   call_openrouter,      ("vision",)),
        ("OpenRouter / Gemma-3-12B (long ctx)", call_openrouter,      ("long",)),
        # Claude Pro: credenciais OAuth locais
        ("Claude CLI / Haiku-4.5 (Pro)",        call_claude_cli,      ("fast",)),
    ]

    print("\n" + "="*70)
    print("EGOS Model Benchmark — Março 2026")
    print("="*70)
    print(f"{'#':<3} {'Provider / Modelo':<45} {'Status':<8} {'Tempo':>6}  Resposta")
    print("-"*70)

    results = []
    for i, (label, fn, args) in enumerate(TESTS, 1):
        t0 = time.time()
        try:
            r = fn(test_prompt, *args)
        except Exception as e:
            r = {"success": False, "error": str(e)}
        elapsed = time.time() - t0

        ok = bool(r.get("success", False))
        status = "✅" if ok else "❌"
        if ok:
            raw = str(r.get("content", ""))
            preview = raw[:40].replace("\n", " ")  # type: ignore[index]
        else:
            err = str(r.get("error", ""))
            preview = err[:40]  # type: ignore[index]
        print(f"{i:<3} {label:<45} {status:<8} {elapsed:>5.1f}s  {preview}")
        results.append({"label": label, "ok": ok, "elapsed": elapsed, "model": str(r.get("model", ""))})

    passed = sum(1 for r in results if r["ok"])
    print("-"*70)
    print(f"✅ {passed}/{len(TESTS)} modelos responderam")

    # Salva resultado do benchmark
    bench_dir = RESULTS_DIR / "benchmarks"
    bench_dir.mkdir(parents=True, exist_ok=True)
    bench_file = bench_dir / f"benchmark-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    bench_file.write_text(json.dumps(results, indent=2))
    print(f"📄 Benchmark salvo: {bench_file}")


def main():
    parser = argparse.ArgumentParser(description="EGOS Multi-Provider Orchestrator")
    parser.add_argument("--status",     action="store_true", help="Mostra status")
    parser.add_argument("--run",        metavar="TASK_ID",   nargs="?", const="next", help="Executa task")
    parser.add_argument("--run-loop",   action="store_true", help="Executa todas as tasks")
    parser.add_argument("--image",      metavar="PROMPT",    help="Gera imagem via Alibaba")
    parser.add_argument("--test-all",   action="store_true", help="Testa todos os providers")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.run is not None:
        run_task(None if args.run == "next" else str(args.run))
    elif args.run_loop:
        while True:
            if not run_task():
                break
            time.sleep(30)
    elif args.image:
        print(f"🎨 Gerando imagem: {args.image[:50]}...")
        r = generate_image_alibaba(args.image)
        print(r)
    elif args.test_all:
        test_all_providers()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
