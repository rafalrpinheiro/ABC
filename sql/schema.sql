-- Banco do Painel do Grande ABC (MySQL/MariaDB da hospedagem RP Brand).
-- O importador (site/api/importar.php) roda este arquivo sozinho na primeira carga.

CREATE TABLE IF NOT EXISTS municipios (
  ibge      INT PRIMARY KEY,
  nome      VARCHAR(60)  NOT NULL,
  slug_tce  VARCHAR(60)  NOT NULL,
  cod6      INT          NOT NULL
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS populacao (
  ibge   INT NOT NULL,
  ano    SMALLINT NOT NULL,
  valor  INT NOT NULL,
  PRIMARY KEY (ibge, ano)
) DEFAULT CHARSET=utf8mb4;

-- Nota CAPAG do Tesouro, uma linha por cidade e posição publicada.
CREATE TABLE IF NOT EXISTS capag (
  ibge     INT NOT NULL,
  posicao  DATE NOT NULL,
  capag    VARCHAR(4),
  ind1     DECIMAL(14,6), nota1 VARCHAR(2),
  ind2     DECIMAL(14,6), nota2 VARCHAR(2),
  ind3     DECIMAL(14,6), nota3 VARCHAR(2),
  PRIMARY KEY (ibge, posicao)
) DEFAULT CHARSET=utf8mb4;

-- Receita arrecadada por mês, como o TCE-SP publica (soma por fonte, aplicação e alínea).
CREATE TABLE IF NOT EXISTS receitas_tce (
  ibge           INT NOT NULL,
  ano            SMALLINT NOT NULL,
  mes            TINYINT NOT NULL,
  fonte_recurso  VARCHAR(120) NOT NULL,
  cod_aplicacao  VARCHAR(200) NOT NULL,
  alinea         VARCHAR(200) NOT NULL,
  valor          DECIMAL(16,2) NOT NULL,
  KEY periodo (ibge, ano, mes),
  KEY aplicacao (cod_aplicacao(3))
) DEFAULT CHARSET=utf8mb4;

-- Registro de cada carga do robô.
CREATE TABLE IF NOT EXISTS cargas (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  conjunto   VARCHAR(40) NOT NULL,
  linhas     INT NOT NULL,
  detalhe    VARCHAR(255),
  criado_em  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) DEFAULT CHARSET=utf8mb4;
