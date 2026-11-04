import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { CAMPOS } from './populacao.mjs';

// Protótipo local das séries globais FRED; publicação provisória até reconciliação independente.
export class ContratoFredError extends Error { name = 'ContratoFredError'; }
export const SERIES = Object.freeze({ PIORECRUSDM: { indicador: 'preco_minerio_ferro', unidade: 'USD/dmt' }, PCOPPUSDM: { indicador: 'preco_cobre', unidade: 'USD/t' } });

export function extrairFred(meta, body, serie, instante) {
  const config = SERIES[serie];
  if (!config || !Array.isArray(meta?.seriess) || meta.seriess.length !== 1 || meta.seriess[0].id !== serie || meta.seriess[0].frequency_short !== 'M' || meta.seriess[0].units !== 'U.S. Dollars per Metric Ton') throw new ContratoFredError(`${serie}: metadados inesperados`);
  if (!Array.isArray(body?.observations) || !body.observations.length || Number(body.count) !== body.observations.length) throw new ContratoFredError(`${serie}: observações incompletas ou paginação inesperada`);
  const chaves = new Set(), rows = [];
  for (const item of body.observations) {
    if (!/^\d{4}-\d{2}-01$/.test(item.date) || typeof item.value !== 'string') throw new ContratoFredError(`${serie}: data ou valor inválido`);
    const [ano, mes] = item.date.split('-').map(Number);
    if (mes < 1 || mes > 12 || chaves.has(item.date)) throw new ContratoFredError(`${serie}: mês inválido ou duplicado`);
    chaves.add(item.date);
    const valor = item.value === '.' ? null : Number(item.value);
    if (valor !== null && (!Number.isFinite(valor) || valor < 0)) throw new ContratoFredError(`${serie}: preço inválido`);
    rows.push({ indicador: config.indicador, municipio_id: null, municipio_nome: null, nivel_territorial: 'global', ano, mes, valor, unidade: config.unidade, natureza_valor: valor === null ? 'ausente' : valor === 0 ? 'zero real' : 'informado', estado_validacao: 'provisório', fonte: `FRED, série ${serie} (IMF)`, edicao_fonte: meta.seriess[0].last_updated ?? null, atualizado_em: instante, versao_tratamento: '1.0.0' });
  }
  rows.sort((a, b) => a.ano - b.ano || a.mes - b.mes);
  for (let i = 1; i < rows.length; i++) if (rows[i].ano * 12 + rows[i].mes !== rows[i - 1].ano * 12 + rows[i - 1].mes + 1) throw new ContratoFredError(`${serie}: lacuna na sequência mensal`);
  return rows;
}

export async function executarCommodities({ dataDir = 'output/observatorio', apiKey = process.env.FRED_API_KEY, fetchFn = fetch, now = () => new Date() } = {}) {
  if (!apiKey || !/^[a-z0-9]{32}$/.test(apiKey)) throw new Error('FRED_API_KEY ausente ou inválida');
  const relDir = path.join(dataDir, 'qualidade'), brutoDir = path.join(dataDir, 'bruto', 'fred'), pubDir = path.join(dataDir, 'publicado');
  await Promise.all([relDir, brutoDir, pubDir].map(dir => mkdir(dir, { recursive: true })));
  const instante = now().toISOString(), execucao = instante.replace(/[:.]/g, '-') + '-' + Math.random().toString(36).slice(2, 8);
  const relatorio = { execucao, atualizado_em: instante, indicador: 'commodities', situacao: 'bloqueado', linhas_lidas: 0, municipios_presentes: [], anos: [], nulos: 0, duplicatas: 0, faixa_valores: {}, divergencia_fonte_primaria: 'Reconciliação independente pendente; valores provisórios', pendencia_ferro: 'Divergência 17: início em 1980 ou 1992 e recorte de exibição em aberto; nenhuma linha foi cortada.', erro: null };
  try {
    const todos = [];
    for (const serie of Object.keys(SERIES)) {
      const get = async endpoint => {
        const url = `https://api.stlouisfed.org/fred/series${endpoint}?${new URLSearchParams({ series_id: serie, api_key: apiKey, file_type: 'json' })}`;
        const response = await fetchFn(url, { signal: AbortSignal.timeout(30_000), headers: { Accept: 'application/json' } });
        if (!response.ok) throw new ContratoFredError(`${serie}: HTTP ${response.status}`);
        const body = await response.text();
        await writeFile(path.join(brutoDir, `${execucao}-${serie}-${endpoint ? 'observations' : 'meta'}.json`), body);
        try { return JSON.parse(body); } catch { throw new ContratoFredError(`${serie}: JSON inválido`); }
      };
      const meta = await get(''), observations = await get('/observations');
      const rows = extrairFred(meta, observations, serie, instante);
      todos.push(...rows);
      relatorio.linhas_lidas += rows.length;
      relatorio.nulos += rows.filter(row => row.valor === null).length;
      const valores = rows.filter(row => row.valor !== null).map(row => row.valor);
      relatorio.faixa_valores[serie] = valores.length ? { minimo: Math.min(...valores), maximo: Math.max(...valores) } : null;
      if (!valores.length) throw new ContratoFredError(`${serie}: série sem valores`);
    }
    relatorio.anos = [...new Set(todos.map(row => row.ano))].sort((a, b) => a - b);
    const destino = path.join(pubDir, 'commodities.json'), tmp = path.join(pubDir, `${execucao}-commodities.tmp`);
    await writeFile(tmp, JSON.stringify(todos, null, 2) + '\n');
    await rename(tmp, destino);
    relatorio.situacao = 'publicado_provisorio';
    return relatorio;
  } catch (error) {
    relatorio.erro = `${error.name}: ${String(error.message).replaceAll(apiKey, '[REDACTED]')}`;
    throw Object.assign(error, { relatorio });
  } finally {
    await writeFile(path.join(relDir, `${execucao}-commodities.json`), JSON.stringify(relatorio, null, 2) + '\n');
  }
}

export async function lerCommoditiesPublicadas(dataDir) {
  try { return JSON.parse(await readFile(path.join(dataDir, 'publicado', 'commodities.json'), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}

export function csvCommodities(rows) {
  const escape = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return '\uFEFF' + [CAMPOS.join(','), ...rows.map(row => CAMPOS.map(campo => escape(row[campo])).join(','))].join('\n') + '\n';
}
