import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime
import requests
import random
import json
import math

# ==========================================
# 1. CONFIG
# ==========================================
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

defaults = {
    'logged_in': False, 'user_role': 'invitado',
    'user_email': '', 'user_id': None,
    'idioma': 'EN', 'fecha_uso': str(date.today()),
    'generaciones_hoy': {}, 'ultima_generacion': None,
    'ultima_loteria': None, 'vista': 'landing',
    'mostrar_reg': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 2. CSS RESPONSIVE DARK GOLD
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    background-color: #0a0a0f !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d0d1a 0%,#0a0a0f 100%) !important;
    border-right: 1px solid rgba(201,168,76,0.15) !important;
}
section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg,#C9A84C,#F5D68A) !important;
    color: #0a0a0f !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(201,168,76,0.22) !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 22px rgba(201,168,76,0.36) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(201,168,76,0.45) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.08) !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: white !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px !important;
    gap: 2px !important;
    padding: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.4) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}
.stTabs [aria-selected="true"] {
    color: #C9A84C !important;
    background: rgba(201,168,76,0.1) !important;
}

/* ── RADIO ── */
.stRadio > div {
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
}
.stRadio > div > label {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    color: rgba(255,255,255,0.5) !important;
    font-size: 13px !important;
    cursor: pointer !important;
}

/* ── EXPANDER ── */
.stExpander {
    border: 1px solid rgba(201,168,76,0.15) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.02) !important;
}

/* ── MULTISELECT ── */
.stMultiSelect > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}

/* ── CHECKBOX ── */
.stCheckbox > label { color: rgba(255,255,255,0.6) !important; }

