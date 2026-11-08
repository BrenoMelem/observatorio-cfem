"""Os 12 municípios da RI Carajás (RN-TER-01) e os campos do esquema comum (RN-MOD-03).

Módulo de laboratório: usado pelos scripts de teste, não é a implementação do produto.
"""

MUNICIPIOS: dict[str, str] = {
    "1501576": "Bom Jesus do Tocantins",
    "1501758": "Brejo Grande do Araguaia",
    "1502152": "Canaã dos Carajás",
    "1502772": "Curionópolis",
    "1502954": "Eldorado do Carajás",
    "1504208": "Marabá",
    "1505494": "Palestina do Pará",
    "1505536": "Parauapebas",
    "1505635": "Piçarra",
    "1507151": "São Domingos do Araguaia",
    "1507458": "São Geraldo do Araguaia",
    "1507508": "São João do Araguaia",
}

CAMPOS: tuple[str, ...] = (
    "indicador", "municipio_id", "municipio_nome", "nivel_territorial", "ano", "mes", "valor",
    "unidade", "natureza_valor", "estado_validacao", "fonte", "edicao_fonte", "atualizado_em",
    "versao_tratamento",
)
