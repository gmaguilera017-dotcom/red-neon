// Pasa a PNG los SVG de canales/*/marca/. Uso: node herramientas/marca_a_png.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  for (const canal of ['medico', 'popular']) {
    const dir = path.resolve(__dirname, '..', 'canales', canal, 'marca');
    for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
      const svg = fs.readFileSync(path.join(dir, f), 'utf8');
      const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/);
      const page = await browser.newPage({ viewport: { width: +w, height: +h } });
      await page.setContent(`<body style="margin:0">${svg}</body>`);
      await page.screenshot({ path: path.join(dir, f.replace('.svg', '.png')) });
      await page.close();
    }
  }
  await browser.close();
})();
