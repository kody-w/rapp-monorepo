import assert from "node:assert/strict";
import http from "node:http";
import test from "node:test";

import { transcribe, whisperAvailable } from "./stt.ts";

test("transcribe posts multipart wav to /inference and reads text", async () => {
  let sawContentType = "";
  let sawBytes = 0;
  const server = http.createServer((req, res) => {
    if (req.url === "/inference") {
      sawContentType = String(req.headers["content-type"]);
      req.on("data", (c) => (sawBytes += c.length));
      req.on("end", () => {
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ text: "  hello mirror  " }));
      });
    } else {
      res.end("whisper.cpp server");
    }
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const prev = process.env.WHISPER_URL;
  process.env.WHISPER_URL = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
  try {
    assert.equal(await whisperAvailable(), true);
    const text = await transcribe(new Uint8Array([82, 73, 70, 70, 0, 0]));
    assert.equal(text, "hello mirror");
    assert.match(sawContentType, /multipart\/form-data/);
    assert.ok(sawBytes > 0);
  } finally {
    server.close();
    if (prev === undefined) delete process.env.WHISPER_URL; else process.env.WHISPER_URL = prev;
  }
});

test("whisperAvailable is false when nothing listens", async () => {
  const prev = process.env.WHISPER_URL;
  process.env.WHISPER_URL = "http://127.0.0.1:1";
  try {
    assert.equal(await whisperAvailable(), false);
  } finally {
    if (prev === undefined) delete process.env.WHISPER_URL; else process.env.WHISPER_URL = prev;
  }
});
