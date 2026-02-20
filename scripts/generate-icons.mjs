/**
 * Generate app icons for all platforms from the TourlyAI logo.
 * Uses the primary-background white logo as the source for app icons.
 * 
 * Generates:
 *   - icon.png     (512x512)   — Linux / generic
 *   - icon.ico     (multi-size) — Windows
 *   - icon.icns    (multi-size) — macOS
 *   - icon-{size}.png           — individual sizes
 *
 * Run: node scripts/generate-icons.mjs
 */
import sharp from 'sharp';
import pngToIco from 'png-to-ico';
import png2icons from 'png2icons';
import { writeFileSync, readFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, '..', 'resources', 'icons');
mkdirSync(outDir, { recursive: true });

// Source: the 1024x1024 primary background white logo (solid bg, ideal for icons)
const sourcePath = join(outDir, '1024x1024_primary_background_white_logo.png');

async function generate() {
  console.log('Generating TourlyAI icons from source logo...\n');

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

  // Generate .ico for Windows (multi-size: 16, 32, 48, 64, 128, 256)
  const icoSizes = [16, 32, 48, 64, 128, 256];
  const icoPngs = icoSizes.map(s => pngBuffers[s]);
  const icoBuffer = await pngToIco(icoPngs);
  writeFileSync(join(outDir, 'icon.ico'), icoBuffer);
  console.log('  ✓ icon.ico (multi-size) — Windows');

  // Generate .icns for macOS (requires 1024x1024 source PNG)
  try {
    const sourcePngBuffer = readFileSync(sourcePath);
    const icnsBuffer = png2icons.createICNS(sourcePngBuffer, png2icons.BICUBIC2, 0);
    if (icnsBuffer) {
      writeFileSync(join(outDir, 'icon.icns'), icnsBuffer);
      console.log('  ✓ icon.icns (multi-size) — macOS');
    } else {
      console.warn('  ⚠ Failed to generate icon.icns (null result)');
    }
  } catch (err) {
    console.warn('  ⚠ Failed to generate icon.icns:', err.message);
  }

  console.log(`\nAll icons saved to ${outDir}`);
}

generate().catch(console.error);
