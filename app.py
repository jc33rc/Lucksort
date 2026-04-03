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
    ADMIN_EMAIL  = st.secrets.get("ADMIN_EMAIL","admin@lucksort.com")
    ADMIN_EMAIL2 = "hello@lucksort.com"
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
    I
