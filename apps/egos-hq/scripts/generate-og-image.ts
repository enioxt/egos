#!/usr/bin/env node
/**
 * GTM-015: OG Image Generator for Guard Brasil
 * 
 * Prerequisites:
 *   npm install -D @playwright/test
 *   npx playwright install chromium
 * 
 * Usage:
 *   npx tsx scripts/generate-og-image.ts
 *   
 * Output: /home/enio/egos/apps/egos-hq/public/og-image.png
 */

import { chromium } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const HTML_PATH = join(__dirname, '../public/og-image-guard-brasil.html');
const OUTPUT_PATH = join(__dirname, '../public/og-image.png');

async function generateOGImage() {
  console.log('🎨 Generating OG image for Guard Brasil...');

  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Set viewport to OG image dimensions
  await page.setViewportSize({ width: 1200, height: 630 });

  // Load the HTML file
  const fileUrl = 'file://' + HTML_PATH;
  await page.goto(fileUrl, { waitUntil: 'networkidle' });

  // Wait for fonts to load
  await page.waitForTimeout(1000);

  // Take screenshot
  await page.screenshot({
    path: OUTPUT_PATH,
    type: 'png',
    fullPage: false
  });

  await browser.close();

  console.log(`✅ OG image generated: ${OUTPUT_PATH}`);
  console.log('📱 Use in meta tags:');
  console.log('   <meta property="og:image" content="https://guard.egos.ia.br/og-image.png">');
  console.log('   <meta property="og:image:width" content="1200">');
  console.log('   <meta property="og:image:height" content="630">');
}

generateOGImage().catch(err => {
  console.error('❌ Failed to generate OG image:', err);
  process.exit(1);
});
