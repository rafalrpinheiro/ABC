<?php
// Recebe as cargas do robô de coleta.
// POST JSON: {"conjunto": "capag", "linhas": [{...}, ...]}
// Cabeçalho obrigatório: X-ABC-Token com o token de importação.

declare(strict_types=1);
require __DIR__ . '/lib.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    abc_erro(405, 'use POST');
}
$token = $_SERVER['HTTP_X_ABC_TOKEN'] ?? '';
if (!is_string($token) || $token === '' || !hash_equals((string) abc_config()['token_importacao'], $token)) {
    abc_erro(403, 'token inválido');
}

$corpo = json_decode((string) file_get_contents('php://input'), true);
$nome = is_array($corpo) ? ($corpo['conjunto'] ?? '') : '';
$linhas = is_array($corpo) ? ($corpo['linhas'] ?? null) : null;
if (!isset(ABC_CONJUNTOS[$nome]) || !is_array($linhas)) {
    abc_erro(400, 'conjunto ou linhas inválidos');
}
$def = ABC_CONJUNTOS[$nome];
$cols = $def['colunas'];

$db = abc_db();
$db->exec((string) file_get_contents(__DIR__ . '/schema.sql'));

$db->beginTransaction();
try {
    if ($def['chave']) {
        // Apaga os períodos que estão chegando de novo.
        $periodos = [];
        foreach ($linhas as $l) {
            $k = array_map(fn($c) => $l[$c] ?? null, $def['chave']);
            $periodos[json_encode($k)] = $k;
        }
        $onde = implode(' AND ', array_map(fn($c) => "`$c` = ?", $def['chave']));
        $del = $db->prepare("DELETE FROM `{$def['tabela']}` WHERE $onde");
        foreach ($periodos as $k) {
            $del->execute($k);
        }
    }
    $lista = implode(', ', array_map(fn($c) => "`$c`", $cols));
    $marc = implode(', ', array_fill(0, count($cols), '?'));
    $atual = implode(', ', array_map(fn($c) => "`$c` = VALUES(`$c`)", $cols));
    $ins = $db->prepare("INSERT INTO `{$def['tabela']}` ($lista) VALUES ($marc) ON DUPLICATE KEY UPDATE $atual");
    foreach ($linhas as $l) {
        if (!is_array($l)) {
            throw new InvalidArgumentException('linha inválida');
        }
        $ins->execute(array_map(fn($c) => $l[$c] ?? null, $cols));
    }
    $db->prepare('INSERT INTO cargas (conjunto, linhas, detalhe) VALUES (?, ?, ?)')
       ->execute([$nome, count($linhas), substr((string) ($corpo['detalhe'] ?? ''), 0, 255)]);
    $db->commit();
} catch (Throwable $e) {
    $db->rollBack();
    abc_erro(400, 'carga recusada: ' . $e->getMessage());
}

abc_json(['ok' => true, 'conjunto' => $nome, 'linhas' => count($linhas)]);
