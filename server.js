/* Tiny web server for Alpine Ascents. No packages needed, only Node.js.
   - serves the site on http://localhost:8080
   - keeps the shared visitor count in data/visitors.json
   run it with:  node server.js   (or npm start / start.bat) */
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const PORT = process.env.PORT || 8080;
const COUNT_FILE = path.join(ROOT, "data", "visitors.json");

const TYPES = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".mp4": "video/mp4", ".woff2": "font/woff2", ".woff": "font/woff", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8"
};

function readCount() {
  try { return JSON.parse(fs.readFileSync(COUNT_FILE, "utf8")); } catch (e) { return { count: 0, lastVisit: null }; }
}
function writeCount(obj) {
  // write to a temp file first so a crash cannot leave half a file behind
  const tmp = COUNT_FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2));
  fs.renameSync(tmp, COUNT_FILE);
}

function send(res, code, body, headers) {
  res.writeHead(code, Object.assign({ "Cache-Control": "no-cache" }, headers || {}));
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");

  if (url.pathname === "/api/visit") {
    let data = readCount();
    if (req.method === "POST" && url.searchParams.get("hit") === "1") {
      data = { count: (data.count || 0) + 1, lastVisit: new Date().toISOString() };
      writeCount(data);
    }
    return send(res, 200, JSON.stringify(data), { "Content-Type": "application/json", "Cache-Control": "no-store" });
  }

  let rel = decodeURIComponent(url.pathname);
  if (rel === "/") rel = "/index.html";
  const file = path.normalize(path.join(ROOT, rel));
  if (!file.startsWith(ROOT)) return send(res, 403, "Forbidden");

  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) return send(res, 404, "Not found", { "Content-Type": "text/plain" });
    const type = TYPES[path.extname(file).toLowerCase()] || "application/octet-stream";
    const range = req.headers.range; // video needs range requests, Safari refuses to play without them
    if (range) {
      const m = /bytes=(\d*)-(\d*)/.exec(range);
      let start = m[1] ? parseInt(m[1], 10) : 0;
      let end = m[2] ? parseInt(m[2], 10) : st.size - 1;
      if (isNaN(start) || start >= st.size || end >= st.size) { start = 0; end = st.size - 1; }
      res.writeHead(206, { "Content-Type": type, "Content-Range": `bytes ${start}-${end}/${st.size}`, "Accept-Ranges": "bytes", "Content-Length": end - start + 1 });
      return fs.createReadStream(file, { start, end }).pipe(res);
    }
    res.writeHead(200, { "Content-Type": type, "Content-Length": st.size, "Accept-Ranges": "bytes", "Cache-Control": "no-cache" });
    fs.createReadStream(file).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log("Alpine Ascents is running at http://localhost:" + PORT);
  console.log("Press Ctrl+C to stop.");
});
