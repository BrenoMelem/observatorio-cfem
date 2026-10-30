import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises';
import path from 'node:path';

export const MUNICIPIOS = Object.freeze({
  '1501576': 'Bom Jesus do Tocantins',
  '1501758': 'Brejo Grande do Araguaia',
  '1502152': 'Canaã dos Carajás',
  '1502772': 'Curionópolis',
  '1502954': 'Eldorado do Carajás',
  '1504208': 'Marabá',
  '1505494': 'Palestina do Pará',
  '1505536': 'Parauapebas',
  '1505635': 'Piçarra',
  '1507151': 'São Domingos do Araguaia',
  '1507458': 'São Geraldo do Araguaia',
  '1507508': 'São João do Araguaia',
});
export const CAMPOS = Object.freeze(['indicador', 'municipio_id', 'municipio_nome', 'nivel_territorial', 'ano', 'mes', 'valor', 'unidade', 'natureza_valor', 'estado_validacao', 'fonte', 'edicao_fonte', 'atualizado_em', 'versao_tratamento']);
const INDICADOR = 'populacao_estimada';
const VERSAO = '1.0.0';

export class ContratoSidraError extends Error { name = 'ContratoSidraError'; }
export class ValidacaoError extends Error { name = 'ValidacaoError'; }
const contrato = (ok, message) => { if (!ok) throw new ContratoSidraError(message); };
const valida = (ok, message) => { if (!ok) throw new ValidacaoError(message); };
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const sha = x => createHash('sha256').update(x).digest('hex');

export function extrairSidra(payload, codigo, anoAlvo) {
  contrato(Array.isArray(payload) && payload.length === 1, `${codigo}: resposta deve conter uma variável`);
  const variavel = payload[0];
  contrato(object(variavel) && String(variavel.id) === '9324', `${codigo}: variável SIDRA mudou`);
  contrato(variavel.unidade === 'Pessoas', `${codigo}: unidade SIDRA mudou`);
  contrato(Array.isArray(variavel.resultados) && variavel.resultados.length === 1, `${codigo}: resultados SIDRA mudaram`);
  const resultado = variavel.resultados[0];
  contrato(Array.isArray(resultado.classificacoes) && resultado.classificacoes.length === 0, `${codigo}: classificação inesperada`);
  contrato(Array.isArray(resultado.series) && resultado.series.length === 1, `${codigo}: séries SIDRA mudaram`);
  const serie = resultado.series[0];
  contrato(object(serie.localidade) && String(serie.localidade.id) === codigo, `${codigo}: código do município diverge`);
  contrato(serie.localidade.nome === `${MUNICIPIOS[codigo]} (PA)`, `${codigo}: nome do município diverge`);
  contrato(serie.localidade.nivel?.id === 'N6', `${codigo}: nível territorial diverge`);
  contrato(object(serie.serie) && Object.keys(serie.serie).length > 0, `${codigo}: períodos ausentes`);
  const anos = Object.keys(serie.serie);
  contrato(anos.every(ano => /^\d{4}$/.test(ano)), `${codigo}: período SIDRA mudou`);
  const ano = anoAlvo ?? Math.max(...anos.map(Number));
  contrato(anos.includes(String(ano)), `${codigo}: ano ${ano} ausente no SIDRA`);
  const valor = serie.serie[String(ano)];
  contrato(typeof valor === 'string' && /^\d+$/.test(valor), `${codigo}: valor do ano ${ano} inválido ou ausente`);
  return { ano, valor: Number(valor), linhas_lidas: anos.length };
}

export function validarLote(observacoes, anterior = []) {
  valida(observacoes.length === 12, 'Lote deve conter os 12 municípios');
  const chaves = new Set();
  for (const o of observacoes) {
    valida(Object.hasOwn(MUNICIPIOS, o.municipio_id), `Município fora do escopo: ${o.municipio_id}`);
    valida(o.municipio_nome === MUNICIPIOS[o.municipio_id], `Nome divergente: ${o.municipio_id}`);
    valida(Number.isSafeInteger(o.valor) && o.valor >= 1 && o.valor <= 5_000_000, `População fora da faixa plausível: ${o.municipio_id}`);
    valida(o.natureza_valor === 'informado' && o.estado_validacao === 'validado', `Estado inválido: ${o.municipio_id}`);
    valida(!chaves.has(o.municipio_id), `Município duplicado: ${o.municipio_id}`);
    chaves.add(o.municipio_id);
  }
  valida(new Set(observacoes.map(o => o.ano)).size === 1, 'Anos diferentes no lote');
  const novos = new Set(observacoes.map(o => `${o.ano}:${o.municipio_id}`));
  const mantidas = new Set(anterior.filter(o => o.ano !== observacoes[0].ano).map(o => `${o.ano}:${o.municipio_id}`));
  valida(novos.size + mantidas.size >= anterior.length, 'Série encolheu em relação à publicação anterior');
  return true;
}

