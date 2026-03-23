# EGOS Commons — commons.egos.ia.br

Marketplace de produtos de IA governada. Cursos, ferramentas, templates e agentes.

## Deploy rápido (Vercel)

```bash
# 1. Build
npm install && npm run build

# 2. Deploy via CLI
npx vercel deploy --prod

# 3. Apontar domínio
# No Vercel Dashboard: Settings → Domains → commons.egos.ia.br
```

## Rodar localmente

```bash
npm install
npm run dev
# Acesse: http://localhost:5173
```

## Personalizar produtos

Edite `src/App.tsx` → array `products[]` para adicionar/editar produtos.

## Stack

- Vite + React 19 + TypeScript
- Tailwind CSS v4
- Lucide React (ícones)
- Vercel (deploy)
