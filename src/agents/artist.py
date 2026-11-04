from qwen_llm import ask
import json
import re

# See modes + multi-scene pipeline. Templates below.

T_3D_PERSON = r"""
<div class=\"character\" style=\"position:relative;width:420px;height:560px;margin:0 auto;\">
<script src=\"https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js\"></script>
<script>
(function(){
  const container=document.currentScript.parentElement;
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(42,420/560,0.1,100);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(420,560);container.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xddeeff,0x443322,1.15));
  const key=new THREE.DirectionalLight(0xfff0dd,1.6);key.position.set(-2.5,5,4);scene.add(key);
  const skinMat=new THREE.MeshStandardMaterial({color:\"{c1}\",roughness:0.65});
  const shirtMat=new THREE.MeshStandardMaterial({color:\"{c2}\",roughness:0.75});
  const pantsMat=new THREE.MeshStandardMaterial({color:\"#2a3a5c\",roughness:0.8});
  const darkMat=new THREE.MeshStandardMaterial({color:\"#2b1010\",roughness:0.55});
  const lipMat=new THREE.MeshStandardMaterial({color:\"#c45c6a\",roughness:0.45});
  const root=new THREE.Group();scene.add(root);
  const pelvis=new THREE.Group();pelvis.position.set(0,1.05,0);root.add(pelvis);
  const spine=new THREE.Group();spine.position.set(0,0.18,0);pelvis.add(spine);
  const chest=new THREE.Group();chest.position.set(0,0.28,0);spine.add(chest);
  const neck=new THREE.Group();neck.position.set(0,0.38,0);chest.add(neck);
  const head=new THREE.Group();head.position.set(0,0.22,0);neck.add(head);
  const armL=new THREE.Group();armL.position.set(-0.38,0.2,0);chest.add(armL);
  const armR=new THREE.Group();armR.position.set(0.38,0.2,0);chest.add(armR);
  const legL=new THREE.Group();legL.position.set(-0.15,-0.05,0);pelvis.add(legL);
  const legR=new THREE.Group();legR.position.set(0.15,-0.05,0);pelvis.add(legR);
  function mesh(p,g,m,y=0,x=0,z=0,sx=1,sy=1,sz=1){const o=new THREE.Mesh(g,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);p.add(o);return o;}
  mesh(pelvis,new THREE.SphereGeometry(0.3,20,20),pantsMat,0,0,0,1.15,0.75,0.95);
  mesh(spine,new THREE.CylinderGeometry(0.24,0.26,0.38,18),shirtMat,0.12);
  mesh(chest,new THREE.CylinderGeometry(0.27,0.25,0.4,18),shirtMat,0.12);
  mesh(neck,new THREE.CylinderGeometry(0.09,0.1,0.18,14),skinMat,0.06);
  mesh(head,new THREE.SphereGeometry(0.24,28,28),skinMat,0.2);
  mesh(head,new THREE.SphereGeometry(0.038,12,12),new THREE.MeshStandardMaterial({color:0xffffff}),0.22,-0.09,0.2);
  mesh(head,new THREE.SphereGeometry(0.038,12,12),new THREE.MeshStandardMaterial({color:0xffffff}),0.22,0.09,0.2);
  mesh(head,new THREE.SphereGeometry(0.018,10,10),new THREE.MeshStandardMaterial({color:0x1a1a1a}),0.22,-0.09,0.23);
  mesh(head,new THREE.SphereGeometry(0.018,10,10),new THREE.MeshStandardMaterial({color:0x1a1a1a}),0.22,0.09,0.23);
  const jaw=new THREE.Group();jaw.position.set(0,0.06,0.14);head.add(jaw);
  const lowerLip=mesh(jaw,new THREE.BoxGeometry(0.11,0.028,0.04),lipMat,-0.012,0,0.02);
  const mouthHole=mesh(jaw,new THREE.BoxGeometry(0.09,0.02,0.03),darkMat,0.002,0,0.015);
  mesh(armL,new THREE.CylinderGeometry(0.085,0.075,0.55,14),skinMat,-0.28);
  mesh(armR,new THREE.CylinderGeometry(0.085,0.075,0.55,14),skinMat,-0.28);
  mesh(legL,new THREE.CylinderGeometry(0.11,0.095,0.75,14),pantsMat,-0.38);
  mesh(legR,new THREE.CylinderGeometry(0.11,0.095,0.75,14),pantsMat,-0.38);
  camera.position.set(0,1.35,5);camera.lookAt(0,1.15,0);
  const anim=\"{anim}\";const lipCurve={lip_curve};const fps=15;
  const clock=new THREE.Clock();const t0=performance.now()/1000;
  function mouthOpen(v){const o=Math.max(0,Math.min(1,v));jaw.rotation.x=o*0.32;lowerLip.position.y=-0.012-o*0.035;mouthHole.scale.y=0.4+o*2.2;}
  function animate(){requestAnimationFrame(animate);const t=clock.getElapsedTime();const el=performance.now()/1000-t0;
    const fr=Math.min(lipCurve.length-1,Math.max(0,Math.floor(el*fps)));mouthOpen(lipCurve.length?lipCurve[fr]:0);
    if(anim===\"jump\"){const c=(t*1.1)%(Math.PI*2);const j=Math.max(0,Math.sin(c))*0.38;root.position.y=j;}
    else if(anim===\"wave\"){armR.rotation.z=Math.sin(t*4.2)*0.45-1.35;}
    else if(anim===\"walk\"){const s=2.2;legL.rotation.x=Math.sin(t*s)*0.38;legR.rotation.x=-Math.sin(t*s)*0.38;}
    else if(anim===\"squat\"){const s=(Math.sin(t*1.6)+1)/2;root.position.y=-s*0.35;legL.rotation.x=s*0.9;legR.rotation.x=s*0.9;}
    else if(anim===\"stand\"||anim===\"look\"){root.position.y=0;root.rotation.y=Math.sin(t*0.4)*0.1;}
    else{chest.position.y=0.28+Math.sin(t*1.6)*0.012;root.rotation.y=Math.sin(t*0.55)*0.12;}
    renderer.render(scene,camera);}
  animate();
})();
</script></div>
"""

# truncated intentionally - use file from compact
print('use compact')
