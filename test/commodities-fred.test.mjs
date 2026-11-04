import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, readFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { executarCommodities, extrairFred, ContratoFredError } from '../src/commodities-fred.mjs';

const key = 'a'.repeat(32);
const meta = serie => ({ seriess: [{ id: serie, frequency_short: 'M', units: 'U.S. Dollars per Metric Ton', last_updated: '2026-10-30' }] });
const data = () => ({ count: 3, observations: [{ date: '1991-12-01', value: '.' }, { date: '1992-01-01', value: '14.31' }, { date: '1992-02-01', value: '15.2' }] });

test('FRED preserva meses ausentes e publica série global provisória sem corte', async () => {
  const dataDir = await mkdtemp(path.join(os.tmpdir(), 'fred-'));
  const fetchFn = async url => {
    const parsed = new URL(url), serie = parsed.searchParams.get('series_id');
    assert.equal(parsed.searchParams.get('api_key'), key);
    return { ok: true, text: async () => JSON.stringify(parsed.pathname.endsWith('/observations') ? data() : meta(serie)) };
  };
  const r = await executarCommodities({ dataDir, apiKey: key, fetchFn, now: () => new Date('2026-10-30T12:00:00Z') });
  assert.equal(r.situacao, 'publicado_provisorio');
  assert.equal(r.nulos, 2);
  const rows = JSON.parse(await readFile(path.join(dataDir, 'publicado', 'commodities.json')));
  assert.equal(rows.length, 6);
  assert.equal(rows[0].municipio_id, null);
  assert.equal(rows[0].nivel_territorial, 'global');
  assert.equal(rows[0].natureza_valor, 'ausente');
  assert.equal(rows[1].valor, 14.31);
  assert.throws(() => extrairFred(meta('PIORECRUSDM'), { count: 2, observations: [data().observations[0], data().observations[0]] }, 'PIORECRUSDM', '2026-10-30'), ContratoFredError);
  await assert.rejects(executarCommodities({ dataDir, apiKey: key, fetchFn: async url => {
    const parsed = new URL(url), serie = parsed.searchParams.get('series_id');
    return { ok: true, text: async () => JSON.stringify(parsed.pathname.endsWith('/observations') && serie === 'PCOPPUSDM' ? { count: 0, observations: [] } : parsed.pathname.endsWith('/observations') ? data() : meta(serie)) };
  } }), ContratoFredError);
  assert.deepEqual(JSON.parse(await readFile(path.join(dataDir, 'publicado', 'commodities.json'))), rows);
  await assert.rejects(executarCommodities({ dataDir, apiKey: key, fetchFn: async () => { throw new Error(`Falha com chave ${key}`); } }), error => {
    assert.doesNotMatch(error.relatorio.erro, new RegExp(key));
    return true;
  });
});
