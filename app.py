import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime
import requests
import random
import json

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆",
    layout="wide"
)

defaults = {
    'logged_in': False,
    'user_role': 'invitado',
    'user_email': '',
    'user_id': None,
    'idioma': 'EN',
    'fecha_uso': str(date.today()),
    'generaciones_hoy': {},
    'ultima_generacion': None,
    'ultima_loteria': None,
    'vista': 'landing',
    'mostrar_reg': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 2. CSS DARK GOLD THEME
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');

* { box-sizing: border-box; }
body, .stApp { background-color: #0a0a0f !important; color: white !important; }
.stApp { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #0a0a0f 100%) !important;
    border-right: 1px solid rgba(201,168,76,0.12) !important;
    min-width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* BUTTONS — gold primary */
.stButton>button {
    background: linear-gradient(135deg, #C9A84C, #F5D68A) !important;
    color: #0a0a0f !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(201,168,76,0.25) !important;
}
.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(201,168,76,0.38) !important;
}

/* ghost button override */
[data-testid="stSidebar"] .stButton>button[kind="secondary"],
.ghost-btn button {
    background: transparent !important;
    color: rgba(255,255,255,0.55) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    box-shadow: none !important;
}

/* INPUTS */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
    background-color: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput>div>div>input:focus {
    border-color: rgba(201,168,76,0.45) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.08) !important;
}
.stSelectbox>div>div {
    background-color: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: white !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.45) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    color: #C9A84C !important;
    background: rgba(201,168,76,0.1) !important;
    border-radius: 6px !important;
}

/* RADIO */
.stRadio>div { flex-direction: row !important; gap: 10px !important; flex-wrap: wrap !important; }
.stRadio>div>label {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    color: rgba(255,255,255,0.55) !important;
    font-size: 13px !important;
}

/* EXPANDER */
.stExpander {
    border: 1px solid rgba(201,168,76,0.15) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.02) !important;
}

