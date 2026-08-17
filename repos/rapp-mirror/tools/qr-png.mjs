import { deflateSync } from "node:zlib";
import { writeFileSync } from "node:fs";
import { encodeQr } from "/Users/kodywildfeuer/Documents/GitHub/rapp-mirror/common/qr.ts";

const text = process.argv[2];
const qr = encodeQr(text);
if (!qr) { console.error("no fit"); process.exit(2); }

const scale = 8, quiet = 4;
const dim = (qr.size + quiet * 2) * scale;

// 8-bit grayscale raw scanlines, each prefixed with filter byte 0
const raw = Buffer.alloc((dim + 1) * dim);
for (let y = 0; y < dim; y++) {
  raw[y * (dim + 1)] = 0;
  for (let x = 0; x < dim; x++) {
    const mr = Math.floor(y / scale) - quiet, mc = Math.floor(x / scale) - quiet;
    const dark = mr >= 0 && mr < qr.size && mc >= 0 && mc < qr.size && qr.modules[mr][mc];
    raw[y * (dim + 1) + 1 + x] = dark ? 0 : 255;
  }
}
const crcTable = Array.from({length:256},(_,n)=>{let c=n;for(let k=0;k<8;k++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0;});
const crc32 = (buf) => { let c = 0xffffffff; for (const b of buf) c = crcTable[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (type, data) => {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const body = Buffer.concat([Buffer.from(type, "ascii"), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
};
const ihdr = Buffer.alloc(13);
ihdr.writeUInt32BE(dim, 0); ihdr.writeUInt32BE(dim, 4);
ihdr[8] = 8; ihdr[9] = 0; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
writeFileSync(process.argv[3], Buffer.concat([
  Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]),
  chunk("IHDR", ihdr), chunk("IDAT", deflateSync(raw)), chunk("IEND", Buffer.alloc(0)),
]));
console.log(`wrote ${process.argv[3]} ${dim}x${dim} v${qr.version}`);
