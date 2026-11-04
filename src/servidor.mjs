import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { csv, lerPublicado } from './populacao.mjs';
import { csvCommodities, lerCommoditiesPublicadas } from './commodities-fred.mjs';
import { lerDespesaPublicada } from './despesa-siconfi.mjs';

const manifestDefault = new URL('../data/indicadores.json', import.meta.url);
const escapeHtml = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
const json = value => JSON.stringify(value);

export function criarServidor({ dataDir = 'output/observatorio', manifestPath = manifestDefault } = {}) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const enviar = (status, tipo, body) => { res.writeHead(status, { 'Content-Type': tipo, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' }); res.end(body); };
    try {
      if (url.pathname === '/api/v1/populacao' || url.pathname === '/api/v1/populacao.csv') {
        const rows = await lerPublicado(dataDir);
        if (!rows.length) return enviar(503, 'application/json; charset=utf-8', json({ erro: 'Nenhum lote homologado publicado' }));
        if (url.pathname.endsWith('.csv')) return enviar(200, 'text/csv; charset=utf-8', csv(rows));
        const municipio = url.searchParams.get('municipio_id');
        if (municipio && !/^\d{7}$/.test(municipio)) return enviar(400, 'application/json; charset=utf-8', json({ erro: 'municipio_id inválido' }));
        return enviar(200, 'application/json; charset=utf-8', json(rows.filter(o => !municipio || o.municipio_id === municipio)));
      }
      if (url.pathname === '/api/v1/commodities' || url.pathname === '/api/v1/commodities.csv') {
        const rows = await lerCommoditiesPublicadas(dataDir);
        if (!rows.length) return enviar(503, 'application/json; charset=utf-8', json({ erro: 'Nenhuma série provisória publicada' }));
        const indicador = url.searchParams.get('indicador');
        if (indicador && !['preco_minerio_ferro', 'preco_cobre'].includes(indicador)) return enviar(400, 'application/json; charset=utf-8', json({ erro: 'indicador inválido' }));
        const filtradas = rows.filter(o => !indicador || o.indicador === indicador);
        return url.pathname.endsWith('.csv') ? enviar(200, 'text/csv; charset=utf-8', csvCommodities(filtradas)) : enviar(200, 'application/json; charset=utf-8', json(filtradas));
      }
      if (url.pathname === '/api/v1/despesa-funcao') {
        const rows = await lerDespesaPublicada(dataDir);
        if (!rows.length) return enviar(503, 'application/json; charset=utf-8', json({ erro: 'Despesa por função aguarda definição de contas e reconciliação independente' }));
        const indicador = url.searchParams.get('indicador');
        if (indicador && !['despesa_funcao_empenhada', 'despesa_funcao_liquidada', 'despesa_funcao_paga'].includes(indicador)) return enviar(400, 'application/json; charset=utf-8', json({ erro: 'indicador inválido' }));
        return enviar(200, 'application/json; charset=utf-8', json(rows.filter(o => !indicador || o.indicador === indicador)));
      }
      if (url.pathname === '/api/v1/status') {
        const rows = await lerPublicado(dataDir);
        const ano = rows.length ? Math.max(...rows.map(o => o.ano)) : null;
        const atualizado_em = rows.length ? rows.map(o => o.atualizado_em).sort().at(-1) : null;
        return enviar(200, 'application/json; charset=utf-8', json({ indicador: 'populacao_estimada', situacao: rows.length ? 'publicado' : 'sem_publicacao', ano_referencia: ano, atualizado_em }));
      }
      if (url.pathname === '/status') {
        const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
        const [pop, commodities, despesa] = await Promise.all([lerPublicado(dataDir), lerCommoditiesPublicadas(dataDir), lerDespesaPublicada(dataDir)]);
        const dados = { populacao_estimada: pop, preco_minerio_ferro: commodities.filter(o => o.indicador === 'preco_minerio_ferro'), preco_cobre: commodities.filter(o => o.indicador === 'preco_cobre') };
        for (const indicador of ['despesa_funcao_empenhada', 'despesa_funcao_liquidada', 'despesa_funcao_paga']) dados[indicador] = despesa.filter(o => o.indicador === indicador);
        const linhas = Object.entries(manifest).map(([indicador, definicao]) => {
          const rows = dados[indicador] ?? [];
          const ano = rows.length ? Math.max(...rows.map(o => o.ano)) : null;
          const atualizado = rows.length ? rows.map(o => o.atualizado_em).filter(Boolean).sort().at(-1) : null;
          const situacao = rows.length ? rows.every(o => o.estado_validacao === 'provisório') ? 'Provisório' : 'Publicado' : 'Sem publicação';
          return `<tr><td>${escapeHtml(definicao.nome)}</td><td>${situacao}</td><td>${ano ?? '—'}</td><td>${atualizado ? escapeHtml(atualizado) : '—'}</td></tr>`;
        }).join('');
        return enviar(200, 'text/html; charset=utf-8', `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Status do Observatório</title><main><h1>Status dos indicadores</h1><table><caption>Publicações por indicador</caption><thead><tr><th>Indicador</th><th>Situação</th><th>Ano de referência</th><th>Última atualização</th></tr></thead><tbody>${linhas}</tbody></table><p><a href="/api/v1/populacao.csv">Baixar CSV da população</a></p></main></html>`);
      }
      return enviar(404, 'application/json; charset=utf-8', json({ erro: 'Rota não encontrada' }));
    } catch {
      return enviar(500, 'application/json; charset=utf-8', json({ erro: 'Falha ao ler camada publicada' }));
    }
  });
}
