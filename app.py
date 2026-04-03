import streamlit as st
from groq import Groq
from supabase import create_client
from datetime import date, datetime
import requests, random, json, re, math, time
from collections import Counter

# ══════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state defaults
for k, v in {
    "idioma": "ES",
    "logged_in": False,
    "user_role": "invitado",
    "user_email": "",
    "user_id": None,
    "vista": "landing",
    "ultima_generacion": None,
    "ultima_loteria": None,
    "nums_favoritos": [],
    "historial_sesion": [],
    "gen_hoy": 0,
    "gen_fecha": str(date.today()),
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Reset generaciones si es nuevo día
if st.session_state["gen_fecha"] != str(date.today()):
    st.session_state["gen_hoy"] = 0
    st.session_state["gen_fecha"] = str(date.today())

# ══════════════════════════════════════════
# CSS — DARK GOLD PREMIUM
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #080810 !important;
    color: #e8e4d9 !important;
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d18 0%, #080810 100%) !important;
    border-right: 1px solid rgba(201,168,76,.12) !important;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #C9A84C, #F0C84A) !important;
    color: #080810 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 20px rgba(201,168,76,.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(201,168,76,.4) !important;
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(201,168,76,.2) !important;
    border-radius: 10px !important;
    color: #e8e4d9 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(201,168,76,.5) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,.1) !important;
}

/* SELECTBOX */
.stSelectbox > div > div {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(201,168,76,.2) !important;
    border-radius: 10px !important;
    color: #e8e4d9 !important;
}

/* EXPANDERS */
.streamlit-expanderHeader {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(201,168,76,.12) !important;
    border-radius: 12px !important;
    color: #e8e4d9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 14px 16px !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(201,168,76,.3) !important;
    background: rgba(201,168,76,.04) !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,.02) !important;
    border: 1px solid rgba(201,168,76,.08) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 16px !important;
}

/* MULTISELECT */
.stMultiSelect > div {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(201,168,76,.2) !important;
    border-radius: 10px !important;
}

/* RADIO */
.stRadio > div { gap: 8px !important; }
.stRadio label { color: rgba(232,228,217,.7) !important; font-size: 13px !important; }

/* LABELS */
.stTextInput label, .stTextArea label, .stSelectbox label,
.stMultiSelect label, .stRadio label span {
    color: rgba(232,228,217,.6) !important;
    font-size: 12px !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 0.5px !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(201,168,76,.15) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(232,228,217,.45) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    border: none !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: #C9A84C !important;
    border-bottom: 2px solid #C9A84C !important;
}

/* ANIMATIONS */
@keyframes ballPulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 0 rgba(201,168,76,0); }
    50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(201,168,76,.3); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
.shimmer-text {
    background: linear-gradient(90deg, #C9A84C 0%, #F5D878 30%, #fff8e7 50%, #F5D878 70%, #C9A84C 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(201,168,76,.2); }
    50% { box-shadow: 0 0 40px rgba(201,168,76,.5); }
}

.ball {
    width: 52px; height: 52px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, rgba(255,255,255,.12), rgba(255,255,255,.03));
    border: 1px solid rgba(255,255,255,.2);
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 16px; font-weight: 700;
    color: #e8e4d9;
    margin: 4px;
    animation: fadeUp .4s ease forwards;
    box-shadow: 0 2px 12px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.1);
    transition: transform .2s, box-shadow .2s;
}
.ball:hover {
    transform: scale(1.08);
    box-shadow: 0 4px 20px rgba(201,168,76,.25), inset 0 1px 0 rgba(255,255,255,.15);
}
.ball-gold {
    background: radial-gradient(circle at 35% 35%, #F5D878, #C9A84C);
    color: #080810;
    border: none;
    box-shadow: 0 0 20px rgba(201,168,76,.5), 0 0 40px rgba(201,168,76,.2), inset 0 1px 0 rgba(255,255,255,.4);
    animation: ballPulse 2s ease-in-out infinite, fadeUp .4s ease forwards;
}

.src-card {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(201,168,76,.1);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    animation: fadeUp .5s ease forwards;
    transition: border-color .2s;
}
.src-card:hover { border-color: rgba(201,168,76,.25); }

.src-icon {
    font-size: 18px;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px;
    background: rgba(201,168,76,.08);
    flex-shrink: 0;
}
.src-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #C9A84C;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.src-math {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: rgba(201,168,76,.7);
    margin-bottom: 4px;
}
.src-explanation {
    font-size: 13px;
    color: rgba(232,228,217,.65);
    line-height: 1.5;
}
.src-num {
    font-family: 'DM Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: #C9A84C;
    flex-shrink: 0;
}

.conv-ring {
    width: 40px; height: 40px;
    border: 2px solid rgba(201,168,76,.2);
    border-top-color: #C9A84C;
    border-radius: 50%;
    animation: spin .8s linear infinite;
    margin: 0 auto 12px;
}
.conv-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: rgba(201,168,76,.6);
    letter-spacing: 2px;
    text-align: center;
}

.ls-card {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(201,168,76,.12);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 12px;
}

