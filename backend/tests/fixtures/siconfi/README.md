# Recorte real do SICONFI para os testes (RN-VPU-04)

Respostas da API pública do SICONFI (`https://apidatalake.tesouro.gov.br/ords/siconfi/tt/`) para **Piçarra (`1505635`), exercício 2024**, baixadas em 25/11/2026. Cada arquivo guarda só as linhas que o produto usa; os campos de cada linha são os da API, sem alteração de valor.

| Arquivo | Consulta | Recorte |
| --- | --- | --- |
| `dca.json` | `dca?an_exercicio=2024&id_ente=1505635&no_anexo=DCA-Anexo I-E` | 156 de 225 linhas: colunas Despesas Empenhadas, Liquidadas e Pagas (sem as de restos a pagar) |
| `rreo.json` | `rreo?an_exercicio=2024&nr_periodo=6&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo 02&id_ente=1505635` | 106 de 575 linhas: empenhadas e liquidadas até o bimestre |
| `msc.json` | `msc_orcamentaria?id_ente=1505635&an_referencia=2024&me_referencia=12&co_tipo_matriz=MSCC&classe_conta=6&id_tv=ending_balance` | 390 de 1.978 linhas: conta 622130400; só os campos que o produto lê |
| `extrato.json` | `extrato_entregas?id_ente=1505635&an_referencia=2024` | 4 de 39 entregas: DCA, RREO do 6º bimestre e MSC de dezembro |

Em 25/11/2026 a DCA de Piçarra 2024 coincidiu ao centavo com o RREO (empenhada e liquidada) e com a MSC (paga), nas sondas `scripts/sondas/siconfi_rreo_dca.py` e `scripts/sondas/siconfi_msc_dca_paga.py`.
