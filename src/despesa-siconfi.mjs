import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { MUNICIPIOS } from './populacao.mjs';

// Coleta de laboratório da DCA I-E. A seleção final de contas e a reconciliação
// independente ainda dependem de decisão; nenhum lote é homologado por este módulo.
export class ContratoSiconfiError extends Error { name = 'ContratoSiconfiError'; }
export const ESTAGIOS = Object.freeze({
  'Despesas Empenhadas': 'despesa_funcao_empenhada',
  'Despesas Liquidadas': 'despesa_funcao_liquidada',
  'Despesas Pagas': 'despesa_funcao_paga',
});

export function validarPagina(payload, codigo, ano, offset) {
  if (!payload || !Array.isArray(payload.items) || typeof payload.hasMore !== 'boolean') throw new ContratoSiconfiError('Paginação DCA alterada');
  if (payload.hasMore && (!payload.items.length || !Number.isSafeInteger(payload.limit) || payload.limit <= 0)) throw new ContratoSiconfiError('Paginação DCA inconsistente');
  for (const item of payload.items) {
    if (Number(item.exercicio) !== ano || String(item.cod_ibge) !== codigo || !String(item.anexo ?? '').includes('Anexo I-E')) throw new ContratoSiconfiError(`${codigo}: exercício, ente ou anexo divergente`);
    if (typeof item.conta !== 'string' || typeof item.coluna !== 'string' || item.valor === null || item.valor === '' || !Number.isFinite(Number(item.valor))) throw new ContratoSiconfiError(`${codigo}: contrato de conta, coluna ou valor alterado`);
  }
  if (offset > 100_000) throw new ContratoSiconfiError('Paginação DCA excedeu limite de segurança');
  return payload.items;
}

export async function executarDespesa({ dataDir = 'output/observatorio', ano = new Date().getUTCFullYear() - 1, fetchFn = fetch, now = () => new Date() } = {}) {
  if (!Number.isInteger(ano) || ano < 2013 || ano > new Date().getUTCFullYear()) throw new RangeError('Exercício inválido');
  const relDir = path.join(dataDir, 'qualidade');
  const brutoDir = path.join(dataDir, 'bruto', 'siconfi');
  const tratadoDir = path.join(dataDir, 'tratado', 'siconfi');
  await Promise.all([relDir, brutoDir, tratadoDir].map(dir => mkdir(dir, { recursive: true })));
  const execucao = now().toISOString().replace(/[:.]/g, '-') + '-' + Math.random().toString(36).slice(2, 8);
  const relatorio = { execucao, atualizado_em: now().toISOString(), indicador: 'despesa_por_funcao', exercicio: ano, situacao: 'bloqueado', linhas_lidas: 0, municipios_presentes: [], anos: [ano], nulos: 0, duplicatas: 0, faixa_valores: null, divergencia_fonte_primaria: 'Reconciliação independente pendente', pendencias: ['Seleção das contas e granularidade função/subfunção', 'Tratamento de retificações (RN-TMP-04)', 'Reconciliação independente (RN-VPU-07)'], erro: null };
  try {
    const todas = [];
    for (const codigo of Object.keys(MUNICIPIOS)) {
      let offset = 0, paginas = 0;
      while (true) {
        const params = new URLSearchParams({ an_exercicio: String(ano), id_ente: codigo, no_anexo: ano === 2013 ? 'Anexo I-E' : 'DCA-Anexo I-E', offset: String(offset), limit: '5000' });
        const response = await fetchFn(`https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?${params}`, { signal: AbortSignal.timeout(30_000), headers: { Accept: 'application/json' } });
        if (!response.ok) throw new ContratoSiconfiError(`${codigo}: HTTP ${response.status}`);
        const body = await response.text();
        await writeFile(path.join(brutoDir, `${execucao}-${codigo}-${paginas}.json`), body);
        let payload;
        try { payload = JSON.parse(body); } catch { throw new ContratoSiconfiError(`${codigo}: JSON inválido`); }
        const items = validarPagina(payload, codigo, ano, offset);
        todas.push(...items.filter(item => Object.hasOwn(ESTAGIOS, item.coluna)).map(item => ({ indicador: ESTAGIOS[item.coluna], municipio_id: codigo, municipio_nome: MUNICIPIOS[codigo], exercicio: ano, conta: item.conta, cod_conta: item.cod_conta, rotulo: item.rotulo, coluna: item.coluna, valor: Number(item.valor), anexo: item.anexo })));
        relatorio.linhas_lidas += items.length;
        offset += items.length; paginas++;
        if (!payload.hasMore) break;
        if (paginas > 100) throw new ContratoSiconfiError(`${codigo}: excesso de páginas`);
      }
      if (Object.values(ESTAGIOS).every(indicador => todas.some(item => item.municipio_id === codigo && item.indicador === indicador))) relatorio.municipios_presentes.push(codigo);
    }
    if (relatorio.municipios_presentes.length !== 12) throw new ContratoSiconfiError('DCA sem cobertura dos 12 municípios');
    const chaves = new Set();
    for (const row of todas) {
      const chave = `${row.municipio_id}\u001f${row.coluna}\u001f${row.rotulo}\u001f${row.conta}`;
      if (chaves.has(chave)) relatorio.duplicatas++;
      chaves.add(chave);
      if (row.valor === null) relatorio.nulos++;
    }
    if (relatorio.duplicatas || relatorio.nulos) throw new ContratoSiconfiError('Lote com duplicatas ou nulos');
    relatorio.faixa_valores = { minimo: Math.min(...todas.map(x => x.valor)), maximo: Math.max(...todas.map(x => x.valor)) };
    const destino = path.join(tratadoDir, `dca-${ano}.json`);
    const temporario = `${destino}.${execucao}.tmp`;
    await writeFile(temporario, JSON.stringify(todas, null, 2) + '\n');
    await rename(temporario, destino);
    return relatorio;
  } catch (error) {
    relatorio.erro = `${error.name}: ${error.message}`;
    throw Object.assign(error, { relatorio });
  } finally {
    await writeFile(path.join(relDir, `${execucao}-despesa-siconfi.json`), JSON.stringify(relatorio, null, 2) + '\n');
  }
}

export async function lerDespesaPublicada(dataDir) {
  try { return JSON.parse(await readFile(path.join(dataDir, 'publicado', 'despesa-siconfi.json'), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}
