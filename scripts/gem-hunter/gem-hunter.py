#!/usr/bin/env python3
"""
EGOS Gem Hunter — Sistema de Descoberta de Ferramentas
Pesquisa automaticamente GitHub, PyPI, npm por ferramentas que melhoram o EGOS.

Executa via cron:
  0 9 * * 1  python3 /home/enio/egos/scripts/gem-hunter/gem-hunter.py --topic scraping
  0 9 * * 3  python3 /home/enio/egos/scripts/gem-hunter/gem-hunter.py --topic ai-agents
  0 9 * * 5  python3 /home/enio/egos/scripts/gem-hunter/gem-hunter.py --topic security

Tópicos disponíveis:
  scraping    — Cloudflare bypass, TLS impersonation, stealth browsers
  ai-agents   — Agent frameworks, LLM orchestration, function calling
  security    — CVEs, supply chain, zero-days para stack EGOS
  frontend    — React, Next.js, UI components, dashboards
  devops      — Deploy, monitoring, CI/CD improvements

Uso manual:
  python3 gem-hunter.py --topic scraping --output docs/gems/
  python3 gem-hunter.py --all
"""

import json
import sys
import subprocess
import argparse
import urllib.request
import urllib.parse
import os
from datetime import datetime
from pathlib import Path

EGOS_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = EGOS_ROOT / "docs" / "gem-hunter"

# Tópicos de pesquisa e suas queries
TOPICS = {
    "scraping": {
        "description": "Cloudflare bypass, scraping stealth, TLS impersonation",
        "github_queries": [
            "cloudflare bypass python stars:>100",
            "nodriver undetected chrome stars:>200",
            "curl_cffi tls impersonation",
            "camoufox firefox stealth scraping",
            "web scraping anti-bot 2025",
            "playwright stealth bypass 2025",
        ],
        "npm_queries": ["puppeteer-stealth", "playwright-extra", "ghost-cursor"],
        "pypi_queries": ["nodriver", "camoufox", "curl-cffi", "drissionpage"],
        "keywords": ["bypass", "stealth", "undetected", "fingerprint", "scraping"],
    },
    "ai-agents": {
        "description": "Agent frameworks, LLM orchestration, memory systems",
        "github_queries": [
            "LLM agent framework python 2025 stars:>500",
            "multi-agent orchestration 2025",
            "claude anthropic agent sdk examples",
            "autonomous agent tools memory",
        ],
        "npm_queries": ["@langchain/core", "ai-sdk"],
        "pypi_queries": ["langchain", "autogen", "crewai", "pydantic-ai"],
        "keywords": ["agent", "orchestration", "autonomous", "memory", "tool-use"],
    },
    "security": {
        "description": "CVEs, supply chain security, zero-days para stack EGOS",
        "github_queries": [
            "CVE 2025 critical chromium",
            "supply chain attack npm 2025",
            "security scanning python dependencies",
        ],
        "npm_queries": [],
        "pypi_queries": ["safety", "pip-audit"],
        "keywords": ["CVE", "vulnerability", "exploit", "patch", "zero-day"],
    },
    "frontend": {
        "description": "React, Next.js, dashboards, UI components",
        "github_queries": [
            "react dashboard component 2025 stars:>500",
            "next.js 15 features examples",
            "tailwind ui components free",
            "recharts tremor react charts",
        ],
        "npm_queries": ["shadcn-ui", "@tremor/react", "recharts"],
        "pypi_queries": [],
        "keywords": ["dashboard", "chart", "component", "UI", "react"],
    },
    "devops": {
        "description": "Deploy, monitoring, CI/CD, observability",
        "github_queries": [
            "github actions workflow templates 2025",
            "docker compose production best practices",
            "fastapi observability logging 2025",
        ],
        "npm_queries": [],
        "pypi_queries": ["prometheus-client", "structlog", "opentelemetry-sdk"],
        "keywords": ["deploy", "monitoring", "observability", "CI/CD", "docker"],
    },
}

def search_github_api(query: str, max_results: int = 5) -> list:
    """Pesquisa no GitHub via API pública (sem auth, rate-limited)"""
    encoded = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page={max_results}"

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'EGOS-GemHunter/1.0'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for item in data.get('items', [])[:max_results]:
                results.append({
                    'name': item['full_name'],
                    'stars': item['stargazers_count'],
                    'description': item.get('description', ''),
                    'url': item['html_url'],
                    'updated': item.get('updated_at', '')[:10],
                    'language': item.get('language', ''),
                })
            return results
    except Exception as e:
        return [{'error': str(e), 'query': query}]


def search_pypi(package: str) -> dict:
    """Verifica package no PyPI"""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'EGOS-GemHunter/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            info = data.get('info', {})
            return {
                'name': info.get('name', package),
                'version': info.get('version', '?'),
                'summary': info.get('summary', ''),
                'url': f"https://pypi.org/project/{package}/",
                'source': info.get('project_urls', {}).get('Source', ''),
            }
    except Exception as e:
        return {'name': package, 'error': str(e)}


