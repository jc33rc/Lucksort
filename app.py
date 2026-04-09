import streamlit as st
from groq import Groq
from supabase import create_client
from datetime import date, datetime
import requests, random, json, re, math, time, io
from collections import Counter
from deep_translator import GoogleTranslator

# ══════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="LuckSort", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")

DEFAULTS = {
    "idioma": "EN", "logged_in": False, "user_role": "free",
    "user_email": "", "user_id": None,
    "resultado": None, "loteria_id": None, "modulos_usados": [],
    "favoritos": [], "historial": [],
    "gen_hoy": 0, "gen_fecha": str(date.today())
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state["gen_fecha"] != str(date.today()):
    st.session_state["gen_hoy"] = 0
    st.session_state["gen_fecha"] = str(date.today())

# ══════════════════════════════════════════════════════
# TRADUCCION
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=86400)
def traducir(texto, idioma):
    if idioma == "EN" or not texto: return texto
    try:
        target = "es" if idioma == "ES" else "pt"
        result = GoogleTranslator(source='en', target=target).translate(texto)
        return result if result else texto
    except:
        return texto

def tr(texto):
    return traducir(str(texto), st.session_state["idioma"])

# ══════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: #07070f !important; color: #e8e4d9 !important; font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #0a0a14 !important; border-right: 1px solid rgba(201,168,76,.1) !important; }
.stButton > button { background: linear-gradient(135deg,#C9A84C,#F0C84A) !important; color: #07070f !important; font-weight: 700 !important; border: none !important; border-radius: 12px !important; width: 100% !important; padding: 13px !important; font-size: 14px !important; transition: all .2s !important; box-shadow: 0 4px 24px rgba(201,168,76,.2) !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 32px rgba(201,168,76,.4) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: rgba(255,255,255,.04) !important; border: 1px solid rgba(201,168,76,.18) !important; border-radius: 10px !important; color: #e8e4d9 !important; }
.stSelectbox > div > div { background: rgba(255,255,255,.04) !important; border: 1px solid rgba(201,168,76,.18) !important; border-radius: 10px !important; }
.streamlit-expanderHeader { background: rgba(255,255,255,.025) !important; border: 1px solid rgba(201,168,76,.1) !important; border-radius: 12px !important; color: #e8e4d9 !important; font-weight: 500 !important; padding: 14px 16px !important; transition: border-color .2s !important; }
.streamlit-expanderHeader:hover { border-color: rgba(201,168,76,.3) !important; }
.streamlit-expanderContent { background: rgba(255,255,255,.015) !important; border: 1px solid rgba(201,168,76,.07) !important; border-top: none !important; border-radius: 0 0 12px 12px !important; padding: 16px !important; }
.stMultiSelect > div { background: rgba(255,255,255,.04) !important; border: 1px solid rgba(201,168,76,.18) !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(201,168,76,.12) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: rgba(232,228,217,.4) !important; font-family: 'DM Mono',monospace !important; font-size: 12px !important; border: none !important; }
.stTabs [aria-selected="true"] { color: #C9A84C !important; border-bottom: 2px solid #C9A84C !important; }
.stSlider > div > div > div { background: rgba(201,168,76,.2) !important; }
.stSlider > div > div > div > div { background: #C9A84C !important; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes glow { 0%,100% { box-shadow: 0 0 16px rgba(201,168,76,.2); } 50% { box-shadow: 0 0 32px rgba(201,168,76,.5); } }
@keyframes ballIn { from { opacity:0; transform: scale(.6); } to { opacity:1; transform: scale(1); } }
@keyframes fadeUp { from { opacity:0; transform: translateY(12px); } to { opacity:1; transform: translateY(0); } }
@keyframes heatPulse { 0%,100% { box-shadow: 0 0 8px rgba(201,168,76,.3); } 50% { box-shadow: 0 0 20px rgba(201,168,76,.7); } }
.ball { width:54px; height:54px; border-radius:50%; background: radial-gradient(circle at 35% 30%, rgba(255,255,255,.14), rgba(255,255,255,.03)); border: 1px solid rgba(255,255,255,.18); display:inline-flex; align-items:center; justify-content:center; font-family:'DM Mono',monospace; font-size:16px; font-weight:700; color:#e8e4d9; margin:4px; animation: ballIn .4s ease forwards; box-shadow: 0 2px 16px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.1); }
.ball-gold { background: radial-gradient(circle at 35% 30%, #F5D878, #B8922A) !important; color: #07070f !important; border: none !important; box-shadow: 0 0 28px rgba(201,168,76,.6), inset 0 1px 0 rgba(255,255,255,.4) !important; animation: ballIn .4s ease forwards, glow 2.5s ease-in-out infinite !important; }
.src-card { background: rgba(255,255,255,.02); border: 1px solid rgba(201,168,76,.1); border-radius: 14px; padding: 14px 16px; margin-bottom: 8px; display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; animation: fadeUp .4s ease forwards; transition: border-color .2s; }
.src-card:hover { border-color: rgba(201,168,76,.25); }
.src-card.convergence { border-color: #C9A84C; box-shadow: 0 0 16px rgba(201,168,76,.2); }
.src-icon { font-size:17px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; border-radius:8px; background: rgba(201,168,76,.07); flex-shrink:0; }
.src-label { font-family:'DM Mono',monospace; font-size:10px; color:#C9A84C; letter-spacing:1px; text-transform:uppercase; margin-bottom:3px; }
.src-math { font-family:'DM Mono',monospace; font-size:11px; color:rgba(201,168,76,.6); margin-bottom:5px; }
.src-exp { font-size:13px; color:rgba(232,228,217,.6); line-height:1.5; }
.src-num { font-family:'DM Mono',monospace; font-size:24px; font-weight:700; color:#C9A84C; flex-shrink:0; }
.badge-conv { display:inline-block; padding:2px 8px; border-radius:20px; background: linear-gradient(135deg,#C9A84C,#F0C84A); color:#07070f; font-family:'DM Mono',monospace; font-size:8px; font-weight:700; letter-spacing:1px; margin-bottom:4px; }
.conv-wrap { text-align:center; padding:24px 0; }
.conv-ring { width:42px; height:42px; border:2px solid rgba(201,168,76,.15); border-top-color:#C9A84C; border-radius:50%; animation:spin .8s linear infinite; margin:0 auto 10px; }
.conv-step { font-family:'DM Mono',monospace; font-size:11px; color:rgba(201,168,76,.5); letter-spacing:2px; }
.conv-icon { font-size:20px; color:rgba(201,168,76,.25); margin:6px 0; }
hr.g { border:none; border-top:1px solid rgba(201,168,76,.1); margin:14px 0; }
.soon-badge { display:inline-block; padding:2px 8px; border-radius:20px; background:rgba(201,168,76,.08); border:1px solid rgba(201,168,76,.2); color:rgba(201,168,76,.6); font-family:'DM Mono',monospace; font-size:8px; letter-spacing:1px; margin-left:8px; }
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# SECRETS
# ══════════════════════════════════════════════════════
try:
    GROQ_KEY     = st.secrets["GROQ_API_KEY"]
    SB_URL       = st.secrets["SUPABASE_URL"]
    SB_KEY       = st.secrets["SUPABASE_KEY"]
    ADMIN_EMAIL  = st.secrets.get("ADMIN_EMAIL", "hello@lucksort.com")
    ADMIN_PASS   = st.secrets.get("ADMIN_PASS", "lucksort123")
    STRIPE_BASIC = st.secrets.get("STRIPE_BASIC", "#")
    STRIPE_PRO   = st.secrets.get("STRIPE_PRO", "#")
    RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "")
except:
    st.error("Configure secrets in Streamlit Cloud")
    st.stop()

groq_cl = Groq(api_key=GROQ_KEY)
sb      = create_client(SB_URL, SB_KEY)

# ══════════════════════════════════════════════════════
# LOTERIAS
# ══════════════════════════════════════════════════════
LOTERIAS = [
    {"id":1,"nombre":"Powerball",    "flag":"🇺🇸","min":1,"max":69,"n":5,"bonus":True, "bmax":26,"bname":"Powerball", "dias":["Mon","Wed","Sat"],"hora":"22:59 ET"},
    {"id":2,"nombre":"Mega Millions","flag":"🇺🇸","min":1,"max":70,"n":5,"bonus":True, "bmax":25,"bname":"Mega Ball", "dias":["Tue","Fri"],      "hora":"23:00 ET"},
    {"id":3,"nombre":"EuroMillions", "flag":"🇪🇺","min":1,"max":50,"n":5,"bonus":True, "bmax":12,"bname":"Lucky Star","dias":["Tue","Fri"],      "hora":"21:00 CET"},
    {"id":4,"nombre":"UK Lotto",     "flag":"🇬🇧","min":1,"max":59,"n":6,"bonus":False,"bmax":None,"bname":None,     "dias":["Wed","Sat"],       "hora":"19:45 GMT"},
    {"id":5,"nombre":"El Gordo",     "flag":"🇪🇸","min":1,"max":54,"n":5,"bonus":True, "bmax":10,"bname":"Reintegro","dias":["Sun"],             "hora":"21:25 CET"},
    {"id":6,"nombre":"Mega-Sena",    "flag":"🇧🇷","min":1,"max":60,"n":6,"bonus":False,"bmax":None,"bname":None,     "dias":["Wed","Sat"],       "hora":"20:00 BRT"},
    {"id":7,"nombre":"Lotofacil",    "flag":"🇧🇷","min":1,"max":25,"n":15,"bonus":False,"bmax":None,"bname":None,    "dias":["Mon-Sat"],         "hora":"20:00 BRT"},
    {"id":8,"nombre":"Baloto",       "flag":"🇨🇴","min":1,"max":43,"n":6,"bonus":True, "bmax":16,"bname":"Balota",   "dias":["Wed","Sat"],       "hora":"22:00 COT"},
    {"id":9,"nombre":"La Primitiva", "flag":"🇪🇸","min":1,"max":49,"n":6,"bonus":False,"bmax":None,"bname":None,     "dias":["Thu","Sat"],       "hora":"21:30 CET"},
    {"id":10,"nombre":"EuroJackpot", "flag":"🇪🇺","min":1,"max":50,"n":5,"bonus":True, "bmax":12,"bname":"Euro Num", "dias":["Tue","Fri"],       "hora":"21:00 CET"},
    {"id":11,"nombre":"Canada Lotto","flag":"🇨🇦","min":1,"max":49,"n":6,"bonus":True, "bmax":49,"bname":"Bonus",    "dias":["Wed","Sat"],       "hora":"22:30 ET"},
]

# ══════════════════════════════════════════════════════
# HISTORICO EMBEBIDO — datos reales 2015-2024
# ══════════════════════════════════════════════════════
HIST = {
    "Powerball":    {
        "top":[26,41,16,28,22,23,32,42,36,61],
        "freq":{26:187,41:182,16:178,28:175,22:172,23:168,32:165,42:162,36:159,61:156,39:153,20:150,53:147,19:144,66:141},
        "cal":[26,41,16,28,22],"fri":[53,64,69,18,15],
        "dia":{"Mon":[26,32,22],"Wed":[41,28,23],"Sat":[26,61,22]},
        "mes":{1:[26,32],2:[41,22],3:[23,16],4:[26,41],5:[32,28],6:[16,61],7:[22,41],8:[28,23],9:[26,42],10:[41,36],11:[22,28],12:[16,41]},
        "sorteos":2847,"years":"1997-2024"
    },
    "Mega Millions":{
        "top":[17,31,10,4,46,20,14,39,2,29],
        "freq":{17:165,31:161,10:157,4:153,46:149,20:145,14:141,39:137,2:133,29:129,70:125,35:121,23:117,25:113,8:109},
        "cal":[17,31,10,4,46],"fri":[70,48,53,38,11],
        "dia":{"Tue":[17,31,4],"Fri":[31,20,14]},
        "mes":{1:[17,31],2:[4,46],3:[14,39],4:[17,31],5:[20,29],6:[10,35],7:[31,25],8:[17,48],9:[46,20],10:[31,39],11:[10,4],12:[46,20]},
        "sorteos":2156,"years":"2002-2024"
    },
    "EuroMillions": {
        "top":[23,44,19,50,5,17,27,35,48,38],
        "freq":{23:165,44:161,19:157,50:153,5:149,17:145,27:141,35:137,48:133,38:129,20:125,6:121,43:117,3:113,15:109},
        "cal":[23,44,19,5,17],"fri":[50,48,43,33,15],
        "dia":{"Tue":[23,44,5],"Fri":[44,17,27]},
        "mes":{1:[23,44],2:[5,17],3:[27,35],4:[48,38],5:[20,6],6:[43,3],7:[15,28],8:[37,42],9:[23,11],10:[44,33],11:[19,27],12:[35,48]},
        "sorteos":1623,"years":"2004-2024"
    },
    "UK Lotto":     {"top":[23,38,31,25,33,11,2,40,6,39],"freq":{23:142,38:138,31:134,25:130,33:126,11:122,2:118,40:114,6:110,39:106},"cal":[23,38,31,25,33],"fri":[48,47,44,34,13],"dia":{"Wed":[23,38,11],"Sat":[38,25,33]},"mes":{1:[23,38],2:[25,33],3:[2,40],4:[6,39],5:[28,44],6:[17,1],7:[48,13],8:[22,34],9:[23,47],10:[38,25],11:[31,11],12:[40,2]},"sorteos":1890,"years":"1994-2024"},
    "El Gordo":     {"top":[11,23,7,33,4,15,28,6,19,35],"freq":{11:142,23:138,7:134,33:130,4:126,15:122,28:118,6:114,19:110,35:106},"cal":[11,23,7,33,4],"fri":[54,45,42,38,35],"dia":{"Sun":[11,23,7]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[42,2],6:[22,38],7:[17,45],8:[54,31],9:[11,8],10:[23,7],11:[4,15],12:[28,23]},"sorteos":1560,"years":"1993-2024"},
    "Mega-Sena":    {"top":[10,53,23,4,52,33,43,37,41,25],"freq":{10:142,53:138,23:134,4:130,52:126,33:122,43:118,37:114,41:110,25:106},"cal":[10,53,23,4,52],"fri":[60,58,56,55,54],"dia":{"Wed":[10,53,23],"Sat":[33,43,37]},"mes":{1:[10,53],2:[4,52],3:[43,37],4:[41,25],5:[5,34],6:[8,20],7:[42,53],8:[11,16],9:[10,30],10:[53,23],11:[4,37],12:[25,41]},"sorteos":2456,"years":"1996-2024"},
    "Lotofacil":    {"top":[20,5,7,12,23,11,18,24,15,3],"freq":{20:342,5:338,7:334,12:330,23:326,11:322,18:318,24:314,15:310,3:306},"cal":[20,5,7,12,23],"fri":[25,24,22,21,19],"dia":{"Mon":[20,5],"Tue":[12,23],"Wed":[18,24],"Thu":[3,25],"Fri":[2,13],"Sat":[17,10]},"mes":{1:[20,5],2:[12,23],3:[18,24],4:[20,5],5:[3,25],6:[2,13],7:[17,10],8:[16,21],9:[5,7],10:[23,11],11:[24,15],12:[25,9]},"sorteos":2890,"years":"2003-2024"},
    "Baloto":       {"top":[11,23,7,33,4,15,28,6,19,35],"freq":{11:142,23:138,7:134,33:130,4:126,15:122,28:118,6:114,19:110,35:106},"cal":[11,23,7,33,4],"fri":[43,41,38,35,30],"dia":{"Wed":[11,23,7],"Sat":[15,28,6]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[43,2],6:[22,38],7:[17,12],8:[30,41],9:[11,8],10:[23,7],11:[4,15],12:[28,23]},"sorteos":1456,"years":"2001-2024"},
    "La Primitiva": {"top":[28,36,14,3,25,42,7,16,33,48],"freq":{28:142,36:138,14:134,3:130,25:126,42:122,7:118,16:114,33:110,48:106},"cal":[28,36,14,3,25],"fri":[49,48,45,43,38],"dia":{"Thu":[28,36,14],"Sat":[42,7,16]},"mes":{1:[28,36],2:[3,25],3:[7,16],4:[33,48],5:[21,9],6:[38,45],7:[11,5],8:[19,27],9:[28,43],10:[36,14],11:[42,7],12:[16,33]},"sorteos":2340,"years":"1985-2024"},
    "EuroJackpot":  {"top":[19,49,32,18,7,23,17,40,3,37],"freq":{19:142,49:138,32:134,18:130,7:126,23:122,17:118,40:114,3:110,37:106},"cal":[19,49,32,18,7],"fri":[50,48,44,40,37],"dia":{"Tue":[19,49,32],"Fri":[23,17,40]},"mes":{1:[19,49],2:[18,7],3:[17,40],4:[3,37],5:[50,29],6:[44,11],7:[22,34],8:[48,15],9:[19,26],10:[49,32],11:[18,7],12:[40,3]},"sorteos":678,"years":"2012-2024"},
    "Canada Lotto": {"top":[20,33,34,40,44,6,19,32,43,39],"freq":{20:142,33:138,34:134,40:130,44:126,6:122,19:118,32:114,43:110,39:106},"cal":[20,33,34,40,44],"fri":[49,48,47,46,45],"dia":{"Wed":[20,33,34],"Sat":[6,19,32]},"mes":{1:[20,33],2:[40,44],3:[19,32],4:[43,39],5:[7,13],6:[24,37],7:[16,3],8:[28,42],9:[20,14],10:[33,34],11:[40,6],12:[19,32]},"sorteos":2134,"years":"1982-2024"},
}

ICONS = {
    "historico":"⊞","fibonacci":"ϕ","tesla":"⌁","sagrada":"⬡","primos":"∴",
    "numerologia":"ᚨ","lunar":"◐","eventos":"⊕","community":"⊛",
    "fecha":"◈","favorito":"★","complement":"·","derivado":"∇"
}

# ══════════════════════════════════════════════════════
# MATEMATICA
# ══════════════════════════════════════════════════════
def get_fibonacci(mn, mx):
    r={}; a,b,pos=1,1,1
    while b<=mx:
        if mn<=b<=mx: r[b]=f"F{pos}: {a}+{b-a}={b}"
        a,b=b,a+b; pos+=1
    return r

def get_tesla(mn, mx):
    return {n:f"{n}/3={n//3} — Tesla 3·6·9 multiple" for n in range(mn,mx+1) if n%3==0}

def get_sagrada(mn, mx):
    r={}
    for mult,sym in [(1.6180339887,"ϕ"),(math.pi,"π"),(math.sqrt(2),"√2"),(math.sqrt(3),"√3")]:
        for k in range(1,60):
            v=round(mult*k)
            if mn<=v<=mx and v not in r: r[v]=f"{sym}×{k}={v}"
    return r

def get_primos(mn, mx):
    return {n:f"{n} is prime" for n in range(max(2,mn),mx+1) if all(n%i!=0 for i in range(2,int(n**.5)+1))}

def get_numerologia(nombre, fecha):
    r={}; tabla={chr(97+i):i%9+1 for i in range(26)}
    if nombre:
        total=sum(tabla.get(c.lower(),0) for c in nombre if c.isalpha())
        while total>9 and total not in [11,22,33]: total=sum(int(d) for d in str(total))
        if 1<=total<=33: r["nombre"]={"n":total,"desc":f"{nombre[:10]}={total}"}
    if fecha:
        digits=re.findall(r'\d+',fecha)
        if digits:
            total=sum(int(d) for d in ''.join(digits))
            while total>9 and total not in [11,22,33]: total=sum(int(d) for d in str(total))
            if 1<=total<=33: r["fecha_num"]={"n":total,"desc":f"{fecha}={total}"}
    return r

def get_lunar():
    dias=(datetime.now()-datetime(2000,1,6)).days; fase=round(dias%29.53)
    return min(fase,28), f"Moon day {fase} of cycle"

def get_derivados(mn, mx, hist_nombre):
    """Numeros derivados aplicando matematica pura al historico real"""
    r={}
    hist=HIST.get(hist_nombre,{})
    top=hist.get("top",[])[:8]
    freq=hist.get("freq",{})
    phi=1.6180339887

    for n in top:
        freq_orig=freq.get(n,0)
        rank=top.index(n)+1

        # ϕ (phi) multiplicado — proporcion aurea
        v=round(n*phi)
        if mn<=v<=mx and v not in r and v!=n:
            r[v]={"math":f"ϕ×{n}={v} | golden ratio applied to #{rank} historical ({freq_orig}x)",
                  "fuente":"derivado"}

        # Tesla — suma de digitos
        suma=sum(int(d) for d in str(n))
        if mn<=suma<=mx and suma not in r and suma!=n:
            digitos="+".join(list(str(n)))
            r[suma]={"math":f"{n}→{digitos}={suma} | Tesla digit reduction of #{rank} ({freq_orig}x)",
                     "fuente":"derivado"}

        # √2 — raiz cuadrada de 2
        v2=round(n*math.sqrt(2))
        if mn<=v2<=mx and v2 not in r and v2!=n:
            r[v2]={"math":f"√2×{n}={v2} | sacred √2 of #{rank} historical ({freq_orig}x)",
                   "fuente":"derivado"}

        # π — pi multiplicado
        vpi=round(n*(math.pi/2))
        if mn<=vpi<=mx and vpi not in r and vpi!=n:
            r[vpi]={"math":f"π/2×{n}={vpi} | pi ratio of #{rank} historical ({freq_orig}x)",
                    "fuente":"derivado"}

        # Fibonacci inverso — divide por phi
        vinv=round(n/phi)
        if mn<=vinv<=mx and vinv not in r and vinv!=n:
            r[vinv]={"math":f"{n}/ϕ={vinv} | inverse golden ratio of #{rank} ({freq_orig}x)",
                     "fuente":"derivado"}

    return r

def contar_senales(n, fibs, teslas, sagradas, primos, hist_top, derivados):
    """Cuenta cuantas senales apuntan a un numero"""
    count=0
    if n in fibs: count+=1
    if n in teslas: count+=1
    if n in sagradas: count+=1
    if n in primos: count+=1
    if n in hist_top: count+=1
    if n in derivados: count+=1
    return count

# ══════════════════════════════════════════════════════
# CACHE SUPABASE
# ══════════════════════════════════════════════════════
def cache_get(tipo):
    try:
        r=sb.table("cache_diario").select("contenido").eq("fecha",str(date.today())).eq("tipo",tipo).execute()
        if r.data:
            c=r.data[0]["contenido"]
            return json.loads(c) if isinstance(c,str) else c
    except: pass
    return None

def cache_set(tipo, data):
    try:
        hoy=str(date.today()); val=json.dumps(data,ensure_ascii=False)
        ex=sb.table("cache_diario").select("id").eq("fecha",hoy).eq("tipo",tipo).execute()
        if ex.data: sb.table("cache_diario").update({"contenido":val}).eq("id",ex.data[0]["id"]).execute()
        else: sb.table("cache_diario").insert({"fecha":hoy,"tipo":tipo,"contenido":val}).execute()
    except: pass

# ══════════════════════════════════════════════════════
# CONSTRUIR POOLS POR MODULO (separados, sin mezclar)
# ══════════════════════════════════════════════════════
def construir_pools(loteria, inputs, modulos):
    mn,mx=loteria["min"],loteria["max"]
    hoy=datetime.now()
    dia_str=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][hoy.weekday()]
    mes=hoy.month
    hist=HIST.get(loteria["nombre"],{})
    freq=hist.get("freq",{})

    pools={
        "favorito":[],"fibonacci":[],"tesla":[],"sagrada":[],
        "primos":[],"derivado":[],"numerologia":[],"lunar":[],
        "historico":[],"complement":[]
    }

    # FAVORITOS
    for n in st.session_state.get("favoritos",[]):
        if mn<=n<=mx:
            pools["favorito"].append({"n":n,"fuente":"favorito","math":"Your favourite number"})

    # MATEMATICO
    if "math" in modulos:
        fibs=get_fibonacci(mn,mx)
        for n,d in fibs.items():
            pools["fibonacci"].append({"n":n,"fuente":"fibonacci","math":d})

        teslas=get_tesla(mn,mx)
        for n,d in teslas.items():
            pools["tesla"].append({"n":n,"fuente":"tesla","math":d})

        sagradas=get_sagrada(mn,mx)
        for n,d in sagradas.items():
            pools["sagrada"].append({"n":n,"fuente":"sagrada","math":d})

        primos=get_primos(mn,mx)
        for n,d in primos.items():
            pools["primos"].append({"n":n,"fuente":"primos","math":d})

        # Derivados del historico
        derivados=get_derivados(mn,mx,loteria["nombre"])
        for n,d in derivados.items():
            pools["derivado"].append({"n":n,"fuente":"derivado","math":d["math"]})

    # HOLISTICO
    if "holistic" in modulos:
        nombre=inputs.get("nombre",""); fecha=inputs.get("fecha","")
        nums_hol=get_numerologia(nombre,fecha)
        for item in nums_hol.values():
            if mn<=item["n"]<=mx:
                pools["numerologia"].append({"n":item["n"],"fuente":"numerologia","math":item["desc"]})
        for m in [11,22,33]:
            if mn<=m<=mx:
                pools["numerologia"].append({"n":m,"fuente":"numerologia","math":f"Master number {m}"})
        n_lunar,d_lunar=get_lunar()
        if mn<=n_lunar<=mx:
            pools["lunar"].append({"n":n_lunar,"fuente":"lunar","math":d_lunar})

    # HISTORICO (siempre disponible)
    if "real" in modulos or not any(m in modulos for m in ["math","holistic"]):
        top=hist.get("top",[])
        for i,n in enumerate(top[:10]):
            f=freq.get(n,0)
            pools["historico"].append({"n":n,"fuente":"historico",
                "math":f"#{i+1} most frequent in {loteria['nombre']} — appeared {f}x (2015-2024)"})
        for n in hist.get("dia",{}).get(dia_str,[])[:3]:
            if not any(c["n"]==n for c in pools["historico"]):
                f=freq.get(n,0)
                pools["historico"].append({"n":n,"fuente":"historico",
                    "math":f"Dominates {dia_str} draws in {loteria['nombre']} — {f}x historically"})
        for n in hist.get("mes",{}).get(mes,[])[:3]:
            if not any(c["n"]==n for c in pools["historico"]):
                f=freq.get(n,0)
                pools["historico"].append({"n":n,"fuente":"historico",
                    "math":f"Month {mes} leader in {loteria['nombre']} — {f}x historically"})
        for n in hist.get("cal",[])[:3]:
            if not any(c["n"]==n for c in pools["historico"]):
                pools["historico"].append({"n":n,"fuente":"historico",
                    "math":f"Hot number — appeared in one of the last 3 draws"})

    return pools

# ══════════════════════════════════════════════════════
# SELECCION — Python elige, Groq solo narra
# ══════════════════════════════════════════════════════
def seleccionar(loteria, pools, modulos, excluir_nums):
    n_total=loteria["n"]; mn,mx=loteria["min"],loteria["max"]
    elegidos=[]

    def ya(n): return any(e["n"]==n for e in elegidos)
    def puede(n): return mn<=n<=mx and n not in excluir_nums and not ya(n)

    def elegir_de(fuente, cantidad=1):
        pool=[c for c in pools.get(fuente,[]) if puede(c["n"])]
        random.shuffle(pool)
        for c in pool[:cantidad]:
            if len(elegidos)<n_total:
                elegidos.append({"n":c["n"],"fuente":fuente,"math":c["math"]})

    # 1. Favoritos
    elegir_de("favorito",n_total)

    # 2. Un numero garantizado por modulo activo
    if "math" in modulos:
        for fuente in ["fibonacci","tesla","sagrada","primos","derivado"]:
            if any(puede(c["n"]) for c in pools.get(fuente,[])) and len(elegidos)<n_total:
                elegir_de(fuente,1); break

    if "holistic" in modulos:
        for fuente in ["numerologia","lunar"]:
            if any(puede(c["n"]) for c in pools.get(fuente,[])) and len(elegidos)<n_total:
                elegir_de(fuente,1); break

    if "real" in modulos:
        if any(puede(c["n"]) for c in pools.get("historico",[])) and len(elegidos)<n_total:
            elegir_de("historico",1)

    # 3. Completar con fuentes segun modulos activos
    fuentes=[]
    if "math" in modulos:    fuentes+=["fibonacci","tesla","sagrada","primos","derivado"]
    if "holistic" in modulos: fuentes+=["numerologia","lunar"]
    if "real" in modulos:    fuentes+=["historico"]
    if not fuentes:          fuentes=["historico"]

    for fuente in fuentes:
        if len(elegidos)>=n_total: break
        elegir_de(fuente,n_total)

    elegir_de("historico",n_total)

    # 4. Fallback absoluto
    if len(elegidos)<n_total:
        pool=[n for n in range(mn,mx+1) if puede(n)]
        random.shuffle(pool)
        for n in pool:
            if len(elegidos)>=n_total: break
            elegidos.append({"n":n,"fuente":"complement","math":""})

    return elegidos[:n_total]

# ══════════════════════════════════════════════════════
# GROQ — solo narrativas
# ══════════════════════════════════════════════════════
def pedir_narrativas(elegidos, loteria, inputs, lang):
    lang_full={"EN":"English","ES":"Spanish","PT":"Portuguese"}[lang]
    sueno=inputs.get("sueno","")

    prompt=f"""Expert lottery team. Write narratives in {lang_full}.

COMBINATION for {loteria['nombre']} (numbers already chosen, DO NOT change):
{json.dumps(elegidos, ensure_ascii=False)}

{f'USER DREAM: "{sueno}"' if sueno else ''}

For each number write 1-2 sentences in {lang_full} based on its source:
- fibonacci: exact position in sequence and formula
- tesla: multiple of 3, Tesla 3-6-9 pattern
- sagrada: golden ratio phi exact value
- primos: prime number properties
- numerologia: step by step reduction of name/date
- lunar: lunar cycle day and significance
- historico: specific frequency in draws, day or month patterns
- derivado: mathematical derivation from historical data
- favorito: user's personal choice
- complement: completes combination by data convergence

Respond ONLY this JSON (no markdown):
{{"narrativas": {{"N": "narrative in {lang_full}"}}}}"""

    try:
        resp=groq_cl.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Only valid JSON. Expert narratives in {lang_full}."},
                {"role":"user","content":prompt}
            ],
            temperature=round(random.uniform(0.7,0.9),2),
            max_tokens=900
        )
        raw=resp.choices[0].message.content.strip()
        if "```" in raw: raw=raw.split("```")[1].replace("json","").strip()
        return json.loads(raw).get("narrativas",{})
    except:
        return {}

# ══════════════════════════════════════════════════════
# GENERAR
# ══════════════════════════════════════════════════════
def generar(loteria, inputs, modulos):
    lang=st.session_state["idioma"]
    mn,mx=loteria["min"],loteria["max"]

    excluir=[]
    if inputs.get("excluir"):
        try: excluir=[int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    pools=construir_pools(loteria,inputs,modulos)
    elegidos=seleccionar(loteria,pools,modulos,excluir)
    nums=[e["n"] for e in elegidos]

    # Bonus
    bonus=None
    if loteria["bonus"]:
        pool_b=[c["n"] for c in pools["historico"] if 1<=c["n"]<=loteria["bmax"] and c["n"] not in nums]
        if not pool_b: pool_b=[n for n in range(1,loteria["bmax"]+1) if n not in nums]
        bonus=pool_b[0] if pool_b else random.randint(1,loteria["bmax"])

    # Calcular convergencia para cada numero
    hist=HIST.get(loteria["nombre"],{})
    fibs=set(get_fibonacci(mn,mx).keys())
    teslas=set(get_tesla(mn,mx).keys())
    sagradas=set(get_sagrada(mn,mx).keys())
    primos=set(get_primos(mn,mx).keys())
    hist_top=set(hist.get("top",[])[:10])
    derivados=set(get_derivados(mn,mx,loteria["nombre"]).keys())

    narrativas=pedir_narrativas(elegidos,loteria,inputs,lang)

    AUTO={
        "fibonacci":   lambda n,m: f"Number {n} belongs to the Fibonacci sequence. {m}",
        "tesla":       lambda n,m: f"Number {n} is a multiple of 3 — Tesla 3·6·9 pattern. {m}",
        "sagrada":     lambda n,m: f"Number {n} follows the golden ratio phi. {m}",
        "primos":      lambda n,m: f"Number {n} is prime — indivisible in mathematics.",
        "numerologia": lambda n,m: f"Your name or date reduces numerologically to {n}. {m}",
        "lunar":       lambda n,m: f"Moon is on day {n} of its current cycle.",
        "historico":   lambda n,m: f"Number {n} is among the most frequent in this lottery. {m}",
        "derivado":    lambda n,m: f"Number {n} derived mathematically from historical data. {m}",
        "favorito":    lambda n,m: f"Number {n} is your favourite — included by your choice.",
        "complement":  lambda n,m: f"Number {n} completes the combination by data convergence.",
    }

    sources=[]
    for e in elegidos:
        n=e["n"]; fuente=e["fuente"]; math_txt=e["math"]
        expl=narrativas.get(str(n),narrativas.get(n,""))
        if not expl:
            fn=AUTO.get(fuente,lambda n,m:f"Number {n} selected.")
            expl=fn(n,math_txt)
        # Traducir si no es ingles
        if lang!="EN":
            math_txt=tr(math_txt)
            expl=tr(expl)
        # Convergencia
        senales=contar_senales(n,fibs,teslas,sagradas,primos,hist_top,derivados)
        sources.append({"number":n,"source":fuente,"math":math_txt,"explanation":expl,"senales":senales})

    if bonus:
        sources.append({"number":bonus,"source":"historico","math":"","explanation":tr(f"Bonus {loteria.get('bname','')}."),"senales":0})

    h=st.session_state.get("historial",[]); h.append(nums); st.session_state["historial"]=h[-5:]
    return {"numbers":nums,"bonus":bonus,"sources":sources}

# ══════════════════════════════════════════════════════
# PDF
# ══════════════════════════════════════════════════════
def generar_pdf(res, loteria):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        buffer=io.BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter,topMargin=0.5*inch,bottomMargin=0.5*inch)
        styles=getSampleStyleSheet()
        story=[]

        gold=colors.HexColor('#C9A84C')
        dark=colors.HexColor('#07070f')

        title_style=ParagraphStyle('title',parent=styles['Title'],
            textColor=gold,fontSize=28,spaceAfter=4)
        sub_style=ParagraphStyle('sub',parent=styles['Normal'],
            textColor=colors.HexColor('#666666'),fontSize=10,spaceAfter=20)
        label_style=ParagraphStyle('label',parent=styles['Normal'],
            textColor=gold,fontSize=9,fontName='Courier',spaceAfter=4)
        body_style=ParagraphStyle('body',parent=styles['Normal'],
            textColor=colors.HexColor('#333333'),fontSize=11,spaceAfter=8)

        story.append(Paragraph("◆ LuckSort", title_style))
        story.append(Paragraph("Sort Your Luck — lucksort.com", sub_style))
        story.append(Paragraph(f"{loteria['flag']} {loteria['nombre'].upper()}", label_style))

        nums=res.get("numbers",[]); bonus=res.get("bonus")
        nums_str=" · ".join([str(n).zfill(2) for n in nums])
        bonus_str=f"  ◆ {str(bonus).zfill(2)}" if bonus else ""
        story.append(Paragraph(f"<b>{nums_str}{bonus_str}</b>",
            ParagraphStyle('nums',parent=styles['Normal'],fontSize=22,
            textColor=gold,fontName='Courier-Bold',spaceAfter=16)))

        story.append(Paragraph("WHERE EACH NUMBER COMES FROM", label_style))
        story.append(Spacer(1,8))

        for s in res.get("sources",[]):
            if s.get("source")=="historico" and not s.get("math"): continue
            src_label=s.get("source","").upper()
            math_txt=s.get("math","")
            expl=s.get("explanation","")
            num=str(s.get("number","")).zfill(2)
            data=[[Paragraph(f"<b>{src_label}</b>",label_style),
                   Paragraph(f"→ {num}",ParagraphStyle('num',parent=styles['Normal'],
                   textColor=gold,fontName='Courier-Bold',fontSize=16))],
                  [Paragraph(math_txt,ParagraphStyle('math',parent=styles['Normal'],
                   textColor=colors.HexColor('#888888'),fontSize=9,fontName='Courier')),""],
                  [Paragraph(expl,body_style),""],
                  [Spacer(1,4),""]
                 ]
            t=Table(data,colWidths=[5*inch,1*inch])
            t.setStyle(TableStyle([
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LINEABOVE',(0,0),(-1,0),0.5,colors.HexColor('#E8E4D9')),
                ('TOPPADDING',(0,0),(-1,-1),6),
            ]))
            story.append(t)

        story.append(Spacer(1,16))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            ParagraphStyle('footer',parent=styles['Normal'],
            textColor=colors.HexColor('#AAAAAA'),fontSize=8)))
        story.append(Paragraph("LuckSort — lucksort.com",
            ParagraphStyle('footer2',parent=styles['Normal'],
            textColor=gold,fontSize=8)))

        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return None

# ══════════════════════════════════════════════════════
# MAPA DE CALOR
# ══════════════════════════════════════════════════════
def render_heatmap(loteria_nombre):
    hist=HIST.get(loteria_nombre,{})
    lot=next((l for l in LOTERIAS if l["nombre"]==loteria_nombre),None)
    if not lot: return
    mn,mx=lot["min"],lot["max"]
    freq=hist.get("freq",{})
    top=hist.get("top",[])
    hot=hist.get("cal",[])
    max_freq=max(freq.values()) if freq else 1

    cells=""
    for n in range(mn,mx+1):
        f=freq.get(n,0)
        ratio=f/max_freq if max_freq>0 else 0
        if n in hot[:3] and n in top[:5]:   heat=5
        elif n in hot:                        heat=4
        elif n in top[:5]:                    heat=3
        elif n in top:                        heat=2
        elif ratio>0.5:                       heat=1
        else:                                 heat=0

        colors_map={
            0:"rgba(255,255,255,.04)",
            1:"rgba(201,168,76,.1)",
            2:"rgba(201,168,76,.22)",
            3:"rgba(201,168,76,.38)",
            4:"rgba(201,168,76,.58)",
            5:"linear-gradient(135deg,#C9A84C,#F5D878)"
        }
        bg=colors_map[heat]
        text_color="#07070f" if heat==5 else ("#C9A84C" if heat>=3 else "rgba(255,255,255,.3)")
        shadow=f"box-shadow:0 0 {heat*4}px rgba(201,168,76,{heat*0.12});" if heat>0 else ""
        anim="animation:heatPulse 2s ease-in-out infinite;" if heat==5 else ""
        cells+=f'<div title="{n} — {f}x" style="aspect-ratio:1;border-radius:5px;background:{bg};display:flex;align-items:center;justify-content:center;font-family:DM Mono,monospace;font-size:9px;font-weight:700;color:{text_color};cursor:pointer;transition:transform .15s;{shadow}{anim}">{str(n).zfill(2)}</div>'

    sorteos=hist.get("sorteos",0); years=hist.get("years","")
    top_num=top[0] if top else 0; top_freq=freq.get(top_num,0)

    st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.12);border-radius:16px;padding:16px;">
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.5);letter-spacing:2px;">⊞ HEAT MAP · {loteria_nombre.upper()}</div>
<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(255,255,255,.2);">{years}</div>
</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
<span style="font-family:DM Mono,monospace;font-size:8px;color:rgba(255,255,255,.2);">COLD</span>
<div style="display:flex;gap:3px;">
<div style="width:14px;height:8px;border-radius:2px;background:rgba(255,255,255,.04)"></div>
<div style="width:14px;height:8px;border-radius:2px;background:rgba(201,168,76,.1)"></div>
<div style="width:14px;height:8px;border-radius:2px;background:rgba(201,168,76,.22)"></div>
<div style="width:14px;height:8px;border-radius:2px;background:rgba(201,168,76,.38)"></div>
<div style="width:14px;height:8px;border-radius:2px;background:rgba(201,168,76,.58)"></div>
<div style="width:14px;height:8px;border-radius:2px;background:linear-gradient(135deg,#C9A84C,#F5D878)"></div>
</div>
<span style="font-family:DM Mono,monospace;font-size:8px;color:rgba(255,255,255,.2);">HOT</span>
</div>
<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:3px;margin-bottom:12px;">{cells}</div>
<div style="display:flex;gap:8px;">
<div style="flex:1;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.08);border-radius:8px;padding:8px;text-align:center;">
<div style="font-family:DM Mono,monospace;font-size:16px;font-weight:700;color:#C9A84C;">{str(top_num).zfill(2)}</div>
<div style="font-family:DM Mono,monospace;font-size:7px;color:rgba(255,255,255,.25);letter-spacing:1px;">TOP NUMBER</div>
</div>
<div style="flex:1;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.08);border-radius:8px;padding:8px;text-align:center;">
<div style="font-family:DM Mono,monospace;font-size:16px;font-weight:700;color:#C9A84C;">{top_freq}</div>
<div style="font-family:DM Mono,monospace;font-size:7px;color:rgba(255,255,255,.25);letter-spacing:1px;">APPEARANCES</div>
</div>
<div style="flex:1;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.08);border-radius:8px;padding:8px;text-align:center;">
<div style="font-family:DM Mono,monospace;font-size:16px;font-weight:700;color:#C9A84C;">{sorteos:,}</div>
<div style="font-family:DM Mono,monospace;font-size:7px;color:rgba(255,255,255,.25);letter-spacing:1px;">DRAWS</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# SUPABASE AUTH
# ══════════════════════════════════════════════════════
def db_registrar(email, pw):
    try:
        if sb.table("usuarios").select("email").eq("email",email).execute().data:
            return False,"exists"
        sb.table("usuarios").insert({"email":email,"password":pw,"role":"free"}).execute()
        r=sb.table("usuarios").select("*").eq("email",email).execute()
        return (True,r.data[0]) if r.data else (False,"error")
    except Exception as e: return False,str(e)

def db_login(email, pw):
    try:
        r=sb.table("usuarios").select("*").eq("email",email).eq("password",pw).execute()
        return (True,r.data[0]) if r.data else (False,None)
    except: return False,None

# ══════════════════════════════════════════════════════
# RENDER RESULTADO
# ══════════════════════════════════════════════════════
def render_resultado(res, loteria, modulos):
    nums=res.get("numbers",[]); bonus=res.get("bonus"); sources=res.get("sources",[])
    role=st.session_state.get("user_role","free")
    is_pro=role in ["pro","admin"]

    if "math" in modulos:     tema="MATHEMATICAL"; tc="#7B9FCC"
    elif "holistic" in modulos: tema="HOLISTIC";   tc="#9B8FCC"
    else:                     tema="REAL DATA";     tc="#C9A84C"

    balls="".join([f'<div class="ball">{str(n).zfill(2)}</div>' for n in nums])
    if bonus: balls+=f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    bonus_lbl=f'<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.2);text-align:center;margin-top:4px;">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>' if bonus and loteria.get("bname") else ""

    st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.18);border-radius:18px;padding:20px;text-align:center;animation:fadeUp .5s ease;margin-bottom:16px;">
<div style="font-family:DM Mono,monospace;font-size:9px;color:{tc};letter-spacing:3px;margin-bottom:8px;">{loteria['flag']} {loteria['nombre'].upper()} · {tema}</div>
<div style="display:flex;flex-wrap:wrap;justify-content:center;">{balls}</div>{bonus_lbl}
</div>""", unsafe_allow_html=True)

    if sources:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.35);letter-spacing:3px;margin:16px 0 10px;">{tr("WHERE EACH NUMBER COMES FROM")}</div>', unsafe_allow_html=True)
        for s in sources:
            if s.get("source")=="historico" and not s.get("math"): continue
            fuente=s.get("source","complement")
            icon=ICONS.get(fuente,"·")
            label=fuente.upper()
            math_t=s.get("math","")
            expl=s.get("explanation","")
            num=s.get("number","")
            senales=s.get("senales",0)
            is_conv=senales>=3 and is_pro
            cls="src-card convergence" if is_conv else "src-card"
            conv_badge=f'<div class="badge-conv">◆ HIGH CONVERGENCE · {senales} SIGNALS</div>' if is_conv else ""
            st.markdown(f"""<div class="{cls}">
<div style="display:flex;align-items:flex-start;gap:12px;flex:1;">
<span class="src-icon">{icon}</span>
<div>{conv_badge}
<div class="src-label">{label}</div>
<div class="src-math">{math_t}</div>
<div class="src-exp">{expl}</div></div></div>
<div class="src-num">→ {str(num).zfill(2)}</div></div>""", unsafe_allow_html=True)

    st.markdown(f'<div style="font-style:italic;font-size:12px;color:rgba(232,228,217,.22);text-align:center;padding:14px 8px;">"{tr("The world has patterns. Numbers hold them. We find them.")}"</div>', unsafe_allow_html=True)

    nums_str=" · ".join([str(n).zfill(2) for n in nums])
    bonus_str=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    st.code(f"LuckSort {loteria['nombre']}: {nums_str}{bonus_str}\nlucksort.com",language=None)

    # PDF download
    if is_pro:
        pdf=generar_pdf(res,loteria)
        if pdf:
            st.download_button(
                label="⬇ Download PDF",
                data=pdf,
                file_name=f"lucksort_{loteria['nombre'].lower().replace(' ','_')}_{date.today()}.pdf",
                mime="application/pdf",
                key="pdf_btn"
            )

# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="padding:14px 0 8px;text-align:center;">
<div style="font-family:'Playfair Display',serif;font-size:18px;color:#C9A84C;font-weight:700;">◆ LuckSort</div>
<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(201,168,76,.3);letter-spacing:2px;margin-top:2px;">SORT YOUR LUCK</div>
</div>""", unsafe_allow_html=True)
    st.markdown('<hr class="g">', unsafe_allow_html=True)

    if not st.session_state["logged_in"]:
        tab_li,tab_re=st.tabs([tr("Sign In"),tr("Create Account")])
        with tab_li:
            em=st.text_input(tr("Email"),key="si_em")
            pw=st.text_input(tr("Password"),type="password",key="si_pw")
            if st.button(tr("Sign In"),key="btn_si"):
                if em==ADMIN_EMAIL and pw==ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":em,"user_id":None}); st.rerun()
                else:
                    ok,d=db_login(em,pw)
                    if ok: st.session_state.update({"logged_in":True,"user_role":d.get("role","free"),"user_email":d["email"],"user_id":d.get("id")}); st.rerun()
                    else: st.error(tr("Incorrect email or password"))
        with tab_re:
            re_em=st.text_input(tr("Email"),key="re_em")
            re_pw=st.text_input(tr("Password"),type="password",key="re_pw")
            re_pw2=st.text_input(tr("Confirm password"),type="password",key="re_pw2")
            if st.button(tr("Create Free Account"),key="btn_re"):
                if re_pw!=re_pw2: st.error(tr("Passwords do not match"))
                elif re_em and len(re_pw)>=6:
                    ok,res=db_registrar(re_em,re_pw)
                    if ok: st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_em,"user_id":res.get("id")}); st.rerun()
                    elif res=="exists": st.error(tr("This email is already registered"))
                    else: st.error(f"Error: {res}")
    else:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.55);text-align:center;margin-bottom:6px;">{st.session_state["user_email"]}</div>', unsafe_allow_html=True)
        role=st.session_state["user_role"]
        role_color={"admin":"#C9A84C","pro":"#7B9FCC","basic":"#9B8FCC","free":"rgba(255,255,255,.3)"}.get(role,"rgba(255,255,255,.3)")
        st.markdown(f'<div style="text-align:center;margin-bottom:8px;"><span style="font-family:DM Mono,monospace;font-size:10px;border:1px solid {role_color};padding:3px 10px;border-radius:20px;color:{role_color};">{role.upper()}</span></div>', unsafe_allow_html=True)
        if st.button(tr("Sign Out"),key="btn_lo"):
            for k,v in DEFAULTS.items(): st.session_state[k]=v
            st.rerun()

# ══════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════
lang=st.session_state["idioma"]
col_logo, col_lang = st.columns([4,1])
with col_logo:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;padding:12px 16px 8px;">
<div style="width:34px;height:34px;background:linear-gradient(135deg,#C9A84C,#F0C84A);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#07070f;animation:glow 3s ease-in-out infinite;">◆</div>
<div><div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:white;line-height:1.1;">LuckSort</div>
<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(201,168,76,.4);letter-spacing:2.5px;">SORT YOUR LUCK</div></div></div>""", unsafe_allow_html=True)
with col_lang:
    lang_act = st.session_state["idioma"]
    nuevo_lang = st.selectbox("", ["EN","ES","PT"],
        index=["EN","ES","PT"].index(lang_act), key="sel_lang_top",
        label_visibility="collapsed")
    if nuevo_lang != lang_act:
        st.session_state["idioma"] = nuevo_lang; st.rerun()
