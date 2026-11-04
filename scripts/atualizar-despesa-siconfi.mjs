/** Coleta exploratória da DCA I-E dos 12 municípios; mantém a publicação bloqueada até homologação. */
import { executarDespesa } from '../src/despesa-siconfi.mjs';

const anoArg = process.argv.indexOf('--ano');
const ano = anoArg >= 0 ? Number(process.argv[anoArg + 1]) : undefined;
try {
  const relatorio = await executarDespesa({ dataDir: process.env.OBS_DATA_DIR || 'output/observatorio', ano });
  console.log(JSON.stringify({ situacao: relatorio.situacao, exercicio: relatorio.exercicio, linhas: relatorio.linhas_lidas, municipios: relatorio.municipios_presentes.length, pendencias: relatorio.pendencias }));
} catch (error) {
  console.error(error.relatorio?.erro ?? error.message);
  process.exitCode = 1;
}
