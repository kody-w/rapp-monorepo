---
permalink: /portfolio/timeline.html
layout: null
---
{::nomarkdown}
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'sha256-EdLbDBprUsQ/fyUmX2gpSAQB7ULPqVwLstG/hJ3S3nw='; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<title>RAPP/1 network: timeline of 7 version(s)</title>
<style>body{margin:0;background:#f6f8fa;color:#1b1f24;font:16px/1.5 Helvetica,Arial,sans-serif}
header{background:#fff;border-bottom:1px solid #d0d7de;padding:14px 24px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
header h1{font-size:22px;margin:0;flex:1}
a{color:#0969da;text-decoration:none}
main{max-width:1040px;margin:0 auto;padding:20px 24px 60px}
section,article{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:16px 20px;margin:0 0 16px}
h2{font-size:19px;margin:0 0 8px}
h3{font-size:18px;margin:0 0 6px}
code,pre{font:13px/1.45 Menlo,Consolas,monospace;overflow-wrap:anywhere}
pre{white-space:pre-wrap;background:#f6f8fa;border-radius:6px;padding:10px 12px;margin:8px 0}
dl{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:8px 0}
dt{font-weight:700;color:#57606a}
dd{margin:0}
.totals span{display:inline-block;margin-right:14px}
.c{color:#1a7f37;font-weight:700}.n{color:#9a6700;font-weight:700}.u{color:#57606a;font-weight:700}
.seq{color:#57606a;font-weight:400;font-size:15px}
.note{border-left:5px solid #dfb317}
ul{margin:4px 0 8px 20px;padding:0}
footer{color:#57606a;font-size:13px;margin-top:24px}</style>
</head>
<body>
<header><h1>RAPP/1 network · timeline</h1><a href="https://kody-w.github.io/rapp-hive-public/portfolio/subway.html">Latest map</a><a href="https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/PORTFOLIO.md">Portfolio</a><a href="https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html">Notices</a><a href="https://github.com/kody-w/rapp-installer#start-here">Start here</a></header>
<main>
<section>
<h2>One RAPP/1 frame per crawl</h2>
<p>Each crawl of the RAPP/1 network is one pulse of its life: a RAPP/1 frame of the registered kind <code>body.pulse</code> on the network's body stream, chained to the pulse before it. Its payload holds the crawl time, the checker pin, the totals per status and per line, every repo's status, verdict and evidence commit, a digest of the links between repos, and the content hashes of that version's <code>PORTFOLIO.md</code> and maps.</p>
<dl>
<dt>Stream</dt><dd><code>rappid:@kody-w/rapp1-network:71216534f9d362c7af054e773d546dfd996f769b08bd38c1b90b9e36760c2def</code><br>Keyless, minted once (2026-09-25T17:36:08.797Z); <a href="https://kody-w.github.io/rapp-hive-public/portfolio/rappid.json">rappid.json</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/rapp-frame-index.json">frame index</a></dd>
<dt>Genesis</dt><dd>payload_hash <code>15530d4785bea042a87b06c7dcfe15fec6ede0b0041299bbd4e80e9e8a5b0894</code><br>frame_hash <code>d765d2698582e937af9cf75e6cb2851d6d1c10e546db1b4e5fe640c591b8b833</code></dd>
<dt>Head</dt><dd>version 7 (seq 6), payload_hash <code>27c398e7659922b6f8721118d4551ef685d129e94c726aa0091d88946269a56d</code></dd>
<dt>Checked</dt><dd>Every pulse passes RAPP/1 §7.5 steps 1–5 with the reference <code>rapp.py</code>, and rapp-1's own <code>rapp_check.py</code> at <code>591e014</code> gives the chain COMPLIANT (7 frame(s) passing, no findings). The reference implementation passes rapp-1's <code>conformance.py</code> (22 controlled checks | 22 PASS | 0 FAIL).</dd>
</dl>
</section>
<section class="note">
<h2>Signing and anchoring</h2>
<p>The pulses are unsigned (<code>sig: null</code>), which RAPP/1 §10 allows on a body stream. Their hashes prove integrity and order, not authorship: do not infer who wrote a pulse from the frame. Attribution comes from the RAPP Hive, which committed each pulse in a signed save and published it in a commit of <a href="https://github.com/kody-w/rapp-hive-public">kody-w/rapp-hive-public</a> signed by the RAPP Hive's own key (only the Hive can check that signature; GitHub shows these commits as unverified). Anchoring comes later: the estate owner authorizes a signer (phase 4), and records this stream's creation genesis in the estate's signed registry (§13.3), with this entry:</p>
<pre>{&quot;type&quot;: &quot;genesis&quot;, &quot;stream_id&quot;: &quot;rappid:@kody-w/rapp1-network:71216534f9d362c7af054e773d546dfd996f769b08bd38c1b90b9e36760c2def&quot;, &quot;frame_hash&quot;: &quot;d765d2698582e937af9cf75e6cb2851d6d1c10e546db1b4e5fe640c591b8b833&quot;, &quot;deprecated&quot;: false}</pre>
<p>Where the pulses live: in public. Every pulse is served as JSON beside its maps, and rapp_check.py still certifies this public copy: CLEAN on its files as they are (the Hive holds only markdown) and COMPLIANT on the files as GitHub Pages serves them, where each unsigned pulse passes the §7 envelope, hash and chain checks (a body stream permits sig null).</p>
</section>
<h2>Versions (7)</h2>
<article>
<h3>Version 7 · 2026-09-26 13:41 UTC <span class="seq">seq 6</span></h3>
<p class="totals"><span>317 stations</span><span class="c">293 certified</span><span class="n">23 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>27c398e7659922b6f8721118d4551ef685d129e94c726aa0091d88946269a56d</code><br>frame_hash <code>6d6dc111a8ffac650281d9adba1b1f7e07f0150a9780eff2b00a02afcdac334e</code><br>prev <code>be8e7ad5a9dcb03cdc87b0f858e681a734611a885f98279ab3c4246e9dc6ed02</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-6/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-6/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-6/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-6/pulse.json">pulse</a> · published with this page</p>
<p><b>Since version 6:</b> 0 status change(s), 0 new repo(s), 0 removed, 8 repo(s) at a new commit.</p>
<p>0 lifecycle change(s), 0 version change(s), 0 channel change(s), 1 member card change(s), 0 repo(s) left the network.</p>
<ul><li>RAPP: member card added</li></ul>
</article>
<article>
<h3>Version 6 · 2026-09-26 12:13 UTC <span class="seq">seq 5</span></h3>
<p class="totals"><span>317 stations</span><span class="c">293 certified</span><span class="n">23 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>be8e7ad5a9dcb03cdc87b0f858e681a734611a885f98279ab3c4246e9dc6ed02</code><br>frame_hash <code>c1934aff8cc860fc9dac9981c2f48f4b422e64ee78299a7c4c41601dca04f5d7</code><br>prev <code>92f562e7b3025e51bbdddaf50f071e59a112b2c2c5f2bd7cab10e5115e181c52</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-5/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-5/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-5/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-5/pulse.json">pulse</a> · first published in <a href="https://github.com/kody-w/rapp-hive-public/commit/c72cdea41b9f469a9b1d1dd4c8910cdecf37089c">c72cdea</a></p>
<p><b>Since version 5:</b> 2 status change(s), 0 new repo(s), 0 removed, 29 repo(s) at a new commit.</p>
<ul><li>RAPP: not yet → certified</li><li>RAR: not yet → certified</li></ul>
<p>0 lifecycle change(s), 0 version change(s), 0 channel change(s), 11 member card change(s), 0 repo(s) left the network.</p>
<ul><li>hive-hub: member card added</li><li>hive-hub-join: member card added</li><li>hive-hub-mcp: member card added</li><li>lisppy: member card added</li><li>rapp-1: member card added</li><li>rapp-drift-lint: member card added</li><li>rapp-hive-hub: member card added</li><li>rapp-hive-hub-join: member card added</li><li>rapp-model-hive: member card added</li><li>rapp-work: member card added</li><li>RAR: member card added</li></ul>
</article>
<article>
<h3>Version 5 · 2026-09-26 05:17 UTC <span class="seq">seq 4</span></h3>
<p class="totals"><span>317 stations</span><span class="c">291 certified</span><span class="n">25 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>92f562e7b3025e51bbdddaf50f071e59a112b2c2c5f2bd7cab10e5115e181c52</code><br>frame_hash <code>0af558a1ce370428c118493ebca5ff576194e23a3cc922515a3982d547fd0f56</code><br>prev <code>29c2f3e514133c2e1b17f2385a4721618de80fe2bf527a95fcb21b6ee62cdec2</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-4/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-4/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-4/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-4/pulse.json">pulse</a> · first published in <a href="https://github.com/kody-w/rapp-hive-public/commit/eafa6de7e04a3d536c21976c1d85e845a499cd7b">eafa6de</a></p>
<p><b>Since version 4:</b> 0 status change(s), 0 new repo(s), 0 removed, 5 repo(s) at a new commit.</p>
<p>0 lifecycle change(s), 0 version change(s), 0 channel change(s), 0 repo(s) left the network.</p>
</article>
<article>
<h3>Version 4 · 2026-09-26 04:22 UTC <span class="seq">seq 3</span></h3>
<p class="totals"><span>317 stations</span><span class="c">291 certified</span><span class="n">25 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>29c2f3e514133c2e1b17f2385a4721618de80fe2bf527a95fcb21b6ee62cdec2</code><br>frame_hash <code>b5846dddca1948876a0fa7828fa53733878f94d6c306564526d22f60c14b74f6</code><br>prev <code>da8e4433a325f460f7b0864bc2a101d0eb97035fd0d2fd0ca1d1ab15d653b00c</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-3/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-3/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-3/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-3/pulse.json">pulse</a> · first published in <a href="https://github.com/kody-w/rapp-hive-public/commit/7702790c58a8e024437ae91619db7e76f16ad9e8">7702790</a></p>
<p><b>Since version 3:</b> 0 status change(s), 0 new repo(s), 0 removed, 4 repo(s) at a new commit.</p>
<p>0 lifecycle change(s), 0 version change(s), 0 channel change(s), 0 repo(s) left the network.</p>
</article>
<article>
<h3>Version 3 · 2026-09-26 03:00 UTC <span class="seq">seq 2</span></h3>
<p class="totals"><span>317 stations</span><span class="c">291 certified</span><span class="n">25 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>da8e4433a325f460f7b0864bc2a101d0eb97035fd0d2fd0ca1d1ab15d653b00c</code><br>frame_hash <code>9b614551b5345dbc9c8de2160fec5432c7ab800727e2ca8c7ed8e975e5bf9bc8</code><br>prev <code>3f27d1169b064044de344b30a4efad7b1330e1163f484b4b04967ff7c4a8b14f</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-2/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-2/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-2/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-2/pulse.json">pulse</a> · first published in <a href="https://github.com/kody-w/rapp-hive-public/commit/b684d17b84f525a541dabcce25d89e5771b8f73b">b684d17</a></p>
<p><b>Since version 2:</b> 0 status change(s), 0 new repo(s), 0 removed, 6 repo(s) at a new commit.</p>
<p>0 lifecycle change(s), 1 version change(s), 0 channel change(s), 0 repo(s) left the network.</p>
<ul><li>rapp-static-brainstem: version v1.1.0 → v1.2.0</li></ul>
</article>
<article>
<h3>Version 2 · 2026-09-26 01:45 UTC <span class="seq">seq 1</span></h3>
<p class="totals"><span>317 stations</span><span class="c">291 certified</span><span class="n">25 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>3f27d1169b064044de344b30a4efad7b1330e1163f484b4b04967ff7c4a8b14f</code><br>frame_hash <code>3915e04eb300d0af5e29e94f47fb12983552cfae46b0604516058024c3354bb1</code><br>prev <code>15530d4785bea042a87b06c7dcfe15fec6ede0b0041299bbd4e80e9e8a5b0894</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-1/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-1/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-1/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-26-1/pulse.json">pulse</a> · first published in <a href="https://github.com/kody-w/rapp-hive-public/commit/b92a97c7ca91663cc33f74cad1de9f2d38f7e0d3">b92a97c</a></p>
<p><b>Since version 1:</b> 0 status change(s), 0 new repo(s), 0 removed, 24 repo(s) at a new commit.</p>
<p>0 lifecycle change(s), 0 version change(s), 0 channel change(s), 0 repo(s) left the network. Version 1 recorded no versions or channels, so none are compared.</p>
</article>
<article>
<h3>Version 1 · 2026-09-25 18:16 UTC <span class="seq">seq 0</span></h3>
<p class="totals"><span>317 stations</span><span class="c">291 certified</span><span class="n">25 not yet</span><span class="u">1 unchecked</span></p>
<p>payload_hash <code>15530d4785bea042a87b06c7dcfe15fec6ede0b0041299bbd4e80e9e8a5b0894</code><br>frame_hash <code>d765d2698582e937af9cf75e6cb2851d6d1c10e546db1b4e5fe640c591b8b833</code><br>prev <code>null</code></p>
<p><a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-25-0/subway.html">map</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-25-0/subway.pdf">poster</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-25-0/subway.svg">SVG</a> · <a href="https://kody-w.github.io/rapp-hive-public/portfolio/versions/2026-09-25-0/pulse.json">pulse</a> · first published in <a href="https://github.com/kody-w/rapp-hive-public/commit/a8f4cd86f6248d07f98ce2c38d1a3c0f97307a31">a8f4cd8</a></p>
<p>Genesis: the first pulse, 317 repos. Nothing before it to compare.</p>
</article>
<footer>Generated from the pulse frames by rapp1_network/timeline.py (source in <a href="https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/tools">portfolio/tools</a>, SHA-256 <code>3155b45d96a6dc06e0deba84857560768579c5405df106ab0a3f8c7d1e81340b</code>; the head pulse's generator names all 27 file(s) of that release).</footer>
</main>
</body>
</html>
{:/}