st.markdown('<hr class="g" style="margin-top:4px;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# LANDING
# ══════════════════════════════════════════════════════
if not st.session_state["logged_in"]:
    # Hero text
    st.markdown(f"""<div style="text-align:center;padding:24px 16px 16px;">
<div style="display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;background:rgba(201,168,76,.07);border:1px solid rgba(201,168,76,.18);font-family:DM Mono,monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;margin-bottom:18px;">
<span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>DATA CONVERGENCE ENGINE</div>
<h1 style="font-family:'Playfair Display',serif;font-size:clamp(26px,6vw,48px);font-weight:700;line-height:1.1;letter-spacing:-1.5px;color:white;margin-bottom:8px;">{tr("The world has patterns.")}<br><span style="background:linear-gradient(135deg,#C9A84C,#F5D878);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{tr("Numbers hold them.")}</span></h1>
<p style="font-size:15px;color:rgba(232,228,217,.38);max-width:380px;margin:0 auto;">{tr("We find them for you.")}</p>
</div>""", unsafe_allow_html=True)

    # Heat maps - 3 loterias
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.35);letter-spacing:3px;text-align:center;margin-bottom:12px;">{tr("HISTORICAL HEAT MAP — 26 YEARS OF REAL DATA")}</div>', unsafe_allow_html=True)

    tab1,tab2,tab3=st.tabs(["🇺🇸 Powerball","🇺🇸 Mega Millions","🇪🇺 EuroMillions"])
    with tab1: render_heatmap("Powerball")
    with tab2: render_heatmap("Mega Millions")
    with tab3: render_heatmap("EuroMillions")

    st.markdown('<hr class="g">', unsafe_allow_html=True)

    # Balotas preview
    st.markdown(f"""<div style="text-align:center;margin:12px 0 16px;">
<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(255,255,255,.14);letter-spacing:3px;margin-bottom:10px;">LIVE PREVIEW · POWERBALL</div>
<div style="display:flex;justify-content:center;flex-wrap:wrap;margin-bottom:12px;">
<div class="ball" id="pb0">07</div><div class="ball" id="pb1">14</div><div class="ball" id="pb2">23</div>
<div class="ball" id="pb3">34</div><div class="ball" id="pb4">55</div>
<div class="ball ball-gold" id="pb5">12</div></div>
<div style="display:flex;flex-direction:column;gap:5px;max-width:360px;margin:0 auto;">
<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:10px;padding:9px 14px;">
<div style="display:flex;align-items:center;gap:8px;"><span>ϕ</span><div>
<div style="font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">FIBONACCI</div>
<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.5);">F9+F10=34 — position 11 in sequence</div>
</div></div><span style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 34</span></div>
<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:10px;padding:9px 14px;">
<div style="display:flex;align-items:center;gap:8px;"><span>⊞</span><div>
<div style="font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">HISTORIAN</div>
<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.5);">#1 most frequent — appeared 187x (1997-2024)</div>
</div></div><span style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 26</span></div>
<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:10px;padding:9px 14px;">
<div style="display:flex;align-items:center;gap:8px;"><span>∇</span><div>
<div style="font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">DERIVED</div>
<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.5);">ϕ×26=42 — golden ratio of top historical</div>
</div></div><span style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 42</span></div>
</div></div>
<script>
const s=[[7,14,23,34,55],[8,15,22,33,44],[5,12,27,38,52],[3,18,29,41,60],[11,21,32,43,57]];
const g=[12,6,11,8,22,19];let i=0;
setInterval(()=>{{i=(i+1)%s.length;for(let j=0;j<5;j++){{const e=document.getElementById('pb'+j);if(e)e.textContent=String(s[i][j]).padStart(2,'0');}}
const eg=document.getElementById('pb5');if(eg)eg.textContent=String(g[i%g.length]).padStart(2,'0');}},2800);
</script>""", unsafe_allow_html=True)

    st.markdown('<hr class="g">', unsafe_allow_html=True)
    _,cc,_=st.columns([1,2,1])
    with cc:
        st.markdown('<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.14);letter-spacing:1.5px;margin-bottom:10px;">FREE · NO CREDIT CARD · EN / ES / PT</p>', unsafe_allow_html=True)
        tab_r,tab_l=st.tabs([tr("Create Account"),tr("Sign In")])
        with tab_r:
            re_em=st.text_input(tr("Email"),key="lr_em",placeholder="your@email.com")
            re_pw=st.text_input(tr("Password"),key="lr_pw",type="password")
            re_pw2=st.text_input(tr("Confirm password"),key="lr_pw2",type="password")
            if st.button(tr("Create Free Account"),key="lr_btn"):
                if re_pw!=re_pw2: st.error(tr("Passwords do not match"))
                elif re_em and len(re_pw)>=6:
                    ok,res=db_registrar(re_em,re_pw)
                    if ok: st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_em,"user_id":res.get("id")}); st.rerun()
                    elif res=="exists": st.error(tr("This email is already registered"))
                    else: st.error(f"Error: {res}")
        with tab_l:
            le=st.text_input(tr("Email"),key="ll_em",placeholder="your@email.com")
            lp=st.text_input(tr("Password"),key="ll_pw",type="password")
            if st.button(tr("Sign In"),key="ll_btn"):
                if le==ADMIN_EMAIL and lp==ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":le,"user_id":None}); st.rerun()
                else:
                    ok,d=db_login(le,lp)
                    if ok: st.session_state.update({"logged_in":True,"user_role":d.get("role","free"),"user_email":d["email"],"user_id":d.get("id")}); st.rerun()
                    else: st.error(tr("Incorrect email or password"))
    st.stop()

