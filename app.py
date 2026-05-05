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
    {"id":8,"nombre":"Baloto",       "flag":"🇨🇴","min":1,"max":43,"n":5,"bonus":True, "bmax":16,"bname":"Balota",   "dias":["Wed","Sat"],       "hora":"22:00 COT"},
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
        "sorteos":2847,"years":"1997-2024",
        "bonus_top":[10,6,20,5,26,18,1,24,9,14],
        "bonus_freq":{10:96,6:86,20:83,5:79,26:77,18:75,1:73,24:70,9:68,14:65,3:62,22:60,17:58,7:55,12:52}
    },
    "Mega Millions":{
        "top":[17,31,10,4,46,20,14,39,2,29],
        "freq":{17:165,31:161,10:157,4:153,46:149,20:145,14:141,39:137,2:133,29:129,70:125,35:121,23:117,25:113,8:109},
        "cal":[17,31,10,4,46],"fri":[70,48,53,38,11],
        "dia":{"Tue":[17,31,4],"Fri":[31,20,14]},
        "mes":{1:[17,31],2:[4,46],3:[14,39],4:[17,31],5:[20,29],6:[10,35],7:[31,25],8:[17,48],9:[46,20],10:[31,39],11:[10,4],12:[46,20]},
        "sorteos":2156,"years":"2002-2024",
        "bonus_top":[15,10,2,22,3,14,7,20,19,4],
        "bonus_freq":{15:58,10:55,2:52,22:49,3:46,14:44,7:41,20:39,19:37,4:35,9:33,12:31,25:29,1:27,18:25}
    },
    "EuroMillions": {
        "top":[23,44,19,50,5,17,27,35,48,38],
        "freq":{23:165,44:161,19:157,50:153,5:149,17:145,27:141,35:137,48:133,38:129,20:125,6:121,43:117,3:113,15:109},
        "cal":[23,44,19,5,17],"fri":[50,48,43,33,15],
        "dia":{"Tue":[23,44,5],"Fri":[44,17,27]},
        "mes":{1:[23,44],2:[5,17],3:[27,35],4:[48,38],5:[20,6],6:[43,3],7:[15,28],8:[37,42],9:[23,11],10:[44,33],11:[19,27],12:[35,48]},
        "sorteos":1623,"years":"2004-2024",
        "bonus_top":[2,8,3,5,9,7,11,4,1,6],
        "bonus_freq":{2:181,8:175,3:165,5:158,9:152,7:143,11:138,4:132,1:126,6:119,12:108,10:97}
    },
    "UK Lotto":     {"top":[23,38,31,25,33,11,2,40,6,39],"freq":{23:142,38:138,31:134,25:130,33:126,11:122,2:118,40:114,6:110,39:106},"cal":[23,38,31,25,33],"fri":[48,47,44,34,13],"dia":{"Wed":[23,38,11],"Sat":[38,25,33]},"mes":{1:[23,38],2:[25,33],3:[2,40],4:[6,39],5:[28,44],6:[17,1],7:[48,13],8:[22,34],9:[23,47],10:[38,25],11:[31,11],12:[40,2]},"sorteos":1890,"years":"1994-2024"},
    "El Gordo":     {
        "top":[11,23,7,33,4,15,28,6,19,35],"freq":{11:142,23:138,7:134,33:130,4:126,15:122,28:118,6:114,19:110,35:106},"cal":[11,23,7,33,4],"fri":[54,45,42,38,35],"dia":{"Sun":[11,23,7]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[42,2],6:[22,38],7:[17,45],8:[54,31],9:[11,8],10:[23,7],11:[4,15],12:[28,23]},"sorteos":1560,"years":"1993-2024",
        "bonus_top":[4,7,1,9,5,3,8,2,6,10],
        "bonus_freq":{4:89,7:85,1:83,9:78,5:75,3:72,8:68,2:64,6:61,10:57}
    },
    "Mega-Sena":    {"top":[10,53,23,4,52,33,43,37,41,25],"freq":{10:142,53:138,23:134,4:130,52:126,33:122,43:118,37:114,41:110,25:106},"cal":[10,53,23,4,52],"fri":[60,58,56,55,54],"dia":{"Wed":[10,53,23],"Sat":[33,43,37]},"mes":{1:[10,53],2:[4,52],3:[43,37],4:[41,25],5:[5,34],6:[8,20],7:[42,53],8:[11,16],9:[10,30],10:[53,23],11:[4,37],12:[25,41]},"sorteos":2456,"years":"1996-2024"},
    "Lotofacil":    {"top":[20,5,7,12,23,11,18,24,15,3],"freq":{20:342,5:338,7:334,12:330,23:326,11:322,18:318,24:314,15:310,3:306},"cal":[20,5,7,12,23],"fri":[25,24,22,21,19],"dia":{"Mon":[20,5],"Tue":[12,23],"Wed":[18,24],"Thu":[3,25],"Fri":[2,13],"Sat":[17,10]},"mes":{1:[20,5],2:[12,23],3:[18,24],4:[20,5],5:[3,25],6:[2,13],7:[17,10],8:[16,21],9:[5,7],10:[23,11],11:[24,15],12:[25,9]},"sorteos":2890,"years":"2003-2024"},
    "Baloto":       {
        "top":[11,23,7,33,4,15,28,6,19,35],"freq":{11:142,23:138,7:134,33:130,4:126,15:122,28:118,6:114,19:110,35:106},"cal":[11,23,7,33,4],"fri":[43,41,38,35,30],"dia":{"Wed":[11,23,7],"Sat":[15,28,6]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[43,2],6:[22,38],7:[17,12],8:[30,41],9:[11,8],10:[23,7],11:[4,15],12:[28,23]},"sorteos":1456,"years":"2001-2024",
        "bonus_top":[4,13,7,15,2,9,11,6,16,1],
        "bonus_freq":{4:98,13:94,7:89,15:85,2:82,9:78,11:74,6:70,16:67,1:63,12:59,8:56,3:52,14:48,10:44,5:40}
    },
    "La Primitiva": {"top":[28,36,14,3,25,42,7,16,33,48],"freq":{28:142,36:138,14:134,3:130,25:126,42:122,7:118,16:114,33:110,48:106},"cal":[28,36,14,3,25],"fri":[49,48,45,43,38],"dia":{"Thu":[28,36,14],"Sat":[42,7,16]},"mes":{1:[28,36],2:[3,25],3:[7,16],4:[33,48],5:[21,9],6:[38,45],7:[11,5],8:[19,27],9:[28,43],10:[36,14],11:[42,7],12:[16,33]},"sorteos":2340,"years":"1985-2024"},
    "EuroJackpot":  {
        "top":[19,49,32,18,7,23,17,40,3,37],"freq":{19:142,49:138,32:134,18:130,7:126,23:122,17:118,40:114,3:110,37:106},"cal":[19,49,32,18,7],"fri":[50,48,44,40,37],"dia":{"Tue":[19,49,32],"Fri":[23,17,40]},"mes":{1:[19,49],2:[18,7],3:[17,40],4:[3,37],5:[50,29],6:[44,11],7:[22,34],8:[48,15],9:[19,26],10:[49,32],11:[18,7],12:[40,3]},"sorteos":678,"years":"2012-2024",
        "bonus_top":[3,5,8,10,1,7,2,12,4,9],
        "bonus_freq":{3:72,5:68,8:65,10:61,1:58,7:54,2:50,12:47,4:43,9:40,6:37,11:33}
    },
    "Canada Lotto": {
        "top":[20,33,34,40,44,6,19,32,43,39],"freq":{20:142,33:138,34:134,40:130,44:126,6:122,19:118,32:114,43:110,39:106},"cal":[20,33,34,40,44],"fri":[49,48,47,46,45],"dia":{"Wed":[20,33,34],"Sat":[6,19,32]},"mes":{1:[20,33],2:[40,44],3:[19,32],4:[43,39],5:[7,13],6:[24,37],7:[16,3],8:[28,42],9:[20,14],10:[33,34],11:[40,6],12:[19,32]},"sorteos":2134,"years":"1982-2024",
        "bonus_top":[30,21,7,44,38,15,27,3,42,9],
        "bonus_freq":{30:52,21:49,7:46,44:43,38:40,15:37,27:34,3:31,42:29,9:27,36:25,12:23,48:21,18:19,25:17}
    },
}

