import csv, json, math, os
from string import Template

BASE = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE, "jura_validation_set.csv")

ROCK = {1:"Argovian",2:"Kimmeridgian",3:"Sequanian",4:"Portlandian",5:"Quaternary"}
LAND = {1:"Forest",2:"Pasture",3:"Meadow",4:"Tillage"}
METALS = ["Cd","Cu","Pb","Co","Cr","Ni","Zn"]
COLORS = ["#f72585","#7209b7","#3a0ca3","#4361ee","#4cc9f0","#06d6a0","#ffd166"]

rows = []
with open(csv_path, newline="") as f:
    reader = csv.reader(f)
    next(reader)
    for line in reader:
        if len(line) < 12 or line[0].strip() == "":
            continue
        try:
            def clean(val):
                return float(val.replace(',', '.').replace('/.', '.').replace('..', '.'))
            
            rows.append({
                "id": int(clean(line[0])), "x": clean(line[1]), "y": clean(line[2]),
                "rock": int(clean(line[3])), "land": int(clean(line[4])),
                "Cd": clean(line[5]), "Cu": clean(line[6]), "Pb": clean(line[7]),
                "Co": clean(line[8]), "Cr": clean(line[9]),
                "Ni": clean(line[10]), "Zn": clean(line[11]),
            })
        except Exception as e:
            pass

n = len(rows)

