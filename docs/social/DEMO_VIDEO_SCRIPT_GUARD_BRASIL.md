# Demo Video Script — Guard Brasil (90 segundos)

> **Job:** GTM-005  
> **Formato:** Screen recording + narração  
> **Duração:** 90 segundos  
> **Destino:** X.com thread, landing page, dev.to

---

## 🎬 ROTEIRO

### [0:00-0:05] Hook — O Problema
**Visual:** Terminal preto, cursor piscando  
**Narração:**
> "Você tem uma API que processa dados brasileiros. Usuários enviam CPF, RG, MASP. LGPD exige que você saiba onde esses dados estão."

**Texto na tela:**
```
Problema: Detectar PII brasileiro é complexo
LGPD: Exige proteção e auditoria
```

---

### [0:05-0:15] A Solução em 30 Segundos
**Visual:** Digitação rápida de comando npm  
**Narração:**
> "Guard Brasil resolve isso em uma linha."

**Ação:**
```bash
npm install @egosbr/guard-brasil
```

**Código aparece:**
```javascript
import { detectPII } from '@egosbr/guard-brasil';

const text = "CPF: 529.982.247-25";
const result = await detectPII(text);

console.log(result.entities[0]);
// { type: 'CPF', value: '529.982.247-25', confidence: 0.995 }
```

---

### [0:15-0:30] Prova — API ao Vivo
**Visual:** Browser mostrando guard.egos.ia.br  
**Narração:**
> "15 padrões brasileiros. CPF, CNPJ, RG, MASP, CNH, PIS. Todos validados matematicamente."

**Ação:**
- Digitar texto em textarea: "O cliente João, CPF 529.982.247-25, RG 12.345.678-9"
- Clicar "Detectar"
- Resultado aparece com highlight nos PII encontrados

**Texto na tela:**
```
Detectado em 4ms:
✓ CPF: 529.982.247-25 (99.5% confidence)
✓ RG: 12.345.678-9 (97.2% confidence)
```

---

### [0:30-0:45] Diferencial — Por Que Não Regex?
**Visual:** Split screen. Esquerda: regex falhando. Direita: Guard Brasil acertando  
**Narração:**
> "Regex caseiro aceita CPF inválido. Guard Brasil valida dígitos verificadores."

**Esquerda (regex):**
```javascript
// ❌ Regex básico
/\d{3}\.\d{3}\.\d{3}-\d{2}/
// Aceita: "000.000.000-00" — CPF inválido!
```

**Direita (Guard Brasil):**
```javascript
// ✅ Validação matemática
{ valid: false, reason: 'Dígitos verificadores incorretos' }
```

---

### [0:45-1:00] Casos de Uso
**Visual:** Rápida sequência de 3 exemplos  
**Narração:**
> "Sanitização de logs, validação de formulários, auditoria LGPD."

**Exemplo 1 — Logs:**
```javascript
maskPII(logEntry);
// "Usuário ***CPF*** acessou sistema"
```

**Exemplo 2 — Validação:**
```javascript
if (detectPII(description).entities.length > 0) {
  return { error: 'Remova dados pessoais antes de enviar' };
}
```

**Exemplo 3 — Auditoria:**
```javascript
// Evidence chain automática
// "CPF detectado em req-12345, posição [12, 28]"
```

---

### [1:00-1:15] Preço — Grátis
**Visual:** Tela simples com preços  
**Narração:**
> "Free tier: 100 requests por dia. Sem cartão. Sem setup."

**Texto na tela:**
```
💰 Preço
━━━━━━━━━━━━━━━━━━━
Free:     100 req/dia  → Grátis
Pro:      10K req/mês  → R$ 49
Enterprise: Ilimitado  → Fale conosco
━━━━━━━━━━━━━━━━━━━
Teste: guard.egos.ia.br
```

---

### [1:15-1:30] Call to Action
**Visual:** Tela final com links e QR code  
**Narração:**
> "Teste agora: guard.egos.ia.br. Código open source em github.com/enioxt/egos."

**Texto na tela:**
```
🚀 Comece Agora
━━━━━━━━━━━━━━━━━━━
📖 Docs: guard.egos.ia.br/docs
💻 GitHub: github.com/enioxt/egos
📧 Email: enioxt@gmail.com
🐦 X: @anoineim

[QR CODE para guard.egos.ia.br]
━━━━━━━━━━━━━━━━━━━
Built with EGOS Framework
Sacred Code: 000.111.369.963.1618
```

---

## 🛠️ PRODUÇÃO

### Ferramentas Sugeridas
- **Gravação:** OBS Studio (free) ou Loom
- **Editor:** DaVinci Resolve (free) ou Clipchamp
- **Terminal:** Hyper ou iTerm2 (tema escuro)
- **Browser:** Chrome com dev tools

### Configurações
- **Resolução:** 1920x1080 (Full HD)
- **Frame rate:** 30fps
- **Áudio:** Microfone headset ou boom
- **Música:** Não (foco na narração)

### Checklist Pré-Gravação
- [ ] API guard.egos.ia.br respondendo
- [ ] npm package instalado para demo local
- [ ] Terminal com fonte grande (16pt+)
- [ ] Browser em modo incógnito (sem extensões visíveis)
- [ ] Script impresso ou teleprompter

---

## 📝 NARRAÇÃO TEXTO COMPLETO

```
Você tem uma API que processa dados brasileiros. 
Usuários enviam CPF, RG, MASP. 
LGPD exige que você saiba onde esses dados estão.

Guard Brasil resolve isso em uma linha.

npm install @egosbr/guard-brasil

[ código funcionando ]

15 padrões brasileiros. 
CPF, CNPJ, RG, MASP, CNH, PIS.
Todos validados matematicamente.

Detectado em 4 milissegundos.
F1 Score 85.3%.

Regex caseiro aceita CPF inválido. 
Guard Brasil valida dígitos verificadores.

Sanitização de logs.
Validação de formulários. 
Auditoria LGPD.

Free tier: 100 requests por dia.
Sem cartão. Sem setup.

Teste agora: guard.egos.ia.br
Código open source: github.com/enioxt/egos
```

**Tempo estimado:** 85 segundos  
**Meta final:** 90 segundos (5s margem)

---

## 🎯 DISTRIBUIÇÃO

### X.com
- Postar como vídeo nativo (melhor alcance)
- Thread com 3-4 tweets complementares
- Pin no perfil

### dev.to
- Incorporar no artigo "Detectar CPF em 5 minutos"
- Thumbnail: frame do [0:15-0:30]

### Landing Page
- Seção "Demo" em guard.egos.ia.br
- Autoplay mute (opcional)

### YouTube (opcional)
- Canal EGOS
- SEO: "LGPD API CPF detection Brazil"

---

**Versão:** 1.0.0  
**Data:** 2026-04-06  
**Próximo passo:** Agendar gravação (30 min setup + 15 min gravação)

