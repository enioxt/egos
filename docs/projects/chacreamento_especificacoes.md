---
title: Especificações do Chacreamento Sustentável em Patos de Minas
version: 1.1.0
status: Active
date_created: 2025-05-12
date_modified: 2025-05-12
authors: [Cascade, Desenvolvedor]
description: Documento de referência com todas as especificações técnicas para o layout do Chacreamento Sustentável, incluindo dimensões, posicionamento e regras de design.
file_type: documentation
scope: projeto-específico
primary_entity_type: especificação
primary_entity_name: chacreamento_sustentavel
tags: [chacreamento, sustentabilidade, svg, layout, especificacoes, dimensoes, mapeamento, patos_de_minas]
related_to: ["mdc:ProjetoRoca.svg", "mdc:ProjetoRoca_base.svg", "mdc:ProjetoRoca_melhorado.svg", "mdc:ProjetoRoca_v2.svg"]
---

## 1. Visão Geral do Projeto

O Chacreamento Sustentável é um empreendimento localizado em Patos de Minas, MG, com área total de 50.846,05m² (coordenadas: -18.521160, -46.502563). O projeto visa criar um espaço residencial que integra princípios de sustentabilidade, privacidade e convivência comunitária, utilizando a proporção áurea para otimizar a estética e funcionalidade do layout.

### 1.1 Conceito e Características

O projeto se destaca por sua arquitetura de bosques interligados, espaços para eventos comunitários e foco na integração com a natureza. Principais características:

- Sistema de bosques interligados (12% da área total)
- Quiosque central para eventos comunitários de até 80 pessoas
- Medidas de terraplanagem leve seguindo a declividade natural
- Aproveitamento da vegetação existente e ampliação estratégica
- Atratividade para aves e fauna local com comedouros e ninhos

### 1.2 Distribuição da Área (Conforme Lei Complementar nº 508/2015)

- **Área Total:** 50.846,05m²
- **Vias (18%):** 9.150m² (Largura total de 9m: 6m leito + 1.5m passeio cada lado)
- **Áreas Verdes (12%):** 6.102m² (Bosque central, bosques pocket, trilhas)
- **Áreas Institucionais (5%):** Coladas ao bosque central em localização estratégica
- **Total Áreas Públicas:** 30% (conforme exigência legal)
- **Lotes (70%):** 35.594m² (25 lotes de 1.250m² a 1.750m² cada)

### 1.3 Escala e Dimensões para SVG

- **Escala SVG:** 1 metro = 2 pixels
- **Dimensões do SVG:** 700px x 500px (incluindo margens)
- **Número de Lotes:** 25 unidades

## 2. Regras de Mapeamento SVG

### 2.1 Princípios Gerais

- **Não-sobreposição:** Cada pixel deve ser mapeado e reservado para seu elemento específico
- **Centralização:** Usar técnicas de transformação SVG para centralização precisa
- **Documentação:** Comentários no código SVG devem indicar áreas ocupadas e cálculos
- **Posicionamento Relativo:** Usar grupos SVG com transformações para posicionamento relativo

### 2.2 Técnicas de Centralização

```xml
<!-- Exemplo de centralização correta -->
<g id="elemento_central" transform="translate(200,300)">
  <!-- x e y negativos representam metade da largura e altura -->
  <rect x="-60" y="-40" width="120" height="80" rx="18" />
</g>
```

### 2.3 Mapeamento de Áreas

- **Espaço Útil:** x=28 até x=372, y=28 até y=572 (após ruas perimetrais)
- **Centro Horizontal:** x=200
- **Centro Vertical:** y=300

## 3. Dimensões dos Elementos

### 3.1 Vias e Caminhos (Conforme Art. 5º e 6º da Lei Complementar nº 508/2015)

| Elemento | Dimensão Real | Dimensão SVG | Observações |
|----------|---------------|--------------|-------------|
| Rua Central | 9m largura total | 18px largura | 6m de leito (12px) + 1,5m de passeio de cada lado (3px cada) |
| Ruas Perimetrais | 9m largura total | 18px largura | 6m de leito (12px) + 1,5m de passeio de cada lado (3px cada) |
| Trilhas Ecológicas | 1.5m largura | 3px largura | Dentro das áreas verdes, conectando bosques |
| Margem Interna | 2m | 4px | Entre perímetro e início da rua |

### 3.2 Áreas Verdes

