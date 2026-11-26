<?php
// Conexão e regras comuns da API do painel.
// config.php é gerado pelo robô de publicação a partir dos secrets do GitHub e nunca vai para o repositório.

declare(strict_types=1);

function abc_config(): array {
    static $cfg = null;
    if ($cfg === null) {
        $arq = __DIR__ . '/config.php';
        if (!is_file($arq)) {
            abc_erro(500, 'config.php ausente');
        }
        $cfg = require $arq;
    }
    return $cfg;
}

function abc_db(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        $c = abc_config();
        $pdo = new PDO(
            "mysql:host={$c['db_host']};dbname={$c['db_nome']};charset=utf8mb4",
            $c['db_usuario'],
            $c['db_senha'],
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]
        );
    }
    return $pdo;
}

function abc_json($dados, int $status = 200): void {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($dados, JSON_UNESCAPED_UNICODE);
    exit;
}

function abc_erro(int $status, string $msg): void {
    abc_json(['erro' => $msg], $status);
}

// Conjuntos aceitos pelo importador: tabela, colunas e como substituir uma carga anterior.
const ABC_CONJUNTOS = [
    'municipios'   => ['tabela' => 'municipios',   'colunas' => ['ibge', 'nome', 'slug_tce', 'cod6'], 'chave' => []],
    'populacao'    => ['tabela' => 'populacao',    'colunas' => ['ibge', 'ano', 'valor'], 'chave' => []],
    'capag'        => ['tabela' => 'capag',        'colunas' => ['ibge', 'posicao', 'capag', 'ind1', 'nota1', 'ind2', 'nota2', 'ind3', 'nota3'], 'chave' => []],
    // receitas: a carga de um (ibge, ano, mes) apaga a anterior do mesmo período.
    'receitas_tce' => ['tabela' => 'receitas_tce', 'colunas' => ['ibge', 'ano', 'mes', 'fonte_recurso', 'cod_aplicacao', 'alinea', 'valor'], 'chave' => ['ibge', 'ano', 'mes']],
];
