<?php
// Wi-Fi monitor ingest. Probes POST JSON here; one JSONL file per day.
// LAN-only by source IP - no token to manage, nothing secret on disk.
// Timezone is pinned explicitly: this QNAP defaults PHP to Asia/Taipei, which
// already caused one silent read-back bug. Nothing here derives a filename from
// the server clock (the day comes from the probe's own timestamp), but pinning
// it keeps any future date() call honest.
date_default_timezone_set(@trim(@file_get_contents(__DIR__.'/timezone.txt')) ?: 'UTC');
header('Content-Type: application/json');
// Allowlist comes from lan-prefix.txt, written by bin/deploy.sh from config.sh.
// Hardcoding a subnet here is what makes a repo un-shareable.
$prefix = @trim(@file_get_contents(__DIR__ . '/lan-prefix.txt')) ?: '127.0.0.1';
$ip = $_SERVER['REMOTE_ADDR'] ?? '';
if (strpos($ip, $prefix) !== 0) {
    http_response_code(403); echo json_encode(['error' => 'LAN only']); exit;
}
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405); echo json_encode(['error' => 'POST only']); exit;
}
$raw = file_get_contents('php://input');
$in  = json_decode($raw, true);
if (!is_array($in)) { http_response_code(400); echo json_encode(['error'=>'bad json']); exit; }
$samples = isset($in['ts']) ? [$in] : $in;
$dir = __DIR__ . '/data';
if (!is_dir($dir)) @mkdir($dir, 0775, true);
$written = 0;
foreach ($samples as $s) {
    if (!is_array($s) || empty($s['ts'])) continue;
    $day = substr($s['ts'], 0, 10);
    if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $day)) continue;
    $s['_rx_ip'] = $ip;
    $f = "$dir/wifi-$day.jsonl";
    $fh = fopen($f, 'a');
    if ($fh) { flock($fh,LOCK_EX); fwrite($fh, json_encode($s)."\n"); flock($fh,LOCK_UN); fclose($fh); $written++; }
}
// Retention, done here rather than in cron: QNAP wipes /etc/config/crontab on
// firmware updates, so a cron job would silently stop. Roughly 1-in-50 requests
// prunes, which at 3 probes x 12/hr is a few times a day.
if (mt_rand(1, 50) === 1) {
    $keep = 30;
    $files = glob($dir . '/wifi-*.jsonl');
    sort($files);
    foreach (array_slice($files, 0, max(0, count($files) - $keep)) as $old) @unlink($old);
}
echo json_encode(['ok' => true, 'written' => $written]);
