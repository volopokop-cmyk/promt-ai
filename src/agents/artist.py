from qwen_llm import ask
import json, re
from agents.artist_templates import (
    T_3D_PERSON, T_3D_CAT, T_3D_OBJECT, T_3D_WORLD,
    T_2D_PERSON, T_2D_CAT, T_2D_SCENE, T_2D_CARD,
    T_ABSTRACT, T_DEFAULT, BASE_HTML,
)
TEMPLATES = {
    "3d_person": T_3D_PERSON, "3d_cat": T_3D_CAT, "2d_cat": T_2D_CAT,
    "3d_object": T_3D_OBJECT, "3d_world": T_3D_WORLD, "2d_person": T_2D_PERSON,
    "2d_scene": T_2D_SCENE, "2d_card": T_2D_CARD, "abstract": T_ABSTRACT, "default": T_DEFAULT,
}
PERSON=["человек","челик","персонаж","парень","девушка","person","man","woman","guy","girl","character"]
CAT=["кошк","кот","cat","kitten"]
WORLD=["город","мир","космос","лес","море","city","world","space","forest"]
ABS=["абстрак","неон","энерг","abstract","neon"]
def _has(t,ws):
    t=(t or "").lower();return any(w in t for w in ws)
def _shape(idea):
    t=(idea or "").lower()
    if any(w in t for w in ["шар","мяч","ball","sphere"]): return "sphere"
    if any(w in t for w in ["кольц","ring","torus"]): return "torus"
    return "box"
def run(scene, plan, original_idea="", lip_curve=None, use_llm=True):
    pal=plan.get("palette") or ["#1a1a2e","#e94560","#ffffff","#16213e"]
    c0,c1,c2,c3=(pal+["#1a1a2e","#e94560","#ffffff","#16213e"])[:4]
    style=plan.get("style","3d"); idea=original_idea or ""; st=scene.get("text","") or ""
    visual=(scene.get("visual") or "").lower().strip(); action=(scene.get("action") or "").lower().strip()
    if visual in ("cat","dog"): key="2d_cat" if style=="2d" else "3d_cat"
    elif visual=="person": key="2d_person" if style=="2d" else "3d_person"
    elif visual=="world": key="2d_scene" if style=="2d" else "3d_world"
    elif visual=="abstract": key="abstract"
    elif visual=="object": key="2d_card" if style=="2d" else "3d_object"
    elif _has(st,CAT): key="2d_cat" if style=="2d" else "3d_cat"
    elif _has(st,PERSON): key="2d_person" if style=="2d" else "3d_person"
    elif _has(idea,PERSON) and not _has(st,CAT): key="2d_person" if style=="2d" else "3d_person"
    elif _has(idea,CAT): key="2d_cat" if style=="2d" else "3d_cat"
    elif _has(idea,WORLD): key="2d_scene" if style=="2d" else "3d_world"
    elif _has(idea,ABS): key="abstract"
    else: key="2d_scene" if style=="2d" else "3d_object"
    anim=action or "idle"
    if use_llm and not action:
        try:
            resp=ask('JSON {"anim":"idle|walk|wave|jump|squat|stand|spin"}', f"{st} {idea}", max_new_tokens=40)
            a,b=resp.find("{"),resp.rfind("}")
            if a!=-1 and b!=-1: anim=json.loads(resp[a:b+1]).get("anim",anim)
        except Exception:
            pass
    if key not in TEMPLATES: key="default"
    if key=="3d_object" and anim in ("walk","wave","jump","squat","stand","look"): anim="spin"
    if key in ("3d_person","2d_person") and anim in ("spin","bounce"): anim="idle"
    curve=lip_curve if lip_curve is not None else [0.0]
    text=re.sub(r"[<>]","",st)[:80]
    html=BASE_HTML.replace("{text}",text).replace("{c0}",c0).replace("{c1}",c1).replace("{c2}",c2).replace("{c3}",c3)
    html=html.replace("{object_html}",TEMPLATES[key]).replace("{anim}",anim or "idle")
    html=html.replace("{lip_curve}",json.dumps(curve)).replace("{shape}",_shape(f"{idea} {st}")).replace("{text}",text)
    return html
