import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { analisarCfem, centesimos, ContratoAnmError, CABECALHO_ANM } from '../src/cfem.mjs';

async function arquivo(body) {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'observatorio-cfem-'));
  const file = path.join(dir, 'CFEM_Arrecadacao.csv');
  await writeFile(file, Buffer.from(body, 'latin1'));
  return file;
}

test('arrecadação mantém grão mensal, ausência e meses nacionais; não fecha total anual incompleto', async () => {
  const file = await arquivo([CABECALHO_ANM, linha('2025','1','1502152','1.234,50'), linha('2025','1','3550308','3,00'), linha('2025','2','1502152','0,00')].map(c => c.map(v => `"${v}"`).join(',')).join('\r\n') + '\r\n');
  const { relatorio, mensais, anuais } = await analisarCfem(file);
  assert.equal(relatorio.linhas_lidas, 3);
  assert.deepEqual(relatorio.meses_nacionais['2025'], [1, 2]);
  assert.equal(mensais.length, 24);
  assert.equal(mensais.find(o => o.municipio_id === '1502152' && o.mes === 1).valor, 1234.5);
  assert.equal(mensais.find(o => o.municipio_id === '1502152' && o.mes === 2).natureza_valor, 'zero real');
  assert.equal(mensais.find(o => o.municipio_id === '1507151' && o.mes === 1).natureza_valor, 'ausente');
  assert.equal(mensais.find(o => o.municipio_id === '1507151' && o.mes === 1).valor, null);
  assert.equal(anuais.length, 0);
});

test('total anual existe só com doze meses nacionais e municipais', async () => {
  const rows = [CABECALHO_ANM, ...Array.from({ length: 12 }, (_, i) => linha('2024', String(i + 1), '1502152', '1,00'))];
  const file = await arquivo(rows.map(c => c.map(v => `"${v}"`).join(',')).join('\n') + '\n');
  const { anuais } = await analisarCfem(file);
  assert.equal(anuais.length, 1);
  assert.equal(anuais[0].municipio_id, '1502152');
  assert.equal(anuais[0].valor, 12);
});

test('coluna alterada, linha duplicada e valor inválido bloqueiam lote', async () => {
  const csv = rows => rows.map(c => c.map(v => `"${v}"`).join(',')).join('\n') + '\n';
  await assert.rejects(analisarCfem(await arquivo(csv([CABECALHO_ANM.map(x => x === 'CodigoMunicipio' ? 'CodigoEnte' : x), linha('2025','1','1502152','1,00')]))), ContratoAnmError);
  await assert.rejects(analisarCfem(await arquivo(csv([CABECALHO_ANM, linha('2025','1','1502152','1,00'), linha('2025','1','1502152','1,00')]))), /duplicadas/);
  await assert.rejects(analisarCfem(await arquivo(csv([CABECALHO_ANM, linha('2025','1','1502152','abc')]))), ContratoAnmError);
  assert.equal(centesimos('1.234,5678'), 12345678n);
});

function linha(ano, mes, codigo, valor) {
  const values = Object.fromEntries(CABECALHO_ANM.map(x => [x, '']));
  Object.assign(values, { Ano: ano, 'Mês': mes, CodigoMunicipio: codigo, ValorRecolhido: valor });
  return CABECALHO_ANM.map(x => values[x]);
}
