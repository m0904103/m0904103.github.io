const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const fs = require('fs');

const html = fs.readFileSync('c:/Users/manpo/OneDrive/桌面/AI_Stock_Scanner_Cloud/frontend/dist/index.html', 'utf8');

const virtualConsole = new jsdom.VirtualConsole();
virtualConsole.on("error", (err) => {
  console.error("JSDOM Error:", err);
});
virtualConsole.on("log", (msg) => {
  console.log("JSDOM Log:", msg);
});

const dom = new JSDOM(html, {
  runScripts: "dangerously",
  resources: "usable",
  url: "http://localhost/",
  virtualConsole
});

setTimeout(() => {
  console.log("Root content:", dom.window.document.getElementById('root').innerHTML.substring(0, 100));
  process.exit(0);
}, 3000);
