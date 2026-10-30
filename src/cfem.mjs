import { createReadStream } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { MUNICIPIOS } from './populacao.mjs';

export class ContratoAnmError extends Error { name = 'ContratoAnmError'; }
export const CABECALHO_ANM = Object.freeze(['Ano', 'Mês', 'Processo', 'AnoDoProcesso', 'Tipo_PF_PJ', 'CPF_CNPJ', 'Substância', 'UF', 'CodigoMunicipio', 'Município', 'QuantidadeComercializada', 'UnidadeDeMedida', 'ValorRecolhido', 'DataCriacao']);
const codigoValido = new Set(Object.keys(MUNICIPIOS));

export async function* lerCsvAnm(file) {
  const stream = createReadStream(file);
  const decoder = new TextDecoder('windows-1252');
  let fields = [], field = '', quoted = false, afterQuote = false, pendingQuote = false;
  for await (const bytes of stream) {
    const chunk = decoder.decode(bytes, { stream: true });
    for (const ch of chunk) {
      if (pendingQuote) { quoted = false; afterQuote = true; pendingQuote = false; if (ch === '"') { field += '"'; quoted = true; afterQuote = false; continue; } }
      if (quoted) { if (ch === '"') pendingQuote = true; else field += ch; continue; }
      if (ch === '"' && !field && !afterQuote) { quoted = true; continue; }
      if (ch === ',') { fields.push(field); field = ''; afterQuote = false; continue; }
      if (ch === '\n') { fields.push(field.replace(/\r$/, '')); yield fields; fields = []; field = ''; afterQuote = false; continue; }
      if (ch === '\r' && afterQuote) continue;
      if (afterQuote && ch !== '\r') throw new ContratoAnmError('Caractere inesperado após aspas no CSV');
      field += ch;
    }
  }
  if (pendingQuote) { quoted = false; pendingQuote = false; }
  if (quoted) throw new ContratoAnmError('Aspas não fechadas no CSV');
  if (field || fields.length) { fields.push(field.replace(/\r$/, '')); yield fields; }
}

export function centesimos(raw) {
  if (!/^-?\d+(?:\.\d{3})*(?:,\d{1,4})?$/.test(raw)) throw new ContratoAnmError(`ValorRecolhido inválido: ${raw}`);
  const negativo = raw.startsWith('-');
  const [inteiro, fracao = ''] = raw.replace(/^-/, '').replaceAll('.', '').split(',');
  const unidades = BigInt(inteiro) * 10000n + BigInt(fracao.padEnd(4, '0'));
  return negativo ? -unidades : unidades;
}

