# Etapa 1 — Teste das fontes (26/11/2026)

Teste feito a partir do ambiente de nuvem "ABC", com acesso liberado só aos domínios das fontes.

## Funcionam para as 7 cidades

| Fonte | Endpoint usado | Observação |
| --- | --- | --- |
| TCE-SP | `transparencia.tce.sp.gov.br/api/json/receitas/{slug}/{ano}/{mes}` e `/despesas/...` | Códigos de aplicação 800 (emenda individual União), 801 (emenda individual Estado), 802 (Pix União), 803 (Pix Estado), 900 (bancada União). Emendas em dez/2025: Mauá 63, SBC 60, Santo André 58, Ribeirão Pires 26, RGS 20, Diadema 19, São Caetano 1 |
| Tesouro — CAPAG | Planilha no CKAN `capag-municipios` (posição 2026-set-1), aba "Prévia da CAPAG" | B+: Mauá, São Bernardo. C: Santo André, São Caetano, Diadema, Ribeirão Pires, Rio Grande da Serra |
| Siconfi | `apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo` e `/rgf` | Rio Grande da Serra entrega `RREO Simplificado` e `RGF Simplificado` (semestral) desde 2025 |
| IBGE | `apisidra.ibge.gov.br/values/t/6579/...`, `servicodados.ibge.gov.br` | População estimada 2026 |
| CNES | `apidadosabertos.saude.gov.br/cnes/estabelecimentos?codigo_municipio=` (6 dígitos) | |
| DataSUS TabNet | `https://tabnet.datasus.gov.br/cgi/...` | Só por https |
| Cadastur | CKAN `dados.turismo.gov.br` | Arquivos CSV |
| Obrasgov | `api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento?uf=SP` | Sem filtro por município conhecido; recorte por cidade em validação |
| MapBiomas, Cemaden | sites respondem | Formato de extração a definir |

## Precisam de ajuste

| Fonte | Problema |
| --- | --- |
| Portal da Transparência | API exige chave gratuita (header `chave-api-dados`) |
| Transferegov API | Bloqueio Cloudflare (403) a partir do servidor |
| SSP-SP | Site em Angular; dados por município via exportação oficial — leitura automática não testada |
| Caged/RAIS | Página migrou para gov.br; microdados em FTP do MTE |
| CETESB | Proteção anti-robô (resposta 202 vazia) |
| Querido Diário | `api.queridodiario.org.br` respondeu 503 |
| Seade, Geoseade | Sem resposta (timeout) |
| Defesa Civil S2iD | 403 |
| Transparência SP | Site responde; repasses por município não localizados |
