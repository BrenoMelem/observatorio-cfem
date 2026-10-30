import http from 'node:http';
import { csv, lerPublicado } from './populacao.mjs';

export function criarServidor({ dataDir = 'output/observatorio' } = {}) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const rows = await lerPublicado(dataDir);
    const enviar = (status, tipo, body) => { res.writeHead(status, { 'Content-Type': tipo, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' }); res.end(body); };
    if (url.pathname === '/api/v1/populacao') {
      if (!rows.length) return enviar(503, 'application/json; charset=utf-8', JSON.stringify({ erro: 'Nenhum lote homologado publicado' }));
      const municipio = url.searchParams.get('municipio_id');
      if (municipio && !/^\d{7}$/.test(municipio)) return enviar(400, 'application/json; charset=utf-8', JSON.stringify({ erro: 'municipio_id inválido' }));
      return enviar(200, 'application/json; charset=utf-8', JSON.stringify(rows.filter(o => !municipio || o.municipio_id === municipio)));
    }
    if (url.pathname === '/api/v1/populacao.csv') {
      if (!rows.length) return enviar(503, 'application/json; charset=utf-8', JSON.stringify({ erro: 'Nenhum lote homologado publicado' }));
      return enviar(200, 'text/csv; charset=utf-8', csv(rows));
    }
    if (url.pathname === '/api/v1/status') {
      const ano = rows.length ? Math.max(...rows.map(o => o.ano)) : null;
      const atualizado_em = rows.length ? rows.map(o => o.atualizado_em).sort().at(-1) : null;
      return enviar(200, 'application/json; charset=utf-8', JSON.stringify({ indicador: 'populacao_estimada', situacao: rows.length ? 'publicado' : 'sem_publicacao', ano_referencia: ano, atualizado_em }));
    }
    if (url.pathname === '/status') {
      const ano = rows.length ? Math.max(...rows.map(o => o.ano)) : null;
      const atualizado = rows.length ? rows.map(o => o.atualizado_em).sort().at(-1) : null;
      return enviar(200, 'text/html; charset=utf-8', `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Status do Observatório</title><main><h1>Status dos indicadores</h1><table><caption>Publicação homologada</caption><thead><tr><th>Indicador</th><th>Situação</th><th>Ano de referência</th><th>Última atualização</th></tr></thead><tbody><tr><td>População estimada</td><td>${rows.length ? 'Publicado' : 'Sem publicação'}</td><td>${ano ?? '—'}</td><td>${atualizado ?? '—'}</td></tr></tbody></table><p><a href="/api/v1/populacao.csv">Baixar CSV</a></p></main></html>`);
    }
    enviar(404, 'application/json; charset=utf-8', JSON.stringify({ erro: 'Rota não encontrada' }));
  });
}
