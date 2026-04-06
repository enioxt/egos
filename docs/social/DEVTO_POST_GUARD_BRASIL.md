# Como Detectar CPF, RG e MASP na Sua API Node.js em 5 Minutos

> **TL;DR:** Use Guard Brasil — API gratuita de detecção de PII brasileiro. 15 padrões, 4ms latência, F1 85.3%. Sem setup, sem cartão.

---

## 🚨 O Problema Real

Você construiu uma API que processa dados brasileiros. Usuários enviam CPF em formulários, RG em uploads, MASP em cadastros de servidores públicos.

**LGPD exige:** Você precisa saber onde esses dados sensíveis estão, protegê-los, e auditar acessos.

**A realidade:** Detectar CPF válido vs. número aleatório de 11 dígitos é não-trivial. E existem 15+ padrões brasileiros diferentes.

---

## 🛠️ A Solução em 30 Segundos

```bash
npm install @egosbr/guard-brasil
```

```javascript
import { detectPII } from '@egosbr/guard-brasil';

const text = "O CPF do cliente é 529.982.247-25";
const result = await detectPII(text);

console.log(result);
// {
//   entities: [
//     { type: 'CPF', value: '529.982.247-25', position: [23, 38], confidence: 0.995 }
//   ]
// }
```

**Pronto.** LGPD compliance técnico em uma linha.

---

## 📊 Por Que Não Regex Caseiro?

### Regex de CPF (o básico)
```javascript
// Não faz isso em produção
const cpfRegex = /\d{3}\.\d{3}\.\d{3}-\d{2}/;
// Problema: aceita "000.000.000-00", "111.111.111-11"
// Não valida dígitos verificadores
```

### Guard Brasil (o correto)
```javascript
// Valida dígitos verificadores matematicamente
// Detecta 15 padrões diferentes (CPF, RG, CNPJ, MASP, CNH...)
// 4ms de latência — mais rápido que seu banco de dados
// F1 85.3% — benchmark independente
```

---

## 🎯 Casos de Uso

### 1. Sanitização de Logs
```javascript
import { maskPII } from '@egosbr/guard-brasil';

const logEntry = "Usuário 529.982.247-25 acessou sistema";
const safeLog = maskPII(logEntry);
// "Usuário ***CPF*** acessou sistema"
```

### 2. Validação de Formulários
```javascript
app.post('/register', async (req, res) => {
  const { description } = req.body;
  
  const pii = await detectPII(description);
  if (pii.entities.length > 0) {
    return res.status(400).json({
      error: 'Descrição contém dados pessoais. Remova antes de enviar.'
    });
  }
  
  // Prosseguir com cadastro
});
```

### 3. Auditoria LGPD
```javascript
// Toda detecção gera evidence chain
const result = await detectPII(text, { 
  audit: true,
  requestId: 'req-12345'
});

// Log auditável para ANPD
// "2026-04-06T14:30:00Z: CPF detectado em req-12345, posição [12, 28]"
```

---

## 💰 Preço: Grátis (até 100 requests/dia)

```bash
# Não precisa de API key para testar
curl -X POST https://guard.egos.ia.br/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Meu CPF é 529.982.247-25"}'
```

**Free tier:** 100 requests/dia  
**Pro:** R$ 49/mês (10K requests)  
**Enterprise:** Fale conosco

---

## 🧪 Teste Agora

```html
<!DOCTYPE html>
<html>
<body>
  <textarea id="input" placeholder="Cole texto com CPF..."></textarea>
  <button onclick="detect()">Detectar PII</button>
  <pre id="result"></pre>
  
  <script src="https://unpkg.com/@egosbr/guard-brasil/dist/browser.js"></script>
  <script>
    async function detect() {
      const text = document.getElementById('input').value;
      const result = await GuardBrasil.detectPII(text);
      document.getElementById('result').textContent = 
        JSON.stringify(result, null, 2);
    }
  </script>
</body>
</html>
```

---

## 📚 Recursos

- **Docs:** [guard.egos.ia.br/docs](https://guard.egos.ia.br/docs)
- **GitHub:** [github.com/enioxt/egos](https://github.com/enioxt/egos) (MIT license)
- **Playground:** Teste ao vivo no site

---

## 🤔 Por "Brasileiro"?

Ferramentas internacionais (Microsoft Presidio, AWS Comprehend) detectam SSN americano, cartões de crédito, emails. **Zero padrões brasileiros.**

Guard Brasil nasceu com:
- CPF, CNPJ, RG, MASP, CNH, PIS, Título de Eleitor
- Validação matemática de dígitos verificadores
- LGPD/ANPD como premissa, não afterthought

---

> **Enio Rocha** — Solo builder de 13 produtos em 18 meses. 
> Busco parceiros de GTM com equity generosa (20-30%). 
> enioxt@gmail.com | @anoineim

---

**Tags:** #lgpd #nodejs #javascript #compliance #privacy #brazil

