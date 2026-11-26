<?php
// Leitura dos dados para as telas do painel.
// GET dados.php?conjunto=capag | emendas | transferencias | populacao | cargas

declare(strict_types=1);
require __DIR__ . '/lib.php';

$db = abc_db();
$conjunto = $_GET['conjunto'] ?? '';

switch ($conjunto) {
    case 'populacao':
        $sql = 'SELECT p.ibge, m.nome, p.ano, p.valor FROM populacao p JOIN municipios m USING (ibge)
                WHERE p.ano = (SELECT MAX(ano) FROM populacao) ORDER BY p.valor DESC';
        break;
    case 'capag':
        // Última posição publicada de cada cidade.
        $sql = 'SELECT c.*, m.nome FROM capag c JOIN municipios m USING (ibge)
                WHERE c.posicao = (SELECT MAX(posicao) FROM capag) ORDER BY m.nome';
        break;
    case 'emendas':
        // Emendas parlamentares por cidade, ano e tipo (códigos de aplicação 800-803 e 900 do TCE-SP).
        $sql = "SELECT r.ibge, m.nome, r.ano, LEFT(r.cod_aplicacao, 3) AS codigo,
                       MIN(r.cod_aplicacao) AS tipo, SUM(r.valor) AS valor
                FROM receitas_tce r JOIN municipios m USING (ibge)
                WHERE LEFT(r.cod_aplicacao, 3) IN ('800','801','802','803','900')
                GROUP BY r.ibge, m.nome, r.ano, codigo ORDER BY r.ano, m.nome, codigo";
        break;
    case 'transferencias':
        // Receita por fonte (02 = estaduais vinculadas, 05 = federais vinculadas, etc.).
        $sql = 'SELECT r.ibge, m.nome, r.ano, r.fonte_recurso, SUM(r.valor) AS valor
                FROM receitas_tce r JOIN municipios m USING (ibge)
                GROUP BY r.ibge, m.nome, r.ano, r.fonte_recurso ORDER BY r.ano, m.nome, r.fonte_recurso';
        break;
    case 'cargas':
        $sql = 'SELECT conjunto, linhas, detalhe, criado_em FROM cargas ORDER BY id DESC LIMIT 50';
        break;
    default:
        abc_erro(400, 'conjunto desconhecido');
}

abc_json($db->query($sql)->fetchAll());
