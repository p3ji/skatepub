const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('Starting Playwright visual verification with docs/calendar/images assets...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 2000 } });

  const htmlPath = path.resolve('docs/calendar/CanSkate202627Calendar.html');
  const fileUrl = `file:///${htmlPath.replace(/\\/g, '/')}`;

  console.log(`Navigating to: ${fileUrl}`);
  await page.goto(fileUrl, { waitUntil: 'load' });

  // 1. Verify 7 monthly tables exist
  const tableCount = await page.locator('table').count();
  console.log(`Tables found on page: ${tableCount}`);
  if (tableCount !== 7) {
    throw new Error(`Expected 7 tables, found ${tableCount}`);
  }

  // 2. Check images loaded properly (naturalWidth > 0)
  const images = page.locator('img');
  const imgCount = await images.count();
  console.log(`Total images found: ${imgCount}`);

  let brokenImages = 0;
  for (let i = 0; i < imgCount; i++) {
    const img = images.nth(i);
    const src = await img.getAttribute('src');
    const isLoaded = await img.evaluate(node => node.complete && node.naturalWidth > 0);
    if (!isLoaded) {
      console.error(`FAILED to load image index ${i}: ${src}`);
      brokenImages++;
    } else {
      console.log(`Image ${i} loaded OK: ${src}`);
    }
  }

  if (brokenImages > 0) {
    throw new Error(`Found ${brokenImages} broken image(s)`);
  }

  // 3. Take screenshots for visual inspection
  const screenshotPath = path.resolve('docs/calendar/calendar_preview.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });

  const septPath = path.resolve('docs/calendar/september_preview.png');
  await page.locator('table').nth(0).screenshot({ path: septPath });

  const octPath = path.resolve('docs/calendar/october_preview.png');
  await page.locator('table').nth(1).screenshot({ path: octPath });

  const decPath = path.resolve('docs/calendar/december_preview.png');
  await page.locator('table').nth(3).screenshot({ path: decPath });
  console.log(`Saved December table preview to: ${decPath}`);

  await browser.close();
  console.log('Visual verification completed successfully!');
})();
