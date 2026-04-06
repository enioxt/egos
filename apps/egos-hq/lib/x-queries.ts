// X Search Queries Configuration
// HQC-011: Moved from hardcoded in route.ts to dynamic config

export interface XSearchQuery {
  q: string;
  label: string;
  category: 'lgpd' | 'compliance' | 'dev' | 'ai' | 'branding';
}

export const DEFAULT_SEARCH_QUERIES: XSearchQuery[] = [
  { q: 'LGPD API -is:retweet lang:pt', label: 'LGPD + API (PT-BR)', category: 'lgpd' },
  { q: 'mascaramento CPF dados -is:retweet lang:pt', label: 'Mascaramento CPF', category: 'compliance' },
  { q: '"proteção de dados" startup Brasil -is:retweet', label: 'Proteção dados startup BR', category: 'lgpd' },
  { q: 'ANPD multa fiscalização -is:retweet lang:pt', label: 'ANPD multas', category: 'compliance' },
  { q: 'LGPD compliance software -is:retweet', label: 'LGPD compliance software', category: 'lgpd' },
  { q: 'CPF CNPJ API developer -is:retweet', label: 'CPF/CNPJ API dev', category: 'dev' },
  { q: '"inteligência artificial" LGPD dados pessoais -is:retweet lang:pt', label: 'IA + LGPD', category: 'ai' },
  { q: 'multi-agent framework -is:retweet lang:en', label: 'Multi-agent frameworks (EN)', category: 'dev' },
  { q: '#LGPD OR #ProteçãoDeDados -is:retweet lang:pt', label: '#LGPD hashtags', category: 'lgpd' },
  { q: '"Guard Brasil" OR "guard-brasil" OR @egosbr', label: 'Menções Guard Brasil', category: 'branding' },
];

// Dynamic query loader - can be extended to load from DB or config file
export function loadSearchQueries(): XSearchQuery[] {
  // Future: Load from Supabase config table
  // const { data } = await sb.from('x_search_queries').select('*').eq('enabled', true);
  return DEFAULT_SEARCH_QUERIES;
}
