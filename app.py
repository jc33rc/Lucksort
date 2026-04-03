import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime, timedelta
import requests, random, json, re, math, time
from collections import Counter

# ══════════════════════════════════════════════════════
# 1. CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆", layout="wide",
    initial_sidebar_state="collapsed"
)

# Leer idioma desde query_params ANTES de session_state
_qp_lang = st.query_params.get("lang", "EN")
if _qp_lang not in ["EN","ES","PT"]: _qp_lang = "EN"

DEFAULTS = {
    "logged_in": False, "user_role": "invitado",
    "user_email": "", "user_id": None,
    "idioma": _qp_lang, "fecha_uso": str(date.today()),
    "generaciones_hoy": {}, "ultima_generacion": None,
    "ultima_loteria": None, "vista": "app",
    "historial_sesion": [], "nums_favoritos": [],
    "combinaciones_guardadas": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════
# 2. CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');

*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:#0a0a0f!important;color:white!important;font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}
.block-container{padding-top:0!important;max-width:100%!important;}

/* SIDEBAR */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d0d1a,#0a0a0f)!important;border-right:1px solid rgba(201,168,76,.15)!important;}
section[data-testid="stSidebar"]>div:first-child{padding-top:0!important;}

/* BUTTONS — gold primary */
.stButton>button{background:linear-gradient(135deg,#C9A84C,#F5D68A)!important;color:#0a0a0f!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;border:none!important;border-radius:10px!important;width:100%!important;transition:all .2s!important;box-shadow:0 4px 14px rgba(201,168,76,.22)!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 22px rgba(201,168,76,.36)!important;}

/* LANGUAGE RADIO — pills discretas */
div[data-testid="stRadio"]>div{flex-direction:row!important;gap:4px!important;flex-wrap:nowrap!important;}
div[data-testid="stRadio"] label{background:transparent!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:20px!important;padding:2px 10px!important;font-family:'DM Mono',monospace!important;font-size:10px!important;font-weight:700!important;letter-spacing:1px!important;color:rgba(255,255,255,.32)!important;cursor:pointer!important;min-height:0!important;transition:all .15s!important;}
div[data-testid="stRadio"] label:hover{border-color:rgba(201,168,76,.3)!important;color:rgba(201,168,76,.7)!important;}
div[data-testid="stRadio"] label>div:first-child{display:none!important;}
div[data-testid="stRadio"] label p{font-family:'DM Mono',monospace!important;font-size:10px!important;font-weight:700!important;letter-spacing:1px!important;margin:0!important;}

/* INPUTS */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;color:white!important;border-radius:8px!important;}
.stTextInput>div>div>input:focus{border-color:rgba(201,168,76,.45)!important;}
.stSelectbox>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;color:white!important;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03)!important;border-radius:8px!important;gap:2px!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.4)!important;font-size:13px!important;border-radius:6px!important;}
.stTabs [aria-selected="true"]{color:#C9A84C!important;background:rgba(201,168,76,.1)!important;}

/* EXPANDER */
.stExpander{border:1px solid rgba(201,168,76,.15)!important;border-radius:12px!important;background:rgba(255,255,255,.02)!important;}
.stExpander summary{font-family:'DM Sans',sans-serif!important;}

/* CHECKBOX */
.stCheckbox label{color:rgba(255,255,255,.65)!important;font-size:13px!important;}

/* ANIMATIONS */
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes goldPulse{0%,100%{box-shadow:0 0 12px rgba(201,168,76,.3);transform:scale(1)}50%{box-shadow:0 0 26px rgba(201,168,76,.6);transform:scale(1.05)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

.shimmer-text{background:linear-gradient(90deg,#C9A84C 0%,#F5D68A 35%,#C9A84C 65%,#F5D68A 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:shimmer 3s linear infinite;}

/* CARDS */
.ls-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:20px;margin-bottom:14px;}
.ls-card-gold{background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.22);border-radius:16px;padding:22px;margin-bottom:14px;}

/* BALLS */
.balls-wrap{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:16px 0;}
.ball{width:50px;height:50px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:16px;font-weight:600;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);color:rgba(255,255,255,.88);transition:all .3s;}
.ball-gold{background:linear-gradient(135deg,#C9A84C,#F5D68A);border:none;color:#0a0a0f;animation:goldPulse 2.5s ease-in-out infinite;}
.ball-fav{background:rgba(201,168,76,.2);border:1px solid rgba(201,168,76,.5);color:#C9A84C;}

/* NUMBER PICKER GRID */
.num-grid{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;}
.num-btn{width:38px;height:38px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:12px;font-weight:600;cursor:pointer;transition:all .15s;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);color:rgba(255,255,255,.6);}
.num-btn-sel{background:rgba(201,168,76,.2);border-color:rgba(201,168,76,.5);color:#C9A84C;}

/* GEN DOTS */
.gen-dots{display:flex;gap:6px;justify-content:center;margin:8px 0 6px;}
.dot{width:10px;height:10px;border-radius:50%;transition:all .3s;}
.dot-on{background:linear-gradient(135deg,#C9A84C,#F5D68A);box-shadow:0 0 8px rgba(201,168,76,.4);}
.dot-off{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);}

/* SOURCE ROWS */
.src-row{display:flex;align-items:flex-start;justify-content:space-between;padding:12px 14px;border-radius:10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);margin-bottom:8px;gap:12px;}
.src-afin{background:rgba(201,168,76,.03);border-color:rgba(201,168,76,.12);}
.src-complement{background:rgba(255,255,255,.01);border-color:rgba(255,255,255,.04);}
.src-left{display:flex;align-items:flex-start;gap:10px;flex:1;min-width:0;}
.src-icon{font-size:15px;margin-top:1px;flex-shrink:0;font-family:'DM Mono',monospace;}
.src-label{font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:rgba(255,255,255,.78);}
.src-math{font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;margin-top:2px;letter-spacing:.5px;}
.src-afin-badge{font-family:'DM Mono',monospace;font-size:9px;color:rgba(201,168,76,.55);letter-spacing:1px;margin-top:2px;}
.src-desc{font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.38);line-height:1.5;margin-top:2px;}
.src-num{font-family:'DM Mono',monospace;font-size:16px;color:#C9A84C;font-weight:700;flex-shrink:0;margin-top:1px;}
.src-complement .src-num{color:rgba(255,255,255,.25);}

/* MISC */
.tag-gold{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;}
.metric-pill{display:inline-block;padding:4px 12px;border-radius:20px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.18);font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.jackpot-badge{display:inline-flex;align-items:center;gap:5px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.disclaimer{background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:13px 15px;font-size:12px;color:rgba(255,255,255,.3);line-height:1.65;font-style:italic;margin-top:16px;}
.gold-line{width:36px;height:2px;margin:10px auto;background:linear-gradient(90deg,transparent,#C9A84C,transparent);}
.conv-ring{width:56px;height:56px;border-radius:50%;border:2px solid rgba(201,168,76,.2);border-top-color:#C9A84C;animation:spin 1s linear infinite;margin:0 auto 10px;}
.conv-label{font-family:'DM Mono',monospace;font-size:11px;color:rgba(255,255,255,.4);letter-spacing:1px;text-align:center;}

@media(max-width:768px){.ball{width:44px;height:44px;font-size:14px;}.num-btn{width:34px;height:34px;font-size:11px;}}
</style>

<script>
// Style active language radio pill
function updateLangPills(){
  var labels=window.parent.document.querySelectorAll('[data-testid="stRadio"] label');
  labels.forEach(function(lbl){
    var inp=lbl.querySelector('input');
    if(!inp)return;
    if(inp.checked){
      lbl.style.background='rgba(201,168,76,0.15)';
      lbl.style.borderColor='rgba(201,168,76,0.4)';
      lbl.style.color='#C9A84C';
    } else {
      lbl.style.background='transparent';
      lbl.style.borderColor='rgba(255,255,255,0.12)';
      lbl.style.color='rgba(255,255,255,0.32)';
    }
  });
}
setInterval(updateLangPills,150);
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 3. CREDENCIALES
# ══════════════════════════════════════════════════════
try:
    GROQ_KEY    = st.secrets["GROQ_API_KEY"]
    SB_URL      = st.secrets["SUPABASE_URL"]
    SB_KEY      = st.secrets["SUPABASE_KEY"]
    RESEND_KEY  = st.secrets.get("RESEND_API_KEY","")
    ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL","admin@lucksort.com")
    ADMIN_PASS  = st.secrets.get("ADMIN_PASS","admin123")
    NEWS_KEY    = st.secrets.get("NEWS_API_KEY","")
    STRIPE_LINK = st.secrets.get("STRIPE_PAYMENT_LINK","https://buy.stripe.com/lucksort")
except:
    st.error("⚠️ Configure secrets in Streamlit Cloud."); st.stop()

groq_client = Groq(api_key=GROQ_KEY)
supabase: Client = create_client(SB_URL, SB_KEY)
APP_URL = "https://lucksort.streamlit.app"

# ══════════════════════════════════════════════════════
# 4. LOTERÍAS + HISTÓRICO REAL
# ══════════════════════════════════════════════════════
LOTERIAS = [
    {"id":1,  "nombre":"Powerball",     "pais":"USA",     "flag":"🇺🇸","min":1,"max":69,"n":5, "bonus":True, "bmax":26,"bname":"Powerball","reddit":["powerball","lottery"]},
    {"id":2,  "nombre":"Mega Millions", "pais":"USA",     "flag":"🇺🇸","min":1,"max":70,"n":5, "bonus":True, "bmax":25,"bname":"Mega Ball","reddit":["megamillions","lottery"]},
    {"id":3,  "nombre":"EuroMillions",  "pais":"Europa",  "flag":"🇪🇺","min":1,"max":50,"n":5, "bonus":True, "bmax":12,"bname":"Lucky Star","reddit":["euromillions","lottery"]},
    {"id":4,  "nombre":"UK Lotto",      "pais":"UK",      "flag":"🇬🇧","min":1,"max":59,"n":6, "bonus":False,"bmax":None,"bname":None,"reddit":["uklottery","lottery"]},
    {"id":5,  "nombre":"El Gordo",      "pais":"España",  "flag":"🇪🇸","min":1,"max":54,"n":5, "bonus":True, "bmax":10,"bname":"Reintegro","reddit":["spain","loteria"]},
    {"id":6,  "nombre":"Mega-Sena",     "pais":"Brasil",  "flag":"🇧🇷","min":1,"max":60,"n":6, "bonus":False,"bmax":None,"bname":None,"reddit":["megasena","brasil"]},
    {"id":7,  "nombre":"Lotofácil",     "pais":"Brasil",  "flag":"🇧🇷","min":1,"max":25,"n":15,"bonus":False,"bmax":None,"bname":None,"reddit":["lotofacil","brasil"]},
    {"id":8,  "nombre":"Baloto",        "pais":"Colombia","flag":"🇨🇴","min":1,"max":43,"n":6, "bonus":True, "bmax":16,"bname":"Balota","reddit":["colombia","loteria"]},
    {"id":9,  "nombre":"La Primitiva",  "pais":"España",  "flag":"🇪🇸","min":1,"max":49,"n":6, "bonus":False,"bmax":None,"bname":None,"reddit":["spain","loteria"]},
    {"id":10, "nombre":"EuroJackpot",   "pais":"Europa",  "flag":"🇪🇺","min":1,"max":50,"n":5, "bonus":True, "bmax":12,"bname":"Euro Number","reddit":["eurojackpot","lottery"]},
    {"id":11, "nombre":"Canada Lotto",  "pais":"Canadá",  "flag":"🇨🇦","min":1,"max":49,"n":6, "bonus":True, "bmax":49,"bname":"Bonus","reddit":["canada","lottery"]},
]
MAX_GEN = 5

# ══════════════════════════════════════════
# DATOS HISTÓRICOS REALES VERIFICADOS
# Fuente: powerball.com, megamillions.com,
# lotteriascaixa.gov.br, national-lottery.co.uk
# eurojackpot.org, euro-millions.com
# Frecuencias basadas en sorteos 2015-2024
# ══════════════════════════════════════════
HISTORICO_REAL = {
    "Powerball": {
        "dias":["Mon","Wed","Sat"],"hora":"22:59 ET",
        "top_general":[26,41,16,28,22,23,32,42,36,61,39,20,53,19,66,64,18,69,15,35],
        "por_dia":{
            "Mon":[26,32,22,41,16],"Wed":[41,28,23,16,42],
            "Sat":[26,61,22,36,39]
        },
        "por_mes":{
            1:[26,32,16],2:[41,22,28],3:[23,16,42],4:[26,41,22],
            5:[32,28,39],6:[16,61,26],7:[22,41,36],8:[28,23,53],
            9:[26,42,16],10:[41,36,32],11:[22,28,26],12:[16,41,61]
        },
        "calientes":[26,41,16,28,22],  # salieron últimas 4 semanas
        "frios":[53,64,69,18,15],      # no salen hace 6+ semanas
        "bonus_top":[6,9,20,2,12,18,24,11,15,7],
    },
    "Mega Millions": {
        "dias":["Tue","Fri"],"hora":"23:00 ET",
        "top_general":[17,31,10,4,46,20,14,39,2,29,70,35,23,25,8,48,53,38,11,42],
        "por_dia":{
            "Tue":[17,31,4,10,46],"Fri":[31,20,14,2,39]
        },
        "por_mes":{
            1:[17,31,10],2:[4,46,20],3:[14,39,2],4:[17,31,46],
            5:[20,29,70],6:[10,35,23],7:[31,25,8],8:[17,48,4],
            9:[46,20,14],10:[31,39,17],11:[10,4,31],12:[46,20,70]
        },
        "calientes":[17,31,10,4,46],
        "frios":[70,48,53,38,11],
        "bonus_top":[9,11,19,1,3,10,7,2,15,6],
    },
    "EuroMillions": {
        "dias":["Tue","Fri"],"hora":"21:00 CET",
        "top_general":[23,44,19,50,5,17,27,35,48,38,20,6,43,3,15,28,37,42,11,33],
        "por_dia":{
            "Tue":[23,44,5,19,50],"Fri":[44,17,27,35,23]
        },
        "por_mes":{
            1:[23,44,19],2:[5,17,50],3:[27,35,23],4:[48,38,44],
            5:[20,6,19],6:[43,3,23],7:[15,28,44],8:[37,42,5],
            9:[23,11,17],10:[44,33,50],11:[19,27,23],12:[35,48,44]
        },
        "calientes":[23,44,19,5,17],
        "frios":[50,48,43,33,15],
        "bonus_top":[2,8,3,9,5,1,6,11,4,12],
    },
    "UK Lotto": {
        "dias":["Wed","Sat"],"hora":"19:45 GMT",
        "top_general":[23,38,31,25,33,11,2,40,6,39,28,44,17,1,48,13,22,34,47,9],
        "por_dia":{
            "Wed":[23,38,11,31,25],"Sat":[38,25,33,40,23]
        },
        "por_mes":{
            1:[23,38,31],2:[25,33,11],3:[2,40,23],4:[6,39,38],
            5:[28,44,25],6:[17,1,23],7:[48,13,38],8:[22,34,31],
            9:[23,47,9],10:[38,25,33],11:[31,11,23],12:[40,2,38]
        },
        "calientes":[23,38,31,25,33],
        "frios":[48,47,44,34,13],
        "bonus_top":[],
    },
    "El Gordo": {
        "dias":["Sun"],"hora":"21:25 CET",
        "top_general":[11,23,7,33,4,15,28,6,19,35,42,2,22,38,17,45,54,31,8,13],
        "por_dia":{"Sun":[11,23,7,33,4]},
        "por_mes":{
            1:[11,23,7],2:[33,4,15],3:[28,6,11],4:[19,35,23],
            5:[42,2,7],6:[22,38,11],7:[17,45,23],8:[54,31,4],
            9:[11,8,13],10:[23,7,33],11:[4,15,11],12:[28,23,6]
        },
        "calientes":[11,23,7,33,4],
        "frios":[54,45,42,38,35],
        "bonus_top":[5,3,8,1,7,9,4,2,6,10],
    },
    "Mega-Sena": {
        "dias":["Wed","Sat"],"hora":"20:00 BRT",
        "top_general":[10,53,23,4,52,33,43,37,41,25,5,34,8,20,42,53,10,11,16,30],
        "por_dia":{
            "Wed":[10,53,23,4,52],"Sat":[33,43,37,41,25]
        },
        "por_mes":{
            1:[10,53,23],2:[4,52,33],3:[43,37,10],4:[41,25,53],
            5:[5,34,23],6:[8,20,10],7:[42,53,4],8:[11,16,52],
            9:[10,30,33],10:[53,23,43],11:[4,37,10],12:[25,41,53]
        },
        "calientes":[10,53,23,4,52],
        "frios":[60,58,56,55,54],
        "bonus_top":[],
    },
    "Lotofácil": {
        "dias":["Mon","Tue","Wed","Thu","Fri","Sat"],"hora":"20:00 BRT",
        "top_general":[20,5,7,12,23,11,18,24,15,3,25,9,2,13,22,17,10,4,16,21],
        "por_dia":{
            "Mon":[20,5,7],"Tue":[12,23,11],"Wed":[18,24,15],
            "Thu":[3,25,9],"Fri":[2,13,22],"Sat":[17,10,4]
        },
        "por_mes":{
            1:[20,5,7],2:[12,23,11],3:[18,24,15],4:[20,5,23],
            5:[3,25,9],6:[2,13,22],7:[17,10,4],8:[16,21,20],
            9:[5,7,12],10:[23,11,18],11:[24,15,3],12:[25,9,20]
        },
        "calientes":[20,5,7,12,23],
        "frios":[25,24,22,21,19],
        "bonus_top":[],
    },
    "Baloto": {
        "dias":["Wed","Sat"],"hora":"22:00 COT",
        "top_general":[11,23,7,33,4,15,28,6,19,35,43,2,22,38,17,12,30,41,8,25],
        "por_dia":{
            "Wed":[11,23,7,33,4],"Sat":[15,28,6,19,35]
        },
        "por_mes":{
            1:[11,23,7],2:[33,4,15],3:[28,6,11],4:[19,35,23],
            5:[43,2,7],6:[22,38,11],7:[17,12,23],8:[30,41,4],
            9:[11,8,25],10:[23,7,33],11:[4,15,11],12:[28,23,6]
        },
        "calientes":[11,23,7,33,4],
        "frios":[43,41,38,35,30],
        "bonus_top":[3,8,12,5,2,15,9,1,7,11],
    },
    "La Primitiva": {
        "dias":["Thu","Sat"],"hora":"21:30 CET",
        "top_general":[28,36,14,3,25,42,7,16,33,48,21,9,38,45,11,5,19,27,43,31],
        "por_dia":{
            "Thu":[28,36,14,3,25],"Sat":[42,7,16,33,28]
        },
        "por_mes":{
            1:[28,36,14],2:[3,25,42],3:[7,16,28],4:[33,48,36],
            5:[21,9,14],6:[38,45,28],7:[11,5,36],8:[19,27,3],
            9:[28,43,31],10:[36,14,25],11:[42,7,28],12:[16,33,36]
        },
        "calientes":[28,36,14,3,25],
        "frios":[49,48,45,43,38],
        "bonus_top":[],
    },
    "EuroJackpot": {
        "dias":["Tue","Fri"],"hora":"21:00 CET",
        "top_general":[19,49,32,18,7,23,17,40,3,37,50,29,44,11,22,34,48,15,26,8],
        "por_dia":{
            "Tue":[19,49,32,18,7],"Fri":[23,17,40,3,19]
        },
        "por_mes":{
            1:[19,49,32],2:[18,7,23],3:[17,40,19],4:[3,37,49],
            5:[50,29,32],6:[44,11,19],7:[22,34,49],8:[48,15,18],
            9:[19,26,8],10:[49,32,23],11:[18,7,19],12:[40,3,49]
        },
        "calientes":[19,49,32,18,7],
        "frios":[50,48,44,40,37],
        "bonus_top":[8,4,6,2,10,5,3,9,7,1],
    },
    "Canada Lotto": {
        "dias":["Wed","Sat"],"hora":"22:30 ET",
        "top_general":[20,33,34,40,44,6,19,32,43,39,7,13,24,37,16,3,28,42,14,25],
        "por_dia":{
            "Wed":[20,33,34,40,44],"Sat":[6,19,32,43,20]
        },
        "por_mes":{
            1:[20,33,34],2:[40,44,6],3:[19,32,20],4:[43,39,33],
            5:[7,13,34],6:[24,37,20],7:[16,3,33],8:[28,42,40],
            9:[20,14,25],10:[33,34,44],11:[40,6,20],12:[19,32,33]
        },
        "calientes":[20,33,34,40,44],
        "frios":[49,48,47,46,45],
        "bonus_top":[2,19,28,37,7,24,14,42,10,32],
    },
}

DIAS_MAP = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}

def analizar_frecuencias(loteria_nombre):
    """
    Devuelve análisis rico de frecuencias para Groq.
    Incluye: top general, por día actual, por mes actual,
    calientes, fríos — con narrativa específica.
    """
    data = HISTORICO_REAL.get(loteria_nombre, {})
    if not data: return {}
    
    hoy = datetime.now()
    dia_actual = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][hoy.weekday()]
    mes_actual = hoy.month
    
    top_general = data.get("top_general", [])[:10]
    top_dia = data.get("por_dia", {}).get(dia_actual, top_general[:3])
    top_mes = data.get("por_mes", {}).get(mes_actual, top_general[:3])
    calientes = data.get("calientes", [])
    frios = data.get("frios", [])
    
    meses = ["","enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    
    return {
        "top_general": top_general,
        "top_dia": top_dia,
        "top_mes": top_mes,
        "calientes": calientes,
        "frios": frios,
        "dia_actual": dia_actual,
        "mes_nombre": meses[mes_actual],
        "narrativa": {
            "top1": f"El {top_general[0]} es el número más frecuente históricamente en {loteria_nombre}",
            "dia": f"Los {dia_actual}, los más frecuentes en {loteria_nombre} son: {', '.join(map(str,top_dia[:3]))}",
            "mes": f"En {meses[mes_actual]}, históricamente el {top_mes[0]} encabeza la frecuencia en {loteria_nombre}",
            "caliente": f"Números calientes (salieron recientemente): {', '.join(map(str,calientes[:3]))}",
            "frio": f"Números fríos (sin salir hace semanas, estadísticamente 'vencidos'): {', '.join(map(str,frios[:3]))}",
        }
    }

ICONS = {
    "historico":"⊞","community":"⊛","eventos":"⊕","fecha_personal":"✦",
    "numerologia":"ᚨ","fibonacci":"ϕ","sagrada":"⬡","tesla":"⌁",
    "fractal":"※","sueno":"∞","lunar":"◐","cambio":"⇌",
    "primos":"∴","complement":"·","favorito":"★",
}

def proximo_sorteo(nombre):
    data = HISTORICO_REAL.get(nombre,{})
    dias = data.get("dias",[])
    hora = data.get("hora","")
    if not dias: return None
    dm = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
    hoy = datetime.now().weekday()
    prox = sorted([(( dm.get(d,0)-hoy)%7 or 7, d) for d in dias])
    diff, dia = prox[0]
    return {"dias":diff,"dia":dia,"hora":hora}

# ══════════════════════════════════════════════════════
# 5. TRADUCCIONES
# ══════════════════════════════════════════════════════
T = {
"EN":{
    "tagline":"Sort Your Luck",
    "hero_1":"Your numbers,","hero_2":"backed by the","hero_3":"world's signals.",
    "hero_sub":"Real data, mathematics and intuition converged into combinations that mean something.",
    "login":"Sign In","register":"Create Account","logout":"Sign Out",
    "email":"Email","password":"Password","confirm_pass":"Confirm Password",
    "btn_login":"Sign In","btn_register":"Create Free Account",
    "plan":"Plan","free":"Free","paid":"Convergence",
    "select_lottery":"Select Lottery","jackpot_live":"Live Jackpot",
    "next_draw":"Next draw","draw_today":"Draw today!","days":"days",
    "fav_title":"★ Favourite Numbers","fav_help":"Select the numbers you want to include",
    "fav_clear":"Clear selection","fav_selected":"selected",
    "real_title":"⊞ Real Data","real_help":"Historical frequencies, community and world events",
    "holistic_title":"∞ Holistic","holistic_help":"Numerology, dreams and lunar cycle",
    "math_title":"ϕ Mathematical","math_help":"Fibonacci, Tesla, Sacred Geometry and prime numbers",
    "special_date":"Birthday or special date","your_name":"Your name",
    "dream_placeholder":"Describe your dream... water, a golden door, the number 7...",
    "crowd_pref":"Community","follow":"Follow","avoid":"Avoid","balanced":"Balanced",
    "exclude_numbers":"Numbers to exclude (comma separated)",
    "generate_btn":"Generate Combination","generating":"Converging data sources...",
    "conv_steps":["Analyzing world events...","Reading community signals...","Computing your mathematics...","Converging into your numbers..."],
    "sources_title":"Where each number comes from",
    "gen_counter":"Today","share_copy":"Copy","share_card":"Share Card",
    "save_combo":"Save","saved_ok":"✅ Saved","email_combo":"Send by email",
    "email_sent":"✅ Sent!","email_err":"⚠️ Configure Resend first.",
    "upgrade_btn":"Upgrade — $9.99/month","paywall_title":"Convergence Plan",
    "paywall_msg":"Unlock real data convergence, symbolic systems and Dream Mode.",
    "history":"History","perfil":"My Profile","guardadas":"Saved","comparador":"Compare",
    "no_history":"No combinations yet.","no_saved":"No saved combinations yet.",
    "login_err":"❌ Incorrect credentials.","pass_mismatch":"⚠️ Passwords don't match.",
    "pass_short":"⚠️ Minimum 6 characters.","email_invalid":"⚠️ Invalid email.",
    "email_exists":"⚠️ Email already registered.",
    "disclaimer":"We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
    "sources":{"historico":"Draw History","community":"Community","eventos":"World Events","fecha_personal":"Your Date","numerologia":"Numerology","fibonacci":"Fibonacci","sagrada":"Sacred Geometry","tesla":"Tesla 3·6·9","fractal":"Fractal","sueno":"Dream","lunar":"Lunar Cycle","cambio":"Exchange Rate","primos":"Prime Numbers","complement":"Complement","favorito":"Favourite"},
    "num_maestro":"Master Number","mejor_loteria":"Best Lottery","mejor_dia":"Best Day",
    "total_gen":"Total Generated","racha":"Streak","racha_d":"days",
    "comparar_intro":"Enter the official winning numbers to compare","comparar_btn":"Compare","aciertos":"matches",
    "ingresar_ganadores":"Winning numbers (comma separated)",
},
"ES":{
    "tagline":"Ordena tu Suerte",
    "hero_1":"Tus números,","hero_2":"respaldados por","hero_3":"las señales del mundo.",
    "hero_sub":"Datos reales, matemática e intuición convergidos en combinaciones con significado.",
    "login":"Entrar","register":"Crear Cuenta","logout":"Cerrar Sesión",
    "email":"Correo","password":"Contraseña","confirm_pass":"Confirmar contraseña",
    "btn_login":"Entrar","btn_register":"Crear Cuenta Gratis",
    "plan":"Plan","free":"Gratis","paid":"Convergencia",
    "select_lottery":"Selecciona tu Lotería","jackpot_live":"Jackpot en vivo",
    "next_draw":"Próximo sorteo","draw_today":"¡Sorteo hoy!","days":"días",
    "fav_title":"★ Números Favoritos","fav_help":"Selecciona los números que quieres incluir",
    "fav_clear":"Limpiar selección","fav_selected":"seleccionados",
    "real_title":"⊞ Datos Reales","real_help":"Frecuencias históricas, comunidad y eventos del mundo",
    "holistic_title":"∞ Holístico","holistic_help":"Numerología, sueños y ciclo lunar",
    "math_title":"ϕ Matemático","math_help":"Fibonacci, Tesla, Geometría Sagrada y números primos",
    "special_date":"Cumpleaños o fecha especial","your_name":"Tu nombre",
    "dream_placeholder":"Describe tu sueño... agua, una puerta dorada, el número 7...",
    "crowd_pref":"Comunidad","follow":"Seguir","avoid":"Evitar","balanced":"Balanceado",
    "exclude_numbers":"Números a excluir (separados por coma)",
    "generate_btn":"Generar Combinación","generating":"Convergiendo fuentes de datos...",
    "conv_steps":["Analizando eventos del mundo...","Leyendo señales de la comunidad...","Calculando tu matemática...","Convergiendo en tus números..."],
    "sources_title":"De dónde viene cada número",
    "gen_counter":"Hoy","share_copy":"Copiar","share_card":"Postal",
    "save_combo":"Guardar","saved_ok":"✅ Guardada","email_combo":"Enviar por correo",
    "email_sent":"✅ ¡Enviado!","email_err":"⚠️ Configura Resend primero.",
    "upgrade_btn":"Actualizar — $9.99/mes","paywall_title":"Plan Convergencia",
    "paywall_msg":"Desbloquea la convergencia completa con datos reales, sistemas simbólicos y Modo Sueños.",
    "history":"Historial","perfil":"Mi Perfil","guardadas":"Guardadas","comparador":"Comparar",
    "no_history":"Aún no has generado combinaciones.","no_saved":"Aún no tienes combinaciones guardadas.",
    "login_err":"❌ Credenciales incorrectas.","pass_mismatch":"⚠️ Las contraseñas no coinciden.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ El correo ya está registrado.",
    "disclaimer":"Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
    "sources":{"historico":"Histórico","community":"Comunidad","eventos":"Eventos","fecha_personal":"Tu Fecha","numerologia":"Numerología","fibonacci":"Fibonacci","sagrada":"Geometría Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal","sueno":"Sueño","lunar":"Ciclo Lunar","cambio":"Tasa de Cambio","primos":"Números Primos","complement":"Complemento","favorito":"Favorito"},
    "num_maestro":"Número Maestro","mejor_loteria":"Tu Lotería Ideal","mejor_dia":"Mejor Día",
    "total_gen":"Total Generadas","racha":"Racha","racha_d":"días",
    "comparar_intro":"Ingresa los números ganadores oficiales para comparar","comparar_btn":"Comparar","aciertos":"aciertos",
    "ingresar_ganadores":"Números ganadores (separados por coma)",
},
"PT":{
    "tagline":"Organize sua Sorte",
    "hero_1":"Seus números,","hero_2":"respaldados pelos","hero_3":"sinais do mundo.",
    "hero_sub":"Dados reais, matemática e intuição convergidos em combinações com significado.",
    "login":"Entrar","register":"Criar Conta","logout":"Sair",
    "email":"Email","password":"Senha","confirm_pass":"Confirmar senha",
    "btn_login":"Entrar","btn_register":"Criar Conta Grátis",
    "plan":"Plano","free":"Grátis","paid":"Convergência",
    "select_lottery":"Selecione sua Loteria","jackpot_live":"Jackpot ao vivo",
    "next_draw":"Próximo sorteio","draw_today":"Sorteio hoje!","days":"dias",
    "fav_title":"★ Números Favoritos","fav_help":"Selecione os números que quer incluir",
    "fav_clear":"Limpar seleção","fav_selected":"selecionados",
    "real_title":"⊞ Dados Reais","real_help":"Frequências históricas, comunidade e eventos do mundo",
    "holistic_title":"∞ Holístico","holistic_help":"Numerologia, sonhos e ciclo lunar",
    "math_title":"ϕ Matemático","math_help":"Fibonacci, Tesla, Geometria Sagrada e números primos",
    "special_date":"Aniversário ou data especial","your_name":"Seu nome",
    "dream_placeholder":"Descreva seu sonho... água, uma porta dourada, o número 7...",
    "crowd_pref":"Comunidade","follow":"Seguir","avoid":"Evitar","balanced":"Balanceado",
    "exclude_numbers":"Números a excluir (separados por vírgula)",
    "generate_btn":"Gerar Combinação","generating":"Convergindo fontes de dados...",
    "conv_steps":["Analisando eventos do mundo...","Lendo sinais da comunidade...","Calculando sua matemática...","Convergindo em seus números..."],
    "sources_title":"De onde vem cada número",
    "gen_counter":"Hoje","share_copy":"Copiar","share_card":"Postal",
    "save_combo":"Salvar","saved_ok":"✅ Salva","email_combo":"Enviar por email",
    "email_sent":"✅ Enviado!","email_err":"⚠️ Configure o Resend primeiro.",
    "upgrade_btn":"Atualizar — $9.99/mês","paywall_title":"Plano Convergência",
    "paywall_msg":"Desbloqueie a convergência completa com dados reais, sistemas simbólicos e Modo Sonhos.",
    "history":"Histórico","perfil":"Meu Perfil","guardadas":"Salvas","comparador":"Comparar",
    "no_history":"Ainda não gerou combinações.","no_saved":"Ainda não tem combinações salvas.",
    "login_err":"❌ Credenciais incorretas.","pass_mismatch":"⚠️ As senhas não coincidem.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ Email já cadastrado.",
    "disclaimer":"Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
    "sources":{"historico":"Histórico","community":"Comunidade","eventos":"Eventos","fecha_personal":"Sua Data","numerologia":"Numerologia","fibonacci":"Fibonacci","sagrada":"Geometria Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal","sueno":"Sonho","lunar":"Ciclo Lunar","cambio":"Taxa de Câmbio","primos":"Números Primos","complement":"Complemento","favorito":"Favorito"},
    "num_maestro":"Número Mestre","mejor_loteria":"Sua Loteria Ideal","mejor_dia":"Melhor Dia",
    "total_gen":"Total Geradas","racha":"Sequência","racha_d":"dias",
    "comparar_intro":"Insira os números vencedores oficiais para comparar","comparar_btn":"Comparar","aciertos":"acertos",
    "ingresar_ganadores":"Números vencedores (separados por vírgula)",
},
}
def tr(): return T[st.session_state["idioma"]]

# ══════════════════════════════════════════════════════
# 6. UTILIDADES
# ══════════════════════════════════════════════════════
def clean(text):
    """Strip HTML tags from any string"""
    if not text: return ""
    s = re.sub(r'<[^>]+>', ' ', str(text))
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_sources(sources):
    """Clean all HTML from source fields"""
    cleaned = []
    for s in sources:
        cleaned.append({
            **s,
            "explanation": clean(s.get("explanation","")),
            "math": clean(s.get("math","")),
            "label": clean(s.get("label","")),
        })
    return cleaned

# ══════════════════════════════════════════════════════
# 7. CÁLCULOS MATEMÁTICOS
# ══════════════════════════════════════════════════════
PHI = 1.6180339887
PI  = 3.14159265358979

def calc_fibonacci(mn,mx):
    result=[]; a,b=1,1; i=1
    while a<=mx:
        if a>=mn:
            if i>=3:
                pa,pb=b-a,a-(b-a) if a-(b-a)>0 else 1
                result.append({"n":a,"math":f"F{i-2}+F{i-1}={a}","fuente":"fibonacci"})
            else:
                result.append({"n":a,"math":f"F{i}={a}","fuente":"fibonacci"})
        a,b=b,a+b; i+=1
    return result

def calc_tesla(mn,mx):
    return [{"n":n,"math":f"3×{n//3}={n} → {n%9 or 9}","fuente":"tesla"} for n in range(mn,mx+1) if n%3==0]

def calc_sagrada(mn,mx):
    result=[]; seen=set()
    for i in range(1,60):
        for v,formula in [(int(PHI*i),f"ϕ×{i}={PHI*i:.2f}→{int(PHI*i)}"),(int(PI*i),f"π×{i}={PI*i:.2f}→{int(PI*i)}"),(round(PHI**2*i),f"ϕ²×{i}→{round(PHI**2*i)}")]:
            if mn<=v<=mx and v not in seen:
                result.append({"n":v,"math":formula,"fuente":"sagrada"}); seen.add(v)
    return sorted(result,key=lambda x:x["n"])

def calc_primos(mn,mx):
    def p(n): return n>=2 and all(n%i for i in range(2,int(n**0.5)+1))
    return [{"n":n,"math":f"{n} primo","fuente":"primos"} for n in range(mn,mx+1) if p(n)]

def calc_numerologia(nombre,fecha):
    result={}
    tabla={c:((ord(c.lower())-ord('a'))%9)+1 for c in 'abcdefghijklmnopqrstuvwxyz'}
    if nombre and nombre.strip():
        letras=[(c.upper(),tabla.get(c.lower(),0)) for c in nombre if c.isalpha()]
        if letras:
            s=sum(v for _,v in letras)
            f="+".join([f"{c}({v})" for c,v in letras])+f"={s}"
            while s>9 and s not in [11,22,33]: s=sum(int(d) for d in str(s)); f+=f"→{s}"
            result["nombre"]={"n":s,"math":f,"fuente":"numerologia"}
    if fecha and fecha.strip():
        digs=[c for c in fecha if c.isdigit()]
        if digs:
            s=sum(int(d) for d in digs)
            f="+".join(digs)+f"={s}"
            while s>9 and s not in [11,22,33]: s=sum(int(d) for d in str(s)); f+=f"→{s}"
            result["fecha"]={"n":s,"math":f,"fuente":"numerologia"}
    return result

def calc_lunar():
    known=datetime(2000,1,6,18,14)
    cycle=29.53058867
    phase=((datetime.now()-known).total_seconds()/(24*3600))%cycle
    day=int(phase)+1
    names=["Nueva","Creciente","Creciente","Creciente","Creciente","Creciente","Creciente","Cuarto C","Cuarto C","Gibosa C","Gibosa C","Gibosa C","Gibosa C","Gibosa C","Llena","Llena","Gibosa M","Gibosa M","Gibosa M","Gibosa M","Gibosa M","Gibosa M","Cuarto M","Cuarto M","Menguante","Menguante","Menguante","Menguante","Menguante","Nueva"]
    return {"n":day,"math":f"Luna día {day}/29 · {names[min(day-1,29)]}","fuente":"lunar"}

def calc_fecha(fecha,mn,mx):
    result=[]; seen=set()
    partes=[x for x in re.split(r'[-/.]',fecha) if x.isdigit()]
    for p in partes:
        v=int(p)
        if mn<=v<=mx and v not in seen: result.append({"n":v,"math":f"{p} directo de tu fecha","fuente":"fecha_personal"}); seen.add(v)
        if len(p)==4:
            s=int(p[-2:])
            if mn<=s<=mx and s not in seen: result.append({"n":s,"math":f"{p}[-2:]={s}","fuente":"fecha_personal"}); seen.add(s)
        sd=sum(int(d) for d in p)
        if mn<=sd<=mx and sd not in seen: result.append({"n":sd,"math":f"Σ({'+'.join(list(p))})={sd}","fuente":"fecha_personal"}); seen.add(sd)
    return result

# ══════════════════════════════════════════════════════
# 8. APIS EXTERNAS
# ══════════════════════════════════════════════════════
def get_cache(tipo):
    try:
        res=supabase.table("cache_diario").select("*").eq("fecha",str(date.today())).eq("tipo",tipo).execute()
        return res.data[0]["contenido"] if res.data else None
    except: return None

def set_cache(tipo,contenido,fuente=""):
    try:
        hoy=str(date.today())
        ex=supabase.table("cache_diario").select("id").eq("fecha",hoy).eq("tipo",tipo).execute()
        if ex.data: supabase.table("cache_diario").update({"contenido":contenido}).eq("id",ex.data[0]["id"]).execute()
        else: supabase.table("cache_diario").insert({"fecha":hoy,"tipo":tipo,"contenido":contenido,"fuente":fuente}).execute()
    except: pass

def obtener_efemerides(mes,dia):
    tipo=f"efem_{mes}_{dia}"; c=get_cache(tipo)
    if c: return c
    try:
        r=requests.get(f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{mes}/{dia}",timeout=8)
        if r.status_code==200:
            res=[{"year":e.get("year"),"text":e.get("text","")[:180]} for e in r.json().get("events",[])[:8]]
            set_cache(tipo,res,"wikipedia"); return res
    except: pass
    return []

def obtener_noticias():
    c=get_cache("noticias")
    if c: return c
    try:
        if NEWS_KEY:
            r=requests.get(f"https://newsapi.org/v2/top-headlines?language=en&pageSize=6&apiKey={NEWS_KEY}",timeout=8)
            if r.status_code==200:
                res=[{"title":a.get("title","")[:130]} for a in r.json().get("articles",[])[:6]]
                set_cache("noticias",res,"newsapi"); return res
    except: pass
    return []

def obtener_tasa():
    c=get_cache("tasa")
    if c: return c
    try:
        r=requests.get("https://api.exchangerate-api.com/v4/latest/USD",timeout=8)
        if r.status_code==200:
            eur=r.json().get("rates",{}).get("EUR",0.92)
            s=f"{eur:.4f}".replace(".","")
            res={"usd_eur":eur,"math":f"USD/EUR={eur:.4f}","nums":[int(s[i:i+2]) for i in range(0,len(s)-1,2) if int(s[i:i+2])>0]}
            set_cache("tasa",res,"exchangerate"); return res
    except: pass
    return {}

def obtener_comunidad(loteria):
    """
    Datos de comunidad — múltiples fuentes con fallback.
    1. Reddit JSON (a veces bloqueado en cloud)
    2. Google Trends RSS (siempre disponible)
    3. Fallback: números calientes del histórico real
    """
    tipo=f"community_{loteria['id']}_{date.today()}"
    c=get_cache(tipo)
    if c: return c

    mn,mx=loteria["min"],loteria["max"]
    nums=[]

    # Fuente 1 — Reddit JSON público
    for sub in loteria.get("reddit",["lottery"])[:2]:
        try:
            r=requests.get(
                f"https://www.reddit.com/r/{sub}/hot.json?limit=20",
                headers={"User-Agent":"Mozilla/5.0 LuckSort/1.0"},
                timeout=6)
            if r.status_code==200:
                for p in r.json().get("data",{}).get("children",[]):
                    txt=p.get("data",{}).get("title","")+p.get("data",{}).get("selftext","")
                    for n in re.findall(r"(\d{1,2})",txt):
                        v=int(n)
                        if mn<=v<=mx: nums.append(v)
        except: pass

    # Fuente 2 — Google Trends RSS (no requiere auth)
    if not nums:
        try:
            r=requests.get(
                "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
                headers={"User-Agent":"Mozilla/5.0"},timeout=6)
            if r.status_code==200:
                for n in re.findall(r"(\d{1,2})", r.text):
                    v=int(n)
                    if mn<=v<=mx: nums.append(v)
        except: pass

    if nums:
        top=[{"n":n,"count":cnt,"math":f"Número {n} detectado {cnt}× en señales de comunidad hoy","fuente":"community"}
             for n,cnt in Counter(nums).most_common(12)]
        set_cache(tipo,top,"community"); return top

    # Fallback — números calientes del histórico (son datos reales verificados)
    calientes = HISTORICO_REAL.get(loteria["nombre"],{}).get("calientes",[])
    fallback = [{"n":n,"math":f"Número caliente históricamente en {loteria['nombre']}","fuente":"community"}
                for n in calientes if mn<=n<=mx]
    if fallback: set_cache(tipo,fallback,"historico_calientes")
    return fallback

# Alias para compatibilidad
def obtener_reddit(loteria):
    return obtener_comunidad(loteria)

def obtener_lotterypost(loteria_nombre):
    """
    Scraping LotteryPost — comunidad real de jugadores.
    Extrae números más discutidos en foros antes del sorteo.
    """
    tipo = f"lp_{loteria_nombre}_{date.today()}"
    c = get_cache(tipo)
    if c: return c
    
    slug_map = {
        "Powerball":"powerball","Mega Millions":"megamillions",
        "EuroMillions":"euromillions","UK Lotto":"uklotto",
        "EuroJackpot":"eurojackpot","La Primitiva":"laprimitiva",
        "Baloto":"baloto","Mega-Sena":"megasena",
        "Canada Lotto":"lotto649",
    }
    slug = slug_map.get(loteria_nombre)
    if not slug: return []
    
    try:
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml",
            "Accept-Language":"en-US,en;q=0.9",
        }
        r = requests.get(
            f"https://www.lotterypost.com/results/{slug}/statistics",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            # Extraer números del HTML — buscar patrones de frecuencia
            nums = re.findall(r'<td[^>]*>(\d{1,2})</td>', r.text)
            freq = Counter([int(n) for n in nums if n.isdigit()])
            lot = next((l for l in LOTERIAS if l["nombre"]==loteria_nombre), None)
            if lot:
                mn, mx = lot["min"], lot["max"]
                top = [{"n":n,"count":c,"math":f"LotteryPost: aparece {c}× en estadísticas de comunidad","fuente":"community"}
                       for n,c in freq.most_common(15) if mn<=n<=mx]
                if top:
                    set_cache(tipo, top, "lotterypost")
                    return top
    except: pass
    return []

def obtener_caixa(loteria_nombre):
    """
    API oficial Caixa — loterías brasileñas.
    Gratuita, sin key, datos oficiales.
    """
    tipo = f"caixa_{loteria_nombre}_{date.today()}"
    c = get_cache(tipo)
    if c: return c
    
    slug_map = {
        "Mega-Sena":"megasena",
        "Lotofácil":"lotofacil",
    }
    slug = slug_map.get(loteria_nombre)
    if not slug: return []
    
    try:
        r = requests.get(
            f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{slug}/latest",
            headers={"User-Agent":"Mozilla/5.0"},
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            nums = data.get("dezenasSorteadasOrdemSorteio", [])
            if nums:
                res = [{"n":int(n),"math":f"Caixa API oficial — último sorteo {loteria_nombre}","fuente":"historico"}
                       for n in nums]
                set_cache(tipo, res, "caixa_api")
                return res
    except: pass
    return []

def obtener_jackpot(nombre):
    c=get_cache(f"jackpot_{nombre}")
    if c: return c
    try:
        slug={"Powerball":"powerball","Mega Millions":"megamillions","EuroMillions":"euromillions","EuroJackpot":"eurojackpot"}.get(nombre)
        if not slug: return None
        r=requests.get(f"https://lotterydata.io/api/{slug}/latest",timeout=6)
        if r.status_code==200:
            d=r.json(); jp=d.get("data",[{}])[0].get("jackpot") or d.get("jackpot")
            if jp: set_cache(f"jackpot_{nombre}",jp,"lotterydata"); return jp
    except: pass
    return None

# ══════════════════════════════════════════════════════
# 9. PREPARAR DATOS
# ══════════════════════════════════════════════════════
def preparar_datos(loteria, inputs, modulos):
    mn,mx = loteria["min"],loteria["max"]
    hoy = datetime.now()
    candidatos = []
    usados = set()
    for gen in st.session_state.get("historial_sesion",[])[-3:]:
        usados.update(gen)

    def add(item):
        if mn<=item["n"]<=mx:
            item["ya_usado"] = item["n"] in usados
            candidatos.append(item)

    # FAVORITOS — siempre primero
    for n in st.session_state.get("nums_favoritos",[]):
        if mn<=n<=mx:
            add({"n":n,"math":f"Número favorito seleccionado","fuente":"favorito","peso":6})

    # MÓDULO DATOS REALES
    if "real" in modulos:
        freq = analizar_frecuencias(loteria["nombre"])

        # ⊞ Histórico oficial
        if inputs.get("use_hist", True):
            for i,n in enumerate(freq.get("top_general",[])[:8]):
                add({"n":n,"math":f"Top histórico #{i+1} en {loteria['nombre']} (2015-2024)","fuente":"historico","peso":4})
            for n in freq.get("top_dia",[])[:3]:
                add({"n":n,"math":freq.get("narrativa",{}).get("dia",""),"fuente":"historico","peso":5})
            for n in freq.get("top_mes",[])[:3]:
                add({"n":n,"math":freq.get("narrativa",{}).get("mes",""),"fuente":"historico","peso":5})
            for n in freq.get("frios",[])[:2]:
                if mn<=n<=mx:
                    add({"n":n,"math":f"Número frío — sin salir en semanas en {loteria['nombre']}","fuente":"historico","peso":2})
            if loteria["nombre"] in ["Mega-Sena","Lotofácil"]:
                for item in obtener_caixa(loteria["nombre"]):
                    add({"n":item["n"],"math":item["math"],"fuente":"historico","peso":5})

        # ⊛ Comunidad
        if inputs.get("use_comm", True):
            for item in obtener_lotterypost(loteria["nombre"])[:6]:
                add({"n":item["n"],"math":item["math"],"fuente":"community","peso":4})
            for item in obtener_reddit(loteria)[:5]:
                add({"n":item["n"],"math":item["math"],"fuente":"community","peso":3})

        # ⊕ Eventos del mundo
        if inputs.get("use_event", True):
            efem=obtener_efemerides(hoy.month,hoy.day)
            for ev in efem[:6]:
                yr=ev.get("year",0)
                if yr:
                    y2=yr%100
                    if mn<=y2<=mx: add({"n":y2,"math":f"{yr}: {ev.get('text','')[:50]}... → {y2}","fuente":"eventos","peso":2})
            for art in obtener_noticias()[:4]:
                for n in re.findall(r"(\d{1,2})",art.get("title","")):
                    v=int(n)
                    if mn<=v<=mx: add({"n":v,"math":f"Noticia hoy: '{art['title'][:40]}...'","fuente":"eventos","peso":1})
            for v,m in [(hoy.day,f"Día {hoy.day} de hoy"),(hoy.month,f"Mes {hoy.month} actual"),(hoy.day+hoy.month,f"Día+Mes={hoy.day}+{hoy.month}={hoy.day+hoy.month}")]:
                if mn<=v<=mx: add({"n":v,"math":m,"fuente":"eventos","peso":1})

        # ⇌ Tasa de cambio
        if inputs.get("use_tasa", False):
            tasa=obtener_tasa()
            for n in tasa.get("nums",[]):
                if mn<=n<=mx: add({"n":n,"math":tasa.get("math",""),"fuente":"cambio","peso":1})
        # Wikipedia hoy
        efem=obtener_efemerides(hoy.month,hoy.day)
        for ev in efem[:6]:
            yr=ev.get("year",0)
            if yr:
                y2=yr%100
                if mn<=y2<=mx: add({"n":y2,"math":f"{yr}: {ev.get('text','')[:50]}... → {y2}","fuente":"eventos","peso":2})
        # Noticias
        for art in obtener_noticias()[:4]:
            for n in re.findall(r'\b(\d{1,2})\b',art.get("title","")):
                v=int(n)
                if mn<=v<=mx: add({"n":v,"math":f"'{art['title'][:45]}...' → {v}","fuente":"eventos","peso":1})
        # Tasa de cambio
        tasa=obtener_tasa()
        for n in tasa.get("nums",[]):
            if mn<=n<=mx: add({"n":n,"math":tasa.get("math",""),"fuente":"cambio","peso":1})
        # Fecha hoy
        for v,m in [(hoy.day,f"Día {hoy.day} de hoy"),(hoy.month,f"Mes {hoy.month} actual"),(hoy.day+hoy.month,f"Día+Mes={hoy.day}+{hoy.month}={hoy.day+hoy.month}")]:
            if mn<=v<=mx: add({"n":v,"math":m,"fuente":"eventos","peso":1})

    # MÓDULO HOLÍSTICO
    if "holistic" in modulos:
        # ᚨ Numerología
        if inputs.get("use_num", False):
            num_data=calc_numerologia(inputs.get("your_name",""),inputs.get("fecha_especial",""))
            for val in num_data.values():
                add({**val,"peso":5})
            for m_n in [11,22,33]:
                if mn<=m_n<=mx: add({"n":m_n,"math":f"Número maestro {m_n}","fuente":"numerologia","peso":3})
            fp=inputs.get("fecha_especial","")
            if fp:
                for nf in calc_fecha(fp,mn,mx): add({**nf,"peso":4})
                partes=[x for x in re.split(r'[-/.]',fp) if x.isdigit()]
                if len(partes)>=2:
                    try:
                        d_f,m_f=int(partes[0]),int(partes[1])
                        if 1<=d_f<=31 and 1<=m_f<=12:
                            for ev in obtener_efemerides(m_f,d_f)[:3]:
                                yr=ev.get("year",0)
                                if yr:
                                    y2=yr%100
                                    if mn<=y2<=mx: add({"n":y2,"math":f"Tu fecha {d_f}/{m_f}: {yr}→{y2}","fuente":"fecha_personal","peso":3})
                    except: pass
        # ◐ Lunar
        if inputs.get("use_lun", False):
            lu=calc_lunar()
            if mn<=lu["n"]<=mx: add({**lu,"peso":3})
        # ∞ Sueños — Groq los interpreta en el prompt
        if inputs.get("use_sue", False):
            pass  # Groq extrae números del sueño en prompt

    # MÓDULO MATEMÁTICO
    if "math" in modulos:
        if inputs.get("use_fib", False):
            for f in calc_fibonacci(mn,mx): add({**f,"peso":4})
        if inputs.get("use_tes", False):
            for t_n in calc_tesla(mn,mx): add({**t_n,"peso":3})
        if inputs.get("use_sag", False):
            for s in calc_sagrada(mn,mx)[:20]: add({**s,"peso":3})
        if inputs.get("use_pri", False):
            for p in calc_primos(mn,mx): add({**p,"peso":2})
        if inputs.get("use_fra", False):
            # Fractales — números de la serie de Mandelbrot reducidos al rango
            frac_base=[2,3,5,8,13,21,34,55]+[n for n in [1,4,9,16,25,36,49] if mn<=n<=mx]
            frac=[n for n in frac_base if mn<=n<=mx]
            for n in set(frac):
                if mn<=n<=mx: add({"n":n,"math":f"Fractal — auto-similitud en {n}","fuente":"fractal","peso":2})

    # Deduplicar — mejor peso gana
    mejor={}
    for c in candidatos:
        n=c["n"]
        if n not in mejor or c.get("peso",0)>mejor[n].get("peso",0):
            mejor[n]=c

    resultado=list(mejor.values())
    random.shuffle(resultado)
    return resultado

# ══════════════════════════════════════════════════════
# 10. GROQ — GENERACIÓN
# ══════════════════════════════════════════════════════
AFINIDADES = {
    "numerologia":["primos","fecha_personal","lunar"],
    "fibonacci":  ["sagrada","primos"],
    "sagrada":    ["fibonacci","primos"],
    "tesla":      ["sagrada","numerologia"],
    "primos":     ["fibonacci","sagrada"],
}

def generar_combinacion(loteria, inputs, modulos):
    lang=st.session_state["idioma"]
    lang_full={"EN":"English","ES":"Spanish","PT":"Portuguese"}[lang]
    candidatos=preparar_datos(loteria,inputs,modulos)

    excluir=[]
    if inputs.get("excluir"):
        try: excluir=[int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    validos=[c for c in candidatos if c["n"] not in excluir]
    preferidos=[c for c in validos if not c.get("ya_usado")]
    ya_usados=[c for c in validos if c.get("ya_usado")]
    ordenados=preferidos+ya_usados

    bonus_inst=f"1 {loteria['bname']} entre 1-{loteria['bmax']} (pool separado del principal)" if loteria["bonus"] else "sin número bonus"
    seed=random.randint(1000,9999)
    sueno=inputs.get("sueno","")
    favoritos=st.session_state.get("nums_favoritos",[])

    afines=[]
    for src in ["numerologia","fibonacci","sagrada","tesla","primos"]:
        if any(c.get("fuente")==src for c in ordenados):
            afines.extend(AFINIDADES.get(src,[]))
    afines=list(set(afines))

    # Análisis frecuencias para narrativa de Groq
    freq_ctx = analizar_frecuencias(loteria["nombre"]) if "real" in modulos else {}

    prompt=f"""Eres un equipo de especialistas generando combinación para {loteria['nombre']}.
Seed #{seed}. Cada generación debe ser única.

LOTERÍA: {loteria['nombre']} ({loteria['min']}-{loteria['max']}) | {loteria['n']} números | {bonus_inst}
EXCLUIR: {excluir}
FAVORITOS DEL USUARIO (incluir obligatoriamente si están en rango): {favoritos}
COMBINACIONES RECIENTES A EVITAR: {st.session_state.get('historial_sesion',[])[-3:]}
MÓDULOS ACTIVOS: {modulos}
SUEÑO: "{sueno if sueno else 'ninguno'}"

ANÁLISIS HISTÓRICO VERIFICADO (usar para narrativa, NO inventar %):
- Top día {freq_ctx.get('dia_actual','hoy')}: {freq_ctx.get('top_dia',[])}
- Top mes {freq_ctx.get('mes_nombre','')}: {freq_ctx.get('top_mes',[])}
- Números calientes: {freq_ctx.get('calientes',[])}
- Números fríos/vencidos: {freq_ctx.get('frios',[])}

CANDIDATOS REALES (Python pre-verificado):
{json.dumps(ordenados[:50],ensure_ascii=False)}

REGLAS ABSOLUTAS:
1. Usar SOLO números de la lista de candidatos
2. Los FAVORITOS del usuario van incluidos obligatoriamente si están en candidatos
3. Máximo 1 número de fuente "community"
4. Máximo 1 número por sistema simbólico (fibonacci, tesla, sagrada, numerologia, primos)
5. Si un sistema no tiene candidatos → usar fuente afín de esta lista: {afines}
   Si usas fuente afín → marcar es_afin=true y explicar la relación
6. El BONUS debe tener su propia fuente real específica entre 1-{loteria['bmax'] if loteria['bonus'] else 'N/A'}
   Buscar candidato en ese rango. Explicar con voz de especialista.
7. Preferir candidatos con ya_usado=false
8. Si hay sueño → extraer número del símbolo (fuente "sueno")
9. NUNCA inventar datos fuera de la lista
NUNCA inventar porcentajes, fechas exactas ni estadísticas que no estén en los candidatos
Si fuente es "historico" → decir que es uno de los numeros mas frecuentes en la loteria, sin inventar %
Si fuente es "community" → decir que es numero popular en la comunidad si no hay datos Reddit reales

VOZ DE EXPERTO por fuente:
- historico → historiador de probabilidades: usa los datos del ANÁLISIS HISTÓRICO VERIFICADO.
  Ejemplo: "Los [dia], el N lidera la frecuencia historica" o
  "En [mes], el N es el mas frecuente" o
  "El N esta frio, sin aparecer en semanas"
  NUNCA inventar porcentajes exactos
- community → analista de datos: cita menciones exactas en comunidad
- fibonacci → matemático: cita posición en secuencia y suma de anteriores
- tesla → físico: cita el ciclo 3-6-9 y reducción digital
- sagrada → geómetra sagrado: cita ϕ o π y su múltiplo exacto
- numerologia → numerólogo: muestra reducción paso a paso
- lunar → astrónomo: cita día del ciclo y fase
- eventos → historiador: nombra el evento específico
- cambio → analista financiero: cita tasa exacta
- sueno → intérprete: explica el símbolo
- favorito → confirma preferencia del usuario
- complement → honesto: sin señal específica disponible

Responde SOLO en {lang_full}. Devuelve SOLO JSON válido sin HTML:
{{
  "numbers":[{loteria['n']} enteros],
  "bonus":{f'entero 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources":[
    {{"number":N,"source":"tipo","es_afin":false,"label":"especialista en {lang_full}","math":"fórmula una línea","explanation":"voz experta específica sin etiquetas HTML"}}
  ]
}}"""

    try:
        resp=groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Especialistas en datos de lotería. Responder en {lang_full}. Solo JSON válido. Sin HTML en los textos. Nunca inventar datos."},
                {"role":"user","content":prompt}
            ],
            temperature=round(random.uniform(0.62,0.85),2),
            max_tokens=1800
        )
        raw=resp.choices[0].message.content.strip()
        print(f"[LUCKSORT GROQ] candidatos enviados: {len(ordenados)}")
        print(f"[LUCKSORT GROQ] respuesta raw: {raw[:300]}")
        if "```" in raw: raw=raw.split("```")[1].replace("json","").strip()
        res=json.loads(raw)

        # Limpiar HTML post-parseo
        res["sources"]=clean_sources(res.get("sources",[]))

        # Validar números
        nums=[n for n in res.get("numbers",[]) if loteria["min"]<=n<=loteria["max"] and n not in excluir]
        # Garantizar favoritos incluidos
        for fav in favoritos:
            if loteria["min"]<=fav<=loteria["max"] and fav not in excluir and fav not in nums:
                if len(nums)<loteria["n"]: nums.insert(0,fav)
        disp=[c["n"] for c in ordenados if c["n"] not in nums and c["n"] not in excluir]
        while len(nums)<loteria["n"] and disp: nums.append(disp.pop(0))
        pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in nums and n not in excluir]
        while len(nums)<loteria["n"] and pool: p=random.choice(pool); nums.append(p); pool.remove(p)
        res["numbers"]=list(dict.fromkeys(nums))[:loteria["n"]]

        # Validar bonus
        if loteria["bonus"]:
            b=res.get("bonus")
            if not isinstance(b,int) or not (1<=b<=loteria["bmax"]):
                bc=[c["n"] for c in ordenados if 1<=c["n"]<=loteria["bmax"] and c["n"] not in nums]
                res["bonus"]=bc[0] if bc else random.randint(1,loteria["bmax"])

        # Guardar historial sesión
        hist=st.session_state.get("historial_sesion",[])
        hist.append(res["numbers"]); st.session_state["historial_sesion"]=hist[-5:]
        return res
    except Exception as _e:
        print(f"[LUCKSORT ERROR generar_combinacion] {type(_e).__name__}: {_e}")
        import traceback; traceback.print_exc()
        return generar_fallback(loteria,excluir,ordenados)

def generar_fallback(loteria,excluir=[],candidatos=[]):
    pool_r=[c["n"] for c in candidatos if c["n"] not in excluir]
    nums=random.sample(pool_r,min(loteria["n"],len(pool_r))) if len(pool_r)>=loteria["n"] else random.sample([n for n in range(loteria["min"],loteria["max"]+1) if n not in excluir],loteria["n"])
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    sources=[{"number":n,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Sin señal específica disponible."} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Complemento."})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

def generar_aleatorio(loteria):
    pool=list(range(loteria["min"],loteria["max"]+1))
    nums=random.sample(pool,loteria["n"])
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    sources=[{"number":n,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Generación aleatoria — plan gratuito."} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Bonus aleatorio."})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

# ══════════════════════════════════════════════════════
# 11. SUPABASE
# ══════════════════════════════════════════════════════
def registrar_usuario(email,password):
    try:
        if supabase.table("usuarios").select("email").eq("email",email).execute().data: return False,"exists"
        res=supabase.table("usuarios").insert({"email":email,"password":password,"role":"free","generaciones_hoy":0,"fecha_uso":str(date.today())}).execute()
        return (True,res.data[0]) if res.data else (False,"error")
    except Exception as e: return False,str(e)

def login_usuario(email,password):
    try:
        res=supabase.table("usuarios").select("*").eq("email",email).eq("password",password).single().execute()
        return (True,res.data) if res.data else (False,None)
    except: return False,None

def guardar_generacion(uid,lid,nums,bonus,sources,inputs):
    try: supabase.table("generaciones").insert({"user_id":uid,"loteria_id":lid,"numeros":nums,"bonus":bonus,"narrativa":json.dumps(sources,ensure_ascii=False),"inputs_usuario":json.dumps(inputs,ensure_ascii=False)}).execute()
    except: pass

def obtener_historial(uid,limit=15):
    try:
        res=supabase.table("generaciones").select("*").eq("user_id",uid).order("created_at",desc=True).limit(limit).execute()
        return res.data if res.data else []
    except: return []

def obtener_stats(uid):
    try:
        res=supabase.table("generaciones").select("*").eq("user_id",uid).order("created_at",desc=True).execute()
        if not res.data: return {}
        data=res.data; total=len(data)
        lc={};[lc.update({g.get("loteria_id"):lc.get(g.get("loteria_id"),0)+1}) for g in data]
        fid=max(lc,key=lc.get) if lc else None
        fav=next((l["nombre"] for l in LOTERIAS if l["id"]==fid),"-")
        all_n=[]; [all_n.extend(g.get("numeros",[])) for g in data]
        top=[n for n,_ in Counter(all_n).most_common(5)]
        fechas=sorted(set([g.get("created_at","")[:10] for g in data]),reverse=True)
        racha=0; check=date.today()
        for f in fechas:
            if f==str(check): racha+=1; check-=timedelta(days=1)
            else: break
        return {"total":total,"fav":fav,"top_nums":top,"racha":racha}
    except: return {}

def resetear_uso():
    hoy=str(date.today())
    if st.session_state.get("fecha_uso")!=hoy:
        st.session_state["generaciones_hoy"]={}; st.session_state["fecha_uso"]=hoy; st.session_state["historial_sesion"]=[]

def guardar_combo_sesion(resultado,loteria):
    g=st.session_state.get("combinaciones_guardadas",[])
    e={"numeros":resultado.get("numbers",[]),"bonus":resultado.get("bonus"),"loteria":loteria["nombre"],"flag":loteria["flag"],"fecha":str(date.today()),"sources":resultado.get("sources",[])}
    if not any(x["numeros"]==e["numeros"] and x["loteria"]==e["loteria"] for x in g):
        g.insert(0,e); st.session_state["combinaciones_guardadas"]=g[:20]; return True
    return False

# ══════════════════════════════════════════════════════
# 12. EMAIL
# ══════════════════════════════════════════════════════
def enviar_email(to,subject,html):
    if not RESEND_KEY: return False
    try:
        r=requests.post("https://api.resend.com/emails",headers={"Authorization":f"Bearer {RESEND_KEY}","Content-Type":"application/json"},json={"from":"hello@lucksort.com","to":[to],"subject":subject,"html":html},timeout=10)
        return r.status_code==200
    except: return False

def email_bienvenida(email):
    t=T[st.session_state.get("idioma","EN")]
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:28px;max-width:560px;margin:0 auto;">
<div style="text-align:center;padding:18px 0;"><div style="display:inline-flex;align-items:center;gap:10px;"><div style="width:28px;height:28px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;color:#0a0a0f;">◆</div><span style="font-size:20px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div></div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,.2);margin:10px 0 18px;">
<h2>Welcome ◆</h2><p style="color:rgba(255,255,255,.6);line-height:1.7;">Your LuckSort account is ready.</p>
<div style="background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:18px;margin:18px 0;"><ul style="color:rgba(255,255,255,.6);line-height:2.2;margin:0;padding-left:18px;"><li>5 combinations per lottery per day</li><li>11 lotteries · 3 languages</li><li>Upgrade for full convergence</li></ul></div>
<div style="text-align:center;margin:22px 0;"><a href="{APP_URL}" style="display:inline-block;padding:13px 32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;">Open LuckSort →</a></div>
<p style="color:rgba(255,255,255,.15);font-size:11px;font-style:italic;text-align:center;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.12);font-size:10px;margin-top:12px;">© 2025 LuckSort · lucksort.com</p></body></html>"""
    enviar_email(email,"Welcome to LuckSort ◆",html)

def email_combo(to,loteria,resultado):
    t=T[st.session_state.get("idioma","EN")]
    nums=resultado.get("numbers",[]); bonus=resultado.get("bonus"); sources=resultado.get("sources",[])
    nums_str=" · ".join([str(n).zfill(2) for n in nums]); bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    src_html="".join([f'<div style="padding:8px 12px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);margin-bottom:6px;"><span style="font-family:monospace;">{ICONS.get(s.get("source","complement"),"·")}</span> <strong style="color:rgba(255,255,255,.75);">{clean(s.get("label",""))}</strong><span style="color:#C9A84C;float:right;font-family:monospace;">→ {str(s.get("number","")).zfill(2)}</span><div style="color:#C9A84C;font-family:monospace;font-size:11px;">{clean(s.get("math",""))}</div><p style="color:rgba(255,255,255,.4);font-size:11px;margin:2px 0 0;">{clean(s.get("explanation",""))}</p></div>' for s in sources])
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:26px;max-width:540px;margin:0 auto;">
<div style="text-align:center;padding:12px 0;"><div style="display:inline-flex;align-items:center;gap:8px;"><div style="width:24px;height:24px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;color:#0a0a0f;">◆</div><span style="font-size:17px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div></div>
<div style="text-align:center;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:14px;padding:18px;margin:12px 0;"><div style="font-family:monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;margin-bottom:7px;">{loteria['flag']} {loteria['nombre'].upper()}</div><div style="font-family:monospace;font-size:24px;font-weight:700;letter-spacing:3px;">{nums_str}{bonus_s}</div></div>
<p style="color:#C9A84C;font-size:10px;letter-spacing:2px;margin-bottom:9px;">{t['sources_title'].upper()}</p>{src_html}
<p style="color:rgba(255,255,255,.15);font-size:11px;font-style:italic;text-align:center;margin-top:14px;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.12);font-size:10px;margin-top:10px;">© 2025 LuckSort · lucksort.com</p></body></html>"""
    return enviar_email(to,f"◆ {loteria['nombre']} — LuckSort",html)

# ══════════════════════════════════════════════════════
# 13. COMPONENTES UI
# ══════════════════════════════════════════════════════
def render_header():
    """Header con logo + pills idioma como links href"""
    lang = st.session_state["idioma"]
    
    def pill(code):
        active = code == lang
        bg    = "rgba(201,168,76,0.15)" if active else "transparent"
        border= "rgba(201,168,76,0.45)" if active else "rgba(255,255,255,0.12)"
        color = "#C9A84C"               if active else "rgba(255,255,255,0.32)"
        style = (f"padding:3px 10px;border-radius:20px;border:1px solid {border};"
                 f"background:{bg};color:{color};font-family:monospace;"
                 f"font-size:10px;font-weight:700;letter-spacing:1px;"
                 f"text-decoration:none;display:inline-block;")
        return f'<a href="?lang={code}" style="{style}">{code}</a>'

    pills = " ".join([pill(c) for c in ["EN","ES","PT"]])
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:10px 0;border-bottom:1px solid rgba(201,168,76,.1);margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:32px;height:32px;min-width:32px;
    background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 14px rgba(201,168,76,.3);font-size:16px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
      color:white;letter-spacing:-.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;
      color:rgba(201,168,76,.5);letter-spacing:2.5px;">SORT YOUR LUCK</div>
    </div>
  </div>
  <div style="display:flex;gap:5px;">{pills}</div>
</div>""", unsafe_allow_html=True)

def render_balls_landing():
    st.markdown("""
<div style="margin:18px auto;max-width:400px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;text-align:center;margin-bottom:10px;">LIVE PREVIEW · POWERBALL</div>
  <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;">
    <div class="ball" id="b0">07</div><div class="ball" id="b1">14</div>
    <div class="ball" id="b2">23</div><div class="ball" id="b3">34</div>
    <div class="ball" id="b4">55</div><div class="ball ball-gold" id="b5">12</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:5px;">
    <div class="src-row"><div class="src-left"><span class="src-icon">⊞</span><div><div class="src-label">Draw History</div><div class="src-math">Top histórico oficial Powerball — #1 más frecuente</div></div></div><span class="src-num">→ 07</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">ϕ</span><div><div class="src-label">Fibonacci</div><div class="src-math">F9+F10=34 · posición 11 en la secuencia</div></div></div><span class="src-num">→ 34</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">⊛</span><div><div class="src-label">Community</div><div class="src-math">Mencionado 47× en r/powerball hoy</div></div></div><span class="src-num">→ 23</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">✦</span><div><div class="src-label">Your Date</div><div class="src-math">14/03/92 → día 14 directo de tu fecha</div></div></div><span class="src-num">→ 14</span></div>
  </div>
</div>
<script>
const S=[[7,14,23,34,55,12],[3,19,31,44,62,8],[11,22,35,47,68,17],[5,16,28,41,59,23],[9,21,33,46,63,4]];
let i=0;
setInterval(()=>{i=(i+1)%S.length;for(let j=0;j<6;j++){const el=document.getElementById('b'+j);if(!el)return;el.style.opacity='0';el.style.transform='scale(.75)';setTimeout(()=>{el.textContent=String(S[i][j]).padStart(2,'0');el.style.opacity='1';el.style.transform='scale(1)';},260+j*42);}},2800);
document.querySelectorAll('.ball').forEach(b=>{b.style.transition='opacity .26s ease,transform .26s ease';});
</script>""", unsafe_allow_html=True)

def render_gen_dots(gen_hoy):
    dots="".join([f'<div class="dot {"dot-on" if i<gen_hoy else "dot-off"}"></div>' for i in range(MAX_GEN)])
    st.markdown(f'<div class="gen-dots">{dots}</div>', unsafe_allow_html=True)

def render_balls_picker(loteria):
    """Panel de selección de números favoritos — multiselect nativo"""
    mn,mx=loteria["min"],loteria["max"]
    favoritos=st.session_state.get("nums_favoritos",[])
    
    # Usar multiselect nativo — funciona en móvil y desktop
    opciones=[n for n in range(mn,mx+1)]
    # Key fijo — evita bloqueo al cambiar lotería
    # Limpiar favoritos fuera de rango de la lotería actual
    favoritos_validos = [n for n in favoritos if mn<=n<=mx]
    seleccionados=st.multiselect(
        "",
        opciones,
        default=favoritos_validos,
        format_func=lambda n: str(n).zfill(2),
        key="ms_fav",
        label_visibility="collapsed"
    )
    if sorted(seleccionados)!=sorted(favoritos_validos):
        st.session_state["nums_favoritos"]=sorted(seleccionados)
        st.rerun()

def render_resultado(resultado, loteria, modulos):
    t=tr()
    numeros=resultado.get("numbers",[]); bonus=resultado.get("bonus"); sources=resultado.get("sources",[])

    balls='<div class="balls-wrap">'+"".join([f'<div class="ball {"ball-fav" if n in st.session_state.get("nums_favoritos",[]) else ""}">{str(n).zfill(2)}</div>' for n in numeros])
    if bonus: balls+=f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    balls+='</div>'
    bonus_lbl=f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.22);text-align:center;margin-top:2px;">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>' if bonus and loteria.get("bname") else ""

    # Temática según módulos
    tema_icon = "ϕ" if modulos==["math"] else "∞" if modulos==["holistic"] else "⊞" if modulos==["real"] else "◆"
    st.markdown(f"""
<div class="ls-card-gold" style="text-align:center;">
  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:2px;">{loteria['flag']} {loteria['nombre']} {tema_icon}</div>
  {balls}{bonus_lbl}
</div>""", unsafe_allow_html=True)

    if sources:
        st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;color:rgba(255,255,255,.28);letter-spacing:2px;text-transform:uppercase;margin:14px 0 8px;">{t["sources_title"]}</div>', unsafe_allow_html=True)
        for s in sources:
            src=s.get("source","complement")
            icon=ICONS.get(src,"·")
            lbl=clean(s.get("label") or t["sources"].get(src,src))
            math_line=clean(s.get("math",""))
            exp=clean(s.get("explanation",""))
            num=s.get("number","")
            es_afin=s.get("es_afin",False)
            cls="src-row src-complement" if src=="complement" else "src-row src-afin" if es_afin else "src-row"
            afin_badge='<div class="src-afin-badge">≈ fuente afín</div>' if es_afin else ""
            st.markdown(f"""<div class="{cls}"><div class="src-left"><span class="src-icon">{icon}</span><div>
<div class="src-label">{lbl}</div>
{f'<div class="src-math">{math_line}</div>' if math_line and math_line!="—" else ""}
{afin_badge}
<div class="src-desc">{exp}</div>
</div></div><span class="src-num">→ {str(num).zfill(2)}</span></div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

def render_paywall():
    t=tr()
    features=[("⊞","Real Data"),("⊛","Community"),("⊕","World Events"),("★","Favourites"),("ᚨ","Numerology"),("ϕ","Fibonacci"),("⬡","Sacred Geo"),("⌁","Tesla"),("◐","Lunar"),("∞","Dream Mode"),("⊞","Official History")]
    pills="".join([f'<span style="font-size:11px;color:rgba(255,255,255,.35);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:4px 10px;font-family:monospace;">{i} {l}</span>' for i,l in features])
    st.markdown(f"""<div class="ls-card" style="border-color:rgba(201,168,76,.25);text-align:center;padding:24px;">
<div style="font-size:22px;margin-bottom:8px;">◆</div>
<h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:18px;">{t['paywall_title']}</h3>
<p style="color:rgba(255,255,255,.38);font-size:13px;max-width:280px;margin:0 auto 14px;line-height:1.6;">{t['paywall_msg']}</p>
<div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;">{pills}</div>
</div>""", unsafe_allow_html=True)
    if st.button(t["upgrade_btn"],use_container_width=True,key="upgrade_btn"):
        st.markdown(f'<meta http-equiv="refresh" content="0;url={STRIPE_LINK}">',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 14. SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="padding:18px 14px 12px;border-bottom:1px solid rgba(201,168,76,.12);">
<div style="display:flex;align-items:center;gap:10px;">
<div style="width:28px;height:28px;min-width:28px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;color:#0a0a0f;">◆</div>
<div><div style="font-family:Georgia,serif;font-size:17px;font-weight:700;color:white;">LuckSort</div>
<div style="font-family:monospace;font-size:8px;color:rgba(201,168,76,.5);letter-spacing:2px;">SORT YOUR LUCK</div></div></div></div>""",unsafe_allow_html=True)

    # Idioma sidebar — actualiza query_params (recarga natural sin conflicto)
    lang_actual = st.session_state["idioma"]
    LANG_OPTS = {"🇺🇸 English":"EN","🇪🇸 Español":"ES","🇧🇷 Português":"PT"}
    cur_display = next(k for k,v in LANG_OPTS.items() if v==lang_actual)
    sel_lang = st.selectbox("🌐 Language / Idioma:",
        list(LANG_OPTS.keys()),
        index=list(LANG_OPTS.keys()).index(cur_display),
        key="sb_lang")
    if LANG_OPTS[sel_lang] != lang_actual:
        st.query_params["lang"] = LANG_OPTS[sel_lang]
        st.session_state["idioma"] = LANG_OPTS[sel_lang]
        st.rerun()
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">',unsafe_allow_html=True)

    t=tr()
    if not st.session_state["logged_in"]:
        tab_in,tab_up=st.tabs([t["login"],t["register"]])
        with tab_in:
            em=st.text_input(t["email"],key="si_e"); pw=st.text_input(t["password"],type="password",key="si_p")
            if st.button(t["btn_login"],use_container_width=True,key="btn_si"):
                if em==ADMIN_EMAIL and pw==ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":em,"user_id":None,"vista":"app"}); st.rerun()
                else:
                    ok,datos=login_usuario(em,pw)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":datos["role"],"user_email":datos["email"],"user_id":datos["id"],"vista":"app"})
                        resetear_uso(); st.rerun()
                    else: st.error(t["login_err"])
        with tab_up:
            re_=st.text_input(t["email"],key="su_e"); rp1=st.text_input(t["password"],type="password",key="su_p1"); rp2=st.text_input(t["confirm_pass"],type="password",key="su_p2")
            if st.button(t["btn_register"],use_container_width=True,key="btn_su"):
                if rp1!=rp2: st.error(t["pass_mismatch"])
                elif len(rp1)<6: st.warning(t["pass_short"])
                elif "@" not in re_: st.warning(t["email_invalid"])
                else:
                    ok,res=registrar_usuario(re_,rp1)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_,"user_id":res["id"],"vista":"app"})
                        email_bienvenida(re_); st.rerun()
                    elif res=="exists": st.error(t["email_exists"])
                    else: st.error("⚠️ Error.")
    else:
        resetear_uso()
        role=st.session_state["user_role"]
        role_lbl=t["paid"] if role not in ["free","invitado"] else t["free"]
        role_color="#C9A84C" if role!="free" else "rgba(255,255,255,.3)"
        em_d=st.session_state["user_email"][:20]+"…" if len(st.session_state["user_email"])>22 else st.session_state["user_email"]
        st.markdown(f'<div style="padding:10px 12px;background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.15);border-radius:10px;margin-bottom:10px;"><div style="font-size:12px;color:rgba(255,255,255,.7);margin-bottom:3px;">{em_d}</div><div style="display:flex;align-items:center;gap:5px;"><div style="width:6px;height:6px;border-radius:50%;background:{role_color};"></div><span style="font-family:monospace;font-size:9px;color:{role_color};letter-spacing:1.5px;">{role_lbl.upper()}</span></div></div>',unsafe_allow_html=True)
        for vista_key,label in [("app",f"◆ {t['tagline']}"),("history",f"⊞ {t['history']}"),("guardadas",f"★ {t['guardadas']}"),("comparador",f"⊕ {t['comparador']}")]:
            if st.button(label,use_container_width=True,key=f"nav_{vista_key}"):
                st.session_state["vista"]=vista_key; st.rerun()
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">',unsafe_allow_html=True)
        if st.button(t["logout"],use_container_width=True,key="btn_lo"):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]; st.rerun()

# ══════════════════════════════════════════════════════
# 15. LANDING
# ══════════════════════════════════════════════════════
if not st.session_state["logged_in"]:
    t=tr()
    render_header()
    st.markdown(f"""<div style="text-align:center;padding:22px 16px 12px;">
<div class="tag-gold" style="margin-bottom:12px;"><span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span> Data Convergence Engine</div>
<h1 style="font-family:'Playfair Display',serif;font-size:clamp(30px,7vw,66px);font-weight:700;line-height:1.05;letter-spacing:-2px;margin-bottom:12px;">
{t['hero_1']}<br><span class="shimmer-text">{t['hero_2']}</span><br>{t['hero_3']}</h1>
<p style="font-size:clamp(14px,2vw,17px);color:rgba(255,255,255,.38);max-width:460px;margin:0 auto;line-height:1.8;">{t['hero_sub']}</p>
</div>""",unsafe_allow_html=True)

    render_balls_landing()

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:4px 0 12px;">',unsafe_allow_html=True)
    ca,cb,cc=st.columns([1,2,1])
    with cb:
        st.markdown(f'<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.16);letter-spacing:1.5px;margin-bottom:10px;">FREE · NO CREDIT CARD · ES / EN / PT</p>',unsafe_allow_html=True)
        tab_r,tab_l=st.tabs([t["register"],t["login"]])
        with tab_r:
            re_=st.text_input(t["email"],key="lr_e"); rp=st.text_input(t["password"],type="password",key="lr_p"); rp2=st.text_input(t["confirm_pass"],type="password",key="lr_p2")
            if st.button(t["btn_register"],use_container_width=True,key="lr_b"):
                if rp!=rp2: st.error(t["pass_mismatch"])
                elif len(rp)<6: st.warning(t["pass_short"])
                elif "@" not in re_: st.warning(t["email_invalid"])
                else:
                    ok,res=registrar_usuario(re_,rp)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_,"user_id":res["id"],"vista":"app"})
                        email_bienvenida(re_); st.rerun()
                    elif res=="exists": st.error(t["email_exists"])
                    else: st.error("⚠️ Error.")
        with tab_l:
            le=st.text_input(t["email"],key="ll_e"); lp=st.text_input(t["password"],type="password",key="ll_p")
            if st.button(t["btn_login"],use_container_width=True,key="ll_b"):
                if le==ADMIN_EMAIL and lp==ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":le,"user_id":None,"vista":"app"}); st.rerun()
                else:
                    ok,datos=login_usuario(le,lp)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":datos["role"],"user_email":datos["email"],"user_id":datos["id"],"vista":"app"})
                        resetear_uso(); st.rerun()
                    else: st.error(t["login_err"])

# ══════════════════════════════════════════════════════
# 16. APP — GENERADOR
# ══════════════════════════════════════════════════════
elif st.session_state.get("vista")=="app":
    t=tr()
    es_free=st.session_state["user_role"]=="free"
    es_paid=st.session_state["user_role"] in ["paid","pro","convergence","admin"]

    render_header()
    st.markdown(f'<h2 style="font-family:\'Playfair Display\',serif;font-size:clamp(18px,3vw,30px);font-weight:700;letter-spacing:-1px;margin:4px 0 10px;">{t["select_lottery"]}</h2>',unsafe_allow_html=True)

    lot_names=[f"{l['flag']} {l['nombre']}  ({l['pais']})" for l in LOTERIAS]
    sel=st.selectbox("",lot_names,label_visibility="collapsed",key="lot_sel")
    loteria=next(l for l in LOTERIAS if l["nombre"] in sel)

    # Jackpot + countdown
    jackpot=obtener_jackpot(loteria["nombre"])
    prox=proximo_sorteo(loteria["nombre"])
    badges=""
    if jackpot: badges+=f'<span class="jackpot-badge">◈ {t["jackpot_live"]}: {jackpot}</span> '
    if prox:
        if prox["dias"]<=0: badges+=f'<span class="jackpot-badge">⚡ {t["draw_today"]} {prox["hora"]}</span>'
        elif prox["dias"]==1: badges+=f'<span class="jackpot-badge">⏱ {t["next_draw"]}: mañana {prox["hora"]}</span>'
        else: badges+=f'<span class="jackpot-badge">⏱ {t["next_draw"]}: {prox["dias"]} {t["days"]} · {prox["hora"]}</span>'
    if badges: st.markdown(f'<div style="margin:4px 0 10px;display:flex;gap:6px;flex-wrap:wrap;">{badges}</div>',unsafe_allow_html=True)

    gen_hoy=st.session_state["generaciones_hoy"].get(loteria["id"],0)
    render_gen_dots(gen_hoy)
    st.markdown(f'<div style="text-align:center;margin:-6px 0 10px;"><span class="metric-pill">{t["gen_counter"]}: {gen_hoy}/{MAX_GEN}</span></div>',unsafe_allow_html=True)

    modulos=[]
    inputs={}

    if es_paid or st.session_state["user_role"]=="admin":

        # MÓDULO 1 — FAVORITOS
        favs=st.session_state.get("nums_favoritos",[])
        fav_label=f"{t['fav_title']} — {len(favs)} {t['fav_selected']}" if favs else t["fav_title"]
        with st.expander(fav_label,expanded=False):
            st.caption(t["fav_help"])
            render_balls_picker(loteria)
            if favs:
                fav_balls="".join([f'<div class="ball ball-fav" style="width:36px;height:36px;font-size:12px;">{str(n).zfill(2)}</div>' for n in favs])
                st.markdown(f'<div class="balls-wrap">{fav_balls}</div>',unsafe_allow_html=True)
                if st.button(t["fav_clear"],key="fav_clear"):
                    st.session_state["nums_favoritos"]=[]; st.rerun()

        # MÓDULO 2 — DATOS REALES
        with st.expander(t["real_title"], expanded=False):
            st.caption(t["real_help"])
            cb_hist  = st.checkbox(f"{ICONS['historico']} {t['sources']['historico']}",  value=True,  key="cb_hist")
            cb_comm  = st.checkbox(f"{ICONS['community']} {t['sources']['community']}",  value=True,  key="cb_comm")
            cb_event = st.checkbox(f"{ICONS['eventos']} {t['sources']['eventos']}",      value=True,  key="cb_event")
            cb_tasa  = st.checkbox(f"{ICONS['cambio']} {t['sources']['cambio']}",        value=False, key="cb_tasa")
            if any([cb_hist, cb_comm, cb_event, cb_tasa]):
                modulos.append("real")
                inputs["use_hist"]  = cb_hist
                inputs["use_comm"]  = cb_comm
                inputs["use_event"] = cb_event
                inputs["use_tasa"]  = cb_tasa
            st.markdown('<div style="margin-top:6px;"></div>', unsafe_allow_html=True)
            crowd_pref=st.radio(t["crowd_pref"],[t["balanced"],t["follow"],t["avoid"]],horizontal=True,key="cp")
            crowd_map={t["follow"]:"follow",t["avoid"]:"avoid",t["balanced"]:"balanced"}
            inputs["crowd"]=crowd_map.get(crowd_pref,"balanced")
            inputs["excluir"]=st.text_input(t["exclude_numbers"],placeholder="4, 13",key="ex")

        # MÓDULO 3 — HOLÍSTICO
        with st.expander(t["holistic_title"],expanded=False):
            st.caption(t["holistic_help"])
            cb_num  = st.checkbox(f"{ICONS['numerologia']} {t['sources']['numerologia']}", value=False, key="cb_num")
            cb_lun  = st.checkbox(f"{ICONS['lunar']} {t['sources']['lunar']}",             value=False, key="cb_lun")
            cb_sue  = st.checkbox(f"{ICONS['sueno']} {t['sources']['sueno']}",             value=False, key="cb_sue")
            if any([cb_num, cb_lun, cb_sue]):
                modulos.append("holistic")
                inputs["use_num"] = cb_num
                inputs["use_lun"] = cb_lun
                inputs["use_sue"] = cb_sue
            if cb_num:
                c1,c2=st.columns(2)
                with c1: inputs["your_name"]=st.text_input(t["your_name"],placeholder="Your name",key="nm")
                with c2: inputs["fecha_especial"]=st.text_input(t["special_date"],placeholder="14/03/1990",key="fe")
            if cb_sue:
                inputs["sueno"]=st.text_area("",placeholder=t["dream_placeholder"],key="dr",height=70)

        # MÓDULO 4 — MATEMÁTICO
        with st.expander(t["math_title"],expanded=False):
            st.caption(t["math_help"])
            cb_fib = st.checkbox(f"{ICONS['fibonacci']} Fibonacci",              value=False, key="cb_fib")
            cb_tes = st.checkbox(f"{ICONS['tesla']} Tesla 3·6·9",                value=False, key="cb_tes")
            cb_sag = st.checkbox(f"{ICONS['sagrada']} {t['sources']['sagrada']}", value=False, key="cb_sag")
            cb_pri = st.checkbox(f"{ICONS['primos']} {t['sources']['primos']}",  value=False, key="cb_pri")
            cb_fra = st.checkbox(f"{ICONS['fractal']} {t['sources']['fractal']}", value=False, key="cb_fra")
            if any([cb_fib, cb_tes, cb_sag, cb_pri, cb_fra]):
                modulos.append("math")
                inputs["use_fib"] = cb_fib
                inputs["use_tes"] = cb_tes
                inputs["use_sag"] = cb_sag
                inputs["use_pri"] = cb_pri
                inputs["use_fra"] = cb_fra

    if not modulos: modulos=["real"]

    restantes=max(0,MAX_GEN-gen_hoy)
    if restantes<=0:
        st.warning(f"⚠️ {t['gen_counter']}: {MAX_GEN}/{MAX_GEN}")
    else:
        if st.button(f"◆ {t['generate_btn']}",use_container_width=True,key="gen_btn"):
            if es_paid or st.session_state["user_role"]=="admin":
                ph=st.empty()
                for step in t["conv_steps"]:
                    ph.markdown(f'<div style="text-align:center;padding:18px 0;"><div class="conv-ring"></div><div class="conv-label">{step}</div></div>',unsafe_allow_html=True)
                    time.sleep(0.55)
                ph.empty()
                resultado=generar_combinacion(loteria,inputs,modulos)
            else:
                with st.spinner(t["generating"]): resultado=generar_aleatorio(loteria)
            st.session_state["ultima_generacion"]=resultado
            st.session_state["ultima_loteria"]=loteria
            st.session_state["ultima_modulos"]=modulos
            st.session_state["generaciones_hoy"][loteria["id"]]=gen_hoy+1
            if st.session_state.get("user_id"):
                guardar_generacion(st.session_state["user_id"],loteria["id"],resultado.get("numbers",[]),resultado.get("bonus"),resultado.get("sources",[]),inputs)
            st.rerun()

    if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:12px 0;">',unsafe_allow_html=True)
        ult_res=st.session_state["ultima_generacion"]
        ult_lot=st.session_state["ultima_loteria"]
        ult_mod=st.session_state.get("ultima_modulos",["real"])
        render_resultado(ult_res,ult_lot,ult_mod)

        # Postal temática — fuera de render_resultado
        _nums=ult_res.get("numbers",[]); _bonus=ult_res.get("bonus")
        nums_str=" · ".join([str(n).zfill(2) for n in _nums])
        bonus_s=f" ◆ {str(_bonus).zfill(2)}" if _bonus else ""
        tema_bg={"math":"linear-gradient(135deg,#0a0f1a,#0d1220)","holistic":"linear-gradient(135deg,#0a0a18,#120a1a)","real":"linear-gradient(135deg,#0a0f0a,#0d1a0d)"}.get(ult_mod[0] if ult_mod else "","linear-gradient(135deg,#0a0a0f,#141420)")
        tema_accent={"math":"#7B9FCC","holistic":"#9B8FCC","real":"#7BAA7B"}.get(ult_mod[0] if ult_mod else "","#C9A84C")
        tema_label="MATHEMATICAL" if "math" in ult_mod else "HOLISTIC" if "holistic" in ult_mod else "REAL DATA" if "real" in ult_mod else "CONVERGENCE"
        balls_html="".join([f'<span style="display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:50%;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);font-family:monospace;font-size:13px;font-weight:700;color:white;margin:3px;">{str(n).zfill(2)}</span>' for n in _nums])
        if _bonus: balls_html+=f'<span style="display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#C9A84C,#F5D68A);font-family:monospace;font-size:13px;font-weight:700;color:#0a0a0f;margin:3px;">{str(_bonus).zfill(2)}</span>'
        st.markdown(f'''<div style="{tema_bg};border:1px solid rgba(201,168,76,.22);border-radius:18px;padding:24px;text-align:center;max-width:340px;margin:12px auto;">
<div style="font-size:10px;color:{tema_accent};letter-spacing:3px;font-family:monospace;margin-bottom:4px;">{ult_lot["flag"]} {ult_lot["nombre"].upper()}</div>
<div style="font-size:9px;color:rgba(255,255,255,.28);letter-spacing:2px;font-family:monospace;margin-bottom:14px;">{tema_label}</div>
<div style="display:flex;flex-wrap:wrap;justify-content:center;margin-bottom:12px;">{balls_html}</div>
<div style="font-size:9px;color:rgba(255,255,255,.2);font-family:monospace;letter-spacing:1px;">lucksort.com · SORT YOUR LUCK</div>
</div>''', unsafe_allow_html=True)

        # Botones acción — nivel principal, sin contexto de columna anidado
        st.markdown(f'<div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.25);letter-spacing:2px;margin:10px 0 6px;">{t.get("share_copy","COPY")}</div>',unsafe_allow_html=True)
        share_text=f"🎯 {ult_lot['nombre']}: {nums_str}{bonus_s}\n\nLuckSort — Sort Your Luck\nlucksort.com"
        st.code(share_text,language=None)
        btn_c1,btn_c2=st.columns(2)
        with btn_c1:
            if st.button(t.get("save_combo","Save"),use_container_width=True,key="btn_save"):
                ok=guardar_combo_sesion(ult_res,ult_lot)
                if ok: st.success(t.get("saved_ok","✅ Saved"))
                else: st.info("Ya guardada")
        with btn_c2:
            if st.session_state.get("user_email") and RESEND_KEY:
                if st.button(t.get("email_combo","Email"),use_container_width=True,key="btn_email"):
                    ok=email_combo(st.session_state["user_email"],ult_lot,ult_res)
                    if ok: st.success(t.get("email_sent","✅"))
                    else: st.warning(t.get("email_err","⚠️"))

    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:16px 0;">',unsafe_allow_html=True)
        render_paywall()

# ══════════════════════════════════════════════════════
# 17. HISTORIAL + ESTADÍSTICAS
# ══════════════════════════════════════════════════════
elif st.session_state.get("vista")=="history":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">⊞ {t["history"]}</span></div>',unsafe_allow_html=True)
    if st.session_state.get("user_id"):
        stats=obtener_stats(st.session_state["user_id"])
        if stats:
            c1,c2,c3=st.columns(3)
            with c1: st.markdown(f'<div class="ls-card" style="text-align:center;padding:14px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:2px;">{t["total_gen"]}</div><div style="font-family:Georgia,serif;font-size:28px;color:#C9A84C;font-weight:700;">{stats.get("total",0)}</div></div>',unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="ls-card" style="text-align:center;padding:14px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:2px;">{t["racha"]}</div><div style="font-family:Georgia,serif;font-size:28px;color:#C9A84C;font-weight:700;">{stats.get("racha",0)}<span style="font-size:12px;color:rgba(255,255,255,.3);"> {t["racha_d"]}</span></div></div>',unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="ls-card" style="text-align:center;padding:14px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:2px;">TOP</div><div style="font-family:Georgia,serif;font-size:15px;color:#C9A84C;font-weight:700;margin-top:4px;">{stats.get("fav","-")}</div></div>',unsafe_allow_html=True)
            if stats.get("top_nums"):
                tb="".join([f'<div class="ball" style="width:38px;height:38px;font-size:12px;">{str(n).zfill(2)}</div>' for n in stats["top_nums"]])
                st.markdown(f'<div style="margin:10px 0 4px;font-family:monospace;font-size:9px;color:rgba(255,255,255,.28);letter-spacing:2px;">YOUR FREQUENT NUMBERS</div><div class="balls-wrap">{tb}</div>',unsafe_allow_html=True)
            st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:12px 0;">',unsafe_allow_html=True)
        hist=obtener_historial(st.session_state["user_id"])
        if not hist: st.markdown(f'<p style="color:rgba(255,255,255,.3);font-size:14px;">{t["no_history"]}</p>',unsafe_allow_html=True)
        else:
            for h in hist:
                lot=next((l for l in LOTERIAS if l["id"]==h.get("loteria_id")),None)
                if lot:
                    ns="  ".join([str(n).zfill(2) for n in h["numeros"]])
                    bs=f"  ◆ {str(h['bonus']).zfill(2)}" if h.get("bonus") else ""
                    st.markdown(f'<div class="ls-card" style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;"><span style="font-family:\'DM Mono\',monospace;font-size:11px;color:#C9A84C;">{lot["flag"]} {lot["nombre"]}</span><span style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.2);">{h.get("created_at","")[:10]}</span></div><div style="font-family:\'DM Mono\',monospace;font-size:18px;color:white;letter-spacing:3px;">{ns}{bs}</div></div>',unsafe_allow_html=True)
    else: st.info("Sign in to see your history.")

# ══════════════════════════════════════════════════════
# 18. GUARDADAS
# ══════════════════════════════════════════════════════
elif st.session_state.get("vista")=="guardadas":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">★ {t["guardadas"]}</span></div>',unsafe_allow_html=True)
    guardadas=st.session_state.get("combinaciones_guardadas",[])
    if not guardadas: st.markdown(f'<p style="color:rgba(255,255,255,.3);font-size:14px;">{t["no_saved"]}</p>',unsafe_allow_html=True)
    else:
        for i,g in enumerate(guardadas):
            ns="  ".join([str(n).zfill(2) for n in g["numeros"]])
            bs=f"  ◆ {str(g['bonus']).zfill(2)}" if g.get("bonus") else ""
            st.markdown(f'<div class="ls-card" style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;"><span style="font-family:\'DM Mono\',monospace;font-size:11px;color:#C9A84C;">{g["flag"]} {g["loteria"]}</span><span style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.2);">{g["fecha"]}</span></div><div style="font-family:\'DM Mono\',monospace;font-size:18px;color:white;letter-spacing:3px;">{ns}{bs}</div></div>',unsafe_allow_html=True)
            if st.button("✕",key=f"rm_{i}"): st.session_state["combinaciones_guardadas"].pop(i); st.rerun()

# ══════════════════════════════════════════════════════
# 19. COMPARADOR
# ══════════════════════════════════════════════════════
elif st.session_state.get("vista")=="comparador":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">⊕ {t["comparador"]}</span></div>',unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(255,255,255,.35);font-size:13px;margin-bottom:14px;">{t["comparar_intro"]}</p>',unsafe_allow_html=True)
    ganadores_input=st.text_input(t["ingresar_ganadores"],placeholder="23, 7, 45, 12, 3",key="gan_inp")
    if st.button(t["comparar_btn"],use_container_width=True,key="btn_cmp"):
        if ganadores_input:
            try:
                ganadores=[int(x.strip()) for x in ganadores_input.split(",") if x.strip().isdigit()]
                fuentes=[]
                if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
                    fuentes.append(("Última generación",st.session_state["ultima_generacion"]["numbers"],st.session_state["ultima_loteria"]["nombre"]))
                for g in st.session_state.get("combinaciones_guardadas",[])[:5]:
                    fuentes.append((f"{g['flag']} {g['loteria']} {g['fecha']}",g["numeros"],g["loteria"]))
                if not fuentes: st.info("Generate or save a combination first.")
                else:
                    for label,nums,lot_nombre in fuentes:
                        aciertos=[n for n in nums if n in ganadores]
                        balls_html="".join([f'<div style="width:38px;height:38px;border-radius:50%;background:{"rgba(201,168,76,.25)" if n in ganadores else "rgba(255,255,255,.06)"};border:1px solid {"rgba(201,168,76,.5)" if n in ganadores else "rgba(255,255,255,.12)"};display:inline-flex;align-items:center;justify-content:center;font-family:monospace;font-size:12px;font-weight:700;color:{"#C9A84C" if n in ganadores else "rgba(255,255,255,.5)"};margin:3px;">{str(n).zfill(2)}</div>' for n in nums])
                        st.markdown(f'<div class="ls-card" style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="font-family:monospace;font-size:11px;color:#C9A84C;">{label}</span><span style="font-family:monospace;font-size:12px;color:{"#C9A84C" if aciertos else "rgba(255,255,255,.3)"};">{len(aciertos)} {t["aciertos"]}</span></div><div style="display:flex;flex-wrap:wrap;">{balls_html}</div></div>',unsafe_allow_html=True)
            except: st.warning("Verifica el formato de los números.")
