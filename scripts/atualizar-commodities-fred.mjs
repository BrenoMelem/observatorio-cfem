/** Coleta de laboratório das séries mensais globais de ferro e cobre do FRED. */
import { executarCommodities } from '../src/commodities-fred.mjs';

try {
  const relatorio = await executarCommodities({ dataDir: process.env.OBS_DATA_DIR || 'output/observatorio' });
  console.log(JSON.stringify({ situacao: relatorio.situacao, linhas: relatorio.linhas_lidas, nulos: relatorio.nulos, execucao: relatorio.execucao }));
} catch (error) {
  console.error(error.relatorio?.erro ?? error.message);
  process.exitCode = 1;
}
