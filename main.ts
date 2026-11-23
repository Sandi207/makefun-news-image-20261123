import { mkdirSync, copyFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
mkdirSync(outputDir, { recursive: true });
const source = join(dirname(fileURLToPath(import.meta.url)), 'entry.png');
const destination = resolve(outputDir, 'entry.png');
copyFileSync(source, destination);
console.log(destination);
