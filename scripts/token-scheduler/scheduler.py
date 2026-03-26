#!/usr/bin/env python3
"""
EGOS Token Budget Scheduler
Gerencia tarefas usando Claude Code dentro do budget de tokens por janela de 5 horas.

Lógica de roteamento (últimos 30 min da janela):
  quota restante > 50%  → claude-opus-4-6    (tarefas complexas)
  quota restante > 20%  → claude-sonnet-4-6  (tarefas médias)
  quota restante > 8%   → claude-haiku-4-5   (tarefas simples)
  quota restante <= 8%  → não executa (preserva quota)

Fora dos últimos 30 min:
  Usa o modelo recomendado na task (default: sonnet)

Uso:
  python3 scheduler.py status          → mostra estado atual
  python3 scheduler.py set-quota 14   → atualiza quota usada (%)
  python3 scheduler.py start-window   → registra início da janela
  python3 scheduler.py run            → executa próxima task pendente
  python3 scheduler.py run-loop       → loop contínuo até fim da janela
  python3 scheduler.py list           → lista tasks pendentes
"""

import json
import subprocess
import sys
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "quota-state.json"
TASKS_FILE = BASE_DIR / "pending-tasks.json"

WINDOW_HOURS = 5
LAST_MINUTE_THRESHOLD = 30  # últimos N minutos

# Modelos disponíveis (por custo/capacidade)
MODEL_OPUS   = "claude-opus-4-6"
MODEL_SONNET = "claude-sonnet-4-6"
MODEL_HAIKU  = "claude-haiku-4-5-20251001"

# Limites de quota para seleção de modelo
QUOTA_FOR_OPUS   = 50  # > 50% restante → usa Opus
QUOTA_FOR_SONNET = 20  # > 20% restante → usa Sonnet
QUOTA_FOR_HAIKU  = 8   # > 8%  restante → usa Haiku
# <= 8% → não executa


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_tasks() -> list:
    if not TASKS_FILE.exists():
        return []
    with open(TASKS_FILE) as f:
        data = json.load(f)
        return data.get("tasks", [])


def save_tasks(tasks: list):
    if not TASKS_FILE.exists():
        data = {"tasks": tasks}
    else:
        with open(TASKS_FILE) as f:
            data = json.load(f)
    data["tasks"] = tasks
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_quota_remaining(state: dict) -> float:
    """Retorna % de quota restante (100 - usado)"""
    return 100 - state.get("quota_used_pct", 0)


def get_minutes_until_reset(state: dict) -> Optional[float]:
    """Retorna minutos até reset da janela (None se janela não iniciada)"""
    window_start = state.get("window_start_iso")
    if not window_start:
        return None

    start = datetime.fromisoformat(window_start)
    reset_time = start + timedelta(hours=WINDOW_HOURS)
    now = datetime.now()
    remaining = (reset_time - now).total_seconds() / 60
    return max(0, remaining)


def is_in_last_window(state: dict) -> bool:
    """Verifica se está nos últimos 30 minutos da janela"""
    mins = get_minutes_until_reset(state)
    if mins is None:
        return False
    return mins <= LAST_MINUTE_THRESHOLD


def select_model(state: dict, task_model: str = None) -> Optional[str]:
    """
    Seleciona o modelo a usar baseado em quota e posição na janela.
    Retorna None se não deve executar.
    """
    quota_remaining = get_quota_remaining(state)
    in_last_window = is_in_last_window(state)

    if in_last_window:
        # Últimos 30 min: usa modelo baseado em quota restante
        if quota_remaining > QUOTA_FOR_OPUS:
            return MODEL_OPUS
        elif quota_remaining > QUOTA_FOR_SONNET:
            return MODEL_SONNET
        elif quota_remaining > QUOTA_FOR_HAIKU:
            return MODEL_HAIKU
        else:
            return None  # Quota esgotada, não executa
    else:
        # Fora dos últimos 30 min: usa modelo recomendado da task
        return task_model or MODEL_SONNET


def format_status(state: dict) -> str:
    """Formata status atual para exibição"""
    quota_remaining = get_quota_remaining(state)
    quota_used = state.get("quota_used_pct", 0)
    mins_remaining = get_minutes_until_reset(state)
    in_last = is_in_last_window(state)

    model = select_model(state)

    lines = [
        "=" * 60,
        "EGOS Token Budget Scheduler — Status",
        "=" * 60,
        f"  Quota usada:     {quota_used:.1f}%",
        f"  Quota restante:  {quota_remaining:.1f}%",
        "",
        f"  Janela início:   {state.get('window_start_iso', 'não iniciada')}",
        f"  Mins p/ reset:   {f'{mins_remaining:.0f}min' if mins_remaining is not None else 'N/A'}",
        f"  Últimos 30min:   {'⚠️  SIM' if in_last else 'NÃO'}",
        "",
        f"  Modelo selecionado: {model or '❌ Não executa (quota ≤ 8%)'}",
        "=" * 60,
    ]
    return "\n".join(lines)


