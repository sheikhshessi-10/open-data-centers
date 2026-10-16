// Home page: the map and the card filters. The HTML holds only the top cards; the rest come from /assets/cards.json
// (built by card_data() in build.py) and are rendered here with the same markup as card() in build.py.
(function(){
  const CSS=new Map(),css=n=>{if(!CSS.has(n))CSS.set(n,getComputedStyle(document.documentElement).getPropertyValue(n).trim());return CSS.get(n)};
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
    more.parentNode.hidden=matched.length<=limit;
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

  // Dots live inside the zoomed group (map coordinates); labels sit on top in screen space so they keep their size.
  // u scales labels up on narrow screens, where one map unit is under half a pixel.
  const W=960,H=620,KMAX=12,LINES=2;
  let k=1,T=null,u=1,svgNode=null;
  const rad=d=>(SITES.length>100?.55:1)*(4+Math.min(9,Math.sqrt(d.mw||d.inv/2e7||1)/4));
  // Same on-screen size at every zoom. On phones dots grow toward their desktop size as you zoom in, so they can be tapped.
  const dotR=d=>rad(d)/k*(1+(u-1)*Math.min(1,(k-1)/3));
  function drawMarks(){
    if(!proj||!SITES)return;const vis=new Set(matched.map(s=>s.id));
    const onMap=s=>!!pos(s);
    dots.selectAll("a").data(SITES.filter(onMap),d=>d.id).join("a").attr("href",d=>d.url).attr("aria-label",d=>d.mn)
      .selectAll("circle").data(d=>[d]).join("circle").attr("class","dot")
      .attr("cx",d=>pos(d)[0]).attr("cy",d=>pos(d)[1]).attr("r",dotR)
      .attr("fill",d=>stageColor(d.stage)).attr("opacity",d=>vis.has(d.id)?1:.15);
    drawTags(vis);
  }
  function drawTags(vis){
    vis=vis||new Set(matched.map(s=>s.id));
    tags.selectAll("*").remove();const placed=[];
    const fs=12*u,h=20*u;
    SITES.filter(s=>pos(s)&&vis.has(s.id)&&(s.inv>=3e9||s.mw>=300))
      .sort((a,b)=>b.inv-a.inv).filter(s=>{const [x,y]=T.apply(pos(s));return x>=0&&x<=W&&y>=0&&y<=H}).slice(0,k>1?14:10).forEach(s=>{
        const [x,y]=T.apply(pos(s));
        const nm=s.mn.replace(/ (campus|data center|Data Center Campus|AI Data Center Campus|AI Factory Campus|Campus)$/i,"");
        const ow=(s.owner||"").split(/[ /(,]/)[0];
        let t=nm.toLowerCase().includes(ow.toLowerCase())?nm:ow+" · "+nm;if(t.length>22)t=t.slice(0,21)+"…";
        const w=(t.length*6.6+14)*u;let tx=x+10*u,ty=y-10*u-h;if(tx+w>W-5)tx=x-10*u-w;if(ty<2)ty=y+10*u;
        if(tx<2||placed.some(p=>tx<p.x+p.w&&tx+w>p.x&&ty<p.y+p.h&&ty+h>p.y))return;placed.push({x:tx,y:ty,w,h});
        const g=tags.append("a").attr("href",s.url).attr("class","tag");
        g.append("rect").attr("x",tx).attr("y",ty).attr("width",w).attr("height",h).attr("fill",stageColor(s.stage));
        g.append("text").attr("x",tx+7*u).attr("y",ty+14*u).style("font-size",fs+"px").attr("fill",css("--on-"+s.stage)||"#fff").text(t);
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
  if(!window.odcMap||!window.d3)return;
  // First draw uses /assets/map.json: states plus the counties that hold a site, about a quarter of the full file.
  // All county lines come from /assets/geo.json, fetched only when the map is zoomed in.
  Promise.all([cardsP,window.odcMap()]).then(([sites,M])=>{
    const covered=new Set(Object.values(FIPS));
    const svg=d3.select("#map");svgNode=svg.node();
    // Fit the projection to the covered states' points, then project every arc point once. The shapes then draw as plain
    // screen-space paths: no spherical clipping or resampling, which was most of the draw time on phones.
    const ll=topojson.feature(M,M.objects.states).features.filter(f=>covered.has(f.id));
    const pts=ll.flatMap(f=>(f.geometry.type==="Polygon"?[f.geometry.coordinates]:f.geometry.coordinates).flat(1)).flat(1);
    proj=d3.geoAlbersUsa().fitExtent(matchMedia("(max-width: 1359px)").matches?[[8,8],[952,612]]:[[300,40],[930,600]],{type:"MultiPoint",coordinates:pts});
    const gp=d3.geoPath();
    const flat=G=>{const [sx,sy]=G.transform.scale,[tx,ty]=G.transform.translate;
      return {...G,transform:null,arcs:G.arcs.map(a=>{let x=0,y=0,o=[];for(const [dx,dy] of a){x+=dx;y+=dy;const q=proj([x*sx+tx,y*sy+ty]);if(q)o.push(q)}return o})}};
    const P=flat(M);
    const hostF=topojson.feature(P,P.objects.counties).features;
    const all=topojson.feature(P,P.objects.states).features;
    const lams={type:"FeatureCollection",features:all.filter(f=>covered.has(f.id))};
    const key=s=>(s.county||"").replace(/ (Parish|County|Borough|Census Area|Municipality|City and Borough)$/,"").toLowerCase();
    hostF.forEach(f=>{const c=gp.centroid(f);if(!isNaN(c[0]))CENT.set(f.id,c)});
    const byId=new Map(hostF.map(f=>[f.id,f]));
    const host=new Map();
    sites.forEach(s=>{const c=s.cfips?byId.get(s.cfips):hostF.find(f=>f.id.startsWith(FIPS[s.st])&&f.properties.name.toLowerCase()===key(s));if(c&&!host.has(c.id))host.set(c.id,s.stage)});
    // One path per layer (and one per stage for the host fills) instead of one per county.
    const root=svg.append("g");
    root.append("g").selectAll("path").data(all.filter(f=>!covered.has(f.id))).join("path").attr("class","nb").attr("d",gp);
    root.append("path").attr("class","land").attr("d",gp(lams));
    root.append("g").selectAll("path").data(d3.groups([...host],([,st])=>st)).join("path").attr("class","host")
      .attr("fill",([st])=>stageColor(st)).attr("d",([,ids])=>gp({type:"FeatureCollection",features:ids.map(([id])=>byId.get(id))}));
    const lines=root.append("path").attr("class","cmesh").attr("display","none");
    root.append("path").attr("class","state").attr("d",gp(topojson.mesh(P,P.objects.states,(a,b)=>covered.has(a.id)||covered.has(b.id))));
    dots=root.append("g");tags=svg.append("g");
    T=d3.zoomIdentity;u=Math.max(1,900/(svgNode.clientWidth||960));
    drawMarks();
    dispatchEvent(new Event("odc:map"));

    let linesP=null,raf=0;
    const showLines=()=>{
      if(!linesP)linesP=window.odcGeo().then(flat).then(G=>lines.attr("d",gp(topojson.mesh(G,G.objects.counties,(a,b)=>a!==b)))).catch(()=>{linesP=null});
      lines.attr("display",k>=LINES?null:"none");
    };
    const bar=document.querySelector(".zoombar"),btn=n=>bar.querySelector(`[data-zoom="${n}"]`);
    const zoom=d3.zoom().scaleExtent([1,KMAX]).extent([[0,0],[W,H]]).translateExtent([[0,0],[W,H]])
      // Wheel and mouse drag zoom and pan. At either zoom limit the wheel scrolls the page instead.
      .filter(e=>e.type==="wheel"?(e.ctrlKey||!((k<=1&&e.deltaY>0)||(k>=KMAX&&e.deltaY<0))):!e.ctrlKey&&!e.button)
      .touchable(()=>false)
      .on("zoom",e=>{
        T=e.transform;root.attr("transform",T);
        if(T.k!==k){k=T.k;dots.selectAll("circle").attr("r",dotR);svg.classed("zin",k>=LINES);svgNode.parentNode.classList.toggle("zoomed",k>1.05);if(k>1.5)showLines();else lines.attr("display","none");
          btn("in").disabled=k>=KMAX-1e-6;btn("out").disabled=btn("reset").disabled=k<=1+1e-6}
        if(!raf)raf=requestAnimationFrame(()=>{raf=0;drawTags()});
      });
    svg.call(zoom).on("dblclick.zoom",null).on("dblclick",e=>{e.preventDefault();svg.transition().duration(250).call(zoom.scaleBy,e.shiftKey?.5:2,d3.pointer(e,svgNode))});
    svg.style("touch-action","pan-x pan-y"); // d3 sets none; one finger must keep scrolling the page
    const fit=t=>zoom.constrain()(t,[[0,0],[W,H]],[[0,0],[W,H]]);

    // Touch: one finger scrolls the page. Two fingers pinch and pan the map. A quick double tap zooms in there.
    let pin=null,start=null,moved=false,lastTap=0,lastXY=null;
    const at=t=>d3.pointer(t,svgNode);
    const two=e=>{const [a,b]=[...e.touches].slice(0,2).map(at);return {d:Math.hypot(a[0]-b[0],a[1]-b[1])||1,m:[(a[0]+b[0])/2,(a[1]+b[1])/2]}};
    svgNode.addEventListener("touchstart",e=>{
      if(e.touches.length>=2){e.preventDefault();svg.interrupt();pin={...two(e),t:T};lastTap=0;return}
      pin=null;moved=false;start=[e.touches[0].clientX,e.touches[0].clientY];
    },{passive:false});
    svgNode.addEventListener("touchmove",e=>{
      if(pin&&e.touches.length>=2){
        e.preventDefault();const g=two(e),kk=Math.max(1,Math.min(KMAX,pin.t.k*g.d/pin.d)),p=pin.t.invert(pin.m);
        svg.call(zoom.transform,fit(d3.zoomIdentity.translate(g.m[0]-p[0]*kk,g.m[1]-p[1]*kk).scale(kk)));return;
      }
      if(start&&Math.hypot(e.touches[0].clientX-start[0],e.touches[0].clientY-start[1])>10)moved=true;
    },{passive:false});
    svgNode.addEventListener("touchend",e=>{
      if(pin){if(e.touches.length<2)pin=null;moved=true;return}
      if(moved||e.touches.length||e.changedTouches.length!==1)return;
      const now=e.timeStamp,t=e.changedTouches[0],xy=[t.clientX,t.clientY];
      if(now-lastTap<320&&lastXY&&Math.hypot(xy[0]-lastXY[0],xy[1]-lastXY[1])<30){
        e.preventDefault();lastTap=0;svg.transition().duration(250).call(zoom.scaleBy,2,at(t));
      }else{lastTap=now;lastXY=xy}
    },{passive:false});

    bar.hidden=false;btn("out").disabled=btn("reset").disabled=true;
    bar.onclick=e=>{const b=e.target.closest("button");if(!b)return;const z=b.dataset.zoom,tr=svg.transition().duration(300);
      if(z==="reset")tr.call(zoom.transform,d3.zoomIdentity);else tr.call(zoom.scaleBy,z==="in"?2:.5)};
  }).catch(e=>console.error(e));
})();