export async function analisarCfem(file) {
  let headers, indexes, linhas = 0, nulos = 0, duplicatas = 0;
  const hash = createHash('sha256');
  const nationalMonths = new Map(), sums = new Map(), targetRows = new Set(), municipios = new Set(), anos = new Set(), duplicateGroups = new Map();
  for await (const cols of lerCsvAnm(file)) {
    if (!headers) {
      headers = cols.map((x, i) => i === 0 ? x.replace(/^\uFEFF/, '') : x);
      if (headers.length !== CABECALHO_ANM.length || headers.some((c, i) => c !== CABECALHO_ANM[i])) throw new ContratoAnmError(`Colunas ANM alteradas: ${JSON.stringify(headers)}`);
      indexes = Object.fromEntries(headers.map((name, i) => [name, i]));
      continue;
    }
    linhas++;
    if (cols.length !== headers.length) throw new ContratoAnmError(`Linha ${linhas}: ${cols.length} colunas; esperado ${headers.length}`);
    const ano = Number(cols[indexes.Ano]), mes = Number(cols[indexes['Mês']]);
    if (!Number.isInteger(ano) || !Number.isInteger(mes) || mes < 1 || mes > 12) throw new ContratoAnmError(`Linha ${linhas}: ano/mês inválidos`);
    if (ano >= 2003) {
      if (!nationalMonths.has(ano)) nationalMonths.set(ano, new Set());
      nationalMonths.get(ano).add(mes);
    }
    const codigo = cols[indexes.CodigoMunicipio];
    if (!codigoValido.has(codigo) || ano < 2003) continue;
    if (!cols[indexes.ValorRecolhido]) { nulos++; throw new ContratoAnmError(`Linha ${linhas}: valor nulo`); }
    const fingerprint = cols.join('\u001f');
    if (targetRows.has(fingerprint)) { duplicatas++; const grupo = `${codigo}:${ano}:${mes}`; duplicateGroups.set(grupo, (duplicateGroups.get(grupo) ?? 0) + 1); }
    else targetRows.add(fingerprint);
    const valor = centesimos(cols[indexes.ValorRecolhido]);
    const key = `${codigo}:${ano}:${mes}`;
    sums.set(key, (sums.get(key) ?? 0n) + valor);
    municipios.add(codigo); anos.add(ano);
    hash.update(fingerprint);
  }
  if (!headers) throw new ContratoAnmError('CSV vazio');
  const mesesNacionais = Object.fromEntries([...nationalMonths].sort((a,b) => a[0]-b[0]).map(([a, months]) => [a, [...months].sort((a,b) => a-b)]));
  const mensais = [];
  const anuais = [];
  for (const [ano, months] of [...nationalMonths].sort((a,b) => a[0]-b[0])) {
    for (const mes of [...months].sort((a,b) => a-b)) for (const codigo of Object.keys(MUNICIPIOS)) {
      const quantia = sums.get(`${codigo}:${ano}:${mes}`);
      const centavos = quantia === undefined ? null : (quantia >= 0n ? (quantia + 50n) / 100n : (quantia - 50n) / 100n);
      mensais.push({ indicador: 'cfem_arrecadada', municipio_id: codigo, municipio_nome: MUNICIPIOS[codigo], nivel_territorial: 'município', ano, mes, valor: centavos === null ? null : Number(centavos) / 100, unidade: 'BRL nominal', natureza_valor: centavos === null ? 'ausente' : centavos === 0n ? 'zero real' : 'informado', estado_validacao: 'provisório', fonte: 'ANM, CFEM_Arrecadacao.csv', edicao_fonte: String(ano), atualizado_em: null, versao_tratamento: '1.0.0' });
    }
    if (months.size === 12) for (const codigo of Object.keys(MUNICIPIOS)) {
      const valoresMensais = Array.from({ length: 12 }, (_, i) => sums.get(`${codigo}:${ano}:${i + 1}`));
      if (valoresMensais.some(v => v === undefined)) continue;
      const total = valoresMensais.reduce((a, b) => a + b, 0n);
      const centavos = total >= 0n ? (total + 50n) / 100n : (total - 50n) / 100n;
      anuais.push({ indicador: 'cfem_arrecadada', municipio_id: codigo, municipio_nome: MUNICIPIOS[codigo], nivel_territorial: 'município', ano, mes: null, valor: Number(centavos) / 100, unidade: 'BRL nominal', natureza_valor: centavos === 0n ? 'zero real' : 'informado', estado_validacao: 'provisório', fonte: 'ANM, CFEM_Arrecadacao.csv', edicao_fonte: String(ano), atualizado_em: null, versao_tratamento: '1.0.0' });
    }
  }
  const valores = mensais.filter(o => o.valor !== null).map(o => o.valor);
  const ausentesPorAno = Object.fromEntries([...nationalMonths].sort((a,b) => a[0]-b[0]).map(([ano, months]) => [ano, Object.keys(MUNICIPIOS).filter(codigo => [...months].every(mes => !sums.has(`${codigo}:${ano}:${mes}`)))]));
  const mesesAusentes = Object.fromEntries([...nationalMonths].sort((a,b) => a[0]-b[0]).flatMap(([ano, months]) => Object.keys(MUNICIPIOS).map(codigo => [`${codigo}:${ano}`, [...months].filter(mes => !sums.has(`${codigo}:${ano}:${mes}`)).sort((a,b) => a-b)]).filter(([, missing]) => missing.length)));
  const relatorio = { situacao: 'bloqueado', linhas_lidas: linhas, municipios_presentes: [...municipios].sort(), anos: [...anos].sort(), nulos, duplicatas, duplicatas_por_municipio_ano_mes: Object.fromEntries([...duplicateGroups].sort()), faixa_valores_mensais: valores.length ? { minimo: Math.min(...valores), maximo: Math.max(...valores) } : null, meses_nacionais: mesesNacionais, municipios_sem_linha_por_ano: ausentesPorAno, meses_ausentes_por_municipio_ano: mesesAusentes, linhas_no_recorte: targetRows.size, hash_recorte_sha256: hash.digest('hex'), divergencia_fonte_primaria: 'não reconciliada; publicação bloqueada' };
  if (duplicatas) throw Object.assign(new ContratoAnmError(`${duplicatas} linhas inteiras duplicadas no recorte; lote bloqueado`), { relatorio });
  return { relatorio, mensais, anuais };
}

export async function prepararCfem(file, dataDir = 'output/observatorio') {
  const dir = path.join(dataDir, 'tratado', 'cfem');
  await mkdir(dir, { recursive: true });
  let relatorio, mensais, anuais;
  try { ({ relatorio, mensais, anuais } = await analisarCfem(file)); }
  catch (error) { if (error.relatorio) await writeFile(path.join(dir, 'relatorio.json'), JSON.stringify(error.relatorio, null, 2) + '\n'); throw error; }
  await writeFile(path.join(dir, 'arrecadacao-mensal-provisoria.json'), JSON.stringify(mensais) + '\n');
  await writeFile(path.join(dir, 'arrecadacao-anual-provisoria.json'), JSON.stringify(anuais) + '\n');
  await writeFile(path.join(dir, 'relatorio.json'), JSON.stringify(relatorio, null, 2) + '\n');
  return relatorio;
}
