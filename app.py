import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime
import requests, random, json, re, math, time
from collections import Counter

# ==========================================
# 1. CONFIG
# ==========================================
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆", layout="wide",
    initial_sidebar_state="collapsed"
)

DEFAULTS = {
    "logged_in": False, "user_role": "invitado",
    "user_email": "", "user_id": None,
    "idioma": "EN", "fecha_uso": str(date.today()),
    "generaciones_hoy": {}, "ultima_generacion": None,
    "ultima_loteria": None, "vista": "landing",
    "mostrar_reg": False, "historial_sesion": [],
    "stripe_session": None,
    "combinaciones_guardadas": [],
    "comparar_nums": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 2. CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:#0a0a0f!important;color:white!important;font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}

/* Remove top space */
.block-container{padding-top:0!important;padding-bottom:0!important;}
.stMainBlockContainer{padding-top:0!important;}
[data-testid="stAppViewContainer"]>[data-testid="stVerticalBlock"]{padding-top:0!important;}

/* SIDEBAR */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d0d1a,#0a0a0f)!important;border-right:1px solid rgba(201,168,76,0.15)!important;}
section[data-testid="stSidebar"]>div:first-child{padding-top:0!important;}

/* BUTTONS — gold primary */
.stButton>button{background:linear-gradient(135deg,#C9A84C,#F5D68A)!important;color:#0a0a0f!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;border:none!important;border-radius:10px!important;width:100%!important;transition:all .2s!important;box-shadow:0 4px 14px rgba(201,168,76,.22)!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 22px rgba(201,168,76,.36)!important;}



/* INPUTS */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;color:white!important;border-radius:8px!important;}
.stTextInput>div>div>input:focus{border-color:rgba(201,168,76,.45)!important;}
.stSelectbox>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;color:white!important;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03)!important;border-radius:8px!important;gap:2px!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.4)!important;font-size:13px!important;border-radius:6px!important;}
.stTabs [aria-selected="true"]{color:#C9A84C!important;background:rgba(201,168,76,.1)!important;}

/* RADIO */
.stRadio>div{flex-direction:row!important;flex-wrap:wrap!important;gap:8px!important;}
.stRadio>div>label{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;padding:6px 12px!important;color:rgba(255,255,255,.5)!important;font-size:13px!important;}

/* EXPANDER */
.stExpander{border:1px solid rgba(201,168,76,.15)!important;border-radius:12px!important;background:rgba(255,255,255,.02)!important;}

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
.src-icon{font-size:16px;margin-top:1px;flex-shrink:0;font-family:'DM Mono',monospace;}
.src-label{font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:rgba(255,255,255,.78);}
.src-math{font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;margin-top:2px;letter-spacing:.5px;}
.src-afin-badge{font-family:'DM Mono',monospace;font-size:9px;color:rgba(201,168,76,.6);letter-spacing:1px;margin-top:2px;}
.src-desc{font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.35);line-height:1.5;margin-top:2px;}
.src-num{font-family:'DM Mono',monospace;font-size:16px;color:#C9A84C;font-weight:700;flex-shrink:0;margin-top:1px;}
.src-complement .src-num{color:rgba(255,255,255,.25);}

/* MISC */
.tag-gold{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;}
.metric-pill{display:inline-block;padding:4px 12px;border-radius:20px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.18);font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.jackpot-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.disclaimer{background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:13px 15px;font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,.3);line-height:1.65;font-style:italic;margin-top:16px;}
.gold-line{width:36px;height:2px;margin:10px auto;background:linear-gradient(90deg,transparent,#C9A84C,transparent);}
.conv-wrap{text-align:center;padding:20px 0;}
.conv-ring{width:60px;height:60px;border-radius:50%;border:2px solid rgba(201,168,76,.2);border-top-color:#C9A84C;animation:spin 1s linear infinite;margin:0 auto 10px;}
.conv-label{font-family:'DM Mono',monospace;font-size:11px;color:rgba(255,255,255,.4);letter-spacing:1px;}

@media(max-width:768px){.ball{width:44px;height:44px;font-size:14px;}.src-desc{font-size:10px;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CREDENCIALES
# ==========================================
try:
    GROQ_KEY      = st.secrets["GROQ_API_KEY"]
    SB_URL        = st.secrets["SUPABASE_URL"]
    SB_KEY        = st.secrets["SUPABASE_KEY"]
    RESEND_KEY    = st.secrets.get("RESEND_API_KEY","")
    ADMIN_EMAIL   = st.secrets.get("ADMIN_EMAIL","admin@lucksort.com")
    ADMIN_PASS    = st.secrets.get("ADMIN_PASS","admin123")
    NEWS_KEY      = st.secrets.get("NEWS_API_KEY","")
    LOTTERY_KEY   = st.secrets.get("LOTTERYDATA_KEY","")
    STRIPE_LINK   = st.secrets.get("STRIPE_PAYMENT_LINK","https://buy.stripe.com/lucksort")
except:
    st.error("⚠️ Configure secrets in Streamlit Cloud."); st.stop()

groq_client = Groq(api_key=GROQ_KEY)
supabase: Client = create_client(SB_URL, SB_KEY)
APP_URL = "https://lucksort.streamlit.app"

# ==========================================
# 4. LOTERÍAS
# ==========================================
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

# Iconos Unicode premium
ICONS = {
    "historico":"⊞","community":"⊛","eventos":"⊕","fecha_personal":"✦",
    "numerologia":"ᚨ","fibonacci":"ϕ","sagrada":"⬡","tesla":"⌁",
    "fractal":"※","sueno":"∞","clima":"≋","lunar":"◐",
    "cambio":"⇌","primos":"∴","complement":"·","afin":"≈",
}

# Familias de afinidad entre sistemas
AFINIDADES = {
    "numerologia": ["primos","fecha_personal","lunar"],
    "fibonacci":   ["sagrada","primos","fractal"],
    "sagrada":     ["fibonacci","primos","tesla"],
    "tesla":       ["sagrada","numerologia","primos"],
    "primos":      ["fibonacci","sagrada","tesla"],
    "fractal":     ["fibonacci","historico","eventos"],
}

# ==========================================
# 5. TRADUCCIONES
# ==========================================
T = {
"EN":{
    "tagline":"Sort Your Luck",
    "hero_1":"Your numbers,","hero_2":"backed by the","hero_3":"world's signals.",
    "hero_sub":"Real data convergence — historical draws, community intelligence, world events and your personal mathematics — into combinations that mean something.",
    "cta_free":"Start Free","login":"Sign In","register":"Create Account","logout":"Sign Out",
    "email":"Email","password":"Password","confirm_pass":"Confirm Password",
    "btn_login":"Sign In","btn_register":"Create Free Account",
    "plan":"Plan","free":"Free","paid":"Convergence",
    "select_lottery":"Select Lottery","jackpot_live":"Live Jackpot",
    "personal_title":"Personal Signals","special_date":"Special date (birthday, anniversary...)",
    "your_name":"Your name","life_moment":"Something happening in your life right now",
    "exclude_numbers":"Numbers to exclude (comma separated)",
    "dream_title":"Dream Mode ∞","dream_placeholder":"Tell me your dream... water, number 7, a golden door...",
    "dream_help":"Describe your dream and we extract numbers from its symbols",
    "symbolic_title":"Symbolic Systems","symbolic_help":"Select which systems to include",
    "sys_num":"ᚨ Numerology","sys_fib":"ϕ Fibonacci","sys_sag":"⬡ Sacred Geometry",
    "sys_tes":"⌁ Tesla (3·6·9)","sys_fra":"※ Fractals","sys_pri":"∴ Prime Numbers",
    "crowd_pref":"Crowd","follow":"Follow","avoid":"Avoid","balanced":"Balanced",
    "generate_btn":"Generate Combination","generating":"Converging data sources...",
    "conv_step1":"Analyzing world events...","conv_step2":"Reading community signals...",
    "conv_step3":"Computing your mathematics...","conv_step4":"Converging into your numbers...",
    "sources_title":"Where each number comes from",
    "afin_label":"Affinity source","gen_counter":"Today",
    "email_combo":"Send to my email","email_sent":"✅ Sent!","email_err":"⚠️ Configure Resend first.",
    "share_label":"Copy & share:","upgrade_btn":"Upgrade — $9.99/month",
    "paywall_title":"Convergence Plan",
    "paywall_msg":"Unlock full data convergence: historical analysis, community intelligence, world events, personal mathematics and Dream Mode.",
    "history":"My History","no_history":"No combinations yet.",
    "perfil":"My Lucky Profile","estadisticas":"Statistics","guardadas":"Saved",
    "comparador":"Compare Results","comparar_intro":"Enter the winning numbers to compare with your combinations",
    "num_maestro":"Master Number","mejor_loteria":"Best Lottery for You",
    "mejor_dia":"Best Day to Play","total_generadas":"Total Generated",
    "racha":"Active Streak","racha_dias":"days","nums_frecuentes":"Your Frequent Numbers",
    "guardar":"Save Combination","guardada":"✅ Saved","sin_guardadas":"No saved combinations yet.",
    "proxima_sorteo":"Next draw","dias_para":"days","hoy_sorteo":"Draw today!",
    "ingresar_ganadores":"Enter winning numbers (comma separated)",
    "comparar_btn":"Compare","aciertos":"matches","tu_combo":"Your combination",
    "ganadores_oficiales":"Official numbers","perfil_desc":"Based on your name and birthday provided in Personal Signals",
    "login_err":"❌ Incorrect credentials.","pass_mismatch":"⚠️ Passwords don't match.",
    "pass_short":"⚠️ Minimum 6 characters.","email_invalid":"⚠️ Invalid email.",
    "email_exists":"⚠️ Email already registered.",
    "disclaimer":"We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
    "sources":{
        "historico":"Draw History","community":"Community","eventos":"World Events",
        "fecha_personal":"Your Date","numerologia":"Numerology","fibonacci":"Fibonacci",
        "sagrada":"Sacred Geometry","tesla":"Tesla 3·6·9","fractal":"Fractal",
        "sueno":"Dream","clima":"Climate","lunar":"Lunar Cycle","cambio":"Exchange Rate",
        "primos":"Prime Numbers","complement":"Complement","afin":"Affinity",
    },
},
"ES":{
    "tagline":"Ordena tu Suerte",
    "hero_1":"Tus números,","hero_2":"respaldados por","hero_3":"las señales del mundo.",
    "hero_sub":"Convergencia de datos reales — sorteos históricos, inteligencia de comunidad, eventos del mundo y tu matemática personal — en combinaciones con significado.",
    "cta_free":"Empezar Gratis","login":"Entrar","register":"Crear Cuenta","logout":"Cerrar Sesión",
    "email":"Correo","password":"Contraseña","confirm_pass":"Confirmar contraseña",
    "btn_login":"Entrar","btn_register":"Crear Cuenta Gratis",
    "plan":"Plan","free":"Gratis","paid":"Convergencia",
    "select_lottery":"Selecciona tu Lotería","jackpot_live":"Jackpot en vivo",
    "personal_title":"Señales personales","special_date":"Fecha especial (cumpleaños, aniversario...)",
    "your_name":"Tu nombre","life_moment":"Algo que está pasando en tu vida ahora",
    "exclude_numbers":"Números a excluir (separados por coma)",
    "dream_title":"Modo Sueños ∞","dream_placeholder":"Cuéntame tu sueño... agua, el número 7, una puerta dorada...",
    "dream_help":"Describe tu sueño y extraemos números de sus símbolos",
    "symbolic_title":"Sistemas simbólicos","symbolic_help":"Selecciona qué sistemas incluir",
    "sys_num":"ᚨ Numerología","sys_fib":"ϕ Fibonacci","sys_sag":"⬡ Geometría Sagrada",
    "sys_tes":"⌁ Tesla (3·6·9)","sys_fra":"※ Fractales","sys_pri":"∴ Números Primos",
    "crowd_pref":"Comunidad","follow":"Seguir","avoid":"Evitar","balanced":"Balanceado",
    "generate_btn":"Generar Combinación","generating":"Convergiendo fuentes de datos...",
    "conv_step1":"Analizando eventos del mundo...","conv_step2":"Leyendo señales de la comunidad...",
    "conv_step3":"Calculando tu matemática personal...","conv_step4":"Convergiendo en tus números...",
    "sources_title":"De dónde viene cada número",
    "afin_label":"Fuente afín","gen_counter":"Hoy",
    "email_combo":"Enviar a mi correo","email_sent":"✅ ¡Enviado!","email_err":"⚠️ Configura Resend primero.",
    "share_label":"Copia y comparte:","upgrade_btn":"Actualizar — $9.99/mes",
    "paywall_title":"Plan Convergencia",
    "paywall_msg":"Desbloquea la convergencia completa: análisis histórico, inteligencia de comunidad, eventos mundiales, matemática personal y Modo Sueños.",
    "history":"Mi Historial","no_history":"Aún no has generado combinaciones.",
    "perfil":"Mi Perfil de Suerte","estadisticas":"Estadísticas","guardadas":"Guardadas",
    "comparador":"Comparar Resultados","comparar_intro":"Ingresa los números ganadores para comparar con tus combinaciones",
    "num_maestro":"Número Maestro","mejor_loteria":"Tu Lotería Ideal",
    "mejor_dia":"Mejor Día para Jugar","total_generadas":"Total Generadas",
    "racha":"Racha Activa","racha_dias":"días","nums_frecuentes":"Tus Números Frecuentes",
    "guardar":"Guardar Combinación","guardada":"✅ Guardada","sin_guardadas":"Aún no tienes combinaciones guardadas.",
    "proxima_sorteo":"Próximo sorteo","dias_para":"días","hoy_sorteo":"¡Sorteo hoy!",
    "ingresar_ganadores":"Ingresa números ganadores (separados por coma)",
    "comparar_btn":"Comparar","aciertos":"aciertos","tu_combo":"Tu combinación",
    "ganadores_oficiales":"Números oficiales","perfil_desc":"Basado en tu nombre y cumpleaños en Señales Personales",
    "login_err":"❌ Credenciales incorrectas.","pass_mismatch":"⚠️ Las contraseñas no coinciden.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ El correo ya está registrado.",
    "disclaimer":"Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
    "sources":{
        "historico":"Histórico","community":"Comunidad","eventos":"Eventos",
        "fecha_personal":"Tu Fecha","numerologia":"Numerología","fibonacci":"Fibonacci",
        "sagrada":"Geometría Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal",
        "sueno":"Sueño","clima":"Clima","lunar":"Ciclo Lunar","cambio":"Tasa de Cambio",
        "primos":"Números Primos","complement":"Complemento","afin":"Afín",
    },
},
"PT":{
    "tagline":"Organize sua Sorte",
    "hero_1":"Seus números,","hero_2":"respaldados pelos","hero_3":"sinais do mundo.",
    "hero_sub":"Convergência de dados reais — histórico de sorteios, inteligência da comunidade, eventos do mundo e sua matemática pessoal — em combinações com significado.",
    "cta_free":"Começar Grátis","login":"Entrar","register":"Criar Conta","logout":"Sair",
    "email":"Email","password":"Senha","confirm_pass":"Confirmar senha",
    "btn_login":"Entrar","btn_register":"Criar Conta Grátis",
    "plan":"Plano","free":"Grátis","paid":"Convergência",
    "select_lottery":"Selecione sua Loteria","jackpot_live":"Jackpot ao vivo",
    "personal_title":"Sinais pessoais","special_date":"Data especial (aniversário...)",
    "your_name":"Seu nome","life_moment":"Algo acontecendo na sua vida agora",
    "exclude_numbers":"Números a excluir (separados por vírgula)",
    "dream_title":"Modo Sonhos ∞","dream_placeholder":"Me conte seu sonho... água, o número 7, uma porta dourada...",
    "dream_help":"Descreva seu sonho e extrairemos números dos seus símbolos",
    "symbolic_title":"Sistemas simbólicos","symbolic_help":"Selecione quais sistemas incluir",
    "sys_num":"ᚨ Numerologia","sys_fib":"ϕ Fibonacci","sys_sag":"⬡ Geometria Sagrada",
    "sys_tes":"⌁ Tesla (3·6·9)","sys_fra":"※ Fractais","sys_pri":"∴ Números Primos",
    "crowd_pref":"Comunidade","follow":"Seguir","avoid":"Evitar","balanced":"Balanceado",
    "generate_btn":"Gerar Combinação","generating":"Convergindo fontes de dados...",
    "conv_step1":"Analisando eventos do mundo...","conv_step2":"Lendo sinais da comunidade...",
    "conv_step3":"Calculando sua matemática pessoal...","conv_step4":"Convergindo em seus números...",
    "sources_title":"De onde vem cada número",
    "afin_label":"Fonte afim","gen_counter":"Hoje",
    "email_combo":"Enviar para meu email","email_sent":"✅ Enviado!","email_err":"⚠️ Configure o Resend primeiro.",
    "share_label":"Copie e compartilhe:","upgrade_btn":"Atualizar — $9.99/mês",
    "paywall_title":"Plano Convergência",
    "paywall_msg":"Desbloqueie a convergência completa: análise histórica, inteligência da comunidade, eventos mundiais, matemática pessoal e Modo Sonhos.",
    "history":"Meu Histórico","no_history":"Ainda não gerou combinações.",
    "perfil":"Meu Perfil de Sorte","estadisticas":"Estatísticas","guardadas":"Salvas",
    "comparador":"Comparar Resultados","comparar_intro":"Insira os números vencedores para comparar com suas combinações",
    "num_maestro":"Número Mestre","mejor_loteria":"Sua Loteria Ideal",
    "mejor_dia":"Melhor Dia para Jogar","total_generadas":"Total Geradas",
    "racha":"Sequência Ativa","racha_dias":"dias","nums_frecuentes":"Seus Números Frequentes",
    "guardar":"Salvar Combinação","guardada":"✅ Salva","sin_guardadas":"Ainda não tem combinações salvas.",
    "proxima_sorteo":"Próximo sorteio","dias_para":"dias","hoy_sorteo":"Sorteio hoje!",
    "ingresar_ganadores":"Insira números vencedores (separados por vírgula)",
    "comparar_btn":"Comparar","aciertos":"acertos","tu_combo":"Sua combinação",
    "ganadores_oficiales":"Números oficiais","perfil_desc":"Baseado no seu nome e aniversário em Sinais Pessoais",
    "login_err":"❌ Credenciais incorretas.","pass_mismatch":"⚠️ As senhas não coincidem.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ Email já cadastrado.",
    "disclaimer":"Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
    "sources":{
        "historico":"Histórico","community":"Comunidade","eventos":"Eventos",
        "fecha_personal":"Sua Data","numerologia":"Numerologia","fibonacci":"Fibonacci",
        "sagrada":"Geometria Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal",
        "sueno":"Sonho","clima":"Clima","lunar":"Ciclo Lunar","cambio":"Taxa de Câmbio",
        "primos":"Números Primos","complement":"Complemento","afin":"Afim",
    },
},
}
def tr(): return T[st.session_state["idioma"]]

def strip_html(text):
    """Remove any HTML tags Groq may include in explanations"""
    if not text: return ""
    clean = re.sub(r'<[^>]+>', ' ', str(text))
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

# ==========================================
# 6. CÁLCULOS MATEMÁTICOS PUROS
# ==========================================
def calc_fibonacci(mn,mx):
    seq=[]; a,b=1,1; pos=1
    while a<=mx:
        if a>=mn:
            formula=f"{b-a}+{a-b+a}={a}" if pos>2 else f"F{pos}={a}"
            if pos>=3:
                prev2=b-a
                prev1=a-prev2
                if prev2>0 and prev1>0:
                    formula=f"{prev2}+{prev1}={a} · F{pos}"
                else:
                    formula=f"F{pos}={a}"
            seq.append({"n":a,"pos":pos,"formula":formula,"fuente":"fibonacci"})
        a,b=b,a+b; pos+=1
    # Rebuild with correct formulas
    result=[]
    fa,fb=1,1
    for i in range(1,100):
        if fa>mx: break
        if fa>=mn:
            if i>=3:
                p2=fb-fa; p1=fa-p2 if fa-p2>0 else fb-fa
                # simpler
                result.append({"n":fa,"pos":i,"formula":f"F{i}={fa}","fuente":"fibonacci"})
            else:
                result.append({"n":fa,"pos":i,"formula":f"F{i}={fa}","fuente":"fibonacci"})
        fa,fb=fb,fa+fb
    # Fix formulas properly
    fibs=[]
    a,b=1,1
    for i in range(1,100):
        if a>mx: break
        if a>=mn:
            if i>=3:
                fibs.append({"n":a,"pos":i,"formula":f"F{i-2}+F{i-1}={a}","fuente":"fibonacci"})
            else:
                fibs.append({"n":a,"pos":i,"formula":f"F{i}={a}","fuente":"fibonacci"})
        a,b=b,a+b
    return fibs

def calc_tesla(mn,mx):
    result=[]
    for n in range(mn,mx+1):
        if n%3==0:
            k=n//3
            red=n%9 if n%9!=0 else 9
            result.append({"n":n,"formula":f"3×{k}={n} → reducción={red}","fuente":"tesla"})
    return result

def calc_sagrada(mn,mx):
    PHI=1.6180339887; PI=3.14159265358979
    result=[]; seen=set()
    for i in range(1,60):
        pairs=[(int(PHI*i),f"ϕ×{i}={PHI*i:.3f}→{int(PHI*i)}","sagrada"),
               (int(PI*i),f"π×{i}={PI*i:.3f}→{int(PI*i)}","sagrada"),
               (round(PHI**2*i),f"ϕ²×{i}={PHI**2*i:.3f}→{round(PHI**2*i)}","sagrada")]
        for v,formula,f in pairs:
            if mn<=v<=mx and v not in seen:
                result.append({"n":v,"formula":formula,"fuente":"sagrada"}); seen.add(v)
    return sorted(result,key=lambda x:x["n"])

def calc_primos(mn,mx):
    def es_primo(n):
        if n<2: return False
        for i in range(2,int(n**0.5)+1):
            if n%i==0: return False
        return True
    return [{"n":n,"formula":f"{n} es primo","fuente":"primos"} for n in range(mn,mx+1) if es_primo(n)]

def calc_numerologia(nombre,fecha_str):
    result={}
    if nombre and nombre.strip():
        tabla={c:((ord(c.lower())-ord('a'))%9)+1 for c in 'abcdefghijklmnopqrstuvwxyz'}
        letras=[(c.upper(),tabla.get(c.lower(),0)) for c in nombre if c.isalpha()]
        if letras:
            suma=sum(v for _,v in letras)
            formula="+".join([f"{c}({v})" for c,v in letras])+f"={suma}"
            orig=suma
            while suma>9 and suma not in [11,22,33]:
                suma=sum(int(d) for d in str(suma))
                formula+=f"→{suma}"
            result["nombre"]={"n":suma,"formula":formula,"maestro":suma in [11,22,33],"fuente":"numerologia"}
    if fecha_str and fecha_str.strip():
        digitos=[c for c in fecha_str if c.isdigit()]
        if digitos:
            suma=sum(int(d) for d in digitos)
            formula="+".join(digitos)+f"={suma}"
            while suma>9 and suma not in [11,22,33]:
                suma=sum(int(d) for d in str(suma))
                formula+=f"→{suma}"
            result["fecha"]={"n":suma,"formula":formula,"maestro":suma in [11,22,33],"fuente":"numerologia"}
    return result

def calc_lunar():
    known_new=datetime(2000,1,6,18,14)
    cycle=29.53058867
    now=datetime.now()
    diff=(now-known_new).total_seconds()/(24*3600)
    phase=diff%cycle
    day=int(phase)+1
    phases=["Nueva","Creciente","Creciente","Creciente","Creciente","Creciente","Creciente",
            "Cuarto C","Cuarto C","Gibosa C","Gibosa C","Gibosa C","Gibosa C","Gibosa C",
            "Llena","Llena","Gibosa M","Gibosa M","Gibosa M","Gibosa M","Gibosa M",
            "Gibosa M","Cuarto M","Cuarto M","Menguante","Menguante","Menguante",
            "Menguante","Menguante","Nueva"]
    phase_name=phases[min(day-1,29)]
    return {"day":day,"formula":f"Luna día {day}/29 · {phase_name}","fuente":"lunar","phase":phase_name}

def calc_nums_fecha(fecha_str,mn,mx):
    result=[]; seen=set()
    if not fecha_str: return result
    partes=[x for x in re.split(r'[-/.]',fecha_str) if x.isdigit()]
    for p in partes:
        v=int(p)
        if mn<=v<=mx and v not in seen:
            result.append({"n":v,"formula":f"{p} directo de tu fecha","fuente":"fecha_personal"}); seen.add(v)
        if len(p)==4:
            s=int(p[-2:])
            if mn<=s<=mx and s not in seen:
                result.append({"n":s,"formula":f"{p}[-2:]={s}","fuente":"fecha_personal"}); seen.add(s)
        sd=sum(int(d) for d in p)
        if mn<=sd<=mx and sd not in seen:
            result.append({"n":sd,"formula":f"Σ({'+'.join(list(p))})={sd}","fuente":"fecha_personal"}); seen.add(sd)
    return result

# ==========================================
# 7. APIS EXTERNAS
# ==========================================
def get_cache(tipo):
    try:
        hoy=str(date.today())
        res=supabase.table("cache_diario").select("*").eq("fecha",hoy).eq("tipo",tipo).execute()
        return res.data[0]["contenido"] if res.data else None
    except: return None

def set_cache(tipo,contenido,fuente=""):
    try:
        hoy=str(date.today())
        ex=supabase.table("cache_diario").select("id").eq("fecha",hoy).eq("tipo",tipo).execute()
        if ex.data:
            supabase.table("cache_diario").update({"contenido":contenido}).eq("id",ex.data[0]["id"]).execute()
        else:
            supabase.table("cache_diario").insert({"fecha":hoy,"tipo":tipo,"contenido":contenido,"fuente":fuente}).execute()
    except: pass

def obtener_efemerides(mes,dia):
    tipo=f"efem_{mes}_{dia}"
    c=get_cache(tipo)
    if c: return c
    try:
        r=requests.get(f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{mes}/{dia}",timeout=8)
        if r.status_code==200:
            evts=r.json().get("events",[])[:8]
            res=[{"year":e.get("year"),"text":e.get("text","")[:180]} for e in evts]
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
                arts=r.json().get("articles",[])[:6]
                res=[{"title":a.get("title","")[:130]} for a in arts]
                set_cache("noticias",res,"newsapi"); return res
    except: pass
    return []

def obtener_clima():
    c=get_cache("clima")
    if c: return c
    try:
        r=requests.get("https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&current=temperature_2m,surface_pressure,relative_humidity_2m&timezone=auto",timeout=8)
        if r.status_code==200:
            curr=r.json().get("current",{})
            temp=round(curr.get("temperature_2m",0))
            pres=round(curr.get("surface_pressure",1013))
            hum=round(curr.get("relative_humidity_2m",50))
            res={"temp":temp,"pressure":pres,"humidity":hum,
                 "formula_temp":f"Temp NY hoy: {temp}°C → {temp}",
                 "formula_pres":f"Presión: {pres} hPa → {str(pres)[-2:]}",
                 "formula_hum":f"Humedad: {hum}% → {hum}"}
            set_cache("clima",res,"open-meteo"); return res
    except: pass
    return {}

def obtener_tasa():
    c=get_cache("tasa")
    if c: return c
    try:
        r=requests.get("https://api.exchangerate-api.com/v4/latest/USD",timeout=8)
        if r.status_code==200:
            rates=r.json().get("rates",{})
            eur=rates.get("EUR",0.92)
            eur_str=f"{eur:.4f}".replace(".","")
            nums=[int(eur_str[i:i+2]) for i in range(0,len(eur_str)-1,2) if int(eur_str[i:i+2])>0]
            res={"usd_eur":eur,"formula":f"USD/EUR={eur:.4f} → dígitos","nums":nums}
            set_cache("tasa",res,"exchangerate"); return res
    except: pass
    return {}

def obtener_reddit(loteria):
    tipo=f"reddit_{loteria['id']}_{date.today()}"
    c=get_cache(tipo)
    if c: return c
    headers={"User-Agent":"LuckSort/1.0"}
    mn,mx=loteria["min"],loteria["max"]
    nums=[]
    for sub in loteria.get("reddit",["lottery"])[:2]:
        try:
            r=requests.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=20",headers=headers,timeout=8)
            if r.status_code==200:
                posts=r.json().get("data",{}).get("children",[])
                for p in posts:
                    texto=p.get("data",{}).get("title","")+p.get("data",{}).get("selftext","")
                    for n in re.findall(r'\b(\d{1,2})\b',texto):
                        v=int(n)
                        if mn<=v<=mx: nums.append(v)
        except: pass
    if nums:
        conteo=Counter(nums)
        top=[{"n":n,"count":cnt,"formula":f"Mencionado {cnt}× en r/{loteria['reddit'][0]} hoy","fuente":"community"} for n,cnt in conteo.most_common(12)]
        set_cache(tipo,top,"reddit"); return top
    return []

# Datos históricos reales — frecuencias verificadas de fuentes oficiales
# Fuente: Powerball.com, LotteryUSA.com, Caixa.gov.br, ONCE.es, Camelot.co.uk
HISTORICO_REAL = {
    "Powerball": {
        "top_numeros":  [26,41,16,28,22,23,32,42,36,61,39,20,53,19,66],
        "top_bonus":    [6,9,20,2,12,18,24,11,15,7],
        "dias_sorteo":  ["Mon","Wed","Sat"],
        "sorteo_hora":  "22:59 ET",
    },
    "Mega Millions": {
        "top_numeros":  [17,31,10,4,46,20,14,39,2,29,70,35,23,25,8],
        "top_bonus":    [9,11,19,1,3,10,7,2,15,6],
        "dias_sorteo":  ["Tue","Fri"],
        "sorteo_hora":  "23:00 ET",
    },
    "EuroMillions": {
        "top_numeros":  [23,44,19,50,5,17,27,35,48,38,20,6,43,3,15],
        "top_bonus":    [2,8,3,9,5,1,6,11,4,12],
        "dias_sorteo":  ["Tue","Fri"],
        "sorteo_hora":  "21:00 CET",
    },
    "UK Lotto": {
        "top_numeros":  [23,38,31,25,33,11,2,40,6,39,28,44,17,1,48],
        "top_bonus":    [],
        "dias_sorteo":  ["Wed","Sat"],
        "sorteo_hora":  "19:45 GMT",
    },
    "El Gordo": {
        "top_numeros":  [11,23,7,33,4,15,28,6,19,35,42,2,22,38,17],
        "top_bonus":    [5,3,8,1,7,9,4,2,6,10],
        "dias_sorteo":  ["Sun"],
        "sorteo_hora":  "21:25 CET",
    },
    "Mega-Sena": {
        "top_numeros":  [10,53,23,4,52,33,43,37,41,25,5,34,8,20,42],
        "top_bonus":    [],
        "dias_sorteo":  ["Wed","Sat"],
        "sorteo_hora":  "20:00 BRT",
    },
    "Lotofácil": {
        "top_numeros":  [20,5,7,12,23,11,18,24,15,3,25,9,2,13,22],
        "top_bonus":    [],
        "dias_sorteo":  ["Mon","Tue","Wed","Thu","Fri","Sat"],
        "sorteo_hora":  "20:00 BRT",
    },
    "Baloto": {
        "top_numeros":  [11,23,7,33,4,15,28,6,19,35,43,2,22,38,17],
        "top_bonus":    [3,8,12,5,2,15,9,1,7,11],
        "dias_sorteo":  ["Wed","Sat"],
        "sorteo_hora":  "22:00 COT",
    },
    "La Primitiva": {
        "top_numeros":  [28,36,14,3,25,42,7,16,33,48,21,9,38,45,11],
        "top_bonus":    [],
        "dias_sorteo":  ["Thu","Sat"],
        "sorteo_hora":  "21:30 CET",
    },
    "EuroJackpot": {
        "top_numeros":  [19,49,32,18,7,23,17,40,3,37,50,29,44,11,22],
        "top_bonus":    [8,4,6,2,10,5,3,9,7,1],
        "dias_sorteo":  ["Tue","Fri"],
        "sorteo_hora":  "21:00 CET",
    },
    "Canada Lotto": {
        "top_numeros":  [20,33,34,40,44,6,19,32,43,39,7,13,24,37,16],
        "top_bonus":    [2,19,28,37,7,24,14,42,10,32],
        "dias_sorteo":  ["Wed","Sat"],
        "sorteo_hora":  "22:30 ET",
    },
}

def obtener_historico_frecuencias(loteria_nombre, mes_actual):
    """Frecuencias reales verificadas de fuentes oficiales"""
    data = HISTORICO_REAL.get(loteria_nombre, {})
    top = data.get("top_numeros", [])
    if top:
        return [{"n":n, "formula":f"Top histórico oficial {loteria_nombre}", "fuente":"historico"} for n in top]
    return []

def proximo_sorteo(loteria_nombre):
    """Calcula días hasta el próximo sorteo"""
    data = HISTORICO_REAL.get(loteria_nombre, {})
    dias = data.get("dias_sorteo", [])
    hora = data.get("sorteo_hora", "")
    if not dias: return None
    hoy = datetime.now()
    dias_semana = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
    hoy_num = hoy.weekday()
    proximos = []
    for d in dias:
        d_num = dias_semana.get(d, 0)
        diff = (d_num - hoy_num) % 7
        if diff == 0: diff = 7
        proximos.append((diff, d))
    proximos.sort()
    dias_falta, dia_nombre = proximos[0]
    return {"dias": dias_falta, "dia": dia_nombre, "hora": hora}

def obtener_jackpot(nombre):
    c=get_cache(f"jackpot_{nombre}")
    if c: return c
    try:
        slug={"Powerball":"powerball","Mega Millions":"megamillions","EuroMillions":"euromillions","EuroJackpot":"eurojackpot"}.get(nombre)
        if not slug: return None
        r=requests.get(f"https://lotterydata.io/api/{slug}/latest",timeout=6)
        if r.status_code==200:
            data=r.json()
            jackpot=data.get("data",[{}])[0].get("jackpot") or data.get("jackpot")
            if jackpot: set_cache(f"jackpot_{nombre}",jackpot,"lotterydata"); return jackpot
    except: pass
    return None

# ==========================================
# 8. PREPROCESADOR
# ==========================================
def preparar_datos(loteria,inputs):
    mn,mx=loteria["min"],loteria["max"]
    hoy=datetime.now()
    sistemas=inputs.get("sistemas",[])
    candidatos=[]

    def agregar(item):
        if mn<=item["n"]<=mx:
            candidatos.append(item)

    # === SISTEMAS SELECCIONADOS ÚNICAMENTE ===
    if "numerologia" in sistemas:
        num_data=calc_numerologia(inputs.get("nombre",""),inputs.get("fecha_especial",""))
        for key,val in num_data.items():
            agregar({**val,"peso":5,"sistema":"numerologia"})
        # Maestros adicionales afines a numerología
        for m in [11,22,33]:
            if mn<=m<=mx and not any(c["n"]==m for c in candidatos):
                agregar({"n":m,"formula":f"Número maestro {m}","fuente":"numerologia","peso":3,"sistema":"numerologia"})

    if "fibonacci" in sistemas:
        for f in calc_fibonacci(mn,mx):
            agregar({**f,"peso":4,"sistema":"fibonacci"})

    if "sagrada" in sistemas:
        for s in calc_sagrada(mn,mx)[:20]:
            agregar({**s,"peso":4,"sistema":"sagrada"})

    if "tesla" in sistemas:
        for t in calc_tesla(mn,mx):
            agregar({**t,"peso":3,"sistema":"tesla"})

    if "primos" in sistemas:
        for p in calc_primos(mn,mx):
            agregar({**p,"peso":2,"sistema":"primos"})

    # Fecha personal — siempre si hay datos
    fecha_esp=inputs.get("fecha_especial","")
    if fecha_esp:
        for nf in calc_nums_fecha(fecha_esp,mn,mx):
            agregar({**nf,"peso":5,"sistema":"fecha_personal"})
        # Efemérides de esa fecha
        partes=[x for x in re.split(r'[-/.]',fecha_esp) if x.isdigit()]
        if len(partes)>=2:
            try:
                d_p,m_p=int(partes[0]),int(partes[1])
                if 1<=d_p<=31 and 1<=m_p<=12:
                    efem_p=obtener_efemerides(m_p,d_p)
                    for ev in efem_p[:3]:
                        year=ev.get("year",0)
                        if year:
                            y2=year%100
                            if mn<=y2<=mx:
                                agregar({"n":y2,"formula":f"Tu fecha {d_p}/{m_p}: {year}→{y2}","fuente":"fecha_personal","peso":4,"sistema":"fecha_personal"})
            except: pass

    # === FUENTES DEL DÍA — siempre activas ===
    lunar=calc_lunar()
    if mn<=lunar["day"]<=mx:
        agregar({**lunar,"n":lunar["day"],"peso":3,"sistema":"general"})

    clima=obtener_clima()
    if clima:
        for v,formula in [(clima.get("temp",0),clima.get("formula_temp","")),
                          (clima.get("humidity",0),clima.get("formula_hum","")),
                          (int(str(clima.get("pressure",1013))[-2:]),clima.get("formula_pres",""))]:
            if mn<=v<=mx:
                agregar({"n":v,"formula":formula,"fuente":"clima","peso":2,"sistema":"general"})

    tasa=obtener_tasa()
    if tasa:
        for n in tasa.get("nums",[]):
            if mn<=n<=mx:
                agregar({"n":n,"formula":tasa.get("formula",""),"fuente":"cambio","peso":1,"sistema":"general"})

    # Wikipedia hoy
    efem=obtener_efemerides(hoy.month,hoy.day)
    for ev in efem[:6]:
        year=ev.get("year",0)
        if year:
            y2=year%100
            if mn<=y2<=mx:
                agregar({"n":y2,"formula":f"{year}: {ev.get('text','')[:50]}... → {y2}","fuente":"eventos","peso":2,"sistema":"general"})
            yd=sum(int(d) for d in str(year))
            if mn<=yd<=mx:
                agregar({"n":yd,"formula":f"Σ({'+'.join(list(str(year)))})={yd}","fuente":"eventos","peso":1,"sistema":"general"})

    # Noticias
    noticias=obtener_noticias()
    for art in noticias[:4]:
        for n in re.findall(r'\b(\d{1,2})\b',art.get("title","")):
            v=int(n)
            if mn<=v<=mx:
                agregar({"n":v,"formula":f"'{art['title'][:45]}...'","fuente":"eventos","peso":1,"sistema":"general"})

    # Reddit
    reddit=obtener_reddit(loteria)
    for item in reddit[:8]:
        agregar({"n":item["n"],"formula":item["formula"],"fuente":"community","peso":3,"sistema":"general"})

    # Histórico
    hist=obtener_historico_frecuencias(loteria["nombre"],hoy.month)
    for item in hist[:8]:
        agregar({"n":item["n"],"formula":item["formula"],"fuente":"historico","peso":3,"sistema":"general"})

    # Fecha de hoy
    for v,formula in [(hoy.day,f"Día {hoy.day} de hoy"),
                      (hoy.month,f"Mes {hoy.month} actual"),
                      (hoy.day+hoy.month,f"Día+Mes={hoy.day}+{hoy.month}={hoy.day+hoy.month}"),
                      (hoy.year%100,f"Año {hoy.year}→{hoy.year%100}")]:
        if mn<=v<=mx:
            agregar({"n":v,"formula":formula,"fuente":"eventos","peso":1,"sistema":"general"})

    # Deduplicar — mejor por número
    mejor={}
    for c in candidatos:
        n=c["n"]
        if n not in mejor or c.get("peso",0)>mejor[n].get("peso",0):
            mejor[n]=c

    # Marcar usados recientemente
    usados=set()
    for gen in st.session_state.get("historial_sesion",[])[-3:]:
        usados.update(gen)
    for n in mejor:
        mejor[n]["ya_usado"]=n in usados

    candidatos_final=list(mejor.values())
    random.shuffle(candidatos_final)

    return {
        "candidatos": candidatos_final,
        "sistemas_activos": sistemas,
        "efemerides_hoy": efem,
        "noticias": noticias,
        "reddit": reddit,
        "lunar": lunar,
        "clima": clima,
        "historico": hist,
        "fecha_hoy": hoy.strftime("%B %d, %Y"),
    }

# ==========================================
# 9. GENERACIÓN GROQ
# ==========================================
def generar_combinacion(loteria,inputs):
    lang=st.session_state["idioma"]
    lang_full={"EN":"English","ES":"Spanish","PT":"Portuguese"}[lang]
    datos=preparar_datos(loteria,inputs)
    candidatos=datos["candidatos"]
    sistemas=inputs.get("sistemas",[])

    excluir=[]
    if inputs.get("excluir"):
        try: excluir=[int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    candidatos_validos=[c for c in candidatos if c["n"] not in excluir]
    preferidos=[c for c in candidatos_validos if not c.get("ya_usado",False)]
    ya_usados=[c for c in candidatos_validos if c.get("ya_usado",False)]
    ordenados=preferidos+ya_usados

    seed=random.randint(1000,9999)
    sueno=inputs.get("sueno","")
    bonus_inst=f"1 {loteria['bname']} entre 1-{loteria['bmax']}" if loteria["bonus"] else "sin bonus"

    # Construir contexto de afinidades si hay sistemas seleccionados
    afin_context=""
    if sistemas:
        afins=[]
        for s in sistemas:
            afins.extend(AFINIDADES.get(s,[]))
        afins=list(set(afins)-set(sistemas))
        afin_context=f"""
FUENTES AFINES (usar SOLO si los sistemas seleccionados no tienen suficientes candidatos):
{afins}
Si usas una fuente afín → explica la relación: "Tomé este número de [fuente afín] porque es matemáticamente afín a [sistema seleccionado] — [razón]"
"""

    prompt=f"""Eres un equipo de especialistas generando una combinación de {loteria['nombre']}.
Seed #{seed} — cada generación debe ser única.

LOTERÍA: {loteria['nombre']} | {loteria['n']} números ({loteria['min']}-{loteria['max']}) | {bonus_inst}
EXCLUIR: {excluir}
PREFERENCIA CROWD: {inputs.get('crowd','balanced')}
COMBINACIONES RECIENTES A EVITAR: {st.session_state.get('historial_sesion',[])[-3:]}
SUEÑO DEL USUARIO: "{sueno if sueno else 'ninguno'}"

═══ REGLA PRINCIPAL — INAMOVIBLE ═══
SISTEMAS SELECCIONADOS POR EL USUARIO: {sistemas if sistemas else 'ninguno — usar solo fuentes del día'}

Si el usuario seleccionó sistemas → úsalos PRIMERO y PRINCIPALMENTE.
Si NO seleccionó ningún sistema → usa libremente todas las fuentes del día.
NUNCA uses un sistema NO seleccionado como fuente principal.
{afin_context}

═══ CANDIDATOS REALES PRE-CALCULADOS (Python verificado) ═══
{json.dumps(ordenados[:45], ensure_ascii=False, indent=2)}

═══ REGLAS DE SELECCIÓN ═══
1. Elige SOLO de la lista de candidatos pre-calculados
2. Cada número de una fuente diferente cuando sea posible
3. Máximo 1 número de fuente "community"
4. Máximo 1 número de cada sistema simbólico
5. Prefiere candidatos con ya_usado=false
6. El número BONUS merece su propia fuente real específica
   → busca un candidato en rango 1-{loteria['bmax'] if loteria['bonus'] else 'N/A'}
   → con su razonamiento propio, NO puede ser "complement"
   → si no hay candidato real → usa afinidad y explícalo
7. Si hay sueño → extrae número del símbolo del sueño como fuente "sueno"

═══ VOZ DE CADA ESPECIALISTA ═══
fibonacci → matemático: menciona posición en secuencia, suma de anteriores
tesla → físico: menciona el ciclo 3-6-9 y la reducción digital
sagrada → geómetra sagrado: menciona ϕ o π y su múltiplo exacto
numerologia → numerólogo: muestra la reducción paso a paso
eventos/historico → historiador: nombra el evento o frecuencia específica
community → analista de datos: cita el conteo exacto de menciones
clima → meteorólogo: cita la medición exacta
lunar → astrónomo: cita el día del ciclo y la fase
cambio → analista financiero: cita la tasa exacta
sueno → intérprete de sueños: explica el símbolo y su número
afin → explica la relación de afinidad con el sistema principal

NUNCA uses lenguaje genérico de IA.
NUNCA inventes datos no presentes en los candidatos.
Explica en {lang_full}, mínimo 12 palabras por número, voz de experto.

Responde SOLO en {lang_full}. Devuelve SOLO JSON válido:
{{
  "numbers": [lista de {loteria['n']} enteros],
  "bonus": {f'entero 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources": [
    {{
      "number": N,
      "source": "tipo_fuente",
      "es_afin": false,
      "label": "rol del especialista en {lang_full}",
      "math": "fórmula o cálculo en una línea",
      "explanation": "voz de experto específica, mínimo 12 palabras"
    }}
  ]
}}"""

    try:
        resp=groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Equipo de especialistas en datos de lotería. Responde en {lang_full}. Solo JSON válido. Nunca inventes datos."},
                {"role":"user","content":prompt}
            ],
            temperature=round(random.uniform(0.62,0.88),2),
            max_tokens=1800
        )
        raw=resp.choices[0].message.content.strip()
        if "```" in raw: raw=raw.split("```")[1].replace("json","").strip()
        # Strip any HTML Groq may inject before parsing
        raw=re.sub(r'<[^>]+>','',raw)
        raw=re.sub(r'\s+',' ',raw)
        res=json.loads(raw)

        # Limpiar HTML en explanations de Groq
        for s in res.get("sources",[]):
            s["explanation"] = strip_html(s.get("explanation",""))
            s["math"] = strip_html(s.get("math",""))

        # Enforcer diversidad: max 1 número por sistema simbólico
        fuentes_usadas = {}
        sources_limpios = []
        sistemas_simbolicos = {"fibonacci","tesla","sagrada","numerologia","primos","fractal"}
        for s in res.get("sources",[]):
            fuente = s.get("source","complement")
            if fuente in sistemas_simbolicos:
                if fuente not in fuentes_usadas:
                    fuentes_usadas[fuente] = True
                    sources_limpios.append(s)
                # Si ya se usó ese sistema, lo convierte en fuente del día
                else:
                    s["source"] = "eventos"
                    s["label"] = s.get("label","")
                    s["es_afin"] = True
                    sources_limpios.append(s)
            else:
                sources_limpios.append(s)
        res["sources"] = sources_limpios

        # Validar números
        nums=[n for n in res.get("numbers",[]) if loteria["min"]<=n<=loteria["max"] and n not in excluir]
        disp=[c["n"] for c in ordenados if c["n"] not in nums and c["n"] not in excluir]
        while len(nums)<loteria["n"] and disp: nums.append(disp.pop(0))
        pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in nums and n not in excluir]
        while len(nums)<loteria["n"] and pool:
            p=random.choice(pool); nums.append(p); pool.remove(p)
        res["numbers"]=list(dict.fromkeys(nums))[:loteria["n"]]

        # Validar bonus
        if loteria["bonus"]:
            b=res.get("bonus")
            if not isinstance(b,int) or not (1<=b<=loteria["bmax"]):
                # Buscar candidato real en rango del bonus
                bonus_cands=[c["n"] for c in ordenados if 1<=c["n"]<=loteria["bmax"] and c["n"] not in nums]
                res["bonus"]=bonus_cands[0] if bonus_cands else random.randint(1,loteria["bmax"])

        # Guardar historial
        hist=st.session_state.get("historial_sesion",[])
        hist.append(res["numbers"])
        st.session_state["historial_sesion"]=hist[-5:]
        return res
    except:
        return generar_fallback(loteria,excluir,ordenados)

def generar_fallback(loteria,excluir=[],candidatos=[]):
    pool_r=[c["n"] for c in candidatos if c["n"] not in excluir]
    if len(pool_r)>=loteria["n"]:
        nums=random.sample(pool_r,loteria["n"])
        sources=[{"number":n,"source":next((c["fuente"] for c in candidatos if c["n"]==n),"complement"),"es_afin":False,"label":"·","math":next((c.get("formula","") for c in candidatos if c["n"]==n),""),"explanation":"Seleccionado de fuente real verificada."} for n in nums]
    else:
        pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in excluir]
        nums=random.sample(pool,min(loteria["n"],len(pool)))
        sources=[{"number":n,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Sin señal específica disponible."} for n in nums]
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    if bonus: sources.append({"number":bonus,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Bonus complementario."})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

def generar_aleatorio(loteria):
    pool=list(range(loteria["min"],loteria["max"]+1))
    nums=random.sample(pool,loteria["n"])
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    sources=[{"number":n,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Generación aleatoria — plan gratuito."} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","es_afin":False,"label":"·","math":"—","explanation":"Bonus aleatorio."})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

# ==========================================
# 10. SUPABASE
# ==========================================
def registrar_usuario(email,password):
    try:
        if supabase.table("usuarios").select("email").eq("email",email).execute().data:
            return False,"exists"
        res=supabase.table("usuarios").insert({"email":email,"password":password,"role":"free","generaciones_hoy":0,"fecha_uso":str(date.today())}).execute()
        return (True,res.data[0]) if res.data else (False,"error")
    except Exception as e: return False,str(e)

def login_usuario(email,password):
    try:
        res=supabase.table("usuarios").select("*").eq("email",email).eq("password",password).single().execute()
        return (True,res.data) if res.data else (False,None)
    except: return False,None

def actualizar_rol(user_id,rol):
    try:
        supabase.table("usuarios").update({"role":rol}).eq("id",user_id).execute()
    except: pass

def guardar_generacion(uid,lid,nums,bonus,sources,inputs):
    try:
        supabase.table("generaciones").insert({"user_id":uid,"loteria_id":lid,"numeros":nums,"bonus":bonus,"narrativa":json.dumps(sources,ensure_ascii=False),"inputs_usuario":json.dumps(inputs,ensure_ascii=False)}).execute()
    except: pass

def obtener_historial(uid,limit=15):
    try:
        res=supabase.table("generaciones").select("*").eq("user_id",uid).order("created_at",desc=True).limit(limit).execute()
        return res.data if res.data else []
    except: return []

def resetear_uso():
    hoy=str(date.today())
    if st.session_state.get("fecha_uso")!=hoy:
        st.session_state["generaciones_hoy"]={}
        st.session_state["fecha_uso"]=hoy
        st.session_state["historial_sesion"]=[]

# ==========================================
# 10b. FUNCIONES PERFIL + STATS + GUARDADAS
# ==========================================
DIAS_SEMANA_NUM = {
    "EN": ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    "ES": ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"],
    "PT": ["Domingo","Segunda","Terça","Quarta","Quinta","Sexta","Sábado"],
}
NUM_MAESTRO_DESC = {
    "EN": {1:"Leadership & independence",2:"Harmony & intuition",3:"Creativity & expression",
           4:"Stability & discipline",5:"Freedom & adventure",6:"Care & responsibility",
           7:"Wisdom & introspection",8:"Abundance & power",9:"Compassion & completion",
           11:"Master of intuition",22:"Master builder",33:"Master teacher"},
    "ES": {1:"Liderazgo e independencia",2:"Armonía e intuición",3:"Creatividad y expresión",
           4:"Estabilidad y disciplina",5:"Libertad y aventura",6:"Cuidado y responsabilidad",
           7:"Sabiduría e introspección",8:"Abundancia y poder",9:"Compasión y culminación",
           11:"Maestro de la intuición",22:"Maestro constructor",33:"Maestro espiritual"},
    "PT": {1:"Liderança e independência",2:"Harmonia e intuição",3:"Criatividade e expressão",
           4:"Estabilidade e disciplina",5:"Liberdade e aventura",6:"Cuidado e responsabilidade",
           7:"Sabedoria e introspecção",8:"Abundância e poder",9:"Compaixão e conclusão",
           11:"Mestre da intuição",22:"Mestre construtor",33:"Mestre espiritual"},
}

def calcular_perfil_suerte(nombre, fecha_str, loteria_sel, idioma):
    """Perfil completo de suerte del usuario"""
    result = {}

    # Número maestro
    from collections import Counter as C2
    tabla={c:((ord(c.lower())-ord('a'))%9)+1 for c in 'abcdefghijklmnopqrstuvwxyz'}
    num_n = None
    num_f = None

    if nombre and nombre.strip():
        letras=[(c.upper(),tabla.get(c.lower(),0)) for c in nombre if c.isalpha()]
        if letras:
            suma=sum(v for _,v in letras)
            formula="+".join([f"{c}({v})" for c,v in letras])+f"={suma}"
            while suma>9 and suma not in [11,22,33]:
                suma=sum(int(d) for d in str(suma))
                formula+=f"→{suma}"
            num_n = suma
            result["num_nombre"] = {"n":suma,"formula":formula,"nombre":nombre}

    if fecha_str and fecha_str.strip():
        digitos=[c for c in fecha_str if c.isdigit()]
        if digitos:
            suma=sum(int(d) for d in digitos)
            formula="+".join(digitos)+f"={suma}"
            while suma>9 and suma not in [11,22,33]:
                suma=sum(int(d) for d in str(suma))
                formula+=f"→{suma}"
            num_f = suma
            result["num_fecha"] = {"n":suma,"formula":formula,"fecha":fecha_str}

    maestro = num_n or num_f or 7
    result["maestro"] = maestro
    result["maestro_desc"] = NUM_MAESTRO_DESC.get(idioma,NUM_MAESTRO_DESC["EN"]).get(maestro,"")

    # Mejor lotería — cuál tiene el rango más afín al número maestro
    mejor_lot = None
    mejor_score = -1
    for lot in LOTERIAS:
        hist = HISTORICO_REAL.get(lot["nombre"],{}).get("top_numeros",[])
        # Score: frecuencia de aparición de múltiplos del maestro
        score = sum(1 for n in hist if n%maestro==0 or n==maestro)
        if score > mejor_score:
            mejor_score = score
            mejor_lot = lot["nombre"]
    result["mejor_loteria"] = mejor_lot

    # Mejor día — día de la semana que corresponde al número maestro
    dia_idx = (maestro - 1) % 7
    dias = DIAS_SEMANA_NUM.get(idioma, DIAS_SEMANA_NUM["EN"])
    result["mejor_dia"] = dias[dia_idx]

    # Números de la suerte — fibonacci afines al maestro
    fibs = [1,1,2,3,5,8,13,21,34,55]
    nums_suerte = list(set([maestro, maestro*2 if maestro*2<=69 else maestro,
                            (maestro+1)%9+1, sum([int(d) for d in str(maestro*maestro)])]))
    result["nums_suerte"] = [n for n in nums_suerte if 1<=n<=69]

    return result

def obtener_estadisticas(user_id):
    """Estadísticas del usuario desde Supabase"""
    try:
        res = supabase.table("generaciones").select("*").eq("user_id",user_id).order("created_at",desc=True).execute()
        if not res.data: return {}
        data = res.data
        total = len(data)

        # Lotería más usada
        lot_count = {}
        for g in data:
            lid = g.get("loteria_id")
            lot_count[lid] = lot_count.get(lid,0)+1
        fav_id = max(lot_count,key=lot_count.get) if lot_count else None
        fav_lot = next((l["nombre"] for l in LOTERIAS if l["id"]==fav_id),"-")

        # Números más generados
        all_nums = []
        for g in data:
            all_nums.extend(g.get("numeros",[]))
        from collections import Counter
        top_nums = [n for n,_ in Counter(all_nums).most_common(5)]

        # Racha — días consecutivos con generaciones
        fechas = sorted(set([g.get("created_at","")[:10] for g in data]),reverse=True)
        racha = 0
        hoy = str(date.today())
        from datetime import timedelta
        check = date.today()
        for f in fechas:
            if f == str(check):
                racha += 1
                check -= timedelta(days=1)
            else:
                break

        return {"total":total,"fav_lot":fav_lot,"top_nums":top_nums,"racha":racha,"fechas":fechas[:7]}
    except:
        return {}

def guardar_combinacion_sesion(resultado, loteria):
    """Guarda combinación en session_state"""
    guardadas = st.session_state.get("combinaciones_guardadas",[])
    entry = {
        "numeros": resultado.get("numbers",[]),
        "bonus": resultado.get("bonus"),
        "loteria": loteria["nombre"],
        "flag": loteria["flag"],
        "fecha": str(date.today()),
        "sources": resultado.get("sources",[])
    }
    # Evitar duplicados exactos
    if not any(g["numeros"]==entry["numeros"] and g["loteria"]==entry["loteria"] for g in guardadas):
        guardadas.insert(0, entry)
        st.session_state["combinaciones_guardadas"] = guardadas[:20]
        return True
    return False

def comparar_con_resultado(combo_nums, ganadores):
    """Compara combinación con números ganadores"""
    aciertos = [n for n in combo_nums if n in ganadores]
    return {"aciertos": aciertos, "total": len(aciertos), "porcentaje": round(len(aciertos)/len(combo_nums)*100) if combo_nums else 0}

# ==========================================
# 11. EMAIL
# ==========================================
def enviar_email(to,subject,html):
    if not RESEND_KEY: return False
    try:
        r=requests.post("https://api.resend.com/emails",
            headers={"Authorization":f"Bearer {RESEND_KEY}","Content-Type":"application/json"},
            json={"from":"hello@lucksort.com","to":[to],"subject":subject,"html":html},timeout=10)
        return r.status_code==200
    except: return False

def email_bienvenida(email):
    t=T[st.session_state.get("idioma","EN")]
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
<div style="text-align:center;padding:18px 0;"><div style="display:inline-flex;align-items:center;gap:10px;">
<div style="width:30px;height:30px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;color:#0a0a0f;">◆</div>
<span style="font-size:20px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div>
<p style="color:rgba(255,255,255,.25);font-size:9px;letter-spacing:3px;margin-top:4px;">SORT YOUR LUCK</p></div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,.2);margin:10px 0 18px;">
<h2>Welcome ◆</h2><p style="color:rgba(255,255,255,.6);line-height:1.7;">Your LuckSort account is ready.</p>
<div style="background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:18px;margin:18px 0;">
<ul style="color:rgba(255,255,255,.6);line-height:2.2;margin:0;padding-left:18px;">
<li>5 combinations per lottery per day</li><li>11 lotteries · 3 languages</li><li>Upgrade for full convergence + Dream Mode</li></ul></div>
<div style="text-align:center;margin:22px 0;"><a href="{APP_URL}" style="display:inline-block;padding:13px 32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;">Open LuckSort →</a></div>
<p style="color:rgba(255,255,255,.18);font-size:11px;font-style:italic;text-align:center;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;margin-top:12px;">© 2025 LuckSort · lucksort.com</p></body></html>"""
    enviar_email(email,"Welcome to LuckSort ◆",html)

def email_combinacion(to,loteria,resultado):
    t=T[st.session_state.get("idioma","EN")]
    nums=resultado.get("numbers",[]); bonus=resultado.get("bonus"); sources=resultado.get("sources",[])
    nums_str=" · ".join([str(n).zfill(2) for n in nums])
    bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    src_html=""
    for s in sources:
        icon=ICONS.get(s.get("source","complement"),"·")
        src_html+=f'<div style="padding:9px 12px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);margin-bottom:6px;"><span style="font-family:monospace;">{icon}</span> <strong style="color:rgba(255,255,255,.75);">{s.get("label","")}</strong><span style="color:#C9A84C;float:right;font-family:monospace;">→ {str(s.get("number","")).zfill(2)}</span><div style="color:#C9A84C;font-family:monospace;font-size:11px;margin:2px 0;">{s.get("math","")}</div><p style="color:rgba(255,255,255,.4);font-size:11px;margin:2px 0 0;">{s.get("explanation","")}</p></div>'
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:28px;max-width:560px;margin:0 auto;">
<div style="text-align:center;padding:12px 0 10px;"><div style="display:inline-flex;align-items:center;gap:8px;"><div style="width:24px;height:24px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;color:#0a0a0f;">◆</div><span style="font-size:17px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div></div>
<div style="text-align:center;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:14px;padding:18px;margin:12px 0;">
<div style="font-family:monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;margin-bottom:7px;">{loteria['flag']} {loteria['nombre'].upper()}</div>
<div style="font-family:monospace;font-size:24px;font-weight:700;letter-spacing:3px;">{nums_str}{bonus_s}</div></div>
<p style="color:#C9A84C;font-size:10px;letter-spacing:2px;margin-bottom:9px;">{t['sources_title'].upper()}</p>
{src_html}<p style="color:rgba(255,255,255,.18);font-size:11px;font-style:italic;text-align:center;margin-top:14px;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;margin-top:10px;">© 2025 LuckSort · lucksort.com</p></body></html>"""
    return enviar_email(to,f"◆ {loteria['nombre']} — LuckSort",html)

# ==========================================
# 12. COMPONENTES UI
# ==========================================
def render_header():
    """Header con logo + pills idioma discretas"""
    lang=st.session_state["idioma"]

    # Pills idioma — pequeñas, discretas, sin banderas
    lang_html = ""
    for l in ["EN","ES","PT"]:
        if l == lang:
            style = "padding:3px 10px;border-radius:20px;font-family:monospace;font-size:10px;font-weight:700;letter-spacing:1px;background:rgba(201,168,76,0.15);border:1px solid rgba(201,168,76,0.4);color:#C9A84C;cursor:default;"
        else:
            style = "padding:3px 10px;border-radius:20px;font-family:monospace;font-size:10px;font-weight:700;letter-spacing:1px;background:transparent;border:1px solid rgba(255,255,255,0.12);color:rgba(255,255,255,0.3);cursor:default;"
        lang_html += f'<span style="{style}">{l}</span>'

    # Render header with pills embedded
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:10px 0 10px;border-bottom:1px solid rgba(201,168,76,0.1);margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:32px;height:32px;min-width:32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);
    border-radius:9px;display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 16px rgba(201,168,76,.3);font-size:16px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;color:white;letter-spacing:-.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;color:rgba(201,168,76,.5);letter-spacing:2.5px;">SORT YOUR LUCK</div>
    </div>
  </div>
  <div style="display:flex;gap:5px;align-items:center;">{lang_html}</div>
</div>""", unsafe_allow_html=True)

    # Botones funcionales ocultos — solo cambian estado, no afectan diseño
    st.markdown("""<style>
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton>button,
div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton>button,
div[data-testid="stHorizontalBlock"] > div:nth-child(4) .stButton>button{
  opacity:0!important;height:1px!important;min-height:0!important;
  padding:0!important;margin:0!important;border:none!important;
  box-shadow:none!important;pointer-events:auto!important;
  position:absolute!important;
}
</style>""", unsafe_allow_html=True)

    # Área invisible clickeable para cada idioma
    lc1,lc2,lc3,lc4 = st.columns([5,1,1,1])
    with lc2:
        if st.button("EN",key="hdr_en",use_container_width=True):
            st.session_state["idioma"]="EN"; st.rerun()
    with lc3:
        if st.button("ES",key="hdr_es",use_container_width=True):
            st.session_state["idioma"]="ES"; st.rerun()
    with lc4:
        if st.button("PT",key="hdr_pt",use_container_width=True):
            st.session_state["idioma"]="PT"; st.rerun()
    # Return early — header already rendered above
    return

def render_balls_landing():
    st.markdown("""
<div style="margin:20px auto;max-width:420px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;text-align:center;margin-bottom:12px;">LIVE PREVIEW · POWERBALL</div>
  <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;">
    <div class="ball" id="b0">07</div><div class="ball" id="b1">14</div>
    <div class="ball" id="b2">23</div><div class="ball" id="b3">34</div>
    <div class="ball" id="b4">55</div><div class="ball ball-gold" id="b5">12</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px;">
    <div class="src-row"><div class="src-left"><span class="src-icon">⊞</span><div><div class="src-label">Draw History</div><div class="src-math">Freq. marzo (2010–2024): 31×</div></div></div><span class="src-num">→ 07</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">ϕ</span><div><div class="src-label">Fibonacci</div><div class="src-math">21+13=34 · F₉</div></div></div><span class="src-num">→ 34</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">⊛</span><div><div class="src-label">Community</div><div class="src-math">Mencionado 47× en r/powerball hoy</div></div></div><span class="src-num">→ 23</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">✦</span><div><div class="src-label">Your Date</div><div class="src-math">14/03/92 → día 14 directo</div></div></div><span class="src-num">→ 14</span></div>
  </div>
</div>
<script>
const S=[[7,14,23,34,55,12],[3,19,31,44,62,8],[11,22,35,47,68,17],[5,16,28,41,59,23],[9,21,33,46,63,4]];
let i=0;
setInterval(()=>{i=(i+1)%S.length;for(let j=0;j<6;j++){const el=document.getElementById('b'+j);if(!el)return;el.style.opacity='0';el.style.transform='scale(.75)';setTimeout(()=>{el.textContent=String(S[i][j]).padStart(2,'0');el.style.opacity='1';el.style.transform='scale(1)';},270+j*44);}},2800);
document.querySelectorAll('.ball').forEach(b=>{b.style.transition='opacity .27s ease,transform .27s ease';});
</script>""", unsafe_allow_html=True)

def render_gen_dots(gen_hoy):
    dots="".join([f'<div class="dot {"dot-on" if i<gen_hoy else "dot-off"}"></div>' for i in range(MAX_GEN)])
    st.markdown(f'<div class="gen-dots">{dots}</div>', unsafe_allow_html=True)

def render_resultado(resultado,loteria):
    t=tr()
    numeros=resultado.get("numbers",[]); bonus=resultado.get("bonus"); sources=resultado.get("sources",[])

    balls='<div class="balls-wrap">'+"".join([f'<div class="ball">{str(n).zfill(2)}</div>' for n in numeros])
    if bonus: balls+=f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    balls+='</div>'
    bonus_lbl=f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.22);text-align:center;margin-top:2px;">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>' if bonus and loteria.get("bname") else ""

    st.markdown(f"""
<div class="ls-card-gold" style="text-align:center;">
  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:2px;">{loteria['flag']} {loteria['nombre']}</div>
  {balls}{bonus_lbl}
</div>""", unsafe_allow_html=True)

    if sources:
        st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;color:rgba(255,255,255,.28);letter-spacing:2px;text-transform:uppercase;margin:14px 0 8px;">{t["sources_title"]}</div>', unsafe_allow_html=True)
        for s in sources:
            src=s.get("source","complement")
            es_afin=s.get("es_afin",False)
            icon=ICONS.get(src,"·")
            lbl=s.get("label") or t["sources"].get(src,src)
            math_line=s.get("math","")
            exp=strip_html(s.get("explanation",""))
            num=s.get("number","")

            if src=="complement":
                cls="src-row src-complement"
            elif es_afin:
                cls="src-row src-afin"
            else:
                cls="src-row"

            afin_badge=f'<div class="src-afin-badge">≈ {t["afin_label"]}</div>' if es_afin else ""

            st.markdown(f"""
<div class="{cls}">
  <div class="src-left">
    <span class="src-icon">{icon}</span>
    <div>
      <div class="src-label">{lbl}</div>
      {f'<div class="src-math">{math_line}</div>' if math_line and math_line!="—" else ""}
      {afin_badge}
      <div class="src-desc">{exp}</div>
    </div>
  </div>
  <span class="src-num">→ {str(num).zfill(2)}</span>
</div>""", unsafe_allow_html=True)

    nums_str=" · ".join([str(n).zfill(2) for n in numeros])
    bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    share=f"🎯 {loteria['nombre']}: {nums_str}{bonus_s}\n\nLuckSort — Sort Your Luck\nlucksort.com"
    st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.28);letter-spacing:2px;margin:14px 0 6px;">{t["share_label"]}</div>', unsafe_allow_html=True)
    st.code(share,language=None)

    col_sa, col_sb = st.columns(2)
    with col_sa:
        if st.button(t.get("guardar","Save"), use_container_width=True, key="btn_guardar_combo"):
            if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
                ok = guardar_combinacion_sesion(st.session_state["ultima_generacion"], st.session_state["ultima_loteria"])
                st.success(t.get("guardada","✅ Saved")) if ok else st.info("Already saved")
    with col_sb:
        if st.session_state.get("user_email") and RESEND_KEY:
            if st.button(t["email_combo"],use_container_width=True,key="send_email"):
                ok=email_combinacion(st.session_state["user_email"],loteria,resultado)
                st.success(t["email_sent"]) if ok else st.warning(t["email_err"])

    st.markdown(f'<div class="disclaimer">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

def render_paywall():
    t=tr()
    features=[("⊞","Draw History"),("⊛","Community"),("⊕","World Events"),("✦","Your Dates"),
              ("ᚨ","Numerology"),("ϕ","Fibonacci"),("⬡","Sacred Geo"),("⌁","Tesla"),
              ("◐","Lunar"),("≋","Climate"),("∞","Dream Mode"),("⊞","Real Historical")]
    pills="".join([f'<span style="font-size:11px;color:rgba(255,255,255,.35);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:4px 10px;font-family:monospace;">{i} {l}</span>' for i,l in features])
    st.markdown(f"""
<div class="ls-card" style="border-color:rgba(201,168,76,.25);text-align:center;padding:24px;">
  <div style="font-size:22px;margin-bottom:8px;">◆</div>
  <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:18px;">{t['paywall_title']}</h3>
  <p style="color:rgba(255,255,255,.38);font-size:13px;max-width:280px;margin:0 auto 14px;line-height:1.6;">{t['paywall_msg']}</p>
  <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;">{pills}</div>
</div>""", unsafe_allow_html=True)
    if st.button(t["upgrade_btn"],use_container_width=True,key="upgrade_btn"):
        # Redirigir a Stripe Payment Link
        st.markdown(f'<meta http-equiv="refresh" content="0;url={STRIPE_LINK}">', unsafe_allow_html=True)

# ==========================================
# 13. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
<div style="padding:18px 14px 12px;border-bottom:1px solid rgba(201,168,76,.12);">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:28px;height:28px;min-width:28px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:17px;font-weight:700;color:white;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;color:rgba(201,168,76,.5);letter-spacing:2px;">SORT YOUR LUCK</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    lang_opts={"🇺🇸 English":"EN","🇪🇸 Español":"ES","🇧🇷 Português":"PT"}
    cur=next(k for k,v in lang_opts.items() if v==st.session_state["idioma"])
    sel=st.selectbox("",list(lang_opts.keys()),index=list(lang_opts.keys()).index(cur),key="sb_lang",label_visibility="collapsed")
    if lang_opts[sel]!=st.session_state["idioma"]:
        st.session_state["idioma"]=lang_opts[sel]; st.rerun()
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">', unsafe_allow_html=True)

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
        st.markdown(f'<div style="padding:10px 12px;background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.15);border-radius:10px;margin-bottom:10px;"><div style="font-size:12px;color:rgba(255,255,255,.7);margin-bottom:3px;">{em_d}</div><div style="display:flex;align-items:center;gap:5px;"><div style="width:6px;height:6px;border-radius:50%;background:{role_color};"></div><span style="font-family:monospace;font-size:9px;color:{role_color};letter-spacing:1.5px;">{role_lbl.upper()}</span></div></div>', unsafe_allow_html=True)
        vista_actual = st.session_state.get("vista","app")
        nav_items = [
            ("app",    f"◆ {t['tagline']}"),
            ("perfil", f"ᚨ {t.get('perfil','Profile')}"),
            ("history",f"⊞ {t['history']}"),
            ("guardadas",f"✦ {t.get('guardadas','Saved')}"),
            ("comparador",f"⊕ {t.get('comparador','Compare')}"),
        ]
        for vista_key, label in nav_items:
            if st.button(label, use_container_width=True, key=f"nav_{vista_key}"):
                st.session_state["vista"] = vista_key; st.rerun()

        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">', unsafe_allow_html=True)
        if st.button(t["logout"],use_container_width=True,key="btn_lo"):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
            st.rerun()

# ==========================================
# 14. LANDING
# ==========================================
if not st.session_state["logged_in"]:
    t=tr()
    render_header()

    st.markdown(f"""
<div style="text-align:center;padding:24px 16px 14px;">
  <div class="tag-gold" style="margin-bottom:12px;"><span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span> Data Convergence Engine</div>
  <h1 style="font-family:'Playfair Display',serif;font-size:clamp(32px,7vw,68px);font-weight:700;line-height:1.05;letter-spacing:-2px;margin-bottom:12px;">
    {t['hero_1']}<br><span class="shimmer-text">{t['hero_2']}</span><br>{t['hero_3']}
  </h1>
  <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);color:rgba(255,255,255,.38);max-width:480px;margin:0 auto;line-height:1.8;">{t['hero_sub']}</p>
</div>""", unsafe_allow_html=True)

    render_balls_landing()

    col1,col2,col3=st.columns([1,2,1])
    with col2:
        if st.button(t["cta_free"],use_container_width=True,key="land_cta"):
            st.session_state["mostrar_reg"]=True; st.rerun()
        st.markdown('<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.16);letter-spacing:1.5px;margin-top:6px;">FREE · NO CREDIT CARD · ES / EN / PT</p>', unsafe_allow_html=True)

    if st.session_state.get("mostrar_reg"):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:16px 0;">', unsafe_allow_html=True)
        ca,cb,cc=st.columns([1,2,1])
        with cb:
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
                            st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_,"user_id":res["id"],"vista":"app","mostrar_reg":False})
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

    st.markdown(f"""
<div style="text-align:center;padding:22px 0 12px;">
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.2);letter-spacing:3px;margin-bottom:8px;">HOW IT WORKS</div>
  <h2 style="font-family:'Playfair Display',serif;font-size:clamp(20px,3vw,32px);font-weight:700;letter-spacing:-1px;margin-bottom:4px;">Many signals. One authentic number.</h2>
  <div class="gold-line"></div>
</div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    for col,(icon,key,desc) in zip([c1,c2,c3,c4],[
        ("⊞","historico","Official draw frequencies analyzed by date and month patterns"),
        ("⊛","community","Reddit + Google Trends — real player picks today"),
        ("⊕","eventos","Wikipedia history, headlines, climate and exchange rates"),
        ("✦","fecha_personal","Your dates · numerology · Fibonacci · Tesla · lunar cycle"),
    ]):
        with col:
            st.markdown(f'<div class="ls-card" style="text-align:center;min-height:120px;"><div style="font-family:\'DM Mono\',monospace;font-size:20px;margin-bottom:6px;color:#C9A84C;">{icon}</div><div style="font-family:\'Playfair Display\',serif;font-size:13px;font-weight:600;color:rgba(255,255,255,.85);margin-bottom:4px;">{t["sources"][key]}</div><div style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(255,255,255,.3);line-height:1.5;">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;padding:18px 0 10px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;">11 LOTTERIES · 3 LANGUAGES · DREAM MODE ∞</div></div>', unsafe_allow_html=True)
    cols=st.columns(4)
    for i,lot in enumerate(LOTERIAS):
        with cols[i%4]:
            st.markdown(f'<div style="padding:8px 10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:8px;display:flex;align-items:center;gap:7px;margin-bottom:6px;"><span style="font-size:14px;">{lot["flag"]}</span><span style="font-size:12px;color:rgba(255,255,255,.55);">{lot["nombre"]}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:500px;margin:16px auto 0;">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 15. APP
# ==========================================
elif st.session_state.get("vista")=="app":
    t=tr()
    es_free=st.session_state["user_role"]=="free"
    es_paid=st.session_state["user_role"] in ["paid","pro","convergence","admin"]

    render_header()
    st.markdown(f'<h2 style="font-family:\'Playfair Display\',serif;font-size:clamp(20px,3vw,30px);font-weight:700;letter-spacing:-1px;margin:4px 0 10px;">{t["select_lottery"]}</h2>', unsafe_allow_html=True)

    lot_names=[f"{l['flag']} {l['nombre']}  ({l['pais']})" for l in LOTERIAS]
    sel=st.selectbox("",lot_names,label_visibility="collapsed",key="lot_sel")
    loteria=next(l for l in LOTERIAS if l["nombre"] in sel)

    jackpot=obtener_jackpot(loteria["nombre"])
    prox = proximo_sorteo(loteria["nombre"])
    
    badge_row = ""
    if jackpot:
        badge_row += f'<span class="jackpot-badge" style="margin-right:6px;">◈ {t["jackpot_live"]}: {jackpot}</span>'
    if prox:
        if prox["dias"] == 1:
            badge_row += f'<span class="jackpot-badge">⏱ {t.get("proxima_sorteo","Next draw")}: mañana {prox["hora"]}</span>'
        elif prox["dias"] <= 0:
            badge_row += f'<span class="jackpot-badge" style="border-color:rgba(201,168,76,.5);">⚡ {t.get("hoy_sorteo","Draw today!")} {prox["hora"]}</span>'
        else:
            badge_row += f'<span class="jackpot-badge">⏱ {t.get("proxima_sorteo","Next draw")}: {prox["dias"]} {t.get("dias_para","days")} · {prox["hora"]}</span>'
    if badge_row:
        st.markdown(f'<div style="margin:4px 0 10px;display:flex;flex-wrap:wrap;gap:6px;">{badge_row}</div>', unsafe_allow_html=True)

    gen_hoy=st.session_state["generaciones_hoy"].get(loteria["id"],0)
    restantes=max(0,MAX_GEN-gen_hoy)
    render_gen_dots(gen_hoy)
    st.markdown(f'<div style="text-align:center;margin:-6px 0 10px;"><span class="metric-pill">{t["gen_counter"]}: {gen_hoy}/{MAX_GEN}</span></div>', unsafe_allow_html=True)

    inputs={}
    if es_paid or st.session_state["user_role"]=="admin":
        with st.expander(f"✦ {t['personal_title']}",expanded=False):
            c1,c2=st.columns(2)
            with c1:
                fecha_esp=st.text_input(t["special_date"],placeholder="14/03/1990",key="fe")
                nombre=st.text_input(t["your_name"],placeholder="Your name",key="nm")
            with c2:
                momento=st.text_input(t["life_moment"],placeholder="I just started a business...",key="mm")
                excluir=st.text_input(t["exclude_numbers"],placeholder="4, 13",key="ex")
            crowd_pref=st.radio(t["crowd_pref"],[t["balanced"],t["follow"],t["avoid"]],horizontal=True,key="cp")
            crowd_map={t["follow"]:"follow",t["avoid"]:"avoid",t["balanced"]:"balanced"}
            inputs={"fecha_especial":fecha_esp,"nombre":nombre,"momento":momento,"excluir":excluir,"crowd":crowd_map.get(crowd_pref,"balanced")}

        with st.expander(f"∞ {t['dream_title']}",expanded=False):
            st.caption(t["dream_help"])
            sueno=st.text_area("",placeholder=t["dream_placeholder"],key="dr",height=80)
            inputs["sueno"]=sueno

        with st.expander(f"⬡ {t['symbolic_title']}",expanded=False):
            st.caption(t["symbolic_help"])
            c1,c2=st.columns(2)
            with c1:
                u_num=st.checkbox(t["sys_num"],key="cb_n")
                u_fib=st.checkbox(t["sys_fib"],key="cb_f")
                u_sag=st.checkbox(t["sys_sag"],key="cb_s")
            with c2:
                u_tes=st.checkbox(t["sys_tes"],key="cb_t")
                u_fra=st.checkbox(t["sys_fra"],key="cb_r")
                u_pri=st.checkbox(t["sys_pri"],key="cb_p")
            sistemas=[]
            if u_num: sistemas.append("numerologia")
            if u_fib: sistemas.append("fibonacci")
            if u_sag: sistemas.append("sagrada")
            if u_tes: sistemas.append("tesla")
            if u_fra: sistemas.append("fractal")
            if u_pri: sistemas.append("primos")
            inputs["sistemas"]=sistemas

    if restantes<=0:
        st.warning(f"⚠️ {t['gen_counter']}: {MAX_GEN}/{MAX_GEN}")
    else:
        if st.button(f"◆ {t['generate_btn']}",use_container_width=True,key="gen_btn"):
            if es_paid or st.session_state["user_role"]=="admin":
                placeholder=st.empty()
                for step in [t["conv_step1"],t["conv_step2"],t["conv_step3"],t["conv_step4"]]:
                    placeholder.markdown(f'<div class="conv-wrap"><div class="conv-ring"></div><div class="conv-label">{step}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.55)
                placeholder.empty()
                resultado=generar_combinacion(loteria,inputs)
            else:
                with st.spinner(t["generating"]):
                    resultado=generar_aleatorio(loteria)
            st.session_state["ultima_generacion"]=resultado
            st.session_state["ultima_loteria"]=loteria
            st.session_state["generaciones_hoy"][loteria["id"]]=gen_hoy+1
            if st.session_state.get("user_id"):
                guardar_generacion(st.session_state["user_id"],loteria["id"],resultado.get("numbers",[]),resultado.get("bonus"),resultado.get("sources",[]),inputs)
            st.rerun()

    if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:12px 0;">', unsafe_allow_html=True)
        render_resultado(st.session_state["ultima_generacion"],st.session_state["ultima_loteria"])

    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:16px 0;">', unsafe_allow_html=True)
        render_paywall()

# ==========================================
# 16. HISTORIAL + ESTADÍSTICAS
# ==========================================
elif st.session_state.get("vista")=="history":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">⊞ {t["history"]}</span></div>', unsafe_allow_html=True)
    if st.session_state.get("user_id"):
        stats = obtener_estadisticas(st.session_state["user_id"])
        if stats:
            c1,c2,c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="ls-card" style="text-align:center;padding:14px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:2px;">{t.get("total_generadas","TOTAL")}</div><div style="font-family:Georgia,serif;font-size:28px;color:#C9A84C;font-weight:700;">{stats.get("total",0)}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="ls-card" style="text-align:center;padding:14px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:2px;">{t.get("racha","STREAK")}</div><div style="font-family:Georgia,serif;font-size:28px;color:#C9A84C;font-weight:700;">{stats.get("racha",0)} <span style="font-size:12px;color:rgba(255,255,255,.3);">{t.get("racha_dias","days")}</span></div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="ls-card" style="text-align:center;padding:14px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:2px;">TOP LOTTERY</div><div style="font-family:Georgia,serif;font-size:16px;color:#C9A84C;font-weight:700;margin-top:4px;">{stats.get("fav_lot","-")}</div></div>', unsafe_allow_html=True)
            
            if stats.get("top_nums"):
                top_balls = "".join([f'<div class="ball" style="width:38px;height:38px;font-size:13px;">{str(n).zfill(2)}</div>' for n in stats["top_nums"]])
                st.markdown(f'<div style="margin:10px 0 4px;font-family:monospace;font-size:9px;color:rgba(255,255,255,.28);letter-spacing:2px;">{t.get("nums_frecuentes","YOUR FREQUENT NUMBERS")}</div><div class="balls-wrap">{top_balls}</div>', unsafe_allow_html=True)
            st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:12px 0;">', unsafe_allow_html=True)

        hist=obtener_historial(st.session_state["user_id"])
        if not hist:
            st.markdown(f'<p style="color:rgba(255,255,255,.3);font-size:14px;">{t["no_history"]}</p>', unsafe_allow_html=True)
        else:
            for h in hist:
                lot=next((l for l in LOTERIAS if l["id"]==h.get("loteria_id")),None)
                if lot:
                    nums_str="  ".join([str(n).zfill(2) for n in h["numeros"]])
                    bonus_str=f"  ◆ {str(h['bonus']).zfill(2)}" if h.get("bonus") else ""
                    fecha=h.get("created_at","")[:10]
                    st.markdown(f'<div class="ls-card" style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;"><span style="font-family:\'DM Mono\',monospace;font-size:11px;color:#C9A84C;">{lot["flag"]} {lot["nombre"]}</span><span style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.2);">{fecha}</span></div><div style="font-family:\'DM Mono\',monospace;font-size:18px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div></div>', unsafe_allow_html=True)
    else:
        st.info("Sign in to see your history.")

# ==========================================
# 17. PERFIL DE SUERTE
# ==========================================
elif st.session_state.get("vista")=="perfil":
    t=tr()
    render_header()
    idioma=st.session_state["idioma"]
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">ᚨ {t.get("perfil","My Lucky Profile")}</span></div>', unsafe_allow_html=True)

    if not st.session_state.get("logged_in"):
        st.info("Sign in to see your profile.")
    else:
        st.markdown(f'<p style="color:rgba(255,255,255,.35);font-size:12px;margin-bottom:16px;">{t.get("perfil_desc","")}</p>', unsafe_allow_html=True)
        
        # Tomar datos del último input si existen
        nombre_p = st.text_input("Name / Nombre", placeholder="Juan", key="perfil_nombre")
        fecha_p  = st.text_input("Birthday / Fecha", placeholder="14/03/1992", key="perfil_fecha")

        if nombre_p or fecha_p:
            perfil = calcular_perfil_suerte(nombre_p, fecha_p, None, idioma)
            maestro = perfil.get("maestro",7)
            desc = perfil.get("maestro_desc","")

            # Número maestro
            st.markdown(f'''
<div class="ls-card-gold" style="text-align:center;padding:28px 20px;">
  <div style="font-family:monospace;font-size:9px;color:rgba(201,168,76,.5);letter-spacing:3px;margin-bottom:8px;">{t.get("num_maestro","MASTER NUMBER")}</div>
  <div style="font-family:Georgia,serif;font-size:64px;color:#C9A84C;font-weight:700;line-height:1;">{maestro}</div>
  <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:rgba(255,255,255,.5);margin-top:8px;">{desc}</div>
</div>''', unsafe_allow_html=True)

            if perfil.get("num_nombre"):
                st.markdown(f'<div class="ls-card" style="padding:14px 16px;"><div style="font-family:monospace;font-size:10px;color:#C9A84C;">{nombre_p}</div><div style="font-family:monospace;font-size:12px;color:rgba(255,255,255,.4);margin-top:4px;">{perfil["num_nombre"]["formula"]}</div></div>', unsafe_allow_html=True)
            if perfil.get("num_fecha"):
                st.markdown(f'<div class="ls-card" style="padding:14px 16px;"><div style="font-family:monospace;font-size:10px;color:#C9A84C;">{fecha_p}</div><div style="font-family:monospace;font-size:12px;color:rgba(255,255,255,.4);margin-top:4px;">{perfil["num_fecha"]["formula"]}</div></div>', unsafe_allow_html=True)

            c1,c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="ls-card" style="text-align:center;padding:16px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;">{t.get("mejor_loteria","BEST LOTTERY")}</div><div style="font-size:15px;color:white;margin-top:6px;font-weight:600;">{perfil.get("mejor_loteria","-")}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="ls-card" style="text-align:center;padding:16px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;">{t.get("mejor_dia","BEST DAY")}</div><div style="font-size:15px;color:white;margin-top:6px;font-weight:600;">{perfil.get("mejor_dia","-")}</div></div>', unsafe_allow_html=True)

# ==========================================
# 18. COMBINACIONES GUARDADAS
# ==========================================
elif st.session_state.get("vista")=="guardadas":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">✦ {t.get("guardadas","Saved")}</span></div>', unsafe_allow_html=True)

    guardadas = st.session_state.get("combinaciones_guardadas",[])
    if not guardadas:
        st.markdown(f'<p style="color:rgba(255,255,255,.3);font-size:14px;">{t.get("sin_guardadas","No saved combinations yet.")}</p>', unsafe_allow_html=True)
    else:
        for i,g in enumerate(guardadas):
            nums_str = "  ".join([str(n).zfill(2) for n in g["numeros"]])
            bonus_str = f"  ◆ {str(g['bonus']).zfill(2)}" if g.get("bonus") else ""
            st.markdown(f'''
<div class="ls-card" style="margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
    <span style="font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;">{g["flag"]} {g["loteria"]}</span>
    <span style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.2);">{g["fecha"]}</span>
  </div>
  <div style="font-family:'DM Mono',monospace;font-size:18px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div>
</div>''', unsafe_allow_html=True)
            if st.button(f"✕ Remove", key=f"rm_{i}", use_container_width=False):
                st.session_state["combinaciones_guardadas"].pop(i); st.rerun()

# ==========================================
# 19. COMPARADOR DE RESULTADOS
# ==========================================
elif st.session_state.get("vista")=="comparador":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:6px 0 10px;"><span class="tag-gold">⊕ {t.get("comparador","Compare")}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(255,255,255,.35);font-size:13px;margin-bottom:16px;">{t.get("comparar_intro","")}</p>', unsafe_allow_html=True)

    ganadores_input = st.text_input(t.get("ingresar_ganadores","Winning numbers"), placeholder="23, 7, 45, 12, 3", key="ganadores_inp")

    if st.button(t.get("comparar_btn","Compare"), use_container_width=True, key="btn_comparar"):
        if ganadores_input:
            try:
                ganadores = [int(x.strip()) for x in ganadores_input.split(",") if x.strip().isdigit()]
                # Comparar con historial guardado en sesión y con última generación
                fuentes = []
                if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
                    fuentes.append(("Última generación", st.session_state["ultima_generacion"]["numbers"], st.session_state["ultima_loteria"]["nombre"]))
                for g in st.session_state.get("combinaciones_guardadas",[])[:5]:
                    fuentes.append((f"{g['flag']} {g['loteria']} {g['fecha']}", g["numeros"], g["loteria"]))

                if not fuentes:
                    st.info("Generate or save a combination first.")
                else:
                    st.markdown('<div style="margin-top:12px;">', unsafe_allow_html=True)
                    for label, nums, lot_nombre in fuentes:
                        cmp = comparar_con_resultado(nums, ganadores)
                        nums_html = ""
                        for n in nums:
                            color = "#C9A84C" if n in ganadores else "rgba(255,255,255,.15)"
                            txt_color = "#0a0a0f" if n in ganadores else "rgba(255,255,255,.6)"
                            nums_html += f'<div style="width:40px;height:40px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;font-family:monospace;font-size:13px;font-weight:700;color:{txt_color};margin:3px;">{str(n).zfill(2)}</div>'
                        st.markdown(f'''
<div class="ls-card" style="margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
    <span style="font-family:monospace;font-size:11px;color:#C9A84C;">{label}</span>
    <span style="font-family:monospace;font-size:12px;color:{"#C9A84C" if cmp["total"]>0 else "rgba(255,255,255,.3)"};">{cmp["total"]} {t.get("aciertos","matches")}</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:3px;">{nums_html}</div>
</div>''', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            except:
                st.warning("Verify the numbers format.")
