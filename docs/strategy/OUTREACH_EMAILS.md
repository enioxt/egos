# Guard Brasil — Rascunhos de Outreach

> **Instrução de uso:** Personalize o [NOME] e [ÓRGÃO] em cada email.
> Envie via LinkedIn InMail ou email direto. Assunto fixo em cada template.
> Aguarde 5 dias antes de follow-up. Máximo 2 contatos por pessoa.

---

## Email A — Para CTOs / Diretores de TI (Tribunais, Ministérios, Autarquias)

**Assunto:** Sua IA está vazando CPF e RG — como evitar multa LGPD

---

Olá [NOME],

Boa tarde. Meu nome é Enio Rocha, fundador da EGOS.

Fui verificar como sistemas de IA em [ÓRGÃO] processam texto com dados pessoais. Sem uma camada de proteção específica, qualquer LLM — GPT-4, Gemini, LLaMA — repete CPF, RG e MASP no output. Isso vai para logs, para a tela do usuário, possivelmente para o treinamento do modelo.

A LGPD responsabiliza o órgão. O controlador de dados pode ser multado em até R$ 50 milhões por incidente.

Desenvolvemos o **Guard Brasil**: uma API que fica na frente da IA e mascara automaticamente CPF, RG, MASP, REDS, número de processo, placa e outros 8 tipos de PII antes de qualquer processamento.

Latência: 4ms. Integração: uma linha de código.

Posso mostrar ao vivo em 15 minutos com dados do tipo que vocês processam. Quando você tem disponibilidade essa semana?

Att,
Enio Rocha
enio@egos.ia.br
https://guard.egos.ia.br

---

## Email B — Para Gestores de Compliance / DPOs (Bancos públicos, planos de saúde)

**Assunto:** Conformidade LGPD em sistemas de IA — solução em 1 dia

---

Olá [NOME],

Você provavelmente já tem um mapeamento de dados pessoais para LGPD. Mas esse mapeamento cobre os sistemas de IA que processam texto livre?

Modelos de linguagem como ChatGPT e Gemini não distinguem automaticamente dados pessoais — eles simplesmente repetem o que recebem. Um funcionário que cola um prontuário ou extrato numa interface de IA já criou um incidente em potencial.

O **Guard Brasil** resolve isso na camada de infraestrutura:
- Detecta CPF, RG, CNS, CNPJ, conta bancária, e-mail, telefone em tempo real
- Mascara antes do envio para o modelo
- Gera disclosure LGPD automático e hash de auditoria por resposta
- Funciona com qualquer LLM — não troca o fornecedor, só adiciona proteção

Para [ÓRGÃO], o piloto de 30 dias pode começar com avaliação local gratuita ou com plano Starter a partir de R$ 49/mês.

Disponível para conversa de 20 minutos?

Enio Rocha
enio@egos.ia.br | guard.egos.ia.br

---

## Email C — Para Govtechs / Fornecedores de software para governo

**Assunto:** Adicione conformidade LGPD no seu produto em 1 dia — Guard Brasil SDK

---

Olá [NOME],

Se [EMPRESA] fornece software para órgãos públicos com qualquer componente de IA ou processamento de texto, os seus clientes vão perguntar: "Como vocês garantem que dados pessoais não vazam para o modelo?"

A resposta hoje é: não garantem. Nenhum LLM faz isso nativamente.

O **Guard Brasil** é um SDK open source (MIT) que você embute no seu produto em um dia:

```python
# Python — 3 linhas
from guard_brasil_client import inspect
result = inspect(text, api_key=GUARD_KEY)
safe_text = result["output"]  # CPF/RG já mascarados
```

Resultado: seu produto passa a oferecer conformidade LGPD nativa como diferencial competitivo.

SDK gratuito para uso local. API hospedada a partir de R$ 49/mês se quiser SLA e suporte.

Quer ver o código? É tudo open source: github.com/enioxt/egos

Abraço,
Enio
enio@egos.ia.br

---

## Follow-up (5 dias após envio inicial)

**Assunto:** Re: [assunto original]

---

Olá [NOME],

Só retomando minha mensagem anterior.

Posso enviar um exemplo específico para [ÓRGÃO]? Em 10 minutos monto uma demonstração com o tipo de texto que vocês processam.

Att,
Enio

---

## Lista de Targets — Priority Govtech BR

| Organização | Tipo | Contato sugerido | Canal |
|---|---|---|---|
| Tribunal de Contas da União (TCU) | Federal | Secretário de TI | LinkedIn |
| Tribunal de Contas do Estado de SP (TCESP) | Estadual | Diretor de TI | LinkedIn |
| Ministério da Justiça e Segurança Pública | Federal | CIO / Assessor TI | Gov.br |
| Secretaria de Segurança Pública SP | Estadual | CIO | LinkedIn |
| DATAPREV | Federal | Diretor Tecnologia | LinkedIn |
| Serpro | Federal | Diretor Produto | LinkedIn |
| CNJ — Conselho Nacional de Justiça | Federal | Secretário TI | LinkedIn |
| Prefeitura de São Paulo — PRODAM | Municipal | CTO | LinkedIn |
| Prefeitura do Rio — IplanRio | Municipal | CTO | LinkedIn |
| Hospital das Clínicas SP (HC-FMUSP) | Saúde | Gestor TI | LinkedIn |
| Unimed Brasil | Saúde | CTO | LinkedIn |
| Banco do Brasil | Financeiro | VP Tecnologia | LinkedIn |
| Caixa Econômica Federal | Financeiro | VP Tecnologia | LinkedIn |
| TOTVS (maior govtech BR) | Govtech | CTO | LinkedIn |
| Stefanini | Govtech | VP Governo | LinkedIn |
| Cedro Technologies | Govtech | CTO | LinkedIn |
| NEC Brasil | Govtech | Diretor Soluções | LinkedIn |
| Boa Vista SCPC | Financeiro | CTO | LinkedIn |
| CIELO | Financeiro | CTO | LinkedIn |
| Dock (fintech infra) | Financeiro | CTO | LinkedIn |
