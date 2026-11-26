"""Confere se as fontes públicas do Painel do Grande ABC respondem para as 7 cidades.

Uso: python3 scripts/testar_fontes.py
Imprime uma linha por fonte e por cidade. Não grava nada.
"""
import json
import urllib.request

CIDADES = {
    3547809: ("Santo André", "santo-andre", 354780),
    3548708: ("São Bernardo do Campo", "sao-bernardo-do-campo", 354870),
    3548807: ("São Caetano do Sul", "sao-caetano-do-sul", 354880),
    3513801: ("Diadema", "diadema", 351380),
    3529401: ("Mauá", "maua", 352940),
    3543303: ("Ribeirão Pires", "ribeirao-pires", 354330),
    3544103: ("Rio Grande da Serra", "rio-grande-da-serra", 354410),
}
SICONFI = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
TCE = "https://transparencia.tce.sp.gov.br/api/json"


def get_json(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "painel-abc/0.1"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def tentar(nome, fn):
    try:
        return f"{nome}={fn()}"
    except Exception as e:  # noqa: BLE001 - relatório de diagnóstico
        return f"{nome}=ERRO({str(e)[:50]})"


def siconfi_rreo(ibge, ano=2025, periodo=6):
    # Municípios pequenos podem entregar a versão simplificada (ex.: Rio Grande da Serra desde 2025).
    for tipo in ("RREO", "RREO%20Simplificado"):
        d = get_json(f"{SICONFI}/rreo?an_exercicio={ano}&nr_periodo={periodo}"
                     f"&co_tipo_demonstrativo={tipo}&no_anexo=RREO-Anexo%2001&id_ente={ibge}")
        if d["items"]:
            return f"{len(d['items'])}({tipo.replace('%20', ' ')})"
    return 0


def tce_emendas(slug, ano=2025, mes=12):
    d = get_json(f"{TCE}/receitas/{slug}/{ano}/{mes}")
    em = [x for x in d if "EMENDA" in (x.get("ds_cd_aplicacao_fixo") or "").upper()]
    return f"{len(d)} linhas, {len(em)} de emendas"


def cnes(cod6):
    d = get_json(f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos?codigo_municipio={cod6}&limit=20")
    return f"{len(d['estabelecimentos'])}+"


def sidra_pop(ibge):
    d = get_json(f"https://apisidra.ibge.gov.br/values/t/6579/n6/{ibge}/v/all/p/last%201")
    return f"{d[1]['V']} ({d[1]['D3N']})"


if __name__ == "__main__":
    for ibge, (nome, slug, cod6) in CIDADES.items():
        partes = [
            tentar("ibge_pop", lambda: sidra_pop(ibge)),
            tentar("siconfi_rreo", lambda: siconfi_rreo(ibge)),
            tentar("tce_receitas", lambda: tce_emendas(slug)),
            tentar("cnes", lambda: cnes(cod6)),
        ]
        print(f"{nome}: " + " | ".join(partes), flush=True)