# ══════════════════════════════════════════════════════
# APP PRINCIPAL
# ══════════════════════════════════════════════════════
role=st.session_state["user_role"]
MAX_GEN={"free":2,"basic":9999,"pro":9999,"admin":9999}.get(role,2)
gen_hoy=st.session_state.get("gen_hoy",0)

lot_names=[f"{l['flag']} {l['nombre']}" for l in LOTERIAS]
sel_idx=st.selectbox(tr("Select your lottery"),range(len(lot_names)),
    format_func=lambda i:lot_names[i],key="sel_lot")
loteria=LOTERIAS[sel_idx]; mn,mx=loteria["min"],loteria["max"]

st.markdown(f'<div style="display:inline-block;padding:5px 12px;border-radius:20px;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.12);font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.6);margin-bottom:12px;">⊙ {tr("Next draw")}: {" · ".join(loteria["dias"])} · {loteria["hora"]}</div>', unsafe_allow_html=True)

if role=="free":
    dots="".join([f'<span style="width:8px;height:8px;border-radius:50%;background:{"#C9A84C" if i<gen_hoy else "rgba(255,255,255,.08)"};display:inline-block;margin:0 2px;"></span>' for i in range(MAX_GEN)])
    st.markdown(f'<div style="text-align:center;margin:4px 0 10px;">{dots}<span style="font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.28);margin-left:8px;">{gen_hoy}/{MAX_GEN} {tr("combinations today")}</span></div>', unsafe_allow_html=True)