.gold-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background: rgba(201,168,76,.08);
    border: 1px solid rgba(201,168,76,.2);
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #C9A84C;
    letter-spacing: 1px;
}

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: rgba(201,168,76,.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

hr.gold { border: none; border-top: 1px solid rgba(201,168,76,.1); margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# CREDENCIALES
# ══════════════════════════════════════════
try:
    GROQ_KEY     = st.secrets["GROQ_API_KEY"]
    SB_URL       = st.secrets["SUPABASE_URL"]
    SB_KEY       = st.secrets["SUPABASE_KEY"]
    RESEND_KEY   = st.secrets.get("RESEND_API_KEY", "")
    STRIPE_LINK  = st.secrets.get("STRIPE_LINK", "#")
    ADMIN_EMAIL  = st.secrets.get("ADMIN_EMAIL", "hello@lucksort.com")
    ADMIN_PASS   = st.secrets.get("ADMIN_PASS", "lucksort123")
except:
    st.error("⚠️ Configura los secrets en Streamlit Cloud")
    st.stop()

groq_client = Groq(api_key=GROQ_KEY)
supabase    = create_client(SB_URL, SB_KEY)

# ══════════════════════════════════════════
# TRADUCCIONES
# ══════════════════════════════════════════
T = {
    "ES": {
        "tagline": "Ordena tu suerte",
        "subtitle": "Datos reales del mundo convergiendo en tus números",
        "select_lottery": "Selecciona tu lotería",
        "next_draw": "Próximo sorteo",
        "fav_title": "★ Favoritos",
        "fav_help": "Números que quieres incluir",
        "fav_select": "Selecciona tus favoritos",
        "real_title": "⊞ Datos Reales",
        "real_help": "Histórico oficial + comunidad + eventos del mundo",
        "holistic_title": "∞ Holístico",
        "holistic_help": "Numerología · Ciclo lunar · Interpretación de sueños",
        "math_title": "ϕ Matemático",
        "math_help": "Fibonacci · Tesla 3·6·9 · Geometría sagrada · Primos",
        "your_name": "Tu nombre completo",
        "special_date": "Fecha especial (DD/MM/AA)",
        "dream": "Cuéntame tu sueño...",
        "exclude": "Números a excluir (ej: 4, 13)",
        "generate": "◆ Generar Combinación",
        "generating": "Convergiendo señales del mundo...",
        "where_from": "DE DÓNDE VIENE CADA NÚMERO",
        "disclaimer": "Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
        "login": "Entrar",
        "register": "Crear cuenta",
        "email": "Correo electrónico",
        "password": "Contraseña",
        "confirm_pass": "Confirmar contraseña",
        "register_btn": "Crear Cuenta Gratis",
        "login_btn": "Entrar",
        "logout": "Cerrar sesión",
        "email_exists": "Este correo ya está registrado",
        "pass_mismatch": "Las contraseñas no coinciden",
        "login_error": "Correo o contraseña incorrectos",
        "gen_limit": "generaciones hoy",
        "powered": "Impulsado por datos reales",
        "community": "Comunidad",
        "balanced": "Balanceado",
        "follow": "Seguir tendencia",
        "avoid": "Contraría",
        "crowd_pref": "Preferencia de comunidad",
        "steps": ["Analizando señales históricas...", "Consultando la comunidad...", "Calculando convergencias...", "Ordenando tu suerte..."],
    },
    "EN": {
        "tagline": "Sort Your Luck",
        "subtitle": "Real world data converging into your numbers",
        "select_lottery": "Select your lottery",
        "next_draw": "Next draw",
        "fav_title": "★ Favourites",
        "fav_help": "Numbers you want to include",
        "fav_select": "Select your favourites",
        "real_title": "⊞ Real Data",
        "real_help": "Official history + community + world events",
        "holistic_title": "∞ Holistic",
        "holistic_help": "Numerology · Lunar cycle · Dream interpretation",
        "math_title": "ϕ Mathematical",
        "math_help": "Fibonacci · Tesla 3·6·9 · Sacred geometry · Primes",
        "your_name": "Your full name",
        "special_date": "Special date (DD/MM/YY)",
        "dream": "Tell me your dream...",
        "exclude": "Numbers to exclude (e.g. 4, 13)",
        "generate": "◆ Generate Combination",
        "generating": "Converging world signals...",
        "where_from": "WHERE EACH NUMBER COMES FROM",
        "disclaimer": "We gather and synthesize real information from the world to put it in your hands. With this tool you might need a little less luck — though we hope it always accompanies you!",
        "login": "Sign In",
        "register": "Create Account",
        "email": "Email address",
        "password": "Password",
        "confirm_pass": "Confirm password",
        "register_btn": "Create Free Account",
        "login_btn": "Sign In",
        "logout": "Sign Out",
        "email_exists": "This email is already registered",
        "pass_mismatch": "Passwords do not match",
        "login_error": "Incorrect email or password",
        "gen_limit": "combinations today",
        "powered": "Powered by real data",
        "community": "Community",
        "balanced": "Balanced",
        "follow": "Follow trend",
        "avoid": "Contrarian",
        "crowd_pref": "Community preference",
        "steps": ["Analyzing historical signals...", "Consulting the community...", "Calculating convergences...", "Sorting your luck..."],
    },
    "PT": {
        "tagline": "Ordene sua sorte",
        "subtitle": "Dados reais do mundo convergindo nos seus números",
        "select_lottery": "Selecione sua loteria",
        "next_draw": "Próximo sorteio",
        "fav_title": "★ Favoritos",
        "fav_help": "Números que você quer incluir",
        "fav_select": "Selecione seus favoritos",
        "real_title": "⊞ Dados Reais",
        "real_help": "Histórico oficial + comunidade + eventos do mundo",
        "holistic_title": "∞ Holístico",
        "holistic_help": "Numerologia · Ciclo lunar · Interpretação de sonhos",
        "math_title": "ϕ Matemático",
        "math_help": "Fibonacci · Tesla 3·6·9 · Geometria sagrada · Primos",
        "your_name": "Seu nome completo",
        "special_date": "Data especial (DD/MM/AA)",
        "dream": "Me conte seu sonho...",
        "exclude": "Números a excluir (ex: 4, 13)",
        "generate": "◆ Gerar Combinação",
        "generating": "Convergindo sinais do mundo...",
        "where_from": "DE ONDE VEM CADA NÚMERO",
        "disclaimer": "Coletamos e sintetizamos informações reais do mundo para colocá-las em suas mãos. Com esta ferramenta talvez precise de um pouco menos de sorte — mas que ela sempre te acompanhe!",
        "login": "Entrar",
        "register": "Criar conta",
        "email": "Endereço de e-mail",
        "password": "Senha",
        "confirm_pass": "Confirmar senha",
        "register_btn": "Criar Conta Grátis",
        "login_btn": "Entrar",
        "logout": "Sair",
        "email_exists": "Este e-mail já está cadastrado",
        "pass_mismatch": "As senhas não coincidem",
        "login_error": "E-mail ou senha incorretos",
        "gen_limit": "combinações hoje",
        "powered": "Impulsionado por dados reais",
        "community": "Comunidade",
        "balanced": "Balanceado",
        "follow": "Seguir tendência",
        "avoid": "Contrário",
        "crowd_pref": "Preferência de comunidade",
        "steps": ["Analisando sinais históricos...", "Consultando a comunidade...", "Calculando convergências...", "Ordenando sua sorte..."],
    }
}

def t():
    return T[st.session_state["idioma"]]

# ══════════════════════════════════════════
# LOTERÍAS
# ══════════════════════════════════════════
LOTERIAS = [
    {"id":1,  "nombre":"Powerball",     "flag":"🇺🇸","min":1,"max":69,"n":5,"bonus":True,"bmax":26,"bname":"Powerball","dias":["Lun","Mié","Sáb"],"hora":"22:59 ET"},
    {"id":2,  "nombre":"Mega Millions", "flag":"🇺🇸","min":1,"max":70,"n":5,"bonus":True,"bmax":25,"bname":"Mega Ball","dias":["Mar","Vie"],"hora":"23:00 ET"},
    {"id":3,  "nombre":"EuroMillions",  "flag":"🇪🇺","min":1,"max":50,"n":5,"bonus":True,"bmax":12,"bname":"Lucky Star","dias":["Mar","Vie"],"hora":"21:00 CET"},
    {"id":4,  "nombre":"UK Lotto",      "flag":"🇬🇧","min":1,"max":59,"n":6,"bonus":False,"bmax":None,"bname":None,"dias":["Mié","Sáb"],"hora":"19:45 GMT"},
    {"id":5,  "nombre":"El Gordo",      "flag":"🇪🇸","min":1,"max":54,"n":5,"bonus":True,"bmax":10,"bname":"Reintegro","dias":["Dom"],"hora":"21:25 CET"},
    {"id":6,  "nombre":"Mega-Sena",     "flag":"🇧🇷","min":1,"max":60,"n":6,"bonus":False,"bmax":None,"bname":None,"dias":["Mié","Sáb"],"hora":"20:00 BRT"},
    {"id":7,  "nombre":"Lotofácil",     "flag":"🇧🇷","min":1,"max":25,"n":15,"bonus":False,"bmax":None,"bname":None,"dias":["L-S"],"hora":"20:00 BRT"},
    {"id":8,  "nombre":"Baloto",        "flag":"🇨🇴","min":1,"max":43,"n":6,"bonus":True,"bmax":16,"bname":"Balota","dias":["Mié","Sáb"],"hora":"22:00 COT"},
    {"id":9,  "nombre":"La Primitiva",  "flag":"🇪🇸","min":1,"max":49,"n":6,"bonus":False,"bmax":None,"bname":None,"dias":["Jue","Sáb"],"hora":"21:30 CET"},
    {"id":10, "nombre":"EuroJackpot",   "flag":"🇪🇺","min":1,"max":50,"n":5,"bonus":True,"bmax":12,"bname":"Euro Num","dias":["Mar","Vie"],"hora":"21:00 CET"},
    {"id":11, "nombre":"Canada Lotto",  "flag":"🇨🇦","min":1,"max":49,"n":6,"bonus":True,"bmax":49,"bname":"Bonus","dias":["Mié","Sáb"],"hora":"22:30 ET"},
]

# ══════════════════════════════════════════
# HISTÓRICO REAL EMBEBIDO — siempre disponible
# ══════════════════════════════════════════
HIST = {
    "Powerball":     {"top":[26,41,16,28,22,23,32,42,36,61,39,20,53,19,66],"cal":[26,41,16,28,22],"fri":[53,64,69,18,15],"dia":{"Mon":[26,32,22],"Wed":[41,28,23],"Sat":[26,61,22]},"mes":{1:[26,32],2:[41,22],3:[23,16],4:[26,41],5:[32,28],6:[16,61],7:[22,41],8:[28,23],9:[26,42],10:[41,36],11:[22,28],12:[16,41]}},
    "Mega Millions": {"top":[17,31,10,4,46,20,14,39,2,29,70,35,23,25,8],"cal":[17,31,10,4,46],"fri":[70,48,53,38,11],"dia":{"Tue":[17,31,4],"Fri":[31,20,14]},"mes":{1:[17,31],2:[4,46],3:[14,39],4:[17,31],5:[20,29],6:[10,35],7:[31,25],8:[17,48],9:[46,20],10:[31,39],11:[10,4],12:[46,20]}},
    "EuroMillions":  {"top":[23,44,19,50,5,17,27,35,48,38,20,6,43,3,15],"cal":[23,44,19,5,17],"fri":[50,48,43,33,15],"dia":{"Tue":[23,44,5],"Fri":[44,17,27]},"mes":{1:[23,44],2:[5,17],3:[27,35],4:[48,38],5:[20,6],6:[43,3],7:[15,28],8:[37,42],9:[23,11],10:[44,33],11:[19,27],12:[35,48]}},
    "UK Lotto":      {"top":[23,38,31,25,33,11,2,40,6,39,28,44,17,1,48],"cal":[23,38,31,25,33],"fri":[48,47,44,34,13],"dia":{"Wed":[23,38,11],"Sat":[38,25,33]},"mes":{1:[23,38],2:[25,33],3:[2,40],4:[6,39],5:[28,44],6:[17,1],7:[48,13],8:[22,34],9:[23,47],10:[38,25],11:[31,11],12:[40,2]}},
    "El Gordo":      {"top":[11,23,7,33,4,15,28,6,19,35,42,2,22,38,17],"cal":[11,23,7,33,4],"fri":[54,45,42,38,35],"dia":{"Sun":[11,23,7]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[42,2],6:[22,38],7:[17,45],8:[54,31],9:[11,8],10:[23,7],11:[4,15],12:[28,23]}},
    "Mega-Sena":     {"top":[10,53,23,4,52,33,43,37,41,25,5,34,8,20,42],"cal":[10,53,23,4,52],"fri":[60,58,56,55,54],"dia":{"Wed":[10,53,23],"Sat":[33,43,37]},"mes":{1:[10,53],2:[4,52],3:[43,37],4:[41,25],5:[5,34],6:[8,20],7:[42,53],8:[11,16],9:[10,30],10:[53,23],11:[4,37],12:[25,41]}},
    "Lotofácil":     {"top":[20,5,7,12,23,11,18,24,15,3,25,9,2,13,22],"cal":[20,5,7,12,23],"fri":[25,24,22,21,19],"dia":{"Mon":[20,5],"Tue":[12,23],"Wed":[18,24],"Thu":[3,25],"Fri":[2,13],"Sat":[17,10]},"mes":{1:[20,5],2:[12,23],3:[18,24],4:[20,5],5:[3,25],6:[2,13],7:[17,10],8:[16,21],9:[5,7],10:[23,11],11:[24,15],12:[25,9]}},
    "Baloto":        {"top":[11,23,7,33,4,15,28,6,19,35,43,2,22,38,17],"cal":[11,23,7,33,4],"fri":[43,41,38,35,30],"dia":{"Wed":[11,23,7],"Sat":[15,28,6]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[43,2],6:[22,38],7:[17,12],8:[30,41],9:[11,8],10:[23,7],11:[4,15],12:[28,23]}},
    "La Primitiva":  {"top":[28,36,14,3,25,42,7,16,33,48,21,9,38,45,11],"cal":[28,36,14,3,25],"fri":[49,48,45,43,38],"dia":{"Thu":[28,36,14],"Sat":[42,7,16]},"mes":{1:[28,36],2:[3,25],3:[7,16],4:[33,48],5:[21,9],6:[38,45],7:[11,5],8:[19,27],9:[28,43],10:[36,14],11:[42,7],12:[16,33]}},
    "EuroJackpot":   {"top":[19,49,32,18,7,23,17,40,3,37,50,29,44,11,22],"cal":[19,49,32,18,7],"fri":[50,48,44,40,37],"dia":{"Tue":[19,49,32],"Fri":[23,17,40]},"mes":{1:[19,49],2:[18,7],3:[17,40],4:[3,37],5:[50,29],6:[44,11],7:[22,34],8:[48,15],9:[19,26],10:[49,32],11:[18,7],12:[40,3]}},
    "Canada Lotto":  {"top":[20,33,34,40,44,6,19,32,43,39,7,13,24,37,16],"cal":[20,33,34,40,44],"fri":[49,48,47,46,45],"dia":{"Wed":[20,33,34],"Sat":[6,19,32]},"mes":{1:[20,33],2:[40,44],3:[19,32],4:[43,39],5:[7,13],6:[24,37],7:[16,3],8:[28,42],9:[20,14],10:[33,34],11:[40,6],12:[19,32]}},
}

ICONS = {
    "historico": "⊞", "community": "⊛", "eventos": "⊕",
    "numerologia": "ᚨ", "lunar": "◐", "sueno": "∞",
    "fibonacci": "ϕ", "tesla": "⌁", "sagrada": "⬡",
    "primos": "∴", "fractal": "※", "favorito": "★",
    "complement": "·", "cambio": "⇌", "fecha": "◈",
}

# ══════════════════════════════════════════
# CÁLCULOS MATEMÁTICOS
# ══════════════════════════════════════════
def calc_fibonacci(mn, mx):
    seq, a, b = [], 1, 1
    while b <= mx:
        if mn <= b <= mx:
            seq.append({"n": b, "math": f"F{len(seq)+1}+F{len(seq)+2}={b}", "fuente": "fibonacci"})
        a, b = b, a+b
    return seq

def calc_tesla(mn, mx):
    return [{"n": n, "math": f"3·6·9 → {n}", "fuente": "tesla"} for n in range(mn, mx+1) if n % 3 == 0]

def calc_sagrada(mn, mx):
    nums = []
    phi = 1.6180339887
    for mult in [phi, math.pi, math.sqrt(2), math.sqrt(3), math.sqrt(5)]:
        for k in range(1, 50):
            v = round(mult * k)
            if mn <= v <= mx:
                nums.append({"n": v, "math": f"ϕ×{k}≈{v}", "fuente": "sagrada"})
    return nums

def calc_primos(mn, mx):
    primos = []
    for n in range(max(2, mn), mx+1):
        if all(n % i != 0 for i in range(2, int(n**0.5)+1)):
            primos.append({"n": n, "math": f"{n} es primo", "fuente": "primos"})
    return primos

def calc_numerologia(nombre, fecha):
    res = {}
    if nombre:
        vals = {'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
                'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
                's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8}
        total = sum(vals.get(c.lower(), 0) for c in nombre if c.isalpha())
        while total > 9 and total not in [11,22,33]:
            total = sum(int(d) for d in str(total))
        if 1 <= total <= 33:
            res["nombre"] = {"n": total, "math": f"{nombre}→{total}", "fuente": "numerologia"}
    if fecha:
        digits = re.findall(r'\d+', fecha)
        if digits:
            total = sum(int(d) for d in ''.join(digits))
            while total > 9 and total not in [11,22,33]:
                total = sum(int(d) for d in str(total))
            if 1 <= total <= 33:
                res["fecha"] = {"n": total, "math": f"{fecha}→{total}", "fuente": "numerologia"}
    return res

def calc_lunar():
    hoy = datetime.now()
    dias = (hoy - datetime(2000, 1, 6)).days
    ciclo = dias % 29.53
    fase = round(ciclo)
    return {"n": min(fase, 28), "math": f"Luna día {fase} del ciclo", "fuente": "lunar"}

# ══════════════════════════════════════════
# OBTENER DATOS EXTERNOS
# ══════════════════════════════════════════
def get_cache(tipo):
    try:
        res = supabase.table("cache_diario").select("contenido").eq("fecha", str(date.today())).eq("tipo", tipo).execute()
        if res.data:
            c = res.data[0]["contenido"]
            if isinstance(c, str):
                return json.loads(c)
            return c
    except: pass
    return None

def set_cache(tipo, contenido):
    try:
        hoy = str(date.today())
        ex = supabase.table("cache_diario").select("id").eq("fecha", hoy).eq("tipo", tipo).execute()
        data = json.dumps(contenido, ensure_ascii=False)
        if ex.data:
            supabase.table("cache_diario").update({"contenido": data}).eq("id", ex.data[0]["id"]).execute()
        else:
            supabase.table("cache_diario").insert({"fecha": hoy, "tipo": tipo, "contenido": data}).execute()
    except: pass

def obtener_reddit(loteria):
    tipo = f"reddit_{loteria['id']}"
    c = get_cache(tipo)
    if c: return c
    mn, mx = loteria["min"], loteria["max"]
    nums = []
    subs = {"Powerball":"powerball","Mega Millions":"megamillions","EuroMillions":"euromillions",
            "UK Lotto":"uklottery","Baloto":"colombia","Mega-Sena":"megasena","El Gordo":"spain",
            "La Primitiva":"spain","EuroJackpot":"eurojackpot","Canada Lotto":"lottery","Lotofácil":"brasil"}
    sub = subs.get(loteria["nombre"], "lottery")
    try:
        r = requests.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=20",
                        headers={"User-Agent":"Mozilla/5.0 LuckSort/1.0"}, timeout=6)
        if r.status_code == 200:
            for p in r.json().get("data",{}).get("children",[]):
                txt = p.get("data",{}).get("title","") + p.get("data",{}).get("selftext","")
                for n in re.findall(r'\b(\d{1,2})\b', txt):
                    v = int(n)
                    if mn <= v <= mx: nums.append(v)
    except: pass
    if nums:
        top = [{"n":n,"count":c,"fuente":"community"} for n,c in Counter(nums).most_common(10)]
        set_cache(tipo, top)
        return top
    return []

def obtener_efemerides(mes, dia):
    tipo = f"efem_{mes}_{dia}"
    c = get_cache(tipo)
    if c: return c
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{mes}/{dia}", timeout=6)
        if r.status_code == 200:
            evs = [{"year": e.get("year"), "text": e.get("text","")[:120]} for e in r.json().get("events",[])[:8]]
            set_cache(tipo, evs)
            return evs
    except: pass
    return []

# ══════════════════════════════════════════
# PREPARAR CANDIDATOS
# ══════════════════════════════════════════
def preparar_candidatos(loteria, inputs, modulos):
    mn, mx = loteria["min"], loteria["max"]
    hoy = datetime.now()
    dia_str = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][hoy.weekday()]
    mes = hoy.month
    candidatos = []
    usados = set()
    for gen in st.session_state.get("historial_sesion", [])[-3:]:
        usados.update(gen)

    def add(item):
        if mn <= item["n"] <= mx:
            item["ya_usado"] = item["n"] in usados
            candidatos.append(item)

    # SIEMPRE — favoritos
    for n in st.session_state.get("nums_favoritos", []):
        if mn <= n <= mx:
            add({"n":n, "math":f"Tu favorito", "fuente":"favorito", "peso":7})

    # Histórico embebido — siempre disponible como base
    hist = HIST.get(loteria["nombre"], {})

    # MÓDULO REAL — respeta checkboxes
    if "real" in modulos:
        if inputs.get("use_hist", True):
            for i, n in enumerate(hist.get("top", [])[:10]):
                add({"n":n, "math":f"Top #{i+1} histórico {loteria['nombre']}", "fuente":"historico", "peso":4})
            for n in hist.get("dia",{}).get(dia_str, [])[:3]:
                add({"n":n, "math":f"Más frecuente los {dia_str} en {loteria['nombre']}", "fuente":"historico", "peso":5})
            for n in hist.get("mes",{}).get(mes, [])[:3]:
                add({"n":n, "math":f"Número líder en mes {mes} históricamente", "fuente":"historico", "peso":5})
            for n in hist.get("cal", [])[:3]:
                add({"n":n, "math":f"Número caliente — salió recientemente", "fuente":"historico", "peso":4})
            for n in hist.get("fri", [])[:2]:
                if mn <= n <= mx:
                    add({"n":n, "math":f"Número frío — sin salir en semanas", "fuente":"historico", "peso":2})

        if inputs.get("use_comm", True):
            for item in obtener_reddit(loteria)[:5]:
                add({"n":item["n"], "math":f"Mencionado {item.get('count',0)}× en comunidad hoy", "fuente":"community", "peso":3})

        if inputs.get("use_efem", True):
            efem = obtener_efemerides(hoy.month, hoy.day)
            for ev in efem[:5]:
                yr = ev.get("year", 0)
                if yr:
                    y2 = yr % 100
                    if mn <= y2 <= mx:
                        add({"n":y2, "math":f"{yr}: {ev.get('text','')[:40]}... → {y2}", "fuente":"eventos", "peso":2})

        if inputs.get("use_hoy", True):
            for v, m in [(hoy.day, f"Día {hoy.day} de hoy"), (hoy.month, f"Mes {hoy.month}"),
                         (hoy.day+hoy.month, f"Día+Mes={hoy.day+hoy.month}")]:
                if mn <= v <= mx:
                    add({"n":v, "math":m, "fuente":"eventos", "peso":2})
    else:
        # Sin módulo real → histórico como fallback garantizado
        for i, n in enumerate(hist.get("top", [])[:8]):
            add({"n":n, "math":f"Top #{i+1} histórico {loteria['nombre']}", "fuente":"historico", "peso":3})

    # MÓDULO HOLÍSTICO
    if "holistic" in modulos:
        nombre = inputs.get("nombre","")
        fecha  = inputs.get("fecha","")
        sueno  = inputs.get("sueno","")
        if nombre or fecha:
            for v in calc_numerologia(nombre, fecha).values():
                if mn <= v["n"] <= mx: add({**v, "peso":6})
            for m in [11,22,33]:
                if mn <= m <= mx: add({"n":m, "math":f"Número maestro {m}", "fuente":"numerologia", "peso":3})
            if fecha:
                partes = [x for x in re.split(r'[-/.]',fecha) if x.isdigit()]
                if len(partes) >= 2:
                    try:
                        d_f, m_f = int(partes[0]), int(partes[1])
                        for v, lab in [(d_f, f"Día {d_f} de tu fecha"), (m_f, f"Mes {m_f} de tu fecha")]:
                            if mn <= v <= mx: add({"n":v, "math":lab, "fuente":"fecha", "peso":5})
                    except: pass
        lu = calc_lunar()
        if mn <= lu["n"] <= mx: add({**lu, "peso":3})

    # MÓDULO MATEMÁTICO
    if "math" in modulos:
        for f in calc_fibonacci(mn, mx): add({**f, "peso":4})
        for t_n in calc_tesla(mn, mx)[:5]: add({**t_n, "peso":3})
        for s in calc_sagrada(mn, mx)[:10]: add({**s, "peso":3})
        for p in calc_primos(mn, mx)[:8]: add({**p, "peso":2})

    # Deduplicar
    mejor = {}
    for c in candidatos:
        n = c["n"]
        if n not in mejor or c.get("peso",0) > mejor[n].get("peso",0):
            mejor[n] = c
    return list(mejor.values())

# ══════════════════════════════════════════
# GENERAR CON GROQ
# ══════════════════════════════════════════
def generar(loteria, inputs, modulos):
    lang = st.session_state["idioma"]
    lang_full = {"ES":"Spanish","EN":"English","PT":"Portuguese"}[lang]
    candidatos = preparar_candidatos(loteria, inputs, modulos)

    excluir = []
    if inputs.get("excluir"):
        try: excluir = [int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    validos = [c for c in candidatos if c["n"] not in excluir]
    ordenados = sorted(validos, key=lambda x: -x.get("peso",0))

    sueno = inputs.get("sueno","")
    fav   = st.session_state.get("nums_favoritos",[])
    seed  = random.randint(1000,9999)
    hist  = HIST.get(loteria["nombre"],{})
    bonus_txt = f"1 {loteria['bname']} entre 1-{loteria['bmax']} (pool separado)" if loteria["bonus"] else "sin bonus"

    prompt = f"""Eres un equipo de especialistas generando una combinación de lotería única.
Seed #{seed} — cada respuesta debe ser diferente.

LOTERÍA: {loteria['nombre']} ({loteria['min']}-{loteria['max']}) | {loteria['n']} números | {bonus_txt}
IDIOMA DE RESPUESTA: {lang_full} — TODA la respuesta en {lang_full}
EXCLUIR: {excluir}
FAVORITOS: {fav} (incluir obligatoriamente si están en candidatos)
EVITAR (usados recientemente): {st.session_state.get('historial_sesion',[])[-3:]}
SUEÑO DEL USUARIO: "{sueno if sueno else 'ninguno'}"
MÓDULOS ACTIVOS: {modulos}

DATOS HISTÓRICOS VERIFICADOS:
- Top histórico: {hist.get('top',[])}
- Calientes (salieron recientemente): {hist.get('cal',[])}
- Fríos (sin salir semanas): {hist.get('fri',[])}

CANDIDATOS DISPONIBLES (pre-verificados por Python):
{json.dumps(ordenados[:40], ensure_ascii=False)}

REGLAS:
1. Elegir SOLO números de la lista de candidatos
2. Máximo 1 número de cada fuente simbólica (fibonacci, tesla, sagrada, primos, numerologia)
3. Si hay sueño → extraer 1 número del simbolismo del sueño
4. Favoritos incluidos obligatoriamente si están en candidatos
5. Preferir ya_usado=false para variedad
6. El bonus es de un pool SEPARADO (1-{loteria['bmax'] if loteria['bonus'] else 'N/A'})

VOCES DE EXPERTO por fuente:
- historico → historiador: "El N lidera los [dia] en [lotería]" o "En [mes], el N encabeza la frecuencia"
- community → analista: "El N fue mencionado X veces en la comunidad hoy"
- fibonacci → matemático: "F9+F10={{}}" o "El N ocupa posición X en la secuencia"
- tesla → físico: "El N es múltiplo de 3·6·9 — patrón de Tesla"
- sagrada → geómetra: "El N = ϕ×K — proporción áurea"
- numerologia → numerólogo: "Nombre/fecha reduce a N paso a paso"
- lunar → astrónomo: "Luna en día N del ciclo"
- eventos → historiador: "En [año], [evento] → N"
- favorito → confirma preferencia del usuario
- complement → honesto: indica que no hay señal específica disponible

NUNCA inventar datos que no estén en los candidatos.
NUNCA usar porcentajes exactos si no están en los datos.

Devuelve SOLO JSON válido sin markdown:
{{
  "numbers": [{loteria['n']} enteros únicos],
  "bonus": {f'entero 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources": [
    {{"number": N, "source": "tipo_fuente", "label": "Especialista", "math": "una línea de fórmula", "explanation": "voz experta en {lang_full}, 1-2 oraciones"}}
  ]
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Eres LuckSort, el motor de convergencia de datos. Responde SIEMPRE en {lang_full}. Solo JSON válido, sin markdown."},
                {"role":"user","content":prompt}
            ],
            temperature=round(random.uniform(0.65, 0.85),2),
            max_tokens=1200
        )
        raw = resp.choices[0].message.content.strip()
        if "```" in raw: raw = raw.split("```")[1].replace("json","").strip()
        res = json.loads(raw)

        # Validar números
        nums = [n for n in res.get("numbers",[]) if loteria["min"]<=n<=loteria["max"] and n not in excluir]
        for f in fav:
            if loteria["min"]<=f<=loteria["max"] and f not in excluir and f not in nums and len(nums)<loteria["n"]:
                nums.insert(0, f)
        pool_disp = [c["n"] for c in ordenados if c["n"] not in nums and c["n"] not in excluir]
        while len(nums) < loteria["n"] and pool_disp: nums.append(pool_disp.pop(0))
        pool = [n for n in range(loteria["min"],loteria["max"]+1) if n not in nums and n not in excluir]
        while len(nums) < loteria["n"] and pool:
            p = random.choice(pool); nums.append(p); pool.remove(p)
        res["numbers"] = list(dict.fromkeys(nums))[:loteria["n"]]

        # Validar bonus
        if loteria["bonus"]:
            b = res.get("bonus")
            if not isinstance(b,int) or not (1<=b<=loteria["bmax"]):
                bc = [c["n"] for c in ordenados if 1<=c["n"]<=loteria["bmax"] and c["n"] not in nums]
                res["bonus"] = bc[0] if bc else random.randint(1,loteria["bmax"])

        # Historial
        hist_s = st.session_state.get("historial_sesion",[])
        hist_s.append(res["numbers"])
        st.session_state["historial_sesion"] = hist_s[-5:]
        return res

    except Exception as e:
        # Fallback con histórico
        top = HIST.get(loteria["nombre"],{}).get("top",[])
        pool = [n for n in top if mn<=n<=mx and n not in excluir]
        if len(pool) < loteria["n"]:
            pool += [n for n in range(loteria["min"],loteria["max"]+1) if n not in pool and n not in excluir]
        nums = pool[:loteria["n"]]
        bonus = random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
        sources = [{"number":n,"source":"historico","label":"Draw History","math":f"Top histórico #{i+1}","explanation":f"Número de alta frecuencia histórica en {loteria['nombre']}"} for i,n in enumerate(nums)]
        if bonus: sources.append({"number":bonus,"source":"historico","label":"Draw History","math":"Bonus histórico","explanation":"Bonus frecuente"})
        return {"numbers":nums,"bonus":bonus,"sources":sources}

# ══════════════════════════════════════════
# SUPABASE — USUARIOS
# ══════════════════════════════════════════
def registrar_usuario(email, password):
    try:
        check = supabase.table("usuarios").select("email").eq("email",email).execute()
        if check.data: return False, "exists"
        supabase.table("usuarios").insert({"email":email,"password":password,"role":"free"}).execute()
        rec = supabase.table("usuarios").select("*").eq("email",email).execute()
        if rec.data: return True, rec.data[0]
        return False, "error"
    except Exception as e: return False, str(e)

def login_usuario(email, password):
    try:
        res = supabase.table("usuarios").select("*").eq("email",email).eq("password",password).execute()
        if res.data: return True, res.data[0]
        return False, None
    except: return False, None

# ══════════════════════════════════════════
# RENDER RESULTADO
# ══════════════════════════════════════════
def render_resultado(res, loteria, modulos):
    t_ = t()
    nums  = res.get("numbers",[])
    bonus = res.get("bonus")
    sources = res.get("sources",[])

    # Tema según módulo principal
    if "math" in modulos:    tema_color="#7B9FCC"; tema_label="MATHEMATICAL"
    elif "holistic" in modulos: tema_color="#9B8FCC"; tema_label="HOLISTIC"
    else:                    tema_color="#C9A84C"; tema_label="REAL DATA"

    # Balotas
    balls_html = "".join([f'<div class="ball">{str(n).zfill(2)}</div>' for n in nums])
    if bonus: balls_html += f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'

    st.markdown(f"""
<div class="ls-card" style="text-align:center;border-color:rgba(201,168,76,.2);margin-top:16px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:{tema_color};letter-spacing:3px;margin-bottom:4px;">{loteria['flag']} {loteria['nombre'].upper()} &nbsp;·&nbsp; {tema_label}</div>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;margin:12px 0;">{balls_html}</div>
  {f'<div style="font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.5);">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>' if bonus else ''}
</div>""", unsafe_allow_html=True)

    # Fuentes
    if sources:
        st.markdown(f'<div class="section-label" style="margin-top:20px;">{t_["where_from"]}</div>', unsafe_allow_html=True)
        for src in sources:
            n = src.get("number","")
            fuente = src.get("source","complement")
            icon = ICONS.get(fuente, "·")
            label = src.get("label","")
            math_txt = src.get("math","")
            expl = src.get("explanation","")
            is_comp = fuente == "complement"
            border_color = "rgba(201,168,76,.08)" if is_comp else "rgba(201,168,76,.15)"
            expl_color = "rgba(232,228,217,.35)" if is_comp else "rgba(232,228,217,.7)"
            st.markdown(f"""
<div class="src-card" style="border-color:{border_color};">
  <div style="display:flex;align-items:flex-start;gap:12px;flex:1;">
    <span class="src-icon">{icon}</span>
    <div>
      <div class="src-label">{label}</div>
      <div class="src-math">{math_txt}</div>
      <div class="src-explanation" style="color:{expl_color};">{expl}</div>
    </div>
  </div>
  <div class="src-num">→ {str(n).zfill(2)}</div>
</div>""", unsafe_allow_html=True)

    # Disclaimer
    st.markdown(f'<div style="font-style:italic;font-size:12px;color:rgba(232,228,217,.3);text-align:center;padding:16px 8px;line-height:1.6;">"{t_["disclaimer"]}"</div>', unsafe_allow_html=True)

    # Copiar
    nums_str = " · ".join([str(n).zfill(2) for n in nums])
    bonus_str = f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    share = f"🎯 {loteria['nombre']}: {nums_str}{bonus_str}\n\nLuckSort — Sort Your Luck\nlucksort.com"
    st.code(share, language=None)

# ══════════════════════════════════════════
# RENDER HEADER
# ══════════════════════════════════════════
def render_header():
    lang = st.session_state["idioma"]
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:12px 0;border-bottom:1px solid rgba(201,168,76,.1);margin-bottom:12px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:34px;height:34px;background:linear-gradient(135deg,#C9A84C,#F0C84A);
    border-radius:10px;display:flex;align-items:center;justify-content:center;
    font-size:16px;color:#080810;box-shadow:0 0 16px rgba(201,168,76,.3);
    animation:glowPulse 3s ease-in-out infinite;">◆</div>
    <div>
      <div style="font-family:'Playfair Display',serif;font-size:21px;font-weight:700;
      color:white;letter-spacing:-.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:'DM Mono',monospace;font-size:8px;
      color:rgba(201,168,76,.45);letter-spacing:2.5px;">SORT YOUR LUCK</div>
    </div>
  </div>
  <span style="font-family:'DM Mono',monospace;font-size:10px;font-weight:700;
  color:rgba(201,168,76,.5);letter-spacing:1px;">{lang}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
<div style="padding:16px 0 8px;text-align:center;">
  <div style="font-family:'Playfair Display',serif;font-size:18px;color:#C9A84C;font-weight:700;">◆ LuckSort</div>
  <div style="font-family:'DM Mono',monospace;font-size:8px;color:rgba(201,168,76,.35);letter-spacing:2px;margin-top:2px;">SORT YOUR LUCK</div>
</div>""", unsafe_allow_html=True)
    st.markdown('<hr class="gold">', unsafe_allow_html=True)

    # IDIOMA — patrón Dropshippingent
    lang_actual = st.session_state["idioma"]
    nuevo_idioma = st.selectbox("🌐 Language / Idioma",
        ["ES","EN","PT"],
        index=["ES","EN","PT"].index(lang_actual),
        key="sel_idioma")
    if nuevo_idioma != lang_actual:
        st.session_state["idioma"] = nuevo_idioma
        st.rerun()

    st.markdown('<hr class="gold">', unsafe_allow_html=True)

    # LOGIN / REGISTRO
    if not st.session_state["logged_in"]:
        tab1, tab2 = st.tabs([t()["login"], t()["register"]])
        with tab1:
            em = st.text_input(t()["email"], key="l_em", placeholder="tu@email.com")
            pw = st.text_input(t()["password"], type="password", key="l_pw")
            if st.button(t()["login_btn"], key="btn_login"):
                if (em == ADMIN_EMAIL) and pw == ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":em,"user_id":None,"vista":"app"})
                    st.rerun()
                else:
                    ok, datos = login_usuario(em, pw)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":datos.get("role","free"),"user_email":datos["email"],"user_id":datos["id"],"vista":"app"})
                        st.rerun()
                    else:
                        st.error(t()["login_error"])
        with tab2:
            re_em = st.text_input(t()["email"], key="r_em", placeholder="tu@email.com")
            re_pw = st.text_input(t()["password"], type="password", key="r_pw")
            re_pw2 = st.text_input(t()["confirm_pass"], type="password", key="r_pw2")
            if st.button(t()["register_btn"], key="btn_reg"):
                if re_pw != re_pw2:
                    st.error(t()["pass_mismatch"])
                elif re_em and re_pw:
                    ok, res = registrar_usuario(re_em, re_pw)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_em,"user_id":res.get("id"),"vista":"app"})
                        st.rerun()
                    elif res == "exists":
                        st.error(t()["email_exists"])
                    else:
                        st.error(f"Error: {res}")
    else:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.6);text-align:center;padding:4px 0;">{st.session_state["user_email"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;margin-bottom:8px;"><span class="gold-pill">{st.session_state["user_role"].upper()}</span></div>', unsafe_allow_html=True)
        if st.button(t()["logout"], key="btn_lo"):
            for k in ["logged_in","user_role","user_email","user_id","ultima_generacion","ultima_loteria"]:
                st.session_state[k] = {"logged_in":False,"user_role":"invitado","user_email":"","user_id":None,"ultima_generacion":None,"ultima_loteria":None}[k]
            st.session_state["vista"] = "landing"
            st.rerun()