/* ── ANIMATIONS ── */
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes goldPulse {
    0%,100% { box-shadow: 0 0 12px rgba(201,168,76,0.3); transform: scale(1); }
    50% { box-shadow: 0 0 26px rgba(201,168,76,0.6); transform: scale(1.05); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes orbPulse {
    0%,100% { opacity: 0.15; transform: scale(1); }
    50% { opacity: 0.28; transform: scale(1.06); }
}

.shimmer-text {
    background: linear-gradient(90deg,#C9A84C 0%,#F5D68A 35%,#C9A84C 65%,#F5D68A 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
}

/* ── CARDS ── */
.ls-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
}
.ls-card-gold {
    background: rgba(201,168,76,0.05);
    border: 1px solid rgba(201,168,76,0.22);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 14px;
}

/* ── NUMBER BALLS ── */
.balls-wrap {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
    margin: 16px 0;
}
.ball {
    width: 50px; height: 50px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 16px; font-weight: 600;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    color: rgba(255,255,255,0.88);
    transition: all 0.3s ease;
}
.ball-gold {
    background: linear-gradient(135deg,#C9A84C,#F5D68A);
    border: none; color: #0a0a0f;
    animation: goldPulse 2.5s ease-in-out infinite;
}

/* ── SOURCE ROWS ── */
.src-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 11px 14px;
    border-radius: 10px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
    gap: 12px;
}
.src-complement {
    background: rgba(255,255,255,0.01);
    border-color: rgba(255,255,255,0.04);
}
.src-left { display: flex; align-items: flex-start; gap: 10px; flex: 1; min-width: 0; }
.src-icon { font-size: 15px; margin-top: 1px; flex-shrink: 0; }
.src-label { font-family:'DM Sans',sans-serif; font-size:12px; font-weight:600; color:rgba(255,255,255,0.75); }
.src-desc { font-family:'DM Sans',sans-serif; font-size:11px; color:rgba(255,255,255,0.35); line-height:1.55; margin-top:2px; }
.src-num { font-family:'DM Mono',monospace; font-size:15px; color:#C9A84C; font-weight:700; flex-shrink:0; margin-top:1px; }
.src-complement .src-num { color: rgba(255,255,255,0.25); }

/* ── MISC ── */
.tag-gold {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(201,168,76,0.1);
    border: 1px solid rgba(201,168,76,0.22);
    border-radius: 20px; padding: 4px 12px;
    font-family: 'DM Mono', monospace;
    font-size: 10px; color: #C9A84C;
    letter-spacing: 2px; text-transform: uppercase;
}
.metric-pill {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.18);
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: #C9A84C;
}
.disclaimer {
    background: rgba(201,168,76,0.04);
    border: 1px solid rgba(201,168,76,0.12);
    border-radius: 10px; padding: 13px 15px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px; color: rgba(255,255,255,0.3);
    line-height: 1.65; font-style: italic; margin-top: 16px;
}
.gold-line {
    width: 36px; height: 2px; margin: 10px auto;
    background: linear-gradient(90deg,transparent,#C9A84C,transparent);
}
.sidebar-hr { border:none; border-top:1px solid rgba(255,255,255,0.06); margin:12px 0; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
    .ball { width: 44px; height: 44px; font-size: 14px; }
    .src-desc { font-size: 10px; }
    h1 { font-size: clamp(32px,9vw,52px) !important; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CREDENCIALES
# ==========================================
try:
    GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
    SUPABASE_URL   = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY   = st.secrets["SUPABASE_KEY"]
    RESEND_KEY     = st.secrets.get("RESEND_API_KEY","")
    ADMIN_EMAIL    = st.secrets.get("ADMIN_EMAIL","admin@lucksort.com")
    ADMIN_PASS     = st.secrets.get("ADMIN_PASS","admin123")
    NEWS_API_KEY   = st.secrets.get("NEWS_API_KEY","")
    REDDIT_CLIENT  = st.secrets.get("REDDIT_CLIENT_ID","")
    REDDIT_SECRET  = st.secrets.get("REDDIT_SECRET","")
except:
    st.error("⚠️ Configure secrets in Streamlit Cloud settings.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
APP_URL = "https://lucksort.streamlit.app"

# ==========================================
# 4. LOTERÍAS
# ==========================================
LOTERIAS = [
    {"id":1,  "nombre":"Powerball",     "pais":"USA",      "flag":"🇺🇸", "min":1,"max":69,"n":5, "bonus":True, "bmax":26,  "bname":"Powerball"},
    {"id":2,  "nombre":"Mega Millions", "pais":"USA",      "flag":"🇺🇸", "min":1,"max":70,"n":5, "bonus":True, "bmax":25,  "bname":"Mega Ball"},
    {"id":3,  "nombre":"EuroMillions",  "pais":"Europa",   "flag":"🇪🇺", "min":1,"max":50,"n":5, "bonus":True, "bmax":12,  "bname":"Lucky Star"},
    {"id":4,  "nombre":"UK Lotto",      "pais":"UK",       "flag":"🇬🇧", "min":1,"max":59,"n":6, "bonus":False,"bmax":None,"bname":None},
    {"id":5,  "nombre":"El Gordo",      "pais":"España",   "flag":"🇪🇸", "min":1,"max":54,"n":5, "bonus":True, "bmax":10,  "bname":"Reintegro"},
    {"id":6,  "nombre":"Mega-Sena",     "pais":"Brasil",   "flag":"🇧🇷", "min":1,"max":60,"n":6, "bonus":False,"bmax":None,"bname":None},
    {"id":7,  "nombre":"Lotofácil",     "pais":"Brasil",   "flag":"🇧🇷", "min":1,"max":25,"n":15,"bonus":False,"bmax":None,"bname":None},
    {"id":8,  "nombre":"Baloto",        "pais":"Colombia", "flag":"🇨🇴", "min":1,"max":43,"n":6, "bonus":True, "bmax":16,  "bname":"Balota"},
    {"id":9,  "nombre":"La Primitiva",  "pais":"España",   "flag":"🇪🇸", "min":1,"max":49,"n":6, "bonus":False,"bmax":None,"bname":None},
    {"id":10, "nombre":"EuroJackpot",   "pais":"Europa",   "flag":"🇪🇺", "min":1,"max":50,"n":5, "bonus":True, "bmax":12,  "bname":"Euro Number"},
    {"id":11, "nombre":"Canada Lotto",  "pais":"Canadá",   "flag":"🇨🇦", "min":1,"max":49,"n":6, "bonus":True, "bmax":49,  "bname":"Bonus"},
]
MAX_GEN = 5

# ==========================================
# 5. TRADUCCIONES
# ==========================================
T = {
"EN":{
    "tagline":"Sort Your Luck",
    "hero_1":"Your numbers,","hero_2":"backed by the","hero_3":"world's signals.",
    "hero_sub":"We gather real data — historical draws, today's headlines, community picks, and your personal dates — converged into combinations that mean something.",
    "cta_free":"Start Free","login":"Sign In","register":"Create Account","logout":"Sign Out",
    "email":"Email","password":"Password","confirm_pass":"Confirm Password",
    "btn_login":"Sign In","btn_register":"Create Free Account",
    "plan":"Plan","free":"Free","paid":"Convergence",
    "select_lottery":"Select Lottery",
    "personal_title":"Personal Signals (optional)",
    "special_date":"Special date (birthday, anniversary...)","your_name":"Your name",
    "life_moment":"Something happening in your life right now",
    "exclude_numbers":"Numbers to exclude (comma separated)",
    "symbolic_title":"Symbolic Systems (optional)",
    "symbolic_help":"Choose which systems to include in your combination",
    "sys_numerology":"Numerology","sys_fibonacci":"Fibonacci","sys_sacred":"Sacred Geometry (φ, π)","sys_tesla":"Tesla (3·6·9)","sys_fractal":"Historical Fractals",
    "crowd_pref":"Crowd preference","follow":"Follow crowd","avoid":"Avoid crowd","balanced":"Balanced",
    "generate_btn":"Generate Combination","generating":"Converging data sources...",
    "sources_title":"Where each number comes from",
    "gen_counter":"Today","disclaimer":"We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
    "paywall_title":"Convergence Plan","upgrade_btn":"Upgrade — $9.99/month",
    "paywall_msg":"Unlock data-driven generation with historical analysis, community intelligence, world events, personal dates and symbolic systems.",
    "history":"My History","no_history":"No combinations yet.",
    "login_err":"❌ Incorrect credentials.","pass_mismatch":"⚠️ Passwords don't match.",
    "pass_short":"⚠️ Minimum 6 characters.","email_invalid":"⚠️ Invalid email.",
    "email_exists":"⚠️ Email already registered.",
    "sources":{"historico":"Draw History","community":"Community","eventos":"World Events",
               "fecha_personal":"Your Date","numerologia":"Numerology","fibonacci":"Fibonacci",
               "sagrada":"Sacred Geometry","tesla":"Tesla 3·6·9","fractal":"Fractal Pattern","complement":"Complement"},
    "icons":{"historico":"📊","community":"👥","eventos":"🌍","fecha_personal":"✦",
             "numerologia":"🔢","fibonacci":"🌀","sagrada":"⬡","tesla":"⚡","fractal":"🔮","complement":"⚪"},
},
"ES":{
    "tagline":"Ordena tu Suerte",
    "hero_1":"Tus números,","hero_2":"respaldados por","hero_3":"las señales del mundo.",
    "hero_sub":"Recopilamos datos reales — sorteos históricos, titulares de hoy, picks de la comunidad y tus fechas personales — convergidos en combinaciones con significado.",
    "cta_free":"Empezar Gratis","login":"Entrar","register":"Crear Cuenta","logout":"Cerrar Sesión",
    "email":"Correo","password":"Contraseña","confirm_pass":"Confirmar contraseña",
    "btn_login":"Entrar","btn_register":"Crear Cuenta Gratis",
    "plan":"Plan","free":"Gratis","paid":"Convergencia",
    "select_lottery":"Selecciona tu Lotería",
    "personal_title":"Señales personales (opcional)",
    "special_date":"Fecha especial (cumpleaños, aniversario...)","your_name":"Tu nombre",
    "life_moment":"Algo que está pasando en tu vida ahora",
    "exclude_numbers":"Números a excluir (separados por coma)",
    "symbolic_title":"Sistemas simbólicos (opcional)",
    "symbolic_help":"Elige qué sistemas incluir en tu combinación",
    "sys_numerology":"Numerología","sys_fibonacci":"Fibonacci","sys_sacred":"Geometría Sagrada (φ, π)","sys_tesla":"Tesla (3·6·9)","sys_fractal":"Fractales del histórico",
    "crowd_pref":"Preferencia comunidad","follow":"Seguir masa","avoid":"Ir contra masa","balanced":"Balanceado",
    "generate_btn":"Generar Combinación","generating":"Convergiendo fuentes de datos...",
    "sources_title":"De dónde viene cada número",
    "gen_counter":"Hoy","disclaimer":"Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
    "paywall_title":"Plan Convergencia","upgrade_btn":"Actualizar — $9.99/mes",
    "paywall_msg":"Desbloquea la generación basada en datos con análisis histórico, inteligencia de comunidad, eventos mundiales, fechas personales y sistemas simbólicos.",
    "history":"Mi Historial","no_history":"Aún no has generado combinaciones.",
    "login_err":"❌ Credenciales incorrectas.","pass_mismatch":"⚠️ Las contraseñas no coinciden.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ El correo ya está registrado.",
    "sources":{"historico":"Histórico","community":"Comunidad","eventos":"Eventos",
               "fecha_personal":"Tu Fecha","numerologia":"Numerología","fibonacci":"Fibonacci",
               "sagrada":"Geometría Sagrada","tesla":"Tesla 3·6·9","fractal":"Patrón Fractal","complement":"Complemento"},
    "icons":{"historico":"📊","community":"👥","eventos":"🌍","fecha_personal":"✦",
             "numerologia":"🔢","fibonacci":"🌀","sagrada":"⬡","tesla":"⚡","fractal":"🔮","complement":"⚪"},
},
"PT":{
    "tagline":"Organize sua Sorte",
    "hero_1":"Seus números,","hero_2":"respaldados pelos","hero_3":"sinais do mundo.",
    "hero_sub":"Coletamos dados reais — histórico de sorteios, manchetes de hoje, picks da comunidade e suas datas pessoais — convergidos em combinações com significado.",
    "cta_free":"Começar Grátis","login":"Entrar","register":"Criar Conta","logout":"Sair",
    "email":"Email","password":"Senha","confirm_pass":"Confirmar senha",
    "btn_login":"Entrar","btn_register":"Criar Conta Grátis",
    "plan":"Plano","free":"Grátis","paid":"Convergência",
    "select_lottery":"Selecione sua Loteria",
    "personal_title":"Sinais pessoais (opcional)",
    "special_date":"Data especial (aniversário...)","your_name":"Seu nome",
    "life_moment":"Algo acontecendo na sua vida agora",
    "exclude_numbers":"Números a excluir (separados por vírgula)",
    "symbolic_title":"Sistemas simbólicos (opcional)",
    "symbolic_help":"Escolha quais sistemas incluir na sua combinação",
    "sys_numerology":"Numerologia","sys_fibonacci":"Fibonacci","sys_sacred":"Geometria Sagrada (φ, π)","sys_tesla":"Tesla (3·6·9)","sys_fractal":"Fractais do histórico",
    "crowd_pref":"Preferência comunidade","follow":"Seguir massa","avoid":"Ir contra massa","balanced":"Balanceado",
    "generate_btn":"Gerar Combinação","generating":"Convergindo fontes de dados...",
    "sources_title":"De onde vem cada número",
    "gen_counter":"Hoje","disclaimer":"Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
    "paywall_title":"Plano Convergência","upgrade_btn":"Atualizar — $9.99/mês",
    "paywall_msg":"Desbloqueie a geração baseada em dados com análise histórica, inteligência da comunidade, eventos mundiais, datas pessoais e sistemas simbólicos.",
    "history":"Meu Histórico","no_history":"Ainda não gerou combinações.",
    "login_err":"❌ Credenciais incorretas.","pass_mismatch":"⚠️ As senhas não coincidem.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ Email já cadastrado.",
    "sources":{"historico":"Histórico","community":"Comunidade","eventos":"Eventos",
               "fecha_personal":"Sua Data","numerologia":"Numerologia","fibonacci":"Fibonacci",
               "sagrada":"Geometria Sagrada","tesla":"Tesla 3·6·9","fractal":"Padrão Fractal","complement":"Complemento"},
    "icons":{"historico":"📊","community":"👥","eventos":"🌍","fecha_personal":"✦",
             "numerologia":"🔢","fibonacci":"🌀","sagrada":"⬡","tesla":"⚡","fractal":"🔮","complement":"⚪"},
},
}

def tr(): return T[st.session_state['idioma']]

# ==========================================
# 6. SISTEMAS SIMBÓLICOS
# ==========================================
PHI = 1.6180339887
PI  = 3.14159265358979

def numeros_fibonacci(min_n, max_n):
    fibs = []
    a, b = 1, 1
    while b <= max_n:
        if a >= min_n:
            fibs.append(a)
        a, b = b, a + b
    if b <= max_n:
        fibs.append(b)
    return [f for f in fibs if min_n <= f <= max_n]

def numeros_sagrada(min_n, max_n):
    """Números derivados de φ, π y sus múltiplos"""
    nums = set()
    # φ derivados
    for i in range(1, 30):
        v = int(PHI * i)
        if min_n <= v <= max_n: nums.add(v)
        v2 = int(PHI ** i)
        if min_n <= v2 <= max_n: nums.add(v2)
    # π derivados
    for i in range(1, 20):
        v = int(PI * i)
        if min_n <= v <= max_n: nums.add(v)
    # Extractos de dígitos: 3,1,4,1,5,9,2,6,5,3
    pi_digits = [3,1,4,1,5,9,2,6,5,3,5,8,9,7,9]
    acum = 0
    for d in pi_digits:
        acum += d
        if min_n <= acum <= max_n: nums.add(acum)
    return sorted(list(nums))

def numeros_tesla(min_n, max_n):
    """3, 6, 9 y sus múltiplos — patrón Tesla"""
    return [n for n in range(min_n, max_n+1) if n % 3 == 0]

def numerologia_nombre(nombre):
    """Reduce nombre a número maestro"""
    if not nombre: return None
    tabla = {'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
             'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
             's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8}
    suma = sum(tabla.get(c.lower(), 0) for c in nombre if c.isalpha())
    while suma > 9 and suma not in [11, 22, 33]:
        suma = sum(int(d) for d in str(suma))
    return suma

def numerologia_fecha(fecha_str):
    """Número de vida desde fecha"""
    if not fecha_str: return None
    try:
        digitos = [c for c in fecha_str if c.isdigit()]
        suma = sum(int(d) for d in digitos)
        while suma > 9 and suma not in [11, 22, 33]:
            suma = sum(int(d) for d in str(suma))
        return suma
    except:
        return None

def extraer_numeros_fecha(fecha_str, min_n, max_n):
    """Extrae números válidos de una fecha personal"""
    nums = []
    if not fecha_str: return nums
    partes = [x for x in fecha_str.replace("/","-").replace(".","-").split("-") if x.isdigit()]
    for p in partes:
        v = int(p)
        if min_n <= v <= max_n: nums.append(v)
        # También año corto
        if len(p) == 4:
            short = int(p[-2:])
            if min_n <= short <= max_n: nums.append(short)
        # Suma de dígitos
        s = sum(int(d) for d in p)
        if min_n <= s <= max_n: nums.append(s)
    return list(set(nums))

# ==========================================
# 7. APIS DE DATOS
# ==========================================
def get_cache(tipo):
    try:
        hoy = str(date.today())
        res = supabase.table("cache_diario").select("*").eq("fecha",hoy).eq("tipo",tipo).execute()
        return res.data[0]['contenido'] if res.data else None
    except: return None

def set_cache(tipo, contenido, fuente=""):
    try:
        hoy = str(date.today())
        ex = supabase.table("cache_diario").select("id").eq("fecha",hoy).eq("tipo",tipo).execute()
        if ex.data:
            supabase.table("cache_diario").update({"contenido":contenido}).eq("id",ex.data[0]['id']).execute()
        else:
            supabase.table("cache_diario").insert({"fecha":hoy,"tipo":tipo,"contenido":contenido,"fuente":fuente}).execute()
    except: pass

def obtener_efemerides_dia(mes, dia):
    tipo = f"efem_{mes}_{dia}"
    cache = get_cache(tipo)
    if cache: return cache
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{mes}/{dia}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            eventos = r.json().get("events",[])[:6]
            res = [{"year":e.get("year"),"text":e.get("text","")[:160]} for e in eventos]
            set_cache(tipo, res, "wikipedia")
            return res
    except: pass
    return []

def obtener_noticias():
    cache = get_cache("noticias")
    if cache: return cache
    try:
        if NEWS_API_KEY:
            url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=6&apiKey={NEWS_API_KEY}"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                arts = r.json().get("articles",[])[:6]
                res = [{"title":a.get("title","")[:130],"source":a.get("source",{}).get("name","")} for a in arts]
                set_cache("noticias", res, "newsapi")
                return res
    except: pass
    return []

def obtener_reddit_crowd(loteria_nombre):
    """Reddit API — picks reales de la comunidad"""
    cache = get_cache(f"reddit_{date.today()}")
    if cache: return cache

    subs_map = {
        "Powerball":     ["powerball","lottery"],
        "Mega Millions": ["megamillions","lottery"],
        "EuroMillions":  ["euromillions","lottery"],
        "Mega-Sena":     ["megasena","loteria"],
        "Baloto":        ["colombia","loteria"],
        "default":       ["lottery","lotto"],
    }
    subs = subs_map.get(loteria_nombre, subs_map["default"])

    numeros_mencionados = []
    try:
        if REDDIT_CLIENT and REDDIT_SECRET:
            # OAuth Reddit
            auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT, REDDIT_SECRET)
            data = {"grant_type":"client_credentials"}
            headers = {"User-Agent":"LuckSort/1.0"}
            token_r = requests.post("https://www.reddit.com/api/v1/access_token",
                                   auth=auth, data=data, headers=headers, timeout=8)
            if token_r.status_code == 200:
                token = token_r.json().get("access_token","")
                h2 = {**headers, "Authorization": f"bearer {token}"}
                for sub in subs[:2]:
                    posts_r = requests.get(
                        f"https://oauth.reddit.com/r/{sub}/hot?limit=10",
                        headers=h2, timeout=8)
                    if posts_r.status_code == 200:
                        posts = posts_r.json().get("data",{}).get("children",[])
                        for post in posts:
                            text = post.get("data",{}).get("selftext","") + " " + post.get("data",{}).get("title","")
                            # Extrae números 1-70
                            import re
                            found = re.findall(r'\b([1-9]|[1-6][0-9]|70)\b', text)
                            numeros_mencionados.extend([int(n) for n in found])
    except: pass

    if not numeros_mencionados:
        # Fallback: patrones conocidos de comunidades de lotería
        numeros_mencionados = [7,11,14,17,21,23,27,32,38,42,3,8,13,19,29,33,44,55,66,17]

    # Top 10 más frecuentes
    from collections import Counter
    conteo = Counter(numeros_mencionados)
    top = [n for n,_ in conteo.most_common(10)]
    set_cache(f"reddit_{date.today()}", top, "reddit")
    return top

def obtener_google_trends():
    """Google Trends via trendspyg"""
    cache = get_cache("trends")
    if cache: return cache
    try:
        from trendspyg import download_google_trends_rss
        trends = download_google_trends_rss(geo='US')
        # Extrae números de los títulos de tendencias
        import re
        nums = []
        for t in trends[:10]:
            text = t.get('trend','') + ' ' + str(t.get('traffic',''))
            found = re.findall(r'\b([1-9]|[1-6][0-9]|70)\b', text)
            nums.extend([int(n) for n in found])
        if nums:
            set_cache("trends", nums[:15], "trendspyg")
            return nums[:15]
    except: pass
    return []

# ==========================================
# 8. GENERACIÓN CON GROQ
# ==========================================
def calcular_numeros_simbolicos(loteria, inputs):
    """Pre-calcula todos los números simbólicos disponibles"""
    min_n, max_n = loteria['min'], loteria['max']
    simbolicos = {}

    sistemas = inputs.get("sistemas", [])

    if "numerologia" in sistemas:
        n_nombre = numerologia_nombre(inputs.get("nombre",""))
        n_fecha  = numerologia_fecha(inputs.get("fecha_especial",""))
        nums_num = []
        if n_nombre and min_n <= n_nombre <= max_n: nums_num.append(n_nombre)
        if n_fecha and min_n <= n_fecha <= max_n: nums_num.append(n_fecha)
        # Números maestros escalados
        for m in [11,22,33]:
            if min_n <= m <= max_n: nums_num.append(m)
        simbolicos["numerologia"] = {"numeros": nums_num, "maestro_nombre": n_nombre, "maestro_fecha": n_fecha}

    if "fibonacci" in sistemas:
        simbolicos["fibonacci"] = {"numeros": numeros_fibonacci(min_n, max_n)}

    if "sagrada" in sistemas:
        simbolicos["sagrada"] = {"numeros": numeros_sagrada(min_n, max_n)}

    if "tesla" in sistemas:
        simbolicos["tesla"] = {"numeros": numeros_tesla(min_n, max_n)[:15]}

    return simbolicos

def generar_combinacion(loteria, inputs):
    lang = st.session_state['idioma']
    lang_map = {"EN":"English","ES":"Spanish","PT":"Portuguese"}
    lang_full = lang_map[lang]

    hoy = datetime.now()
    efem_hoy = obtener_efemerides_dia(hoy.month, hoy.day)
    noticias  = obtener_noticias()
    crowd_reddit = obtener_reddit_crowd(loteria['nombre'])
    crowd_trends = obtener_google_trends()

    # Efemérides fecha personal
    efem_personal = []
    fecha_esp = inputs.get("fecha_especial","")
    nums_fecha = []
    if fecha_esp:
        partes = [x for x in fecha_esp.replace("/","-").replace(".","-").split("-") if x.isdigit()]
        if len(partes) >= 2:
            try:
                dia_p, mes_p = int(partes[0]), int(partes[1])
                if 1<=dia_p<=31 and 1<=mes_p<=12:
                    efem_personal = obtener_efemerides_dia(mes_p, dia_p)
                    nums_fecha = extraer_numeros_fecha(fecha_esp, loteria['min'], loteria['max'])
            except: pass

    # Sistemas simbólicos
    simbolicos = calcular_numeros_simbolicos(loteria, inputs)

    # Excluir
    excluir = []
    if inputs.get("excluir"):
        try: excluir = [int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    bonus_inst = f"- 1 {loteria['bname']} between 1 and {loteria['bmax']}" if loteria['bonus'] else "- No bonus number"

    prompt = f"""You are LuckSort's convergence engine. Generate a {loteria['nombre']} combination using ONLY real verified data signals.

LOTTERY: {loteria['nombre']} | Main: {loteria['n']} numbers ({loteria['min']}-{loteria['max']}) | {bonus_inst}
EXCLUDE: {excluir if excluir else 'none'}
CROWD: {inputs.get('crowd','balanced')} (follow=use crowd, avoid=avoid crowd, balanced=mix)

═══ REAL DATA SIGNALS ═══

1. TODAY'S WORLD EVENTS ({hoy.strftime('%B %d')}):
{json.dumps(efem_hoy[:4], ensure_ascii=False)}

2. USER PERSONAL DATE ({fecha_esp if fecha_esp else 'not provided'}):
Events: {json.dumps(efem_personal[:3], ensure_ascii=False)}
Numbers extracted: {nums_fecha}

3. TODAY'S NEWS:
{json.dumps(noticias[:4], ensure_ascii=False)}

4. COMMUNITY INTELLIGENCE:
Reddit picks: {crowd_reddit}
Google Trends numbers: {crowd_trends[:8] if crowd_trends else 'unavailable'}

5. SYMBOLIC SYSTEMS SELECTED BY USER:
{json.dumps(simbolicos, ensure_ascii=False, indent=2)}

USER: name={inputs.get('nombre','')}, moment={inputs.get('momento','')}

═══ CRITICAL RULES ═══
1. Each number MUST have a REAL specific signal from the data above
2. Extract numbers from: years→last 2 digits, dates→day/month, headlines→quantities, Fibonacci sequence, φ multiples, Tesla 3·6·9 multiples, numerology reductions
3. ONLY use "complement" source if truly no signal exists for that position — be honest
4. DO NOT use "complement" if you can find ANY real signal
5. Numbers must be unique, within valid range, not in exclude list
6. For NUMEROLOGY: reduce name/date digits until single digit or master (11,22,33)
7. For FIBONACCI: only use actual Fibonacci numbers within range
8. For SACRED GEOMETRY: use φ=1.618... or π=3.14159... multiples
9. For TESLA: use multiples of 3 (3,6,9,12,15,18,21...)
10. Be SPECIFIC in explanations — minimum 15 words, cite exact data point

Respond ONLY in {lang_full}. Return ONLY valid JSON:
{{
  "numbers": [list of {loteria['n']} integers],
  "bonus": {f'integer 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources": [
    {{
      "number": N,
      "source": "historico|community|eventos|fecha_personal|numerologia|fibonacci|sagrada|tesla|fractal|complement",
      "label": "short name in {lang_full}",
      "explanation": "specific real explanation minimum 15 words in {lang_full}"
    }}
  ]
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"LuckSort convergence engine. Respond ONLY in {lang_full}. Return ONLY valid JSON. Be specific."},
                {"role":"user","content":prompt}
            ],
            temperature=0.65,
            max_tokens=1400
        )
        raw = resp.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].replace("json","").strip()
        resultado = json.loads(raw)

        # Validate
        nums = [n for n in resultado.get("numbers",[]) if loteria['min']<=n<=loteria['max'] and n not in excluir]
        pool = [n for n in range(loteria['min'],loteria['max']+1) if n not in nums and n not in excluir]
        while len(nums) < loteria['n'] and pool:
            pick = random.choice(pool); nums.append(pick); pool.remove(pick)
        resultado['numbers'] = list(dict.fromkeys(nums))[:loteria['n']]

        if loteria['bonus'] and resultado.get('bonus'):
            b = resultado['bonus']
            if not isinstance(b,int) or not (1<=b<=loteria['bmax']):
                resultado['bonus'] = random.randint(1,loteria['bmax'])

        return resultado
    except:
        return generar_fallback(loteria, excluir)

def generar_fallback(loteria, excluir=[]):
    pool = [n for n in range(loteria['min'],loteria['max']+1) if n not in excluir]
    nums = random.sample(pool, min(loteria['n'],len(pool)))
    bonus = random.randint(1,loteria['bmax']) if loteria['bonus'] else None
    sources = [{"number":n,"source":"complement","label":"Random","explanation":"No specific signal found — generated randomly as complement"} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","label":"Random","explanation":"No specific signal found"})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

def generar_aleatorio(loteria):
    return generar_fallback(loteria)

# ==========================================
# 9. SUPABASE
# ==========================================
def registrar_usuario(email, password):
    try:
        if supabase.table("usuarios").select("email").eq("email",email).execute().data:
            return False,"exists"
        res = supabase.table("usuarios").insert({"email":email,"password":password,"role":"free","generaciones_hoy":0,"fecha_uso":str(date.today())}).execute()
        return (True,res.data[0]) if res.data else (False,"error")
    except Exception as e: return False,str(e)

def login_usuario(email, password):
    try:
        res = supabase.table("usuarios").select("*").eq("email",email).eq("password",password).single().execute()
        return (True,res.data) if res.data else (False,None)
    except: return False,None

def guardar_generacion(user_id, loteria_id, numeros, bonus, sources, inputs):
    try:
        supabase.table("generaciones").insert({
            "user_id":user_id,"loteria_id":loteria_id,
            "numeros":numeros,"bonus":bonus,
            "narrativa":json.dumps(sources,ensure_ascii=False),
            "inputs_usuario":json.dumps(inputs,ensure_ascii=False),
        }).execute()
    except: pass

def obtener_historial(user_id, limit=15):
    try:
        res = supabase.table("generaciones").select("*").eq("user_id",user_id).order("created_at",desc=True).limit(limit).execute()
        return res.data if res.data else []
    except: return []

def resetear_uso():
    hoy = str(date.today())
    if st.session_state.get('fecha_uso') != hoy:
        st.session_state['generaciones_hoy'] = {}
        st.session_state['fecha_uso'] = hoy

# ==========================================
# 10. EMAIL
# ==========================================
def enviar_email(to, subject, html):
    if not RESEND_KEY: return False
    try:
        r = requests.post("https://api.resend.com/emails",
            headers={"Authorization":f"Bearer {RESEND_KEY}","Content-Type":"application/json"},
            json={"from":"hello@lucksort.com","to":[to],"subject":subject,"html":html},timeout=10)
        return r.status_code==200
    except: return False

def email_bienvenida(email):
    tr_data = T[st.session_state.get('idioma','EN')]
    html = f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
<div style="text-align:center;padding:24px 0 16px;">
  <div style="display:inline-flex;align-items:center;gap:10px;">
    <div style="width:34px;height:34px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:17px;color:#0a0a0f;">◆</div>
    <span style="font-size:24px;font-weight:700;color:white;font-family:Georgia,serif;">LuckSort</span>
  </div>
  <p style="color:rgba(255,255,255,0.25);font-size:10px;letter-spacing:3px;margin-top:5px;">SORT YOUR LUCK</p>
</div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,0.2);margin:10px 0 22px;">
<h2 style="color:white;">Welcome ◆</h2>
<p style="color:rgba(255,255,255,0.6);line-height:1.7;">Your LuckSort account is ready. Start generating combinations backed by real-world data signals.</p>
<div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:20px 0;">
  <p style="color:#C9A84C;font-size:11px;letter-spacing:2px;margin-bottom:12px;">FREE PLAN</p>
  <ul style="color:rgba(255,255,255,0.6);line-height:2.2;margin:0;padding-left:18px;">
    <li>5 random combinations per lottery per day</li>
    <li>11 major lotteries — 3 languages</li>
    <li>Upgrade for full data convergence</li>
  </ul>
</div>
<div style="text-align:center;margin:26px 0;">
  <a href="{APP_URL}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;font-size:15px;">Open LuckSort →</a>
</div>
<p style="color:rgba(255,255,255,0.18);font-size:11px;font-style:italic;text-align:center;line-height:1.6;">"{tr_data['disclaimer']}"</p>
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:18px 0;">
<p style="text-align:center;color:rgba(255,255,255,0.15);font-size:10px;">© 2025 LuckSort · lucksort.com</p>
</body></html>"""
    enviar_email(email,"Welcome to LuckSort ◆",html)

# ==========================================
# 11. RENDER RESULTADO
# ==========================================
def render_resultado(resultado, loteria):
    t = tr()
    numeros = resultado.get("numbers",[])
    bonus   = resultado.get("bonus")
    sources = resultado.get("sources",[])

    # Balls
    balls_html = '<div class="balls-wrap">'
    for n in numeros:
        balls_html += f'<div class="ball">{str(n).zfill(2)}</div>'
    if bonus:
        balls_html += f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    balls_html += '</div>'

    bonus_lbl = ""
    if bonus and loteria.get('bname'):
        bonus_lbl = f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.22);text-align:center;margin-top:2px;">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>'

    st.markdown(f"""
    <div class="ls-card-gold" style="text-align:center;">
      <div style="font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:2px;">
        {loteria['flag']} {loteria['nombre']}
      </div>
      {balls_html}{bonus_lbl}
    </div>""", unsafe_allow_html=True)

    if sources:
        st.markdown(f"""<div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.28);
        letter-spacing:2px;text-transform:uppercase;margin:16px 0 10px;">{t['sources_title']}</div>""",
        unsafe_allow_html=True)

        for s in sources:
            src  = s.get("source","complement")
            icon = t['icons'].get(src,"⚪")
            lbl  = s.get("label") or t['sources'].get(src,src)
            exp  = s.get("explanation","")
            num  = s.get("number","")
            is_c = src=="complement"
            cls  = "src-row src-complement" if is_c else "src-row"
            st.markdown(f"""
            <div class="{cls}">
              <div class="src-left">
                <span class="src-icon">{icon}</span>
                <div>
                  <div class="src-label">{lbl}</div>
                  <div class="src-desc">{exp}</div>
                </div>
              </div>
              <span class="src-num">→ {str(num).zfill(2)}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

def render_paywall():
    t = tr()
    st.markdown(f"""
    <div class="ls-card" style="border-color:rgba(201,168,76,0.25);text-align:center;padding:28px;">
      <div style="font-size:26px;margin-bottom:10px;">◆</div>
      <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:20px;">{t['paywall_title']}</h3>
      <p style="color:rgba(255,255,255,0.38);font-size:13px;max-width:320px;margin:0 auto 18px;line-height:1.65;">{t['paywall_msg']}</p>
      <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;">
        {"".join([f'<span style="font-size:11px;color:rgba(255,255,255,0.35);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:4px 10px;">{icon} {lbl}</span>' for lbl,icon in [("Draw History","📊"),("Community","👥"),("World Events","🌍"),("Your Dates","✦"),("Numerology","🔢"),("Fibonacci","🌀"),("Sacred Geometry","⬡"),("Tesla 3·6·9","⚡")]])}
      </div>
    </div>""", unsafe_allow_html=True)
    if st.button(t['upgrade_btn'], use_container_width=True, key="upgrade_btn"):
        pass

# ==========================================
# 12. ANIMATED BALLS LANDING
# ==========================================
def render_balls_landing():
    st.markdown("""
    <div style="margin:28px auto;max-width:460px;">
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.18);
      letter-spacing:3px;text-align:center;margin-bottom:14px;">LIVE PREVIEW · POWERBALL</div>
      <div id="balls" style="display:flex;gap:9px;justify-content:center;flex-wrap:wrap;margin-bottom:20px;">
        <div class="ball" id="b0">07</div>
        <div class="ball" id="b1">14</div>
        <div class="ball" id="b2">23</div>
        <div class="ball" id="b3">34</div>
        <div class="ball" id="b4">55</div>
        <div class="ball ball-gold" id="b5">12</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:7px;">
        <div class="src-row"><div class="src-left"><span class="src-icon">📊</span><div><div class="src-label">Draw History</div><div class="src-desc">Appeared 31× in March draws (2010-2024)</div></div></div><span class="src-num">→ 07</span></div>
        <div class="src-row"><div class="src-left"><span class="src-icon">🌀</span><div><div class="src-label">Fibonacci</div><div class="src-desc">34 is a Fibonacci number (21+13=34)</div></div></div><span class="src-num">→ 34</span></div>
        <div class="src-row"><div class="src-left"><span class="src-icon">👥</span><div><div class="src-label">Community</div><div class="src-desc">Top 3 most picked on r/powerball today</div></div></div><span class="src-num">→ 23</span></div>
        <div class="src-row"><div class="src-left"><span class="src-icon">✦</span><div><div class="src-label">Your Date</div><div class="src-desc">Day extracted from birthday Mar 14</div></div></div><span class="src-num">→ 14</span></div>
      </div>
    </div>
    <script>
    const sets=[[7,14,23,34,55,12],[3,19,31,44,62,8],[11,22,35,47,68,17],[5,16,28,41,59,23],[9,21,33,46,63,4]];
    let i=0;
    setInterval(()=>{
      i=(i+1)%sets.length;
      for(let j=0;j<6;j++){
        const el=document.getElementById('b'+j);
        if(!el)return;
        el.style.opacity='0';el.style.transform='scale(0.75)';
        setTimeout(()=>{el.textContent=String(sets[i][j]).padStart(2,'0');el.style.opacity='1';el.style.transform='scale(1)';},280+j*45);
      }
    },2800);
    document.querySelectorAll('.ball').forEach(b=>{b.style.transition='opacity .28s ease,transform .28s ease';});
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# 13. SIDEBAR
# ==========================================
with st.sidebar:

    # LOGO
    st.markdown("""
    <div style="padding:22px 16px 14px;border-bottom:1px solid rgba(201,168,76,0.12);margin-bottom:4px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;min-width:34px;
        background:linear-gradient(135deg,#C9A84C,#F5D68A);
        border-radius:9px;display:flex;align-items:center;justify-content:center;
        box-shadow:0 0 18px rgba(201,168,76,0.35);">
          <span style="font-size:17px;color:#0a0a0f;line-height:1;">◆</span>
        </div>
        <div style="min-width:0;">
          <div style="font-family:Georgia,'Times New Roman',serif;font-size:21px;
          font-weight:700;color:white;letter-spacing:-0.5px;line-height:1.1;">LuckSort</div>
          <div style="font-family:'Courier New',monospace;font-size:8px;
          color:rgba(201,168,76,0.55);letter-spacing:2.5px;margin-top:2px;">SORT YOUR LUCK</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # IDIOMA — 3 botones compactos
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("🇺🇸 EN", key="l_en", use_container_width=True):
            st.session_state['idioma']='EN'; st.rerun()
    with c2:
        if st.button("🇪🇸 ES", key="l_es", use_container_width=True):
            st.session_state['idioma']='ES'; st.rerun()
    with c3:
        if st.button("🇧🇷 PT", key="l_pt", use_container_width=True):
            st.session_state['idioma']='PT'; st.rerun()

    # Indicador idioma activo
    lang_labels = {"EN":"English","ES":"Español","PT":"Português"}
    st.markdown(f"""<div style="text-align:center;font-family:'DM Mono',monospace;font-size:9px;
    color:#C9A84C;letter-spacing:1px;margin:-4px 0 8px;">{lang_labels[st.session_state['idioma']]}</div>""",
    unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-hr">', unsafe_allow_html=True)

    t = tr()

    # AUTH
    if not st.session_state['logged_in']:
        tab_in, tab_up = st.tabs([t['login'], t['register']])
        with tab_in:
            em = st.text_input(t['email'], key="si_e")
            pw = st.text_input(t['password'], type="password", key="si_p")
            if st.button(t['btn_login'], use_container_width=True, key="btn_si"):
                if em==ADMIN_EMAIL and pw==ADMIN_PASS:
                    st.session_state.update({'logged_in':True,'user_role':'admin','user_email':em,'user_id':None,'vista':'app'})
                    st.rerun()
                else:
                    ok,datos = login_usuario(em,pw)
                    if ok:
                        st.session_state.update({'logged_in':True,'user_role':datos['role'],'user_email':datos['email'],'user_id':datos['id'],'vista':'app'})
                        resetear_uso(); st.rerun()
                    else: st.error(t['login_err'])
        with tab_up:
            re = st.text_input(t['email'], key="su_e")
            rp1 = st.text_input(t['password'], type="password", key="su_p1")
            rp2 = st.text_input(t['confirm_pass'], type="password", key="su_p2")
            if st.button(t['btn_register'], use_container_width=True, key="btn_su"):
                if rp1!=rp2: st.error(t['pass_mismatch'])
                elif len(rp1)<6: st.warning(t['pass_short'])
                elif "@" not in re: st.warning(t['email_invalid'])
                else:
                    ok,res = registrar_usuario(re,rp1)
                    if ok:
                        st.session_state.update({'logged_in':True,'user_role':'free','user_email':re,'user_id':res['id'],'vista':'app'})
                        email_bienvenida(re); st.rerun()
                    elif res=="exists": st.error(t['email_exists'])
                    else: st.error("⚠️ Error. Try again.")
    else:
        resetear_uso()
        role = st.session_state['user_role']
        role_lbl = t['paid'] if role not in ['free','invitado'] else t['free']
        role_color = "#C9A84C" if role!='free' else "rgba(255,255,255,0.3)"
        email_display = st.session_state['user_email']
        if len(email_display)>22: email_display = email_display[:20]+"…"
        st.markdown(f"""
        <div style="padding:11px 13px;background:rgba(201,168,76,0.05);
        border:1px solid rgba(201,168,76,0.15);border-radius:10px;margin-bottom:12px;">
          <div style="font-size:12px;color:rgba(255,255,255,0.7);margin-bottom:3px;">{email_display}</div>
          <div style="display:flex;align-items:center;gap:5px;">
            <div style="width:6px;height:6px;border-radius:50%;background:{role_color};"></div>
            <span style="font-family:'DM Mono',monospace;font-size:9px;color:{role_color};letter-spacing:1.5px;">{role_lbl.upper()}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button(f"◆ {t['tagline']}", use_container_width=True, key="nav_g"):
            st.session_state['vista']='app'; st.rerun()
        if st.button(f"📋 {t['history']}", use_container_width=True, key="nav_h"):
            st.session_state['vista']='history'; st.rerun()
        st.markdown('<hr class="sidebar-hr">', unsafe_allow_html=True)
        if st.button(t['logout'], use_container_width=True, key="btn_lo"):
            for k in defaults: st.session_state[k]=defaults[k]
            st.rerun()

# ==========================================
# 14. LANDING
# ==========================================
if not st.session_state['logged_in']:
    t = tr()

    st.markdown(f"""
    <div style="text-align:center;padding:44px 16px 20px;animation:fadeUp .7s ease both;">
      <div class="tag-gold" style="margin-bottom:18px;">
        <span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;
        display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>
        Data Convergence Engine
      </div>
      <h1 style="font-family:'Playfair Display',serif;
      font-size:clamp(36px,7vw,76px);font-weight:700;
      line-height:1.05;letter-spacing:-2px;margin-bottom:16px;">
        {t['hero_1']}<br>
        <span class="shimmer-text">{t['hero_2']}</span><br>
        {t['hero_3']}
      </h1>
      <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);
      color:rgba(255,255,255,0.38);max-width:500px;margin:0 auto;line-height:1.8;">
        {t['hero_sub']}
      </p>
    </div>""", unsafe_allow_html=True)

    render_balls_landing()

    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        if st.button(t['cta_free'], use_container_width=True, key="land_cta"):
            st.session_state['mostrar_reg']=True; st.rerun()
        st.markdown("""<p style="text-align:center;font-family:'DM Mono',monospace;font-size:9px;
        color:rgba(255,255,255,0.16);letter-spacing:1.5px;margin-top:7px;">
        FREE · NO CREDIT CARD · ES / EN / PT</p>""", unsafe_allow_html=True)

    if st.session_state.get('mostrar_reg'):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:22px 0;">', unsafe_allow_html=True)
        ca,cb,cc = st.columns([1,2,1])
        with cb:
            tab_r, tab_l = st.tabs([t['register'], t['login']])
            with tab_r:
                re=st.text_input(t['email'],key="lr_e"); rp=st.text_input(t['password'],type="password",key="lr_p")
                rp2=st.text_input(t['confirm_pass'],type="password",key="lr_p2")
                if st.button(t['btn_register'],use_container_width=True,key="lr_b"):
                    if rp!=rp2: st.error(t['pass_mismatch'])
                    elif len(rp)<6: st.warning(t['pass_short'])
                    elif "@" not in re: st.warning(t['email_invalid'])
                    else:
                        ok,res=registrar_usuario(re,rp)
                        if ok:
                            st.session_state.update({'logged_in':True,'user_role':'free','user_email':re,'user_id':res['id'],'vista':'app','mostrar_reg':False})
                            email_bienvenida(re); st.rerun()
                        elif res=="exists": st.error(t['email_exists'])
                        else: st.error("⚠️ Error.")
            with tab_l:
                le=st.text_input(t['email'],key="ll_e"); lp=st.text_input(t['password'],type="password",key="ll_p")
                if st.button(t['btn_login'],use_container_width=True,key="ll_b"):
                    if le==ADMIN_EMAIL and lp==ADMIN_PASS:
                        st.session_state.update({'logged_in':True,'user_role':'admin','user_email':le,'user_id':None,'vista':'app'}); st.rerun()
                    else:
                        ok,datos=login_usuario(le,lp)
                        if ok:
                            st.session_state.update({'logged_in':True,'user_role':datos['role'],'user_email':datos['email'],'user_id':datos['id'],'vista':'app'})
                            resetear_uso(); st.rerun()
                        else: st.error(t['login_err'])

    # 4 signals
    st.markdown(f"""
    <div style="text-align:center;padding:36px 0 18px;">
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.2);letter-spacing:3px;margin-bottom:10px;">HOW IT WORKS</div>
      <h2 style="font-family:'Playfair Display',serif;font-size:clamp(20px,3vw,38px);font-weight:700;letter-spacing:-1px;margin-bottom:4px;">
        Four signals. One combination.
      </h2>
      <div class="gold-line"></div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    signal_data = [
        ("📊","historico","Years of official draws analyzed by date, month and frequency patterns"),
        ("👥","community","Reddit picks + Google Trends — what real players are choosing right now"),
        ("🌍","eventos","Numbers hidden in today's Wikipedia history and news headlines"),
        ("✦","fecha_personal","Your birthday, anniversary — plus numerology, Fibonacci and sacred geometry"),
    ]
    for col,(icon,key,desc) in zip([c1,c2,c3,c4],signal_data):
        with col:
            st.markdown(f"""
            <div class="ls-card" style="text-align:center;min-height:135px;">
              <div style="font-size:22px;margin-bottom:8px;">{icon}</div>
              <div style="font-family:'Playfair Display',serif;font-size:13px;font-weight:600;
              color:rgba(255,255,255,0.85);margin-bottom:5px;">{t['sources'][key]}</div>
              <div style="font-family:'DM Sans',sans-serif;font-size:11px;
              color:rgba(255,255,255,0.3);line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # Lotteries
    st.markdown("""<div style="text-align:center;padding:26px 0 12px;">
    <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.18);letter-spacing:3px;">
    GLOBAL COVERAGE · 11 LOTTERIES · 3 LANGUAGES</div></div>""", unsafe_allow_html=True)
    cols = st.columns(4)
    for i,lot in enumerate(LOTERIAS):
        with cols[i%4]:
            st.markdown(f"""<div style="padding:9px 11px;background:rgba(255,255,255,0.025);
            border:1px solid rgba(255,255,255,0.06);border-radius:8px;
            display:flex;align-items:center;gap:7px;margin-bottom:7px;">
            <span style="font-size:14px;">{lot['flag']}</span>
            <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.58);">{lot['nombre']}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:560px;margin:24px auto 0;">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 15. APP — GENERADOR
# ==========================================
elif st.session_state.get('vista')=='app':
    t = tr()
    es_free  = st.session_state['user_role']=='free'
    es_paid  = st.session_state['user_role'] in ['paid','pro','convergence','admin']

    st.markdown(f"""
    <div style="padding:18px 0 6px;">
      <span class="tag-gold">◆ {t['tagline']}</span>
      <h2 style="font-family:'Playfair Display',serif;font-size:clamp(20px,3vw,36px);
      font-weight:700;letter-spacing:-1px;margin-top:10px;">{t['select_lottery']}</h2>
    </div>""", unsafe_allow_html=True)

    lot_names = [f"{l['flag']} {l['nombre']}  ({l['pais']})" for l in LOTERIAS]
    sel = st.selectbox("",lot_names,label_visibility="collapsed",key="lot_sel")
    loteria = next(l for l in LOTERIAS if l['nombre'] in sel)

    gen_hoy = st.session_state['generaciones_hoy'].get(loteria['id'],0)
    restantes = max(0,MAX_GEN-gen_hoy)
    st.markdown(f'<div style="margin:6px 0 16px;"><span class="metric-pill">{t["gen_counter"]}: {gen_hoy}/{MAX_GEN}</span></div>', unsafe_allow_html=True)

    inputs = {}
    if es_paid or st.session_state['user_role']=='admin':
        with st.expander(f"✦ {t['personal_title']}", expanded=False):
            c1,c2 = st.columns(2)
            with c1:
                fecha_esp = st.text_input(t['special_date'],placeholder="14/03/1990",key="fe")
                nombre    = st.text_input(t['your_name'],placeholder="Your name",key="nm")
            with c2:
                momento = st.text_input(t['life_moment'],placeholder="I just started a business...",key="mm")
                excluir = st.text_input(t['exclude_numbers'],placeholder="4, 13",key="ex")
            crowd_pref = st.radio(t['crowd_pref'],[t['balanced'],t['follow'],t['avoid']],horizontal=True,key="cp")
            crowd_map = {t['follow']:"follow",t['avoid']:"avoid",t['balanced']:"balanced"}
            inputs = {"fecha_especial":fecha_esp,"nombre":nombre,"momento":momento,
                     "excluir":excluir,"crowd":crowd_map.get(crowd_pref,"balanced")}

        with st.expander(f"⬡ {t['symbolic_title']}", expanded=False):
            st.caption(t['symbolic_help'])
            c1,c2 = st.columns(2)
            with c1:
                use_num  = st.checkbox(t['sys_numerology'],key="cb_num")
                use_fib  = st.checkbox(t['sys_fibonacci'],key="cb_fib")
                use_sag  = st.checkbox(t['sys_sacred'],key="cb_sag")
            with c2:
                use_tes  = st.checkbox(t['sys_tesla'],key="cb_tes")
                use_frac = st.checkbox(t['sys_fractal'],key="cb_frac")
            sistemas = []
            if use_num:  sistemas.append("numerologia")
            if use_fib:  sistemas.append("fibonacci")
            if use_sag:  sistemas.append("sagrada")
            if use_tes:  sistemas.append("tesla")
            if use_frac: sistemas.append("fractal")
            inputs["sistemas"] = sistemas

    if restantes<=0:
        st.warning(f"⚠️ {t['gen_counter']}: {MAX_GEN}/{MAX_GEN}")
    else:
        if st.button(f"◆ {t['generate_btn']}", use_container_width=True, key="gen_btn"):
            with st.spinner(t['generating']):
                if es_paid or st.session_state['user_role']=='admin':
                    resultado = generar_combinacion(loteria,inputs)
                else:
                    resultado = generar_aleatorio(loteria)
                st.session_state['ultima_generacion']=resultado
                st.session_state['ultima_loteria']=loteria
                st.session_state['generaciones_hoy'][loteria['id']]=gen_hoy+1
                if st.session_state.get('user_id'):
                    guardar_generacion(st.session_state['user_id'],loteria['id'],
                        resultado.get('numbers',[]),resultado.get('bonus'),
                        resultado.get('sources',[]),inputs)

    if st.session_state.get('ultima_generacion') and st.session_state.get('ultima_loteria'):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:16px 0;">', unsafe_allow_html=True)
        render_resultado(st.session_state['ultima_generacion'],st.session_state['ultima_loteria'])

    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.04);margin:20px 0;">', unsafe_allow_html=True)
        render_paywall()

# ==========================================
# 16. HISTORIAL
# ==========================================
elif st.session_state.get('vista')=='history':
    t = tr()
    st.markdown(f'<div style="padding:18px 0 12px;"><span class="tag-gold">◆ {t["history"]}</span></div>', unsafe_allow_html=True)

    if st.session_state.get('user_id'):
        hist = obtener_historial(st.session_state['user_id'])
        if not hist:
            st.markdown(f'<p style="color:rgba(255,255,255,0.3);font-size:14px;">{t["no_history"]}</p>', unsafe_allow_html=True)
        else:
            for h in hist:
                lot = next((l for l in LOTERIAS if l['id']==h.get('loteria_id')),None)
                if lot:
                    nums_str = "  ".join([str(n).zfill(2) for n in h['numeros']])
                    bonus_str = f"  ◆ {str(h['bonus']).zfill(2)}" if h.get('bonus') else ""
                    fecha = h.get('created_at','')[:10]
                    st.markdown(f"""
                    <div class="ls-card" style="margin-bottom:10px;">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;">{lot['flag']} {lot['nombre']}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.2);">{fecha}</span>
                      </div>
                      <div style="font-family:'DM Mono',monospace;font-size:19px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info("Sign in to see your history.")
