// Pasa los SVG de 02_Imagenes/svg/ a PNG 1920x1080 en 02_Imagenes/.
// Uso: node herramientas/svg_a_png.js <carpeta_video>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = path.resolve(process.argv[2], '02_Imagenes');
  const svgs = fs.readdirSync(path.join(dir, 'svg')).filter(f => f.endsWith('.svg')).sort();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const f of svgs) {
    const svg = fs.readFileSync(path.join(dir, 'svg', f), 'utf8');
    await page.setContent(`<body style="margin:0">${svg}</body>`);
    await page.screenshot({ path: path.join(dir, f.replace('.svg', '.png')) });
  }
  await browser.close();
  console.log(`${svgs.length} PNG en ${dir}`);
})();
