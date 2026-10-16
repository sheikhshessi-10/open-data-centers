// Home page: the map and the card filters. The HTML holds only the top cards; the rest come from /assets/cards.json
// (built by card_data() in build.py) and are rendered here with the same markup as card() in build.py.
(function(){
  const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const stageColor=s=>css("--s-"+s)||"#888";
  const STAGES=["announced","permitted","building","running","paused","blocked","cancelled","closed"];
  const BARS=["Data found","Company openness","Local pushback","News coverage","Size"];
  const KEY={invest:"inv",power:"mw",push:"push",data:"data",news:"news"};
  const PAGE=48;
  const grid=document.getElementById("grid"),more=document.getElementById("more"),count=document.getElementById("count");
  const sel=document.getElementById("statesel"),qIn=document.getElementById("q"),sortSel=document.getElementById("sort");
  const nodes=new Map([...grid.querySelectorAll(".card")].map(c=>[c.dataset.id,c]));
  const F={state:sel?sel.value:"all",stages:new Set(),q:qIn.value,sort:sortSel.value};
  let SITES=null,limit=PAGE,matched=[],proj=null,dots=null,tags=null,CENT=new Map();
  // Sites without an exact pin sit at their county's center (shown as approximate on the site page).
  const pos=s=>s.lat?proj([s.lng,s.lat]):(CENT.get(s.cfips)||null);
  const ok=s=>(F.state==="all"||s.st===F.state)&&(!F.stages.size||F.stages.has(s.stage))&&(!F.q||s.q.includes(F.q.toLowerCase()));

  const esc=v=>String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#x27;");
  function cardEl(d){
    const t=document.createElement("template");
    t.innerHTML=`<a class="card" href="${esc(d.url)}" data-id="${esc(d.id)}" data-state="${d.st}" data-stage="${esc(d.stage)}" data-q="${esc(d.q)}" data-invest="${d.inv}" `+
      `data-power="${d.mw}" data-push="${d.push}" data-data="${d.data}" data-news="${d.news}">`+
      `<svg class="bgsvg" viewBox="0 0 400 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true" data-state="${esc(d.st)}" data-fips="${d.fips}" `+
      `data-county="${esc(d.county)}" data-cfips="${d.cfips}" data-lat="${d.lat}" data-lng="${d.lng}" data-stage="${esc(d.stage)}">`+
      `<rect width="400" height="340" class="stagefill-${esc(d.stage)}"/></svg><div class="shade"></div>`+
      `<span class="rank">${d.r}</span><span class="stage">${esc(d.stage)}</span>`+
      `<div class="mid"><div class="name">${esc(d.n)}</div><div class="where">${esc(d.where)}</div></div>`+
      `<div class="foot"><span>${esc(d.m)}</span><span>${esc(d.p)}</span></div>`+
      `<div class="bars">${d.b.map(([w,c,x],i)=>`<div class="brow"><span>${BARS[i]}</span><div class="btrack"><div class="bfill" style="width:${w}%;background:var(--${c})">${esc(x)}</div></div></div>`).join("")}</div></a>`;
    return t.content.firstElementChild;
  }
  const node=d=>{let n=nodes.get(d.id);if(!n){n=cardEl(d);nodes.set(d.id,n)}n.hidden=false;return n};

  function apply(){
    if(!SITES){ // data not here yet: filter the cards already on the page
      const q=F.q.toLowerCase();
      nodes.forEach(c=>{c.hidden=!((F.state==="all"||c.dataset.state===F.state)&&(!F.stages.size||F.stages.has(c.dataset.stage))&&(!q||c.dataset.q.includes(q)))});
      return;
    }
    const k=KEY[F.sort];
    matched=SITES.filter(ok).sort((a,b)=>b[k]-a[k]||a.r-b.r);
    grid.replaceChildren(...matched.slice(0,limit).map(node));
    if(window.odcEnhance)window.odcEnhance(grid);
    more.hidden=matched.length<=limit;
    count.textContent=`${matched.length} of ${SITES.length} sites`;
    drawMarks();
  }
  const refilter=()=>{limit=PAGE;apply()};

  document.querySelectorAll("button[data-state]").forEach(b=>b.onclick=()=>{
    F.state=b.dataset.state;document.querySelectorAll("button[data-state]").forEach(x=>x.setAttribute("aria-pressed",x===b));refilter();
  });
  if(sel)sel.onchange=()=>{F.state=sel.value;refilter()};
  qIn.oninput=e=>{F.q=e.target.value;refilter()};
  sortSel.onchange=e=>{F.sort=e.target.value;refilter()};
  more.onclick=e=>{e.preventDefault();limit+=PAGE;apply()};

  function legend(){
    const box=document.getElementById("legend");
    STAGES.filter(st=>SITES.some(s=>s.stage===st)).forEach(st=>{
      const n=SITES.filter(s=>s.stage===st).length;
      const b=document.createElement("button");b.className="chip";b.setAttribute("aria-pressed","false");
      b.innerHTML=`<span class="sw" style="background:${stageColor(st)}"></span>${st[0].toUpperCase()+st.slice(1)} <span class="count">${n}</span>`;
      b.onclick=()=>{F.stages.has(st)?F.stages.delete(st):F.stages.add(st);b.setAttribute("aria-pressed",F.stages.has(st));refilter()};
      box.appendChild(b);
    });
  }

  function drawMarks(){
    if(!proj||!SITES)return;const vis=new Set(matched.map(s=>s.id));
    const onMap=s=>!!pos(s);
    dots.selectAll("a").data(SITES.filter(onMap),d=>d.id).join("a").attr("href",d=>d.url).attr("aria-label",d=>d.mn)
      .selectAll("circle").data(d=>[d]).join("circle").attr("class","dot")
      .attr("cx",d=>pos(d)[0]).attr("cy",d=>pos(d)[1])
      .attr("r",d=>(SITES.length>100?.55:1)*(4+Math.min(9,Math.sqrt(d.mw||d.inv/2e7||1)/4)))
      .attr("fill",d=>stageColor(d.stage)).attr("opacity",d=>vis.has(d.id)?1:.15);
    tags.selectAll("*").remove();const placed=[];
    SITES.filter(s=>onMap(s)&&vis.has(s.id)&&(s.inv>=3e9||s.mw>=300))
      .sort((a,b)=>b.inv-a.inv).slice(0,10).forEach(s=>{
        const [x,y]=pos(s);
        const nm=s.mn.replace(/ (campus|data center|Data Center Campus|AI Data Center Campus|AI Factory Campus|Campus)$/i,"");
        const ow=(s.owner||"").split(/[ /(,]/)[0];
        let t=nm.toLowerCase().includes(ow.toLowerCase())?nm:ow+" · "+nm;if(t.length>22)t=t.slice(0,21)+"…";
        const w=t.length*6.6+14,h=20;let tx=x+10,ty=y-10-h;if(tx+w>955)tx=x-10-w;
        if(placed.some(p=>tx<p.x+p.w&&tx+w>p.x&&ty<p.y+p.h&&ty+h>p.y))return;placed.push({x:tx,y:ty,w,h});
        const g=tags.append("a").attr("href",s.url).attr("class","tag");
        g.append("rect").attr("x",tx).attr("y",ty).attr("width",w).attr("height",h).attr("rx",6).attr("fill",stageColor(s.stage));
        g.append("text").attr("x",tx+7).attr("y",ty+14).text(t);
      });
  }

  // Rebuild what card_data() in build.py holds from the slim rows.
  const COLOR={g:"good",o:"ok",b:"bad",m:"muted",i:"info"};
  function unpack(J){
    return J.rows.map(row=>{
      const d=Object.fromEntries(J.cols.map((c,j)=>[c,row[j]]));
      const [fips,stName]=J.states[d.st];const short=d.name.split(" (")[0];
      Object.assign(d,{fips,n:d.ss?d.name:short,mn:short,
        q:[d.name,d.owner,d.county,d.town].join(" ").toLowerCase(),
        where:`${d.county||(d.town||"Unknown area").split(" (")[0]}, ${stName}`,
        b:[`${d.data} of ${J.metrics}`,d.op?`${d.op} of 8 so far`:"Not asked yet",d.push?`${d.push} actions`:"None found",`${d.news} stories`,d.inv?d.m:"Unknown"]
          .map((t,k)=>[d.w[k],COLOR[d.c[k]],t])});
      return d;
    });
  }
  let FIPS={};
  const cardsP=fetch("/assets/cards.json").then(r=>r.json()).then(J=>{
    FIPS=Object.fromEntries(Object.entries(J.states).map(([c,v])=>[c,v[0]]));SITES=unpack(J);legend();apply();return SITES});
  cardsP.catch(()=>{});
  if(!window.odcGeo||!window.d3)return;
  Promise.all([cardsP,window.odcGeo()]).then(([sites,GEO])=>{
    const covered=new Set(Object.values(FIPS));
    const svg=d3.select("#map");
    const counties=topojson.feature(GEO,GEO.objects.counties).features;
    const all=topojson.feature(GEO,GEO.objects.states).features;
    const lams={type:"FeatureCollection",features:all.filter(f=>covered.has(f.id))};
    proj=d3.geoAlbersUsa().fitExtent([[300,40],[930,600]],lams);const gp=d3.geoPath(proj);
    const key=s=>(s.county||"").replace(/ (Parish|County|Borough|Census Area|Municipality|City and Borough)$/,"").toLowerCase();
    counties.forEach(f=>{const c=gp.centroid(f);if(!isNaN(c[0]))CENT.set(f.id,c)});
    const byId=new Map(counties.map(f=>[f.id,f]));
    const host=new Map();
    sites.forEach(s=>{const c=s.cfips?byId.get(s.cfips):counties.find(f=>f.id.startsWith(FIPS[s.st])&&f.properties.name.toLowerCase()===key(s));if(c&&!host.has(c.id))host.set(c.id,s.stage)});
    svg.append("g").selectAll("path").data(all.filter(f=>!covered.has(f.id))).join("path").attr("class","nb").attr("d",gp);
    svg.append("g").selectAll("path").data(counties).join("path").attr("d",gp).attr("class",d=>"county"+(host.has(d.id)?" host":""))
      .style("fill",d=>host.has(d.id)?stageColor(host.get(d.id)):null).style("fill-opacity",d=>host.has(d.id)?.4:null);
    svg.append("g").selectAll("path").data(lams.features).join("path").attr("class","state").attr("d",gp);
    dots=svg.append("g");tags=svg.append("g");drawMarks();
  }).catch(()=>{});
})();
