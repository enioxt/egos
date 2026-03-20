#!/usr/bin/env bun
/**
 * Test Alibaba Orchestrator — Multi-Model Economic Routing
 */

import { llmOrchestrator } from '../packages/shared/src/llm-orchestrator';

const testCases = [
  { prompt: 'Olá, como vai?', expected: 'simple' },
  { prompt: 'Explique como funciona autenticação OAuth2 com PKCE em detalhes, incluindo os passos de autorização, token exchange e refresh.', expected: 'moderate' },
  { prompt: 'Crie um sistema completo de agendamento com:\n1. Backend em TypeScript\n2. Frontend em React\n3. Database schema\n4. API endpoints\n5. Testes unitários\n```typescript\n// exemplo\n```', expected: 'complex' },
];

console.log('🧪 Testing LLM Orchestrator\n');

for (const test of testCases) {
  const result = await llmOrchestrator.orchestrate({ prompt: test.prompt });
  const complexity = llmOrchestrator.estimateComplexity(test.prompt);
  
  console.log(`Prompt: "${test.prompt.substring(0, 60)}..."`);
  console.log(`Complexity: ${complexity} (expected: ${test.expected})`);
  console.log(`Model: ${result.model.provider}/${result.model.model}`);
  console.log(`Cost: $${result.estimatedCost.toFixed(4)}`);
  console.log(`Match: ${complexity === test.expected ? '✅' : '❌'}\n`);
}

console.log('\n💰 Cost Comparison:\n');
const complexPrompt = testCases[2].prompt;
const models = ['gemini-flash', 'qwen-turbo', 'qwen-plus'];

for (const modelKey of models) {
  const result = await llmOrchestrator.orchestrate({ 
    prompt: complexPrompt, 
    forceModel: modelKey 
  });
  console.log(`${modelKey.padEnd(15)} → $${result.estimatedCost.toFixed(4)}`);
}

console.log('\n✅ Orchestrator configured. Use free/cheap models first, qwen-plus only when needed.');