/* ANIMATIONS */
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes ballPulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 12px rgba(201,168,76,0.3); }
    50% { transform: scale(1.06); box-shadow: 0 0 24px rgba(201,168,76,0.55); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes spin {
    0% { transform: rotate(0deg) scale(1); opacity: 0.4; }
    50% { transform: rotate(180deg) scale(1.1); opacity: 0.7; }
    100% { transform: rotate(360deg) scale(1); opacity: 0.4; }
}

.shimmer {
    background: linear-gradient(90deg, #C9A84C 0%, #F5D68A 35%, #C9A84C 65%, #F5D68A 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
}

/* CARDS */
.luck-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 14px;
}
.luck-card-gold {
    background: rgba(201,168,76,0.055);
    border: 1px solid rgba(201,168,76,0.22);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 14px;
}

/* NUMBER BALLS */
.balls-wrap {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin: 18px 0;
}
.ball {
    width: 54px; height: 54px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 17px; font-weight: 600;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    color: rgba(255,255,255,0.9);
}
.ball-gold {
    background: linear-gradient(135deg, #C9A84C, #F5D68A);
    border: none;
    color: #0a0a0f;
    animation: ballPulse 2.5s ease-in-out infinite;
}

/* SOURCE ROWS */
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
.src-left { display: flex; align-items: flex-start; gap: 10px; flex: 1; }
.src-icon { font-size: 16px; margin-top: 1px; flex-shrink: 0; }
.src-label { font-family: 'DM Sans',sans-serif; font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.7); }
.src-desc { font-family: 'DM Sans',sans-serif; font-size: 11px; color: rgba(255,255,255,0.35); line-height: 1.55; margin-top: 2px; }
.src-num { font-family: 'DM Mono',monospace; font-size: 15px; color: #C9A84C; font-weight: 600; flex-shrink: 0; margin-top: 2px; }
.src-complement { border-color: rgba(255,255,255,0.04); background: rgba(255,255,255,0.015); }
.src-complement .src-num { color: rgba(255,255,255,0.3); }

/* MISC */
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
    display: inline-block;
    padding: 4px 12px; border-radius: 20px;
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
    line-height: 1.65; font-style: italic;
    margin-top: 16px;
}
.gold-line {
    width: 36px; height: 2px;
    background: linear-gradient(90deg, transparent, #C9A84C, transparent);
    margin: 10px auto;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CREDENCIALES
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    RESEND_API_KEY = st.secrets.get("RESEND_API_KEY", "")
    ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL", "admin@lucksort.com")
    ADMIN_PASS = st.secrets.get("ADMIN_PASS", "admin123")
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")
except:
    st.error("⚠️ Configure your secrets in Streamlit Cloud settings.")
    st.stop()

client_groq = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
APP_URL = "https://lucksort.streamlit.app"

# ==========================================
# 4. LOTERÍAS
# ==========================================
LOTERIAS = [
    {"id": 1,  "nombre": "Powerball",     "pais": "USA",     "bandera": "🇺🇸", "min": 1, "max": 69, "cantidad": 5, "bonus": True,  "bonus_max": 26,  "bonus_name": "Powerball"},
    {"id": 2,  "nombre": "Mega Millions", "pais": "USA",     "bandera": "🇺🇸", "min": 1, "max": 70, "cantidad": 5, "bonus": True,  "bonus_max": 25,  "bonus_name": "Mega Ball"},
    {"id": 3,  "nombre": "EuroMillions",  "pais": "Europa",  "bandera": "🇪🇺", "min": 1, "max": 50, "cantidad": 5, "bonus": True,  "bonus_max": 12,  "bonus_name": "Lucky Star"},
    {"id": 4,  "nombre": "UK Lotto",      "pais": "UK",      "bandera": "🇬🇧", "min": 1, "max": 59, "cantidad": 6, "bonus": False, "bonus_max": None,"bonus_name": None},
    {"id": 5,  "nombre": "El Gordo",      "pais": "España",  "bandera": "🇪🇸", "min": 1, "max": 54, "cantidad": 5, "bonus": True,  "bonus_max": 10,  "bonus_name": "Reintegro"},
    {"id": 6,  "nombre": "Mega-Sena",     "pais": "Brasil",  "bandera": "🇧🇷", "min": 1, "max": 60, "cantidad": 6, "bonus": False, "bonus_max": None,"bonus_name": None},
    {"id": 7,  "nombre": "Lotofácil",     "pais": "Brasil",  "bandera": "🇧🇷", "min": 1, "max": 25, "cantidad": 15,"bonus": False, "bonus_max": None,"bonus_name": None},
    {"id": 8,  "nombre": "Baloto",        "pais": "Colombia","bandera": "🇨🇴", "min": 1, "max": 43, "cantidad": 6, "bonus": True,  "bonus_max": 16,  "bonus_name": "Balota"},
    {"id": 9,  "nombre": "La Primitiva",  "pais": "España",  "bandera": "🇪🇸", "min": 1, "max": 49, "cantidad": 6, "bonus": False, "bonus_max": None,"bonus_name": None},
    {"id": 10, "nombre": "EuroJackpot",   "pais": "Europa",  "bandera": "🇪🇺", "min": 1, "max": 50, "cantidad": 5, "bonus": True,  "bonus_max": 12,  "bonus_name": "Euro Number"},
    {"id": 11, "nombre": "Canada Lotto",  "pais": "Canadá",  "bandera": "🇨🇦", "min": 1, "max": 49, "cantidad": 6, "bonus": True,  "bonus_max": 49,  "bonus_name": "Bonus"},
]

MAX_GEN = 5

# ==========================================
# 5. TRADUCCIONES
# ==========================================
T = {
    "EN": {
        "tagline": "Sort Your Luck",
        "hero_1": "Your numbers,", "hero_2": "backed by the", "hero_3": "world's signals.",
        "hero_sub": "We gather real data — historical draws, today's headlines, community picks, and your personal dates — converged into combinations that mean something.",
        "cta_free": "Start Free",
        "login": "Sign In", "register": "Create Account", "logout": "Sign Out",
        "email": "Email", "password": "Password", "confirm_pass": "Confirm Password",
        "btn_login": "Sign In", "btn_register": "Create Free Account",
        "plan": "Plan", "free": "Free", "paid": "Convergence",
        "select_lottery": "Select Lottery",
        "personal_inputs": "Tell us about you (optional)",
        "special_date": "Special date (birthday, anniversary...)",
        "your_name": "Your name",
        "life_moment": "Something happening in your life right now",
        "exclude_numbers": "Numbers to exclude (comma separated)",
        "follow_crowd": "Crowd preference",
        "follow": "Follow the crowd", "avoid": "Avoid the crowd", "balanced": "Balanced",
        "generate_btn": "Generate Combination",
        "generating": "Converging 4 data sources...",
        "sources_title": "Where each number comes from",
        "gen_left": "Today", "of": "of",
        "disclaimer": "We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
        "paywall_title": "Convergence Plan",
        "paywall_msg": "Unlock data-driven generation with historical analysis, community intelligence, world events and your personal dates.",
        "upgrade_btn": "Upgrade — $9.99/month",
        "history": "My History", "no_history": "No combinations yet.",
        "login_err": "❌ Incorrect credentials.",
        "pass_mismatch": "⚠️ Passwords don't match.",
        "pass_short": "⚠️ Minimum 6 characters.",
        "email_invalid": "⚠️ Invalid email.",
        "email_exists": "⚠️ Email already registered.",
        "complement": "Complement",
        "complement_desc": "No specific signal found for this position today",
        "sources": {
            "historico": "Draw History",
            "community": "Community",
            "eventos": "World Events",
            "fecha_personal": "Your Date",
            "complement": "Complement",
        },
        "src_icons": {
            "historico": "📊", "community": "👥",
            "eventos": "🌍", "fecha_personal": "✦", "complement": "⚪",
        }
    },
    "ES": {
        "tagline": "Ordena tu Suerte",
        "hero_1": "Tus números,", "hero_2": "respaldados por", "hero_3": "las señales del mundo.",
        "hero_sub": "Recopilamos datos reales — sorteos históricos, titulares de hoy, picks de la comunidad y tus fechas personales — convergidos en combinaciones con significado.",
        "cta_free": "Empezar Gratis",
        "login": "Entrar", "register": "Crear Cuenta", "logout": "Cerrar Sesión",
        "email": "Correo", "password": "Contraseña", "confirm_pass": "Confirmar contraseña",
        "btn_login": "Entrar", "btn_register": "Crear Cuenta Gratis",
        "plan": "Plan", "free": "Gratis", "paid": "Convergencia",
        "select_lottery": "Selecciona tu Lotería",
        "personal_inputs": "Cuéntanos sobre ti (opcional)",
        "special_date": "Fecha especial (cumpleaños, aniversario...)",
        "your_name": "Tu nombre",
        "life_moment": "Algo que está pasando en tu vida ahora",
        "exclude_numbers": "Números a excluir (separados por coma)",
        "follow_crowd": "Preferencia de comunidad",
        "follow": "Seguir la masa", "avoid": "Ir contra la masa", "balanced": "Balanceado",
        "generate_btn": "Generar Combinación",
        "generating": "Convergiendo 4 fuentes de datos...",
        "sources_title": "De dónde viene cada número",
        "gen_left": "Hoy", "of": "de",
        "disclaimer": "Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
        "paywall_title": "Plan Convergencia",
        "paywall_msg": "Desbloquea la generación basada en datos con análisis histórico, inteligencia de comunidad, eventos mundiales y tus fechas personales.",
        "upgrade_btn": "Actualizar — $9.99/mes",
        "history": "Mi Historial", "no_history": "Aún no has generado combinaciones.",
        "login_err": "❌ Credenciales incorrectas.",
        "pass_mismatch": "⚠️ Las contraseñas no coinciden.",
        "pass_short": "⚠️ Mínimo 6 caracteres.",
        "email_invalid": "⚠️ Email inválido.",
        "email_exists": "⚠️ El correo ya está registrado.",
        "complement": "Complemento",
        "complement_desc": "Sin señal específica encontrada para esta posición hoy",
        "sources": {
            "historico": "Histórico", "community": "Comunidad",
            "eventos": "Eventos", "fecha_personal": "Tu Fecha", "complement": "Complemento",
        },
        "src_icons": {
            "historico": "📊", "community": "👥",
            "eventos": "🌍", "fecha_personal": "✦", "complement": "⚪",
        }
    },
    "PT": {
        "tagline": "Organize sua Sorte",
        "hero_1": "Seus números,", "hero_2": "respaldados pelos", "hero_3": "sinais do mundo.",
        "hero_sub": "Coletamos dados reais — histórico de sorteios, manchetes de hoje, picks da comunidade e suas datas pessoais — convergidos em combinações com significado.",
        "cta_free": "Começar Grátis",
        "login": "Entrar", "register": "Criar Conta", "logout": "Sair",
        "email": "Email", "password": "Senha", "confirm_pass": "Confirmar senha",
        "btn_login": "Entrar", "btn_register": "Criar Conta Grátis",
        "plan": "Plano", "free": "Grátis", "paid": "Convergência",
        "select_lottery": "Selecione sua Loteria",
        "personal_inputs": "Nos conte sobre você (opcional)",
        "special_date": "Data especial (aniversário, data especial...)",
        "your_name": "Seu nome",
        "life_moment": "Algo acontecendo na sua vida agora",
        "exclude_numbers": "Números a excluir (separados por vírgula)",
        "follow_crowd": "Preferência da comunidade",
        "follow": "Seguir a massa", "avoid": "Ir contra a massa", "balanced": "Balanceado",
        "generate_btn": "Gerar Combinação",
        "generating": "Convergindo 4 fontes de dados...",
        "sources_title": "De onde vem cada número",
        "gen_left": "Hoje", "of": "de",
        "disclaimer": "Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
        "paywall_title": "Plano Convergência",
        "paywall_msg": "Desbloqueie a geração baseada em dados com análise histórica, inteligência da comunidade, eventos mundiais e suas datas pessoais.",
        "upgrade_btn": "Atualizar — $9.99/mês",
        "history": "Meu Histórico", "no_history": "Ainda não gerou combinações.",
        "login_err": "❌ Credenciais incorretas.",
        "pass_mismatch": "⚠️ As senhas não coincidem.",
        "pass_short": "⚠️ Mínimo 6 caracteres.",
        "email_invalid": "⚠️ Email inválido.",
        "email_exists": "⚠️ Email já cadastrado.",
        "complement": "Complemento",
        "complement_desc": "Nenhum sinal específico encontrado para esta posição hoje",
        "sources": {
            "historico": "Histórico", "community": "Comunidade",
            "eventos": "Eventos", "fecha_personal": "Sua Data", "complement": "Complemento",
        },
        "src_icons": {
            "historico": "📊", "community": "👥",
            "eventos": "🌍", "fecha_personal": "✦", "complement": "⚪",
        }
    }
}

def t():
    return T[st.session_state['idioma']]

# ==========================================
# 6. SUPABASE
# ==========================================
def registrar_usuario(email, password):
    try:
        if supabase.table("usuarios").select("email").eq("email", email).execute().data:
            return False, "exists"
        res = supabase.table("usuarios").insert({
            "email": email, "password": password,
            "role": "free", "generaciones_hoy": 0,
            "fecha_uso": str(date.today())
        }).execute()
        return (True, res.data[0]) if res.data else (False, "error")
    except Exception as e:
        return False, str(e)

def login_usuario(email, password):
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).eq("password", password).single().execute()
        return (True, res.data) if res.data else (False, None)
    except:
        return False, None

def guardar_generacion(user_id, loteria_id, numeros, bonus, narrativa, inputs):
    try:
        supabase.table("generaciones").insert({
            "user_id": user_id, "loteria_id": loteria_id,
            "numeros": numeros, "bonus": bonus,
            "narrativa": narrativa, "inputs_usuario": json.dumps(inputs),
        }).execute()
    except:
        pass

def obtener_historial(user_id, limit=15):
    try:
        res = supabase.table("generaciones").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return res.data if res.data else []
    except:
        return []

def resetear_uso_diario():
    hoy = str(date.today())
    if st.session_state.get('fecha_uso') != hoy:
        st.session_state['generaciones_hoy'] = {}
        st.session_state['fecha_uso'] = hoy

# ==========================================
# 7. DATOS EXTERNOS (CACHÉ DIARIO)
# ==========================================
def get_cache(tipo):
    try:
        hoy = str(date.today())
        res = supabase.table("cache_diario").select("*").eq("fecha", hoy).eq("tipo", tipo).execute()
        return res.data[0]['contenido'] if res.data else None
    except:
        return None

def set_cache(tipo, contenido, fuente=""):
    try:
        hoy = str(date.today())
        ex = supabase.table("cache_diario").select("id").eq("fecha", hoy).eq("tipo", tipo).execute()
        if ex.data:
            supabase.table("cache_diario").update({"contenido": contenido}).eq("id", ex.data[0]['id']).execute()
        else:
            supabase.table("cache_diario").insert({"fecha": hoy, "tipo": tipo, "contenido": contenido, "fuente": fuente}).execute()
    except:
        pass

def obtener_efemerides(fecha_personal=None):
    """Efemérides del día del sorteo — si hay fecha personal, también las de esa fecha"""
    cache = get_cache("efemerides")
    if cache:
        return cache
    try:
        hoy = datetime.now()
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{hoy.month}/{hoy.day}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            eventos = r.json().get("events", [])[:6]
            resultado = [{"year": e.get("year"), "text": e.get("text", "")[:150]} for e in eventos]
            set_cache("efemerides", resultado, "wikipedia")
            return resultado
    except:
        pass
    return []

def obtener_efemerides_fecha(dia, mes):
    """Efemérides de una fecha específica del usuario"""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{mes}/{dia}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            eventos = r.json().get("events", [])[:4]
            return [{"year": e.get("year"), "text": e.get("text", "")[:150]} for e in eventos]
    except:
        pass
    return []

def obtener_noticias():
    cache = get_cache("noticias")
    if cache:
        return cache
    try:
        if NEWS_API_KEY:
            url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=6&apiKey={NEWS_API_KEY}"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                arts = r.json().get("articles", [])[:6]
                resultado = [{"title": a.get("title", "")[:120], "source": a.get("source", {}).get("name", "")} for a in arts]
                set_cache("noticias", resultado, "newsapi")
                return resultado
    except:
        pass
    return []

def obtener_crowd():
    cache = get_cache("crowd")
    if cache:
        return cache
    # Números populares basados en patrones conocidos de comunidades de lotería
    # Se actualizará con trendspyg en próxima entrega
    base = [7, 11, 14, 17, 21, 23, 27, 32, 38, 42, 3, 8, 13, 19, 29]
    crowd = random.sample(base, min(10, len(base)))
    set_cache("crowd", crowd, "community_base")
    return crowd

# ==========================================
# 8. GENERACIÓN CON GROQ
# ==========================================
def generar_combinacion(loteria, inputs_usuario):
    lang = st.session_state['idioma']
    lang_map = {"EN": "English", "ES": "Spanish", "PT": "Portuguese"}
    lang_full = lang_map[lang]

    efemerides_hoy = obtener_efemerides()
    noticias = obtener_noticias()
    crowd = obtener_crowd()

    # Efemérides de fecha personal si existe
    efemerides_personal = []
    fecha_esp = inputs_usuario.get("fecha_especial", "")
    if fecha_esp:
        try:
            partes = [x for x in fecha_esp.replace("/","-").replace(".","-").split("-") if x.isdigit()]
            if len(partes) >= 2:
                dia_p, mes_p = int(partes[0]), int(partes[1])
                if 1 <= dia_p <= 31 and 1 <= mes_p <= 12:
                    efemerides_personal = obtener_efemerides_fecha(dia_p, mes_p)
        except:
            pass

    excluir = []
    if inputs_usuario.get("excluir"):
        try:
            excluir = [int(x.strip()) for x in inputs_usuario["excluir"].split(",") if x.strip().isdigit()]
        except:
            pass

    bonus_instruccion = ""
    if loteria['bonus']:
        bonus_instruccion = f"- 1 {loteria['bonus_name']} between 1 and {loteria['bonus_max']} (different pool from main numbers)"
    
    prompt = f"""You are LuckSort's data convergence engine. Your task is to generate a {loteria['nombre']} combination using ONLY real data signals.

LOTTERY: {loteria['nombre']} ({loteria['pais']})
RULES:
- Exactly {loteria['cantidad']} unique main numbers between {loteria['min']} and {loteria['max']}
{bonus_instruccion}
- Numbers to EXCLUDE: {excluir if excluir else 'none'}
- Crowd preference: {inputs_usuario.get('crowd', 'balanced')} (follow=use crowd numbers, avoid=avoid them, balanced=mix)

REAL DATA AVAILABLE TODAY:
1. TODAY'S HISTORICAL EVENTS (Wikipedia, draw date {datetime.now().strftime('%B %d')}):
{json.dumps(efemerides_hoy[:4], ensure_ascii=False)}

2. USER'S PERSONAL DATE EVENTS ({fecha_esp if fecha_esp else 'not provided'}):
{json.dumps(efemerides_personal[:3], ensure_ascii=False) if efemerides_personal else 'No personal date provided'}

3. TODAY'S NEWS HEADLINES:
{json.dumps(noticias[:4], ensure_ascii=False)}

4. COMMUNITY POPULAR NUMBERS TODAY: {crowd[:8]}

USER INFO: name={inputs_usuario.get('nombre','')}, life_moment={inputs_usuario.get('momento','')}

CRITICAL RULES:
1. Each number MUST come from a REAL specific signal in the data above
2. Extract numbers from: years (1986→86 or 8+6=14), dates (March 14→14 or 3), quantities, rankings, digits in headlines
3. If you cannot find a real signal for a required position → use source "complement" with honest explanation
4. NEVER invent or fabricate a source connection
5. All numbers must be UNIQUE and within valid range for {loteria['nombre']}
6. If crowd preference is "follow" → prioritize numbers from community list
7. If crowd preference is "avoid" → exclude community numbers when possible

Respond ONLY in {lang_full} with this exact JSON (no extra text, no markdown):
{{
  "numbers": [list of {loteria['cantidad']} integers],
  "bonus": {f'integer between 1-{loteria["bonus_max"]}' if loteria['bonus'] else 'null'},
  "sources": [
    {{"number": N, "source": "historico|community|eventos|fecha_personal|complement", "label": "short source name in {lang_full}", "explanation": "specific real reason — what exact data point, be concrete and specific, minimum 15 words"}},
    ... (one entry per number including bonus if applicable)
  ]
}}"""

    try:
        response = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are LuckSort convergence engine. Respond ONLY in {lang_full}. Return ONLY valid JSON. Be specific and concrete in explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.65,
            max_tokens=1200
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        # Fix potential trailing issues
        if raw.count('{') > raw.count('}'):
            raw += '}'
        resultado = json.loads(raw)
        
        # Validate ranges
        nums = resultado.get("numbers", [])
        valid_nums = [n for n in nums if loteria['min'] <= n <= loteria['max'] and n not in excluir]
        if len(valid_nums) < loteria['cantidad']:
            # Fill missing with random valid numbers
            all_valid = [n for n in range(loteria['min'], loteria['max']+1) if n not in valid_nums and n not in excluir]
            while len(valid_nums) < loteria['cantidad'] and all_valid:
                pick = random.choice(all_valid)
                valid_nums.append(pick)
                all_valid.remove(pick)
        resultado['numbers'] = valid_nums[:loteria['cantidad']]
        
        # Validate bonus
        if loteria['bonus'] and resultado.get('bonus'):
            b = resultado['bonus']
            if not (1 <= b <= loteria['bonus_max']):
                resultado['bonus'] = random.randint(1, loteria['bonus_max'])
        
        return resultado
    except Exception as e:
        return generar_fallback(loteria, excluir)

def generar_fallback(loteria, excluir=[]):
    """Generación aleatoria limpia como fallback"""
    pool = [n for n in range(loteria['min'], loteria['max']+1) if n not in excluir]
    numeros = random.sample(pool, min(loteria['cantidad'], len(pool)))
    bonus = random.randint(1, loteria['bonus_max']) if loteria['bonus'] else None
    sources = [{"number": n, "source": "complement", "label": "Random", "explanation": "Generated randomly — no specific signal found"} for n in numeros]
    if bonus:
        sources.append({"number": bonus, "source": "complement", "label": "Random", "explanation": "Generated randomly"})
    return {"numbers": numeros, "bonus": bonus, "sources": sources}

def generar_aleatorio(loteria):
    return generar_fallback(loteria)

# ==========================================
# 9. EMAIL
# ==========================================
def enviar_email(to_email, subject, html):
    if not RESEND_API_KEY:
        return False
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={"from": "hello@lucksort.com", "to": [to_email], "subject": subject, "html": html},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def email_bienvenida(email):
    lang = st.session_state.get('idioma', 'EN')
    tr = T[lang]
    html = f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
    <div style="text-align:center;padding:30px 0 20px;">
        <div style="display:inline-flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#0a0a0f;">◆</div>
            <span style="font-size:22px;font-weight:700;color:white;">LuckSort</span>
        </div>
        <p style="color:rgba(255,255,255,0.3);font-size:12px;letter-spacing:2px;margin-top:6px;">SORT YOUR LUCK</p>
    </div>
    <hr style="border:none;border-top:1px solid rgba(201,168,76,0.2);margin:10px 0 24px;">
    <h2 style="color:white;">Welcome ◆</h2>
    <p style="color:rgba(255,255,255,0.6);line-height:1.7;">Your account is ready. Start generating combinations backed by real-world data.</p>
    <div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:20px 0;">
        <p style="color:#C9A84C;font-size:12px;letter-spacing:2px;margin-bottom:12px;">FREE PLAN INCLUDES</p>
        <ul style="color:rgba(255,255,255,0.6);line-height:2;margin:0;padding-left:18px;">
            <li>5 random combinations per lottery per day</li>
            <li>All 11 major lotteries — 3 languages</li>
            <li>Upgrade anytime for data convergence</li>
        </ul>
    </div>
    <div style="text-align:center;margin:28px 0;">
        <a href="{APP_URL}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;font-size:15px;">Open LuckSort →</a>
    </div>
    <p style="color:rgba(255,255,255,0.2);font-size:11px;font-style:italic;text-align:center;line-height:1.6;">"{tr['disclaimer']}"</p>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:20px 0;">
    <p style="text-align:center;color:rgba(255,255,255,0.18);font-size:10px;">© 2025 LuckSort · lucksort.com</p>
    </body></html>"""
    enviar_email(email, "Welcome to LuckSort ◆", html)

# ==========================================
# 10. ANIMATED BALLS COMPONENT
# ==========================================
def render_animated_balls():
    """Bolas animadas para la landing page"""
    st.markdown("""
    <div style="margin:32px 0 24px;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.2);letter-spacing:3px;text-align:center;margin-bottom:16px;">POWERBALL · LIVE PREVIEW</div>
        <div id="balls-container" style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:20px;">
            <div class="ball" id="b0">07</div>
            <div class="ball" id="b1">14</div>
            <div class="ball" id="b2">23</div>
            <div class="ball" id="b3">38</div>
            <div class="ball" id="b4">56</div>
            <div class="ball ball-gold" id="b5">12</div>
        </div>
        <div style="display:flex;flex-direction:column;gap:7px;max-width:400px;margin:0 auto;">
            <div class="src-row">
                <div class="src-left"><span class="src-icon">📊</span><div><div class="src-label">Draw History</div><div class="src-desc">Appeared 34× in March draws since 2010</div></div></div>
                <span class="src-num">→ 07</span>
            </div>
            <div class="src-row">
                <div class="src-left"><span class="src-icon">👥</span><div><div class="src-label">Community</div><div class="src-desc">Top picked number in r/powerball this week</div></div></div>
                <span class="src-num">→ 23</span>
            </div>
            <div class="src-row">
                <div class="src-left"><span class="src-icon">🌍</span><div><div class="src-label">World Events</div><div class="src-desc">Year 1938 in today's Wikipedia event</div></div></div>
                <span class="src-num">→ 38</span>
            </div>
            <div class="src-row">
                <div class="src-left"><span class="src-icon">✦</span><div><div class="src-label">Your Date</div><div class="src-desc">Day from your birthday — Mar 14</div></div></div>
                <span class="src-num">→ 14</span>
            </div>
        </div>
    </div>
    <script>
    const nums = [
        [7,14,23,38,56,12],[3,19,31,44,62,8],[11,22,35,47,68,17],
        [5,16,28,41,59,23],[9,21,33,46,63,4],[13,24,37,49,65,19],
    ];
    let idx = 0;
    function rotateBalls() {
        idx = (idx + 1) % nums.length;
        const set = nums[idx];
        for(let i=0;i<6;i++) {
            const el = document.getElementById('b'+i);
            if(el) {
                el.style.opacity='0';
                el.style.transform='scale(0.7)';
                setTimeout(()=>{
                    el.textContent = String(set[i]).padStart(2,'0');
                    el.style.opacity='1';
                    el.style.transform='scale(1)';
                }, 300 + i*50);
            }
        }
    }
    setInterval(rotateBalls, 2800);
    // Transition styles
    document.querySelectorAll('.ball').forEach(b=>{
        b.style.transition='opacity 0.3s ease, transform 0.3s ease';
    });
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# 11. MOSTRAR RESULTADO
# ==========================================
def mostrar_numeros(resultado, loteria):
    tr = t()
    numeros = resultado.get("numbers", [])
    bonus = resultado.get("bonus")
    sources = resultado.get("sources", [])

    # Balls HTML
    balls_html = '<div class="balls-wrap">'
    for n in numeros:
        balls_html += f'<div class="ball">{str(n).zfill(2)}</div>'
    if bonus:
        balls_html += f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    balls_html += '</div>'

    bonus_label = ""
    if bonus and loteria.get('bonus_name'):
        bonus_label = f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.25);text-align:center;margin-top:4px;">◆ {loteria["bonus_name"]}: {str(bonus).zfill(2)}</div>'

    st.markdown(f"""
    <div class="luck-card-gold" style="text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:4px;">
            {loteria['bandera']} {loteria['nombre']}
        </div>
        {balls_html}
        {bonus_label}
    </div>
    """, unsafe_allow_html=True)

    # Sources — narrativa rica
    if sources:
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.3);
        letter-spacing:2px;text-transform:uppercase;margin:18px 0 10px;">
            {tr['sources_title']}
        </div>
        """, unsafe_allow_html=True)

        for s in sources:
            src_type = s.get("source", "complement")
            icon = tr['src_icons'].get(src_type, "⚪")
            label = s.get("label") or tr['sources'].get(src_type, src_type)
            explanation = s.get("explanation", "")
            num = s.get("number", "")
            is_complement = src_type == "complement"
            extra_class = "src-complement" if is_complement else ""

            st.markdown(f"""
            <div class="src-row {extra_class}">
                <div class="src-left">
                    <span class="src-icon">{icon}</span>
                    <div>
                        <div class="src-label">{label}</div>
                        <div class="src-desc">{explanation}</div>
                    </div>
                </div>
                <span class="src-num">→ {str(num).zfill(2)}</span>
            </div>
            """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown(f'<div class="disclaimer">"{tr["disclaimer"]}"</div>', unsafe_allow_html=True)

def mostrar_paywall():
    tr = t()
    st.markdown(f"""
    <div class="luck-card" style="border-color:rgba(201,168,76,0.25);text-align:center;padding:28px;">
        <div style="font-size:24px;margin-bottom:10px;">◆</div>
        <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:20px;">
            {tr['paywall_title']}
        </h3>
        <p style="color:rgba(255,255,255,0.4);font-size:13px;max-width:340px;margin:0 auto 20px;line-height:1.65;">
            {tr['paywall_msg']}
        </p>
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;">
            <span style="font-size:11px;color:rgba(255,255,255,0.35);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:4px 10px;">📊 Draw History</span>
            <span style="font-size:11px;color:rgba(255,255,255,0.35);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:4px 10px;">👥 Community</span>
            <span style="font-size:11px;color:rgba(255,255,255,0.35);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:4px 10px;">🌍 World Events</span>
            <span style="font-size:11px;color:rgba(255,255,255,0.35);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:4px 10px;">✦ Your Dates</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(tr['upgrade_btn'], use_container_width=True, key="upgrade_btn"):
        pass

