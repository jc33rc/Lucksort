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

# Session state
defaults = {
    'logged_in': False,
    'user_role': 'invitado',
    'user_email': '',
    'user_id': None,
    'idioma': 'EN',
    'fecha_uso': str(date.today()),
    'generaciones_hoy': {},  # {loteria_id: count}
    'ultima_generacion': None,
    'vista': 'landing',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 2. CSS — DARK GOLD THEME
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');

/* Base */
body, .stApp { background-color: #0a0a0f !important; color: white !important; }
.stApp { font-family: 'DM Sans', sans-serif !important; }

/* Hide streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f0f18 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #C9A84C, #F5D68A) !important;
    color: #0a0a0f !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 16px rgba(201,168,76,0.28) !important;
    transition: all 0.2s !important;
}
.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(201,168,76,0.38) !important;
}

/* Secondary buttons */
.btn-secondary>button {
    background: transparent !important;
    color: rgba(255,255,255,0.6) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    box-shadow: none !important;
}

/* Inputs */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>select {
    background-color: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color: rgba(201,168,76,0.5) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.1) !important;
}

/* Selectbox */
.stSelectbox>div>div {
    background-color: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: white !important;
}

/* Cards */
.luck-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.luck-card-gold {
    background: rgba(201,168,76,0.06);
    border: 1px solid rgba(201,168,76,0.25);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}

/* Number balls */
.number-ball {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px; height: 52px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    font-family: 'DM Mono', monospace;
    font-size: 16px; font-weight: 600;
    color: rgba(255,255,255,0.9);
    margin: 4px;
}
.number-ball-gold {
    background: linear-gradient(135deg, #C9A84C, #F5D68A);
    border: none;
    color: #0a0a0f;
    box-shadow: 0 0 20px rgba(201,168,76,0.4);
}

/* Tags */
.tag-gold {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(201,168,76,0.1);
    border: 1px solid rgba(201,168,76,0.25);
    border-radius: 20px; padding: 4px 12px;
    font-family: 'DM Mono', monospace;
    font-size: 10px; color: #C9A84C;
    letter-spacing: 2px; text-transform: uppercase;
}

/* Source row */
.source-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px; border-radius: 9px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
    font-family: 'DM Sans', sans-serif; font-size: 13px;
    color: rgba(255,255,255,0.4);
}
.source-number {
    font-family: 'DM Mono', monospace;
    font-size: 13px; color: #C9A84C; font-weight: 600;
}

/* Divider gold */
.gold-divider {
    width: 40px; height: 2px; margin: 12px 0;
    background: linear-gradient(90deg, transparent, #C9A84C, transparent);
}

/* Metric pill */
.metric-pill {
    display: inline-block;
    padding: 4px 12px; border-radius: 20px;
    background: rgba(201,168,76,0.1);
    border: 1px solid rgba(201,168,76,0.2);
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: #C9A84C;
}

/* Shimmer text */
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
.shimmer {
    background: linear-gradient(90deg, #C9A84C 0%, #F5D68A 35%, #C9A84C 65%, #F5D68A 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
}

/* Radio buttons */
.stRadio>div { flex-direction: row !important; gap: 12px !important; }
.stRadio>div>label {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; padding: 8px 16px !important;
    cursor: pointer !important; color: rgba(255,255,255,0.6) !important;
}

/* Disclaimer box */
.disclaimer {
    background: rgba(201,168,76,0.05);
    border: 1px solid rgba(201,168,76,0.15);
    border-radius: 10px; padding: 14px 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px; color: rgba(255,255,255,0.35);
    line-height: 1.65; font-style: italic;
    margin-top: 16px;
}

/* Grid bg */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.018) 1px, transparent 1px);
    background-size: 50px 50px;
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
    st.error("⚠️ Configura tus variables en st.secrets")
    st.stop()

client_groq = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
APP_URL = "https://lucksort.streamlit.app"

# ==========================================
# 4. LOTERÍAS
# ==========================================
LOTERIAS = [
    {"id": 1, "nombre": "Powerball",      "pais": "USA",    "bandera": "🇺🇸", "min": 1, "max": 69, "cantidad": 5, "bonus": True,  "bonus_max": 26},
    {"id": 2, "nombre": "Mega Millions",  "pais": "USA",    "bandera": "🇺🇸", "min": 1, "max": 70, "cantidad": 5, "bonus": True,  "bonus_max": 25},
    {"id": 3, "nombre": "EuroMillions",   "pais": "Europa", "bandera": "🇪🇺", "min": 1, "max": 50, "cantidad": 5, "bonus": True,  "bonus_max": 12},
    {"id": 4, "nombre": "UK Lotto",       "pais": "UK",     "bandera": "🇬🇧", "min": 1, "max": 59, "cantidad": 6, "bonus": False, "bonus_max": None},
    {"id": 5, "nombre": "El Gordo",       "pais": "España", "bandera": "🇪🇸", "min": 1, "max": 54, "cantidad": 5, "bonus": True,  "bonus_max": 10},
    {"id": 6, "nombre": "Mega-Sena",      "pais": "Brasil", "bandera": "🇧🇷", "min": 1, "max": 60, "cantidad": 6, "bonus": False, "bonus_max": None},
    {"id": 7, "nombre": "Baloto",         "pais": "Colombia","bandera":"🇨🇴", "min": 1, "max": 43, "cantidad": 6, "bonus": True,  "bonus_max": 16},
    {"id": 8, "nombre": "La Primitiva",   "pais": "España", "bandera": "🇪🇸", "min": 1, "max": 49, "cantidad": 6, "bonus": False, "bonus_max": None},
]

MAX_GENERACIONES_FREE = 5
MAX_GENERACIONES_PAID = 5

# ==========================================
# 5. TRADUCCIONES
# ==========================================
T = {
    "EN": {
        "tagline": "Sort Your Luck",
        "sub": "Data-driven lottery combinations powered by real-world signals.",
        "hero_1": "Your numbers,",
        "hero_2": "backed by the",
        "hero_3": "world's signals.",
        "hero_sub": "We gather real data — historical draws, today's news, community picks, and your personal dates — converged into combinations that mean something.",
        "cta": "Generate My Numbers",
        "cta_free": "Start Free",
        "login": "Sign In",
        "register": "Create Account",
        "logout": "Sign Out",
        "email": "Email",
        "password": "Password",
        "confirm_pass": "Confirm Password",
        "btn_login": "Sign In",
        "btn_register": "Create Free Account",
        "plan": "Plan",
        "free": "Free",
        "paid": "Convergence",
        "select_lottery": "Select Lottery",
        "personal_inputs": "Tell us about you (optional)",
        "special_date": "Special date (birthday, anniversary...)",
        "your_name": "Your name",
        "life_moment": "Something happening in your life right now",
        "exclude_numbers": "Numbers to exclude (comma separated)",
        "follow_crowd": "Crowd preference",
        "follow": "Follow the crowd",
        "avoid": "Avoid the crowd",
        "balanced": "Balanced",
        "generate_btn": "Generate Combination",
        "generating": "Converging data sources...",
        "your_combo": "Your Combination",
        "sources_title": "Where each number comes from",
        "gen_left": "Generations today",
        "disclaimer": "We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
        "paywall_msg": "Upgrade to Convergence plan to unlock data-driven generation.",
        "upgrade_btn": "Upgrade — $9.99/month",
        "history": "My History",
        "no_history": "No combinations generated yet.",
        "login_err": "❌ Incorrect credentials.",
        "pass_mismatch": "⚠️ Passwords don't match.",
        "pass_short": "⚠️ Minimum 6 characters.",
        "email_invalid": "⚠️ Invalid email.",
        "email_exists": "⚠️ Email already registered.",
        "welcome": "Welcome to LuckSort",
        "sources": {
            "historico": "Draw History",
            "community": "Community",
            "eventos": "World Events",
            "fecha_personal": "Your Date",
            "aleatorio": "Random",
        }
    },
    "ES": {
        "tagline": "Ordena tu Suerte",
        "sub": "Combinaciones de lotería basadas en datos reales del mundo.",
        "hero_1": "Tus números,",
        "hero_2": "respaldados por",
        "hero_3": "las señales del mundo.",
        "hero_sub": "Recopilamos datos reales — sorteos históricos, noticias de hoy, picks de la comunidad y tus fechas personales — convergidos en combinaciones con significado.",
        "cta": "Generar Mis Números",
        "cta_free": "Empezar Gratis",
        "login": "Entrar",
        "register": "Crear Cuenta",
        "logout": "Cerrar Sesión",
        "email": "Correo electrónico",
        "password": "Contraseña",
        "confirm_pass": "Confirmar Contraseña",
        "btn_login": "Entrar",
        "btn_register": "Crear Cuenta Gratis",
        "plan": "Plan",
        "free": "Gratis",
        "paid": "Convergencia",
        "select_lottery": "Selecciona tu Lotería",
        "personal_inputs": "Cuéntanos sobre ti (opcional)",
        "special_date": "Fecha especial (cumpleaños, aniversario...)",
        "your_name": "Tu nombre",
        "life_moment": "Algo que está pasando en tu vida ahora",
        "exclude_numbers": "Números a excluir (separados por coma)",
        "follow_crowd": "Preferencia de comunidad",
        "follow": "Seguir la masa",
        "avoid": "Ir contra la masa",
        "balanced": "Balanceado",
        "generate_btn": "Generar Combinación",
        "generating": "Convergiendo fuentes de datos...",
        "your_combo": "Tu Combinación",
        "sources_title": "De dónde viene cada número",
        "gen_left": "Generaciones hoy",
        "disclaimer": "Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
        "paywall_msg": "Actualiza al plan Convergencia para desbloquear la generación basada en datos.",
        "upgrade_btn": "Actualizar — $9.99/mes",
        "history": "Mi Historial",
        "no_history": "Aún no has generado combinaciones.",
        "login_err": "❌ Credenciales incorrectas.",
        "pass_mismatch": "⚠️ Las contraseñas no coinciden.",
        "pass_short": "⚠️ Mínimo 6 caracteres.",
        "email_invalid": "⚠️ Email inválido.",
        "email_exists": "⚠️ El correo ya está registrado.",
        "welcome": "Bienvenido a LuckSort",
        "sources": {
            "historico": "Histórico",
            "community": "Comunidad",
            "eventos": "Eventos",
            "fecha_personal": "Tu Fecha",
            "aleatorio": "Aleatorio",
        }
    },
    "PT": {
        "tagline": "Organize sua Sorte",
        "sub": "Combinações de loteria baseadas em dados reais do mundo.",
        "hero_1": "Seus números,",
        "hero_2": "respaldados pelos",
        "hero_3": "sinais do mundo.",
        "hero_sub": "Coletamos dados reais — histórico de sorteios, notícias de hoje, picks da comunidade e suas datas pessoais — convergidos em combinações com significado.",
        "cta": "Gerar Meus Números",
        "cta_free": "Começar Grátis",
        "login": "Entrar",
        "register": "Criar Conta",
        "logout": "Sair",
        "email": "Email",
        "password": "Senha",
        "confirm_pass": "Confirmar Senha",
        "btn_login": "Entrar",
        "btn_register": "Criar Conta Grátis",
        "plan": "Plano",
        "free": "Grátis",
        "paid": "Convergência",
        "select_lottery": "Selecione sua Loteria",
        "personal_inputs": "Nos conte sobre você (opcional)",
        "special_date": "Data especial (aniversário, data especial...)",
        "your_name": "Seu nome",
        "life_moment": "Algo acontecendo na sua vida agora",
        "exclude_numbers": "Números a excluir (separados por vírgula)",
        "follow_crowd": "Preferência da comunidade",
        "follow": "Seguir a massa",
        "avoid": "Ir contra a massa",
        "balanced": "Balanceado",
        "generate_btn": "Gerar Combinação",
        "generating": "Convergindo fontes de dados...",
        "your_combo": "Sua Combinação",
        "sources_title": "De onde vem cada número",
        "gen_left": "Gerações hoje",
        "disclaimer": "Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
        "paywall_msg": "Atualize para o plano Convergência para desbloquear a geração baseada em dados.",
        "upgrade_btn": "Atualizar — $9.99/mês",
        "history": "Meu Histórico",
        "no_history": "Ainda não gerou combinações.",
        "login_err": "❌ Credenciais incorretas.",
        "pass_mismatch": "⚠️ As senhas não coincidem.",
        "pass_short": "⚠️ Mínimo 6 caracteres.",
        "email_invalid": "⚠️ Email inválido.",
        "email_exists": "⚠️ Email já cadastrado.",
        "welcome": "Bem-vindo ao LuckSort",
        "sources": {
            "historico": "Histórico",
            "community": "Comunidade",
            "eventos": "Eventos",
            "fecha_personal": "Sua Data",
            "aleatorio": "Aleatório",
        }
    }
}

def t():
    return T[st.session_state['idioma']]

# ==========================================
# 6. FUNCIONES SUPABASE
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
            "user_id": user_id,
            "loteria_id": loteria_id,
            "numeros": numeros,
            "bonus": bonus,
            "narrativa": narrativa,
            "inputs_usuario": json.dumps(inputs),
        }).execute()
    except:
        pass

