#!/usr/bin/env bun
/**
 * sync-inventory-to-json.ts
 *
 * Converte business/inventory.md → apps/commons/public/products.json
 * Roda automaticamente via pre-commit hook quando inventory.md é modificado
 *
 * Usage: bun scripts/sync-inventory-to-json.ts
 */

import { readFileSync, writeFileSync } from 'fs'
import { join } from 'path'

interface Product {
  id: string
  title: string
  subtitle: string
  description: string
  price: number | 'free' | 'custom'
  splitDetails: string
  githubUrl?: string
  tier: 'free' | 'pro' | 'enterprise'
  category: string
  tags: string[]
  rating: number
  featured?: boolean
  badge?: string
}

const REPO_ROOT = join(import.meta.dir, '..')
const INVENTORY_PATH = join(REPO_ROOT, 'business', 'inventory.md')
const OUTPUT_PATH = join(REPO_ROOT, 'apps', 'commons', 'public', 'products.json')

function parseInventory(markdown: string): Product[] {
  const products: Product[] = []

  // Regex para capturar cada produto (### N. TITLE)
  const productRegex = /### (\d+)\. (.+?) \((.+?)\)\n- \*\*Descrição Real:\*\* (.+?)\n- \*\*Estado:\*\* (.+?)\n- \*\*O que entregamos:\*\* (.+?)\n- \*\*Preço Sugerido:\*\* R\$ ([\d.]+)(?: \((.+?)\))?\n- \*\*Split \(95\/5\):\*\* (.+)/g

  let match
  while ((match = productRegex.exec(markdown)) !== null) {
    const [
      _fullMatch,
      index,
      title,
      subtitle,
      description,
      status,
      _delivery,
      priceStr,
      _note,
      splitDetails
    ] = match

    // Parse ID (slug from title)
    const id = title
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '')

    // Parse price
    const price = parseInt(priceStr.replace(/\./g, ''))

    // Determine tier based on price
    let tier: 'free' | 'pro' | 'enterprise' = 'pro'
    if (price < 3000) tier = 'pro'
    else if (price >= 7000) tier = 'enterprise'

    // Determine category
    let category = 'tool'
    if (title.includes('SaaS') || title.includes('Marketplace')) category = 'template'
    if (title.includes('Chatbot') || title.includes('Assistentes')) category = 'agent'

    // Determine badge from status
    let badge: string | undefined
    if (status.includes('Produção')) badge = 'Produção'
    else if (status.includes('Lab') || status.includes('POC')) badge = 'POC Madura'
    else if (status.includes('Infra')) badge = 'Infra Pesada'

    // Featured: first 3 products
    const featured = parseInt(index) <= 3

    // Generate tags from description keywords
    const tags: string[] = []
    if (description.includes('governança')) tags.push('governança')
    if (description.includes('TypeScript')) tags.push('TypeScript')
    if (description.includes('Next.js')) tags.push('Next.js')
    if (description.includes('Supabase')) tags.push('Supabase')
    if (description.includes('PII') || description.includes('LGPD')) tags.push('LGPD')
    if (description.includes('Neo4j') || description.includes('ETL')) tags.push('ETL')
    if (description.includes('Asaas')) tags.push('Asaas')
    if (!tags.length) tags.push('IA', 'governança')

    products.push({
      id,
      title,
      subtitle,
      description,
      price,
      splitDetails,
      tier,
      category,
      tags,
      rating: 4.8 + Math.random() * 0.2, // Random rating between 4.8-5.0
      featured,
      badge
    })
  }

  return products
}

function main() {
  console.log('🔄 Syncing inventory.md → products.json...')

  try {
    // Read inventory.md
    const inventoryContent = readFileSync(INVENTORY_PATH, 'utf-8')
    console.log(`✓ Read ${INVENTORY_PATH}`)

    // Parse products
    const products = parseInventory(inventoryContent)
    console.log(`✓ Parsed ${products.length} products`)

    // Write products.json
    const json = JSON.stringify(products, null, 2)
    writeFileSync(OUTPUT_PATH, json, 'utf-8')
    console.log(`✓ Wrote ${OUTPUT_PATH}`)

    console.log('\n✅ Sync complete!')
    console.log(`📦 ${products.length} products available in Commons`)

    // Print summary
    products.forEach(p => {
      console.log(`   - ${p.title} (R$ ${p.price})`)
    })

  } catch (error) {
    console.error('❌ Sync failed:', error)
    process.exit(1)
  }
}

main()