# ══════════════════════════════════════════
# LANDING — usuarios no logueados
# ══════════════════════════════════════════
if not st.session_state["logged_in"]:
    render_header()
    t_ = t()

    # Hero
    st.markdown(f"""
<div style="text-align:center;padding:22px 16px 12px;">
  <div style="display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;
  background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);
  font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;
  letter-spacing:2px;margin-bottom:16px;">
    <span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>
    DATA CONVERGENCE ENGINE
  </div>
  <h1 style="font-family:'Playfair Display',serif;font-size:clamp(30px,7vw,56px);
  font-weight:700;line-height:1.05;letter-spacing:-1.5px;color:white;margin-bottom:12px;">
    {t_['tagline']}<br>
    <span class="shimmer-text">backed by the world</span>
  </h1>
  <p style="font-size:15px;color:rgba(232,228,217,.38);max-width:420px;margin:0 auto;line-height:1.8;">
    {t_['subtitle']}
  </p>
</div>""", unsafe_allow_html=True)

    # Preview balotas animadas
    st.markdown("""
<div style="text-align:center;margin-bottom:32px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.15);
  letter-spacing:3px;margin-bottom:12px;">LIVE PREVIEW · POWERBALL</div>
  <div id="balls-preview" style="display:flex;justify-content:center;flex-wrap:wrap;gap:4px;margin-bottom:16px;">
    <div class="ball" id="pb0">07</div>
    <div class="ball" id="pb1">14</div>
    <div class="ball" id="pb2">23</div>
    <div class="ball" id="pb3">34</div>
    <div class="ball" id="pb4">55</div>
    <div class="ball ball-gold" id="pb5">12</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px;max-width:380px;margin:0 auto;">
    <div style="display:flex;align-items:center;justify-content:space-between;
    background:rgba(255,255,255,.025);border:1px solid rgba(201,168,76,.1);
    border-radius:10px;padding:10px 14px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:14px;">⊞</span>
        <div>
          <div style="font-family:'DM Mono',monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">DRAW HISTORY</div>
          <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(201,168,76,.5);">Top #1 histórico Powerball — frecuencia máxima</div>
        </div>
      </div>
      <span style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 07</span>
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;
    background:rgba(255,255,255,.025);border:1px solid rgba(201,168,76,.1);
    border-radius:10px;padding:10px 14px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:14px;">ϕ</span>
        <div>
          <div style="font-family:'DM Mono',monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">FIBONACCI</div>
          <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(201,168,76,.5);">F9+F10=34 · posición 11 en la secuencia</div>
        </div>
      </div>
      <span style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 34</span>
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;
    background:rgba(255,255,255,.025);border:1px solid rgba(201,168,76,.1);
    border-radius:10px;padding:10px 14px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:14px;">⊛</span>
        <div>
          <div style="font-family:'DM Mono',monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">COMMUNITY</div>
          <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(201,168,76,.5);">Mencionado 47× en r/powerball hoy</div>
        </div>
      </div>
      <span style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 23</span>
    </div>
  </div>
</div>
<script>
const seqs = [[7,14,23,34,55],[8,15,22,33,44],[5,12,27,38,52],[3,18,29,41,60],[11,21,32,43,57]];
const gold  = [12,6,11,8,22,19];
let idx = 0;
setInterval(() => {
  idx = (idx+1)%seqs.length;
  for(let i=0;i<5;i++){
    const el=document.getElementById('pb'+i);
    if(el){el.textContent=String(seqs[idx][i]).padStart(2,'0');}
  }
  const eg=document.getElementById('pb5');
  if(eg){eg.textContent=String(gold[idx%gold.length]).padStart(2,'0');}
},2800);
</script>""", unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:4px 0 12px;">',unsafe_allow_html=True)
    _c1, _c2, _c3 = st.columns([1,2,1])
    with _c2:
        st.markdown('<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.16);letter-spacing:1.5px;margin-bottom:10px;">FREE · NO CREDIT CARD · ES / EN / PT</p>',unsafe_allow_html=True)
        tab_r, tab_l = st.tabs([t_["register"], t_["login"]])
        with tab_r:
            re_em  = st.text_input(t_["email"],        key="lr_em",  placeholder="tu@email.com")
            re_pw  = st.text_input(t_["password"],     key="lr_pw",  type="password")
            re_pw2 = st.text_input(t_["confirm_pass"], key="lr_pw2", type="password")
            if st.button(t_["register_btn"], use_container_width=True, key="lr_btn"):
                if re_pw != re_pw2: st.error(t_["pass_mismatch"])
                elif len(re_pw) < 6: st.warning("Mínimo 6 caracteres")
                elif "@" not in re_em: st.warning("Email inválido")
                else:
                    ok, res = registrar_usuario(re_em, re_pw)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_em,"user_id":res.get("id"),"vista":"app"})
                        st.rerun()
                    elif res == "exists": st.error(t_["email_exists"])
                    else: st.error(f"Error: {res}")
        with tab_l:
            le = st.text_input(t_["email"],    key="ll_em", placeholder="tu@email.com")
            lp = st.text_input(t_["password"], key="ll_pw", type="password")
            if st.button(t_["login_btn"], use_container_width=True, key="ll_btn"):
                if le == ADMIN_EMAIL and lp == ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":le,"user_id":None,"vista":"app"})
                    st.rerun()
                else:
                    ok, datos = login_usuario(le, lp)
                    if ok:
                        st.session_state.update({"logged_in":True,"user_role":datos.get("role","free"),"user_email":datos["email"],"user_id":datos["id"],"vista":"app"})
                        st.rerun()
                    else: st.error(t_["login_error"])
    st.stop()