def obtener_historial(user_id, limit=10):
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
# 7. FUNCIONES DE DATOS (CACHÉ DIARIO)
# ==========================================
def obtener_cache(tipo):
    try:
        hoy = str(date.today())
        res = supabase.table("cache_diario").select("*").eq("fecha", hoy).eq("tipo", tipo).execute()
        return res.data[0]['contenido'] if res.data else None
    except:
        return None

def guardar_cache(tipo, contenido, fuente=""):
    try:
        hoy = str(date.today())
        existing = supabase.table("cache_diario").select("id").eq("fecha", hoy).eq("tipo", tipo).execute()
        if existing.data:
            supabase.table("cache_diario").update({"contenido": contenido}).eq("id", existing.data[0]['id']).execute()
        else:
            supabase.table("cache_diario").insert({
                "fecha": hoy, "tipo": tipo,
                "contenido": contenido, "fuente": fuente
            }).execute()
    except:
        pass

def obtener_efemerides():
    cache = obtener_cache("efemerides")
    if cache:
        return cache
    try:
        hoy = datetime.now()
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{hoy.month}/{hoy.day}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            eventos = data.get("events", [])[:5]
            resultado = [{"year": e.get("year"), "text": e.get("text", "")[:120]} for e in eventos]
            guardar_cache("efemerides", resultado, "wikipedia")
            return resultado
    except:
        pass
    return []

