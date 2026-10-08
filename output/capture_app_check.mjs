import { chromium } from '../frontend/node_modules/playwright/index.mjs';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
process.chdir(fileURLToPath(new URL('../', import.meta.url)));

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await mkdir('output/app_check_images', { recursive: true });
await page.goto('http://localhost:5173/#/', { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.setItem('campus_customs_user', JSON.stringify({ id: 1, first_name: 'Test', name: 'Test User', email: 'test@campuscustoms.yale.edu' })));
await page.reload({ waitUntil: 'networkidle' });

await page.getByRole('button', { name: 'Ask Campus Customs' }).click();
await page.screenshot({ path: 'output/app_check_images/usability_chips.png', fullPage: true });

const input = page.getByPlaceholder('Ask about the collection...');
await input.fill('How many medium 2025 Yale Vs Harvard T Shirt are in stock and what is the price?');
await input.press('Enter');
await page.waitForTimeout(1500);
await page.screenshot({ path: 'output/app_check_images/inventory.png', fullPage: true });
await page.waitForTimeout(20000);
await page.screenshot({ path: 'output/app_check_images/inventory_final.png', fullPage: true });

await input.fill('What hoodies do you have?');
await input.press('Enter');
await page.waitForTimeout(20000);
await page.screenshot({ path: 'output/app_check_images/hoodies.png', fullPage: true });
await browser.close();