| Elemento | Dimensão Real | Dimensão SVG | Observações |
|----------|---------------|--------------|-------------|
| Bosque Central | 60m x 40m | 120px x 80px | Centralizado, área de 3.300m² |
| Bosques Pocket | Raio ~12m | Raio ~24px | 6 unidades de ~467m² cada, total ~2.802m² |
| Trilhas Ecológicas | 1,5m (principais), 1,0m (secundárias) | 3px e 2px | Total ~1.200m lineares, material: saibro compactado |
| Áreas de Preservação | Variável | Variável | Total 12% da área total (~6.102m²) |

### 3.3 Lotes

| Elemento | Dimensão Real | Dimensão SVG | Observações |
|----------|---------------|--------------|-------------|
| Lote Padrão | Variável | Variável | 25 unidades, entre 1.250m² e 1.750m² cada |
| Lote Médio | ~35m x 40m | ~70px x 80px | Média de ~1.425m² por lote |
| Espaçamento entre Lotes | 4-5m | 8-10px | 2m de cada lado para vegetação/cerca viva |
| Recuo Frontal | 5m | 10px | Da rua até a frente do lote |
| Recuo Fundos | 5m | 10px | Dos fundos até áreas verdes ou vias |

### 3.4 Áreas Comuns

| Elemento | Dimensão Real | Dimensão SVG | Observações |
|----------|---------------|--------------|-------------|
| Quiosque Central | 10m x 9m | 20px x 18px | 90m², estrutura coberta com telhas ecológicas tipo "Ecotelhado" |
| Banheiros | 8m x 6m | 16px x 12px | 48m², masculino (3 vasos, 6 mictórios), feminino (4 vasos), PcD/Família (2 unidades) |
| Churrasqueiras Integradas | 5m x 5m | 10px x 10px | Integradas ao quiosque, com bancada de 6m lineares e pia |
| Churrasqueiras Independentes | 5m x 5m | 10px x 10px | 2 unidades distribuídas pelos bosques pocket (Norte e Sul) |
| Playground | 10m x 10m | 20px x 20px | Estrutura em madeira tratada, escorregador, balanços, gangorra, piso de segurança |
| Área de Convivência | 20m x 15m | 40px x 30px | 6 mesas grandes (3m x 1m), 4 mesas médias (2m x 1m), capacidade para 80 pessoas |

### 3.5 Elementos Ecológicos

| Elemento | Dimensão Real | Dimensão SVG | Observações |
|----------|---------------|--------------|-------------|
| Comedouros para Pássaros | 1m x 1m | 2px x 2px | 1-2 por bosque pocket, 3-4 no bosque central |
| Ninhos para Pássaros | 0.5m x 0.5m | 1px x 1px | Pelo menos 10 unidades em posições estratégicas |
| Bancos | 2m x 0.5m | 4px x 1px | A cada ~100m nas trilhas, 2-3 em cada bosque pocket |
| Arborização das Vias | Árvores a cada 8-10m | Pontos a cada 16-20px | Recuo de 1.5m da borda da via |

## 4. Posicionamento dos Elementos

### 4.1 Ruas e Acessos

- **Rua Central:** Atravessa o terreno verticalmente, centralizada (x=200)
- **Ruas Perimetrais:** Contornam o perímetro interno, 2m da borda
- **Acessos aos Lotes:** Conectados às ruas principais ou perimetrais
- **Tratamento:** Vias com tratamento superficial simples (TSS)
- **Iluminação:** Pontos de luz baixa e direcionada ao longo das vias

### 4.2 Bosque e Áreas Verdes

- **Bosque Central:** Centralizado no terreno 
- **Bosques Pocket:** Distribuídos estrategicamente em 6 pontos do terreno
  - Bosque do Tucano (Norte)
  - Bosque do Beija-flor (Sul)
  - Outros 4 bosques distribuídos pelo empreendimento
- **Trilhas Ecológicas:** 
  - Largura: 1.5m (principais) e 1.0m (secundárias)
  - Material: Saibro compactado com contenção lateral em madeira
  - Conectam todos os bosques pocket ao bosque central
  - Circulam o empreendimento
- **Área Institucional:**
  - Localizada adjacente ao bosque central
  - Posicionada de forma a não interferir no fluxo do empreendimento

### 4.3 Lotes

