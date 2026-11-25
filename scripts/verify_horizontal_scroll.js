const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'screenshots');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function verify() {
  console.log('--- Starting Horizontal Scroll Verification ---');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  const pageUrl = 'http://127.0.0.1:8000/';
  console.log(`Loading page: ${pageUrl}`);

  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(pageUrl, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 800));

  // 1. Check section exists and get its bounding box
  const sectionMetrics = await page.evaluate(() => {
    const section = document.getElementById('how-it-works');
    const container = document.getElementById('timelineScrollContainer');
    const prevBtn = document.getElementById('timelinePrevBtn');
    const nextBtn = document.getElementById('timelineNextBtn');
    const cards = document.querySelectorAll('.methodology-card');

    if (!section || !container) return null;

    const rect = section.getBoundingClientRect();
    return {
      sectionHeight: rect.height,
      containerScrollWidth: container.scrollWidth,
      containerClientWidth: container.clientWidth,
      containerScrollLeft: container.scrollLeft,
      cardsCount: cards.length,
      prevDisabled: prevBtn ? prevBtn.disabled : null,
      nextDisabled: nextBtn ? nextBtn.disabled : null,
    };
  });

  console.log('Section Metrics:', JSON.stringify(sectionMetrics, null, 2));

  if (!sectionMetrics) {
    throw new Error('Section or scroll container not found!');
  }

  // Scroll into view of #how-it-works
  await page.evaluate(() => {
    document.getElementById('how-it-works').scrollIntoView({ behavior: 'instant', block: 'start' });
  });
  await new Promise(r => setTimeout(r, 400));

  // Take screenshot of desktop methodology in view
  const initialShot = path.join(SCREENSHOT_DIR, 'verify_methodology_desktop_initial.png');
  await page.screenshot({ path: initialShot });
  console.log(`Saved screenshot: ${initialShot}`);

  // 2. Test horizontal next button click
  console.log('Clicking Next Button (#timelineNextBtn)...');
  await page.click('#timelineNextBtn');
  await new Promise(r => setTimeout(r, 600));

  const afterNextMetrics = await page.evaluate(() => {
    const container = document.getElementById('timelineScrollContainer');
    const prevBtn = document.getElementById('timelinePrevBtn');
    const nextBtn = document.getElementById('timelineNextBtn');
    return {
      scrollLeft: container.scrollLeft,
      prevDisabled: prevBtn.disabled,
      nextDisabled: nextBtn.disabled
    };
  });
  console.log('After Next Click Metrics:', JSON.stringify(afterNextMetrics, null, 2));

  const scrolledShot = path.join(SCREENSHOT_DIR, 'verify_methodology_desktop_scrolled.png');
  await page.screenshot({ path: scrolledShot });
  console.log(`Saved screenshot: ${scrolledShot}`);

  // 3. Test horizontal prev button click
  console.log('Clicking Prev Button (#timelinePrevBtn)...');
  await page.click('#timelinePrevBtn');
  await new Promise(r => setTimeout(r, 600));

  const afterPrevMetrics = await page.evaluate(() => {
    const container = document.getElementById('timelineScrollContainer');
    return { scrollLeft: container.scrollLeft };
  });
  console.log('After Prev Click Metrics:', JSON.stringify(afterPrevMetrics, null, 2));

  // 4. Test Mobile Viewport (375x812)
  console.log('Testing Mobile Viewport (375x812)...');
  await page.setViewport({ width: 375, height: 812 });
  await page.evaluate(() => {
    document.getElementById('how-it-works').scrollIntoView({ behavior: 'instant', block: 'start' });
  });
  await new Promise(r => setTimeout(r, 400));

  const mobileShot = path.join(SCREENSHOT_DIR, 'verify_methodology_mobile_375.png');
  await page.screenshot({ path: mobileShot });
  console.log(`Saved screenshot: ${mobileShot}`);

  // 5. Check full page to confirm NO gigantic black gaps anywhere
  await page.setViewport({ width: 1280, height: 900 });
  const fullPageShot = path.join(SCREENSHOT_DIR, 'verify_fullpage_layout.png');
  await page.screenshot({ path: fullPageShot, fullPage: true });
  console.log(`Saved full page screenshot: ${fullPageShot}`);

  console.log('Console Errors:', consoleErrors);
  await browser.close();
  console.log('--- Verification Completed Successfully! ---');
}

verify().catch(err => {
  console.error('Verification failed:', err);
  process.exit(1);
});