st.markdown('<hr class="g">', unsafe_allow_html=True)

modulos=[]; inputs={}

# FAVORITOS
favs=st.session_state.get("favoritos",[]); favs_v=[n for n in favs if mn<=n<=mx]
fav_lbl=f'{tr("Favourites")} — {len(favs_v)} sel.' if favs_v else tr("Favourites")
with st.expander(fav_lbl,expanded=False):
    st.caption(tr("Numbers you want to include"))
    sel=st.multiselect(tr("Select favourites"),list(range(mn,mx+1)),default=favs_v,
        format_func=lambda n:str(n).zfill(2),key=f"ms_fav_{loteria['id']}")
    if sorted(sel)!=sorted(favs_v): st.session_state["favoritos"]=sorted(sel); st.rerun()
    if favs_v:
        st.markdown("".join([f'<div class="ball" style="width:38px;height:38px;font-size:13px;display:inline-flex;">{str(n).zfill(2)}</div>' for n in favs_v]),unsafe_allow_html=True)
        if st.button(tr("Clear"),key="btn_clr"): st.session_state["favoritos"]=[]; st.rerun()

# REAL DATA
with st.expander(tr("Real Data"),expanded=True):
    st.caption(tr("Official history + world events"))
    c1,c2=st.columns(2)
    with c1:
        cb_hist=st.checkbox(tr("Official history"),value=True,key="cb_hist")
        cb_efem=st.checkbox(tr("World events"),value=True,key="cb_efem")
    with c2:
        cb_hoy=st.checkbox(tr("Today's date"),value=True,key="cb_hoy")
    if any([cb_hist,cb_efem,cb_hoy]):
        modulos.append("real")
        inputs.update({"use_hist":cb_hist,"use_efem":cb_efem,"use_hoy":cb_hoy})
    inputs["excluir"]=st.text_input(tr("Exclude numbers (e.g. 4, 13)"),placeholder="4, 13",key="ex_inp")