def run_task(task: dict, model: str) -> bool:
    """Executa uma task usando claude CLI"""
    task_id = task.get("id", "?")
    prompt = task.get("prompt", "")
    cwd = task.get("cwd", str(BASE_DIR))

    print(f"\n▶ Executando task [{task_id}]: {task.get('title', '?')}")
    print(f"  Modelo: {model}")
    print(f"  Dir:    {cwd}")
    print(f"  Prompt: {prompt[:80]}...")
    print()

    cmd = [
        "claude",
        "--model", model,
        "--print",
        prompt
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=False,
            text=True,
            timeout=300  # 5 min por task
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏱️  Task {task_id} timeout após 5 minutos")
        return False
    except FileNotFoundError:
        print("❌ claude CLI não encontrado. Instale com: npm install -g @anthropic-ai/claude-code")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar task: {e}")
        return False


def cmd_status():
    state = load_state()
    print(format_status(state))
    tasks = load_tasks()
    pending = [t for t in tasks if t.get("status") == "pending"]
    print(f"\n  Tasks pendentes: {len(pending)}")
    for t in pending[:5]:
        model_hint = f"[{t.get('model', 'sonnet')}]"
        priority = f"P{t.get('priority', '?')}"
        print(f"    {priority} {model_hint} {t.get('title', '?')}")
    if len(pending) > 5:
        print(f"    ... e mais {len(pending) - 5}")


def cmd_set_quota(pct: float):
    state = load_state()
    state["quota_used_pct"] = pct
    state["last_updated"] = datetime.now().isoformat()
    save_state(state)
    print(f"✅ Quota atualizada: {pct}% usado ({100-pct:.1f}% restante)")
    print(f"   Modelo selecionado: {select_model(state)}")


def cmd_start_window():
    state = load_state()
    state["window_start_iso"] = datetime.now().isoformat()
    state["quota_used_pct"] = 0
    state["sessions_this_window"] = 0
    state["last_updated"] = datetime.now().isoformat()
    save_state(state)
    reset_at = datetime.now() + timedelta(hours=WINDOW_HOURS)
    print(f"✅ Janela iniciada! Reset em: {reset_at.strftime('%H:%M')} ({WINDOW_HOURS}h)")


def cmd_run():
    """Executa próxima task pendente"""
    state = load_state()
    tasks = load_tasks()
    pending = [t for t in tasks if t.get("status") == "pending"]

    if not pending:
        print("✅ Nenhuma task pendente!")
        return

    # Ordena por prioridade
    pending.sort(key=lambda x: (x.get("priority", 99), x.get("id", "")))
    next_task = pending[0]

    model = select_model(state, next_task.get("model"))
    if not model:
        quota_remaining = get_quota_remaining(state)
        print(f"⛔ Quota insuficiente ({quota_remaining:.1f}% restante ≤ 8%). Aguardando reset.")
        return

    success = run_task(next_task, model)

    # Atualiza status da task
    for t in tasks:
        if t.get("id") == next_task.get("id"):
            t["status"] = "completed" if success else "failed"
            t["completed_at"] = datetime.now().isoformat()
            t["model_used"] = model
            break

    save_tasks(tasks)
    state["sessions_this_window"] = state.get("sessions_this_window", 0) + 1
    state["last_model_used"] = model
    save_state(state)

    status = "✅ Concluída" if success else "❌ Falhou"
    print(f"\n{status}: {next_task.get('title', '?')}")


def cmd_run_loop():
    """Loop contínuo até acabar tasks ou quota"""
    state = load_state()
    tasks = load_tasks()

    print("\n🔁 Modo loop iniciado. Ctrl+C para parar.\n")

    while True:
        state = load_state()
        tasks = load_tasks()
        pending = [t for t in tasks if t.get("status") == "pending"]

        if not pending:
            print("✅ Todas as tasks concluídas!")
            break

        model = select_model(state, pending[0].get("model"))
        if not model:
            quota_remaining = get_quota_remaining(state)
            print(f"⛔ Quota {quota_remaining:.1f}% ≤ 8%. Parando loop.")
            break

        cmd_run()

        # Espera entre tasks
        wait = 30
        print(f"⏸️  Aguardando {wait}s antes da próxima task...")
        time.sleep(wait)


def cmd_list():
    """Lista todas as tasks"""
    tasks = load_tasks()
    if not tasks:
        print("Nenhuma task cadastrada. Crie em pending-tasks.json")
        return

    statuses = {"pending": [], "in_progress": [], "completed": [], "failed": []}
    for t in tasks:
        s = t.get("status", "pending")
        statuses.get(s, statuses["pending"]).append(t)

    print(f"\n{'='*60}")
    print(f"EGOS Task Queue — {len(tasks)} tasks total")
    print(f"{'='*60}")

    icons = {"pending": "⏳", "in_progress": "▶", "completed": "✅", "failed": "❌"}
    for status, items in statuses.items():
        if not items:
            continue
        print(f"\n{icons[status]} {status.upper()} ({len(items)})")
        for t in items:
            p = f"P{t.get('priority', '?')}"
            m = t.get('model', 'sonnet')[:6]
            title = t.get('title', '?')[:50]
            print(f"  [{p}][{m}] {title}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "status":
        cmd_status()
    elif cmd == "set-quota":
        if len(sys.argv) < 3:
            print("Uso: scheduler.py set-quota <pct>")
            return
        cmd_set_quota(float(sys.argv[2]))
    elif cmd == "start-window":
        cmd_start_window()
    elif cmd == "run":
        cmd_run()
    elif cmd == "run-loop":
        cmd_run_loop()
    elif cmd == "list":
        cmd_list()
    else:
        print(f"Comando desconhecido: {cmd}")
        print("Comandos: status, set-quota, start-window, run, run-loop, list")


if __name__ == "__main__":
    main()
