import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { criarServidor } from '../src/servidor.mjs';

test('painel itera o manifesto; commodities globais e despesa bloqueada na API', async () => {
  const dataDir = await mkdtemp(path.join(os.tmpdir(), 'painel-'));
  await mkdir(path.join(dataDir, 'publicado'));
  await writeFile(path.join(dataDir, 'publicado', 'commodities.json'), JSON.stringify([{ indicador: 'preco_cobre', municipio_id: null, ano: 2025, mes: 9, valor: 8000, estado_validacao: 'provisório', atualizado_em: '2026-10-30T12:00:00.000Z' }]));
  const server = criarServidor({ dataDir }).listen(0);
  try {
    await new Promise(resolve => server.once('listening', resolve));
    const base = `http://127.0.0.1:${server.address().port}`;
    const html = await (await fetch(`${base}/status`)).text();
    assert.match(html, /População residente estimada/);
    assert.match(html, /Preço internacional do cobre/);
    assert.match(html, /2025/);
    assert.match(html, /Sem publicação/);
    const result = await fetch(`${base}/api/v1/commodities?indicador=preco_cobre`);
    assert.equal(result.status, 200);
    assert.equal((await result.json()).length, 1);
    assert.equal((await fetch(`${base}/api/v1/despesa-funcao`)).status, 503);
  } finally { server.close(); }
});
