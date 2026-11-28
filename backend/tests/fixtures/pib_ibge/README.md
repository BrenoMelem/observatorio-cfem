# Recortes do SIDRA 5938 para os testes do PIB municipal

- `sidra-5938-recorte.json`: resposta real do SIDRA (baixada em 27/11/2026, edição modificada em 19/12/2025)
  ao pedido de 2012, 2022 e 2023, das variáveis 37, 543, 498, 513, 517, 6575 e 525, para os 12 municípios da
  RI Carajás. Os valores não foram alterados; o JSON só foi regravado sem espaços. 2012 traz os quatro VAB da
  indústria negativos; 2022 e 2023 trazem só o PIB (`...` nos componentes).
- `periodos-recorte.json`: a lista real de períodos do agregado 5938, reduzida aos anos 2009, 2012, 2022 e
  2023, para que a coleta peça exatamente os anos do recorte (2009 fica fora por ser anterior a 2010,
  RN-TMP-16).
