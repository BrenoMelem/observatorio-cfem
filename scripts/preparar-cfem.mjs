import { prepararCfem } from '../src/cfem.mjs';

const file = process.argv[2];
if (!file) { console.error('Uso: node scripts/preparar-cfem.mjs CAMINHO/CFEM_Arrecadacao.csv'); process.exit(2); }
try { console.log(JSON.stringify(await prepararCfem(file, process.env.OBS_DATA_DIR || 'output/observatorio'))); }
catch (error) { console.error(`${error.name}: ${error.message}`); process.exitCode = 1; }
