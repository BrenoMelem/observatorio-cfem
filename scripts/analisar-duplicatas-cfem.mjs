/** Analisa duplicatas da arrecadação ANM para decisão humana; nunca exporta identificadores pessoais. */
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { CABECALHO_ANM, lerCsvAnm } from '../src/cfem.mjs';
import { MUNICIPIOS } from '../src/populacao.mjs';

export async function analisarDuplicatas(file, destino = 'output/observatorio/qualidade/duplicatas-cfem.json') {
  const vistos = new Map(), totais = new Map(), duplicatas = [];
  let cabecalho = false, linha = 0;
  for await (const cols of lerCsvAnm(file)) {
    if (!cabecalho) {
      const nomes = cols.map((x, i) => i === 0 ? x.replace(/^\uFEFF/, '') : x);
      if (nomes.length !== 14 || nomes.some((x, i) => x !== CABECALHO_ANM[i])) throw new Error('Cabeçalho ANM alterado');
      cabecalho = true;
      continue;
    }
    linha++;
    if (cols.length !== 14) throw new Error(`Linha ${linha}: quantidade de campos alterada`);
    const [ano, mes, codigo] = [Number(cols[0]), Number(cols[1]), cols[8]];
    if (!Object.hasOwn(MUNICIPIOS, codigo) || ano < 2003) continue;
    if (!Number.isInteger(ano) || !Number.isInteger(mes) || mes < 1 || mes > 12) throw new Error(`Linha ${linha}: período inválido`);
    const resumo = totais.get(ano) ?? { linhas_recorte: 0, duplicatas: 0 };
    resumo.linhas_recorte++;
    totais.set(ano, resumo);
    // A chave só existe em memória. JSON.stringify preserva a igualdade de todos os 14 campos.
    const chave = JSON.stringify(cols);
    const primeira = vistos.get(chave);
    if (primeira) {
      resumo.duplicatas++;
      duplicatas.push({ municipio_id: codigo, municipio_nome: MUNICIPIOS[codigo], ano, mes, linha_original: primeira.linha, linha_duplicada: linha, data_criacao_original: primeira.data, data_criacao_duplicada: cols[13], datas_criacao_iguais: primeira.data === cols[13], campos_identicos_incluindo_identificador: true });
    } else vistos.set(chave, { linha, data: cols[13] });
  }
  if (!cabecalho) throw new Error('CSV vazio');
  const relatorio = { finalidade: 'Insumo para decisão do mantenedor; nenhuma duplicata foi removida e nenhum lote foi liberado.', linhas_lidas: linha, duplicatas: duplicatas.length, por_ano: Object.fromEntries([...totais].sort((a, b) => a[0] - b[0])), linhas_duplicadas: duplicatas };
  await mkdir(path.dirname(destino), { recursive: true });
  await writeFile(destino, JSON.stringify(relatorio, null, 2) + '\n');
  return relatorio;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const file = process.argv[2] ?? 'tmp/CFEM_Arrecadacao.csv';
  const destino = process.argv[3] ?? 'output/observatorio/qualidade/duplicatas-cfem.json';
  try {
    const r = await analisarDuplicatas(file, destino);
    console.log(`CFEM arrecadada: ${r.linhas_lidas} linhas nacionais; ${[...Object.values(r.por_ano)].reduce((n, x) => n + x.linhas_recorte, 0)} linhas no recorte; ${r.duplicatas} duplicatas integrais. Relatório: ${destino}. Tratamento pendente de decisão do mantenedor.`);
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
