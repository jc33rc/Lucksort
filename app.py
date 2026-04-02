import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime
import requests, random, json, re, math
from collections import Counter

# ==========================================
# 1. CONFIG + IDIOMA via query_params
# ==========================================
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆", layout="wide",
    initial_sidebar_state="collapsed"
)

# Idioma desde query_params — sin botones que rompan UX
params = st.query_params
if "lang" in params and params["lang"] in ["EN","ES","PT"]:
    st.session_state["idioma"] = params["lang"]

DEFAULTS = {
    "logged_in": False, "user_role": "invitado",
    "user_email": "", "user_id": None,
    "idioma": "EN", "fecha_uso": str(date.today()),
    "generaciones_hoy": {}, "ultima_generacion": None,
    "ultima_loteria": None, "vista": "landing",
    "mostrar_reg": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def set_lang(lang):
    st.session_state["idioma"] = lang
    st.query_params["lang"] = lang
    st.rerun()

# ==========================================
# 2. CSS — definitivo, sin parches
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');

*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:#0a0a0f!important;color:white!important;font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}

/* SIDEBAR */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0d0d1a,#0a0a0f)!important;
  border-right:1px solid rgba(201,168,76,0.15)!important;
}
section[data-testid="stSidebar"]>div:first-child{padding-top:0!important;}

/* BUTTONS — gold */
.stButton>button{
  background:linear-gradient(135deg,#C9A84C,#F5D68A)!important;
  color:#0a0a0f!important;font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;border:none!important;border-radius:10px!important;
  width:100%!important;transition:all .2s!important;
  box-shadow:0 4px 14px rgba(201,168,76,.22)!important;
}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 22px rgba(201,168,76,.36)!important;}