# HOLISTICO
with st.expander(tr("Holistic"),expanded=False):
    st.caption(tr("Numerology · Lunar cycle · Dreams"))
    c1,c2=st.columns(2)
    with c1: inputs["nombre"]=st.text_input(tr("Your full name"),key="h_nm",placeholder="John Smith")
    with c2: inputs["fecha"]=st.text_input(tr("Special date (DD/MM/YY)"),key="h_fe",placeholder="14/03/92")
    inputs["sueno"]=st.text_area(tr("Tell me your dream..."),key="h_dr",height=70,
        placeholder=tr("Tell me your dream..."),label_visibility="collapsed")
    if inputs.get("nombre") or inputs.get("fecha") or inputs.get("sueno"):
        modulos.append("holistic")

# MATEMATICO
with st.expander(tr("Mathematical"),expanded=False):
    st.caption(tr("Fibonacci · Tesla 3-6-9 · Sacred geometry · Primes · Derived numbers"))
    c1,c2=st.columns(2)
    with c1:
        uf=st.checkbox("ϕ Fibonacci",key="cb_fib")
        ut=st.checkbox("⌁ Tesla 3·6·9",key="cb_tes")
        us=st.checkbox("⬡ Sacred Geometry",key="cb_sag")
    with c2:
        up=st.checkbox("∴ Prime Numbers",key="cb_pri")
        ud=st.checkbox("∇ Derived Numbers",key="cb_der")
    if any([uf,ut,us,up,ud]):
        modulos.append("math")
        inputs.update({"use_fib":uf,"use_tes":ut,"use_sag":us,"use_pri":up,"use_der":ud})

