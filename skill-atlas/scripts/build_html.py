"""Render a searchable, self-contained bilingual-source Chinese skill map with fluid, soft crystal micro-animations."""
from __future__ import annotations

import json
from pathlib import Path


def render(snapshot: dict) -> str:
    payload = json.dumps(snapshot, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return TEMPLATE.replace("__ATLAS_JSON__", payload)


def write_html(snapshot: dict, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(snapshot), encoding="utf-8")
    return output


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>技能地图 · 空间水晶版</title><link rel="icon" href="data:,"><style>
:root{
  color-scheme:dark;
  --bg-deep:#080c14;
  --panel-glass:rgba(12, 18, 30, 0.72);
  --border-glass:rgba(255, 255, 255, 0.14);
  --ink:#ffffff;
  --ink-muted:#94a3b8;
  --crystal-cyan:#38bdf8;
  --ease-soft:cubic-bezier(0.16, 1, 0.3, 1);
}
*{box-sizing:border-box;scrollbar-width:thin;scrollbar-color:#334155 #080c14}
body{
  margin:0;
  background:#080c14;
  color:var(--ink);
  font:14px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
  overflow-x:hidden;
  background-image:
    radial-gradient(circle at 50% 25%, #131d33 0%, #080c14 75%),
    radial-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px);
  background-size:100% 100%, 24px 24px;
}
button,input,select{font:inherit;color:inherit}
button{cursor:pointer}
button:focus-visible,input:focus-visible,select:focus-visible,.node:focus-visible .plate{outline:2px solid var(--crystal-cyan);outline-offset:3px}
::selection{background:#0284c7;color:#fff}

header{
  height:76px;
  padding:16px 28px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  border-bottom:1px solid var(--border-glass);
  background:rgba(8, 12, 20, 0.85);
  backdrop-filter:blur(24px);
  position:relative;
  z-index:10;
}
h1{font-size:21px;font-weight:700;letter-spacing:-.02em;margin:0;display:flex;align-items:center;gap:10px}
.host-badge{
  font-size:12px;
  font-weight:600;
  color:#38bdf8;
  background:rgba(56, 189, 248, 0.12);
  border:1px solid rgba(56, 189, 248, 0.35);
  padding:2px 10px;
  border-radius:12px;
  box-shadow:0 0 12px rgba(56, 189, 248, 0.2);
}
header p{margin:2px 0 0;color:var(--ink-muted);font-size:12px}
.stats{display:flex;gap:24px;color:var(--ink-muted);font-size:12px;align-items:center}
.stats strong{font-size:18px;color:#fff;margin-right:4px;font-variant-numeric:tabular-nums;font-weight:700}

.toolbar{
  display:flex;
  gap:10px;
  align-items:center;
  padding:10px 28px;
  border-bottom:1px solid var(--border-glass);
  background:rgba(10, 16, 26, 0.72);
  backdrop-filter:blur(20px);
  position:relative;
  z-index:9;
}
input,select,.toolbar button,.map-controls button{
  background:rgba(255, 255, 255, 0.06);
  border:1px solid var(--border-glass);
  border-top:1px solid rgba(255, 255, 255, 0.3);
  border-radius:8px;
  padding:7px 12px;
  font-size:13px;
  color:#fff;
  backdrop-filter:blur(12px);
  transition:all .2s ease;
}
.toolbar input{flex:1;min-width:140px;max-width:380px;caret-color:var(--crystal-cyan)}
input::placeholder{color:#64748b}
input:focus,select:focus{border-color:var(--crystal-cyan);box-shadow:0 0 14px rgba(56, 189, 248, 0.3)}
button:hover{
  border-color:rgba(255, 255, 255, 0.4);
  background:rgba(255, 255, 255, 0.12);
}

.layout{
  display:grid;
  grid-template-columns:220px minmax(0,1fr);
  height:calc(100dvh - 136px);
  min-height:500px;
}
.layout:has(.details.open){grid-template-columns:220px minmax(0,1fr) 320px}

aside,.details{
  background:var(--panel-glass);
  backdrop-filter:blur(24px);
  padding:20px 16px;
  overflow:auto;
  position:relative;
  z-index:8;
}
aside{border-right:1px solid var(--border-glass)}
.details{display:none;border-left:1px solid var(--border-glass)}
.details.open{display:block}

.panel-title{font-size:13.5px;margin:0 0 16px;font-weight:700;color:#fff;letter-spacing:.02em;display:flex;align-items:center;gap:8px}
.panel-title::before{
  content:"";
  display:inline-block;
  width:3px;
  height:13px;
  background:#38bdf8;
  border-radius:2px;
  box-shadow:0 0 8px #38bdf8;
}

.category{
  display:flex;
  align-items:center;
  gap:8px;
  justify-content:space-between;
  width:100%;
  text-align:left;
  border:1px solid transparent;
  background:transparent;
  border-radius:8px;
  padding:8px 10px;
  margin:2px 0;
  font-size:13px;
  color:#cbd5e1;
  transition:all .2s ease;
}
.category:hover{
  background:rgba(255, 255, 255, 0.06);
  color:#fff;
}
.category span:last-child{color:var(--ink-muted);font-size:11px;font-variant-numeric:tabular-nums}
.category.child{width:calc(100% - 16px);margin-left:16px;font-size:12px;color:#94a3b8}
.category.active{
  background:rgba(56, 189, 248, 0.16);
  border:1px solid rgba(56, 189, 248, 0.45);
  color:#fff;
  font-weight:600;
  box-shadow:0 0 16px rgba(56, 189, 248, 0.2);
}
.chevron{display:inline-block;width:12px;color:var(--crystal-cyan);font-size:11px}
.legend{font-size:12px;color:var(--ink-muted);margin-top:24px;padding-top:16px;border-top:1px dashed var(--border-glass)}
.legend p{margin:4px 0}

main{min-width:0;position:relative;overflow:hidden}
#canvas{width:100%;height:100%;display:block;touch-action:none;cursor:grab}
#canvas.dragging{cursor:grabbing}

#viewport{
  transition:transform 0.42s var(--ease-soft);
  will-change:transform;
}

/* S-Curve Liquid Fiber Optic Lines with Smooth Morphing */
.edge{
  fill:none;
  stroke-width:1.8;
  opacity:.48;
  transition:d 0.42s var(--ease-soft), stroke-width 0.2s ease, opacity 0.35s ease;
  will-change:d, opacity;
}
.edge:hover,.edge.active{
  stroke-width:2.8;
  opacity:1;
  filter:drop-shadow(0 0 8px var(--node-color));
}

/* Soft, Fluid Spring Easing on Node Positions */
.node{
  cursor:pointer;
  outline:none;
  user-select:none;
  transition:transform 0.42s var(--ease-soft), opacity 0.35s ease;
  will-change:transform, opacity;
}
.node:hover{
  transform:translate(var(--nx), var(--ny)) scale(1.035) !important;
  transition:transform 0.2s var(--ease-soft) !important;
}
.node:active{
  transform:translate(var(--nx), var(--ny)) scale(0.96) !important;
  transition:transform 0.08s ease !important;
}
.node.selected{
  transform:translate(var(--nx), var(--ny)) scale(1.05);
}

/* Pure Optical Crystal Glass Plate */
.node .plate{
  fill:url(#pure-crystal-grad);
  stroke:rgba(255, 255, 255, 0.22);
  stroke-width:1.2;
  filter:url(#clean-shadow);
  transition:stroke 0.25s ease, filter 0.25s ease;
}
.node .crystal-top-sheen{
  fill:url(#specular-sheen);
  pointer-events:none;
  opacity:.65;
}
.node .crystal-tint{
  fill:var(--node-color);
  opacity:.08;
  pointer-events:none;
  transition:opacity 0.25s ease;
}
.node.selected .crystal-tint{
  opacity:.22;
}
.node:hover .plate{
  stroke:var(--node-color);
  stroke-width:1.8;
  filter:url(#clean-glow-hover);
}
.node.selected .plate{
  stroke:var(--node-color);
  stroke-width:2.2;
  filter:url(#clean-glow-active);
}

.node .label{
  fill:#ffffff;
  font-size:14px;
  font-weight:600;
  text-anchor:start;
  pointer-events:none;
  letter-spacing:.015em;
  filter:drop-shadow(0 1px 2px rgba(0,0,0,0.7));
  transition:fill 0.2s ease;
}
.node.category-node .label{font-size:14px;font-weight:700}
.node.subcategory-node .label{font-size:13px;font-weight:600}
.node.skill-node .label{font-size:12.5px;font-weight:550;fill:#f1f5f9}
.node.selected .label{fill:#ffffff;font-weight:700;filter:drop-shadow(0 0 8px var(--node-color))}

/* Gemstone Orb Markers */
.node .gem-orb{
  fill:var(--node-color);
  filter:drop-shadow(0 0 6px var(--node-color));
}

.node .toggle-btn{cursor:pointer}
.node .toggle-bg{
  fill:rgba(15, 23, 40, 0.9);
  stroke:rgba(255, 255, 255, 0.35);
  stroke-width:1.2;
  transition:all .18s var(--ease-soft);
}
.node:hover .toggle-bg{fill:var(--node-color);stroke:#fff}
.node .toggle-text{
  fill:#ffffff;
  font-size:11px;
  font-weight:800;
  text-anchor:middle;
  pointer-events:none;
}
.node:hover .toggle-text{fill:#080c14}

.node.dimmed{opacity:.18}

/* Central Pristine Crystal Core (NO dashed ring) */
.center-node{cursor:pointer}
.center-node .orb{
  fill:url(#pure-crystal-grad);
  stroke:rgba(56, 189, 248, 0.6);
  stroke-width:1.8;
  filter:url(#center-glow);
  transition:all .25s ease;
}
.center-node:hover .orb{
  stroke:#38bdf8;
  filter:url(#center-glow-hover);
}
.center-node text{text-anchor:middle;pointer-events:none}
.center-node .host-label{
  font-size:20px;
  font-weight:800;
  fill:#ffffff;
  letter-spacing:-.01em;
  filter:drop-shadow(0 0 10px rgba(56, 189, 248, 0.6));
}
.center-node .count{
  font-size:11.5px;
  font-weight:600;
  fill:#38bdf8;
  letter-spacing:.02em;
}

.map-controls{
  position:absolute;
  bottom:18px;
  left:50%;
  transform:translateX(-50%);
  display:flex;
  gap:6px;
  background:rgba(12, 18, 30, 0.85);
  backdrop-filter:blur(16px);
  padding:5px 8px;
  border:1px solid var(--border-glass);
  border-top:1px solid rgba(255, 255, 255, 0.28);
  border-radius:12px;
  box-shadow:0 8px 24px rgba(0,0,0,0.4), 0 0 14px rgba(56, 189, 248, 0.15);
  white-space:nowrap;
  z-index:5;
}
.map-note{
  position:absolute;
  top:14px;
  left:18px;
  font-size:12px;
  color:#94a3b8;
  pointer-events:none;
  background:rgba(12, 18, 30, 0.75);
  padding:4px 12px;
  border-radius:8px;
  border:1px solid var(--border-glass);
  border-top:1px solid rgba(255, 255, 255, 0.25);
  backdrop-filter:blur(12px);
  z-index:5;
}

.details h2{
  font-size:18px;
  line-height:1.4;
  overflow-wrap:anywhere;
  margin:0 0 16px;
  color:#fff;
  font-weight:700;
  text-shadow:0 0 12px rgba(255,255,255,0.25);
}
.details h3{
  font-size:12px;
  color:var(--crystal-cyan);
  margin:20px 0 8px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.04em;
  display:flex;
  align-items:center;
  gap:6px;
}
.details p{line-height:1.75;overflow-wrap:anywhere;margin:8px 0;color:#cbd5e1}
.tag{
  display:inline-block;
  background:rgba(56, 189, 248, 0.12);
  border:1px solid rgba(56, 189, 248, 0.35);
  border-radius:6px;
  padding:3px 8px;
  margin:3px 4px 3px 0;
  font-size:12px;
  color:#7dd3fc;
  overflow-wrap:anywhere;
  max-width:100%;
}
.path{
  font-size:11.5px;
  color:#94a3b8;
  font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;
  background:rgba(8, 12, 20, 0.75);
  padding:7px 9px;
  border-radius:6px;
  border:1px solid var(--border-glass);
  word-break:break-all;
}
.muted-note{color:var(--ink-muted);font-size:12px}
.close{
  float:right;
  background:none;
  border:0;
  font-size:20px;
  color:var(--ink-muted);
  line-height:1;
  padding:2px 6px;
  border-radius:4px;
}
.close:hover{color:#fff;background:rgba(255,255,255,0.12)}
.detail-skill{
  display:block;
  width:100%;
  text-align:left;
  background:transparent;
  border:0;
  border-bottom:1px solid var(--border-glass);
  padding:9px 6px;
  font-size:13px;
  color:#e2e8f0;
  overflow-wrap:anywhere;
  transition:all .15s ease;
  border-radius:6px;
}
.detail-skill:hover{
  color:var(--crystal-cyan);
  background:rgba(56, 189, 248, 0.1);
  padding-left:10px;
}
.empty{position:absolute;top:45%;width:100%;text-align:center;color:var(--ink-muted);font-size:14px}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}

@media(max-width:1100px){
  .layout,.layout:has(.details.open){grid-template-columns:190px minmax(0,1fr)}
  .details.open{
    position:fixed;
    z-index:50;
    right:0;
    top:0;
    height:100dvh;
    width:320px;
    max-width:92vw;
    box-shadow:-16px 0 36px rgba(0,0,0,0.7);
  }
}
@media(max-width:650px){
  header{padding:12px 16px;height:auto;flex-wrap:wrap;gap:8px}
  .toolbar{padding:8px 12px;flex-wrap:wrap;gap:6px}
  .layout,.layout:has(.details.open){display:flex;flex-direction:column;height:auto;min-height:0}
  aside{max-height:160px;border-bottom:1px solid var(--border-glass);padding:10px 14px}
  .legend{display:none}
  main{height:65dvh;min-height:420px;flex:none}
}
</style></head><body>
<header>
  <div>
    <h1>技能地图 <span class="host-badge" id="host"></span></h1>
    <p>从一个终端，探索你的全部技能</p>
  </div>
  <div class="stats">
    <div><strong id="skillCount">0</strong>技能</div>
    <div><strong id="categoryCount">0</strong>分类</div>
    <div class="warnings"><strong id="warningCount">0</strong>警告</div>
  </div>
</header>
<div class="toolbar">
  <label class="sr-only" for="search">搜索技能</label>
  <input id="search" placeholder="搜索技能名称、说明或触发词" autocomplete="off">
  <label class="sr-only" for="status">筛选状态</label>
  <select id="status">
    <option value="all">全部状态</option>
    <option value="valid">有效技能</option>
    <option value="warning">有警告</option>
    <option value="invalid">无法读取</option>
  </select>
  <button id="expand">全部展开</button>
  <button id="collapse">全部收起</button>
  <button id="reset">重置视图</button>
</div>
<div class="layout">
  <aside>
    <h2 class="panel-title">分类列表</h2>
    <div id="categories"></div>
    <div class="legend">
      <p>一级分类 → 二级分类 → 技能</p>
      <p>点击分类原地展开；点击技能查看说明。</p>
    </div>
  </aside>
  <main>
    <div class="map-note">交互式技能脑图 · 空间流光水晶态 · 柔性缓动动效 · 滚轮缩放</div>
    <svg id="canvas" role="group" aria-label="交互式技能脑图">
      <defs>
        <!-- Pure Optical Crystal Material: Clear White Frosted Gradient -->
        <linearGradient id="pure-crystal-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.14"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0.03"/>
        </linearGradient>
        <linearGradient id="specular-sheen" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.45"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
        </linearGradient>
        <!-- Clean, Delicate Crystal Glow -->
        <filter id="clean-shadow" x="-20%" y="-30%" width="140%" height="170%">
          <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity=".32"/>
        </filter>
        <filter id="clean-glow-hover" x="-30%" y="-40%" width="160%" height="190%">
          <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000000" flood-opacity=".4"/>
          <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="var(--node-color)" flood-opacity=".65"/>
        </filter>
        <filter id="clean-glow-active" x="-35%" y="-45%" width="170%" height="200%">
          <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity=".5"/>
          <feDropShadow dx="0" dy="0" stdDeviation="14" flood-color="var(--node-color)" flood-opacity=".85"/>
        </filter>
        <filter id="center-glow" x="-25%" y="-30%" width="150%" height="170%">
          <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#38bdf8" flood-opacity=".35"/>
          <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000000" flood-opacity=".4"/>
        </filter>
        <filter id="center-glow-hover" x="-30%" y="-35%" width="160%" height="180%">
          <feDropShadow dx="0" dy="0" stdDeviation="18" flood-color="#38bdf8" flood-opacity=".75"/>
        </filter>
      </defs>
      <g id="viewport">
        <g id="edge-layer"></g>
        <g id="node-layer"></g>
      </g>
    </svg>
    <div id="empty" class="empty" hidden>没有找到匹配的技能</div>
    <div class="map-controls">
      <button id="zoomOut" aria-label="缩小">−</button>
      <button id="fit">适应画布</button>
      <button id="zoomIn" aria-label="放大">＋</button>
    </div>
  </main>
  <section id="details" class="details" aria-live="polite">
    <button id="close" class="close" aria-label="关闭详情">×</button>
    <h2 class="panel-title">详细说明</h2>
    <div id="detailBody"><p class="muted-note">选择一个分类或技能。<br>这里会展示技能用途、中文触发场景和安装路径。</p></div>
  </section>
</div>
<script>
const DATA=__ATLAS_JSON__;
const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
let state={query:'',status:'all',expanded:new Set(),selected:null,zoom:1,pan:{x:0,y:0}},graph=null,drag=null;

// Persistent DOM Element Maps for Smooth Transitions
const nodeMap=new Map();
const edgeMap=new Map();

function esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function filtered(){const q=state.query.toLowerCase();return DATA.skills.filter(s=>(state.status==='all'||s.status===state.status)&&(!q||[s.name,s.description,s.summary,...s.triggers].join(' ').toLowerCase().includes(q)))}
function groups(list){const out=new Map();for(const s of list){if(!out.has(s.category))out.set(s.category,new Map());const ch=out.get(s.category),key=s.parent_category||'';if(!ch.has(key))ch.set(key,[]);ch.get(key).push(s)}return [...out].sort(([a],[b])=>a.localeCompare(b,'zh-CN'))}

// Pure vibrant gemstone crystals
const COLORS=['#38bdf8','#10b981','#a855f7','#f59e0b','#ec4899','#6366f1','#14b8a6','#f43f5e','#8b5cf6','#06b6d4','#eab308','#0ea5e9'];
const measureCanvas=document.createElement('canvas');
const measureCtx=measureCanvas.getContext('2d');
function dimensions(n){
  measureCtx.font=(n.type==='category'?'700 14px':'600 12.5px')+' -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif';
  const textW=Math.ceil(measureCtx.measureText(n.label).width);
  if(n.type==='skill'){
    n.width=Math.max(136,textW+50);
    n.height=34;
  }else if(n.type==='subcategory'){
    n.width=Math.max(116,textW+56);
    n.height=36;
  }else{
    n.width=Math.max(126,textW+72);
    n.height=42;
  }
}

const pk=p=>'cat:'+p,ck=(p,c)=>'sub:'+p+'::'+c;
function opened(id){return !!state.query||state.expanded.has(id)}
function skillNode(s){return{id:s.id,label:s.name,type:'skill',skill:s,children:[]}}
function tree(list){
  return groups(list).map(([p,ch])=>({
    id:pk(p),label:p,type:'category',members:[...ch.values()].flat(),
    children:opened(pk(p))?[...ch].flatMap(([c,m])=>c?[{id:ck(p,c),label:c,type:'subcategory',members:m,children:opened(ck(p,c))?m.map(skillNode):[]}]:m.map(skillNode)):[]
  }));
}

// 100% Deterministic Permanent Lane Allocation - NEVER RE-SORTS!
let permanentLaneMap=null;
function getPermanentLanes(allRoots){
  if(permanentLaneMap)return permanentLaneMap;
  const sorted=[...allRoots].sort((a,b)=>b.members.length-a.members.length);
  const left=[],right=[];
  let sumL=0,sumR=0;
  for(const r of sorted){
    if(sumR<=sumL){right.push(r.label);sumR+=r.members.length}
    else{left.push(r.label);sumL+=r.members.length}
  }
  permanentLaneMap={leftList:left,rightList:right};
  return permanentLaneMap;
}

function layout(list){
  const roots=tree(list);
  const laneConfig=getPermanentLanes(roots);
  const lanes=[[],[]];
  const heights=[0,0];
  const nodes=[],edges=[];

  function measure(n){
    dimensions(n);
    if(!n.children||n.children.length===0){
      n.span=n.height+14;
    }else{
      n.span=Math.max(n.height+14,n.children.reduce((sum,c)=>sum+measure(c),0));
    }
    return n.span;
  }

  roots.forEach((root,i)=>{
    measure(root);
    root.color=COLORS[i%COLORS.length];
  });

  for(const catName of laneConfig.leftList){
    const r=roots.find(x=>x.label===catName);
    if(r){lanes[0].push(r);heights[0]+=r.span}
  }
  for(const catName of laneConfig.rightList){
    const r=roots.find(x=>x.label===catName);
    if(r){lanes[1].push(r);heights[1]+=r.span}
  }

  function place(n,startX,top,dir,color,parent){
    n.dir=dir;n.color=color;n._parent=parent;
    n.x=startX+dir*(n.width/2);
    n.y=top+n.span/2;
    nodes.push(n);
    let childTop=top;
    const childStartX=dir>0?(n.x+n.width/2+64):(n.x-n.width/2-64);
    for(const child of n.children){
      place(child,childStartX,childTop,dir,color,n);
      edges.push({
        source:n,target:child,color,
        sx:dir>0?n.x+n.width/2:n.x-n.width/2,sy:n.y,
        tx:dir>0?child.x-child.width/2:child.x+child.width/2,ty:child.y,
        dir
      });
      childTop+=child.span;
    }
  }

  const centerNode={id:'center',label:DATA.host,type:'center',width:180,height:58,x:0,y:0};
  const categoryStartX=240;

  for(let side=0;side<2;side++){
    const dir=side===1?1:-1;
    let top=-heights[side]/2;
    const startX=dir*categoryStartX;
    for(const root of lanes[side]){
      place(root,startX,top,dir,root.color,centerNode);
      edges.push({
        source:centerNode,target:root,color:root.color,
        sx:dir>0?centerNode.width/2:-centerNode.width/2,
        sy:0,
        tx:dir>0?root.x-root.width/2:root.x+root.width/2,
        ty:root.y,
        dir
      });
      top+=root.span;
    }
  }

  return {
    nodes,edges,centerNode,
    minX:Math.min(-centerNode.width/2-30,...nodes.map(n=>n.x-n.width/2-24)),
    maxX:Math.max(centerNode.width/2+30,...nodes.map(n=>n.x+n.width/2+24)),
    minY:Math.min(-centerNode.height/2-24,...nodes.map(n=>n.y-n.height/2-20)),
    maxY:Math.max(centerNode.height/2+24,...nodes.map(n=>n.y+n.height/2+20))
  };
}

function renderSidebar(list){
  let h='';
  for(const [p,ch] of groups(list)){
    const id=pk(p),children=[...ch].filter(([c])=>c),members=[...ch.values()].flat();
    h+=`<button class="category ${state.selected===id?'active':''}" data-key="${esc(id)}" ${children.length?`aria-expanded="${opened(id)}"`:''}><span>${children.length?`<span class="chevron">${opened(id)?'▾':'▸'}</span>`:''}${esc(p)}</span><span>${members.length}</span></button>`;
    if(opened(id))for(const [c,m] of children){
      h+=`<button class="category child ${state.selected===ck(p,c)?'active':''}" data-key="${esc(ck(p,c))}"><span>${esc(c)}</span><span>${m.length}</span></button>`;
    }
  }
  $('categories').innerHTML=h;
  $('categories').querySelectorAll('button').forEach(b=>b.onclick=()=>chooseCategory(b.dataset.key));
}

function fit(){
  const list=filtered();
  graph=layout(list);
  const svg=$('canvas'),w=svg.clientWidth||800,h=svg.clientHeight||600;
  const availW=Math.max(320,w-80),availH=Math.max(320,h-110);
  const scaleFit=Math.min(availW/(graph.maxX-graph.minX),availH/(graph.maxY-graph.minY),1.1);
  state.zoom=Math.max(0.75,Math.min(1.1,scaleFit));
  state.pan={x:0,y:0};
  draw(false);
}

// IN-PLACE toggle: strictly NEVER jumps pan, smoothly expands with fluid easing!
function toggleCategory(id){
  if(state.expanded.has(id)){
    state.expanded.delete(id);
    for(const k of [...state.expanded]){
      if(k.startsWith('sub:')&&k.includes(id.replace('cat:','')))state.expanded.delete(k);
    }
  }else{
    if(id.startsWith('cat:')){
      for(const k of [...state.expanded]){
        if(k.startsWith('cat:')||k.startsWith('sub:'))state.expanded.delete(k);
      }
      state.expanded.add(id);
    }else if(id.startsWith('sub:')){
      const parentCat=id.split('::')[0].replace('sub:','');
      for(const k of [...state.expanded]){
        if(k.startsWith('sub:'+parentCat+'::'))state.expanded.delete(k);
      }
      state.expanded.add(id);
    }else{
      state.expanded.add(id);
    }
  }
  draw(false);
}

function el(tag,attrs,parent){
  const e=document.createElementNS(NS,tag);
  for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);
  if(parent)parent.appendChild(e);
  return e;
}

// RECONCILED SMOOTH DRAW ENGINE
function draw(refit=false){
  const list=filtered();
  if(refit)fit();
  renderSidebar(list);
  $('skillCount').textContent=list.length;
  $('categoryCount').textContent=groups(list).length;
  $('warningCount').textContent=(DATA.warnings||[]).length+list.filter(s=>s.warnings.length).length;
  $('host').textContent=DATA.host;
  $('empty').hidden=!!list.length;

  graph=layout(list);
  const svg=$('canvas'),w=svg.clientWidth||800,h=svg.clientHeight||600;
  svg.setAttribute('viewBox','0 0 '+w+' '+h);
  const mx=(graph.minX+graph.maxX)/2,my=(graph.minY+graph.maxY)/2;

  const viewport=$('viewport');
  viewport.setAttribute('transform','translate('+(w/2+state.pan.x)+' '+(h/2+state.pan.y)+') scale('+state.zoom+') translate('+(-mx)+' '+(-my)+')');

  const edgeLayer=$('edge-layer');
  const nodeLayer=$('node-layer');
  const q=state.query.toLowerCase();

  // 1. RECONCILE EDGES (Smooth Path Transition)
  const activeEdgeKeys=new Set();
  for(const e of graph.edges){
    const key=e.source.id+'->'+e.target.id;
    activeEdgeKeys.add(key);
    const isRootEdge=e.source.id==='center';
    const sx=e.sx,sy=e.sy,tx=e.tx,ty=e.ty;
    const mxCurve=(sx+tx)/2;
    const d='M '+sx+' '+sy+' C '+mxCurve+' '+sy+', '+mxCurve+' '+ty+', '+tx+' '+ty;
    const active=state.selected&&(state.selected===e.source.id||state.selected===e.target.id);

    let path=edgeMap.get(key);
    if(!path){
      // New Edge: emerge smoothly from origin!
      path=el('path',{
        d,class:'edge'+(active?' active':''),
        stroke:e.color,
        style:'--node-color:'+e.color+';opacity:0;'
      },edgeLayer);
      edgeMap.set(key,path);
      requestAnimationFrame(()=>{
        path.style.opacity=active?'1':(isRootEdge?'0.55':'0.45');
      });
    }else{
      // Existing Edge: smoothly update d attribute (smooth morphing)!
      path.setAttribute('d',d);
      path.setAttribute('class','edge'+(active?' active':''));
      path.style.opacity=active?'1':(isRootEdge?'0.55':'0.45');
      path.setAttribute('stroke-width',active?'2.8':(isRootEdge?'2.2':'1.8'));
    }
  }

  // Remove stale edges with soft fade-out
  for(const [key,path] of edgeMap.entries()){
    if(!activeEdgeKeys.has(key)){
      path.style.opacity='0';
      setTimeout(()=>{if(path.parentNode)path.parentNode.removeChild(path);},380);
      edgeMap.delete(key);
    }
  }

  // 2. RECONCILE NODES (Smooth Position Spring Easing)
  const activeNodeIds=new Set(graph.nodes.map(n=>n.id));
  activeNodeIds.add('center');

  // Center Node
  let centerG=nodeMap.get('center');
  if(!centerG){
    centerG=el('g',{class:'node center-node',role:'button',tabindex:0,'aria-label':DATA.host,style:'--nx:0px;--ny:0px;transform:translate(0, 0);'},nodeLayer);
    el('rect',{x:-graph.centerNode.width/2,y:-graph.centerNode.height/2,width:graph.centerNode.width,height:graph.centerNode.height,rx:18,class:'orb'},centerG);
    el('rect',{x:-graph.centerNode.width/2+1,y:-graph.centerNode.height/2+1,width:graph.centerNode.width-2,height:18,rx:10,class:'crystal-top-sheen'},centerG);
    const title=el('text',{y:-3,class:'host-label'},centerG);
    title.textContent=DATA.host;
    el('text',{y:18,class:'count'},centerG).textContent=list.length+' 个技能';
    centerG.onclick=fit;
    centerG.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fit()}};
    nodeMap.set('center',centerG);
  }

  for(const n of graph.nodes){
    let g=nodeMap.get(n.id);
    const active=state.selected===n.id;
    const isMatch=q&&n.type==='skill'&&[n.skill.name,n.skill.description,n.skill.summary,...n.skill.triggers].join(' ').toLowerCase().includes(q);
    const isDimmed=q&&n.type==='skill'&&!isMatch;

    if(!g){
      // NEW NODE: start smoothly from parent position, scale 0.65, opacity 0
      g=createNodeDOM(n);
      const originX=n._parent?n._parent.x:n.x;
      const originY=n._parent?n._parent.y:n.y;
      g.style.setProperty('--nx',n.x+'px');
      g.style.setProperty('--ny',n.y+'px');
      g.style.transform='translate('+originX+'px, '+originY+'px) scale(0.65)';
      g.style.opacity='0';
      nodeLayer.appendChild(g);
      nodeMap.set(n.id,g);

      // Blossom out to target position on next frame
      requestAnimationFrame(()=>{
        g.style.transform='translate('+n.x+'px, '+n.y+'px)'+(active?' scale(1.05)':'');
        g.style.opacity=isDimmed?'0.18':'1';
      });
    }else{
      // EXISTING NODE: smoothly glide to new position!
      g.style.setProperty('--nx',n.x+'px');
      g.style.setProperty('--ny',n.y+'px');
      g.style.transform='translate('+n.x+'px, '+n.y+'px)'+(active?' scale(1.05)':'');
      g.style.opacity=isDimmed?'0.18':'1';
      g.setAttribute('class','node '+n.type+'-node'+(active?' selected':'')+(isDimmed?' dimmed':''));
      g.setAttribute('aria-pressed',active);

      // Update toggle icon if present
      const toggleText=g.querySelector('.toggle-text');
      if(toggleText){
        toggleText.textContent=opened(n.id)?'−':'+';
      }
    }
    g._parentX=n._parent?n._parent.x:0;
    g._parentY=n._parent?n._parent.y:0;
  }

  // Remove collapsed nodes with soft slide back to parent
  for(const [id,g] of nodeMap.entries()){
    if(!activeNodeIds.has(id)){
      g.style.transform='translate('+(g._parentX||0)+'px, '+(g._parentY||0)+'px) scale(0.65)';
      g.style.opacity='0';
      setTimeout(()=>{if(g.parentNode)g.parentNode.removeChild(g);},380);
      nodeMap.delete(id);
    }
  }
}

function createNodeDOM(n){
  const active=state.selected===n.id;
  const g=el('g',{
    class:'node '+n.type+'-node'+(active?' selected':''),
    role:'button',tabindex:0,'aria-label':n.label,'data-node-id':n.id,'aria-pressed':active,
    style:'--node-color:'+n.color+';'
  });

  if(n.type!=='skill')g.setAttribute('aria-expanded',opened(n.id));
  const rect={x:-n.width/2,y:-n.height/2,width:n.width,height:n.height,rx:n.type==='skill'?8:10};

  el('rect',{...rect,class:'plate'},g);
  el('rect',{...rect,class:'crystal-tint'},g);
  el('rect',{x:-n.width/2+1,y:-n.height/2+1,width:n.width-2,height:Math.min(14,n.height/2),rx:5,class:'crystal-top-sheen'},g);

  const markerX=-n.width/2+16;
  if(n.type==='skill'){
    el('rect',{x:markerX-4,y:-4,width:8,height:8,rx:2,class:'gem-orb'},g);
  }else{
    el('circle',{cx:markerX,cy:0,r:4.5,class:'gem-orb'},g);
  }

  const labelX=-n.width/2+30;
  el('text',{x:labelX,y:5,class:'label'},g).textContent=n.label;
  el('title',{},g).textContent=n.label+(n.members?' · '+n.members.length+' 个技能':'');

  if(n.type!=='skill'&&n.members){
    const isExpanded=opened(n.id);
    const toggleX=n.dir>0?n.width/2:( -n.width/2);
    const toggleG=el('g',{class:'toggle-btn',transform:'translate('+toggleX+' 0)'},g);
    el('circle',{cx:0,cy:0,r:7.5,class:'toggle-bg'},toggleG);
    el('text',{x:0,y:3.5,class:'toggle-text'},toggleG).textContent=isExpanded?'−':'+';
    toggleG.onclick=e=>{
      e.stopPropagation();
      toggleCategory(n.id);
    };
  }

  const action=()=>n.type==='skill'?select(n.skill):chooseCategory(n.id);
  g.onclick=action;
  g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();action()}};
  return g;
}

// IN-PLACE chooseCategory: strictly NEVER jumps pan or scrolls screen!
function chooseCategory(id){
  let label='',members=[];
  for(const [p,ch] of groups(filtered())){
    if(id===pk(p)){label=p;members=[...ch.values()].flat()}
    for(const [c,m] of ch)if(id===ck(p,c)){label=c;members=m}
  }
  state.selected=id;
  if(!state.expanded.has(id)){
    toggleCategory(id);
  }
  $('detailBody').innerHTML=`<h2>${esc(label)}</h2><p class="muted-note">此分类包含 ${members.length} 个技能</p>`;
  for(const s of members){
    const b=document.createElement('button');
    b.className='detail-skill';
    b.textContent=s.name;
    b.onclick=()=>{
      state.expanded.add(pk(s.category));
      if(s.parent_category)state.expanded.add(ck(s.category,s.parent_category));
      select(s);
    };
    $('detailBody').appendChild(b);
  }
  $('details').classList.add('open');
  draw(false);
}

function select(s){
  state.selected=s.id;
  $('detailBody').innerHTML=`<h2>${esc(s.name)}</h2><h3>触发词</h3><div>${s.triggers&&s.triggers.length?s.triggers.map(t=>`<span class="tag">${esc(t)}</span>`).join(''):'<p class="muted-note">未能从技能说明提炼触发场景。</p>'}</div><h3>详细说明</h3><p>${esc(s.summary||'中文说明尚未生成，请重新构建。')}</p><h3>路径</h3><p class="path">${esc(s.path)}</p>`;
  $('details').classList.add('open');
  draw(false);
}

function expandAll(){
  for(const [p,ch] of groups(filtered())){
    state.expanded.add(pk(p));
    for(const [c] of ch)if(c)state.expanded.add(ck(p,c));
  }
  fit();
}

$('search').oninput=e=>{
  state.query=e.target.value.trim();
  if(state.query){
    const matched=filtered();
    for(const s of matched){
      state.expanded.add(pk(s.category));
      if(s.parent_category)state.expanded.add(ck(s.category,s.parent_category));
    }
  }
  draw(false);
};

$('status').onchange=e=>{
  state.status=e.target.value;
  draw(false);
};

$('expand').onclick=expandAll;
$('collapse').onclick=()=>{
  state.expanded.clear();
  fit();
};

$('reset').onclick=()=>{
  state={query:'',status:'all',expanded:new Set(),selected:null,zoom:1,pan:{x:0,y:0}};
  $('search').value='';
  $('status').value='all';
  $('details').classList.remove('open');
  fit();
};

$('close').onclick=()=>{
  $('details').classList.remove('open');
  draw(false);
};

$('fit').onclick=fit;

function zoom(factor,centerX=null,centerY=null){
  const svg=$('canvas'),w=svg.clientWidth||800,h=svg.clientHeight||600;
  const cx=centerX!==null?centerX:w/2;
  const cy=centerY!==null?centerY:h/2;
  const oldZoom=state.zoom;
  const newZoom=Math.max(0.4,Math.min(3.5,oldZoom*factor));
  if(Math.abs(newZoom-oldZoom)<0.001)return;
  const mouseX=cx-w/2;
  const mouseY=cy-h/2;
  state.pan.x=mouseX-(mouseX-state.pan.x)*(newZoom/oldZoom);
  state.pan.y=mouseY-(mouseY-state.pan.y)*(newZoom/oldZoom);
  state.zoom=newZoom;
  draw(false);
}

$('zoomIn').onclick=()=>zoom(1.2);
$('zoomOut').onclick=()=>zoom(0.83);

$('canvas').addEventListener('wheel',e=>{
  e.preventDefault();
  const rect=$('canvas').getBoundingClientRect();
  const factor=e.deltaY<0?1.12:0.89;
  zoom(factor,e.clientX-rect.left,e.clientY-rect.top);
},{passive:false});

$('canvas').onpointerdown=e=>{
  if(e.target.closest('.node'))return;
  drag={x:e.clientX,y:e.clientY,pan:{...state.pan}};
  $('canvas').setPointerCapture(e.pointerId);
  $('canvas').classList.add('dragging');
};

$('canvas').onpointermove=e=>{
  if(!drag)return;
  state.pan={x:drag.pan.x+e.clientX-drag.x,y:drag.pan.y+e.clientY-drag.y};
  draw(false);
};

function stopDrag(){
  drag=null;
  $('canvas').classList.remove('dragging');
}
$('canvas').onpointerup=stopDrag;
$('canvas').onpointercancel=stopDrag;
window.addEventListener('resize',()=>draw(false));

fit();
</script></body></html>'''
