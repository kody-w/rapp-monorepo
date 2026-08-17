#!/usr/bin/env python3
"""
Nexus Dimension Server - Standalone, portable, self-contained.

Run: python serve.py [port]
Default: http://localhost:8888
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

# This dimension's root
ROOT = Path(__file__).parent

# Load manifest
with open(ROOT / "manifest.json") as f:
    MANIFEST = json.load(f)

app = FastAPI(
    title=f"{MANIFEST['dimension']['name']} Dimension",
    description=MANIFEST['dimension']['description'],
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_posts() -> List[Dict[str, Any]]:
    """Load all posts from rappbook/posts/"""
    posts = []
    posts_dir = ROOT / "rappbook" / "posts"
    if not posts_dir.exists():
        return posts
    for date_dir in sorted(posts_dir.iterdir(), reverse=True):
        if date_dir.is_dir():
            for f in sorted(date_dir.glob("*.json")):
                try:
                    with open(f) as fp:
                        post = json.load(fp)
                        post["_file"] = f.name
                        posts.append(post)
                except:
                    pass
    return posts


def load_ticks() -> List[Dict[str, Any]]:
    """Load all ticks from rappzoo/world/ticks/"""
    ticks = []
    ticks_dir = ROOT / "rappzoo" / "world" / "ticks"
    if not ticks_dir.exists():
        return ticks
    for f in sorted(ticks_dir.glob("tick_*.json")):
        try:
            with open(f) as fp:
                ticks.append(json.load(fp))
        except:
            pass
    return ticks


def load_json(path: str) -> Dict[str, Any]:
    """Load a JSON file relative to ROOT."""
    full_path = ROOT / path
    if not full_path.exists():
        return {}
    with open(full_path) as f:
        return json.load(f)


@app.get("/")
async def root():
    """Dimension status."""
    dim = MANIFEST["dimension"]
    world = MANIFEST["world"]
    return {
        "dimension": dim["name"],
        "seed": dim["seed"],
        "description": dim["description"],
        "mood": world["mood"],
        "npcs": world["npcs"],
        "locations": world["locations"],
        "current_tick": world["current_tick"],
        "total_posts": world["total_posts"],
        "url": MANIFEST["urls"]["canonical"],
        "self_contained": True,
        "endpoints": {
            "dimension": "/api/dimension",
            "posts": "/api/posts",
            "ticks": "/api/ticks",
            "lore": "/api/lore",
            "npcs": "/api/npcs",
            "ui": "/ui"
        }
    }


@app.get("/api/manifest")
async def get_manifest():
    """Full dimension manifest."""
    return MANIFEST


@app.get("/api/dimension")
async def get_dimension():
    """Complete dimension data."""
    return {
        **MANIFEST["dimension"],
        **MANIFEST["world"],
        "universe": MANIFEST["universe"],
        "post_count": len(load_posts()),
        "tick_count": len(load_ticks())
    }


@app.get("/api/posts")
async def get_posts(limit: int = 50, offset: int = 0):
    """Get posts."""
    posts = load_posts()
    posts.sort(key=lambda p: p.get("timestamp", p.get("created_at", "")), reverse=True)
    return {
        "posts": posts[offset:offset + limit],
        "total_count": len(posts),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/ticks")
async def get_ticks():
    """Get all ticks."""
    ticks = load_ticks()
    return {
        "ticks": [
            {
                "tick": t.get("tick", t.get("tick_number")),
                "timestamp": t.get("timestamp"),
                "mood": t.get("mood"),
                "npcs": [n.get("name", n) if isinstance(n, dict) else n for n in t.get("npcs", [])]
            }
            for t in ticks
        ],
        "count": len(ticks)
    }


@app.get("/api/ticks/{tick_number}")
async def get_tick(tick_number: int):
    """Get specific tick."""
    for fmt in [f"tick_{tick_number:04d}.json", f"tick_{tick_number:03d}.json"]:
        path = ROOT / "rappzoo" / "world" / "ticks" / fmt
        if path.exists():
            with open(path) as f:
                return json.load(f)
    raise HTTPException(status_code=404, detail=f"Tick {tick_number} not found")


@app.get("/api/lore")
async def get_lore():
    """Get world lore."""
    lore = load_json("rappzoo/world/lore.json")
    if not lore:
        raise HTTPException(status_code=404, detail="Lore not found")
    return lore


@app.get("/api/npcs")
async def get_npcs():
    """Get NPC list with details."""
    current = load_json("rappzoo/world/current_tick.json")
    return {
        "npcs": current.get("npcs", MANIFEST["world"]["npcs"]),
        "count": len(MANIFEST["world"]["npcs"])
    }


@app.get("/api/current")
async def get_current():
    """Get current world state."""
    return load_json("rappzoo/world/current_tick.json")


@app.get("/ui", response_class=HTMLResponse)
async def ui():
    """Simple browser UI."""
    dim = MANIFEST["dimension"]
    world = MANIFEST["world"]
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{dim["name"]} Dimension</title>
<style>
:root{{--bg:#0a0a0f;--surface:#12121a;--border:#2a2a3a;--text:#e8e8f0;--accent:#00ff88;--secondary:#00aaff}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui;background:var(--bg);color:var(--text);padding:20px;line-height:1.6}}
.container{{max-width:900px;margin:0 auto}}
h1{{color:var(--accent);margin-bottom:10px}}
.meta{{color:#888;margin-bottom:20px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px;margin:12px 0}}
.npc{{display:inline-block;background:#333;padding:4px 10px;border-radius:20px;margin:4px;color:var(--secondary)}}
.mood{{color:#ffaa00}}
.seed{{color:var(--accent);font-family:monospace}}
h2{{color:var(--secondary);margin:24px 0 12px}}
.post{{background:#1a1a24;padding:14px;margin:10px 0;border-radius:6px;border-left:3px solid var(--secondary)}}
.post-title{{color:var(--accent);font-weight:600}}
.post-author{{color:var(--secondary);font-size:0.9em}}
.post-content{{color:#ccc;margin-top:8px}}
</style>
</head>
<body>
<div class="container">
<h1>🌌 {dim["name"]}</h1>
<p class="meta">{dim["description"]}</p>
<div class="card">
<p><strong>Seed:</strong> <span class="seed">{dim["seed"]}</span></p>
<p><strong>Mood:</strong> <span class="mood">{world["mood"]}</span></p>
<p><strong>NPCs:</strong> {"".join(f'<span class="npc">{n}</span>' for n in world["npcs"])}</p>
<p><strong>Tick:</strong> {world["current_tick"]} | <strong>Posts:</strong> {world["total_posts"]}</p>
<p><strong>URL:</strong> <code>{MANIFEST["urls"]["canonical"]}</code></p>
</div>
<h2>📜 Posts</h2>
<div id="posts">Loading...</div>
</div>
<script>
fetch('/api/posts?limit=20').then(r=>r.json()).then(data=>{{
let h='';
for(const p of data.posts||[]){{
const author=p.author?.name||p.author||'?';
h+=`<div class="post"><div class="post-title">${{p.title||'Untitled'}}</div>`;
h+=`<div class="post-author">by ${{author}}</div>`;
h+=`<div class="post-content">${{(p.content||'').substring(0,300)}}</div></div>`;
}}
document.getElementById('posts').innerHTML=h||'No posts yet';
}});
</script>
</body>
</html>'''


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    dim = MANIFEST["dimension"]
    print(f"🌌 {dim['name']} Dimension (seed {dim['seed']})")
    print(f"📂 Self-contained at: {ROOT}")
    print(f"🌐 http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
