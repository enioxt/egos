import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'fs';
import { extname, join, relative, resolve } from 'path';
import { Topics } from '../runtime/event-bus';
import { log, printResult, runAgent, type Finding, type RunContext } from '../runtime/runner';

const IGNORE = new Set(['node_modules', 'dist', '.git', '.next', '.vercel', '.turbo', '.logs']);
const EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.py', '.md', '.json']);
const CODE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.py']);
const SSOT_PATH = 'EGOS core → docs/modules/CHATBOT_SSOT.md';
const CHECKS = [
  ['prompt', 'Modular prompt architecture', ['buildprompt(', 'buildsystemprompt(', 'buildintelinksystemprompt(', 'task_instructions', 'output_format', 'domain_references', 'prompt_registry', 'getpromptconfig(']],
  ['atrian', 'ATRiAN validation', ['atrian', 'validateresponse(', 'filterchunk(']],
  ['pii', 'PII scanner', ['pii-scanner', 'scanforpii(', 'sanitizetext(']],
  ['memory', 'Conversation memory', ['conversation-memory', 'summarizeconversation(', 'buildconversationmemoryblock(', 'buildconversationtranscript(', 'getmemorycontext(', 'memória de sessões anteriores']],
  ['routing', 'Model routing', ['ai-provider', 'llm-provider', 'getmodelconfig(', 'chat_model', 'llm_model', 'openrouterprovider', 'chatwithllm(', 'provider: openrouterprovider.name', 'budget mode', 'cost tracking']],
  ['telemetry', 'Telemetry', ['telemetry', 'recordevent(', 'chat_completion', 'provider_unavailable', 'apilogger.debug(', 'apilogger.warn(']],
  ['hardening', 'Production hardening', ['rate limit', 'message sanitization', 'provider availability', 'scanforpii(', 'sanitizetext(', 'provider unavailable']],
] as const;

function walk(dir: string): string[] { const out: string[] = []; for (const name of readdirSync(dir)) { if (IGNORE.has(name)) continue; const full = join(dir, name); const stat = statSync(full); if (stat.isDirectory()) out.push(...walk(full)); else if (EXTENSIONS.has(extname(name))) out.push(full); } return out; }

type ComplianceStatus = 'implemented' | 'documented_only' | 'missing';

async function checkCompliance(ctx: RunContext): Promise<Finding[]> {
  const target = resolve(process.argv.find((arg) => arg.startsWith('--target='))?.split('=')[1] || ctx.repoRoot);
  const files = walk(target);
  const docs = files.map((file) => ({ file, ext: extname(file).toLowerCase(), rel: relative(target, file).toLowerCase(), content: readFileSync(file, 'utf-8').toLowerCase() }));
  const findings: Finding[] = [];
  const results = CHECKS.map(([key, label, signals]) => {
    const matching = docs.filter((doc) => signals.some((signal) => doc.rel.includes(signal) || doc.content.includes(signal)));
    const codeEvidence = matching.filter((doc) => CODE_EXTENSIONS.has(doc.ext)).slice(0, 3).map((doc) => relative(target, doc.file));
    const docEvidence = matching.filter((doc) => !CODE_EXTENSIONS.has(doc.ext)).slice(0, 3).map((doc) => relative(target, doc.file));
    const status: ComplianceStatus = codeEvidence.length > 0 ? 'implemented' : docEvidence.length > 0 ? 'documented_only' : 'missing';
    return { key, label, codeEvidence, docEvidence, status };
  });
  const score = Math.round((results.reduce((total, result) => total + (result.status === 'implemented' ? 1 : result.status === 'documented_only' ? 0.5 : 0), 0) / results.length) * 100);
  findings.push({ severity: 'info', category: 'chatbot:summary', message: `Chatbot SSOT score ${score}/100 for ${target}`, suggestion: `Reference: ${SSOT_PATH}` });
  for (const result of results.filter((item) => item.status !== 'implemented')) {
    findings.push({ severity: 'warning', category: result.status === 'documented_only' ? 'chatbot:ssot_documented_only' : 'chatbot:ssot_missing', message: result.status === 'documented_only' ? `${result.label} documented but not detected in code` : `${result.label} not detected`, suggestion: `Implement according to ${SSOT_PATH}` });
    ctx.bus.emit(Topics.ARCH_SSOT_VIOLATION, { target, module: result.key, score, status: result.status }, 'chatbot_compliance_checker', ctx.correlationId);
  }
  if (ctx.mode === 'execute') {
    const reportDir = join(target, 'docs', 'agentic', 'reports');
    mkdirSync(reportDir, { recursive: true });
    const lines = ['# Chatbot Compliance Report', '', `> Target: ${target}`, `> Score: ${score}/100`, `> SSOT: ${SSOT_PATH}`, '', '| Module | Status | Evidence |', '|---|---|---|'];
    for (const result of results) lines.push(`| ${result.label} | ${result.status === 'implemented' ? '✅ implemented' : result.status === 'documented_only' ? '📝 docs only' : '⚠️ missing'} | ${[...result.codeEvidence, ...result.docEvidence].join('<br>') || '—'} |`);
    writeFileSync(join(reportDir, 'chatbot-compliance.md'), lines.join('\n'));
    log(ctx, 'info', `Report written to ${join('docs', 'agentic', 'reports', 'chatbot-compliance.md')}`);
  }
  return findings;
}

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('chatbot_compliance_checker', mode, checkCompliance).then((result) => { printResult(result); process.exit(result.success ? 0 : 1); });