export function reconciliar(observacoes, referencia) {
  valida(referencia?.fonte === `IBGE - Estimativas da População ${referencia?.ano}, publicação independente do SIDRA`, 'Fonte de reconciliação não identificada');
  valida(referencia.ano === observacoes[0].ano, 'Referência independente não cobre o ano mais recente');
  valida(Object.keys(referencia.valores ?? {}).length === 12, 'Referência independente incompleta');
  const divergencias = observacoes.filter(o => referencia.valores[o.municipio_id] !== o.valor).map(o => ({ municipio_id: o.municipio_id, sidra: o.valor, referencia: referencia.valores[o.municipio_id] }));
  valida(divergencias.length === 0, `Reconciliação falhou: ${JSON.stringify(divergencias)}`);
  return divergencias;
}

export async function executar({ dataDir = 'output/observatorio', fetchFn = fetch, referenciaPath, anoAlvo, now = () => new Date() } = {}) {
  const brutoDir = path.join(dataDir, 'bruto', 'sidra');
  const relDir = path.join(dataDir, 'qualidade');
  const pubDir = path.join(dataDir, 'publicado');
  await Promise.all([mkdir(brutoDir, { recursive: true }), mkdir(relDir, { recursive: true }), mkdir(pubDir, { recursive: true })]);
  const instante = now().toISOString();
  const execId = instante.replace(/[:.]/g, '-') + '-' + Math.random().toString(36).slice(2, 8);
  const relatorio = { execucao: execId, atualizado_em: instante, indicador: INDICADOR, situacao: 'bloqueado', linhas_lidas: 0, municipios_presentes: [], anos: [], nulos: 0, duplicatas: 0, faixa_valores: null, divergencia_fonte_primaria: null, erro: null };
  try {
    const anterior = await lerPublicado(dataDir);
    const extraidos = [];
    for (const codigo of Object.keys(MUNICIPIOS)) {
      const url = `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/all/variaveis/9324?localidades=N6%5B${codigo}%5D`;
      const response = await fetchFn(url, { signal: AbortSignal.timeout(30_000), headers: { Accept: 'application/json' } });
      contrato(response.ok, `${codigo}: HTTP ${response.status} do SIDRA`);
      const body = await response.text();
      await writeFile(path.join(brutoDir, `${execId}-${codigo}.json`), body, 'utf8');
      let payload;
      try { payload = JSON.parse(body); } catch { throw new ContratoSidraError(`${codigo}: JSON inválido`); }
      const dado = extrairSidra(payload, codigo, anoAlvo);
      extraidos.push({ codigo, ...dado, hash: sha(body) });
      relatorio.linhas_lidas += dado.linhas_lidas;
    }
    const observacoes = extraidos.map(({ codigo, ano, valor }) => ({ indicador: INDICADOR, municipio_id: codigo, municipio_nome: MUNICIPIOS[codigo], nivel_territorial: 'município', ano, mes: null, valor, unidade: 'pessoas', natureza_valor: 'informado', estado_validacao: 'validado', fonte: 'IBGE SIDRA, agregado 6579, variável 9324', edicao_fonte: String(ano), atualizado_em: instante, versao_tratamento: VERSAO }));
    relatorio.municipios_presentes = observacoes.map(o => o.municipio_id);
    relatorio.anos = [...new Set(observacoes.map(o => o.ano))];
    relatorio.faixa_valores = { minimo: Math.min(...observacoes.map(o => o.valor)), maximo: Math.max(...observacoes.map(o => o.valor)) };
    validarLote(observacoes, anterior);
    const caminhoReferencia = referenciaPath ?? `data/referencia-populacao-${observacoes[0].ano}.json`;
    const referencia = JSON.parse(await readFile(caminhoReferencia, 'utf8'));
    relatorio.divergencia_fonte_primaria = reconciliar(observacoes, referencia);
    const mantidas = anterior.filter(o => o.ano !== observacoes[0].ano);
    const publicado = [...mantidas, ...observacoes].sort((a, b) => a.ano - b.ano || a.municipio_id.localeCompare(b.municipio_id));
    const destino = path.join(pubDir, 'populacao.json');
    const temporario = path.join(pubDir, `${execId}.tmp`);
    await writeFile(temporario, JSON.stringify(publicado, null, 2) + '\n', 'utf8');
    await rename(temporario, destino);
    relatorio.situacao = 'publicado';
    relatorio.hashes_brutos = extraidos.map(({ codigo, hash }) => ({ municipio_id: codigo, sha256: hash }));
    return relatorio;
  } catch (error) {
    relatorio.erro = `${error.name}: ${error.message}`;
    throw Object.assign(error, { relatorio });
  } finally {
    await writeFile(path.join(relDir, `${execId}.json`), JSON.stringify(relatorio, null, 2) + '\n', 'utf8');
  }
}

export async function lerPublicado(dataDir) {
  try { return JSON.parse(await readFile(path.join(dataDir, 'publicado', 'populacao.json'), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}

export function csv(observacoes) {
  const escape = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return '\uFEFF' + [CAMPOS.join(','), ...observacoes.map(o => CAMPOS.map(c => escape(o[c])).join(','))].join('\n') + '\n';
}
