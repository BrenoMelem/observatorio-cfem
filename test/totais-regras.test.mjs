import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { checarTotais } from '../scripts/checar-totais-regras.mjs';

test('checagem detecta divergência entre regras e linha Total', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'regras-'));
  await writeFile(path.join(dir, 'tema.md'), '### RN-XXX-01\n- **Status:** DECIDIDA\n');
  await writeFile(path.join(dir, 'README.md'), 'Total: 1 regras, sendo 1 DECIDIDAS, 0 PROPOSTAS e 0 EM ABERTO.\n');
  assert.equal((await checarTotais(dir)).confere, true);
  await writeFile(path.join(dir, 'README.md'), 'Total: 2 regras, sendo 2 DECIDIDAS, 0 PROPOSTAS e 0 EM ABERTO.\n');
  assert.equal((await checarTotais(dir)).confere, false);
});
