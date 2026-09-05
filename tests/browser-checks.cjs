'use strict';
const { chromium } = require('playwright');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'test-results');
fs.mkdirSync(output, { recursive: true });
const results = [];
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8' };
const server = http.createServer((req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    const file = path.resolve(root, '.' + (url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname)));
    if (!file.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' });
    res.end(fs.readFileSync(file));
  } catch (error) { res.writeHead(500); res.end(); }
});
(async () => {
  await new Promise(resolve => server.listen(4173, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto('http://127.0.0.1:4173/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1300);
    assert.equal(await page.title(), 'Shubham Kadam — Scientific Computing & AI Evaluation');
    assert.equal(await page.locator('.project-card').count(), 4);
    results.push('Homepage content loads');
    await page.locator('#motion-toggle').click();
    assert.equal(await page.locator('#motion-toggle').getAttribute('aria-pressed'), 'true');
    const knot = await page.locator('#sculpture').evaluate(c => c.toDataURL());
    await page.locator('[data-scene="wave"]').click();
    const wave = await page.locator('#sculpture').evaluate(c => c.toDataURL());
    await page.locator('[data-scene="lorenz"]').click();
    const lorenz = await page.locator('#sculpture').evaluate(c => c.toDataURL());
    assert.notEqual(knot, wave); assert.notEqual(wave, lorenz);
    await page.locator('[data-scene="knot"]').click();
    results.push('All three sculpture modes render distinct scenes');
    await page.screenshot({ path: path.join(output, 'desktop.png'), animations: 'disabled' });
    for (const [filter, count] of [['science', 2], ['evaluation', 1], ['engineering', 2], ['all', 4]]) {
      await page.locator(`[data-filter="${filter}"]`).click();
      assert.equal(await page.locator('.project-card:visible').count(), count);
    }
    results.push('Project filters show the correct projects');
    for (const id of ['reactor', 'evalforge', 'tracevault', 'optimization']) {
      await page.locator(`[data-open-project="${id}"]`).click();
      assert.equal(await page.locator('#project-dialog').evaluate(e => e.open), true);
      assert.ok((await page.locator('#project-title').textContent()).length > 5);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('#project-dialog').evaluate(e => e.open), false);
    }
    results.push('All project dialogs and Escape navigation work');
    await page.locator('#noise').evaluate(input => { input.value = '0'; input.dispatchEvent(new Event('input', { bubbles: true })); });
    await page.locator('#rate').evaluate(input => { input.value = '1.8'; input.dispatchEvent(new Event('input', { bubbles: true })); });
    await page.locator('#fit').click();
    await page.waitForFunction(() => document.querySelector('#solver-status').textContent.includes('Converged'));
    assert.ok(Math.abs(Number(await page.locator('#parameter').textContent()) - .64) < .001);
    assert.ok(Number(await page.locator('#rmse').textContent()) < .0001);
    results.push('Noise-free fit recovers k = 0.640 with negligible residual');
    await page.locator('#reset').click();
    const before = Number(await page.locator('#rmse').textContent());
    await page.locator('#fit').click();
    await page.waitForFunction(() => document.querySelector('#solver-status').textContent.includes('Converged'));
    assert.ok(Number(await page.locator('#rmse').textContent()) <= before);
    const downloadEvent = page.waitForEvent('download');
    await page.locator('#export').click();
    const download = await downloadEvent;
    const csvPath = path.join(output, 'model-fit.csv');
    await download.saveAs(csvPath);
    const rows = fs.readFileSync(csvPath, 'utf8').trim().split('\n');
    assert.equal(rows.length, 29); assert.ok(rows[0].includes('model_prediction'));
    results.push('Noisy fit improves error; CSV contains all 28 observations');
    await page.locator('#lab').screenshot({ path: path.join(output, 'lab.png'), animations: 'disabled' });
    await page.keyboard.press('Control+k');
    await page.locator('#command-search').fill('Thermal');
    assert.equal(await page.locator('#command-results button').count(), 1);
    await page.locator('#command-search').press('Enter');
    assert.equal(await page.locator('#project-title').textContent(), 'Thermal Reactor Twin');
    await page.keyboard.press('Escape');
    results.push('Command palette supports search and keyboard activation');
    await page.locator('#theme-toggle').click();
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(output, 'light.png'), animations: 'disabled' });
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.locator('#theme-toggle').click();
    results.push('Color theme persists on the local device');
    for (const width of [320, 375, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(150);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
      assert.equal(overflow, false, `Horizontal overflow at ${width}px`);
    }
    await page.setViewportSize({ width: 375, height: 900 });
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.locator('#menu-toggle').click();
    assert.equal(await page.locator('#mobile-nav').isVisible(), true);
    await page.locator('#mobile-nav a[href="#lab"]').click();
    assert.equal(await page.locator('#mobile-nav').isVisible(), false);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(output, 'mobile.png'), animations: 'disabled' });
    results.push('320–1440px layouts have no horizontal overflow; mobile menu works');
    const reduced = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    const rp = await reduced.newPage();
    await rp.goto('http://127.0.0.1:4173/', { waitUntil: 'networkidle' });
    assert.equal(await rp.locator('#motion-toggle').getAttribute('aria-pressed'), 'true');
    assert.equal(await rp.locator('.hero-copy').evaluate(e => getComputedStyle(e).opacity), '1');
    await rp.locator('[data-scene="wave"]').click();
    assert.ok((await rp.locator('#scene-label').textContent()).includes('WAVE'));
    await reduced.close();
    results.push('Reduced-motion setting pauses animation while preserving controls');
    const nojs = await browser.newContext({ javaScriptEnabled: false });
    const np = await nojs.newPage();
    await np.goto('http://127.0.0.1:4173/');
    assert.equal(await np.locator('.project-card').count(), 4);
    assert.equal(await np.locator('#expertise').isVisible(), true);
    await nojs.close();
    results.push('Primary portfolio content remains readable without JavaScript');
    await page.goto('http://127.0.0.1:4173/resume.html');
    assert.equal(await page.locator('h1').textContent(), 'SHUBHAM KADAM');
    assert.equal(await page.locator('.skills p').count(), 8);
    await page.setViewportSize({ width: 1200, height: 1000 });
    await page.screenshot({ path: path.join(output, 'resume.png'), animations: 'disabled' });
    results.push('Printable résumé contains all eight technical skill categories');
    assert.deepEqual(errors, []);
    results.push('No uncaught browser JavaScript errors');
    fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify({ passed: true, checks: results }, null, 2));
    console.log(JSON.stringify({ passed: true, checks: results }, null, 2));
  } catch (error) {
    fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify({ passed: false, checks: results, error: error.stack, browserErrors: errors }, null, 2));
    await page.screenshot({ path: path.join(output, 'failure.png'), fullPage: false }).catch(() => {});
    throw error;
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; server.close(); });
