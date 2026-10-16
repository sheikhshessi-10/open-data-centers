// Home page: the map and the card filters. Cards are already in the HTML; this only filters, sorts and draws the map.
(function(){
  const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const stageColor=s=>css("--s-"+s)||"#888";
  const STAGES=["announced","permitted","building","running","paused","blocked","cancelled","closed"];
  const grid=document.getElementById("grid");const cards=[...grid.querySelectorAll(".card")];
  const F={state:"all",stages:new Set(),q:"",sort:"invest"};
  let SITES=[],proj=null,dots=null,tags=null,CENT=new Map();
  // Sites without an exact pin sit at their county's center (shown as approximate on the site page).
  const pos=s=>s.lat?proj([s.lng,s.lat]):(CENT.get(s.county_fips)||null);
  const visibleIds=()=>new Set(cards.filter(c=>!c.hidden).map(c=>c.dataset.id));

  function apply(){
    const q=F.q.toLowerCase();let n=0;
    cards.forEach(c=>{
      const ok=(F.state==="all"||c.dataset.state===F.state)&&(!F.stages.size||F.stages.has(c.dataset.stage))&&(!q||c.dataset.q.includes(q));
      c.hidden=!ok;if(ok)n++;
    });
    cards.slice().sort((a,b)=>(+b.dataset[F.sort])-(+a.dataset[F.sort])).forEach(c=>grid.appendChild(c));
    document.getElementById("count").textContent=`${n} of ${cards.length} sites`;
    drawMarks();
  }

  const legend=document.getElementById("legend");
  STAGES.filter(st=>cards.some(c=>c.dataset.stage===st)).forEach(st=>{
    const n=cards.filter(c=>c.dataset.stage===st).length;
    const b=document.createElement("button");b.className="chip";b.setAttribute("aria-pressed","false");
    b.innerHTML=`<span class="sw" style="background:${stageColor(st)}"></span>${st[0].toUpperCase()+st.slice(1)} <span class="count">${n}</span>`;
    b.onclick=()=>{F.stages.has(st)?F.stages.delete(st):F.stages.add(st);b.setAttribute("aria-pressed",F.stages.has(st));apply()};
    legend.appendChild(b);
  });
  document.querySelectorAll("button[data-state]").forEach(b=>b.onclick=()=>{
    F.state=b.dataset.state;document.querySelectorAll("button[data-state]").forEach(x=>x.setAttribute("aria-pressed",x===b));apply();
  });
  const sel=document.getElementById("statesel");if(sel)sel.onchange=()=>{F.state=sel.value;apply()};
  document.getElementById("q").oninput=e=>{F.q=e.target.value;apply()};
  document.getElementById("sort").onchange=e=>{F.sort=e.target.value;apply()};

  const val=(s,k)=>{const m=s.metrics&&s.metrics[k];return m&&typeof m.value==="number"?m.value:0};
  function drawMarks(){
    if(!proj)return;const vis=visibleIds();
    const onMap=s=>!!pos(s);
    dots.selectAll("a").data(SITES.filter(onMap),d=>d.id).join("a").attr("href",d=>d.url).attr("aria-label",d=>d.name.split(" (")[0])
      .selectAll("circle").data(d=>[d]).join("circle").attr("class","dot")
      .attr("cx",d=>pos(d)[0]).attr("cy",d=>pos(d)[1])
      .attr("r",d=>(SITES.length>100?.55:1)*(4+Math.min(9,Math.sqrt(val(d,"power_mw")||val(d,"investment_usd")/2e7||1)/4)))
      .attr("fill",d=>stageColor(d.stage)).attr("opacity",d=>vis.has(d.id)?1:.15);
    tags.selectAll("*").remove();const placed=[];
    SITES.filter(s=>onMap(s)&&vis.has(s.id)&&(val(s,"investment_usd")>=3e9||val(s,"power_mw")>=300))
      .sort((a,b)=>val(b,"investment_usd")-val(a,"investment_usd")).slice(0,10).forEach(s=>{
        const [x,y]=pos(s);
        const nm=s.name.split(" (")[0].replace(/ (campus|data center|Data Center Campus|AI Data Center Campus|AI Factory Campus|Campus)$/i,"");
        const ow=(s.owner||"").split(/[ /(,]/)[0];
        let t=nm.toLowerCase().includes(ow.toLowerCase())?nm:ow+" · "+nm;if(t.length>22)t=t.slice(0,21)+"…";
        const w=t.length*6.6+14,h=20;let tx=x+10,ty=y-10-h;if(tx+w>955)tx=x-10-w;
        if(placed.some(p=>tx<p.x+p.w&&tx+w>p.x&&ty<p.y+p.h&&ty+h>p.y))return;placed.push({x:tx,y:ty,w,h});
        const g=tags.append("a").attr("href",s.url).attr("class","tag");
        g.append("rect").attr("x",tx).attr("y",ty).attr("width",w).attr("height",h).attr("rx",6).attr("fill",stageColor(s.stage));
        g.append("text").attr("x",tx+7).attr("y",ty+14).text(t);
      });
  }

  Promise.all([fetch("/assets/sites.json").then(r=>r.json()),fetch("/assets/geo.json").then(r=>r.json()),fetch("/assets/states.json").then(r=>r.json())]).then(([sites,GEO,STATES])=>{
    const FIPS=Object.fromEntries(STATES.map(s=>[s.code,s.fips]));const covered=new Set(Object.values(FIPS));
    SITES=sites;const svg=d3.select("#map");
    const counties=topojson.feature(GEO,GEO.objects.counties).features;
    const all=topojson.feature(GEO,GEO.objects.states).features;
    const lams={type:"FeatureCollection",features:all.filter(f=>covered.has(f.id))};
    proj=d3.geoAlbersUsa().fitExtent([[300,40],[930,600]],lams);const gp=d3.geoPath(proj);
    const key=s=>(s.county||"").replace(/ (Parish|County|Borough|Census Area|Municipality|City and Borough)$/,"").toLowerCase();
    counties.forEach(f=>{const c=gp.centroid(f);if(!isNaN(c[0]))CENT.set(f.id,c)});
    const host=new Map();
    sites.forEach(s=>{const c=s.county_fips?counties.find(f=>f.id===s.county_fips):counties.find(f=>f.id.startsWith(FIPS[s.state])&&f.properties.name.toLowerCase()===key(s));if(c&&!host.has(c.id))host.set(c.id,s.stage)});
    svg.append("g").selectAll("path").data(all.filter(f=>!covered.has(f.id))).join("path").attr("class","nb").attr("d",gp);
    svg.append("g").selectAll("path").data(counties).join("path").attr("d",gp).attr("class",d=>"county"+(host.has(d.id)?" host":""))
      .style("fill",d=>host.has(d.id)?stageColor(host.get(d.id)):null).style("fill-opacity",d=>host.has(d.id)?.4:null);
    svg.append("g").selectAll("path").data(lams.features).join("path").attr("class","state").attr("d",gp);
    dots=svg.append("g");tags=svg.append("g");drawMarks();
  }).catch(()=>{});
})();