def obtener_noticias():
    cache = obtener_cache("noticias")
    if cache:
        return cache
    try:
        if NEWS_API_KEY:
            url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                arts = data.get("articles", [])[:5]
                resultado = [{"title": a.get("title", "")[:100]} for a in arts]
                guardar_cache("noticias", resultado, "newsapi")
                return resultado
    except:
        pass
    return []

def obtener_crowd():
    cache = obtener_cache("crowd")
    if cache:
        return cache
    # Números más mencionados en comunidades (simulado hasta integrar Reddit API)
    crowd_numeros = random.sample(range(1, 70), 10)
    guardar_cache("crowd", crowd_numeros, "community")
    return crowd_numeros

# ==========================================
# 8. GENERACIÓN CON GROQ
# ==========================================
def generar_combinacion(loteria, inputs_usuario):
    lang = st.session_state['idioma']
    lang_map = {"EN": "English", "ES": "Spanish", "PT": "Portuguese"}
    lang_full = lang_map[lang]

    efemerides = obtener_efemerides()
    noticias = obtener_noticias()
    crowd = obtener_crowd()

    excluir = []
    if inputs_usuario.get("excluir"):
        try:
            excluir = [int(x.strip()) for x in inputs_usuario["excluir"].split(",") if x.strip().isdigit()]
        except:
            pass

    prompt = f"""You are LuckSort's data convergence engine. Generate a lottery combination for {loteria['nombre']}.

LOTTERY RULES:
- Pick {loteria['cantidad']} numbers between {loteria['min']} and {loteria['max']}
- {"Pick 1 bonus number between 1 and " + str(loteria['bonus_max']) if loteria['bonus'] else "No bonus number"}
- Exclude these numbers: {excluir if excluir else "none"}

REAL DATA SOURCES (use these to justify each number):
1. TODAY'S HISTORICAL EVENTS (Wikipedia): {json.dumps(efemerides[:3])}
2. TODAY'S NEWS: {json.dumps(noticias[:3])}
3. COMMUNITY POPULAR NUMBERS: {crowd[:8]}
4. USER PERSONAL DATA: {json.dumps(inputs_usuario)}

CROWD PREFERENCE: {inputs_usuario.get('crowd', 'balanced')}
- "follow": use numbers from community list
- "avoid": avoid community numbers  
- "balanced": mix

YOUR TASK:
Generate exactly {loteria['cantidad']} unique numbers + {"1 bonus" if loteria['bonus'] else "no bonus"}.
Each number MUST have a real source from the data above.

Respond ONLY in {lang_full} with this exact JSON format:
{{
  "numbers": [n1, n2, n3, n4, n5],
  "bonus": {12 if loteria['bonus'] else "null"},
  "sources": {{
    "n1": {{"number": n1, "source": "historico|community|eventos|fecha_personal|aleatorio", "explanation": "brief real reason in {lang_full}"}},
    "n2": {{"number": n2, "source": "...", "explanation": "..."}},
    "n3": {{"number": n3, "source": "...", "explanation": "..."}},
    "n4": {{"number": n4, "source": "...", "explanation": "..."}},
    "n5": {{"number": n5, "source": "...", "explanation": "..."}},
    {"\"bonus\": {\"number\": 12, \"source\": \"...\", \"explanation\": \"...\"}" if loteria['bonus'] else ""}
  }}
}}

CRITICAL: Return ONLY valid JSON. No extra text. All numbers must be within valid range and unique."""

    try:
        response = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are LuckSort data engine. Respond only in {lang_full}. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        raw = response.choices[0].message.content.strip()
        # Clean JSON
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        resultado = json.loads(raw)
        return resultado
    except Exception as e:
        # Fallback: generación aleatoria con fuentes básicas
        numeros = random.sample(range(loteria['min'], loteria['max'] + 1), loteria['cantidad'])
        bonus = random.randint(1, loteria['bonus_max']) if loteria['bonus'] else None
        sources = {}
        for i, n in enumerate(numeros):
            sources[f"n{i+1}"] = {"number": n, "source": "aleatorio", "explanation": "Generated randomly"}
        if bonus:
            sources["bonus"] = {"number": bonus, "source": "aleatorio", "explanation": "Generated randomly"}
        return {"numbers": numeros, "bonus": bonus, "sources": sources}