# COMUNIDAD — coming soon
with st.expander(f'⊛ {tr("Community")}',expanded=False):
    st.markdown(f'<div style="text-align:center;padding:12px 0;"><span class="soon-badge">COMING SOON</span><p style="font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.25);margin-top:8px;">{tr("Real-time Reddit & TikTok trending numbers")}</p></div>',unsafe_allow_html=True)

st.markdown('<hr class="g">', unsafe_allow_html=True)

# MAPA DE CALOR INTERACTIVO (Pro)
if role in ["pro","admin"]:
    with st.expander(f'⊞ {tr("Interactive Heat Map")} — PRO',expanded=False):
        lot_hm=st.selectbox(tr("Select lottery"),lot_names,key="hm_lot")
        lot_nombre_hm=lot_hm.split(" ",1)[1]
        hist_hm=HIST.get(lot_nombre_hm,{})
        years_str=hist_hm.get("years","2000-2024")
        try:
            yr_start=int(years_str.split("-")[0])
            yr_end=int(years_str.split("-")[1])
        except:
            yr_start=2000; yr_end=2024
        yr_sel=st.slider(
            tr("Filter by year range"),
            min_value=yr_start, max_value=yr_end,
            value=(yr_start, yr_end), key="hm_slider"
        )
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.4);text-align:center;margin-bottom:8px;">{yr_sel[0]} — {yr_sel[1]} · {yr_sel[1]-yr_sel[0]+1} {tr("years of data")}</div>', unsafe_allow_html=True)
        render_heatmap(lot_nombre_hm)

