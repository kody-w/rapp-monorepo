<?php
// Serves recent samples to the dashboard.
// Deliberately does NOT compute filenames from the server clock: this QNAP runs
// PHP in Asia/Taipei while the probes stamp local US time, so a date-derived
// filename silently missed today's file. Globbing the directory is clock-proof.
header('Content-Type: application/json');
$days  = max(1, min(30, (int)($_GET['days'] ?? 2)));
$files = glob(__DIR__ . '/data/wifi-*.jsonl');
sort($files);                       // wifi-YYYY-MM-DD sorts chronologically
$files = array_slice($files, -$days);
$out = [];
foreach ($files as $f) {
    foreach (file($f, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $l) {
        $d = json_decode($l, true);
        if ($d && !empty($d['ts'])) $out[] = $d;
    }
}
usort($out, fn($a, $b) => strcmp($a['ts'], $b['ts']));
echo json_encode($out);
