const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'screenshots');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function capture() {
  console.log('Launching Chrome...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();

  // 1. Desktop Initial View (1280x900)
  console.log('Capturing Desktop Initial...');
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'before_desktop_initial.png'), fullPage: true });

  // 2. Desktop Detection Run Result
  console.log('Capturing Desktop Detection Result...');
  const analyzeBtn = await page.$('#analyzeBtn');
  if (analyzeBtn) {
    await analyzeBtn.click();
    await new Promise(r => setTimeout(r, 2000));
  }
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'before_desktop_result.png'), fullPage: false });

  // 3. Desktop Meme Tab
  console.log('Capturing Desktop Meme Tab...');
  const tabMeme = await page.$('#tabMemeMode');
  if (tabMeme) {
    await tabMeme.click();
    await new Promise(r => setTimeout(r, 1000));
  }
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'before_desktop_meme.png'), fullPage: false });

  // 4. Tablet (768x1024)
  console.log('Capturing Tablet (768px)...');
  await page.setViewport({ width: 768, height: 1024 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'before_tablet_768.png'), fullPage: true });

  // 5. Mobile (375x812)
  console.log('Capturing Mobile (375px)...');
  await page.setViewport({ width: 375, height: 812 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'before_mobile_375.png'), fullPage: true });

  // 6. ThoughtStream Dashboard (1280x900)
  console.log('Capturing ThoughtStream Dashboard...');
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8000/static/thoughtstream_dashboard.html', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'before_thoughtstream_dashboard.png'), fullPage: false });

  console.log('Done capturing before screenshots.');
  await browser.close();
}

capture().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