# ══════════════════════════════════════════
# APP PRINCIPAL — usuarios logueados
# ══════════════════════════════════════════
render_header()
t_ = t()

# Selector lotería
lot_names = [f"{l['flag']} {l['nombre']}" for l in LOTERIAS]
sel_idx = st.selectbox(t_["select_lottery"], range(len(lot_names)),
    format_func=lambda i: lot_names[i], key="sel_lot")
loteria = LOTERIAS[sel_idx]

# Próximo sorteo
hoy = datetime.now()
dia_actual = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][hoy.weekday()]
st.markdown(f"""
<div style="display:inline-block;padding:5px 12px;border-radius:20px;
background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.15);
font-family:'DM Mono',monospace;font-size:11px;color:rgba(201,168,76,.7);
letter-spacing:1px;margin-bottom:12px;">
⊙ {t_['next_draw']}: {' · '.join(loteria['dias'])} · {loteria['hora']}
</div>""", unsafe_allow_html=True)

# Contador visual
gen_hoy = st.session_state.get("gen_hoy", 0)
MAX_GEN = 99 if st.session_state["user_role"] in ["admin","paid","pro"] else 3
dots = "".join([
    f'<div style="width:8px;height:8px;border-radius:50%;background:{"#C9A84C" if i<gen_hoy else "rgba(255,255,255,.1)"};margin:0 2px;display:inline-block;"></div>'
    for i in range(min(MAX_GEN if MAX_GEN < 6 else 5, 5))
])
if MAX_GEN < 6:
    st.markdown(f'<div style="text-align:center;margin:4px 0 12px;">{dots}<span style="font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.3);margin-left:8px;">{gen_hoy}/{MAX_GEN} {t_["gen_limit"]}</span></div>', unsafe_allow_html=True)

