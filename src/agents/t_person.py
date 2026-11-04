T_3D_PERSON = '''<div style="width:320px;height:480px;margin:0 auto;position:relative">
<div id="body" style="position:absolute;left:110px;top:200px;width:100px;height:140px;border-radius:40px;background:{c2}"></div>
<div id="head" style="position:absolute;left:120px;top:120px;width:80px;height:80px;border-radius:50%;background:{c1}"></div>
<div style="position:absolute;left:135px;top:145px;width:12px;height:12px;border-radius:50%;background:#111"></div>
<div style="position:absolute;left:175px;top:145px;width:12px;height:12px;border-radius:50%;background:#111"></div>
<div id="mouth" style="position:absolute;left:145px;top:175px;width:30px;height:8px;border-radius:8px;background:#2b1010"></div>
<div style="position:absolute;left:100px;top:340px;width:30px;height:100px;border-radius:12px;background:#2a3a5c"></div>
<div style="position:absolute;left:190px;top:340px;width:30px;height:100px;border-radius:12px;background:#2a3a5c"></div>
<script>
(function(){const anim="{anim}";const lip={lip_curve};const t0=performance.now()/1000;const mouth=document.getElementById("mouth");const body=document.getElementById("body");
function tick(){const el=(performance.now()/1000-t0);const fr=Math.min(lip.length-1,Math.max(0,Math.floor(el*15)));const v=lip.length?lip[fr]:0;
if(mouth)mouth.style.height=(8+v*18)+"px";
if(anim==="squat"&&body){const s=(Math.sin(el*1.6)+1)/2;body.style.top=(200+s*40)+"px"}requestAnimationFrame(tick)}requestAnimationFrame(tick)})();
</script></div>'''
T_2D_PERSON = T_3D_PERSON
