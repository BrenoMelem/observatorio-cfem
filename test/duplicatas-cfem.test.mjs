import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { CABECALHO_ANM } from '../src/cfem.mjs';
import { analisarDuplicatas } from '../scripts/analisar-duplicatas-cfem.mjs';

test('relatório confirma campos integrais sem exportar identificador', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'duplicatas-'));
  const file = path.join(dir, 'origem.csv'), destino = path.join(dir, 'relatorio.json');
  const linha = Object.fromEntries(CABECALHO_ANM.map(c => [c, '']));
  Object.assign(linha, { Ano: '2025', 'Mês': '9', CodigoMunicipio: '1505536', CPF_CNPJ: 'IDENTIFICADOR_FICTICIO', DataCriacao: '2025-10-01' });
  const values = CABECALHO_ANM.map(c => linha[c]);
  await writeFile(file, Buffer.from([CABECALHO_ANM, values, values].map(row => row.map(x => `"${x}"`).join(',')).join('\n'), 'latin1'));
  const result = await analisarDuplicatas(file, destino);
  assert.equal(result.duplicatas, 1);
  assert.equal(result.linhas_duplicadas[0].campos_identicos_incluindo_identificador, true);
  assert.equal(result.linhas_duplicadas[0].datas_criacao_iguais, true);
  assert.doesNotMatch(await readFile(destino, 'utf8'), /IDENTIFICADOR_FICTICIO|CPF_CNPJ/);
});
