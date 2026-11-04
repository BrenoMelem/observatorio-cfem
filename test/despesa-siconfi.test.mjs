import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, readFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { executarDespesa, validarPagina, ContratoSiconfiError } from '../src/despesa-siconfi.mjs';

test('DCA valida ente, anexo, estágio e mantém lote sem homologação', async () => {
  const dataDir = await mkdtemp(path.join(os.tmpdir(), 'dca-'));
  const fetchFn = async url => {
    const query = new URL(url).searchParams, codigo = query.get('id_ente'), ano = Number(query.get('an_exercicio'));
    const items = ['Despesas Empenhadas', 'Despesas Liquidadas', 'Despesas Pagas'].map((coluna, i) => ({ exercicio: ano, cod_ibge: codigo, anexo: 'DCA-Anexo I-E', conta: '12 - Educação', cod_conta: '12', coluna, valor: 100 - i }));
    return { ok: true, text: async () => JSON.stringify({ items, hasMore: false, limit: 5000 }) };
  };
  const relatorio = await executarDespesa({ dataDir, ano: 2025, fetchFn, now: () => new Date('2026-10-30T12:00:00Z') });
  assert.equal(relatorio.situacao, 'bloqueado');
  assert.equal(relatorio.municipios_presentes.length, 12);
  assert.equal(JSON.parse(await readFile(path.join(dataDir, 'tratado', 'siconfi', 'dca-2025.json'))).length, 36);
  await assert.rejects(readFile(path.join(dataDir, 'publicado', 'despesa-siconfi.json')), { code: 'ENOENT' });
  assert.throws(() => validarPagina({ items: [{ exercicio: 2025, cod_ibge: '1502152', anexo: 'DCA-Anexo I-E', conta: '12 - Educação', coluna: 'Despesas Pagas', valor: null }], hasMore: false }, '1502152', 2025, 0), ContratoSiconfiError);
});