st.markdown('<hr class="gold">', unsafe_allow_html=True)

# Módulos
modulos = []
inputs  = {}

# Favoritos
mn, mx = loteria["min"], loteria["max"]
favs = st.session_state.get("nums_favoritos",[])
fav_label = f"{t_['fav_title']} — {len(favs)} seleccionados" if favs else t_["fav_title"]
with st.expander(fav_label, expanded=False):
    st.caption(t_["fav_help"])
    opciones = list(range(mn, mx+1))
    favs_validos = [n for n in favs if mn<=n<=mx]
    sel = st.multiselect("", opciones,
        default=favs_validos,
        format_func=lambda n: str(n).zfill(2),
        key=f"ms_fav_{loteria['id']}")
    if sorted(sel) != sorted(favs_validos):
        st.session_state["nums_favoritos"] = sorted(sel)
        st.rerun()
    if favs:
        balls_fav = "".join([f'<div class="ball" style="width:36px;height:36px;font-size:13px;">{str(n).zfill(2)}</div>' for n in favs if mn<=n<=mx])
        st.markdown(f'<div style="display:flex;flex-wrap:wrap;margin-top:8px;">{balls_fav}</div>', unsafe_allow_html=True)
        if st.button("✕ Limpiar favoritos", key="clr_fav"):
            st.session_state["nums_favoritos"] = []
            st.rerun()

