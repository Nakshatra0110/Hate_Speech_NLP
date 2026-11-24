const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'screenshots');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function capture() {
  console.log('Launching Chrome for After Screenshots...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();

  // 1. Desktop Initial View (1280x900) - Full Page
  console.log('Capturing After Desktop Initial...');
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'after_desktop_initial.png'), fullPage: true });

  // 2. Desktop Detection Result
  console.log('Capturing After Desktop Detection Result...');
  const runBtn = await page.$('#runDetectionBtn');
  if (runBtn) {
    await runBtn.click();
    await new Promise(r => setTimeout(r, 2500));
  }
  // Scroll to detector section
  await page.evaluate(() => {
    const el = document.getElementById('detector');
    if (el) el.scrollIntoView();
  });
  await new Promise(r => setTimeout(r, 600));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'after_desktop_result.png'), fullPage: false });

  // 3. Desktop Meme Tab
  console.log('Capturing After Desktop Meme Tab...');
  const tabMeme = await page.$('#tabMemeBtn');
  if (tabMeme) {
    await tabMeme.click();
    await new Promise(r => setTimeout(r, 1200));
  }
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'after_desktop_meme.png'), fullPage: false });

  // 4. Tablet (768x1024) - Full Page
  console.log('Capturing After Tablet (768px)...');
  await page.setViewport({ width: 768, height: 1024 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'after_tablet_768.png'), fullPage: true });

  // 5. Mobile (375x812) - Full Page
  console.log('Capturing After Mobile (375px)...');
  await page.setViewport({ width: 375, height: 812 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'after_mobile_375.png'), fullPage: true });

  // 6. ThoughtStream Dashboard (1280x900)
  console.log('Capturing After ThoughtStream Dashboard...');
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8000/static/thoughtstream_dashboard.html', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'after_thoughtstream_dashboard.png'), fullPage: false });

  console.log('Done capturing all After screenshots!');
  await browser.close();
}

capture().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