# ==========================================
# 12. SIDEBAR
# ==========================================
with st.sidebar:

    # LOGO
    st.markdown("""
    <div style="padding:24px 16px 16px;border-bottom:1px solid rgba(201,168,76,0.1);">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);
            border-radius:9px;display:flex;align-items:center;justify-content:center;
            flex-shrink:0;box-shadow:0 0 16px rgba(201,168,76,0.3);">
                <span style="font-size:16px;color:#0a0a0f;">◆</span>
            </div>
            <div>
                <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;
                color:white;letter-spacing:-0.5px;line-height:1;">LuckSort</div>
                <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.25);
                letter-spacing:2px;margin-top:2px;">SORT YOUR LUCK</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # LANGUAGE SELECTOR — discreto
    st.markdown('<div style="padding:12px 4px 4px;">', unsafe_allow_html=True)
    lang_options = {"EN 🇺🇸": "EN", "ES 🇪🇸": "ES", "PT 🇧🇷": "PT"}
    current_display = next(k for k, v in lang_options.items() if v == st.session_state['idioma'])
    selected = st.selectbox("", list(lang_options.keys()),
                           index=list(lang_options.keys()).index(current_display),
                           key="sb_lang", label_visibility="collapsed")
    if lang_options[selected] != st.session_state['idioma']:
        st.session_state['idioma'] = lang_options[selected]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        tr = t()
        tab_in, tab_up = st.tabs([tr['login'], tr['register']])

        with tab_in:
            em = st.text_input(tr['email'], key="si_email")
            pw = st.text_input(tr['password'], type="password", key="si_pass")
            if st.button(tr['btn_login'], use_container_width=True, key="btn_si"):
                if em == ADMIN_EMAIL and pw == ADMIN_PASS:
                    st.session_state.update({'logged_in': True, 'user_role': 'admin', 'user_email': em, 'user_id': None, 'vista': 'app'})
                    st.rerun()
                else:
                    ok, datos = login_usuario(em, pw)
                    if ok:
                        st.session_state.update({'logged_in': True, 'user_role': datos['role'], 'user_email': datos['email'], 'user_id': datos['id'], 'vista': 'app'})
                        resetear_uso_diario()
                        st.rerun()
                    else:
                        st.error(tr['login_err'])

        with tab_up:
            re = st.text_input(tr['email'], key="su_email")
            rp1 = st.text_input(tr['password'], type="password", key="su_p1")
            rp2 = st.text_input(tr['confirm_pass'], type="password", key="su_p2")
            if st.button(tr['btn_register'], use_container_width=True, key="btn_su"):
                if rp1 != rp2: st.error(tr['pass_mismatch'])
                elif len(rp1) < 6: st.warning(tr['pass_short'])
                elif "@" not in re: st.warning(tr['email_invalid'])
                else:
                    ok, res = registrar_usuario(re, rp1)
                    if ok:
                        st.session_state.update({'logged_in': True, 'user_role': 'free', 'user_email': re, 'user_id': res['id'], 'vista': 'app'})
                        email_bienvenida(re)
                        st.rerun()
                    elif res == "exists": st.error(tr['email_exists'])
                    else: st.error("⚠️ Error. Try again.")

    else:
        tr = t()
        resetear_uso_diario()

        # User info card
        role_display = tr['paid'] if st.session_state['user_role'] not in ['free', 'invitado'] else tr['free']
        role_color = "#C9A84C" if st.session_state['user_role'] != 'free' else "rgba(255,255,255,0.35)"
        st.markdown(f"""
        <div style="padding:12px 14px;background:rgba(201,168,76,0.05);
        border:1px solid rgba(201,168,76,0.15);border-radius:10px;margin-bottom:14px;">
            <div style="font-family:'DM Sans',sans-serif;font-size:12px;
            color:rgba(255,255,255,0.7);font-weight:500;margin-bottom:3px;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                {st.session_state['user_email']}
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
                <div style="width:6px;height:6px;border-radius:50%;background:{role_color};"></div>
                <span style="font-family:'DM Mono',monospace;font-size:9px;
                color:{role_color};letter-spacing:1.5px;">{role_display.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        if st.button(f"◆ {tr['tagline']}", use_container_width=True, key="nav_gen"):
            st.session_state['vista'] = 'app'
            st.rerun()
        if st.button(f"📋 {tr['history']}", use_container_width=True, key="nav_hist"):
            st.session_state['vista'] = 'history'
            st.rerun()

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        if st.button(tr['logout'], use_container_width=True, key="btn_lo"):
            for k in list(defaults.keys()):
                st.session_state[k] = defaults[k]
            st.rerun()

# ==========================================
# 13. LANDING PAGE
# ==========================================
if not st.session_state['logged_in']:
    tr = t()

    # Hero
    st.markdown(f"""
    <div style="text-align:center;padding:48px 16px 24px;">
        <div class="tag-gold" style="margin-bottom:20px;">
            <span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;
            display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>
            Data Convergence Engine
        </div>
        <h1 style="font-family:'Playfair Display',serif;
        font-size:clamp(38px,7vw,76px);font-weight:700;
        line-height:1.05;letter-spacing:-2px;margin-bottom:18px;">
            {tr['hero_1']}<br>
            <span class="shimmer">{tr['hero_2']}</span><br>
            {tr['hero_3']}
        </h1>
        <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);
        color:rgba(255,255,255,0.38);max-width:500px;margin:0 auto;line-height:1.8;">
            {tr['hero_sub']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Animated balls
    render_animated_balls()

    # CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(tr['cta_free'], use_container_width=True, key="land_cta"):
            st.session_state['mostrar_reg'] = True
            st.rerun()
        st.markdown("""
        <p style="text-align:center;font-family:'DM Mono',monospace;font-size:9px;
        color:rgba(255,255,255,0.18);letter-spacing:1.5px;margin-top:8px;">
        FREE · NO CREDIT CARD · ES / EN / PT
        </p>
        """, unsafe_allow_html=True)

    # Register/Login inline
    if st.session_state.get('mostrar_reg'):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:24px 0;">', unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1,2,1])
        with col_b:
            tab_r, tab_l = st.tabs([tr['register'], tr['login']])
            with tab_r:
                re = st.text_input(tr['email'], key="lr_e")
                rp = st.text_input(tr['password'], type="password", key="lr_p")
                rp2 = st.text_input(tr['confirm_pass'], type="password", key="lr_p2")
                if st.button(tr['btn_register'], use_container_width=True, key="lr_btn"):
                    if rp != rp2: st.error(tr['pass_mismatch'])
                    elif len(rp) < 6: st.warning(tr['pass_short'])
                    elif "@" not in re: st.warning(tr['email_invalid'])
                    else:
                        ok, res = registrar_usuario(re, rp)
                        if ok:
                            st.session_state.update({'logged_in': True, 'user_role': 'free', 'user_email': re, 'user_id': res['id'], 'vista': 'app', 'mostrar_reg': False})
                            email_bienvenida(re)
                            st.rerun()
                        elif res == "exists": st.error(tr['email_exists'])
                        else: st.error("⚠️ Error.")
            with tab_l:
                le = st.text_input(tr['email'], key="ll_e")
                lp = st.text_input(tr['password'], type="password", key="ll_p")
                if st.button(tr['btn_login'], use_container_width=True, key="ll_btn"):
                    if le == ADMIN_EMAIL and lp == ADMIN_PASS:
                        st.session_state.update({'logged_in': True, 'user_role': 'admin', 'user_email': le, 'user_id': None, 'vista': 'app'})
                        st.rerun()
                    else:
                        ok, datos = login_usuario(le, lp)
                        if ok:
                            st.session_state.update({'logged_in': True, 'user_role': datos['role'], 'user_email': datos['email'], 'user_id': datos['id'], 'vista': 'app'})
                            resetear_uso_diario()
                            st.rerun()
                        else:
                            st.error(tr['login_err'])

    # 4 Sources
    st.markdown(f"""
    <div style="text-align:center;padding:40px 0 20px;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.22);letter-spacing:3px;margin-bottom:12px;">HOW IT WORKS</div>
        <h2 style="font-family:'Playfair Display',serif;font-size:clamp(22px,3vw,40px);font-weight:700;letter-spacing:-1px;margin-bottom:6px;">Four signals. One combination.</h2>
        <div class="gold-line"></div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col, (icon, key, desc) in zip([c1,c2,c3,c4], [
        ("📊","historico","Years of official draws analyzed by date pattern"),
        ("👥","community","What real players are choosing right now"),
        ("🌍","eventos","Numbers hidden in today's headlines and history"),
        ("✦","fecha_personal","Your birthday, anniversary, life moments"),
    ]):
        with col:
            st.markdown(f"""
            <div class="luck-card" style="text-align:center;min-height:130px;">
                <div style="font-size:22px;margin-bottom:8px;">{icon}</div>
                <div style="font-family:'Playfair Display',serif;font-size:14px;font-weight:600;color:rgba(255,255,255,0.85);margin-bottom:5px;">{tr['sources'][key]}</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,0.32);line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Lotteries grid
    st.markdown("""
    <div style="padding:28px 0 14px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.2);letter-spacing:3px;">GLOBAL COVERAGE · 11 LOTTERIES</div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(4)
    for i, lot in enumerate(LOTERIAS):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="padding:10px 12px;background:rgba(255,255,255,0.025);
            border:1px solid rgba(255,255,255,0.06);border-radius:9px;
            display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:15px;">{lot['bandera']}</span>
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.6);">{lot['nombre']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:580px;margin:28px auto 0;">"{tr["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 14. APP — GENERADOR
# ==========================================
elif st.session_state.get('vista') == 'app':
    tr = t()
    es_free = st.session_state['user_role'] == 'free'
    es_paid = st.session_state['user_role'] in ['paid', 'pro', 'convergence', 'admin']

    st.markdown(f"""
    <div style="padding:20px 0 8px;">
        <span class="tag-gold">◆ {tr['tagline']}</span>
        <h2 style="font-family:'Playfair Display',serif;font-size:clamp(22px,3vw,38px);
        font-weight:700;letter-spacing:-1px;margin-top:10px;margin-bottom:4px;">
            {tr['select_lottery']}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Lottery selector
    lot_names = [f"{l['bandera']} {l['nombre']} ({l['pais']})" for l in LOTERIAS]
    sel_name = st.selectbox("", lot_names, label_visibility="collapsed", key="lot_sel")
    loteria = next(l for l in LOTERIAS if l['nombre'] in sel_name)

    # Counter
    gen_hoy = st.session_state['generaciones_hoy'].get(loteria['id'], 0)
    restantes = max(0, MAX_GEN - gen_hoy)
    st.markdown(f"""
    <div style="margin:8px 0 18px;">
        <span class="metric-pill">{tr['gen_left']}: {gen_hoy}/{MAX_GEN}</span>
    </div>
    """, unsafe_allow_html=True)

    # Personal inputs — plan pago
    inputs_usuario = {}
    if es_paid or st.session_state['user_role'] == 'admin':
        with st.expander(f"✦ {tr['personal_inputs']}", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                fecha_esp = st.text_input(tr['special_date'], placeholder="14/03/1990", key="fe")
                nombre = st.text_input(tr['your_name'], placeholder="Your name", key="nm")
            with c2:
                momento = st.text_input(tr['life_moment'], placeholder="I just had a baby...", key="mm")
                excluir = st.text_input(tr['exclude_numbers'], placeholder="4, 13, 17", key="ex")
            crowd_pref = st.radio(tr['follow_crowd'], [tr['balanced'], tr['follow'], tr['avoid']], horizontal=True, key="cp")
            crowd_map = {tr['follow']: "follow", tr['avoid']: "avoid", tr['balanced']: "balanced"}
            inputs_usuario = {
                "fecha_especial": fecha_esp,
                "nombre": nombre,
                "momento": momento,
                "excluir": excluir,
                "crowd": crowd_map.get(crowd_pref, "balanced"),
            }

    # Generate
    if restantes <= 0:
        st.warning(f"⚠️ {tr['gen_left']}: {MAX_GEN}/{MAX_GEN} — Come back tomorrow!")
    else:
        if st.button(f"◆ {tr['generate_btn']}", use_container_width=True, key="gen_btn"):
            with st.spinner(tr['generating']):
                if es_paid or st.session_state['user_role'] == 'admin':
                    resultado = generar_combinacion(loteria, inputs_usuario)
                else:
                    resultado = generar_aleatorio(loteria)
                st.session_state['ultima_generacion'] = resultado
                st.session_state['ultima_loteria'] = loteria
                st.session_state['generaciones_hoy'][loteria['id']] = gen_hoy + 1
                if st.session_state.get('user_id'):
                    guardar_generacion(st.session_state['user_id'], loteria['id'],
                        resultado.get('numbers', []), resultado.get('bonus'),
                        str(resultado.get('sources', [])), inputs_usuario)

    # Result
    if st.session_state.get('ultima_generacion') and st.session_state.get('ultima_loteria'):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:18px 0;">', unsafe_allow_html=True)
        mostrar_numeros(st.session_state['ultima_generacion'], st.session_state['ultima_loteria'])

    # Paywall
    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.04);margin:22px 0;">', unsafe_allow_html=True)
        mostrar_paywall()

# ==========================================
# 15. HISTORIAL
# ==========================================
elif st.session_state.get('vista') == 'history':
    tr = t()
    st.markdown(f"""
    <div style="padding:20px 0 14px;">
        <span class="tag-gold">◆ {tr['history']}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('user_id'):
        historial = obtener_historial(st.session_state['user_id'])
        if not historial:
            st.markdown(f'<p style="color:rgba(255,255,255,0.3);font-family:DM Sans,sans-serif;font-size:14px;">{tr["no_history"]}</p>', unsafe_allow_html=True)
        else:
            for h in historial:
                lot = next((l for l in LOTERIAS if l['id'] == h.get('loteria_id')), None)
                if lot:
                    nums_str = "  ".join([str(n).zfill(2) for n in h['numeros']])
                    bonus_str = f"  ◆ {str(h['bonus']).zfill(2)}" if h.get('bonus') else ""
                    fecha = h.get('created_at', '')[:10]
                    st.markdown(f"""
                    <div class="luck-card" style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <span style="font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;">{lot['bandera']} {lot['nombre']}</span>
                            <span style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.2);">{fecha}</span>
                        </div>
                        <div style="font-family:'DM Mono',monospace;font-size:20px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Sign in to see your history.")
