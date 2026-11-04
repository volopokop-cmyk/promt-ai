T_3D_PERSON = '''<div style="width:320px;height:480px;margin:0 auto;position:relative">
<div id="body" style="position:absolute;left:110px;top:200px;width:100px;height:140px;border-radius:40px;background:{c2}"></div>
<div id="head" style="position:absolute;left:120px;top:120px;width:80px;height:80px;border-radius:50%;background:{c1}"></div>
<div style="position:absolute;left:135px;top:145px;width:12px;height:12px;border-radius:50%;background:#111"></div>
<div style="position:absolute;left:175px;top:145px;width:12px;height:12px;border-radius:50%;background:#111"></div>
<div id="mouth" style="position:absolute;left:145px;top:175px;width:30px;height:8px;border-radius:8px;background:#2b1010"></div>
<div id="legL" style="position:absolute;left:100px;top:340px;width:30px;height:100px;border-radius:12px;background:#2a3a5c"></div>
<div id="legR" style="position:absolute;left:190px;top:340px;width:30px;height:100px;border-radius:12px;background:#2a3a5c"></div>
<script>
(function(){
  const anim="{anim}";
  const lip={lip_curve};
  const t0=performance.now()/1000;
  const mouth=document.getElementById("mouth");
  const body=document.getElementById("body");
  const head=document.getElementById("head");
  const legL=document.getElementById("legL");
  const legR=document.getElementById("legR");
  function tick(){
    const el=(performance.now()/1000-t0);
    const fr=Math.min(lip.length-1,Math.max(0,Math.floor(el*15)));
    const v=lip.length?lip[fr]:0;
    if(mouth) mouth.style.height=(8+v*18)+"px";
    if(anim==="squat" && body){
      const s=(Math.sin(el*1.6)+1)/2;
      body.style.top=(200+s*45)+"px";
      if(head) head.style.top=(120+s*45)+"px";
      if(legL){legL.style.height=(100-s*30)+"px"; legL.style.top=(340+s*30)+"px";}
      if(legR){legR.style.height=(100-s*30)+"px"; legR.style.top=(340+s*30)+"px";}
    } else if(anim==="stand" && body){
      const s=Math.min(1, el/1.2);
      body.style.top=(245-s*45)+"px";
      if(head) head.style.top=(165-s*45)+"px";
    } else if(anim==="walk" && body){
      const s=Math.sin(el*3)*12;
      body.style.left=(110+s)+"px";
      if(head) head.style.left=(120+s)+"px";
      if(legL) legL.style.transform="rotate("+Math.sin(el*3)*15+"deg)";
      if(legR) legR.style.transform="rotate("+Math.sin(el*3+Math.PI)*15+"deg)";
    } else if(anim==="wave" && body){
      body.style.transform="rotate("+Math.sin(el*4)*8+"deg)";
    } else if(anim==="jump" && body){
      const s=Math.abs(Math.sin(el*2.5))*50;
      body.style.top=(200-s)+"px";
      if(head) head.style.top=(120-s)+"px";
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script></div>'''
T_2D_PERSON = T_3D_PERSON
