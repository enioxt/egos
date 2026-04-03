# Adaptive Atomic Retrieval (AAR)

**Alias Histórico/Conceitual:** `Quantum Search` (Bloqueado/Depreciado no Framework)

## Visão Geral

O pacote `@egos/search-engine` (junto ao `@egos/atomizer`) implementa o mecanismo de busca nativo do EGOS: o **Adaptive Atomic Retrieval (AAR)**. 

Originalmente idealizado e apelidado como *"Pesquisa Quântica"* (Quantum Search) nos primeiros drafts conceituais do projeto, o sistema foi renomeado para **AAR** para refletir com precisão sua arquitetura estrutural de software. Como prova de maturidade do framework, o termo "Quantum Search" original e "QuantumSearch" foram inseridos no *Vocab Guard* (`.husky/pre-commit` linha 127) para proibir que IAs futuras criem alucinações arquiteturais usando o jargão quântico sem base no código existente.

Sempre que a necessidade de uma "Busca Quântica" ou busca semântica robusta for citada por agentes ou pelo usuário localmente, ela deve ser roteada imediatamente para esta implementação e à arquitetura AAR.

## Como Funciona

Ao invés de delegar a análise para bancos vetoriais pesados logo de início, ou depender exclusivamente de APIs de *Embeddings*, o AAR realiza **In-Memory Full-Text Search com Scoring Hierárquico**.

A estratégia é fatiar o conhecimento do framework em "Átomos" semânticos (claims, regras, excertos no nível de sentença) e cruzar de forma extremamente rápida:
- **Substring exato** (Alta afinidade no scoring)
- **Token Overlap** (Sobreposição e correspondência parcial do texto da busca com o conteúdo do átomo)
- **Atom Confidence Score** (Peso basal de confiança herdado do conteúdo semântico do Átomo)

## Uso Técnico

*Referência principal encontrada em: `src/in-memory-search.ts`*

O `InMemorySearchEngine` suporta:
- `.index(atoms: Atom[])`: Carrega os recortes (átomos) na memória.
- `.search(query: SearchQuery)`: Retorna os átomos de maior score baseados em token match e substring match.
- `.suggest(prefix: string)`: Realiza recomendações imediatas ("typeahead").

## Roadmap (Busca Semântica por Embeddings)

Enquanto o núcleo AAR garante velocidade pura, buscas semânticas vetoriais pesadas (`search_memory()`) são delegadas ou para o `codebase-memory-mcp` (Graph Search) ou para o design via integração em vetor (ex: *Alibaba Embeddings* via *Supabase S3 Vectors*). A infraestrutura de Átomos está pronta para ser consumida e vetorizada por essas instâncias complementares.