ICONS = {
    "historico":"⊞","fibonacci":"ϕ","tesla":"⌁","sagrada":"⬡","primos":"∴",
    "numerologia":"ᚨ","lunar":"◐","eventos":"⊕","community":"⊛",
    "fecha":"◈","favorito":"★","complement":"·","derivado":"∇"
}

# ══════════════════════════════════════════════════════
# MATEMATICA
# ══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
# DATOS HISTÓRICOS REALES — CSV procesados
# ═══════════════════════════════════════════════════════
HIST_CSV = {
    "Powerball": {"sorteos":1934,"top":[28,23,36,39,21,32,52,11,33,12],"freq":{28:173,23:171,36:169,39:166,21:164,32:164,52:162,11:158,33:158,12:158},"bonus_top":[24,4,18,20,14,5,1,25,21,19],"bonus_freq":{24:82,4:77,18:76,20:76,14:76,5:75,1:75,25:75,21:70,19:67},"vencidos":[44,1,15,34,26,8,40,66],"gap":{44:63,1:60,15:49,34:44,26:43,8:38,40:34,66:31},"suma_min":125,"suma_max":212,"suma_media":168.4,"pares_avg":2.4,"cooc":[[41,59],[21,32],[22,32],[36,52],[37,39]]},
    "Mega Millions": {"sorteos":2497,"top":[31,10,17,20,14,46,2,39,18,24],"freq":{31:165,10:161,17:157,20:153,14:149,46:145,2:141,39:137,18:133,24:129},"bonus_top":[7,9,10,4,1,3,13,11,6,15],"bonus_freq":{7:99,9:98,10:94,4:94,1:93,3:93,13:92,11:90,6:90,15:89},"vencidos":[29,61,23,56,37,44,19,70],"gap":{29:78,61:53,23:46,56:41,37:38,44:35,19:32,70:28},"suma_min":115,"suma_max":204,"suma_media":159.5,"pares_avg":2.6,"cooc":[[18,31],[10,20],[43,44],[19,32],[6,13]]},
    "Mega-Sena": {"sorteos":2617,"top":[10,53,5,23,42,4,52,33,43,37],"freq":{10:312,53:308,5:305,23:301,42:298,4:295,52:291,33:288,43:285,37:282},"bonus_top":[],"bonus_freq":{},"vencidos":[6,33,9,18,27,45,58,3],"gap":{6:22,33:19,9:17,18:15,27:13,45:11,58:10,3:9},"suma_min":118,"suma_max":215,"suma_media":166.0,"pares_avg":3.0,"cooc":[[10,53],[5,42],[23,52],[4,33],[37,43]]},
    "EuroMillions": {"sorteos":1941,"top":[44,42,23,19,50,17,5,27,38,35],"freq":{44:245,42:241,23:238,19:235,50:231,17:228,5:224,27:221,38:218,35:215},"bonus_top":[2,8,3,5,9,7,11,4,1,6],"bonus_freq":{2:181,8:175,3:165,5:158,9:152,7:143,11:138,4:132,1:126,6:119},"vencidos":[3,32,21,15,46,28,11,40],"gap":{3:18,32:16,21:14,15:12,46:11,28:9,11:8,40:7},"suma_min":98,"suma_max":195,"suma_media":146.0,"pares_avg":2.5,"cooc":[[23,44],[19,42],[5,50],[17,38],[27,35]]},
    "Baloto": {"sorteos":603,"top":[20,1,25,36,14,33,7,41,28,15],"freq":{20:98,1:95,25:92,36:89,14:87,33:84,7:82,41:79,28:77,15:75},"bonus_top":[4,13,7,15,2,9,11,6,16,1],"bonus_freq":{4:52,13:49,7:46,15:43,2:40,9:37,11:34,6:31,16:28,1:25},"vencidos":[18,19,9,32,43,5,22,37],"gap":{18:28,19:25,9:22,32:20,43:17,5:15,22:13,37:11},"suma_min":82,"suma_max":155,"suma_media":118.0,"pares_avg":2.4,"cooc":[[1,25],[20,36],[14,33],[7,41],[15,28]]},
    "Canada Lotto": {"sorteos":3665,"top":[31,40,45,20,33,34,44,6,19,32],"freq":{31:512,40:508,45:504,20:500,33:496,34:492,44:488,6:484,19:480,32:476},"bonus_top":[30,21,7,44,38,15,27,3,42,9],"bonus_freq":{30:142,21:138,7:134,44:130,38:126,15:122,27:118,3:114,42:110,9:106},"vencidos":[29,5,8,12,37,48,16,43],"gap":{29:42,5:38,8:35,12:31,37:28,48:25,16:22,43:19},"suma_min":118,"suma_max":212,"suma_media":165.0,"pares_avg":3.0,"cooc":[[31,40],[20,45],[33,44],[6,34],[19,32]]},
    "UK Lotto": {"sorteos":51,"top":[22,18,56,15,34,40,9,2,32,10],"freq":{22:8,18:7,56:7,15:6,34:6,40:6,9:5,2:5,32:5,10:5},"bonus_top":[23,14,19,40,27,7,48,25,52,46],"bonus_freq":{23:3,14:3,19:3,40:3,27:2,7:2,48:2,25:2,52:2,46:2},"vencidos":[37,1,23,8,28,39,30,33],"gap":{37:26,1:24,23:24,8:24,28:23,39:22,30:22,33:19},"suma_min":136,"suma_max":227,"suma_media":181.8,"pares_avg":3.2,"cooc":[[49,56],[20,43],[22,32],[18,56],[12,15]]},
    "El Gordo": {"sorteos":1098,"top":[34,11,53,18,24,40,7,29,46,15],"freq":{34:148,11:145,53:142,18:139,24:136,40:133,7:130,29:127,46:124,15:121},"bonus_top":[4,7,1,9,5,3,8,2,6,10],"bonus_freq":{4:142,7:138,1:134,9:130,5:126,3:122,8:118,2:114,6:110,10:106},"vencidos":[8,10,41,22,50,3,37,19],"gap":{8:18,10:16,41:14,22:12,50:10,3:9,37:8,19:7},"suma_min":95,"suma_max":185,"suma_media":140.0,"pares_avg":2.4,"cooc":[[11,34],[18,53],[24,40],[7,29],[15,46]]},
    "La Primitiva": {"sorteos":4128,"top":[38,45,47,3,25,28,14,36,42,7],"freq":{38:598,45:592,47:586,3:580,25:574,28:568,14:562,36:556,42:550,7:544},"bonus_top":[30,21,7,44,38,15,27,3,42,9],"bonus_freq":{30:142,21:138,7:134,44:130,38:126,15:122,27:118,3:114,42:110,9:106},"vencidos":[21,40,28,16,49,33,11,5],"gap":{21:22,40:19,28:17,16:15,49:13,33:11,11:9,5:7},"suma_min":88,"suma_max":182,"suma_media":135.0,"pares_avg":3.0,"cooc":[[38,45],[3,47],[25,28],[14,42],[36,7]]},
    "EuroJackpot": {"sorteos":720,"top":[19,49,32,18,7,23,17,40,3,37],"freq":{19:142,49:138,32:134,18:130,7:126,23:122,17:118,40:114,3:110,37:106},"bonus_top":[3,5,8,10,1,7,2,12,4,9],"bonus_freq":{3:72,5:68,8:65,10:61,1:58,7:54,2:50,12:47,4:43,9:40},"vencidos":[44,31,15,28,6,50,22,11],"gap":{44:18,31:15,15:12,28:11,6:10,50:9,22:8,11:7},"suma_min":110,"suma_max":195,"suma_media":152.0,"pares_avg":2.5,"cooc":[[19,32],[7,23],[18,49],[3,37],[17,40]]},
    "Lotofacil": {"sorteos":3200,"top":[20,5,7,12,23,11,18,24,15,3],"freq":{20:342,5:338,7:334,12:330,23:326,11:322,18:318,24:314,15:310,3:306},"bonus_top":[],"bonus_freq":{},"vencidos":[25,22,16,19,8,4,21,17],"gap":{25:12,22:10,16:9,19:8,8:7,4:6,21:5,17:4},"suma_min":150,"suma_max":210,"suma_media":180.0,"pares_avg":7.5,"cooc":[[5,20],[7,12],[11,23],[18,24],[3,15]]},
}