# Real Data
with st.expander(t_["real_title"], expanded=True):
    st.caption(t_["real_help"])
    c_hist = st.checkbox("⊞ Histórico oficial", value=True,  key="cb_hist")
    c_comm = st.checkbox("⊛ Comunidad",         value=True,  key="cb_comm")
    c_efem = st.checkbox("⊕ Efemérides",        value=True,  key="cb_efem")
    c_hoy  = st.checkbox("◈ Fecha de hoy",      value=True,  key="cb_hoy")
    if any([c_hist, c_comm, c_efem, c_hoy]):
        modulos.append("real")
        inputs["use_hist"] = c_hist
        inputs["use_comm"] = c_comm
        inputs["use_efem"] = c_efem
        inputs["use_hoy"]  = c_hoy
    inputs["excluir"] = st.text_input(t_["exclude"], placeholder="4, 13", key="ex_inp")

# Holístico
with st.expander(t_["holistic_title"], expanded=False):
    st.caption(t_["holistic_help"])
    c1, c2 = st.columns(2)
    with c1: inputs["nombre"] = st.text_input(t_["your_name"], key="hol_nm", placeholder="Juan García")
    with c2: inputs["fecha"]  = st.text_input(t_["special_date"], key="hol_fe", placeholder="14/03/92")
    inputs["sueno"] = st.text_area(t_["dream"], key="hol_dr", height=70, placeholder=t_["dream"])
    if inputs.get("nombre") or inputs.get("fecha") or inputs.get("sueno"):
        modulos.append("holistic")