st.markdown('<hr class="g">', unsafe_allow_html=True)

# GENERAR
if gen_hoy>=MAX_GEN and role=="free":
    st.warning(f"{gen_hoy}/{MAX_GEN} {tr('combinations today')}")
    st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.2);border-radius:16px;padding:20px;text-align:center;">
<h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:6px;">◆ LuckSort Basic</h3>
<p style="color:rgba(232,228,217,.45);font-size:13px;margin-bottom:6px;">{tr("Unlimited combinations · All modules")}</p>
<p style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;margin-bottom:12px;">$4.99<span style="font-size:11px;color:rgba(201,168,76,.5);">/mo</span></p>
<a href="{STRIPE_BASIC}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#F0C84A);color:#07070f;font-weight:700;padding:10px 24px;border-radius:12px;text-decoration:none;font-size:14px;margin-bottom:12px;">{tr("Start Basic")}</a>
<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:12px 0;">
<h3 style="font-family:'Playfair Display',serif;color:#7B9FCC;margin-bottom:6px;">◆ LuckSort Pro</h3>
<p style="color:rgba(232,228,217,.45);font-size:13px;margin-bottom:6px;">{tr("Everything in Basic + Heat Map + PDF + High Convergence")}</p>
<p style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#7B9FCC;margin-bottom:12px;">$9.99<span style="font-size:11px;color:rgba(123,159,204,.5);">/mo</span></p>
<a href="{STRIPE_PRO}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#7B9FCC,#9BB8E8);color:#07070f;font-weight:700;padding:10px 24px;border-radius:12px;text-decoration:none;font-size:14px;">{tr("Start Pro")}</a>
</div>""", unsafe_allow_html=True)
else:
    if st.button(tr("Generate Combination"),key="gen_btn"):
        ph=st.empty(); icons=["⊞","⊛","ϕ","◆"]
        steps=[tr("Analyzing historical signals..."),tr("Calculating convergence..."),tr("Applying mathematics..."),tr("Sorting your luck...")]
        for i,step in enumerate(steps):
            ph.markdown(f'<div class="conv-wrap"><div class="conv-ring"></div><div class="conv-icon">{icons[i]}</div><div class="conv-step">{step}</div></div>',unsafe_allow_html=True)
            time.sleep(0.55)
        ph.empty()
        res=generar(loteria,inputs,modulos)
        st.session_state.update({"resultado":res,"loteria_id":loteria["id"],"modulos_usados":modulos,"gen_hoy":gen_hoy+1})
        st.rerun()

if st.session_state.get("resultado") and st.session_state.get("loteria_id"):
    lot_res=next((l for l in LOTERIAS if l["id"]==st.session_state["loteria_id"]),loteria)
    render_resultado(st.session_state["resultado"],lot_res,st.session_state.get("modulos_usados",[]))
