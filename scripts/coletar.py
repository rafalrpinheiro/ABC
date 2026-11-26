"""Coleta os dados públicos das 7 cidades e envia ao banco do painel na RP Brand.

Uso:
  python3 scripts/coletar.py                  # só grava os JSON em dados/
  ABC_URL=https://rpbranding.com.br/abc ABC_TOKEN=... python3 scripts/coletar.py   # grava e envia

Variáveis opcionais: ANOS_TCE (ex.: "2025,2026"; padrão: ano passado e o atual).
Precisa de openpyxl para ler a planilha da CAPAG.
"""
import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

CIDADES = [
    # ibge, nome, slug TCE-SP, código DataSUS
    (3547809, "Santo André", "santo-andre", 354780),
    (3548708, "São Bernardo do Campo", "sao-bernardo-do-campo", 354870),
    (3548807, "São Caetano do Sul", "sao-caetano-do-sul", 354880),
    (3513801, "Diadema", "diadema", 351380),
    (3529401, "Mauá", "maua", 352940),
    (3543303, "Ribeirão Pires", "ribeirao-pires", 354330),
    (3544103, "Rio Grande da Serra", "rio-grande-da-serra", 354410),
]
IBGES = {c[0] for c in CIDADES}
MESES = {m: i for i, m in enumerate(
    ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
     "agosto", "setembro", "outubro", "novembro", "dezembro"], start=1)}
SAIDA = Path(__file__).resolve().parent.parent / "dados"
UA = {"User-Agent": "painel-abc/0.1"}


def baixar(url, timeout=90, tentativas=3):
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(5 * (i + 1))


def valor_br(txt):
    return float(str(txt).replace(".", "").replace(",", ".")) if txt not in (None, "") else 0.0


# ---------- coletas ----------

def coletar_municipios():
    return [{"ibge": i, "nome": n, "slug_tce": s, "cod6": c} for i, n, s, c in CIDADES]


def coletar_populacao():
    ids = ",".join(str(i) for i in IBGES)
    d = json.loads(baixar(f"https://apisidra.ibge.gov.br/values/t/6579/n6/{ids}/v/all/p/last%201"))
    return [{"ibge": int(r["D1C"]), "ano": int(r["D3C"]), "valor": int(r["V"])} for r in d[1:]]


def coletar_capag():
    import openpyxl

    meta = json.loads(baixar(
        "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=capag-municipios"))
    planilhas = [r for r in meta["result"]["resources"] if r["url"].lower().endswith(".xlsx")]
    def data_posicao(r):  # "Capag Municípios 2026 - 01/09/2026" -> "2026-09-01"
        m = re.search(r"(\d{2})/(\d{2})/(\d{4})", r["name"])
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else (r.get("created") or "")[:10]

    ultima = max(planilhas, key=data_posicao)
    posicao = data_posicao(ultima)
    wb = openpyxl.load_workbook(io.BytesIO(baixar(ultima["url"], timeout=180)), read_only=True, data_only=True)
    ws = wb["Prévia da CAPAG"]
    linhas = []
    for r in ws.iter_rows(values_only=True):
        if r and r[0] in IBGES:
            num = lambda v: v if isinstance(v, (int, float)) else None  # noqa: E731
            linhas.append({"ibge": r[0], "posicao": posicao, "capag": r[3],
                           "ind1": num(r[4]), "nota1": r[5], "ind2": num(r[6]), "nota2": r[7],
                           "ind3": num(r[8]), "nota3": r[9]})
    return linhas, ultima["name"]


def coletar_receitas_tce(anos):
    """Receita arrecadada por mês, somada por fonte, aplicação e alínea."""
    hoje = dt.date.today()
    linhas = []
    for ibge, _nome, slug, _c in CIDADES:
        for ano in anos:
            ultimo_mes = 12 if ano < hoje.year else hoje.month
            for mes in range(1, ultimo_mes + 1):
                try:
                    d = json.loads(baixar(f"https://transparencia.tce.sp.gov.br/api/json/receitas/{slug}/{ano}/{mes}"))
                except Exception as e:  # mês ainda não publicado ou fora do ar
                    print(f"  TCE {slug} {ano}/{mes}: {str(e)[:60]}", file=sys.stderr)
                    continue
                soma = {}
                for x in d:
                    k = (x.get("ds_fonte_recurso") or "", x.get("ds_cd_aplicacao_fixo") or "",
                         x.get("ds_alinea") or "")
                    soma[k] = soma.get(k, 0.0) + valor_br(x.get("vl_arrecadacao"))
                linhas += [{"ibge": ibge, "ano": ano, "mes": mes, "fonte_recurso": k[0][:120],
                            "cod_aplicacao": k[1][:200], "alinea": k[2][:200], "valor": round(v, 2)}
                           for k, v in soma.items()]
    return linhas


# ---------- envio ----------

def enviar(conjunto, linhas, detalhe=""):
    url, token = os.environ.get("ABC_URL"), os.environ.get("ABC_TOKEN")
    if not (url and token):
        return
    # Lotes de até ~2000 linhas, sem nunca dividir um período (ibge, ano, mes):
    # o importador apaga o período inteiro antes de gravar o lote.
    grupos = {}
    for l in linhas:
        grupos.setdefault((l.get("ibge"), l.get("ano"), l.get("mes")), []).append(l)
    lotes, atual = [], []
    for g in grupos.values():
        if atual and len(atual) + len(g) > 2000:
            lotes.append(atual)
            atual = []
        atual += g
    if atual:
        lotes.append(atual)
    for lote in lotes:
        corpo = json.dumps({"conjunto": conjunto, "linhas": lote, "detalhe": detalhe}).encode()
        req = urllib.request.Request(f"{url.rstrip('/')}/api/importar.php", data=corpo, method="POST",
                                     headers={**UA, "Content-Type": "application/json", "X-ABC-Token": token})
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
        print(f"  enviado {conjunto}: {resp}")


def gravar(conjunto, linhas, detalhe=""):
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / f"{conjunto}.json").write_text(json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{conjunto}: {len(linhas)} linhas {detalhe}")
    enviar(conjunto, linhas, detalhe)


if __name__ == "__main__":
    ano = dt.date.today().year
    anos = [int(a) for a in (os.environ.get("ANOS_TCE") or f"{ano - 1},{ano}").split(",")]
    falhas = 0
    for nome, fn in [
        ("municipios", lambda: (coletar_municipios(), "")),
        ("populacao", lambda: (coletar_populacao(), "IBGE/Sidra tabela 6579")),
        ("capag", coletar_capag),
        ("receitas_tce", lambda: (coletar_receitas_tce(anos), f"TCE-SP anos {anos}")),
    ]:
        try:
            linhas, detalhe = fn()
            gravar(nome, linhas, detalhe)
        except Exception as e:
            falhas += 1
            print(f"FALHA {nome}: {e}", file=sys.stderr)
    sys.exit(1 if falhas else 0)
