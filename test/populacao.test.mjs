import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { MUNICIPIOS, ContratoSidraError, executar, extrairSidra, lerPublicado } from '../src/populacao.mjs';
import { criarServidor } from '../src/servidor.mjs';

const referenciaPath = new URL('../data/referencia-populacao-2025.json', import.meta.url);
const referencia = JSON.parse(await readFile(referenciaPath, 'utf8'));
function resposta(codigo, valor = referencia.valores[codigo]) {
  return [{ id: 9324, variavel: 'População residente estimada', unidade: 'Pessoas', resultados: [{ classificacoes: [], series: [{ localidade: { id: codigo, nome: `${MUNICIPIOS[codigo]} (PA)`, nivel: { id: 'N6', nome: 'Município' } }, serie: { '2025': String(valor) } }] }] }];
}
function fetchSimulado(alterar = x => x) {
  return async url => {
    const codigo = url.match(/N6%5B(\d{7})%5D/)?.[1];
    assert.ok(codigo, `URL inesperada: ${url}`);
    return { ok: true, text: async () => JSON.stringify(alterar(resposta(codigo), codigo)) };
  };
}
const dir = () => mkdtemp(path.join(os.tmpdir(), 'observatorio-pop-'));

test('contrato rejeita mudança de variável, unidade, município e estrutura', () => {
  const codigo = '1502152';
  for (const alterar of [
    p => { p[0].id = 999; },
    p => { p[0].unidade = 'Mil pessoas'; },
    p => { p[0].resultados[0].series[0].localidade.id = 1505536; },
    p => { delete p[0].resultados[0].series; },
  ]) {
    const payload = resposta(codigo);
    alterar(payload);
    assert.throws(() => extrairSidra(payload, codigo), ContratoSidraError);
  }
});

test('publica somente após conferir os 12 municípios com publicação independente; falha preserva último lote', async () => {
  const dataDir = await dir();
  const now = () => new Date('2026-10-30T12:00:00.000Z');
  const relatorio = await executar({ dataDir, referenciaPath, fetchFn: fetchSimulado(), now });
  assert.equal(relatorio.situacao, 'publicado');
  assert.equal(relatorio.municipios_presentes.length, 12);
  const anterior = await lerPublicado(dataDir);
  assert.equal(anterior.length, 12);
  assert.deepEqual(Object.keys(anterior[0]), ['indicador', 'municipio_id', 'municipio_nome', 'nivel_territorial', 'ano', 'mes', 'valor', 'unidade', 'natureza_valor', 'estado_validacao', 'fonte', 'edicao_fonte', 'atualizado_em', 'versao_tratamento']);
  await assert.rejects(executar({ dataDir, referenciaPath, now, fetchFn: fetchSimulado((p, codigo) => { if (codigo === '1502152') p[0].resultados[0].series[0].serie['2025'] = '99999'; return p; }) }), /Reconciliação falhou/);
  assert.deepEqual(await lerPublicado(dataDir), anterior);
  await assert.rejects(executar({ dataDir, referenciaPath, now, fetchFn: fetchSimulado((p, codigo) => { if (codigo === '1502152') p[0].unidade = 'Mil pessoas'; return p; }) }), ContratoSidraError);
  assert.deepEqual(await lerPublicado(dataDir), anterior);
});

test('API e CSV leem somente camada publicada e status informa ano e atualização', async () => {
  const dataDir = await dir();
  await executar({ dataDir, referenciaPath, fetchFn: fetchSimulado(), now: () => new Date('2026-10-30T12:00:00.000Z') });
  const server = criarServidor({ dataDir }).listen(0);
  try {
    await new Promise(resolve => server.once('listening', resolve));
    const base = `http://127.0.0.1:${server.address().port}`;
    const status = await (await fetch(`${base}/api/v1/status`)).json();
    assert.equal(status.ano_referencia, 2025);
    assert.equal(status.atualizado_em, '2026-10-30T12:00:00.000Z');
    const rows = await (await fetch(`${base}/api/v1/populacao`)).json();
    assert.equal(rows.length, 12);
    assert.equal(rows[0].natureza_valor, 'informado');
    const csv = await (await fetch(`${base}/api/v1/populacao.csv`)).text();
    assert.match(csv, /municipio_id/);
    assert.doesNotMatch(csv, /resultados|classificacoes|localidade/);
  } finally { server.close(); }
});
