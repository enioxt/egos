// X Reply Suggestions Engine
// HQC-011: Moved from hardcoded in route.ts to dynamic suggestion engine

export interface ReplySuggestion {
  text: string;
  category: 'lgpd' | 'api' | 'compliance' | 'ai' | 'branding';
  confidence: number; // 0-1 relevance score
}

// Context-aware suggestion patterns
const SUGGESTION_PATTERNS: Array<{
  keywords: string[];
  suggestions: ReplySuggestion[];
}> = [
  {
    keywords: ['lgpd', 'cpf', 'dados pessoais', 'proteção de dados'],
    suggestions: [
      {
        text: 'Construí uma API open-source que detecta e mascara 15 tipos de PII brasileiro (CPF, CNPJ, RG, etc.) em tempo real, com receipt SHA-256 por inspeção — guard.egos.ia.br',
        category: 'api',
        confidence: 0.95,
      },
      {
        text: 'Trabalhando nisso há meses — @egosbr/guard-brasil detecta CPF, CNPJ, RG, placa, processo judicial e mais. Open source, MIT. guard.egos.ia.br',
        category: 'branding',
        confidence: 0.90,
      },
    ],
  },
  {
    keywords: ['anpd', 'multa', 'fiscalização', 'autuação'],
    suggestions: [
      {
        text: 'Com as fiscalizações da ANPD aumentando, compliance automático vira obrigação. Estou construindo uma API que gera receipts SHA-256 por inspeção como prova auditável. guard.egos.ia.br',
        category: 'compliance',
        confidence: 0.92,
      },
    ],
  },
  {
    keywords: ['llm', 'openai', 'claude', 'ia', 'gpt', 'modelo'],
    suggestions: [
      {
        text: 'Antes de mandar dados brasileiros pra qualquer LLM, vale mascarar CPF/CNPJ automaticamente. 3 linhas de código: npm install @egosbr/guard-brasil — ainda em beta, feedback é ouro.',
        category: 'ai',
        confidence: 0.88,
      },
    ],
  },
  {
    keywords: ['api', 'developer', 'dev', 'sdk', 'npm', 'biblioteca'],
    suggestions: [
      {
        text: 'Para devs brasileiros: @egosbr/guard-brasil — PII detection nativo com 15 padrões BR (CPF, CNPJ, RG, MASP, placa, processo judicial). Zero deps, TypeScript, MIT.',
        category: 'api',
        confidence: 0.85,
      },
    ],
  },
];

// Default fallback suggestion
const FALLBACK_SUGGESTION: ReplySuggestion = {
  text: 'Contexto relevante — tenho trabalhado em ferramentas de compliance LGPD para devs brasileiros. Se for útil: guard.egos.ia.br',
  category: 'branding',
  confidence: 0.60,
};

/**
 * Generate contextual reply suggestions based on tweet content
 * HQC-011: Dynamic replacement for hardcoded suggestions
 */
export function generateSuggestions(tweetText: string): ReplySuggestion[] {
  const lowerText = tweetText.toLowerCase();
  const suggestions: ReplySuggestion[] = [];

  for (const pattern of SUGGESTION_PATTERNS) {
    const matches = pattern.keywords.some(kw => lowerText.includes(kw));
    if (matches) {
      suggestions.push(...pattern.suggestions);
    }
  }

  // Add fallback if no specific matches
  if (suggestions.length === 0) {
    suggestions.push(FALLBACK_SUGGESTION);
  }

  // Sort by confidence
  return suggestions.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Get just the text suggestions (for API compatibility)
 */
export function generateSuggestionTexts(tweetText: string): string[] {
  return generateSuggestions(tweetText).map(s => s.text);
}

// Future: Load from Supabase for dynamic updates without deploy
// export async function loadSuggestionsFromDB(): Promise<typeof SUGGESTION_PATTERNS> { ... }