/* INPUTS */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
  background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;
  color:white!important;border-radius:8px!important;
}
.stTextInput>div>div>input:focus{border-color:rgba(201,168,76,.45)!important;}
.stSelectbox>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;color:white!important;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03)!important;border-radius:8px!important;gap:2px!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.4)!important;font-size:13px!important;border-radius:6px!important;}
.stTabs [aria-selected="true"]{color:#C9A84C!important;background:rgba(201,168,76,.1)!important;}

/* RADIO */
.stRadio>div{flex-direction:row!important;flex-wrap:wrap!important;gap:8px!important;}
.stRadio>div>label{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;padding:6px 12px!important;color:rgba(255,255,255,.5)!important;font-size:13px!important;cursor:pointer!important;}

/* EXPANDER */
.stExpander{border:1px solid rgba(201,168,76,.15)!important;border-radius:12px!important;background:rgba(255,255,255,.02)!important;}

/* ANIMATIONS */
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes goldPulse{0%,100%{box-shadow:0 0 12px rgba(201,168,76,.3);transform:scale(1)}50%{box-shadow:0 0 26px rgba(201,168,76,.6);transform:scale(1.05)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes convergeSpin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes nodeAppear{0%{opacity:0;transform:scale(0)}60%{transform:scale(1.2)}100%{opacity:1;transform:scale(1)}}

.shimmer-text{
  background:linear-gradient(90deg,#C9A84C 0%,#F5D68A 35%,#C9A84C 65%,#F5D68A 100%);
  background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;animation:shimmer 3s linear infinite;
}

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
.src-row{display:flex;align-items:flex-start;justify-content:space-between;padding:11px 14px;border-radius:10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);margin-bottom:8px;gap:12px;}
.src-complement{background:rgba(255,255,255,.01);border-color:rgba(255,255,255,.04);}
.src-left{display:flex;align-items:flex-start;gap:10px;flex:1;min-width:0;}
.src-icon{font-size:15px;margin-top:1px;flex-shrink:0;}
.src-label{font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:rgba(255,255,255,.75);}
.src-desc{font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.35);line-height:1.55;margin-top:2px;}
.src-num{font-family:'DM Mono',monospace;font-size:15px;color:#C9A84C;font-weight:700;flex-shrink:0;margin-top:1px;}
.src-complement .src-num{color:rgba(255,255,255,.25);}

/* LANG PILLS */
.lang-pill{display:inline-flex;gap:5px;align-items:center;}
.lp{padding:3px 10px;border-radius:20px;font-family:'DM Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1px;text-decoration:none;transition:all .2s;}
.lp-on{background:rgba(201,168,76,.15);border:1px solid rgba(201,168,76,.4);color:#C9A84C;}
.lp-off{background:transparent;border:1px solid rgba(255,255,255,.1);color:rgba(255,255,255,.3);}

/* MISC */
.tag-gold{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;}
.metric-pill{display:inline-block;padding:4px 12px;border-radius:20px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.18);font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.jackpot-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.disclaimer{background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:13px 15px;font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,.3);line-height:1.65;font-style:italic;margin-top:16px;}
.gold-line{width:36px;height:2px;margin:10px auto;background:linear-gradient(90deg,transparent,#C9A84C,transparent);}
.hr{border:none;border-top:1px solid rgba(255,255,255,.06);margin:12px 0;}

/* CONVERGENCE ANIMATION */
.conv-wrap{text-align:center;padding:20px 0;}
.conv-ring{width:80px;height:80px;border-radius:50%;border:2px solid rgba(201,168,76,.3);border-top-color:#C9A84C;animation:convergeSpin 1s linear infinite;margin:0 auto 14px;}
.conv-step{font-family:'DM Mono',monospace;font-size:11px;color:rgba(255,255,255,.4);letter-spacing:1px;margin:4px 0;}
.conv-num{color:#C9A84C;font-weight:700;}

/* DREAM BOX */
.dream-box{background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.15);border-radius:12px;padding:16px;margin-bottom:14px;}

@media(max-width:768px){
  .ball{width:44px;height:44px;font-size:14px;}
  .src-desc{font-size:10px;}
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CREDENCIALES
# ==========================================
try:
    GROQ_KEY    = st.secrets["GROQ_API_KEY"]
    SB_URL      = st.secrets["SUPABASE_URL"]
    SB_KEY      = st.secrets["SUPABASE_KEY"]
    RESEND_KEY  = st.secrets.get("RESEND_API_KEY","")
    ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL","admin@lucksort.com")
    ADMIN_PASS  = st.secrets.get("ADMIN_PASS","admin123")
    NEWS_KEY    = st.secrets.get("NEWS_API_KEY","")
    LOTTERY_KEY = st.secrets.get("LOTTERYDATA_KEY","")
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

# ==========================================
# 5. TRADUCCIONES
# ==========================================
T = {
"EN":{
    "tagline":"Sort Your Luck",
    "hero_1":"Your numbers,","hero_2":"backed by the","hero_3":"world's signals.",
    "hero_sub":"We gather real data — historical draws, community picks, today's headlines, and your personal dates — converged into combinations that mean something.",
    "cta_free":"Start Free","login":"Sign In","register":"Create Account","logout":"Sign Out",
    "email":"Email","password":"Password","confirm_pass":"Confirm Password",
    "btn_login":"Sign In","btn_register":"Create Free Account",
    "plan":"Plan","free":"Free","paid":"Convergence",
    "select_lottery":"Select Lottery","jackpot_live":"Live Jackpot",
    "personal_title":"Personal Signals","special_date":"Special date (birthday, anniversary...)",
    "your_name":"Your name","life_moment":"Something happening in your life right now",
    "exclude_numbers":"Numbers to exclude (comma separated)",
    "dream_title":"Dream Mode 🌙","dream_placeholder":"Tell me your dream... I saw water, the number 7, a golden door...",
    "dream_help":"Describe your dream and we'll extract numbers from its symbols",
    "symbolic_title":"Symbolic Systems","symbolic_help":"Select systems to include",
    "sys_num":"Numerology","sys_fib":"Fibonacci","sys_sag":"Sacred Geometry (φ,π)",
    "sys_tes":"Tesla (3·6·9)","sys_fra":"Fractals",
    "crowd_pref":"Crowd","follow":"Follow","avoid":"Avoid","balanced":"Balanced",
    "generate_btn":"Generate Combination","generating":"Converging data sources...",
    "conv_step1":"Analyzing world events...","conv_step2":"Reading community signals...",
    "conv_step3":"Computing symbolic systems...","conv_step4":"Converging into your numbers...",
    "sources_title":"Where each number comes from",
    "gen_counter":"Today","email_combo":"Send to my email",
    "email_sent":"✅ Sent!","email_err":"⚠️ Configure Resend first.",
    "share_label":"Copy & share:",
    "disclaimer":"We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
    "paywall_title":"Convergence Plan","upgrade_btn":"Upgrade — $9.99/month",
    "paywall_msg":"Unlock data-driven generation with historical analysis, community intelligence, world events, personal dates, symbolic systems and Dream Mode.",
    "history":"My History","no_history":"No combinations yet.",
    "login_err":"❌ Incorrect credentials.","pass_mismatch":"⚠️ Passwords don't match.",
    "pass_short":"⚠️ Minimum 6 characters.","email_invalid":"⚠️ Invalid email.",
    "email_exists":"⚠️ Email already registered.",
    "sources":{"historico":"Draw History","community":"Community","eventos":"World Events",
               "fecha_personal":"Your Date","numerologia":"Numerology","fibonacci":"Fibonacci",
               "sagrada":"Sacred Geometry","tesla":"Tesla 3·6·9","fractal":"Fractal",
               "sueno":"Dream","complement":"Complement"},
    "icons":{"historico":"📊","community":"👥","eventos":"🌍","fecha_personal":"✦",
             "numerologia":"🔢","fibonacci":"🌀","sagrada":"⬡","tesla":"⚡",
             "fractal":"🔮","sueno":"🌙","complement":"⚪"},
},
"ES":{
    "tagline":"Ordena tu Suerte",
    "hero_1":"Tus números,","hero_2":"respaldados por","hero_3":"las señales del mundo.",
    "hero_sub":"Recopilamos datos reales — sorteos históricos, picks de la comunidad, titulares de hoy y tus fechas personales — convergidos en combinaciones con significado.",
    "cta_free":"Empezar Gratis","login":"Entrar","register":"Crear Cuenta","logout":"Cerrar Sesión",
    "email":"Correo","password":"Contraseña","confirm_pass":"Confirmar contraseña",
    "btn_login":"Entrar","btn_register":"Crear Cuenta Gratis",
    "plan":"Plan","free":"Gratis","paid":"Convergencia",
    "select_lottery":"Selecciona tu Lotería","jackpot_live":"Jackpot en vivo",
    "personal_title":"Señales personales","special_date":"Fecha especial (cumpleaños, aniversario...)",
    "your_name":"Tu nombre","life_moment":"Algo que está pasando en tu vida ahora",
    "exclude_numbers":"Números a excluir (separados por coma)",
    "dream_title":"Modo Sueños 🌙","dream_placeholder":"Cuéntame tu sueño... Vi agua, el número 7, una puerta dorada...",
    "dream_help":"Describe tu sueño y extraeremos números de sus símbolos",
    "symbolic_title":"Sistemas simbólicos","symbolic_help":"Selecciona sistemas a incluir",
    "sys_num":"Numerología","sys_fib":"Fibonacci","sys_sag":"Geometría Sagrada (φ,π)",
    "sys_tes":"Tesla (3·6·9)","sys_fra":"Fractales",
    "crowd_pref":"Comunidad","follow":"Seguir","avoid":"Evitar","balanced":"Balanceado",
    "generate_btn":"Generar Combinación","generating":"Convergiendo fuentes de datos...",
    "conv_step1":"Analizando eventos del mundo...","conv_step2":"Leyendo señales de la comunidad...",
    "conv_step3":"Calculando sistemas simbólicos...","conv_step4":"Convergiendo en tus números...",
    "sources_title":"De dónde viene cada número",
    "gen_counter":"Hoy","email_combo":"Enviar a mi correo",
    "email_sent":"✅ ¡Enviado!","email_err":"⚠️ Configura Resend primero.",
    "share_label":"Copia y comparte:",
    "disclaimer":"Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
    "paywall_title":"Plan Convergencia","upgrade_btn":"Actualizar — $9.99/mes",
    "paywall_msg":"Desbloquea la generación basada en datos con análisis histórico, inteligencia de comunidad, eventos mundiales, fechas personales, sistemas simbólicos y Modo Sueños.",
    "history":"Mi Historial","no_history":"Aún no has generado combinaciones.",
    "login_err":"❌ Credenciales incorrectas.","pass_mismatch":"⚠️ Las contraseñas no coinciden.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ El correo ya está registrado.",
    "sources":{"historico":"Histórico","community":"Comunidad","eventos":"Eventos",
               "fecha_personal":"Tu Fecha","numerologia":"Numerología","fibonacci":"Fibonacci",
               "sagrada":"Geometría Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal",
               "sueno":"Sueño","complement":"Complemento"},
    "icons":{"historico":"📊","community":"👥","eventos":"🌍","fecha_personal":"✦",
             "numerologia":"🔢","fibonacci":"🌀","sagrada":"⬡","tesla":"⚡",
             "fractal":"🔮","sueno":"🌙","complement":"⚪"},
},
"PT":{
    "tagline":"Organize sua Sorte",
    "hero_1":"Seus números,","hero_2":"respaldados pelos","hero_3":"sinais do mundo.",
    "hero_sub":"Coletamos dados reais — histórico de sorteios, picks da comunidade, manchetes de hoje e suas datas pessoais — convergidos em combinações com significado.",
    "cta_free":"Começar Grátis","login":"Entrar","register":"Criar Conta","logout":"Sair",
    "email":"Email","password":"Senha","confirm_pass":"Confirmar senha",
    "btn_login":"Entrar","btn_register":"Criar Conta Grátis",
    "plan":"Plano","free":"Grátis","paid":"Convergência",
    "select_lottery":"Selecione sua Loteria","jackpot_live":"Jackpot ao vivo",
    "personal_title":"Sinais pessoais","special_date":"Data especial (aniversário...)",
    "your_name":"Seu nome","life_moment":"Algo acontecendo na sua vida agora",
    "exclude_numbers":"Números a excluir (separados por vírgula)",
    "dream_title":"Modo Sonhos 🌙","dream_placeholder":"Me conte seu sonho... Vi água, o número 7, uma porta dourada...",
    "dream_help":"Descreva seu sonho e extrairemos números dos seus símbolos",
    "symbolic_title":"Sistemas simbólicos","symbolic_help":"Selecione sistemas a incluir",
    "sys_num":"Numerologia","sys_fib":"Fibonacci","sys_sag":"Geometria Sagrada (φ,π)",
    "sys_tes":"Tesla (3·6·9)","sys_fra":"Fractais",
    "crowd_pref":"Comunidade","follow":"Seguir","avoid":"Evitar","balanced":"Balanceado",
    "generate_btn":"Gerar Combinação","generating":"Convergindo fontes de dados...",
    "conv_step1":"Analisando eventos do mundo...","conv_step2":"Lendo sinais da comunidade...",
    "conv_step3":"Calculando sistemas simbólicos...","conv_step4":"Convergindo em seus números...",
    "sources_title":"De onde vem cada número",
    "gen_counter":"Hoje","email_combo":"Enviar para meu email",
    "email_sent":"✅ Enviado!","email_err":"⚠️ Configure o Resend primeiro.",
    "share_label":"Copie e compartilhe:",
    "disclaimer":"Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
    "paywall_title":"Plano Convergência","upgrade_btn":"Atualizar — $9.99/mês",
    "paywall_msg":"Desbloqueie a geração baseada em dados com análise histórica, inteligência da comunidade, eventos mundiais, datas pessoais, sistemas simbólicos e Modo Sonhos.",
    "history":"Meu Histórico","no_history":"Ainda não gerou combinações.",
    "login_err":"❌ Credenciais incorretas.","pass_mismatch":"⚠️ As senhas não coincidem.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ Email já cadastrado.",
    "sources":{"historico":"Histórico","community":"Comunidade","eventos":"Eventos",
               "fecha_personal":"Sua Data","numerologia":"Numerologia","fibonacci":"Fibonacci",
               "sagrada":"Geometria Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal",
               "sueno":"Sonho","complement":"Complemento"},
    "icons":{"historico":"📊","community":"👥","eventos":"🌍","fecha_personal":"✦",
             "numerologia":"🔢","fibonacci":"🌀","sagrada":"⬡","tesla":"⚡",
             "fractal":"🔮","sueno":"🌙","complement":"⚪"},
},
}
def tr(): return T[st.session_state["idioma"]]

# ==========================================
# 6. SISTEMAS SIMBÓLICOS
# ==========================================
PHI = 1.6180339887
PI  = 3.14159265358979

def fib_rango(mn,mx):
    out=[];a,b=1,1
    while a<=mx:
        if a>=mn: out.append(a)
        a,b=b,a+b
    return out

def sagrada_rango(mn,mx):
    nums=set()
    for i in range(1,50):
        for v in [int(PHI*i),int(PI*i),round(PHI**2*i)]:
            if mn<=v<=mx: nums.add(v)
    acum=0
    for d in [3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6]:
        acum+=d
        if mn<=acum<=mx: nums.add(acum)
    return sorted(nums)

def tesla_rango(mn,mx):
    return [n for n in range(mn,mx+1) if n%3==0]

def num_nombre(nombre):
    if not nombre: return None
    tabla={c:((ord(c.lower())-ord('a'))%9)+1 for c in 'abcdefghijklmnopqrstuvwxyz'}
    suma=sum(tabla.get(c.lower(),0) for c in nombre if c.isalpha())
    while suma>9 and suma not in [11,22,33]:
        suma=sum(int(d) for d in str(suma))
    return suma

def num_fecha(fecha_str):
    if not fecha_str: return None
    try:
        digitos=[c for c in fecha_str if c.isdigit()]
        suma=sum(int(d) for d in digitos)
        while suma>9 and suma not in [11,22,33]:
            suma=sum(int(d) for d in str(suma))
        return suma
    except: return None

def nums_de_fecha(fecha_str,mn,mx):
    nums=[]
    if not fecha_str: return nums
    partes=[x for x in re.split(r'[-/.]',fecha_str) if x.isdigit()]
    for p in partes:
        v=int(p)
        if mn<=v<=mx: nums.append(v)
        if len(p)==4:
            s=int(p[-2:])
            if mn<=s<=mx: nums.append(s)
        sd=sum(int(d) for d in p)
        if mn<=sd<=mx: nums.append(sd)
    return list(set(nums))

def calcular_simbolicos(loteria,inputs):
    mn,mx=loteria["min"],loteria["max"]
    sistemas=inputs.get("sistemas",[])
    result={}
    if "numerologia" in sistemas:
        nn=num_nombre(inputs.get("nombre",""))
        nf=num_fecha(inputs.get("fecha_especial",""))
        candidates=[n for n in [nn,nf,11,22,33] if n and mn<=n<=mx]
        result["numerologia"]={"numeros":list(set(candidates)),"maestro_nombre":nn,"maestro_fecha":nf}
    if "fibonacci" in sistemas:
        result["fibonacci"]={"numeros":fib_rango(mn,mx)}
    if "sagrada" in sistemas:
        result["sagrada"]={"numeros":sagrada_rango(mn,mx)[:20]}
    if "tesla" in sistemas:
        result["tesla"]={"numeros":tesla_rango(mn,mx)[:15]}
    return result

# ==========================================
# 7. APIS — con caché y fallbacks silenciosos
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
            evts=r.json().get("events",[])[:6]
            res=[{"year":e.get("year"),"text":e.get("text","")[:160]} for e in evts]
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

def obtener_reddit(loteria):
    tipo=f"reddit_{loteria['id']}_{date.today()}"
    c=get_cache(tipo)
    if c: return c
    headers={"User-Agent":"LuckSort/1.0"}
    mn,mx=loteria["min"],loteria["max"]
    nums=[]
    for sub in loteria.get("reddit",["lottery"])[:2]:
        try:
            r=requests.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=15",headers=headers,timeout=8)
            if r.status_code==200:
                posts=r.json().get("data",{}).get("children",[])
                for p in posts:
                    texto=p.get("data",{}).get("title","")+p.get("data",{}).get("selftext","")
                    for n in re.findall(r'\b(\d{1,2})\b',texto):
                        v=int(n)
                        if mn<=v<=mx: nums.append(v)
        except: pass
    if not nums:
        base=[7,11,14,17,21,23,27,32,38,42,3,8,13,19,29,33]
        nums=[n for n in base if mn<=n<=mx]
    top=[n for n,_ in Counter(nums).most_common(10)]
    set_cache(tipo,top,"reddit"); return top

def obtener_trends():
    c=get_cache("trends")
    if c: return c
    try:
        from trendspyg import download_google_trends_rss
        trends=download_google_trends_rss(geo='US')
        nums=[]
        for t in trends[:10]:
            for n in re.findall(r'\b(\d{1,2})\b',t.get('trend','')):
                if 1<=int(n)<=70: nums.append(int(n))
        if nums: set_cache("trends",nums[:15],"trendspyg"); return nums[:15]
    except: pass
    return []

def obtener_jackpot(nombre):
    tipo=f"jackpot_{nombre}"
    c=get_cache(tipo)
    if c: return c
    try:
        slug={"Powerball":"powerball","Mega Millions":"megamillions","EuroMillions":"euromillions","EuroJackpot":"eurojackpot"}.get(nombre)
        if not slug: return None
        r=requests.get(f"https://lotterydata.io/api/{slug}/latest",timeout=6)
        if r.status_code==200:
            data=r.json()
            jackpot=data.get("data",[{}])[0].get("jackpot") or data.get("jackpot")
            if jackpot: set_cache(tipo,jackpot,"lotterydata"); return jackpot
    except: pass
    return None

# ==========================================
# 8. GENERACIÓN GROQ
# ==========================================
def generar_combinacion(loteria,inputs):
    lang=st.session_state["idioma"]
    lang_full={"EN":"English","ES":"Spanish","PT":"Portuguese"}[lang]
    hoy=datetime.now()

    efem_hoy=obtener_efemerides(hoy.month,hoy.day)
    noticias=obtener_noticias()
    crowd_reddit=obtener_reddit(loteria)
    crowd_trends=obtener_trends()

    efem_personal=[]
    nums_fecha=[]
    fecha_esp=inputs.get("fecha_especial","")
    if fecha_esp:
        partes=[x for x in re.split(r'[-/.]',fecha_esp) if x.isdigit()]
        if len(partes)>=2:
            try:
                d,m=int(partes[0]),int(partes[1])
                if 1<=d<=31 and 1<=m<=12:
                    efem_personal=obtener_efemerides(m,d)
                    nums_fecha=nums_de_fecha(fecha_esp,loteria["min"],loteria["max"])
            except: pass

    simbolicos=calcular_simbolicos(loteria,inputs)
    sistemas_sel=inputs.get("sistemas",[])
    sueno=inputs.get("sueno","")

    excluir=[]
    if inputs.get("excluir"):
        try: excluir=[int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    bonus_inst=f"1 {loteria['bname']} (1-{loteria['bmax']})" if loteria["bonus"] else "no bonus"

    prompt=f"""You are LuckSort's convergence engine. Generate a {loteria['nombre']} combination.

RULES:
- {loteria['n']} unique numbers ({loteria['min']}-{loteria['max']}) + {bonus_inst}
- Exclude: {excluir if excluir else 'none'}
- Crowd: {inputs.get('crowd','balanced')} (follow=use community numbers, avoid=avoid them)

DATA SIGNALS:
1. TODAY ({hoy.strftime('%B %d')}): {json.dumps(efem_hoy[:3],ensure_ascii=False)}
2. USER DATE ({fecha_esp}): events={json.dumps(efem_personal[:2],ensure_ascii=False)}, nums={nums_fecha}
3. NEWS: {json.dumps(noticias[:3],ensure_ascii=False)}
4. COMMUNITY: reddit={crowd_reddit[:8]}, trends={crowd_trends[:5]}
5. SYMBOLIC (ONLY USE IF IN THIS LIST: {sistemas_sel}):
{json.dumps(simbolicos,ensure_ascii=False)}
6. DREAM (if provided): "{sueno}"

CRITICAL:
- Only use a symbolic system if it appears in the selected list {sistemas_sel}
- If fibonacci NOT selected → never use fibonacci source
- If tesla NOT selected → never use tesla source
- Each number needs a REAL specific signal from data above
- Use "complement" only if truly no signal found
- Be SPECIFIC: minimum 15 words per explanation, cite exact data point
- Explanations must be in {lang_full}

Return ONLY valid JSON:
{{
  "numbers": [{loteria['n']} integers],
  "bonus": {f'integer 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources": [
    {{"number": N, "source": "historico|community|eventos|fecha_personal|numerologia|fibonacci|sagrada|tesla|fractal|sueno|complement",
      "label": "short name in {lang_full}",
      "explanation": "specific real reason 15+ words in {lang_full}"}}
  ]
}}"""

    try:
        resp=groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"LuckSort engine. Return ONLY valid JSON. Respond in {lang_full}."},
                {"role":"user","content":prompt}
            ],
            temperature=0.65,max_tokens=1400
        )
        raw=resp.choices[0].message.content.strip()
        if "```" in raw: raw=raw.split("```")[1].replace("json","").strip()
        res=json.loads(raw)

        nums=[n for n in res.get("numbers",[]) if loteria["min"]<=n<=loteria["max"] and n not in excluir]
        pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in nums and n not in excluir]
        while len(nums)<loteria["n"] and pool:
            p=random.choice(pool); nums.append(p); pool.remove(p)
        res["numbers"]=list(dict.fromkeys(nums))[:loteria["n"]]

        if loteria["bonus"] and res.get("bonus"):
            b=res["bonus"]
            if not isinstance(b,int) or not (1<=b<=loteria["bmax"]):
                res["bonus"]=random.randint(1,loteria["bmax"])
        return res
    except:
        return generar_fallback(loteria,excluir)

def generar_fallback(loteria,excluir=[]):
    pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in excluir]
    nums=random.sample(pool,min(loteria["n"],len(pool)))
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    sources=[{"number":n,"source":"complement","label":"Random","explanation":"No specific signal found for this position today"} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","label":"Random","explanation":"Randomly generated"})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

# ==========================================
# 9. SUPABASE
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

# ==========================================
# 10. EMAIL
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
<div style="text-align:center;padding:20px 0;">
<div style="display:inline-flex;align-items:center;gap:10px;">
<div style="width:32px;height:32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#0a0a0f;">◆</div>
<span style="font-size:22px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div>
<p style="color:rgba(255,255,255,.25);font-size:9px;letter-spacing:3px;margin-top:4px;">SORT YOUR LUCK</p></div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,.2);margin:10px 0 20px;">
<h2>Welcome ◆</h2>
<p style="color:rgba(255,255,255,.6);line-height:1.7;">Your LuckSort account is ready.</p>
<div style="background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:20px;margin:20px 0;">
<ul style="color:rgba(255,255,255,.6);line-height:2.2;margin:0;padding-left:18px;">
<li>5 combinations per lottery per day</li><li>11 lotteries · 3 languages</li><li>Upgrade for full convergence</li>
</ul></div>
<div style="text-align:center;margin:24px 0;">
<a href="{APP_URL}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;">Open LuckSort →</a></div>
<p style="color:rgba(255,255,255,.18);font-size:11px;font-style:italic;text-align:center;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;margin-top:16px;">© 2025 LuckSort · lucksort.com</p>
</body></html>"""
    enviar_email(email,"Welcome to LuckSort ◆",html)

def email_combinacion(to,loteria,resultado):
    t=T[st.session_state.get("idioma","EN")]
    nums=resultado.get("numbers",[])
    bonus=resultado.get("bonus")
    sources=resultado.get("sources",[])
    nums_str=" · ".join([str(n).zfill(2) for n in nums])
    bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    src_html=""
    for s in sources:
        icon=t["icons"].get(s.get("source","complement"),"⚪")
        src_html+=f'<div style="padding:9px 12px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);margin-bottom:6px;"><span>{icon} <strong style="color:rgba(255,255,255,.75);">{s.get("label","")}</strong> <span style="color:#C9A84C;float:right;">→ {str(s.get("number","")).zfill(2)}</span></span><p style="color:rgba(255,255,255,.4);font-size:11px;margin:3px 0 0;">{s.get("explanation","")}</p></div>'
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
<div style="text-align:center;padding:16px 0 12px;"><div style="display:inline-flex;align-items:center;gap:8px;"><div style="width:26px;height:26px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;color:#0a0a0f;">◆</div><span style="font-size:18px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div></div>
<div style="text-align:center;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:14px;padding:20px;margin:16px 0;">
<div style="font-family:monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;margin-bottom:8px;">{loteria['flag']} {loteria['nombre'].upper()}</div>
<div style="font-family:monospace;font-size:26px;font-weight:700;letter-spacing:4px;">{nums_str}{bonus_s}</div></div>
<p style="color:#C9A84C;font-size:10px;letter-spacing:2px;margin-bottom:10px;">{t['sources_title'].upper()}</p>
{src_html}
<p style="color:rgba(255,255,255,.2);font-size:11px;font-style:italic;text-align:center;margin-top:18px;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;margin-top:14px;">© 2025 LuckSort · lucksort.com</p>
</body></html>"""
    return enviar_email(to,f"◆ {loteria['nombre']} — LuckSort",html)

# ==========================================
# 11. COMPONENTES UI
# ==========================================
def render_header(show_lang_buttons=False):
    """Header con logo — siempre visible. Lang pills solo decorativas."""
    lang=st.session_state["idioma"]
    en_on="lp lp-on" if lang=="EN" else "lp lp-off"
    es_on="lp lp-on" if lang=="ES" else "lp lp-off"
    pt_on="lp lp-on" if lang=="PT" else "lp lp-off"
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:14px 0 10px;border-bottom:1px solid rgba(201,168,76,0.1);margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:32px;height:32px;min-width:32px;
    background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 16px rgba(201,168,76,.32);font-size:16px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
      color:white;letter-spacing:-.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;
      color:rgba(201,168,76,.5);letter-spacing:2.5px;">SORT YOUR LUCK</div>
    </div>
  </div>
  <div class="lang-pill">
    <span class="{en_on}">EN</span>
    <span class="{es_on}">ES</span>
    <span class="{pt_on}">PT</span>
  </div>
</div>
<div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.2);
margin-bottom:4px;">↑ {'Change in sidebar' if lang=='EN' else 'Cambiar en menú' if lang=='ES' else 'Mudar no menu'}</div>
""", unsafe_allow_html=True)

def render_balls_landing():
    st.markdown("""
<div style="margin:22px auto;max-width:420px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;text-align:center;margin-bottom:12px;">LIVE PREVIEW · POWERBALL</div>
  <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;">
    <div class="ball" id="b0">07</div><div class="ball" id="b1">14</div>
    <div class="ball" id="b2">23</div><div class="ball" id="b3">34</div>
    <div class="ball" id="b4">55</div><div class="ball ball-gold" id="b5">12</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px;">
    <div class="src-row"><div class="src-left"><span class="src-icon">📊</span><div><div class="src-label">Draw History</div><div class="src-desc">Appeared 31× in March draws (2010–2024)</div></div></div><span class="src-num">→ 07</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">🌀</span><div><div class="src-label">Fibonacci</div><div class="src-desc">34 is a Fibonacci number (21+13=34)</div></div></div><span class="src-num">→ 34</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">👥</span><div><div class="src-label">Community</div><div class="src-desc">Top picked on r/powerball this week</div></div></div><span class="src-num">→ 23</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">✦</span><div><div class="src-label">Your Date</div><div class="src-desc">Day extracted from birthday Mar 14</div></div></div><span class="src-num">→ 14</span></div>
  </div>
</div>
<script>
const S=[[7,14,23,34,55,12],[3,19,31,44,62,8],[11,22,35,47,68,17],[5,16,28,41,59,23],[9,21,33,46,63,4]];
let i=0;
setInterval(()=>{i=(i+1)%S.length;for(let j=0;j<6;j++){const el=document.getElementById('b'+j);if(!el)return;el.style.opacity='0';el.style.transform='scale(.75)';setTimeout(()=>{el.textContent=String(S[i][j]).padStart(2,'0');el.style.opacity='1';el.style.transform='scale(1)';},270+j*44);}},2800);
document.querySelectorAll('.ball').forEach(b=>{b.style.transition='opacity .27s ease,transform .27s ease';});
</script>""", unsafe_allow_html=True)

def render_convergence_animation(t):
    """Animación mientras Groq procesa"""
    placeholder=st.empty()
    steps=[t["conv_step1"],t["conv_step2"],t["conv_step3"],t["conv_step4"]]
    import time
    for step in steps:
        placeholder.markdown(f"""
<div class="conv-wrap">
  <div class="conv-ring"></div>
  <div class="conv-step">{step}</div>
</div>""", unsafe_allow_html=True)
        time.sleep(0.7)
    placeholder.empty()

def render_gen_dots(gen_hoy):
    dots=""
    for i in range(MAX_GEN):
        cls="dot dot-on" if i<gen_hoy else "dot dot-off"
        dots+=f'<div class="{cls}"></div>'
    st.markdown(f'<div class="gen-dots">{dots}</div>', unsafe_allow_html=True)

def render_resultado(resultado,loteria):
    t=tr()
    numeros=resultado.get("numbers",[])
    bonus=resultado.get("bonus")
    sources=resultado.get("sources",[])

    balls='<div class="balls-wrap">'
    for n in numeros: balls+=f'<div class="ball">{str(n).zfill(2)}</div>'
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
            icon=t["icons"].get(src,"⚪")
            lbl=s.get("label") or t["sources"].get(src,src)
            exp=s.get("explanation","")
            num=s.get("number","")
            cls="src-row src-complement" if src=="complement" else "src-row"
            st.markdown(f'<div class="{cls}"><div class="src-left"><span class="src-icon">{icon}</span><div><div class="src-label">{lbl}</div><div class="src-desc">{exp}</div></div></div><span class="src-num">→ {str(num).zfill(2)}</span></div>', unsafe_allow_html=True)

    # Acciones
    nums_str=" · ".join([str(n).zfill(2) for n in numeros])
    bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    share=f"🎯 {loteria['nombre']}: {nums_str}{bonus_s}\n\nLuckSort — Sort Your Luck\nlucksort.com"

    st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.28);letter-spacing:2px;margin:14px 0 6px;">{t["share_label"]}</div>', unsafe_allow_html=True)
    st.code(share,language=None)

    if st.session_state.get("user_email") and RESEND_KEY:
        if st.button(t["email_combo"],use_container_width=True,key="send_email"):
            ok=email_combinacion(st.session_state["user_email"],loteria,resultado)
            st.success(t["email_sent"]) if ok else st.warning(t["email_err"])

    st.markdown(f'<div class="disclaimer">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

def render_paywall():
    t=tr()
    st.markdown(f"""
<div class="ls-card" style="border-color:rgba(201,168,76,.25);text-align:center;padding:26px;">
  <div style="font-size:24px;margin-bottom:10px;">◆</div>
  <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:19px;">{t['paywall_title']}</h3>
  <p style="color:rgba(255,255,255,.38);font-size:13px;max-width:300px;margin:0 auto 16px;line-height:1.65;">{t['paywall_msg']}</p>
  <div style="display:flex;gap:7px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;">
    {"".join([f'<span style="font-size:11px;color:rgba(255,255,255,.35);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:4px 10px;">{i} {l}</span>' for l,i in [("Draw History","📊"),("Community","👥"),("World Events","🌍"),("Your Dates","✦"),("Numerology","🔢"),("Fibonacci","🌀"),("Sacred Geo","⬡"),("Tesla","⚡"),("Dream Mode","🌙")]])}
  </div>
</div>""", unsafe_allow_html=True)
    if st.button(t["upgrade_btn"],use_container_width=True,key="upgrade_btn"):
        pass

# ==========================================
# 12. SIDEBAR
# ==========================================
with st.sidebar:
    # Logo sidebar
    st.markdown("""
<div style="padding:20px 14px 12px;border-bottom:1px solid rgba(201,168,76,.12);">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:30px;height:30px;min-width:30px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:18px;font-weight:700;color:white;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;color:rgba(201,168,76,.5);letter-spacing:2px;">SORT YOUR LUCK</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Idioma en sidebar — selectbox limpio
    st.markdown('<div style="padding:8px 0 4px;">', unsafe_allow_html=True)
    lang_options={"🇺🇸 English":"EN","🇪🇸 Español":"ES","🇧🇷 Português":"PT"}
    current=next(k for k,v in lang_options.items() if v==st.session_state["idioma"])
    sel=st.selectbox("",list(lang_options.keys()),index=list(lang_options.keys()).index(current),key="sb_lang",label_visibility="collapsed")
    if lang_options[sel]!=st.session_state["idioma"]:
        set_lang(lang_options[sel])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">', unsafe_allow_html=True)

    t=tr()

    if not st.session_state["logged_in"]:
        tab_in,tab_up=st.tabs([t["login"],t["register"]])
        with tab_in:
            em=st.text_input(t["email"],key="si_e")
            pw=st.text_input(t["password"],type="password",key="si_p")
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
            re_=st.text_input(t["email"],key="su_e")
            rp1=st.text_input(t["password"],type="password",key="su_p1")
            rp2=st.text_input(t["confirm_pass"],type="password",key="su_p2")
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
        em_d=st.session_state["user_email"]
        if len(em_d)>22: em_d=em_d[:20]+"…"
        st.markdown(f"""
<div style="padding:10px 12px;background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.15);border-radius:10px;margin-bottom:10px;">
  <div style="font-size:12px;color:rgba(255,255,255,.7);margin-bottom:3px;">{em_d}</div>
  <div style="display:flex;align-items:center;gap:5px;">
    <div style="width:6px;height:6px;border-radius:50%;background:{role_color};"></div>
    <span style="font-family:monospace;font-size:9px;color:{role_color};letter-spacing:1.5px;">{role_lbl.upper()}</span>
  </div>
</div>""", unsafe_allow_html=True)
        if st.button(f"◆ {t['tagline']}",use_container_width=True,key="nav_g"):
            st.session_state["vista"]="app"; st.rerun()
        if st.button(f"📋 {t['history']}",use_container_width=True,key="nav_h"):
            st.session_state["vista"]="history"; st.rerun()
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">', unsafe_allow_html=True)
        if st.button(t["logout"],use_container_width=True,key="btn_lo"):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
            st.query_params.clear(); st.rerun()

# ==========================================
# 13. LANDING
# ==========================================
if not st.session_state["logged_in"]:
    t=tr()
    render_header()

    st.markdown(f"""
<div style="text-align:center;padding:32px 16px 16px;">
  <div class="tag-gold" style="margin-bottom:14px;">
    <span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>
    Data Convergence Engine
  </div>
  <h1 style="font-family:'Playfair Display',serif;font-size:clamp(34px,7vw,70px);
  font-weight:700;line-height:1.05;letter-spacing:-2px;margin-bottom:14px;">
    {t['hero_1']}<br><span class="shimmer-text">{t['hero_2']}</span><br>{t['hero_3']}
  </h1>
  <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);
  color:rgba(255,255,255,.38);max-width:480px;margin:0 auto;line-height:1.8;">{t['hero_sub']}</p>
</div>""", unsafe_allow_html=True)

    render_balls_landing()

    col1,col2,col3=st.columns([1,2,1])
    with col2:
        if st.button(t["cta_free"],use_container_width=True,key="land_cta"):
            st.session_state["mostrar_reg"]=True; st.rerun()
        st.markdown('<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.16);letter-spacing:1.5px;margin-top:7px;">FREE · NO CREDIT CARD · ES / EN / PT</p>', unsafe_allow_html=True)

    if st.session_state.get("mostrar_reg"):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:20px 0;">', unsafe_allow_html=True)
        ca,cb,cc=st.columns([1,2,1])
        with cb:
            tab_r,tab_l=st.tabs([t["register"],t["login"]])
            with tab_r:
                re_=st.text_input(t["email"],key="lr_e"); rp=st.text_input(t["password"],type="password",key="lr_p")
                rp2=st.text_input(t["confirm_pass"],type="password",key="lr_p2")
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

    # 4 signals
    st.markdown(f"""
<div style="text-align:center;padding:28px 0 14px;">
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.2);letter-spacing:3px;margin-bottom:8px;">HOW IT WORKS</div>
  <h2 style="font-family:'Playfair Display',serif;font-size:clamp(20px,3vw,34px);font-weight:700;letter-spacing:-1px;margin-bottom:4px;">Four signals. One combination.</h2>
  <div class="gold-line"></div>
</div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    for col,(icon,key,desc) in zip([c1,c2,c3,c4],[
        ("📊","historico","Official draws analyzed by date, month and frequency patterns"),
        ("👥","community","Reddit picks + Google Trends in real time"),
        ("🌍","eventos","Numbers from today's Wikipedia history and headlines"),
        ("✦","fecha_personal","Your dates + numerology, Fibonacci, sacred geometry & dreams"),
    ]):
        with col:
            st.markdown(f"""<div class="ls-card" style="text-align:center;min-height:128px;">
<div style="font-size:22px;margin-bottom:7px;">{icon}</div>
<div style="font-family:'Playfair Display',serif;font-size:13px;font-weight:600;color:rgba(255,255,255,.85);margin-bottom:4px;">{t['sources'][key]}</div>
<div style="font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.3);line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;padding:22px 0 10px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;">11 LOTTERIES · 3 LANGUAGES · DREAM MODE</div></div>', unsafe_allow_html=True)
    cols=st.columns(4)
    for i,lot in enumerate(LOTERIAS):
        with cols[i%4]:
            st.markdown(f'<div style="padding:8px 10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:8px;display:flex;align-items:center;gap:7px;margin-bottom:6px;"><span style="font-size:14px;">{lot["flag"]}</span><span style="font-size:12px;color:rgba(255,255,255,.55);">{lot["nombre"]}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:520px;margin:20px auto 0;">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 14. APP
# ==========================================
elif st.session_state.get("vista")=="app":
    t=tr()
    es_free=st.session_state["user_role"]=="free"
    es_paid=st.session_state["user_role"] in ["paid","pro","convergence","admin"]

    render_header()
    st.markdown(f'<h2 style="font-family:\'Playfair Display\',serif;font-size:clamp(20px,3vw,32px);font-weight:700;letter-spacing:-1px;margin:6px 0 12px;">{t["select_lottery"]}</h2>', unsafe_allow_html=True)

    lot_names=[f"{l['flag']} {l['nombre']}  ({l['pais']})" for l in LOTERIAS]
    sel=st.selectbox("",lot_names,label_visibility="collapsed",key="lot_sel")
    loteria=next(l for l in LOTERIAS if l["nombre"] in sel)

    # Jackpot en tiempo real
    jackpot=obtener_jackpot(loteria["nombre"])
    if jackpot:
        st.markdown(f'<div style="margin:4px 0 10px;"><span class="jackpot-badge">🏆 {t["jackpot_live"]}: {jackpot}</span></div>', unsafe_allow_html=True)

    # Contador visual
    gen_hoy=st.session_state["generaciones_hoy"].get(loteria["id"],0)
    restantes=max(0,MAX_GEN-gen_hoy)
    render_gen_dots(gen_hoy)
    st.markdown(f'<div style="text-align:center;margin:-6px 0 12px;"><span class="metric-pill">{t["gen_counter"]}: {gen_hoy}/{MAX_GEN}</span></div>', unsafe_allow_html=True)

    # Inputs plan pago
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

        with st.expander(f"🌙 {t['dream_title']}",expanded=False):
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
            sistemas=[]
            if u_num: sistemas.append("numerologia")
            if u_fib: sistemas.append("fibonacci")
            if u_sag: sistemas.append("sagrada")
            if u_tes: sistemas.append("tesla")
            if u_fra: sistemas.append("fractal")
            inputs["sistemas"]=sistemas

    # Generar
    if restantes<=0:
        st.warning(f"⚠️ {t['gen_counter']}: {MAX_GEN}/{MAX_GEN}")
    else:
        if st.button(f"◆ {t['generate_btn']}",use_container_width=True,key="gen_btn"):
            if es_paid or st.session_state["user_role"]=="admin":
                render_convergence_animation(t)
                resultado=generar_combinacion(loteria,inputs)
            else:
                with st.spinner(t["generating"]):
                    resultado=generar_fallback(loteria,[])
            st.session_state["ultima_generacion"]=resultado
            st.session_state["ultima_loteria"]=loteria
            st.session_state["generaciones_hoy"][loteria["id"]]=gen_hoy+1
            if st.session_state.get("user_id"):
                guardar_generacion(st.session_state["user_id"],loteria["id"],resultado.get("numbers",[]),resultado.get("bonus"),resultado.get("sources",[]),inputs)
            st.rerun()

    if st.session_state.get("ultima_generacion") and st.session_state.get("ultima_loteria"):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:14px 0;">', unsafe_allow_html=True)
        render_resultado(st.session_state["ultima_generacion"],st.session_state["ultima_loteria"])

    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:18px 0;">', unsafe_allow_html=True)
        render_paywall()

# ==========================================
# 15. HISTORIAL
# ==========================================
elif st.session_state.get("vista")=="history":
    t=tr()
    render_header()
    st.markdown(f'<div style="padding:8px 0 12px;"><span class="tag-gold">◆ {t["history"]}</span></div>', unsafe_allow_html=True)

    if st.session_state.get("user_id"):
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
                    st.markdown(f"""<div class="ls-card" style="margin-bottom:10px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
<span style="font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;">{lot['flag']} {lot['nombre']}</span>
<span style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.2);">{fecha}</span></div>
<div style="font-family:'DM Mono',monospace;font-size:18px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Sign in to see your history.")