def stats(vals):
    s = sorted(vals)
    mean = sum(s)/len(s)
    std = math.sqrt(sum((v-mean)**2 for v in s)/len(s))
    return {"min":round(s[0],3),"max":round(s[-1],3),"mean":round(mean,3),
            "std":round(std,3),"median":round(s[len(s)//2],3),
            "q1":round(s[len(s)//4],3),"q3":round(s[3*len(s)//4],3)}

def corr(a, b):
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    num = sum((a[i]-ma)*(b[i]-mb) for i in range(len(a)))
    da = math.sqrt(sum((v-ma)**2 for v in a))
    db = math.sqrt(sum((v-mb)**2 for v in b))
    return round(num/(da*db), 3) if da*db else 0

def histogram(vals, bins=15):
    mn, mx = min(vals), max(vals)
    w = (mx-mn)/bins
    edges = [mn + i*w for i in range(bins+1)]
    counts = [0]*bins
    for v in vals:
        b = min(int((v-mn)/w), bins-1)
        counts[b] += 1
    return [f"{edges[i]:.2f}" for i in range(bins)], counts

metal_stats = {m: stats([r[m] for r in rows]) for m in METALS}
corr_matrix = [[corr([r[m1] for r in rows],[r[m2] for r in rows]) for m2 in METALS] for m1 in METALS]
rock_counts = {v: sum(1 for r in rows if r["rock"]==k) for k,v in ROCK.items()}
land_counts = {v: sum(1 for r in rows if r["land"]==k) for k,v in LAND.items()}
hist_data = {m: {"labels": histogram([r[m] for r in rows])[0], "counts": histogram([r[m] for r in rows])[1]} for m in METALS}

# Use Template substitution — no brace escaping for JS needed
TMPL = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Jura EDA Dashboard — Validation Set (n=100)</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#0f0f1a;color:#e0e0ff;min-height:100vh}
header{background:linear-gradient(135deg,#1a1a3e 0%,#0d0d2b 100%);padding:28px 40px;border-bottom:1px solid #2a2a5a;display:flex;align-items:center;gap:20px}
.logo{font-size:2rem}
.header-text h1{font-size:1.6rem;font-weight:700;background:linear-gradient(90deg,#4cc9f0,#7209b7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header-text p{font-size:.85rem;color:#8888bb;margin-top:4px}
.badge{background:rgba(76,201,240,.15);border:1px solid #4cc9f0;color:#4cc9f0;border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600;margin-left:auto}
.nav-btn{background:rgba(76,201,240,.1);border:1px solid #4cc9f0;color:#4cc9f0;border-radius:8px;padding:6px 14px;font-size:.85rem;font-weight:600;text-decoration:none;transition:all 0.2s}
.nav-btn:hover{background:rgba(76,201,240,.25)}
main{padding:32px 40px;max-width:1600px;margin:0 auto}
.section-title{font-size:1.1rem;font-weight:700;color:#a0a0ff;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.section-title::before{content:'';display:inline-block;width:4px;height:18px;background:linear-gradient(180deg,#4cc9f0,#7209b7);border-radius:2px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px;margin-bottom:36px}
.kpi-card{background:linear-gradient(135deg,#1a1a3e,#12122a);border:1px solid #2a2a5a;border-radius:14px;padding:20px;transition:transform .2s,border-color .2s;cursor:default}
.kpi-card:hover{transform:translateY(-3px);border-color:#4cc9f0}
.kpi-metal{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.kpi-mean{font-size:2rem;font-weight:700;line-height:1}
.kpi-unit{font-size:.75rem;color:#6666aa;margin-top:2px}
.kpi-row{display:flex;gap:16px;font-size:.78rem;margin-top:10px;color:#8888bb}
.kpi-row span b{color:#c0c0ff}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:36px}
.card{background:#13132b;border:1px solid #2a2a5a;border-radius:14px;padding:24px}
.card-title{font-size:.85rem;font-weight:600;color:#8888cc;margin-bottom:16px;text-transform:uppercase;letter-spacing:.5px}
canvas{max-height:260px}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;align-items:center;font-size:.8rem;color:#8888bb}
select{background:#1a1a3e;border:1px solid #3a3a6a;color:#e0e0ff;padding:6px 12px;border-radius:8px;font-family:inherit;font-size:.82rem;cursor:pointer}
#corrCanvas{max-height:380px!important;height:380px;max-width:100%}
.stat-table{width:100%;border-collapse:collapse;font-size:.82rem}
.stat-table th{background:#1a1a3e;color:#8888bb;padding:8px 12px;text-align:left;font-weight:600;border-bottom:1px solid #2a2a5a}
.stat-table td{padding:8px 12px;border-bottom:1px solid #1e1e40}
.stat-table tr:hover td{background:rgba(76,201,240,.05)}
.hist-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;margin-bottom:36px}
footer{text-align:center;padding:24px;color:#444466;font-size:.78rem;border-top:1px solid #1a1a3a}
</style>
</head>
<body>
<header>
  <div class="logo">&#127758;</div>
  <div class="header-text">
    <h1>Jura Heavy Metals &mdash; Exploratory Data Analysis</h1>
    <p>Validation Set &middot; Swiss Jura Region &middot; Spatial Geochemical Survey</p>
  </div>
  <div class="nav-group" style="display:flex;gap:12px;margin-left:auto;align-items:center">
    <div class="badge">n = $n_samples samples</div>
    <a href="validation_maps.html" class="nav-btn">Spatial Maps &rarr;</a>
    <a href="../Prediction set/index.html" class="nav-btn">&larr; Prediction Set</a>
  </div>
</header>
<main>
<div class="section-title">Summary Statistics</div>
<div class="kpi-grid" id="kpiGrid"></div>
<div class="card" style="margin-bottom:36px">
  <div class="card-title">Descriptive Statistics &mdash; All Metals (ppm)</div>
  <table class="stat-table">
    <thead><tr><th>Metal</th><th>Min</th><th>Q1</th><th>Median</th><th>Mean</th><th>Q3</th><th>Max</th><th>Std Dev</th></tr></thead>
    <tbody id="statTbody"></tbody>
  </table>
</div>
<div class="section-title">Frequency Distributions</div>
<div class="hist-grid" id="histGrid"></div>
<div class="section-title">Correlation Analysis</div>
<div class="grid-2">
  <div class="card">
    <div class="card-title">Pearson Correlation Heatmap</div>
    <canvas id="corrCanvas"></canvas>
  </div>
  <div class="card">
    <div class="card-title">Metal Pair Scatter Plot</div>
    <div class="controls">X: <select id="scatX"></select> &nbsp; Y: <select id="scatY"></select></div>
    <canvas id="scatCanvas"></canvas>
  </div>
</div>

<div class="section-title">By Rock Type &amp; Land Use</div>
<div class="grid-2">
  <div class="card"><div class="card-title">Count by Rock Type</div><canvas id="rockCount"></canvas></div>
  <div class="card"><div class="card-title">Count by Land Use</div><canvas id="landCount"></canvas></div>
</div>
<div class="grid-2" style="margin-top:24px">
  <div class="card">
    <div class="card-title">Mean by Rock Type</div>
    <div class="controls">Metal: <select id="rockMetal"></select></div>
    <canvas id="rockMetalChart"></canvas>
  </div>
  <div class="card">
    <div class="card-title">Mean by Land Use</div>
    <div class="controls">Metal: <select id="landMetal"></select></div>
    <canvas id="landMetalChart"></canvas>
  </div>
</div>
</main>
<footer>Jura EDA Dashboard &middot; Swiss Jura Heavy Metals Dataset &middot; Validation Set (n=100)</footer>
<script>
var ROWS = $rows_js;
var STATS = $stats_js;
var CORR = $corr_js;
var ROCK_C = $rock_c_js;
var LAND_C = $land_c_js;
var COLORS = $colors_js;
var METALS = $metals_js;
var HIST = $hist_js;
var ROCK_LABELS = $rock_labels_js;
var LAND_LABELS = $land_labels_js;

function alpha(hex,a){return hex+Math.round(a*255).toString(16).padStart(2,'0');}
function lerp(a,b,t){return a+(b-a)*t;}
function metalColor(val,mn,mx){
  var t=Math.max(0,Math.min(1,(val-mn)/(mx-mn)));
  var r=Math.round(lerp(14,247,t)),g=Math.round(lerp(165,37,t)),b=Math.round(lerp(233,133,t));
  return 'rgba('+r+','+g+','+b+',0.85)';
}

// KPI Cards
var kpiGrid=document.getElementById('kpiGrid');
METALS.forEach(function(m,i){
  var s=STATS[m];
  var card=document.createElement('div');
  card.className='kpi-card';
  card.innerHTML='<div class="kpi-metal" style="color:'+COLORS[i]+'">'+m+'</div>'
    +'<div class="kpi-mean" style="color:'+COLORS[i]+'">'+s.mean+'</div>'
    +'<div class="kpi-unit">mean (ppm)</div>'
    +'<div class="kpi-row"><span>Min <b>'+s.min+'</b></span> <span>Max <b>'+s.max+'</b></span> <span>Std <b>'+s.std+'</b></span></div>';
  kpiGrid.appendChild(card);
});

// Stat table
var tbody=document.getElementById('statTbody');
METALS.forEach(function(m,i){
  var s=STATS[m];
  var tr=document.createElement('tr');
  tr.innerHTML='<td style="color:'+COLORS[i]+';font-weight:600">'+m+'</td>'
    +'<td>'+s.min+'</td><td>'+s.q1+'</td><td>'+s.median+'</td><td>'+s.mean+'</td>'
    +'<td>'+s.q3+'</td><td>'+s.max+'</td><td>'+s.std+'</td>';
  tbody.appendChild(tr);
});

// Histograms
var histGrid=document.getElementById('histGrid');
METALS.forEach(function(m,i){
  var div=document.createElement('div');
  div.className='card';
  var cid='hist_'+m;
  div.innerHTML='<div class="card-title">'+m+' (ppm)</div><canvas id="'+cid+'"></canvas>';
  histGrid.appendChild(div);
  new Chart(document.getElementById(cid),{
    type:'bar',
    data:{labels:HIST[m].labels,datasets:[{label:m,data:HIST[m].counts,
      backgroundColor:alpha(COLORS[i],.7),borderColor:COLORS[i],borderWidth:1,borderRadius:4}]},
    options:{plugins:{legend:{display:false}},scales:{
      x:{ticks:{color:'#6666aa',maxRotation:45,font:{size:9}},grid:{color:'#1e1e40'}},
      y:{ticks:{color:'#6666aa'},grid:{color:'#1e1e40'}}}}
  });
});

// Correlation Heatmap (bubble chart)
var corrDatasets=[];
METALS.forEach(function(m1,i){
  METALS.forEach(function(m2,j){
    var v=CORR[i][j];
    corrDatasets.push({
      data:[{x:j,y:i,r:Math.abs(v)*18+4}],
      backgroundColor:'rgba('+(v>0?'76,201,240':'247,37,133')+','+Math.abs(v).toFixed(2)+')',
      label:m1+'-'+m2+': '+v
    });
  });
});
new Chart(document.getElementById('corrCanvas'),{
  type:'bubble',
  data:{datasets:corrDatasets},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return c.dataset.label;}}}},
    scales:{
      x:{min:-0.5,max:6.5,ticks:{callback:function(v){return METALS[v]||'';},color:'#8888bb'},grid:{color:'#1e1e40'}},
      y:{min:-0.5,max:6.5,ticks:{callback:function(v){return METALS[v]||'';},color:'#8888bb'},grid:{color:'#1e1e40'}}
    }}
});

// Scatter plot
var scatX=document.getElementById('scatX');
var scatY=document.getElementById('scatY');
METALS.forEach(function(m,i){
  var o1=new Option(m,m); if(i===0)o1.selected=true; scatX.appendChild(o1);
  var o2=new Option(m,m); if(i===1)o2.selected=true; scatY.appendChild(o2);
});
var scatChart=null;
function buildScat(){
  var mx=scatX.value, my=scatY.value, ix=METALS.indexOf(mx);
  var pts=ROWS.map(function(r){return {x:r[mx],y:r[my]};});
  if(scatChart) scatChart.destroy();
  scatChart=new Chart(document.getElementById('scatCanvas'),{
    type:'scatter',
    data:{datasets:[{label:mx+' vs '+my,data:pts,backgroundColor:alpha(COLORS[ix],.6),pointRadius:4}]},
    options:{plugins:{legend:{display:false}},scales:{
      x:{title:{display:true,text:mx+' (ppm)',color:'#8888bb'},ticks:{color:'#6666aa'},grid:{color:'#1e1e40'}},
      y:{title:{display:true,text:my+' (ppm)',color:'#8888bb'},ticks:{color:'#6666aa'},grid:{color:'#1e1e40'}}}}
  });
}
scatX.addEventListener('change',buildScat);
scatY.addEventListener('change',buildScat);
buildScat();



// Doughnuts
var dOpts={cutout:'60%',plugins:{legend:{position:'right',labels:{color:'#a0a0cc',font:{size:11},boxWidth:12}}}};
new Chart(document.getElementById('rockCount'),{type:'doughnut',
  data:{labels:Object.keys(ROCK_C),datasets:[{data:Object.values(ROCK_C),backgroundColor:COLORS,borderWidth:0}]},
  options:dOpts});
new Chart(document.getElementById('landCount'),{type:'doughnut',
  data:{labels:Object.keys(LAND_C),datasets:[{data:Object.values(LAND_C),backgroundColor:['#06d6a0','#ffd166','#f72585','#4cc9f0'],borderWidth:0}]},
  options:dOpts});

// Mean by category charts
function buildRockMetal(){
  var m=document.getElementById('rockMetal').value, idx=METALS.indexOf(m);
  var means=ROCK_LABELS.map(function(rk){
    var vals=ROWS.filter(function(r){return ['Argovian','Kimmeridgian','Sequanian','Portlandian','Quaternary'][r.rock-1]===rk;}).map(function(r){return r[m];});
    return vals.length?(vals.reduce(function(a,b){return a+b;},0)/vals.length).toFixed(3):0;
  });
  if(window._rmc) window._rmc.destroy();
  window._rmc=new Chart(document.getElementById('rockMetalChart'),{
    type:'bar',
    data:{labels:ROCK_LABELS,datasets:[{label:m+' mean',data:means,backgroundColor:alpha(COLORS[idx],.7),borderColor:COLORS[idx],borderWidth:1,borderRadius:6}]},
    options:{plugins:{legend:{display:false}},scales:{
      x:{ticks:{color:'#8888bb',maxRotation:30},grid:{color:'#1e1e40'}},
      y:{ticks:{color:'#6666aa'},grid:{color:'#1e1e40'}}}}
  });
}
function buildLandMetal(){
  var m=document.getElementById('landMetal').value, idx=METALS.indexOf(m);
  var means=LAND_LABELS.map(function(lk){
    var vals=ROWS.filter(function(r){return ['Forest','Pasture','Meadow','Tillage'][r.land-1]===lk;}).map(function(r){return r[m];});
    return vals.length?(vals.reduce(function(a,b){return a+b;},0)/vals.length).toFixed(3):0;
  });
  if(window._lmc) window._lmc.destroy();
  window._lmc=new Chart(document.getElementById('landMetalChart'),{
    type:'bar',
    data:{labels:LAND_LABELS,datasets:[{label:m+' mean',data:means,
      backgroundColor:['rgba(6,214,160,.7)','rgba(255,209,102,.7)','rgba(247,37,133,.7)','rgba(76,201,240,.7)'],
      borderColor:['#06d6a0','#ffd166','#f72585','#4cc9f0'],borderWidth:1,borderRadius:6}]},
    options:{plugins:{legend:{display:false}},scales:{
      x:{ticks:{color:'#8888bb'},grid:{color:'#1e1e40'}},
      y:{ticks:{color:'#6666aa'},grid:{color:'#1e1e40'}}}}
  });
}
var rmSel=document.getElementById('rockMetal'), lmSel=document.getElementById('landMetal');
METALS.forEach(function(m){
  rmSel.appendChild(new Option(m,m));
  lmSel.appendChild(new Option(m,m));
});
rmSel.addEventListener('change',buildRockMetal);
lmSel.addEventListener('change',buildLandMetal);
buildRockMetal();
buildLandMetal();
</script>
</body>
</html>
""")

out = os.path.join(BASE, "index2.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(TMPL.substitute(
        n_samples=n,
        rows_js=json.dumps(rows),
        stats_js=json.dumps(metal_stats),
        corr_js=json.dumps(corr_matrix),
        rock_c_js=json.dumps(rock_counts),
        land_c_js=json.dumps(land_counts),
        colors_js=json.dumps(COLORS),
        metals_js=json.dumps(METALS),
        hist_js=json.dumps(hist_data),
        rock_labels_js=json.dumps(list(ROCK.values())),
        land_labels_js=json.dumps(list(LAND.values())),
    ))
print("Validation Dashboard written.")
print(f"Rows: {n}")