def generar_combinacion_aleatoria(loteria):
    numeros = random.sample(range(loteria['min'], loteria['max'] + 1), loteria['cantidad'])
    bonus = random.randint(1, loteria['bonus_max']) if loteria['bonus'] else None
    return {"numbers": numeros, "bonus": bonus, "sources": {}}

# ==========================================
# 9. FUNCIONES EMAIL
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
    html = f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:600px;margin:0 auto;">
    <h1 style="color:#C9A84C;text-align:center;">◆ LuckSort</h1>
    <p style="text-align:center;color:#888;">Sort Your Luck</p>
    <hr style="border:none;border-top:1px solid rgba(201,168,76,0.2);margin:20px 0;">
    <h2>Welcome! 🎯</h2>
    <p style="color:#ccc;">Your account is ready. Start generating combinations backed by real data.</p>
    <div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:20px 0;">
        <h3 style="color:#C9A84C;">Free plan includes:</h3>
        <ul style="color:#ccc;line-height:2;">
            <li>✅ 5 random combinations per lottery per day</li>
            <li>✅ All major lotteries</li>
            <li>✅ Access to all 3 languages</li>
        </ul>
    </div>
    <div style="text-align:center;margin:30px 0;">
        <a href="{APP_URL}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:bold;border-radius:10px;text-decoration:none;">Open LuckSort →</a>
    </div>
    <p style="text-align:center;color:rgba(255,255,255,0.25);font-size:11px;font-style:italic;">"{T['EN']['disclaimer']}"</p>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:20px 0;">
    <p style="text-align:center;color:#444;font-size:11px;">© 2025 LuckSort · lucksort.com</p>
    </body></html>"""
    enviar_email(email, "Welcome to LuckSort ◆", html)

# ==========================================
# 10. UI COMPONENTS
# ==========================================
def mostrar_numeros(resultado, loteria):
    tr = t()
    numeros = resultado.get("numbers", [])
    bonus = resultado.get("bonus")
    sources = resultado.get("sources", {})

    # Balls
    balls_html = ""
    for n in numeros:
        balls_html += f'<div class="number-ball">{str(n).zfill(2)}</div>'
    if bonus:
        balls_html += f'<div class="number-ball number-ball-gold">{str(bonus).zfill(2)}</div>'

    st.markdown(f"""
    <div class="luck-card-gold" style="text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
            {loteria['bandera']} {loteria['nombre']}
        </div>
        <div style="margin:16px 0;">{balls_html}</div>
        {f'<div style="font-family:DM Sans,sans-serif;font-size:11px;color:rgba(255,255,255,0.3);margin-top:6px;">◆ Bonus: {str(bonus).zfill(2)}</div>' if bonus else ""}
    </div>
    """, unsafe_allow_html=True)

    # Sources
    if sources:
        st.markdown(f"""
        <div style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.4);
        letter-spacing:1px;text-transform:uppercase;margin:16px 0 8px;">
            {tr['sources_title']}
        </div>
        """, unsafe_allow_html=True)

        source_icons = {
            "historico": "📊",
            "community": "👥",
            "eventos": "🌍",
            "fecha_personal": "✦",
            "aleatorio": "🎲",
        }

        all_sources = list(sources.values())
        for s in all_sources:
            icon = source_icons.get(s.get("source", "aleatorio"), "🎲")
            source_label = tr['sources'].get(s.get("source", "aleatorio"), s.get("source", ""))
            explanation = s.get("explanation", "")
            num = s.get("number", "")
            st.markdown(f"""
            <div class="source-row">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:14px;">{icon}</span>
                    <div>
                        <div style="color:rgba(255,255,255,0.6);font-size:12px;">{source_label}</div>
                        <div style="color:rgba(255,255,255,0.3);font-size:11px;">{explanation}</div>
                    </div>
                </div>
                <span class="source-number">→ {str(num).zfill(2)}</span>
            </div>
            """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown(f'<div class="disclaimer">"{tr["disclaimer"]}"</div>', unsafe_allow_html=True)

def mostrar_paywall():
    tr = t()
    st.markdown(f"""
    <div class="luck-card" style="text-align:center;border-color:rgba(201,168,76,0.3);">
        <div style="font-size:28px;margin-bottom:12px;">◆</div>
        <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;">
            {tr['paid']}
        </h3>
        <p style="color:rgba(255,255,255,0.4);font-size:14px;margin-bottom:20px;">
            {tr['paywall_msg']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(tr['upgrade_btn'], use_container_width=True):
        pass  # Stripe link aquí

# ==========================================
# 11. SIDEBAR
# ==========================================
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px;">
        <div style="display:inline-flex;align-items:center;gap:8px;">
            <div style="width:28px;height:28px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:8px;display:flex;align-items:center;justify-content:center;">
                <span style="color:#0a0a0f;font-size:14px;">◆</span>
            </div>
            <span style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:white;">LuckSort</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Language selector
    lang_sel = st.selectbox("", ["EN 🇺🇸", "ES 🇪🇸", "PT 🇧🇷"], key="lang_sel",
                            label_visibility="collapsed")
    nuevo_lang = lang_sel.split(" ")[0]
    if nuevo_lang != st.session_state['idioma']:
        st.session_state['idioma'] = nuevo_lang
        st.rerun()

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:10px 0;">', unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        tr = t()
        tab_login, tab_reg = st.tabs([tr['login'], tr['register']])

        with tab_login:
            email_in = st.text_input(tr['email'], key="sb_email")
            pass_in = st.text_input(tr['password'], type="password", key="sb_pass")
            if st.button(tr['btn_login'], use_container_width=True, key="btn_sb_login"):
                if email_in == ADMIN_EMAIL and pass_in == ADMIN_PASS:
                    st.session_state.update({'logged_in': True, 'user_role': 'admin', 'user_email': email_in, 'user_id': None, 'vista': 'app'})
                    st.rerun()
                else:
                    ok, datos = login_usuario(email_in, pass_in)
                    if ok:
                        st.session_state.update({
                            'logged_in': True, 'user_role': datos['role'],
                            'user_email': datos['email'], 'user_id': datos['id'],
                            'vista': 'app'
                        })
                        resetear_uso_diario()
                        st.rerun()
                    else:
                        st.error(tr['login_err'])

        with tab_reg:
            r_email = st.text_input(tr['email'], key="r_email")
            r_pass = st.text_input(tr['password'], type="password", key="r_pass")
            r_pass2 = st.text_input(tr['confirm_pass'], type="password", key="r_pass2")
            if st.button(tr['btn_register'], use_container_width=True, key="btn_reg"):
                if r_pass != r_pass2:
                    st.error(tr['pass_mismatch'])
                elif len(r_pass) < 6:
                    st.warning(tr['pass_short'])
                elif "@" not in r_email:
                    st.warning(tr['email_invalid'])
                else:
                    ok, res = registrar_usuario(r_email, r_pass)
                    if ok:
                        st.session_state.update({
                            'logged_in': True, 'user_role': 'free',
                            'user_email': r_email, 'user_id': res['id'],
                            'vista': 'app'
                        })
                        email_bienvenida(r_email)
                        st.rerun()
                    elif res == "exists":
                        st.error(tr['email_exists'])
                    else:
                        st.error("⚠️ Error. Please try again.")

    else:
        tr = t()
        resetear_uso_diario()

        st.markdown(f"""
        <div style="padding:12px;background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.2);border-radius:10px;margin-bottom:12px;">
            <div style="font-family:'DM Sans',sans-serif;font-size:12px;color:#C9A84C;font-weight:600;">
                {st.session_state['user_email']}
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:1px;margin-top:3px;">
                {tr['plan'].upper()}: {(tr['paid'] if st.session_state['user_role'] != 'free' else tr['free']).upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Nav
        if st.button("◆ Generate", use_container_width=True, key="nav_gen"):
            st.session_state['vista'] = 'app'
            st.rerun()
        if st.button(f"📋 {tr['history']}", use_container_width=True, key="nav_hist"):
            st.session_state['vista'] = 'history'
            st.rerun()

        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:10px 0;">', unsafe_allow_html=True)

        if st.button(tr['logout'], use_container_width=True, key="btn_logout"):
            for k in ['logged_in', 'user_role', 'user_email', 'user_id', 'generaciones_hoy', 'ultima_generacion']:
                st.session_state[k] = defaults.get(k, None)
            st.session_state['vista'] = 'landing'
            st.rerun()

# ==========================================
# 12. LANDING PAGE
# ==========================================
if not st.session_state['logged_in']:
    tr = t()

    st.markdown(f"""
    <div style="text-align:center;padding:60px 20px 40px;position:relative;">
        <div class="tag-gold" style="margin-bottom:24px;">
            <span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>
            LuckSort · Data Convergence
        </div>
        <h1 style="font-family:'Playfair Display',serif;font-size:clamp(36px,6vw,72px);font-weight:700;line-height:1.06;letter-spacing:-2px;margin-bottom:20px;">
            {tr['hero_1']}<br>
            <span class="shimmer">{tr['hero_2']}</span><br>
            {tr['hero_3']}
        </h1>
        <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);color:rgba(255,255,255,0.4);max-width:540px;margin:0 auto 32px;line-height:1.75;">
            {tr['hero_sub']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(tr['cta_free'], use_container_width=True, key="landing_cta"):
            st.session_state['mostrar_reg'] = True
            st.rerun()
        st.markdown("""
        <p style="text-align:center;font-family:'DM Mono',monospace;font-size:9px;
        color:rgba(255,255,255,0.2);letter-spacing:1.5px;margin-top:8px;">
        FREE · NO CREDIT CARD · ES / EN / PT
        </p>
        """, unsafe_allow_html=True)

    # Sources section
    st.markdown(f"""
    <div style="padding:40px 0 20px;text-align:center;">
        <h2 style="font-family:'Playfair Display',serif;font-size:clamp(22px,3vw,36px);font-weight:700;letter-spacing:-1px;margin-bottom:8px;">
            {tr['sources_title'] if 'sources_title' in tr else 'Four signals. One combination.'}
        </h2>
        <div class="gold-divider" style="margin:12px auto;"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    sources_data = [
        ("📊", tr['sources']['historico'], "Years of draw data cross-referenced by date"),
        ("👥", tr['sources']['community'], "What players are choosing today"),
        ("🌍", tr['sources']['eventos'], "Numbers from today's headlines"),
        ("✦", tr['sources']['fecha_personal'], "Your birthdays and special dates"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], sources_data):
        with col:
            st.markdown(f"""
            <div class="luck-card" style="text-align:center;height:140px;">
                <div style="font-size:24px;margin-bottom:8px;">{icon}</div>
                <div style="font-family:'Playfair Display',serif;font-size:14px;font-weight:600;color:rgba(255,255,255,0.88);margin-bottom:6px;">{title}</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,0.35);line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Lotteries
    st.markdown("""
    <div style="padding:30px 0 16px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.25);letter-spacing:3px;">GLOBAL COVERAGE</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, lot in enumerate(LOTERIAS):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="padding:10px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:9px;display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:16px;">{lot['bandera']}</span>
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.65);">{lot['nombre']}</span>
            </div>
            """, unsafe_allow_html=True)

    # Disclaimer footer
    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:600px;margin:30px auto 0;">"{tr["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 13. APP PRINCIPAL — GENERADOR
# ==========================================
elif st.session_state.get('vista') == 'app':
    tr = t()
    es_free = st.session_state['user_role'] == 'free'
    es_paid = st.session_state['user_role'] in ['paid', 'pro', 'admin']

    st.markdown(f"""
    <div style="padding:20px 0 10px;">
        <div class="tag-gold">◆ {tr['tagline']}</div>
        <h2 style="font-family:'Playfair Display',serif;font-size:clamp(24px,3vw,40px);
        font-weight:700;letter-spacing:-1px;margin-top:12px;">
            {tr['select_lottery']}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Lottery selector
    lot_names = [f"{l['bandera']} {l['nombre']}" for l in LOTERIAS]
    lot_sel_name = st.selectbox("", lot_names, label_visibility="collapsed", key="lot_sel")
    loteria = next(l for l in LOTERIAS if l['nombre'] in lot_sel_name)

    # Generaciones counter
    gen_hoy = st.session_state['generaciones_hoy'].get(loteria['id'], 0)
    max_gen = MAX_GENERACIONES_PAID if es_paid else MAX_GENERACIONES_FREE
    restantes = max(0, max_gen - gen_hoy)

    st.markdown(f"""
    <div style="margin:8px 0 20px;">
        <span class="metric-pill">{tr['gen_left']}: {restantes}/{max_gen}</span>
    </div>
    """, unsafe_allow_html=True)

    # Personal inputs — solo plan pago
    if es_paid or st.session_state['user_role'] == 'admin':
        with st.expander(f"✦ {tr['personal_inputs']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                fecha_especial = st.text_input(tr['special_date'], placeholder="14/03/1990", key="fecha_esp")
                nombre = st.text_input(tr['your_name'], placeholder="Your name", key="inp_nombre")
            with col2:
                momento = st.text_input(tr['life_moment'], placeholder="I just had a baby...", key="inp_momento")
                excluir = st.text_input(tr['exclude_numbers'], placeholder="13, 4, 17", key="inp_excluir")

            crowd_pref = st.radio(
                tr['follow_crowd'],
                [tr['balanced'], tr['follow'], tr['avoid']],
                horizontal=True, key="crowd_pref"
            )
            crowd_map = {tr['follow']: "follow", tr['avoid']: "avoid", tr['balanced']: "balanced"}
            crowd_val = crowd_map.get(crowd_pref, "balanced")

        inputs_usuario = {
            "fecha_especial": fecha_especial if 'fecha_especial' in dir() else "",
            "nombre": nombre if 'nombre' in dir() else "",
            "momento": momento if 'momento' in dir() else "",
            "excluir": excluir if 'excluir' in dir() else "",
            "crowd": crowd_val if 'crowd_val' in dir() else "balanced",
        }
    else:
        inputs_usuario = {}

    # Generate button
    if restantes <= 0:
        st.warning(f"⚠️ {tr['gen_left']}: 0/{max_gen}")
    else:
        if st.button(f"◆ {tr['generate_btn']}", use_container_width=True, key="btn_gen"):
            with st.spinner(tr['generating']):
                if es_paid or st.session_state['user_role'] == 'admin':
                    resultado = generar_combinacion(loteria, inputs_usuario)
                else:
                    resultado = generar_combinacion_aleatoria(loteria)

                st.session_state['ultima_generacion'] = resultado
                st.session_state['ultima_loteria'] = loteria

                # Actualizar contador
                gen_count = st.session_state['generaciones_hoy'].get(loteria['id'], 0)
                st.session_state['generaciones_hoy'][loteria['id']] = gen_count + 1

                # Guardar en DB
                if st.session_state.get('user_id'):
                    guardar_generacion(
                        st.session_state['user_id'],
                        loteria['id'],
                        resultado.get('numbers', []),
                        resultado.get('bonus'),
                        str(resultado.get('sources', {})),
                        inputs_usuario
                    )

    # Mostrar resultado
    if st.session_state.get('ultima_generacion') and st.session_state.get('ultima_loteria'):
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        mostrar_numeros(
            st.session_state['ultima_generacion'],
            st.session_state['ultima_loteria']
        )

    # Paywall para free
    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:24px 0;">', unsafe_allow_html=True)
        mostrar_paywall()

# ==========================================
# 14. HISTORIAL
# ==========================================
elif st.session_state.get('vista') == 'history':
    tr = t()
    st.markdown(f"""
    <div style="padding:20px 0 16px;">
        <div class="tag-gold">◆ {tr['history']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('user_id'):
        historial = obtener_historial(st.session_state['user_id'])
        if not historial:
            st.markdown(f'<p style="color:rgba(255,255,255,0.35);font-family:DM Sans,sans-serif;">{tr["no_history"]}</p>', unsafe_allow_html=True)
        else:
            for h in historial:
                loteria_hist = next((l for l in LOTERIAS if l['id'] == h['loteria_id']), None)
                if loteria_hist:
                    numeros_str = " · ".join([str(n).zfill(2) for n in h['numeros']])
                    bonus_str = f" ◆ {str(h['bonus']).zfill(2)}" if h.get('bonus') else ""
                    fecha = h['created_at'][:10] if h.get('created_at') else ""
                    st.markdown(f"""
                    <div class="luck-card" style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div style="font-family:'DM Mono',monospace;font-size:12px;color:#C9A84C;">
                                {loteria_hist['bandera']} {loteria_hist['nombre']}
                            </div>
                            <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.25);">
                                {fecha}
                            </div>
                        </div>
                        <div style="font-family:'DM Mono',monospace;font-size:18px;color:white;margin-top:10px;letter-spacing:2px;">
                            {numeros_str}{bonus_str}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Login to see your history.")
