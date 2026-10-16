// Draws each site's county outline and pin over its card or hero background.
// window.odcGeo() is the one shared geo.json fetch (home.js uses it too); window.odcEnhance(root) draws cards added later.
(function(){
  if(!window.d3||!window.topojson)return;
  const ns="http://www.w3.org/2000/svg";
  let geo=null,load=null;
  window.odcGeo=()=>load||(load=fetch("/assets/geo.json").then(r=>r.json()).then(GEO=>{
    geo={counties:topojson.feature(GEO,GEO.objects.counties).features,states:topojson.feature(GEO,GEO.objects.states).features};
    return GEO;
  }));
  const el=(tag,attrs)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));return n};
  function draw(root){
    const svgs=[...root.querySelectorAll("svg.bgsvg[data-state]")].filter(s=>!s.dataset.drawn);
    if(!svgs.length)return;
    if(!document.getElementById("odc-defs")){
      const d=document.createElementNS(ns,"svg");d.id="odc-defs";d.setAttribute("width","0");d.setAttribute("height","0");d.style.position="absolute";
      d.innerHTML='<defs><linearGradient id="odc-dark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></linearGradient></defs>';
      document.body.appendChild(d);
    }
    const {counties,states}=geo;
    svgs.forEach(svg=>{
      svg.dataset.drawn="1";
      const st=svg.dataset.fips;
      const key=(svg.dataset.county||"").replace(/ (Parish|County)$/,"").toLowerCase();
      const cf=svg.dataset.cfips;
      const f=(cf?counties.find(c=>c.id===cf):counties.find(c=>c.id.startsWith(st)&&c.properties.name.toLowerCase()===key))||states.find(s=>s.id===st);
      if(!f)return;
      const [w,h]=svg.getAttribute("viewBox").split(" ").slice(2).map(Number);
      const p=d3.geoMercator().fitExtent([[w*.12,h*.1],[w*.88,h*.9]],f);const path=d3.geoPath(p);
      svg.appendChild(el("rect",{width:w,height:h,fill:"url(#odc-dark)"}));
      svg.appendChild(el("path",{d:path(f),fill:"rgba(255,255,255,.16)",stroke:"rgba(255,255,255,.55)","stroke-width":"1.5"}));
      const lat=parseFloat(svg.dataset.lat),lng=parseFloat(svg.dataset.lng);
      if(!isNaN(lat)&&!isNaN(lng)){
        const [x,y]=p([lng,lat]);
        svg.appendChild(el("circle",{cx:x,cy:y,r:7,fill:"#fff","fill-opacity":".9"}));
        svg.appendChild(el("circle",{cx:x,cy:y,r:16,fill:"none",stroke:"#fff","stroke-opacity":".5"}));
      }
    });
  }
  window.odcEnhance=root=>{window.odcGeo().then(()=>draw(root||document)).catch(()=>{})};
  if(document.querySelector("svg.bgsvg[data-state]"))window.odcEnhance(document);
})();
