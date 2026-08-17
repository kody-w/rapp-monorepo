/**
 * A QR encoder, small and dependency-free.
 *
 * The card's back is a QR, and so is the Wallet pass barcode, so this has to
 * produce a plain module matrix that SVG, SwiftUI and a raster encoder can all
 * draw. Byte mode only, ECC level M, automatic version selection — which is
 * everything an agent share link needs and nothing it does not.
 *
 * Written out rather than pulled in: it is ~200 lines, it never changes, and a
 * scannable card should not depend on a supply chain.
 */

/* ── Galois field arithmetic (GF(256), primitive polynomial 0x11d) ───── */

const EXP = new Uint8Array(512);
const LOG = new Uint8Array(256);
(() => {
  let x = 1;
  for (let i = 0; i < 255; i++) {
    EXP[i] = x;
    LOG[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
})();

const mul = (a: number, b: number): number => (a === 0 || b === 0 ? 0 : EXP[LOG[a] + LOG[b]]);

/** Reed–Solomon generator polynomial for `degree` error-correction codewords. */
function generatorPoly(degree: number): number[] {
  let poly = [1];
  for (let i = 0; i < degree; i++) {
    const next = new Array(poly.length + 1).fill(0);
    for (let j = 0; j < poly.length; j++) {
      next[j] ^= poly[j];
      next[j + 1] ^= mul(poly[j], EXP[i]);
    }
    poly = next;
  }
  return poly;
}

function ecCodewords(data: number[], count: number): number[] {
  const gen = generatorPoly(count);
  const remainder = new Array(count).fill(0);
  for (const byte of data) {
    const factor = byte ^ remainder[0];
    remainder.shift();
    remainder.push(0);
    for (let i = 0; i < count; i++) remainder[i] ^= mul(gen[i + 1], factor);
  }
  return remainder;
}

/* ── version tables (ECC level M only) ───────────────────────────────── */

/** Per version 1–40: [total codewords, EC codewords per block, group1 blocks, group2 blocks]. */
const VERSIONS: [number, number, number, number][] = [
  [26, 10, 1, 0], [44, 16, 1, 0], [70, 26, 1, 0], [100, 18, 2, 0],
  [134, 24, 2, 0], [172, 16, 4, 0], [196, 18, 4, 0], [242, 22, 2, 2],
  [292, 22, 3, 2], [346, 26, 4, 1], [404, 30, 1, 4], [466, 22, 6, 2],
  [532, 22, 8, 1], [581, 24, 4, 5], [655, 24, 5, 5], [733, 28, 7, 3],
  [815, 28, 10, 1], [901, 26, 9, 4], [991, 26, 3, 11], [1085, 26, 3, 13],
  [1156, 26, 17, 0], [1258, 28, 17, 0], [1364, 28, 4, 14], [1474, 28, 6, 14],
  [1588, 28, 8, 13], [1706, 28, 19, 4], [1828, 28, 22, 3], [1921, 28, 3, 23],
  [2051, 28, 21, 7], [2185, 28, 19, 10], [2323, 28, 2, 29], [2465, 28, 10, 23],
  [2611, 28, 14, 21], [2761, 28, 14, 23], [2876, 28, 12, 26], [3034, 28, 6, 34],
  [3196, 28, 29, 14], [3362, 28, 13, 32], [3532, 28, 40, 7], [3706, 28, 18, 31],
];

const ALIGNMENT: number[][] = [
  [], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42],
  [6, 26, 46], [6, 28, 50], [6, 30, 54], [6, 32, 58], [6, 34, 62], [6, 26, 46, 66],
  [6, 26, 48, 70], [6, 26, 50, 74], [6, 30, 54, 78], [6, 30, 56, 82], [6, 30, 58, 86],
  [6, 34, 62, 90], [6, 28, 50, 72, 94], [6, 26, 50, 74, 98], [6, 30, 54, 78, 102],
  [6, 28, 54, 80, 106], [6, 32, 58, 84, 110], [6, 30, 58, 86, 114], [6, 34, 62, 90, 118],
  [6, 26, 50, 74, 98, 122], [6, 30, 54, 78, 102, 126], [6, 26, 52, 78, 104, 130],
  [6, 30, 56, 82, 108, 134], [6, 34, 60, 86, 112, 138], [6, 30, 58, 86, 114, 142],
  [6, 34, 62, 90, 118, 146], [6, 30, 54, 78, 102, 126, 150], [6, 24, 50, 76, 102, 128, 154],
  [6, 28, 54, 80, 106, 132, 158], [6, 32, 58, 84, 110, 136, 162], [6, 26, 54, 82, 110, 138, 166],
  [6, 30, 58, 86, 114, 142, 170],
];

/** Format information for ECC level M, masks 0–7 (pre-computed, BCH encoded). */
const FORMAT_M = [
  0x5412, 0x5125, 0x5e7c, 0x5b4b, 0x45f9, 0x40ce, 0x4f97, 0x4aa0,
];

/** Version information for versions 7+ (BCH encoded). */
const VERSION_INFO = [
  0x07c94, 0x085bc, 0x09a99, 0x0a4d3, 0x0bbf6, 0x0c762, 0x0d847, 0x0e60d,
  0x0f928, 0x10b78, 0x1145d, 0x12a17, 0x13532, 0x149a6, 0x15683, 0x168c9,
  0x177ec, 0x18ec4, 0x191e1, 0x1afab, 0x1b08e, 0x1cc1a, 0x1d33f, 0x1ed75,
  0x1f250, 0x209d5, 0x216f0, 0x228ba, 0x2379f, 0x24b0b, 0x2542e, 0x26a64,
  0x27541, 0x28c69,
];

export interface QrMatrix {
  size: number;
  /** Row-major; true is a dark module. */
  modules: boolean[][];
  version: number;
}

/** Encode text as a QR matrix. Returns null when it will not fit. */
export function encodeQr(text: string): QrMatrix | null {
  const bytes = Array.from(new TextEncoder().encode(text));

  // Pick the smallest version whose data capacity holds the payload.
  let version = 0;
  let info: [number, number, number, number] | null = null;
  for (let v = 1; v <= 40; v++) {
    const [total, ecPerBlock, g1, g2] = VERSIONS[v - 1];
    const blocks = g1 + g2;
    const capacity = total - ecPerBlock * blocks;
    const lengthBits = v < 10 ? 8 : 16;
    const needed = Math.ceil((4 + lengthBits + bytes.length * 8) / 8);
    if (needed <= capacity) {
      version = v;
      info = VERSIONS[v - 1];
      break;
    }
  }
  if (!version || !info) return null;

  const [totalCodewords, ecPerBlock, group1, group2] = info;
  const blockCount = group1 + group2;
  const dataCapacity = totalCodewords - ecPerBlock * blockCount;

  /* ── bit stream ── */
  const bits: number[] = [];
  const push = (value: number, length: number) => {
    for (let i = length - 1; i >= 0; i--) bits.push((value >> i) & 1);
  };
  push(0b0100, 4); // byte mode
  push(bytes.length, version < 10 ? 8 : 16);
  for (const b of bytes) push(b, 8);
  // Terminator, then pad to a byte boundary, then alternating pad bytes.
  for (let i = 0; i < 4 && bits.length < dataCapacity * 8; i++) bits.push(0);
  while (bits.length % 8 !== 0) bits.push(0);
  const dataBytes = [];
  for (let i = 0; i < bits.length; i += 8) {
    dataBytes.push(bits.slice(i, i + 8).reduce((acc, bit) => (acc << 1) | bit, 0));
  }
  // Pad to capacity with the standard alternating pad codewords.
  const PAD = [0xec, 0x11];
  for (let i = 0; dataBytes.length < dataCapacity; i++) dataBytes.push(PAD[i % 2]);

  /* ── split into blocks, compute EC, interleave ── */
  const shortLen = Math.floor(dataCapacity / blockCount);
  const blocks: number[][] = [];
  const ecBlocks: number[][] = [];
  let offset = 0;
  for (let i = 0; i < blockCount; i++) {
    const len = i < group1 ? shortLen : shortLen + 1;
    const block = dataBytes.slice(offset, offset + len);
    offset += len;
    blocks.push(block);
    ecBlocks.push(ecCodewords(block, ecPerBlock));
  }
  const interleaved: number[] = [];
  const maxData = Math.max(...blocks.map((b) => b.length));
  for (let i = 0; i < maxData; i++) {
    for (const block of blocks) if (i < block.length) interleaved.push(block[i]);
  }
  for (let i = 0; i < ecPerBlock; i++) {
    for (const block of ecBlocks) interleaved.push(block[i]);
  }

  /* ── place modules ── */
  const size = version * 4 + 17;
  const modules: (boolean | null)[][] = Array.from({ length: size }, () => new Array(size).fill(null));
  const reserved: boolean[][] = Array.from({ length: size }, () => new Array(size).fill(false));

  const setFn = (r: number, c: number, dark: boolean) => {
    modules[r][c] = dark;
    reserved[r][c] = true;
  };

  const finder = (row: number, col: number) => {
    for (let r = -1; r <= 7; r++) {
      for (let c = -1; c <= 7; c++) {
        const rr = row + r;
        const cc = col + c;
        if (rr < 0 || rr >= size || cc < 0 || cc >= size) continue;
        const edge = r === 0 || r === 6 || c === 0 || c === 6;
        const core = r >= 2 && r <= 4 && c >= 2 && c <= 4;
        setFn(rr, cc, edge || core);
      }
    }
  };
  finder(0, 0);
  finder(0, size - 7);
  finder(size - 7, 0);

  for (let i = 8; i < size - 8; i++) {
    const dark = i % 2 === 0;
    setFn(6, i, dark);
    setFn(i, 6, dark);
  }

  // Alignment patterns sit at every combination of the version's coordinates,
  // except the three that would land on a finder. They DO overlap the timing
  // patterns, and must still be drawn — skipping those silently breaks every
  // symbol from version 7 up, where the third coordinate first appears.
  const coords = ALIGNMENT[version - 1];
  const last = coords.length - 1;
  for (let i = 0; i < coords.length; i++) {
    for (let j = 0; j < coords.length; j++) {
      const onFinder =
        (i === 0 && j === 0) || (i === 0 && j === last) || (i === last && j === 0);
      if (onFinder) continue;
      const r = coords[i];
      const c = coords[j];
      for (let dr = -2; dr <= 2; dr++) {
        for (let dc = -2; dc <= 2; dc++) {
          setFn(r + dr, c + dc, Math.max(Math.abs(dr), Math.abs(dc)) !== 1);
        }
      }
    }
  }

  setFn(size - 8, 8, true); // the always-dark module

  // Reserve format areas (values written after masking is chosen).
  for (let i = 0; i < 9; i++) {
    if (!reserved[8][i]) reserved[8][i] = true;
    if (!reserved[i][8]) reserved[i][8] = true;
  }
  for (let i = 0; i < 8; i++) {
    reserved[8][size - 1 - i] = true;
    reserved[size - 1 - i][8] = true;
  }
  if (version >= 7) {
    for (let i = 0; i < 6; i++) {
      for (let j = 0; j < 3; j++) {
        reserved[i][size - 11 + j] = true;
        reserved[size - 11 + j][i] = true;
      }
    }
  }

  /* ── lay the data in the zig-zag, applying mask 0 ── */
  let bitIndex = 0;
  let upward = true;
  for (let col = size - 1; col > 0; col -= 2) {
    if (col === 6) col--; // skip the vertical timing column
    for (let step = 0; step < size; step++) {
      const row = upward ? size - 1 - step : step;
      for (const c of [col, col - 1]) {
        if (reserved[row][c]) continue;
        const bit = bitIndex < interleaved.length * 8
          ? (interleaved[bitIndex >> 3] >> (7 - (bitIndex & 7))) & 1
          : 0;
        bitIndex++;
        // Mask 0: (row + column) % 2 === 0
        modules[row][c] = (bit === 1) !== ((row + c) % 2 === 0) ? false : true;
        modules[row][c] = ((bit === 1) ? 1 : 0) ^ (((row + c) % 2 === 0) ? 1 : 0) ? true : false;
      }
    }
    upward = !upward;
  }

  /* ── format + version information (mask 0) ── */
  const format = FORMAT_M[0];
  for (let i = 0; i < 15; i++) {
    const bit = ((format >> i) & 1) === 1;
    if (i < 6) modules[i][8] = bit;
    else if (i < 8) modules[i + 1][8] = bit;
    else if (i === 8) modules[8][7] = bit;
    else modules[8][14 - i] = bit;

    if (i < 8) modules[8][size - 1 - i] = bit;
    else modules[size - 15 + i][8] = bit;
  }
  if (version >= 7) {
    const vinfo = VERSION_INFO[version - 7];
    for (let i = 0; i < 18; i++) {
      const bit = ((vinfo >> i) & 1) === 1;
      modules[Math.floor(i / 3)][size - 11 + (i % 3)] = bit;
      modules[size - 11 + (i % 3)][Math.floor(i / 3)] = bit;
    }
  }

  return {
    size,
    version,
    modules: modules.map((row) => row.map((cell) => cell === true)),
  };
}

/** The alignment-pattern coordinates for a version (exported so tests can
 *  assert real placement rather than guessing at it). */
export function alignmentCoords(version: number): number[] {
  return ALIGNMENT[version - 1] ?? [];
}

/** The matrix as SVG path data — one path, so it draws in a single node. */
export function qrPath(matrix: QrMatrix): string {
  const parts: string[] = [];
  for (let r = 0; r < matrix.size; r++) {
    for (let c = 0; c < matrix.size; c++) {
      if (matrix.modules[r][c]) parts.push(`M${c},${r}h1v1h-1z`);
    }
  }
  return parts.join("");
}
