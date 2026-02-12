/**
 * Generate app icons for all platforms.
 * Run: node scripts/generate-icons.mjs
 */
import sharp from 'sharp';
import pngToIco from 'png-to-ico';
import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, '..', 'resources', 'icons');
mkdirSync(outDir, { recursive: true });

// SVG icon: stylized "AT" with a compass/analysis motif on a gradient
const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0ea5e9"/>
      <stop offset="100%" style="stop-color:#6366f1"/>
    </linearGradient>
    <linearGradient id="shine" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:rgba(255,255,255,0.25)"/>
      <stop offset="100%" style="stop-color:rgba(255,255,255,0)"/>
    </linearGradient>
  </defs>
  <!-- Rounded background -->
  <rect width="512" height="512" rx="100" ry="100" fill="url(#bg)"/>
  <!-- Subtle shine overlay -->
  <rect width="512" height="256" rx="100" ry="100" fill="url(#shine)"/>
  <!-- Compass circle (tourism) -->
  <circle cx="256" cy="240" r="130" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="6"/>
  <!-- Analytics bar chart icon -->
  <rect x="170" y="300" width="40" height="80" rx="6" fill="rgba(255,255,255,0.5)"/>
  <rect x="236" y="260" width="40" height="120" rx="6" fill="rgba(255,255,255,0.7)"/>
  <rect x="302" y="280" width="40" height="100" rx="6" fill="rgba(255,255,255,0.5)"/>
  <!-- AI text -->
  <text x="256" y="230" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="900" font-size="160" fill="white" letter-spacing="-5">AI</text>
  <!-- Tagline -->
  <text x="256" y="450" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="600" font-size="40" fill="rgba(255,255,255,0.9)">TOURISM</text>
</svg>
`;

async function generate() {
  console.log('Generating icons...');

  // Generate PNGs at various sizes
  const sizes = [16, 32, 48, 64, 128, 256, 512, 1024];
  const pngBuffers = {};

  for (const size of sizes) {
    const buf = await sharp(Buffer.from(svg))
      .resize(size, size)
      .png()
      .toBuffer();
    pngBuffers[size] = buf;

    // Save individual PNGs
    writeFileSync(join(outDir, `icon-${size}.png`), buf);
    console.log(`  ✓ icon-${size}.png`);
  }

  // Main icon.png (512x512)
  writeFileSync(join(outDir, 'icon.png'), pngBuffers[512]);
  console.log('  ✓ icon.png (512x512)');

  // Generate .ico (multi-size: 16, 32, 48, 64, 128, 256)
  const icoSizes = [16, 32, 48, 64, 128, 256];
  const icoPngs = icoSizes.map(s => pngBuffers[s]);
  const icoBuffer = await pngToIco(icoPngs);
  writeFileSync(join(outDir, 'icon.ico'), icoBuffer);
  console.log('  ✓ icon.ico (multi-size)');

  console.log(`\nAll icons saved to ${outDir}`);
}

generate().catch(console.error);
