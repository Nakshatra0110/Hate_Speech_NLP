const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');

async function main() {
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const proc = spawn(edgePath, [
    '--headless',
    '--disable-gpu',
    '--remote-debugging-port=9222',
    '--window-size=1280,1000',
    'http://127.0.0.1:8000'
  ]);

  await new Promise(r => setTimeout(r, 2000));

  http.get('http://127.0.0.1:9222/json', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', async () => {
      try {
        const list = JSON.parse(data);
        const page = list.find(p => p.type === 'page');
        const ws = new (require('ws'))(page.webSocketDebuggerUrl);
        let id = 1;
        function send(method, params = {}) {
          return new Promise(resolve => {
            const reqId = id++;
            const handler = (msg) => {
              const res = JSON.parse(msg);
              if (res.id === reqId) {
                ws.off('message', handler);
                resolve(res.result);
              }
            };
            ws.on('message', handler);
            ws.send(JSON.stringify({ id: reqId, method, params }));
          });
        }

        ws.on('open', async () => {
          // Click meme tab
          await send('Runtime.evaluate', {
            expression: `
              document.getElementById('tabMemeBtn').click();
            `
          });

          await new Promise(r => setTimeout(r, 800));

          const shot = await send('Page.captureScreenshot', { format: 'png' });
          if (shot && shot.data) {
            fs.writeFileSync('scratch/screenshot_meme_tab.png', Buffer.from(shot.data, 'base64'));
            console.log('Saved scratch/screenshot_meme_tab.png');
          }
          ws.close();
          proc.kill();
        });
      } catch (err) {
        console.error(err);
        proc.kill();
      }
    });
  }).on('error', e => {
    console.error(e);
    proc.kill();
  });
}

main();
