# Цвета кожи фиксированные — не зависят от palette (иначе в 2D человек бывает чёрным)

_PERSON_CSS = '''
.p-skin{background:#e8b89a}
.p-shirt{background:#4a90d9}
.p-pants{background:#2a3a5c}
.p-eye{background:#1a1a1a}
.p-mouth{background:#2b1010}
'''

# Один человек
T_3D_PERSON = '''<div class="person-wrap" style="width:320px;height:480px;margin:0 auto;position:relative">
<style>''' + _PERSON_CSS + '''</style>
<div id="body" class="p-shirt" style="position:absolute;left:110px;top:200px;width:100px;height:140px;border-radius:40px"></div>
<div id="head" class="p-skin" style="position:absolute;left:120px;top:120px;width:80px;height:80px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:135px;top:145px;width:12px;height:12px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:175px;top:145px;width:12px;height:12px;border-radius:50%"></div>
<div id="mouth" class="p-mouth" style="position:absolute;left:145px;top:175px;width:30px;height:8px;border-radius:8px"></div>
<div id="legL" class="p-pants" style="position:absolute;left:100px;top:340px;width:30px;height:100px;border-radius:12px"></div>
<div id="legR" class="p-pants" style="position:absolute;left:190px;top:340px;width:30px;height:100px;border-radius:12px"></div>
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

# Два человека в одной сцене (светлая кожа, разные рубашки)
T_2_PEOPLE = '''<div class="two-people" style="width:420px;height:480px;margin:0 auto;position:relative">
<style>
.p-skin{background:#e8b89a}
.p-shirt-a{background:#4a90d9}
.p-shirt-b{background:#e94560}
.p-pants{background:#2a3a5c}
.p-eye{background:#1a1a1a}
.p-mouth{background:#2b1010}
</style>
<!-- Person A (left) -->
<div id="bodyA" class="p-shirt-a" style="position:absolute;left:40px;top:200px;width:90px;height:130px;border-radius:36px"></div>
<div id="headA" class="p-skin" style="position:absolute;left:50px;top:125px;width:70px;height:70px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:62px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:95px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-mouth" style="position:absolute;left:72px;top:172px;width:24px;height:7px;border-radius:6px"></div>
<div class="p-pants" style="position:absolute;left:48px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<div class="p-pants" style="position:absolute;left:96px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<!-- Person B (right) -->
<div id="bodyB" class="p-shirt-b" style="position:absolute;left:250px;top:200px;width:90px;height:130px;border-radius:36px"></div>
<div id="headB" class="p-skin" style="position:absolute;left:260px;top:125px;width:70px;height:70px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:272px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:305px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-mouth" style="position:absolute;left:282px;top:172px;width:24px;height:7px;border-radius:6px"></div>
<div class="p-pants" style="position:absolute;left:258px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<div class="p-pants" style="position:absolute;left:306px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<script>
(function(){
  const anim="{anim}";
  const t0=performance.now()/1000;
  const bodyA=document.getElementById("bodyA");
  const bodyB=document.getElementById("bodyB");
  const headA=document.getElementById("headA");
  const headB=document.getElementById("headB");
  function tick(){
    const el=(performance.now()/1000-t0);
    if(anim==="wave"){
      if(bodyA) bodyA.style.transform="rotate("+Math.sin(el*4)*10+"deg)";
      if(bodyB) bodyB.style.transform="rotate("+Math.sin(el*4+1)*10+"deg)";
    } else if(anim==="walk"){
      const s=Math.sin(el*2.5)*10;
      if(bodyA) bodyA.style.left=(40+s)+"px";
      if(headA) headA.style.left=(50+s)+"px";
      if(bodyB) bodyB.style.left=(250-s)+"px";
      if(headB) headB.style.left=(260-s)+"px";
    } else if(anim==="jump"){
      const s=Math.abs(Math.sin(el*2))*40;
      if(bodyA) bodyA.style.top=(200-s)+"px";
      if(headA) headA.style.top=(125-s)+"px";
      if(bodyB) bodyB.style.top=(200-s)+"px";
      if(headB) headB.style.top=(125-s)+"px";
    } else {
      // idle — лёгкое покачивание
      if(bodyA) bodyA.style.transform="rotate("+Math.sin(el*1.2)*3+"deg)";
      if(bodyB) bodyB.style.transform="rotate("+Math.sin(el*1.2+2)*3+"deg)";
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script></div>'''