- **Distribuição:** Organizados em 4 quadrantes formados pelas vias centrais
- **Numeração:** Começa no canto Noroeste (L01) e segue em sentido horário
- **Orientação:** Preferencialmente norte-sul para melhor insolação
- **Privacidade:**
  - Recuo frontal mínimo: 5m
  - Distância mínima entre laterais: 4m (2m de cada lado)
  - Distância mínima dos fundos para áreas verdes: 5m

### 4.4 Áreas Comuns

- **Complexo Central:** Adjacente ao bosque central, preferencialmente ao sul
  - **Quiosque Multifuncional:**
    - Estrutura central coberta com telhas ecológicas
    - Área da churrasqueira integrada ao quiosque
    - Mobiliário: 6 mesas grandes (3m x 1m), 4 mesas médias (2m x 1m)
    - Bancada lateral de apoio para buffet (6m lineares)
    - Piso em deck de madeira plástica ou cimento queimado
  - **Banheiros:**
    - Construção anexa ao quiosque, com acesso independente
    - Masculino: 3 vasos, 6 mictórios com divisórias, 3 pias
    - Feminino: 4 vasos em cabines isoladas, 3 pias
    - PcD/Família: 2 unidades com barras de apoio, pias em alturas variadas (70cm para crianças)
    - Sistemas econômicos: descarga dual flush, torneiras com temporizador, reaproveitamento de águas pluviais
  - **Playground:**
    - Estrutura em madeira tratada e cordas
    - Escorregador, balanços, gangorra, caixa de areia
    - Piso de segurança

- **Churrasqueiras Independentes:**
  - 2 unidades distribuídas estrategicamente (Norte/Sul)
  - Estrutura coberta com coifa
  - Bancada de 3m com cuba funda
  - Cooktop 2 bocas integrado
  - Mesa para 10 pessoas e balcão de apoio por unidade

## 5. Regras de Design

### 5.1 Proporção Áurea

- Aplicar a proporção áurea (1:1.618) no dimensionamento de áreas e espaçamentos
- Utilizar a sequência de Fibonacci para determinar distâncias entre elementos principais
- Aplicar na relação entre bosque central e bosques pocket
- Considerar na distribuição dos lotes e áreas comuns

### 5.2 Sustentabilidade

- Preservar 70% da vegetação existente no bosque central
- Complementar com espécies nativas do cerrado mineiro
- Planejar sistema de drenagem natural seguindo a declividade do terreno
- Integrar captação de água da chuva
- Prever áreas para compostagem comunitária
- Terraplanagem leve, respeitando a topografia natural

### 5.3 Acessibilidade

- Todas as áreas comuns devem ser acessíveis
- Trilhas principais com largura mínima de 1,5m (3px)
- Rampas em vez de degraus onde necessário
- Banheiros adaptados para PcD e famílias com crianças
- Sinalização tátil em áreas estratégicas

### 5.4 Integração com a Fauna

- Comedouros estratégicos para atrair avifauna local
- Ninhos artificiais em posições elevadas
- Evitar iluminação excessiva que perturbe animais noturnos
- Preservar corredores ecológicos entre bosques

## 6. Implementação SVG

### 6.1 Ordem de Desenho (Z-Index)

1. Perímetro e fundo
2. Ruas perimetrais (com pista e passeios)
3. Rua central (com pista e passeios)
4. Bosques e áreas verdes
5. Áreas institucionais
6. Lotes
7. Áreas comuns
8. Infraestrutura básica (simbologias para água, esgoto, energia)
9. Elementos decorativos e detalhes

### 6.2 Cores e Estilos

| Elemento | Cor de Preenchimento | Cor de Borda | Estilo |
|----------|----------------------|--------------|--------|
| Perímetro | #f9f9f9 | #222222 | stroke-width: 2px |
| Ruas | #cccccc | #444444 | stroke-width: 1px |
| Bosque | #90ee90 | #228B22 | stroke-width: 2px |
| Lotes | #e0f2e0 | #888888 | stroke-width: 1px |
| Área Comum | #add8e6 | #0000ff | stroke-width: 1.5px |
| Trilhas | #4caf50 | none | stroke-dasharray: 5,3 |

## 7. Verificação e Validação

### 7.1 Checklist de Verificação

