const puppeteer = require('puppeteer-core');
const path = require('path');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'screenshots');

async function test() {
  console.log('--- Testing Context Removal and Button Loading ---');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  await page.setViewport({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 600));

  // 1. Confirm conversation context elements are GONE from DOM
  const contextCheck = await page.evaluate(() => {
    return {
      hasAccordion: !!document.getElementById('contextAccordion'),
      hasTrigger: !!document.getElementById('contextTrigger'),
      hasInput: !!document.getElementById('contextInput'),
    };
  });
  console.log('Context Elements Check (all should be false):', contextCheck);

  if (contextCheck.hasAccordion || contextCheck.hasTrigger || contextCheck.hasInput) {
    throw new Error('Conversation context elements still found in DOM!');
  }

  // Scroll detector into view
  await page.evaluate(() => {
    document.getElementById('detector').scrollIntoView({ behavior: 'instant', block: 'start' });
  });
  await new Promise(r => setTimeout(r, 300));

  // Take screenshot of input form without conversation context
  const formShot = path.join(SCREENSHOT_DIR, 'verify_no_conversation_context.png');
  await page.screenshot({ path: formShot });
  console.log(`Saved screenshot: ${formShot}`);

  // 2. Click an example link to populate textarea
  console.log('Clicking example button...');
  await page.click('.example-link[data-example="direct_slur"]');
  await new Promise(r => setTimeout(r, 500));

  // 3. Monitor button loading text when Run detector is clicked
  console.log('Clicking Run detector button (#runDetectionBtn)...');
  
  // Track text updates over time
  const recordedButtonTexts = [];
  const captureInterval = setInterval(async () => {
    try {
      const text = await page.evaluate(() => {
        const btn = document.getElementById('runDetectionBtn');
        return btn ? btn.innerText.trim().replace(/\s+/g, ' ') : null;
      });
      if (text && (!recordedButtonTexts.length || recordedButtonTexts[recordedButtonTexts.length - 1] !== text)) {
        recordedButtonTexts.push(text);
      }
    } catch (e) {}
  }, 100);

  // Take a screenshot during loading
  const runClickPromise = page.click('#runDetectionBtn');
  await new Promise(r => setTimeout(r, 150));
  
  const loadingShot = path.join(SCREENSHOT_DIR, 'verify_button_loading_state.png');
  await page.screenshot({ path: loadingShot });
  console.log(`Saved loading state screenshot: ${loadingShot}`);

  await runClickPromise;
  console.log('Waiting for results loaded state...');
  await page.waitForFunction(() => {
    const loaded = document.getElementById('resultsLoadedState');
    return loaded && loaded.style.display !== 'none';
  }, { timeout: 15000 });
  clearInterval(captureInterval);

  console.log('Recorded Button Texts during execution:', recordedButtonTexts);

  // Check results loaded
  const resultsCheck = await page.evaluate(() => {
    const heading = document.getElementById('verdictHeading');
    const score = document.getElementById('verdictScore');
    const btn = document.getElementById('runDetectionBtn');
    return {
      verdictText: heading ? heading.innerText.trim() : null,
      score: score ? score.innerText.trim() : null,
      btnRestoredText: btn ? btn.innerText.trim().replace(/\s+/g, ' ') : null
    };
  });
  console.log('Results and Button Restored State:', resultsCheck);

  const finalShot = path.join(SCREENSHOT_DIR, 'verify_after_run_result.png');
  await page.screenshot({ path: finalShot });
  console.log(`Saved final result screenshot: ${finalShot}`);

  console.log('Console Errors:', consoleErrors);
  await browser.close();
  console.log('--- Test Completed Successfully! ---');
}

test().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
