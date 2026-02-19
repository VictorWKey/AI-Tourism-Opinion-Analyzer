/**
 * Generate app icons for all platforms from the TourlyAI logo.
 * Uses the primary-background white logo as the source for app icons.
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

// Source: the 1024x1024 primary background white logo (solid bg, ideal for icons)
const sourcePath = join(outDir, '1024x1024_primary_background_white_logo.png');

async function generate() {
  console.log('Generating TourlyAI icons from source logo...');

  // Generate PNGs at various sizes
  const sizes = [16, 32, 48, 64, 128, 256, 512, 1024];
  const pngBuffers = {};

  for (const size of sizes) {
    const buf = await sharp(sourcePath)
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
