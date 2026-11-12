"""Resposta determinística da camada publicada; o LLM apenas redige a introdução."""
import re
import unicodedata

from app.dtos.assistente import Acao, Citacao, Pergunta, Resposta
from app.llm.redator import Redator
from app.repositories.publicacao import populacao_publicada
from app.services.explicacoes import explicacao


def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def _acoes(entrada: Pergunta) -> list[Acao]:
    pergunta = normalizar(entrada.pergunta)
    if "restaurar filtros" in pergunta:
        return [Acao(tipo="restaurar")]
    anos = [int(a) for a in re.findall(r"\b(?:19|20)\d{2}\b", pergunta)]
    if "periodo" in pergunta and len(anos) >= 2:
        de, ate = sorted(anos[:2])
        return [Acao(tipo="definirPeriodo", de=de, ate=ate)]
    if "mostrar so" in pergunta or "mostre so" in pergunta:
        nomes = [nome for nome in entrada.contexto.comparacoes if normalizar(nome) in pergunta]
        if nomes:
            return [Acao(tipo="definirSeries", nomes=nomes)]
    if ("abrir aba" in pergunta or "abra a aba" in pergunta) and normalizar(entrada.contexto.tema.titulo) in pergunta:
        return [Acao(tipo="escolherTema", tema=entrada.contexto.tema.id)]
    if "ver grafico" in pergunta or "mostre o grafico" in pergunta:
        graficos = [g for g in entrada.contexto.graficos if normalizar(g.titulo) in pergunta]
        if len(graficos) == 1:
            return [Acao(tipo="destacar", tema=entrada.contexto.tema.id, i=graficos[0].i)]
    if "abrir dimensao" in pergunta:
        paginas = [p for p in ("social", "economica", "ambiental", "institucional") if p in pergunta]
        if len(paginas) == 1 and entrada.contexto.graficos:
            return [Acao(tipo="irPara", pagina=paginas[0], tema=entrada.contexto.tema.id,
                         i=entrada.contexto.graficos[0].i)]
    return []


def responder(entrada: Pergunta, redator: Redator) -> Resposta:
    acoes = _acoes(entrada)
    pergunta = normalizar(entrada.pergunta)
    if "popul" not in pergunta:
        return Resposta(resposta="Não há observação validada compatível nesta camada para responder à pergunta.",
                        citacoes=[], limitacoes=["Indicador sem publicação homologada ou pergunta fora do recorte disponível."],
                        acoes=acoes)
    observacoes = populacao_publicada()
    if not observacoes:
        return Resposta(resposta="Não há dado validado de população publicado nesta camada.", citacoes=[],
                        limitacoes=["O pacote publicado de população não está disponível."], acoes=acoes)
    nomes = {o.municipio_nome: o.municipio_id for o in observacoes if o.municipio_nome}
    mencionados = [codigo for nome, codigo in nomes.items() if normalizar(nome) in pergunta]
    mencionados = sorted(set(mencionados))
    if len(mencionados) != 1:
        return Resposta(resposta="Indique um município da RI Carajás para consultar a população.", citacoes=[],
                        limitacoes=["A pergunta precisa identificar um único município com observação validada."],
                        acoes=acoes)
    anos = [int(a) for a in re.findall(r"\b(?:19|20)\d{2}\b", pergunta)]
    if len(set(anos)) > 1 or any(t in pergunta for t in ("cresceu", "crescimento", "compar", "diferenca")):
        return Resposta(resposta="Não há cálculo validado compatível com essa comparação.", citacoes=[],
                        limitacoes=["Esta fase consulta valores pontuais; crescimento e comparações exigem método definido."],
                        acoes=acoes)
    ano = anos[0] if anos else max(o.ano for o in observacoes if o.municipio_id == mencionados[0])
    encontrados = [o for o in observacoes if o.municipio_id == mencionados[0] and o.ano == ano
                   and o.estado_validacao == "validado" and o.valor is not None]
    if len(encontrados) != 1:
        return Resposta(resposta="Não há dado validado de população para o município e o ano pedidos.",
                        citacoes=[], limitacoes=["Ausência não equivale a zero; não foi feita interpolação."], acoes=acoes)
    o = encontrados[0]
    base = "População residente estimada, distinta do Censo."
    introducao = redator.introducao(entrada.pergunta, base)
    # O provedor escolhe apenas entre frases aprovadas; nenhum fato livre entra na resposta.
    if introducao not in {base, "Esta é uma estimativa de população residente, distinta do Censo."}:
        introducao = base
    numero = f"{int(o.valor):,}".replace(",", ".")
    resposta = f"{introducao} {o.municipio_nome}: {numero} {o.unidade} em {o.ano}. Fonte: {o.fonte}, edição {o.edicao_fonte}."
    return Resposta(resposta=resposta, citacoes=[Citacao(indicador=o.indicador, fonte=o.fonte,
                    periodo=str(o.ano), edicao=o.edicao_fonte)],
                    limitacoes=["Estimativa populacional, distinta do Censo. Anos ausentes não são preenchidos.",
                                explicacao(o.indicador)[:300]], acoes=acoes)
