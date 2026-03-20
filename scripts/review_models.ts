import fs from 'fs';
import path from 'path';
import { chatWithLLM } from '../packages/shared/src/llm-provider';

async function runReview() {
  const content = fs.readFileSync(path.join(process.cwd(), 'docs/strategy/MULTI_MODEL_PLANNING.md'), 'utf-8');
  
  console.log('Sending to Alibaba (Qwen)...');
  const alibabaResponse = await chatWithLLM({
    systemPrompt: "Você é o Alibaba Qwen, o cérebro principal focado em execução bruta e análise fria. Revise criticamente o plano proposto, aponte inconsistências operacionais ou de custo, e defina se a estratégia de pivotar o framework inteiro para focar no ATRiAN e PII-BR é sólida.",
    userPrompt: `Revise este documento:\n\n${content}`,
    provider: 'alibaba',
    model: 'qwen-plus',
    maxTokens: 2000
  });

  console.log('Sending to Codex (via OpenRouter)...');
  const codexResponse = await chatWithLLM({
    systemPrompt: "Você é o Codex (representando a IA de revisão e governança obrigatória). Analise o plano focando em segurança, arquitetura, proof-of-work e coerência com o pipeline EGOS. O pivot para o ATRiAN Guard Enterprise viola nossa identidade ou é a evolução natural mais segura?",
    userPrompt: `Revise este documento e dê seu veredito técnico:\n\n${content}`,
    provider: 'openrouter',
    model: 'google/gemini-2.0-flash-001', // simulating codex/reviewer via available OpenRouter model
    maxTokens: 2000
  });

  const appendData = `
## Fase 3: Validação do Conselho (Alibaba & Codex)

### Parecer do Alibaba (Qwen-Plus) - Execução e Viabilidade
${alibabaResponse.content}

### Parecer do Codex (OpenRouter/Reviewer) - Segurança e Arquitetura
${codexResponse.content}
`;

  fs.appendFileSync(path.join(process.cwd(), 'docs/strategy/MULTI_MODEL_PLANNING.md'), appendData);
  console.log('Review completed and appended to the file.');
}

runReview().catch(console.error);