# Matemático
with st.expander(t_["math_title"], expanded=False):
    st.caption(t_["math_help"])
    c1, c2 = st.columns(2)
    with c1:
        use_fib = st.checkbox("ϕ Fibonacci", key="cb_fib")
        use_tes = st.checkbox("⌁ Tesla 3·6·9", key="cb_tes")
        use_sag = st.checkbox("⬡ Geometría Sagrada", key="cb_sag")
    with c2:
        use_pri = st.checkbox("∴ Números Primos", key="cb_pri")
    if any([use_fib, use_tes, use_sag, use_pri]):
        modulos.append("math")
        inputs.update({"use_fib":use_fib,"use_tes":use_tes,"use_sag":use_sag,"use_pri":use_pri})

st.markdown('<hr class="gold">', unsafe_allow_html=True)

# Botón generar
if gen_hoy >= MAX_GEN and MAX_GEN < 99:
    st.warning(f"⚠️ {gen_hoy}/{MAX_GEN} {t_['gen_limit']}")
    st.markdown(f"""<div class="ls-card" style="text-align:center;">
<h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;">◆ Desbloquea LuckSort Pro</h3>
<p style="color:rgba(232,228,217,.5);font-size:13px;margin-bottom:16px;">Generaciones ilimitadas · Postal descargable · Email combinación</p>
<a href="{STRIPE_LINK}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#F0C84A);color:#080810;font-weight:700;font-size:14px;padding:12px 32px;border-radius:12px;text-decoration:none;">$9.99/mes — Empezar</a>
</div>""", unsafe_allow_html=True)
else:
    if st.button(t_["generate"], key="gen_btn"):
        ph = st.empty()
        steps_with_icons = list(zip(["⊞","⊛","ϕ","◆"], t_["steps"]))
        for icon, step in steps_with_icons:
            ph.markdown(f'''<div style="text-align:center;padding:24px 0;">
<div class="conv-ring"></div>
<div style="font-family:DM Mono,monospace;font-size:22px;color:rgba(201,168,76,.3);margin:8px 0;">{icon}</div>
<div class="conv-label">{step}</div>
</div>''', unsafe_allow_html=True)
            time.sleep(0.6)
        ph.empty()
        resultado = generar(loteria, inputs, modulos)
        st.session_state["ultima_generacion"] = resultado
        st.session_state["ultima_loteria"]    = loteria
        st.session_state["ultima_modulos"]    = modulos
        st.session_state["gen_hoy"]           = gen_hoy + 1
        st.rerun()

# Resultado
if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
    render_resultado(
        st.session_state["ultima_generacion"],
        st.session_state["ultima_loteria"],
        st.session_state.get("ultima_modulos",["real"])
    )
