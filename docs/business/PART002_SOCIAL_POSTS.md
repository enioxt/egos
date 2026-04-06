# PART-002: Post X.com + LinkedIn — Guard Brasil

## X.com Thread (4 tweets)

**Tweet 1 (hook):**
🔍 Validamos CPF, RG, MASP e 11 outros padrões de dados pessoais brasileiros em 4ms.

@guard_brasil — API de detecção de PII para conformidade com a LGPD.

Free tier: 500 chamadas/mês. Sem cartão.

🧵 (1/4)

**Tweet 2 (prova técnica):**
Testamos ao vivo:

```
POST https://guard.egos.ia.br/v1/inspect
{
  "content": "CPF: 123.456.789-00, cartão 4111 1111..."
}
```

→ Resposta: 4ms
→ Detectado: CPF, CREDIT_CARD, LGPD_RISK: HIGH

Código aberto. Deploy em 5 min.

(2/4)

**Tweet 3 (diferencial):**
O que nos diferencia:
• 15 padrões BR nativos (CPF, RG, MASP, CNPJ, título eleitor...)
• Conformidade LGPD automática
• 0 dados enviados a terceiros (self-hostable)
• SDK TypeScript/Python no npm

Não é só regex — usa validação de dígitos verificadores reais.

(3/4)

**Tweet 4 (CTA):**
Integre em 3 linhas:

```ts
import { guard } from "@egosbr/guard-brasil"
const result = await guard.inspect(text)
if (result.lgpd_risk === "HIGH") redactPII(text)
```

Docs + demo: guard.egos.ia.br
npm: @egosbr/guard-brasil

Quem aqui lida com dados de usuários BR? 👇

(4/4)

---

## LinkedIn Post

**Headline:** Construímos a API de detecção de dados pessoais mais rápida do Brasil — open source

**Body:**
Nos últimos 3 meses construímos o Guard Brasil: uma API que detecta e classifica dados pessoais brasileiros (CPF, RG, CNPJ, cartão de crédito e mais 11 padrões) em menos de 5 milissegundos.

**Por que isso importa:**
A LGPD exige que empresas identifiquem, classifiquem e protejam dados pessoais antes de armazenar ou processar. Hoje, a maioria usa soluções genéricas que não conhecem o formato brasileiro.

**O que fizemos diferente:**
→ 15 padrões validados com dígito verificador real (não só regex)
→ Classificação automática de risco LGPD (BAIXO / MÉDIO / ALTO)
→ Resposta em 4ms (média em produção)
→ Free tier de 500 chamadas/mês sem cartão
→ SDK open source no npm (@egosbr/guard-brasil)

**Casos de uso:**
• Sanitização antes de armazenar em banco de dados
• Validação em pipelines de CI/CD
• Auditoria de logs e arquivos
• Conformidade em LLMs que processam dados BR

Está no ar: guard.egos.ia.br

Se sua empresa lida com dados de usuários brasileiros e não tem uma solução de PII detection, seria ótimo conversar.

#LGPD #PrivacidadeDeDados #OpenSource #API #Brasil #Compliance

---

## og-image.jpg spec (para designer/geração)
Dimensões: 1200x630px
Background: #0a0a0a (escuro)
Elemento central: Logo ⬡ EGOS + "Guard Brasil" em verde (#22c55e)
Subtítulo: "PII Detection API — 15 padrões BR — 4ms — Free tier"
Rodapé: guard.egos.ia.br | @egosbr/guard-brasil