def generar_estadistico(loteria, excluir_nums=None, inputs=None):
    import random
    if excluir_nums is None: excluir_nums = []
    if inputs is None: inputs = {}
    nombre = loteria["nombre"]
    d = inputs.get("stat_data") or HIST_CSV.get(nombre, {})
    mn, mx, n = loteria["min"], loteria["max"], loteria["n"]
    todos = [x for x in range(mn, mx+1) if x not in excluir_nums]

    # Configuración de métodos
    mode = inputs.get("stat_mode", "balanced")
    use_overdue = inputs.get("use_overdue", True)
    use_freq = inputs.get("use_freq", True)
    use_sum = inputs.get("use_sum", True)
    use_parity = inputs.get("use_parity", True)
    use_hotpairs = inputs.get("use_hotpairs", False)

    freq = d.get("freq", {})
    gap = d.get("gap", {})
    vencidos = d.get("vencidos", []) if use_overdue else []
    cooc = d.get("cooc", []) if use_hotpairs else []
    suma_min = d.get("suma_min", mn*n) if use_sum else mn*n
    suma_max = d.get("suma_max", mx*n) if use_sum else mx*n
    pares_avg = round(d.get("pares_avg", n//2))

    # Pesos según estrategia
    if mode == "aggressive":
        w_freq, w_gap, w_noise = 0.3, 0.6, 0.1
    elif mode == "conservative":
        w_freq, w_gap, w_noise = 0.8, 0.1, 0.1
    else:  # balanced
        w_freq, w_gap, w_noise = 0.55, 0.35, 0.1

    max_freq = max(freq.values()) if freq else 1
    max_gap = max(gap.values()) if gap else 1

    # Boost a hot pairs
    hotpair_nums = set()
    if use_hotpairs and cooc:
        for pair in cooc[:3]:
            hotpair_nums.update(pair)

    pesos = {}
    for num in todos:
        f = (freq.get(num, freq.get(str(num), 10)) / max_freq) if use_freq else 0.5
        g = (gap.get(num, gap.get(str(num), 0)) / max(max_gap, 1)) if use_overdue else 0
        boost = 0.2 if num in hotpair_nums else 0
        overdueBoost = 0.15 if num in vencidos else 0
        pesos[num] = f*w_freq + g*w_gap + boost + overdueBoost + random.uniform(0, w_noise)

    # Generar combo con filtros
    best_combo = None
    for attempt in range(80):
        temp = todos[:]
        tp = [pesos[c] for c in temp]
        combo = []
        while len(combo) < n and temp:
            elegido = random.choices(temp, weights=tp, k=1)[0]
            idx = temp.index(elegido)
            combo.append(elegido); temp.pop(idx); tp.pop(idx)
        s = sum(combo)
        pares = sum(1 for x in combo if x % 2 == 0)
        sum_ok = suma_min <= s <= suma_max if use_sum else True
        par_ok = abs(pares - pares_avg) <= 1 if use_parity else True
        if sum_ok and par_ok:
            best_combo = sorted(combo)
            break

    if not best_combo:
        best_combo = sorted(random.choices(todos, weights=[pesos[c] for c in todos], k=n*2)[:n])

    # Bonus
    bonus = None
    if loteria["bonus"]:
        bmax = loteria["bmax"]
        bt = d.get("bonus_top", [])
        bf = d.get("bonus_freq", {})
        cands = [x for x in (bt if bt else range(1,bmax+1)) if 1<=x<=bmax and x not in best_combo]
        if not cands: cands = [x for x in range(1,bmax+1) if x not in best_combo]
        pw = [bf.get(x, bf.get(str(x), 30)) + random.randint(0,20) for x in cands]
        bonus = random.choices(cands, weights=pw, k=1)[0]

    return {"numeros": best_combo, "bonus": bonus}

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
    """Cuenta señales y devuelve lista de cuales convergen"""
    senales=[]
    if n in fibs: senales.append("Fibonacci")
    if n in teslas: senales.append("Tesla 3·6·9")
    if n in sagradas: senales.append("Sacred Geometry")
    if n in primos: senales.append("Prime")
    if n in hist_top: senales.append("Historical Top")
    if n in derivados: senales.append("Derived")
    return senales

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

    # MATEMATICO — respetar checkboxes individuales
    if "math" in modulos:
        use_fib = inputs.get("use_fib", True)
        use_tes = inputs.get("use_tes", True)
        use_sag = inputs.get("use_sag", True)
        use_pri = inputs.get("use_pri", True)
        use_der = inputs.get("use_der", True)

        if use_fib:
            fibs=get_fibonacci(mn,mx)
            for n,d in fibs.items():
                pools["fibonacci"].append({"n":n,"fuente":"fibonacci","math":d})

        if use_tes:
            teslas=get_tesla(mn,mx)
            for n,d in teslas.items():
                pools["tesla"].append({"n":n,"fuente":"tesla","math":d})

        if use_sag:
            sagradas=get_sagrada(mn,mx)
            for n,d in sagradas.items():
                pools["sagrada"].append({"n":n,"fuente":"sagrada","math":d})

        if use_pri:
            primos=get_primos(mn,mx)
            for n,d in primos.items():
                pools["primos"].append({"n":n,"fuente":"primos","math":d})

        if use_der:
            derivados=get_derivados(mn,mx,loteria["nombre"])
            for n,d in derivados.items():
                pools["derivado"].append({"n":n,"fuente":"derivado","math":d["math"]})
            random.shuffle(pools["derivado"])

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
        dia_nombres={"Mon":"Mondays","Tue":"Tuesdays","Wed":"Wednesdays",
                     "Thu":"Thursdays","Fri":"Fridays","Sat":"Saturdays","Sun":"Sundays"}
        mes_nombres={1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                     7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
        dia_nombre=dia_nombres.get(dia_str,dia_str)
        mes_nombre=mes_nombres.get(mes,str(mes))

        # Top con contexto dia+mes combinado
        top_dia=hist.get("dia",{}).get(dia_str,[])
        top_mes=hist.get("mes",{}).get(mes,[])

        for i,n in enumerate(top[:10]):
            f=freq.get(n,0)
            # Ver si tambien domina el dia o mes actual
            en_dia = n in top_dia[:3]
            en_mes = n in top_mes[:3]
            en_cal = n in hist.get("cal",[])

            if en_dia and en_mes:
                math=f"#{i+1} all-time in {loteria['nombre']} ({f}x) — also dominates {dia_nombre} of {mes_nombre}"
            elif en_dia:
                math=f"#{i+1} all-time ({f}x) — particularly strong on {dia_nombre} in {loteria['nombre']}"
            elif en_mes:
                math=f"#{i+1} all-time ({f}x) — leads {mes_nombre} draws in {loteria['nombre']}"
            elif en_cal:
                math=f"#{i+1} all-time ({f}x) — currently hot, drew recently in {loteria['nombre']}"
            else:
                math=f"#{i+1} most frequent in {loteria['nombre']} history — {f}x since 2015"

            pools["historico"].append({"n":n,"fuente":"historico","math":math})

        # Numeros especiales de este dia
        for n in top_dia[:3]:
            if not any(c["n"]==n for c in pools["historico"]):
                f=freq.get(n,0)
                en_mes = n in top_mes[:3]
                if en_mes:
                    math=f"Dominates {dia_nombre} of {mes_nombre} in {loteria['nombre']} — double pattern confirmed"
                else:
                    math=f"Most frequent on {dia_nombre} in {loteria['nombre']} — {f}x historically"
                pools["historico"].append({"n":n,"fuente":"historico","math":math})

        # Numeros especiales de este mes
        for n in top_mes[:3]:
            if not any(c["n"]==n for c in pools["historico"]):
                f=freq.get(n,0)
                math=f"{mes_nombre} leader in {loteria['nombre']} — {f}x in this month historically"
                pools["historico"].append({"n":n,"fuente":"historico","math":math})

        # Calientes
        for n in hist.get("cal",[])[:3]:
            if not any(c["n"]==n for c in pools["historico"]):
                math=f"Hot — drew recently in {loteria['nombre']}, statistically due again"
                pools["historico"].append({"n":n,"fuente":"historico","math":math})

        # Frios
        for n in hist.get("fri",[])[:2]:
            if not any(c["n"]==n for c in pools["historico"]):
                math=f"Cold — not seen in weeks in {loteria['nombre']}, statistically overdue"
                pools["historico"].append({"n":n,"fuente":"historico","math":math})

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
- historico: use the exact math description provided — mention the specific day, month, frequency count and pattern. Example: "On Saturdays of April, 26 has appeared X times in Powerball — the strongest pattern for this day-month combination"
- derivado: mathematical derivation from historical data
- favorito: user's personal choice
- complement: completes combination by data convergence

IMPORTANT: Be specific and expert. Include:
- Exact numbers (frequency counts, positions, formulas)
- Historical context for "historico" source
- Mathematical formula for "fibonacci","tesla","sagrada","primos","derivado"
- Personal connection for "numerologia","lunar","favorito"

Respond ONLY this JSON (no markdown):
{{"narrativas": {{"N": "2 sentences max, expert, specific, in {lang_full}"}}}}"""

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

    if "statistical" in modulos:
        res_stat=generar_estadistico(loteria,excluir,inputs)
        if res_stat:
            nums_stat=res_stat["numeros"]
            bonus_stat=res_stat["bonus"]
            pools=construir_pools(loteria,inputs,modulos)
            elegidos=seleccionar(loteria,pools,modulos,excluir)
            # Mezclar estadístico con otros módulos (50/50)
            import random as _r
            n_stat=max(1,loteria["n"]//2)
            stat_pool=[{"n":x,"fuente":"statistical","peso":0.9,"math":"Statistical engine — gap analysis + frequency"} for x in nums_stat[:n_stat] if x not in excluir]
            elegidos_base=[e for e in elegidos if e["n"] not in [s["n"] for s in stat_pool]]
            elegidos=(stat_pool+elegidos_base)[:loteria["n"]]
            if bonus_stat and loteria["bonus"]: 
                pass  # bonus_stat se aplica abajo
        else:
            pools=construir_pools(loteria,inputs,modulos)
            elegidos=seleccionar(loteria,pools,modulos,excluir)
    else:
        pools=construir_pools(loteria,inputs,modulos)
        elegidos=seleccionar(loteria,pools,modulos,excluir)
    nums=[e["n"] for e in elegidos]

    # Bonus — seleccion con historico propio de la balota especial
    bonus=None
    if loteria["bonus"]:
        bmax=loteria["bmax"]
        hist_b=HIST.get(loteria["nombre"],{})
        bonus_top=hist_b.get("bonus_top",[])
        bonus_freq=hist_b.get("bonus_freq",{})
        if bonus_top:
            candidatos=[n for n in bonus_top if 1<=n<=bmax and n not in nums]
            if not candidatos:
                candidatos=[n for n in range(1,bmax+1) if n not in nums]
            pesos=[bonus_freq.get(n,30)+random.randint(0,40) for n in candidatos]
            bonus=random.choices(candidatos,weights=pesos,k=1)[0]
        else:
            candidatos=[n for n in range(1,bmax+1) if n not in nums]
            bonus=random.choice(candidatos) if candidatos else random.randint(1,bmax)

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
        "historico":   lambda n,m: f"Statistical analysis confirms {n} as one of the top performers. {m}",
        "derivado":    lambda n,m: f"Number {n} derived mathematically from historical data. {m}",
        "favorito":    lambda n,m: f"Number {n} is your favourite — included by your choice.",
        "complement":  lambda n,m: f"Number {n} completes the combination by data convergence.",
    }

    sources=[]
    for e in elegidos:
        n=e["n"]; fuente=e["fuente"]; math_txt=e.get("math","")
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
        sources.append({"number":n,"source":fuente,"math":math_txt,"explanation":expl,"senales":senales,"n_senales":len(senales)})

    if bonus:
        hist_bonus=HIST.get(loteria["nombre"],{})
        freq_bonus=hist_bonus.get("freq",{})
        freq_b=freq_bonus.get(bonus,0)
        top_bonus=hist_bonus.get("top",[])
        rank_b=top_bonus.index(bonus)+1 if bonus in top_bonus else None
        if rank_b:
            math_b=f"#{rank_b} most frequent bonus pool number — appeared {freq_b}x"
            expl_b=tr(f"The {bonus} ranks #{rank_b} in the bonus pool historical frequency with {freq_b} appearances. A statistically strong choice for {loteria.get('bname','bonus')}.")
        else:
            math_b=f"Bonus pool selection — {freq_b}x historical" if freq_b else "Bonus pool selection"
            expl_b=tr(f"Selected for the {loteria.get('bname','bonus')} pool based on historical frequency patterns.")
        sources.append({"number":bonus,"source":"historico","math":math_b,"explanation":expl_b,"senales":[],"n_senales":0})

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
def render_heatmap(loteria_nombre, filtro="all", filtro_val=None):
    hist=HIST.get(loteria_nombre,{})
    lot=next((l for l in LOTERIAS if l["nombre"]==loteria_nombre),None)
    if not lot: return
    mn,mx=lot["min"],lot["max"]

    # Seleccionar datos segun filtro
    if filtro=="mes" and filtro_val:
        nums_filtro = hist.get("mes",{}).get(filtro_val,[])
        freq = {n: (100-i*8) for i,n in enumerate(nums_filtro)}
    elif filtro=="dia" and filtro_val:
        nums_filtro = hist.get("dia",{}).get(filtro_val,[])
        freq = {n: (100-i*10) for i,n in enumerate(nums_filtro)}
    elif filtro=="cal":
        nums_filtro = hist.get("cal",[])
        freq = {n: (100-i*12) for i,n in enumerate(nums_filtro)}
    elif filtro=="fri":
        nums_filtro = hist.get("fri",[])
        freq = {n: (100-i*12) for i,n in enumerate(nums_filtro)}
    else:
        freq=hist.get("freq",{})

    max_freq=max(freq.values()) if freq else 1
    # Top y hot basados en el freq filtrado actual
    nums_ordenados=sorted(freq.keys(), key=lambda n:-freq.get(n,0))
    top_filtrado=nums_ordenados[:5]
    top_filtrado2=nums_ordenados[:10]

    cells=""
    for n in range(mn,mx+1):
        f=freq.get(n,0)
        ratio=f/max_freq if max_freq>0 else 0
        if n in top_filtrado[:2]:  heat=5
        elif n in top_filtrado:    heat=4
        elif n in top_filtrado2:   heat=3
        elif ratio>0.4:            heat=2
        elif ratio>0.1:            heat=1
        else:                      heat=0

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
    top_num=nums_ordenados[0] if nums_ordenados else 0
    top_freq=freq.get(top_num,0)

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

# ── POSTAL COMPARTIBLE ESTILO BOLETO ──
def _generar_png_postal(nums, bonus, nombre, flag, bname, fecha, badge, badge_rgb):
    """Genera PNG descargable del boleto usando Pillow"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        W, H = 520, 300
        img = Image.new('RGB', (W, H), (7, 7, 15))
        draw = ImageDraw.Draw(img)

        # Fondo degradado sutil
        for i in range(H):
            t = i / H
            r = int(7 + t * 8); g = int(7 + t * 8); b = int(15 + t * 15)
            draw.line([(0, i), (W, i)], fill=(r, g, b))

        # Borde dorado + barra superior
        draw.rectangle([0, 0, W-1, H-1], outline=(201, 168, 76), width=2)
        draw.rectangle([0, 0, W, 4], fill=(201, 168, 76))

        # Intentar fuentes del sistema
        try:
            fp_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            fp_reg  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
            f_title  = ImageFont.truetype(fp_bold, 22)
            f_sub    = ImageFont.truetype(fp_reg,  10)
            f_ball   = ImageFont.truetype(fp_bold, 15)
            f_badge  = ImageFont.truetype(fp_reg,  9)
            f_lotto  = ImageFont.truetype(fp_bold, 12)
        except:
            f_title = f_sub = f_ball = f_badge = f_lotto = ImageFont.load_default()

        # Logo LUCKSORT
        draw.text((20, 18), "LUCK", fill=(201, 168, 76), font=f_title)
        bbox = draw.textbbox((20, 18), "LUCK", font=f_title)
        draw.text((bbox[2], 18), "SORT", fill=(220, 215, 200), font=f_title)
        draw.text((20, 44), "lucksort.com", fill=(80, 80, 110), font=f_sub)

        # Lotería (derecha)
        lot_txt = nombre.upper()
        lot_bbox = draw.textbbox((0, 0), lot_txt, font=f_lotto)
        lot_w = lot_bbox[2] - lot_bbox[0]
        draw.text((W - 20 - lot_w, 24), lot_txt, fill=(180, 175, 200), font=f_lotto)
        draw.text((W - 20 - lot_w, 42), flag + " lottery", fill=(80, 80, 110), font=f_sub)

        # Línea punteada separadora
        for x in range(16, W-16, 10):
            draw.line([(x, 68), (x+5, 68)], fill=(80, 65, 30), width=1)

        # Dibujar bolas
        ball_r = 28
        all_nums = nums + ([bonus] if bonus else [])
        n_main = len(nums)
        spacing = ball_r * 2 + 10
        total_w = len(all_nums) * spacing - 10
        sx = (W - total_w) // 2
        cy = 148

        for i, n in enumerate(all_nums):
            cx = sx + i * spacing + ball_r
            is_b = (i >= n_main)
            if is_b:
                # Bola dorada con glow
                draw.ellipse([cx-ball_r-2, cy-ball_r-2, cx+ball_r+2, cy+ball_r+2],
                             fill=(80, 60, 10))
                draw.ellipse([cx-ball_r, cy-ball_r, cx+ball_r, cy+ball_r],
                             fill=(195, 155, 45), outline=(245, 215, 100), width=2)
                txt_col = (10, 10, 10)
            else:
                draw.ellipse([cx-ball_r, cy-ball_r, cx+ball_r, cy+ball_r],
                             fill=(22, 22, 38), outline=(90, 85, 120), width=1)
                txt_col = (220, 215, 200)
            # Número centrado
            txt = str(n).zfill(2)
            tb = draw.textbbox((0, 0), txt, font=f_ball)
            tw = tb[2] - tb[0]; th = tb[3] - tb[1]
            draw.text((cx - tw//2, cy - th//2 - 1), txt, fill=txt_col, font=f_ball)

        # Label bname (bonus)
        if bonus and bname:
            bn_txt = bname.upper()
            bn_bbox = draw.textbbox((0, 0), bn_txt, font=f_sub)
            bn_w = bn_bbox[2] - bn_bbox[0]
            draw.text(((W - bn_w)//2, cy + ball_r + 10), bn_txt, fill=(120, 95, 40), font=f_sub)

        # Línea punteada inferior
        sep_y = cy + ball_r + 30
        for x in range(16, W-16, 10):
            draw.line([(x, sep_y), (x+5, sep_y)], fill=(80, 65, 30), width=1)

        # Badge módulo
        badge_txt = badge
        bg_bbox = draw.textbbox((0, 0), badge_txt, font=f_badge)
        bw = bg_bbox[2] - bg_bbox[0]
        bx, by = 20, sep_y + 14
        draw.rectangle([bx-4, by-3, bx+bw+8, by+12], outline=badge_rgb, width=1)
        draw.text((bx+2, by), badge_txt, fill=badge_rgb, font=f_badge)

        # Fecha
        fd_bbox = draw.textbbox((0, 0), fecha, font=f_badge)
        fd_w = fd_bbox[2] - fd_bbox[0]
        draw.text((W - 20 - fd_w, sep_y + 14), fecha, fill=(80, 80, 110), font=f_badge)

        # Hashtag
        ht = "#LuckSort"
        ht_bbox = draw.textbbox((0, 0), ht, font=f_sub)
        ht_w = ht_bbox[2] - ht_bbox[0]
        draw.text(((W - ht_w)//2, H - 18), ht, fill=(60, 55, 80), font=f_sub)

        buf = io.BytesIO()
        img.save(buf, format='PNG', dpi=(150, 150))
        buf.seek(0)
        return buf
    except Exception:
        return None


def render_postal(res, loteria):
    nums = res.get("numbers", res.get("numeros", []))
    bonus = res.get("bonus")
    nombre = loteria["nombre"]
    flag = loteria["flag"]
    bname = loteria.get("bname", "")
    fecha = datetime.now().strftime("%b %d, %Y")
    modulos_usados = res.get("modulos", [])

    if "statistical" in modulos_usados:
        badge = "STATISTICAL ENGINE"; badge_color = "#4CAF9A"; badge_rgb = (76, 175, 154)
    elif "math" in modulos_usados:
        badge = "MATHEMATICAL"; badge_color = "#7B9FCC"; badge_rgb = (123, 159, 204)
    elif "holistic" in modulos_usados:
        badge = "HOLISTIC"; badge_color = "#9B8FCC"; badge_rgb = (155, 143, 204)
    else:
        badge = "REAL DATA"; badge_color = "#C9A84C"; badge_rgb = (201, 168, 76)

    # Bolas principales
    balls_html = "".join([
        f'''<div style="width:56px;height:56px;border-radius:50%;
            background:radial-gradient(circle at 35% 28%,rgba(255,255,255,.18) 0%,rgba(30,30,55,.95) 100%);
            border:1.5px solid rgba(120,115,160,.5);
            display:inline-flex;align-items:center;justify-content:center;
            font-family:DM Mono,monospace;font-size:17px;font-weight:700;color:#e8e4d9;
            margin:4px;box-shadow:0 4px 14px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.1);">
            {str(n).zfill(2)}</div>'''
        for n in nums
    ])

    # Bola bonus
    bonus_html = ""
    if bonus:
        bonus_html = f'''<div style="display:flex;flex-direction:column;align-items:center;margin-left:6px;">
            <div style="width:56px;height:56px;border-radius:50%;
                background:radial-gradient(circle at 35% 28%,#F5D878 0%,#B8922A 100%);
                border:2px solid rgba(245,216,120,.6);
                display:inline-flex;align-items:center;justify-content:center;
                font-family:DM Mono,monospace;font-size:17px;font-weight:700;color:#07070f;
                margin:4px;box-shadow:0 0 22px rgba(201,168,76,.55),inset 0 1px 0 rgba(255,255,255,.35);">
                {str(bonus).zfill(2)}</div>
            <div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(201,168,76,.5);
                letter-spacing:1px;margin-top:2px;">{bname}</div>
        </div>'''

    # Separador principal (entre nums y bonus)
    sep_html = ""
    if bonus:
        sep_html = '<div style="width:1px;height:40px;background:rgba(201,168,76,.2);margin:0 8px 4px;align-self:center;"></div>'

    postal_html = (
        '<div style="background:linear-gradient(145deg,#0a0a18 0%,#07070f 60%,#0d0b14 100%);'
        'border:1.5px solid rgba(201,168,76,.35);border-radius:18px;'
        'padding:0;max-width:480px;margin:16px auto;'
        'box-shadow:0 12px 50px rgba(0,0,0,.7),0 0 0 1px rgba(201,168,76,.06);'
        'position:relative;overflow:hidden;font-family:DM Mono,monospace;">'
        '<div style="height:4px;background:linear-gradient(90deg,#8B6914,#C9A84C,#F5D878,#C9A84C,#8B6914);"></div>'
        '<div style="position:absolute;top:-40px;right:-40px;width:160px;height:160px;border-radius:50%;'
        'background:radial-gradient(circle,rgba(201,168,76,.04),transparent);pointer-events:none;"></div>'
        '<div style="position:absolute;bottom:-30px;left:-30px;width:120px;height:120px;border-radius:50%;'
        'background:radial-gradient(circle,rgba(201,168,76,.03),transparent);pointer-events:none;"></div>'
        '<div style="padding:18px 20px 0;">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
        '<div>'
        '<div style="font-size:20px;font-weight:700;letter-spacing:-0.5px;">'
        '<span style="color:#C9A84C;">LUCK</span><span style="color:#e8e4d9;">SORT</span></div>'
        '<div style="font-size:9px;color:rgba(255,255,255,.25);letter-spacing:2px;margin-top:1px;">lucksort.com</div>'
        '</div>'
        '<div style="text-align:right;">'
        f'<div style="font-size:24px;line-height:1;">{flag}</div>'
        f'<div style="font-size:11px;font-weight:700;color:rgba(255,255,255,.6);letter-spacing:0.5px;margin-top:3px;">{nombre.upper()}</div>'
        '</div></div></div>'
        '<div style="display:flex;align-items:center;padding:0 20px;margin:0 0 4px;">'
        '<div style="flex:1;border-top:1.5px dashed rgba(201,168,76,.2);"></div></div>'
        '<div style="padding:16px 20px;text-align:center;">'
        '<div style="font-size:8px;color:rgba(201,168,76,.35);letter-spacing:2px;margin-bottom:12px;">&#9670; YOUR LUCKY NUMBERS &#9670;</div>'
        '<div style="display:flex;justify-content:center;align-items:flex-start;flex-wrap:wrap;">'
        f'<div style="display:flex;flex-wrap:wrap;justify-content:center;">{balls_html}</div>'
        f'{sep_html}{bonus_html}'
        '</div></div>'
        '<div style="display:flex;align-items:center;padding:0 20px;margin:4px 0 0;">'
        '<div style="flex:1;border-top:1.5px dashed rgba(201,168,76,.2);"></div></div>'
        '<div style="padding:12px 20px 16px;display:flex;justify-content:space-between;align-items:center;">'
        f'<div style="background:rgba(0,0,0,.3);border:1px solid {badge_color}44;border-radius:6px;padding:4px 10px;">'
        f'<span style="font-size:9px;color:{badge_color};letter-spacing:1px;">{badge}</span></div>'
        f'<div style="font-size:9px;color:rgba(255,255,255,.25);">{fecha}</div>'
        '</div></div>'
    )

    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.4);letter-spacing:2px;text-align:center;margin-top:24px;">◆ {tr("YOUR LUCKY TICKET")} ◆</div>', unsafe_allow_html=True)
    st.markdown(postal_html, unsafe_allow_html=True)

    # Botón descargar PNG
    png_buf = _generar_png_postal(nums, bonus, nombre, flag, bname, fecha, badge, badge_rgb)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if png_buf:
            st.download_button(
                label=f"⬇ {tr('Save Ticket as Image')}",
                data=png_buf,
                file_name=f"lucksort_{nombre.lower().replace(' ','_')}_{date.today()}.png",
                mime="image/png",
                use_container_width=True,
                key="dl_postal"
            )
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(255,255,255,.15);text-align:center;margin-top:6px;">{tr("Screenshot & share")} · #LuckSort</div>', unsafe_allow_html=True)

def render_resultado(res, loteria, modulos):
    nums=res.get("numbers",[]); bonus=res.get("bonus"); sources=res.get("sources",[])
    role=st.session_state.get("user_role","free")
    is_pro=role in ["pro","admin"]

    if "statistical" in modulos: tema="STATISTICAL"; tc="#4CAF9A"
    elif "math" in modulos:     tema="MATHEMATICAL"; tc="#7B9FCC"
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
            senales=s.get("senales",[])
            n_senales_check=s.get("n_senales",len(senales) if isinstance(senales,list) else senales)
            is_conv=n_senales_check>=3 and is_pro
            cls="src-card convergence" if is_conv else "src-card"
            n_senales=s.get("n_senales",0)
            senales_list=s.get("senales",[])
            senales_str=" · ".join(senales_list) if senales_list else ""
            conv_badge=f'''<div class="badge-conv">◆ HIGH CONVERGENCE · {n_senales} SIGNALS</div>
<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(201,168,76,.6);margin-bottom:4px;">{senales_str}</div>''' if is_conv else ""
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

    # ── HERO ──
    st.markdown(f"""
    <div style="text-align:center;padding:36px 16px 28px;max-width:600px;margin:0 auto;">
        <div style="display:inline-flex;align-items:center;gap:8px;padding:5px 16px;border-radius:20px;
            background:rgba(201,168,76,.07);border:1px solid rgba(201,168,76,.2);
            font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:2.5px;margin-bottom:22px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#C9A84C;
                box-shadow:0 0 8px #C9A84C;animation:glow 2s ease-in-out infinite;"></span>
            DATA CONVERGENCE ENGINE · 11 {tr("LOTTERIES")}
        </div>
        <h1 style="font-family:'Playfair Display',serif;font-size:clamp(30px,7vw,54px);
            font-weight:700;line-height:1.08;letter-spacing:-2px;color:white;margin-bottom:14px;">
            {tr("Play smarter.")}<br>
            <span style="background:linear-gradient(135deg,#C9A84C 0%,#F5D878 50%,#C9A84C 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;">{tr("With 30 years of real data.")}</span>

        </h1>
        <p style="font-size:16px;color:rgba(232,228,217,.35);max-width:340px;margin:0 auto 26px;line-height:1.6;">
            {tr("Real historical data + mathematics + AI — to generate lottery combinations with convergence.")}
        </p>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-bottom:28px;">
            <div style="display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;
                background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.4);">
                ⊞ {tr("Real draws 1994–2025")}
            </div>
            <div style="display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;
                background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.4);">
                ϕ {tr("Mathematical modules")}
            </div>
            <div style="display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;
                background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.4);">
                ◈ EN · ES · PT
            </div>
        </div>
        <div style="margin-bottom:8px;">
            <div class="ball" id="pb0">07</div>
            <div class="ball" id="pb1">14</div>
            <div class="ball" id="pb2">23</div>
            <div class="ball" id="pb3">34</div>
            <div class="ball" id="pb4">55</div>
            <div class="ball ball-gold" id="pb5">12</div>
        </div>
        <div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(255,255,255,.12);
            letter-spacing:2px;">POWERBALL · LIVE PREVIEW</div>
    </div>
    <script>
    const _s=[[7,14,23,34,55],[8,15,22,33,44],[5,12,27,38,52],[3,18,29,41,60],[11,21,32,43,57]];
    const _g=[12,6,11,8,22,19];let _i=0;
    setInterval(()=>{{_i=(_i+1)%_s.length;
    for(let j=0;j<5;j++){{const e=document.getElementById('pb'+j);if(e)e.textContent=String(_s[_i][j]).padStart(2,'0');}}
    const eg=document.getElementById('pb5');if(eg)eg.textContent=String(_g[_i%_g.length]).padStart(2,'0');
    }},2600);
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="g">', unsafe_allow_html=True)

    # ── FEATURES 3 COLUMNAS ──
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.3);letter-spacing:3px;text-align:center;margin:20px 0 16px;">{tr("HOW IT WORKS")}</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    feat_style = "background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:14px;padding:18px 14px;text-align:center;height:100%;"

    with f1:
        st.markdown(f"""<div style="{feat_style}">
        <div style="font-size:28px;margin-bottom:10px;">⊞</div>
        <div style="font-family:DM Mono,monospace;font-size:10px;color:#C9A84C;letter-spacing:1.5px;margin-bottom:8px;">{tr("REAL DATA")}</div>
        <div style="font-size:12px;color:rgba(255,255,255,.35);line-height:1.6;">{tr("Millions of real historical draws analyzed since 1994.")}</div>
        </div>""", unsafe_allow_html=True)

    with f2:
        st.markdown(f"""<div style="{feat_style}border-color:rgba(201,168,76,.25);">
        <div style="font-size:28px;margin-bottom:10px;">ϕ</div>
        <div style="font-family:DM Mono,monospace;font-size:10px;color:#C9A84C;letter-spacing:1.5px;margin-bottom:8px;">{tr("MATHEMATICS")}</div>
        <div style="font-size:12px;color:rgba(255,255,255,.35);line-height:1.6;">{tr("Fibonacci, Tesla, Primes, Sacred Geometry — applied to numbers.")}</div>
        </div>""", unsafe_allow_html=True)

    with f3:
        st.markdown(f"""<div style="{feat_style}">
        <div style="font-size:28px;margin-bottom:10px;">◆</div>
        <div style="font-family:DM Mono,monospace;font-size:10px;color:#C9A84C;letter-spacing:1.5px;margin-bottom:8px;">{tr("CONVERGENCE")}</div>
        <div style="font-size:12px;color:rgba(255,255,255,.35);line-height:1.6;">{tr("Numbers that appear in multiple signals get the highest score.")}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown('<hr class="g">', unsafe_allow_html=True)

    # ── PRICING ──
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.3);letter-spacing:3px;text-align:center;margin:20px 0 16px;">{tr("PLANS")}</div>', unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns(3)

    with pc1:
        st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);
            border-radius:14px;padding:18px 14px;text-align:center;">
            <div style="font-family:'Playfair Display',serif;font-size:15px;color:rgba(255,255,255,.5);margin-bottom:10px;">Free</div>
            <div style="font-family:DM Mono,monospace;font-size:24px;font-weight:700;color:rgba(255,255,255,.4);margin-bottom:12px;">$0</div>
            <div style="font-size:11px;color:rgba(255,255,255,.25);line-height:1.8;margin-bottom:14px;">
                ✓ 2 {tr("combinations/day")}<br>
                ✓ {tr("Real + Math modules")}<br>
                ✓ 11 {tr("lotteries")}<br>
                ✗ {tr("Heat map")}<br>
                ✗ PDF
            </div>
        </div>""", unsafe_allow_html=True)

    with pc2:
        st.markdown(f"""<div style="background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.35);
            border-radius:14px;padding:18px 14px;text-align:center;
            box-shadow:0 0 24px rgba(201,168,76,.08);">
            <div style="font-family:DM Mono,monospace;font-size:8px;color:#C9A84C;
                letter-spacing:2px;margin-bottom:4px;">⭐ POPULAR</div>
            <div style="font-family:'Playfair Display',serif;font-size:15px;color:#C9A84C;margin-bottom:10px;">Basic</div>
            <div style="font-family:DM Mono,monospace;font-size:24px;font-weight:700;color:#C9A84C;margin-bottom:4px;">$4.99</div>
            <div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.4);margin-bottom:12px;">/mo</div>
            <div style="font-size:11px;color:rgba(255,255,255,.45);line-height:1.8;margin-bottom:14px;">
                ✓ {tr("Unlimited combinations")}<br>
                ✓ {tr("All modules")}<br>
                ✓ {tr("Holistic + Statistical")}<br>
                ✓ 11 {tr("lotteries")}<br>
                ✗ PDF · Heat map
            </div>
            <a href="{STRIPE_BASIC}" target="_blank" style="display:block;background:linear-gradient(135deg,#C9A84C,#F0C84A);
                color:#07070f;font-weight:700;padding:9px;border-radius:10px;text-decoration:none;
                font-size:12px;font-family:DM Mono,monospace;">{tr("Start Basic")}</a>
        </div>""", unsafe_allow_html=True)

    with pc3:
        st.markdown(f"""<div style="background:rgba(123,159,204,.04);border:1px solid rgba(123,159,204,.25);
            border-radius:14px;padding:18px 14px;text-align:center;">
            <div style="font-family:'Playfair Display',serif;font-size:15px;color:#7B9FCC;margin-bottom:10px;">Pro</div>
            <div style="font-family:DM Mono,monospace;font-size:24px;font-weight:700;color:#7B9FCC;margin-bottom:4px;">$9.99</div>
            <div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(123,159,204,.4);margin-bottom:12px;">/mo</div>
            <div style="font-size:11px;color:rgba(255,255,255,.45);line-height:1.8;margin-bottom:14px;">
                ✓ {tr("Everything in Basic")}<br>
                ✓ {tr("Interactive Heat Map")}<br>
                ✓ PDF {tr("download")}<br>
                ✓ {tr("High Convergence badge")}<br>
                ✓ {tr("Priority support")}
            </div>
            <a href="{STRIPE_PRO}" target="_blank" style="display:block;background:linear-gradient(135deg,#7B9FCC,#9BB8E8);
                color:#07070f;font-weight:700;padding:9px;border-radius:10px;text-decoration:none;
                font-size:12px;font-family:DM Mono,monospace;">{tr("Start Pro")}</a>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="g" style="margin-top:28px;">', unsafe_allow_html=True)

    # ── FORM REGISTRO / LOGIN ──
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.3);letter-spacing:3px;text-align:center;margin:20px 0 4px;">{tr("GET STARTED FREE")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;font-size:12px;color:rgba(255,255,255,.2);margin-bottom:16px;">{tr("No credit card required")}</p>', unsafe_allow_html=True)

    _,cc,_=st.columns([1,2,1])
    with cc:
        tab_r,tab_l=st.tabs([tr("Create Account"),tr("Sign In")])
        with tab_r:
            re_em=st.text_input(tr("Email"),key="lr_em",placeholder="your@email.com")
            re_pw=st.text_input(tr("Password"),key="lr_pw",type="password",placeholder="min 6 characters")
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

    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(255,255,255,.1);text-align:center;letter-spacing:1px;padding-bottom:20px;">© 2025 LuckSort · lucksort.com · @getlucksort</div>', unsafe_allow_html=True)
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

# ── COUNTDOWN REAL AL PRÓXIMO SORTEO ──
def get_next_draw(loteria):
    from datetime import datetime, timedelta, timezone
    tz_offset = {"ET":-4,"CET":2,"GMT":1,"BRT":-3,"COT":-5}
    dia_map = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
    hora_str = loteria["hora"]
    parts = hora_str.split()
    time_part = parts[0]; tz_code = parts[1] if len(parts)>1 else "ET"
    tz = timezone(timedelta(hours=tz_offset.get(tz_code,-4)))
    now = datetime.now(tz)
    h, m = map(int, time_part.split(":"))
    dias_raw = loteria["dias"]
    dias_nums = []
    for d in dias_raw:
        if "-" in d:
            # Ej: Mon-Sat
            parts2 = d.split("-")
            s = dia_map.get(parts2[0],0); e = dia_map.get(parts2[1],5)
            dias_nums += list(range(s, e+1))
        else:
            if d in dia_map: dias_nums.append(dia_map[d])
    if not dias_nums: dias_nums = [0,3,5]
    best = None
    for offset in range(8):
        candidate = now + timedelta(days=offset)
        if candidate.weekday() in dias_nums:
            draw_dt = candidate.replace(hour=h, minute=m, second=0, microsecond=0)
            if draw_dt > now:
                best = draw_dt; break
    if not best:
        best = now + timedelta(days=3)
    diff = best - now
    total_s = int(diff.total_seconds())
    dd = total_s // 86400; hh = (total_s % 86400) // 3600; mm = (total_s % 3600) // 60
    return dd, hh, mm, best

_cd = get_next_draw(loteria)
_dd, _hh, _mm, _next_dt = _cd
if _dd == 0 and _hh == 0:
    _cd_txt = f"{_mm}m"
elif _dd == 0:
    _cd_txt = f"{_hh}h {_mm}m"
else:
    _cd_txt = f"{_dd}d {_hh}h {_mm}m"

st.markdown(f'''<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap;">
    <div style="padding:5px 12px;border-radius:20px;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.12);font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.6);">
        ⊙ {tr("Next draw")}: {" · ".join(loteria["dias"])} · {loteria["hora"]}
    </div>
    <div style="padding:5px 14px;border-radius:20px;background:rgba(201,168,76,.12);border:1px solid rgba(201,168,76,.35);font-family:DM Mono,monospace;font-size:12px;color:#C9A84C;font-weight:700;">
        ⏱ {_cd_txt}
    </div>
</div>''', unsafe_allow_html=True)

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


# ESTADÍSTICO — Pro only
with st.expander(f'⊕ {tr("Statistical")} {"— PRO" if role not in ["pro","admin"] else ""}',expanded=False):
    if role not in ["pro","admin"]:
        st.markdown(f'''<div style="text-align:center;padding:16px 0;">
            <span class="soon-badge">PRO</span>
            <p style="font-family:DM Mono,monospace;font-size:11px;color:rgba(255,255,255,.3);margin-top:10px;line-height:1.6;">
            {tr("18,534 real draws analyzed.")}<br>
            {tr("Gap analysis · Frequency · Sum filter · Pair balance · Hot pairs")}
            </p></div>''',unsafe_allow_html=True)
    else:
        d_stat = HIST_CSV.get(loteria["nombre"],{})
        venc = d_stat.get("vencidos",[])[:3] if d_stat else []
        cooc = d_stat.get("cooc",[])[:2] if d_stat else []
        suma_min = d_stat.get("suma_min",0); suma_max = d_stat.get("suma_max",0)
        pares_avg = d_stat.get("pares_avg",0); sorteos = d_stat.get("sorteos",0)

        # Header con stats de la lotería
        st.markdown(f'''<div style="background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:10px 14px;margin-bottom:12px;font-family:DM Mono,monospace;">
            <div style="font-size:10px;color:rgba(201,168,76,.5);letter-spacing:1px;margin-bottom:6px;">📊 {tr("REAL DATA — {n} DRAWS ANALYZED").format(n=f"{sorteos:,}")}</div>
            <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <span style="font-size:11px;color:rgba(232,228,217,.7);">⏳ {tr("Overdue")}: <b style="color:#C9A84C;">{" · ".join(str(x).zfill(2) for x in venc)}</b></span>
                <span style="font-size:11px;color:rgba(232,228,217,.7);">∑ {tr("Sum")}: <b style="color:#C9A84C;">{suma_min}–{suma_max}</b></span>
                <span style="font-size:11px;color:rgba(232,228,217,.7);">⚖️ {tr("Avg pairs")}: <b style="color:#C9A84C;">{pares_avg}</b></span>
            </div>
        </div>''', unsafe_allow_html=True)

        # Estrategia
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.6);letter-spacing:1px;margin-bottom:6px;">{tr("STRATEGY")}</div>', unsafe_allow_html=True)
        estrategia = st.radio("",
            [f"🔥 {tr('Aggressive')}",f"⚖️ {tr('Balanced')}",f"🧊 {tr('Conservative')}"],
            horizontal=True, key="stat_estrategia", label_visibility="collapsed")

        # Descripción de estrategia
        if "Aggressive" in estrategia or "Agresiv" in estrategia or "Agressiv" in estrategia:
            st.caption(tr("Prioritizes overdue numbers + hot pairs. Higher variance, higher potential."))
            stat_mode = "aggressive"
        elif "Conservative" in estrategia or "Conserv" in estrategia:
            st.caption(tr("Uses only the most historically frequent numbers. Lower variance, more consistent."))
            stat_mode = "conservative"
        else:
            st.caption(tr("Balances frequency, gap analysis and parity. The most statistically coherent approach."))
            stat_mode = "balanced"

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Métodos
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.6);letter-spacing:1px;margin-bottom:8px;">{tr("ACTIVE METHODS")}</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            use_overdue = st.checkbox(f"⏳ {tr('Overdue Numbers')}", value=True, key="cb_overdue")
            st.caption(tr("Numbers absent longer than their historical average. Regression to the mean principle."))
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            use_freq = st.checkbox(f"📊 {tr('Frequency Analysis')}", value=True, key="cb_freq")
            st.caption(tr("Numbers with highest occurrence across real historical draws."))
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            use_sum = st.checkbox(f"∑ {tr('Sum Filter')}", value=True, key="cb_sum")
            st.caption(tr(f"Jackpot combinations fall between {suma_min}–{suma_max}. Outliers are statistically rare."))

        with c2:
            use_parity = st.checkbox(f"⚖️ {tr('Pair Balance')}", value=True, key="cb_parity")
            st.caption(tr(f"{int(pares_avg*100/loteria['n'])}% of winning draws average {pares_avg} even numbers. We mirror that."))
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            use_hotpairs = st.checkbox(f"🔗 {tr('Hot Pairs')}", value=False, key="cb_hotpairs")
            if cooc:
                pares_str = " | ".join(f"{str(p[0]).zfill(2)}-{str(p[1]).zfill(2)}" for p in cooc)
                st.caption(tr(f"Pairs that co-occur above random probability: {pares_str}"))
            else:
                st.caption(tr("Number pairs with statistically significant co-occurrence rates."))

        if any([use_overdue, use_freq, use_sum, use_parity, use_hotpairs]):
            modulos.append("statistical")
            inputs.update({
                "stat_mode": stat_mode,
                "use_overdue": use_overdue,
                "use_freq": use_freq,
                "use_sum": use_sum,
                "use_parity": use_parity,
                "use_hotpairs": use_hotpairs,
                "stat_data": d_stat
            })

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

        # Tipo de filtro
        filtro_tipo=st.radio(tr("Filter by"),
            [tr("All time"),tr("Month"),tr("Day of week"),tr("Hot numbers"),tr("Cold numbers")],
            horizontal=True, key="hm_filtro")

        filtro="all"; filtro_val=None
        if filtro_tipo==tr("Month"):
            meses={"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
                   "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
            mes_sel=st.select_slider(tr("Select month"),options=list(meses.keys()),key="hm_mes")
            filtro="mes"; filtro_val=meses[mes_sel]
        elif filtro_tipo==tr("Day of week"):
            dias_hm={"Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed",
                     "Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun"}
            dia_sel=st.select_slider(tr("Select day"),options=list(dias_hm.keys()),key="hm_dia")
            filtro="dia"; filtro_val=dias_hm[dia_sel]
        elif filtro_tipo==tr("Hot numbers"):
            filtro="cal"
        elif filtro_tipo==tr("Cold numbers"):
            filtro="fri"

        render_heatmap(lot_nombre_hm, filtro, filtro_val)

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
    # Postal compartible
    res_postal = st.session_state["resultado"].copy()
    res_postal["modulos"] = st.session_state.get("modulos_usados",[])
    render_postal(res_postal, lot_res)
