// Records the opening hook card and the end card (HTML in ./cards) as short clips.
//   node scripts/video/record_cards.js OUT_DIR
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const OUT = path.resolve(process.argv[2]);
(async () => {
  const browser = await chromium.launch();
  for (const [name, seconds] of [['hook', 7], ['end', 6.5]]) {
    const context = await browser.newContext({ viewport: { width: 1536, height: 864 }, recordVideo: { dir: OUT, size: { width: 1536, height: 864 } } });
    const page = await context.newPage();
    const t0 = Date.now();
    await page.goto('file://' + path.join(__dirname, 'cards', `${name}.html`), { waitUntil: 'networkidle' });
    const lead = (Date.now() - t0) / 1000;
    await page.waitForTimeout(seconds * 1000);
    const video = page.video();
    await context.close();
    fs.renameSync(await video.path(), path.join(OUT, `${name}.webm`));
    fs.writeFileSync(path.join(OUT, `${name}.lead.txt`), String(lead));
    console.log(name, 'lead', lead.toFixed(2));
  }
  await browser.close();
})();
