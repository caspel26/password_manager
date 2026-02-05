/**
 * Generate app icons for Vault
 * Run with: node scripts/generate-icon.js
 */

import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function generateIcons() {
  const buildDir = path.join(__dirname, '..', 'build');

  // Create build directory if it doesn't exist
  if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
  }

  // Create base icon at 1024x1024 using compositing for proper gradient
  const size = 1024;
  const padding = 32;
  const cornerRadius = 192;

  // Create gradient background by compositing two color layers
  const topColor = { r: 102, g: 126, b: 234, alpha: 1 };    // #667eea
  const bottomColor = { r: 118, g: 75, b: 162, alpha: 1 };  // #764ba2

  // Create a gradient effect using sharp's built-in gradient support
  // We'll create a diagonal gradient by blending two solid colors

  // First, create the rounded rectangle mask
  const maskSvg = `
    <svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
      <rect x="${padding}" y="${padding}" width="${size - padding * 2}" height="${size - padding * 2}" rx="${cornerRadius}" fill="white"/>
    </svg>
  `;

  // Create a gradient background image
  const gradientSvg = `
    <svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect x="${padding}" y="${padding}" width="${size - padding * 2}" height="${size - padding * 2}" rx="${cornerRadius}" fill="url(#grad)"/>
    </svg>
  `;

  // Lock icon SVG (white lock on transparent background)
  const lockSvg = `
    <svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
      <!-- Lock body -->
      <rect x="312" y="480" width="400" height="320" rx="48" fill="white"/>

      <!-- Lock shackle -->
      <path d="M384 480V352C384 281.308 441.308 224 512 224C582.692 224 640 281.308 640 352V480"
            stroke="white" stroke-width="64" stroke-linecap="round" fill="none"/>

      <!-- Keyhole -->
      <circle cx="512" cy="620" r="48" fill="#667eea"/>
      <rect x="488" y="620" width="48" height="96" rx="24" fill="#667eea"/>
    </svg>
  `;

  // Generate the base icon by compositing layers
  const baseIcon = await sharp({
    create: {
      width: size,
      height: size,
      channels: 4,
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    }
  })
    .composite([
      { input: Buffer.from(gradientSvg), top: 0, left: 0 },
      { input: Buffer.from(lockSvg), top: 0, left: 0 },
    ])
    .png()
    .toBuffer();

  // Save the 1024 version
  const icon1024Path = path.join(buildDir, 'icon-1024.png');
  await sharp(baseIcon).toFile(icon1024Path);
  console.log('Created: build/icon-1024.png');

  // Generate PNG icons at different sizes
  const sizes = [16, 32, 64, 128, 256, 512];

  for (const s of sizes) {
    const pngPath = path.join(buildDir, s === 512 ? 'icon.png' : `icon-${s}.png`);
    await sharp(baseIcon)
      .resize(s, s, { kernel: sharp.kernel.lanczos3 })
      .png()
      .toFile(pngPath);
    console.log(`Created: build/${path.basename(pngPath)}`);
  }

  // Also save an SVG version for reference
  const fullSvg = `
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect x="16" y="16" width="480" height="480" rx="96" fill="url(#bgGrad)"/>

  <!-- Lock body -->
  <rect x="156" y="240" width="200" height="160" rx="24" fill="white"/>

  <!-- Lock shackle -->
  <path d="M192 240V176C192 140.654 220.654 112 256 112C291.346 112 320 140.654 320 176V240"
        stroke="white" stroke-width="32" stroke-linecap="round" fill="none"/>

  <!-- Keyhole -->
  <circle cx="256" cy="310" r="24" fill="#667eea"/>
  <rect x="244" y="310" width="24" height="48" rx="12" fill="#667eea"/>
</svg>
`;

  fs.writeFileSync(path.join(buildDir, 'icon.svg'), fullSvg.trim());
  console.log('Created: build/icon.svg');

  // Create favicon.ico
  const faviconPath = path.join(__dirname, '..', 'public', 'favicon.ico');
  const publicDir = path.join(__dirname, '..', 'public');
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
  }

  await sharp(baseIcon)
    .resize(32, 32, { kernel: sharp.kernel.lanczos3 })
    .png()
    .toFile(faviconPath);
  console.log('Created: public/favicon.ico');

  console.log('\nIcon generation complete!');
  console.log('\nRegenerating macOS .icns file...');
}

generateIcons().catch(console.error);