def generate_report(topic: str, findings: dict) -> str:
    """Gera relatório Markdown das descobertas"""
    date = datetime.now().strftime("%Y-%m-%d")
    topic_info = TOPICS.get(topic, {})

    lines = [
        f"# Gem Hunter Report — {topic.upper()} — {date}",
        f"",
        f"> **Tópico:** {topic_info.get('description', topic)}",
        f"> **Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
    ]

    # GitHub results
    github_results = findings.get('github', [])
    if github_results:
        lines += [
            "## GitHub — Repositórios Mais Relevantes",
            "",
            "| Repo | Stars | Lang | Atualizado | Descrição |",
            "|------|-------|------|------------|-----------|",
        ]
        for r in github_results:
            if 'error' in r:
                continue
            name = f"[{r['name']}]({r['url']})"
            lines.append(f"| {name} | ⭐{r['stars']:,} | {r.get('language','')} | {r['updated']} | {r['description'][:60]} |")
        lines.append("")

    # PyPI results
    pypi_results = findings.get('pypi', [])
    if pypi_results:
        lines += [
            "## PyPI — Pacotes Python",
            "",
            "| Pacote | Versão | Descrição |",
            "|--------|--------|-----------|",
        ]
        for r in pypi_results:
            if 'error' in r:
                lines.append(f"| {r['name']} | ❌ não encontrado | — |")
                continue
            name = f"[{r['name']}]({r['url']})"
            lines.append(f"| {name} | {r['version']} | {r.get('summary', '')[:60]} |")
        lines.append("")

    # Recomendações
    lines += [
        "## Recomendações para EGOS",
        "",
        "### Ação Imediata (P0)",
        "- [ ] Avaliar os 3 repos com mais stars desta pesquisa",
        "- [ ] Testar pacote PyPI mais relevante em ambiente isolado",
        "",
        "### Próxima Sprint",
        "- [ ] Integrar melhor ferramenta encontrada no módulo correspondente",
        "- [ ] Atualizar requirements.txt / package.json se aplicável",
        "",
        f"---",
        f"*Auto-gerado por EGOS Gem Hunter v1.0 — {date}*",
    ]

    return "\n".join(lines)


def run_gem_hunt(topic: str) -> Path:
    """Executa hunt para um tópico e salva relatório"""
    print(f"\n🔍 Gem Hunter — Pesquisando: {topic.upper()}")
    print(f"{'='*60}")

    topic_info = TOPICS.get(topic, {})
    if not topic_info:
        print(f"❌ Tópico desconhecido: {topic}")
        print(f"   Tópicos disponíveis: {', '.join(TOPICS.keys())}")
        sys.exit(1)

    findings = {'github': [], 'pypi': []}

    # GitHub searches
    queries = topic_info.get('github_queries', [])
    print(f"\n📦 GitHub ({len(queries)} queries)...")
    seen_repos = set()
    for query in queries[:3]:  # Limita para não exceder rate limit
        print(f"  Pesquisando: {query[:50]}...")
        results = search_github_api(query, max_results=3)
        for r in results:
            if 'error' not in r and r['name'] not in seen_repos:
                seen_repos.add(r['name'])
                findings['github'].append(r)
                print(f"  ✅ {r['name']} (⭐{r['stars']:,})")

    # PyPI searches
    pypi_pkgs = topic_info.get('pypi_queries', [])
    if pypi_pkgs:
        print(f"\n🐍 PyPI ({len(pypi_pkgs)} pacotes)...")
        for pkg in pypi_pkgs:
            result = search_pypi(pkg)
            findings['pypi'].append(result)
            if 'error' not in result:
                print(f"  ✅ {result['name']} v{result['version']}")
            else:
                print(f"  ❌ {pkg}: {result['error']}")

    # Gera e salva relatório
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    report_path = OUTPUT_DIR / f"{topic}-gems-{date}.md"

    report = generate_report(topic, findings)
    report_path.write_text(report, encoding='utf-8')

    print(f"\n📄 Relatório salvo: {report_path}")
    print(f"   GitHub: {len([r for r in findings['github'] if 'error' not in r])} repos encontrados")
    print(f"   PyPI: {len([r for r in findings['pypi'] if 'error' not in r])} pacotes encontrados")

    return report_path


def main():
    parser = argparse.ArgumentParser(description='EGOS Gem Hunter — Descobre ferramentas')
    parser.add_argument('--topic', choices=list(TOPICS.keys()), help='Tópico de pesquisa')
    parser.add_argument('--all', action='store_true', help='Pesquisa todos os tópicos')
    parser.add_argument('--output', help='Diretório de saída (padrão: docs/gem-hunter/)')
    args = parser.parse_args()

    if args.output:
        global OUTPUT_DIR
        OUTPUT_DIR = Path(args.output)

    if args.all:
        reports = []
        for topic in TOPICS:
            report = run_gem_hunt(topic)
            reports.append(report)
        print(f"\n✅ {len(reports)} relatórios gerados em {OUTPUT_DIR}/")
    elif args.topic:
        run_gem_hunt(args.topic)
    else:
        parser.print_help()
        print(f"\nTópicos disponíveis:")
        for name, info in TOPICS.items():
            print(f"  {name:12} — {info['description']}")


if __name__ == "__main__":
    main()
