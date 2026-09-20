<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wi-Fi Monitor</title><style>
:root{--bg:#fafaf9;--fg:#1c1917;--mut:#78716c;--line:#e7e5e4;--card:#fff;--ok:#15803d;--warn:#b45309;--bad:#b91c1c;--accent:#0369a1}
@media(prefers-color-scheme:dark){:root{--bg:#0c0a09;--fg:#f5f5f4;--mut:#a8a29e;--line:#292524;--card:#1c1917;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--accent:#38bdf8}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,system-ui,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);margin:0 0 24px;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:24px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.k{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
.v{font-size:26px;font-weight:600;margin-top:4px;font-variant-numeric:tabular-nums}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}
h2{font-size:14px;margin:26px 0 10px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
svg{width:100%;height:150px;display:block}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-weight:500;font-size:11px;text-transform:uppercase}
td{font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:1px 7px;border-radius:99px;font-size:11px;background:var(--line)}
.scroll{overflow-x:auto}
</style></head><body><div class="wrap">
<h1>Wi-Fi Monitor</h1>
<p class="sub">Probes report every 5 minutes. Jitter is the number that decides call quality &mdash; under 15&nbsp;ms is healthy, over 30&nbsp;ms breaks calls.</p>
<div id="app">Loading&hellip;</div></div>
<script>
const $=s=>document.querySelector(s);
const f=(n,d=1)=>n==null?'—':Number(n).toFixed(d);
function cls(v,w,b){return v==null?'':v>=b?'bad':v>=w?'warn':'ok'}
function spark(pts,warn,bad,unit){
  if(!pts.length) return '<svg></svg>';
  const w=1000,h=150,pad=22;
  const ys=pts.map(p=>p.v).filter(v=>v!=null);
  const max=Math.max(bad*1.2,...ys),min=0;
  const X=i=>pad+i*(w-pad*2)/Math.max(1,pts.length-1);
  const Y=v=>h-pad-(v-min)/(max-min||1)*(h-pad*2);
  const d=pts.map((p,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(p.v??0).toFixed(1)).join(' ');
  const band=(y1,y2,c)=>`<rect x="${pad}" y="${Y(y2)}" width="${w-pad*2}" height="${Math.max(0,Y(y1)-Y(y2))}" fill="${c}" opacity=".08"/>`;
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
   ${band(warn,bad,'orange')}${band(bad,max,'red')}
   <line x1="${pad}" y1="${Y(warn)}" x2="${w-pad}" y2="${Y(warn)}" stroke="orange" stroke-dasharray="4 4" opacity=".5"/>
   <line x1="${pad}" y1="${Y(bad)}" x2="${w-pad}" y2="${Y(bad)}" stroke="red" stroke-dasharray="4 4" opacity=".5"/>
   <path d="${d}" fill="none" stroke="var(--accent)" stroke-width="1.8"/>
   <text x="2" y="12" font-size="11" fill="currentColor" opacity=".55">${f(max,0)}${unit}</text>
   <text x="2" y="${h-6}" font-size="11" fill="currentColor" opacity=".55">0</text></svg>`;
}
fetch('api.php?days=2').then(r=>r.json()).then(rows=>{
  if(!rows.length){$('#app').innerHTML='<div class="card">No samples yet. Probes POST to <code>ingest.php</code>.</div>';return}
  const hosts=[...new Set(rows.map(r=>r.host))];
  const last=rows[rows.length-1];
  const recent=rows.slice(-36);
  const avgJit=recent.reduce((a,r)=>a+(r.wifi_hop?.jitter||0),0)/recent.length;
  const worst=Math.max(...recent.map(r=>r.wifi_hop?.max||0));
  const flagged=rows.filter(r=>(r.flags||[]).length);
  let h=`<div class="grid">
    <div class="card"><div class="k">Jitter (3h avg)</div><div class="v ${cls(avgJit,15,30)}">${f(avgJit)} <span style="font-size:13px">ms</span></div></div>
    <div class="card"><div class="k">Worst spike (3h)</div><div class="v ${cls(worst,60,120)}">${f(worst,0)} <span style="font-size:13px">ms</span></div></div>
    <div class="card"><div class="k">Mesh nodes</div><div class="v">${last.node_count??'—'}</div></div>
    <div class="card"><div class="k">Probes reporting</div><div class="v">${hosts.length}</div></div>
    <div class="card"><div class="k">Samples</div><div class="v">${rows.length}</div></div></div>`;
  for(const host of hosts){
    const hr=rows.filter(r=>r.host===host).slice(-160);
    const cur=hr[hr.length-1];
    h+=`<h2>${host} &nbsp;<span class="pill">${cur.rf?.signal_dbm??'?'} dBm &middot; ch ${cur.rf?.channel??'?'} &middot; ${cur.rf?.tx_rate_mbps??'?'} Mbps</span></h2>
        <div class="card"><div class="k" style="margin-bottom:6px">Wi-Fi hop jitter (ms)</div>
        ${spark(hr.map(r=>({v:r.wifi_hop?.jitter})),15,30,'ms')}</div>`;
  }
  h+=`<h2>Events</h2><div class="card scroll"><table><tr><th>Time</th><th>Probe</th><th>Flags</th><th>Jitter</th><th>Max</th><th>Signal</th></tr>`;
  for(const r of flagged.slice(-40).reverse())
    h+=`<tr><td>${(r.ts||'').replace('T',' ').slice(5,16)}</td><td>${r.host}</td>
        <td>${(r.flags||[]).map(x=>`<span class="pill">${x}</span>`).join(' ')}</td>
        <td class="${cls(r.wifi_hop?.jitter,15,30)}">${f(r.wifi_hop?.jitter)}</td>
        <td>${f(r.wifi_hop?.max,0)}</td><td>${r.rf?.signal_dbm??'—'}</td></tr>`;
  if(!flagged.length) h+='<tr><td colspan="6" style="color:var(--mut)">No events — everything within thresholds.</td></tr>';
  h+='</table></div>';
  $('#app').innerHTML=h;
}).catch(e=>$('#app').innerHTML='<div class="card bad">Failed to load: '+e+'</div>');
</script></body></html>
