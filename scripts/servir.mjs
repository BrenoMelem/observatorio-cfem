import { criarServidor } from '../src/servidor.mjs';

const port = Number(process.env.PORT || 3000);
const dataDir = process.env.OBS_DATA_DIR || 'output/observatorio';
criarServidor({ dataDir }).listen(port, () => console.log(`Observatório: http://localhost:${port}/status`));
