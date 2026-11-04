/** Confere localmente os totais de status das regras antes de revisar a documentação. */
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export async function checarTotais(dir = fileURLToPath(new URL('../docs/regras-de-negocio/', import.meta.url))) {
  const contagem = { DECIDIDAS: 0, PROPOSTAS: 0, 'EM ABERTO': 0 };
  for (const name of await readdir(dir)) {
    if (!name.endsWith('.md') || name === 'README.md') continue;
    const body = await readFile(path.join(dir, name), 'utf8');
    for (const match of body.matchAll(/^- \*\*Status:\*\* (DECIDIDA|PROPOSTA|EM ABERTO)\s*$/gm)) {
      contagem[match[1] === 'DECIDIDA' ? 'DECIDIDAS' : match[1] === 'PROPOSTA' ? 'PROPOSTAS' : 'EM ABERTO']++;
    }
  }
  const readme = await readFile(path.join(dir, 'README.md'), 'utf8');
  const match = readme.match(/^Total:\s*(\d+) regras, sendo (\d+) DECIDIDAS, (\d+) PROPOSTAS e (\d+) EM ABERTO\./m);
  if (!match) throw new Error('Linha Total: ausente ou em formato inesperado');
  const esperado = { total: Number(match[1]), DECIDIDAS: Number(match[2]), PROPOSTAS: Number(match[3]), 'EM ABERTO': Number(match[4]) };
  const obtido = { total: Object.values(contagem).reduce((a, b) => a + b, 0), ...contagem };
  return { esperado, obtido, confere: Object.keys(esperado).every(k => esperado[k] === obtido[k]) };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const resultado = await checarTotais();
    console.log(JSON.stringify(resultado));
    if (!resultado.confere) process.exitCode = 1;
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