- [ ] Todas as dimensões respeitam a escala (1m = 2px)
- [ ] Nenhum elemento sobrepõe outro
- [ ] Bosque está perfeitamente centralizado
- [ ] Ruas e caminhos estão conectados corretamente
- [ ] Todos os lotes têm acesso a ruas ou caminhos
- [ ] Áreas comuns são acessíveis de todos os lotes
- [ ] Proporção áurea foi aplicada onde apropriado
- [ ] Comentários no SVG documentam todas as áreas ocupadas
- [ ] Espaçamento mínimo entre lotes respeitado
- [ ] Áreas verdes representam no mínimo 12% do total
- [ ] Elementos ecológicos distribuídos adequadamente

### 7.2 Testes de Visualização

- Testar visualização em diferentes navegadores
- Verificar renderização em dispositivos móveis e desktop
- Confirmar que não há distorções ou sobreposições
- Validar o SVG com ferramentas oficiais (W3C Validator)

## 8. Referências

- Plantas originais do terreno em Patos de Minas
- Coordenadas geográficas: -18.521160, -46.502563
- Lei Complementar nº 508/2015 de Patos de Minas (Chacreamento de Recreio)
- Normativas municipais de Patos de Minas para loteamentos
- Princípios de permacultura e design sustentável
- Técnicas de SVG para mapeamento preciso
- Guias de acessibilidade universal
- Estudos de avifauna local para posicionamento de comedouros

## 9. Infraestrutura Básica Exigida (Conforme Art. 14 da Lei Complementar nº 508/2015)

### 9.1 Demarcação Física

- Demarcação dos lotes com marcos de concreto
- Demarcação das quadras e logradouros
- Placas de identificação das ruas

### 9.2 Sistema de Abastecimento de Água

- Rede de distribuição de água potável
- Poço artesiano com vazão mínima de 5m³/h e outorga
- Reservatório elevado com capacidade mínima de 20.000 litros
- Hidrômetros individuais para cada lote

### 9.3 Sistema de Esgotamento Sanitário

- Fossas/biodigestores individuais por lote (dimensionados para 6 pessoas/lote)
- Sistema específico para áreas comuns (biodigestor dedicado)
- Disposição final adequada do efluente tratado

### 9.4 Sistema Elétrico

- Rede de distribuição de energia elétrica (CEMIG)
- Iluminação pública em LED com fotocélulas
- Pontos de luz baixa e direcionada (para reduzir poluição luminosa)
- Transformação e distribuição conforme normas da concessionária

### 9.5 Sistema de Drenagem Pluvial

- Drenagem natural pelas curvas de nível
- Valas de infiltração em pontos estratégicos
- Aproveitamento de águas pluviais no quiosque central
- Sistema sustentável de drenagem seguindo a declividade do terreno

### 9.6 Pavimentação e Acessibilidade

- Pavimentação do leito das vias (6m) com tratamento superficial simples (TSS)
- Meio-fio e sarjeta em concreto
- Passeios (1.5m de cada lado) em piso intertravado permeável ou similar
- Rampas de acessibilidade nas esquinas e travessias
- Sinalização tátil em áreas estratégicas

### 9.7 Diferenciais de Sustentabilidade

- Paisagismo funcional com espécies nativas do cerrado mineiro
- Sistema integrado de comedouros, bebedouros e ninhos para avifauna
- Iluminação de baixo impacto para preservar hábitos da fauna noturna
- Materiais de construção sustentáveis e de baixa manutenção
- Preservação de corredores ecológicos entre os bosques

## 10. Viabilidade Financeira

### 10.1 Custos e Receitas

- **Investimento Total:** R$ 2.369.692
- **Estratégias de Financiamento:**
  - Permuta: 6 lotes avaliados em R$ 1.200.000 (serviços de engenharia/terraplanagem)
  - Investimento Direto: R$ 1.169.692
- **Receitas Projetadas:**
  - 19 lotes para venda direta a preços entre R$ 180.000 a R$ 250.000
  - Valor médio por lote: R$ 210.000
  - Receita total estimada: R$ 3.990.000
- **Margem Projetada:**
  - Lucro: R$ 2.820.308
  - Rentabilidade: 241% sobre investimento direto

### 10.2 Cronograma de Implementação

- **Fase 1 (Meses 1-3):** Aprovações, terraplanagem, demarcação de lotes
- **Fase 2 (Meses 4-6):** Infraestrutura básica, vias e cerca perimetral
- **Fase 3 (Meses 7-9):** Bosque central e quiosque, rede elétrica
- **Fase 4 (Meses 10-12):** Bosques pocket, trilhas, marketing e vendas
