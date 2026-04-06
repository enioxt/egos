#!/usr/bin/env node
/**
 * KB-019: HARVEST.md Deduplication Script
 * 
 * Problem: HARVEST.md has grown to 10,000+ lines with potential triplication
 * Solution: Parse patterns, deduplicate by content hash, rewrite clean file
 * 
 * Usage: npx tsx scripts/dedup-harvest.ts
 */

import { readFileSync, writeFileSync } from 'fs';
import { createHash } from 'crypto';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const HARVEST_PATH = join(__dirname, '../docs/knowledge/HARVEST.md');
const BACKUP_PATH = join(__dirname, '../docs/knowledge/HARVEST.md.backup');

interface Pattern {
  id: string;
  date: string;
  content: string;
  hash: string;
}

function hashContent(content: string): string {
  return createHash('sha256').update(content.trim()).digest('hex').slice(0, 16);
}

function parsePatterns(content: string): Pattern[] {
  const patterns: Pattern[] = [];
  
  // Split by pattern headers (## P[0-9]+ Patterns)
  const sections = content.split(/(?=## P[0-9]+ Patterns)/);
  
  for (const section of sections) {
    const headerMatch = section.match(/## (P[0-9]+) Patterns \(([0-9-]+)\)/);
    if (!headerMatch) continue;
    
    const [, id, date] = headerMatch;
    const patternContent = section.trim();
    
    // Extract individual patterns within section
    const patternBlocks = patternContent.split(/\n\*\*[A-Z][^*]+\*\*/);
    
    for (const block of patternBlocks) {
      if (!block.trim()) continue;
      
      const titleMatch = block.match(/^\*\*([^*]+)\*\*/);
      const title = titleMatch ? titleMatch[1] : 'Untitled';
      
      patterns.push({
        id: `${id}-${title.slice(0, 30)}`,
        date,
        content: block.trim(),
        hash: hashContent(block)
      });
    }
  }
  
  return patterns;
}

function deduplicatePatterns(patterns: Pattern[]): Pattern[] {
  const seen = new Map<string, Pattern>();
  
  for (const pattern of patterns) {
    if (seen.has(pattern.hash)) {
      console.log(`Duplicate found: ${pattern.id} (same as ${seen.get(pattern.hash)!.id})`);
    } else {
      seen.set(pattern.hash, pattern);
    }
  }
  
  return Array.from(seen.values());
}

function rewriteHarvest(patterns: Pattern[]): string {
  // Group by P-number
  const groups = new Map<string, Pattern[]>();
  
  for (const pattern of patterns) {
    const pNumber = pattern.id.match(/^(P[0-9]+)/)?.[1] || 'P0';
    if (!groups.has(pNumber)) groups.set(pNumber, []);
    groups.get(pNumber)!.push(pattern);
  }
  
  // Sort P-numbers descending (newest first)
  const sortedPNumbers = Array.from(groups.keys()).sort().reverse();
  
  let output = `# HARVEST.md — EGOS Core Knowledge\n\n`;
  output += `> **VERSION:** 4.0.0 | **UPDATED:** ${new Date().toISOString().split('T')[0]}\n`;
  output += `> **PURPOSE:** compact accumulation of reusable patterns discovered in the kernel repo\n`;
  output += `> **Latest:** Deduplicated via KB-019 — unique patterns only\n\n`;
  
  for (const pNumber of sortedPNumbers) {
    const groupPatterns = groups.get(pNumber)!;
    const latestDate = groupPatterns[0]?.date || new Date().toISOString().split('T')[0];
    
    output += `## ${pNumber} Patterns (${latestDate})\n\n`;
    
    for (const pattern of groupPatterns) {
      // Extract title from first line
      const lines = pattern.content.split('\n');
      const titleLine = lines[0];
      const body = lines.slice(1).join('\n').trim();
      
      output += `**${titleLine.replace(/^\*\*/, '').replace(/\*\*$/, '')}**\n`;
      output += body + '\n\n';
    }
    
    output += '---\n\n';
  }
  
  return output;
}

async function main() {
  console.log('🔍 KB-019: Analyzing HARVEST.md for duplicates...\n');
  
  // Read file
  const content = readFileSync(HARVEST_PATH, 'utf-8');
  console.log(`Original size: ${content.length.toLocaleString()} chars, ${content.split('\n').length} lines`);
  
  // Backup
  writeFileSync(BACKUP_PATH, content);
  console.log(`💾 Backup created: HARVEST.md.backup\n`);
  
  // Parse patterns
  const patterns = parsePatterns(content);
  console.log(`📊 Found ${patterns.length} pattern blocks\n`);
  
  // Deduplicate
  const uniquePatterns = deduplicatePatterns(patterns);
  console.log(`\n✅ Unique patterns: ${uniquePatterns.length}`);
  console.log(`🗑️  Duplicates removed: ${patterns.length - uniquePatterns.length}\n`);
  
  // Rewrite
  const newContent = rewriteHarvest(uniquePatterns);
  
  // Write back
  writeFileSync(HARVEST_PATH, newContent);
  
  console.log(`📝 New size: ${newContent.length.toLocaleString()} chars, ${newContent.split('\n').length} lines`);
  console.log(`📉 Reduction: ${((1 - newContent.length / content.length) * 100).toFixed(1)}%\n`);
  
  console.log('✅ KB-019 complete. Review HARVEST.md and delete backup if satisfied.');
}

main().catch(err => {
  console.error('❌ Error:', err);
  process.exit(1);
});
