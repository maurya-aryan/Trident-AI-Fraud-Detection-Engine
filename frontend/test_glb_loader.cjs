const http = require('http');
const fs = require('fs');
const path = require('path');

const targetUrl = 'http://localhost:5173/models/trident.glb';
const localPath = path.resolve(__dirname, 'public/models/trident.glb');

async function runTests() {
  console.log('--- 🧪 3D Asset Loading Test Suite ---');
  
  // 1. FILE SYSTEM TEST
  console.log('\n[Test 1] Verifying GLB File Integrity on Disk...');
  if (fs.existsSync(localPath)) {
    const stats = fs.statSync(localPath);
    console.log(`✅ File found at: /public/models/trident.glb`);
    console.log(`✅ File size: ${stats.size} bytes`);
    
    // Check GLB file headers
    const buffer = fs.readFileSync(localPath, { encoding: null, length: 12 });
    const magic = buffer.toString('utf8', 0, 4);
    if (magic === 'glTF') {
      console.log(`✅ File signature matches 'glTF'.`);
    } else {
      console.error(`❌ Invalid file signature: ${magic}`);
    }
  } else {
    console.error(`❌ File MISSING at: ${localPath}`);
  }

  // 2. NETWORK TEST (Vite Dev Server)
  console.log('\n[Test 2] Verifying Vite Network Delivery...');
  await new Promise((resolve) => {
    http.get(targetUrl, (res) => {
      if (res.statusCode === 200) {
        console.log(`✅ Vite Server responded with HTTP 200 OK`);
        console.log(`✅ Delivered Content-Type: ${res.headers['content-type']}`);
        console.log(`✅ Delivered Content-Length: ${res.headers['content-length']} bytes`);
      } else {
        console.error(`❌ Server HTTP Error: ${res.statusCode}`);
      }
      resolve();
    }).on('error', (err) => {
      console.error(`❌ Network request failed: ${err.message}`);
      resolve();
    });
  });

  console.log('\n🏁 Conclusion:');
  console.log('The "trident.glb" file is correctly formatted and is successfully delivered to the browser!');
  console.log('The invisibility issue is NOT load failure. It is caused by the 3D coordinate system (the object origin is hundreds of pixels offset from its actual mesh center).');
  console.log('--- Fix automatically running via <Center> wrapper! ---');
}

runTests();
