// Draws each site's county outline and pin over its card or hero background.
// Shapes come from /assets/map.json (every state plus each county that holds a site), so the full county file is never needed here.
// window.odcMap() is that one shared fetch (home.js draws the map from it too); window.odcGeo() is the full county file, which only
// the home map loads, when it is zoomed in. window.odcEnhance(root) draws cards added later.
(function(){
  if(!window.d3||!window.topojson)return;
  const ns="http://www.w3.org/2000/svg";
  const json=u=>fetch(u).then(r=>{if(!r.ok)throw new Error(u+" "+r.status);return r.json()});
  let mapP=null,geoP=null,idx=null;
  window.odcMap=()=>mapP||(mapP=json("/assets/map.json"));
  window.odcGeo=()=>geoP||(geoP=json("/assets/geo.json"));
  // On the home page the card outlines wait until the map has drawn (home.js fires odc:map), or 4 s at most.
  const ready=document.getElementById("map")?new Promise(r=>{addEventListener("odc:map",r,{once:true});setTimeout(r,4000)}):Promise.resolve();
  function index(M){
    const byId=new Map(),byName=new Map();
    M.objects.counties.geometries.forEach(g=>{
      byId.set(g.id,g);const n=g.id.slice(0,2)+"|"+g.properties.name.toLowerCase();if(!byName.has(n))byName.set(n,g);
    });
    return {M,byId,byName,states:new Map(M.objects.states.geometries.map(g=>[g.id,g]))};
  }
  const el=(tag,attrs)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));return n};
  function draw(root){
    const {M,byId,byName,states}=idx;
    root.querySelectorAll("svg.bgsvg[data-state]").forEach(svg=>{
      if(svg.dataset.drawn)return;svg.dataset.drawn="1";
      const st=svg.dataset.fips;
      const key=(svg.dataset.county||"").replace(/ (Parish|County)$/,"").toLowerCase();
      const g=byId.get(svg.dataset.cfips)||byName.get(st+"|"+key)||states.get(st);
      if(!g)return;
      const f=topojson.feature(M,g);
      const [w,h]=svg.getAttribute("viewBox").split(" ").slice(2).map(Number);
      const p=d3.geoMercator().fitExtent([[w*.12,h*.1],[w*.88,h*.9]],f);
      svg.appendChild(el("path",{d:d3.geoPath(p)(f),class:"cty"}));
      const lat=parseFloat(svg.dataset.lat),lng=parseFloat(svg.dataset.lng);
      if(!isNaN(lat)&&!isNaN(lng)){
        const [x,y]=p([lng,lat]);
        svg.appendChild(el("circle",{cx:x,cy:y,r:16,class:"ring"}));
        svg.appendChild(el("circle",{cx:x,cy:y,r:7,class:"pin"}));
      }
    });
  }
  window.odcEnhance=root=>{ready.then(window.odcMap).then(M=>{idx=idx||index(M);draw(root||document)}).catch(()=>{})};
  if(document.querySelector("svg.bgsvg[data-state]"))window.odcEnhance(document);
})();
