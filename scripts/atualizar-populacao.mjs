import { executar } from '../src/populacao.mjs';

const dataDir = process.env.OBS_DATA_DIR || 'output/observatorio';
try {
  const anoArg = process.argv.indexOf('--ano');
  const anoAlvo = anoArg >= 0 ? Number(process.argv[anoArg + 1]) : undefined;
  if (anoArg >= 0 && (!Number.isInteger(anoAlvo) || anoAlvo < 2000 || anoAlvo > 2100)) throw new Error('--ano exige um ano válido');
  const relatorio = await executar({ dataDir, anoAlvo });
  console.log(JSON.stringify({ situacao: relatorio.situacao, ano: relatorio.anos[0], municipios: relatorio.municipios_presentes.length, execucao: relatorio.execucao }));
} catch (error) {
  console.error(error.relatorio?.erro ?? error.message);
  process.exitCode = 1;
}
