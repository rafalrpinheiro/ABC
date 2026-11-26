# Painel de Dados do Grande ABC

Painel com dados públicos das 7 cidades do Consórcio Intermunicipal do Grande ABC:
Santo André, São Bernardo do Campo, São Caetano do Sul, Diadema, Mauá, Ribeirão Pires e Rio Grande da Serra.

Projeto independente, sem relação com a SGRI ou com o portfoliosgri.

## Hospedagem: RP Brand

Tudo fica na hospedagem RP Brand (rpbranding.com.br, Hostinger):

- **Site:** `rpbranding.com.br/abc/`, publicado pelo robô `.github/workflows/publicar.yml` a cada mudança em `site/` no branch `main`.
- **Banco:** MySQL da própria hospedagem, com usuário exclusivo do painel. Só o PHP da hospedagem fala com ele (sem acesso remoto).
- **Carga:** o robô `.github/workflows/coletar.yml` roda toda segunda, coleta as fontes (`scripts/coletar.py`) e envia para `api/importar.php`, protegido por token. As tabelas são criadas sozinhas na primeira carga (`sql/schema.sql`).
- **Leitura:** `api/dados.php?conjunto=capag | emendas | transferencias | populacao | cargas`.

Secrets do repositório (Settings → Secrets and variables → Actions):

| Secret | Valor |
| --- | --- |
| `FTP_SERVIDOR` | servidor FTP da Hostinger |
| `FTP_USUARIO` | usuário FTP exclusivo do ABC, com pasta inicial `public_html/abc` |
| `FTP_SENHA` | senha desse usuário |
| `MYSQL_BANCO` | nome completo do banco (com o prefixo `u…_` da Hostinger) |
| `MYSQL_USUARIO` | usuário completo do banco (com o prefixo) |
| `MYSQL_SENHA` | senha do banco |
| `ABC_TOKEN` | texto aleatório longo, inventado por você; é a senha do importador |

O repositório é público: nenhuma senha vai para o código, só para os secrets.

- `docs/etapa1-fontes.md`: resultado do teste das fontes (26/11/2026).
- `scripts/testar_fontes.py`: repete o teste das fontes principais para as 7 cidades.

## Códigos das cidades

| Cidade | IBGE (7 díg.) | DataSUS (6 díg.) | TCE-SP |
| --- | --- | --- | --- |
| Santo André | 3547809 | 354780 | santo-andre |
| São Bernardo do Campo | 3548708 | 354870 | sao-bernardo-do-campo |
| São Caetano do Sul | 3548807 | 354880 | sao-caetano-do-sul |
| Diadema | 3513801 | 351380 | diadema |
| Mauá | 3529401 | 352940 | maua |
| Ribeirão Pires | 3543303 | 354330 | ribeirao-pires |
| Rio Grande da Serra | 3544103 | 354410 | rio-grande-da-serra |
