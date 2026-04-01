import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime
import requests, random, json, re, math
from collections import Counter

# ==========================================
# 1. CONFIG
# ==========================================
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆", layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULTS = {
    'logged_in': False, 'user_role': 'invitado',
    'user_email': '', 'user_id': None,
    'idioma': 'EN', 'fecha_uso': str(date.today()),
    'generaciones_hoy': {}, 'ultima_generacion': None,
    'ultima_loteria': None, 'vista': 'landing',
    'mostrar_reg': False,
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
html,body,.stApp{background-color:#0a0a0f!important;color:white!important;font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}

/* SIDEBAR */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0d0d1a 0%,#0a0a0f 100%)!important;
  border-right:1px solid rgba(201,168,76,0.15)!important;
}
section[data-testid="stSidebar"]>div:first-child{padding-top:0!important;}

/* BUTTONS */
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
  color:white!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;
}
.stTextInput>div>div>input:focus{border-color:rgba(201,168,76,.45)!important;box-shadow:0 0 0 2px rgba(201,168,76,.08)!important;}
.stSelectbox>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;color:white!important;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03)!important;border-radius:8px!important;gap:2px!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.4)!important;font-family:'DM Sans',sans-serif!important;font-size:13px!important;border-radius:6px!important;}
.stTabs [aria-selected="true"]{color:#C9A84C!important;background:rgba(201,168,76,.1)!important;}

/* RADIO */
.stRadio>div{flex-direction:row!important;flex-wrap:wrap!important;gap:8px!important;}
.stRadio>div>label{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;padding:6px 12px!important;color:rgba(255,255,255,.5)!important;font-size:13px!important;cursor:pointer!important;}

/* EXPANDER */
.stExpander{border:1px solid rgba(201,168,76,.15)!important;border-radius:12px!important;background:rgba(255,255,255,.02)!important;}

/* ANIMATIONS */
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes goldPulse{0%,100%{box-shadow:0 0 12px rgba(201,168,76,.3);transform:scale(1)}50%{box-shadow:0 0 26px rgba(201,168,76,.6);transform:scale(1.05)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes ballFade{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.8)}}

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

/* PROGRESS DOTS */
.gen-dots{display:flex;gap:6px;justify-content:center;margin:8px 0 16px;}
.dot{width:10px;height:10px;border-radius:50%;transition:all .3s;}
.dot-used{background:linear-gradient(135deg,#C9A84C,#F5D68A);box-shadow:0 0 8px rgba(201,168,76,.4);}
.dot-empty{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);}

/* SOURCE ROWS */
.src-row{display:flex;align-items:flex-start;justify-content:space-between;padding:11px 14px;border-radius:10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);margin-bottom:8px;gap:12px;}
.src-complement{background:rgba(255,255,255,.01);border-color:rgba(255,255,255,.04);}
.src-left{display:flex;align-items:flex-start;gap:10px;flex:1;min-width:0;}
.src-icon{font-size:15px;margin-top:1px;flex-shrink:0;}
.src-label{font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:rgba(255,255,255,.75);}
.src-desc{font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.35);line-height:1.55;margin-top:2px;}
.src-num{font-family:'DM Mono',monospace;font-size:15px;color:#C9A84C;font-weight:700;flex-shrink:0;margin-top:1px;}
.src-complement .src-num{color:rgba(255,255,255,.25);}

/* JACKPOT BADGE */
.jackpot-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}

/* MISC */
.tag-gold{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;}
.metric-pill{display:inline-block;padding:4px 12px;border-radius:20px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.18);font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.disclaimer{background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:13px 15px;font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,.3);line-height:1.65;font-style:italic;margin-top:16px;}
.gold-line{width:36px;height:2px;margin:10px auto;background:linear-gradient(90deg,transparent,#C9A84C,transparent);}
.sidebar-hr{border:none;border-top:1px solid rgba(255,255,255,.06);margin:12px 0;}

@media(max-width:768px){.ball{width:44px;height:44px;font-size:14px;}.src-desc{font-size:10px;}h1{font-size:clamp(32px,9vw,52px)!important;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CREDENCIALES
# ==========================================
try:
    GROQ_KEY     = st.secrets["GROQ_API_KEY"]
    SB_URL       = st.secrets["SUPABASE_URL"]
    SB_KEY       = st.secrets["SUPABASE_KEY"]
    RESEND_KEY   = st.secrets.get("RESEND_API_KEY","")
    ADMIN_EMAIL  = st.secrets.get("ADMIN_EMAIL","admin@lucksort.com")
    ADMIN_PASS   = st.secrets.get("ADMIN_PASS","admin123")
    NEWS_KEY     = st.secrets.get("NEWS_API_KEY","")
    LOTTERY_KEY  = st.secrets.get("LOTTERYDATA_KEY","")
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
    "personal_title":"Personal Signals (optional)",
    "special_date":"Special date (birthday, anniversary...)","your_name":"Your name",
    "life_moment":"Something happening in your life right now",
    "exclude_numbers":"Numbers to exclude (comma separated)",
    "symbolic_title":"Symbolic Systems (optional)",
    "symbolic_help":"Select which systems to include in your combination",
    "sys_num":"Numerology","sys_fib":"Fibonacci","sys_sag":"Sacred Geometry (φ, π)",
    "sys_tes":"Tesla (3·6·9)","sys_fra":"Historical Fractals",
    "crowd_pref":"Crowd preference","follow":"Follow crowd","avoid":"Avoid crowd","balanced":"Balanced",
    "generate_btn":"Generate Combination","generating":"Converging 4 data sources...",
    "sources_title":"Where each number comes from",
    "gen_counter":"Today","share_btn":"Share this combination","email_combo":"Send to my email",
    "email_sent":"✅ Sent to your email!","email_err":"⚠️ Configure Resend to send emails.",
    "disclaimer":"We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
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
    "hero_sub":"Recopilamos datos reales — sorteos históricos, picks de la comunidad, titulares de hoy y tus fechas personales — convergidos en combinaciones con significado.",
    "cta_free":"Empezar Gratis","login":"Entrar","register":"Crear Cuenta","logout":"Cerrar Sesión",
    "email":"Correo","password":"Contraseña","confirm_pass":"Confirmar contraseña",
    "btn_login":"Entrar","btn_register":"Crear Cuenta Gratis",
    "plan":"Plan","free":"Gratis","paid":"Convergencia",
    "select_lottery":"Selecciona tu Lotería","jackpot_live":"Jackpot en vivo",
    "personal_title":"Señales personales (opcional)",
    "special_date":"Fecha especial (cumpleaños, aniversario...)","your_name":"Tu nombre",
    "life_moment":"Algo que está pasando en tu vida ahora",
    "exclude_numbers":"Números a excluir (separados por coma)",
    "symbolic_title":"Sistemas simbólicos (opcional)",
    "symbolic_help":"Selecciona qué sistemas incluir en tu combinación",
    "sys_num":"Numerología","sys_fib":"Fibonacci","sys_sag":"Geometría Sagrada (φ, π)",
    "sys_tes":"Tesla (3·6·9)","sys_fra":"Fractales del histórico",
    "crowd_pref":"Preferencia comunidad","follow":"Seguir masa","avoid":"Ir contra masa","balanced":"Balanceado",
    "generate_btn":"Generar Combinación","generating":"Convergiendo 4 fuentes de datos...",
    "sources_title":"De dónde viene cada número",
    "gen_counter":"Hoy","share_btn":"Compartir combinación","email_combo":"Enviar a mi correo",
    "email_sent":"✅ ¡Enviado a tu correo!","email_err":"⚠️ Configura Resend para enviar emails.",
    "disclaimer":"Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
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
    "hero_sub":"Coletamos dados reais — histórico de sorteios, picks da comunidade, manchetes de hoje e suas datas pessoais — convergidos em combinações com significado.",
    "cta_free":"Começar Grátis","login":"Entrar","register":"Criar Conta","logout":"Sair",
    "email":"Email","password":"Senha","confirm_pass":"Confirmar senha",
    "btn_login":"Entrar","btn_register":"Criar Conta Grátis",
    "plan":"Plano","free":"Grátis","paid":"Convergência",
    "select_lottery":"Selecione sua Loteria","jackpot_live":"Jackpot ao vivo",
    "personal_title":"Sinais pessoais (opcional)",
    "special_date":"Data especial (aniversário...)","your_name":"Seu nome",
    "life_moment":"Algo acontecendo na sua vida agora",
    "exclude_numbers":"Números a excluir (separados por vírgula)",
    "symbolic_title":"Sistemas simbólicos (opcional)",
    "symbolic_help":"Selecione quais sistemas incluir na sua combinação",
    "sys_num":"Numerologia","sys_fib":"Fibonacci","sys_sag":"Geometria Sagrada (φ, π)",
    "sys_tes":"Tesla (3·6·9)","sys_fra":"Fractais do histórico",
    "crowd_pref":"Preferência comunidade","follow":"Seguir massa","avoid":"Ir contra massa","balanced":"Balanceado",
    "generate_btn":"Gerar Combinação","generating":"Convergindo 4 fontes de dados...",
    "sources_title":"De onde vem cada número",
    "gen_counter":"Hoje","share_btn":"Compartilhar combinação","email_combo":"Enviar para meu email",
    "email_sent":"✅ Enviado para seu email!","email_err":"⚠️ Configure o Resend para enviar emails.",
    "disclaimer":"Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
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

def fib_en_rango(mn, mx):
    out=[];a,b=1,1
    while a<=mx:
        if a>=mn: out.append(a)
        a,b=b,a+b
    return out

def sagrada_en_rango(mn, mx):
    nums=set()
    for i in range(1,40):
        for v in [int(PHI*i), int(PI*i), round(PHI**2*i)]:
            if mn<=v<=mx: nums.add(v)
    pi_digs=[3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6]
    acum=0
    for d in pi_digs:
        acum+=d
        if mn<=acum<=mx: nums.add(acum)
    return sorted(nums)

def tesla_en_rango(mn, mx):
    return [n for n in range(mn,mx+1) if n%3==0]

def numerologia_nombre(nombre):
    if not nombre: return None
    tabla={c:((ord(c.lower())-ord('a'))%9)+1 for c in 'abcdefghijklmnopqrstuvwxyz'}
    suma=sum(tabla.get(c.lower(),0) for c in nombre if c.isalpha())
    while suma>9 and suma not in [11,22,33]:
        suma=sum(int(d) for d in str(suma))
    return suma

def numerologia_fecha(fecha_str):
    if not fecha_str: return None
    try:
        digitos=[c for c in fecha_str if c.isdigit()]
        suma=sum(int(d) for d in digitos)
        while suma>9 and suma not in [11,22,33]:
            suma=sum(int(d) for d in str(suma))
        return suma
    except: return None

def extraer_nums_fecha(fecha_str, mn, mx):
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

def calcular_simbolicos(loteria, inputs):
    mn,mx=loteria['min'],loteria['max']
    sistemas=inputs.get('sistemas',[])
    result={}
    if 'numerologia' in sistemas:
        nn=numerologia_nombre(inputs.get('nombre',''))
        nf=numerologia_fecha(inputs.get('fecha_especial',''))
        nums=[n for n in [nn,nf,11,22,33] if n and mn<=n<=mx]
        result['numerologia']={'numeros':list(set(nums)),'maestro_nombre':nn,'maestro_fecha':nf}
    if 'fibonacci' in sistemas:
        result['fibonacci']={'numeros':fib_en_rango(mn,mx)}
    if 'sagrada' in sistemas:
        result['sagrada']={'numeros':sagrada_en_rango(mn,mx)[:20]}
    if 'tesla' in sistemas:
        result['tesla']={'numeros':tesla_en_rango(mn,mx)[:15]}
    return result

# ==========================================
# 7. DATOS EXTERNOS
# ==========================================
def get_cache(tipo):
    try:
        hoy=str(date.today())
        res=supabase.table("cache_diario").select("*").eq("fecha",hoy).eq("tipo",tipo).execute()
        return res.data[0]['contenido'] if res.data else None
    except: return None

def set_cache(tipo, contenido, fuente=""):
    try:
        hoy=str(date.today())
        ex=supabase.table("cache_diario").select("id").eq("fecha",hoy).eq("tipo",tipo).execute()
        if ex.data:
            supabase.table("cache_diario").update({"contenido":contenido}).eq("id",ex.data[0]['id']).execute()
        else:
            supabase.table("cache_diario").insert({"fecha":hoy,"tipo":tipo,"contenido":contenido,"fuente":fuente}).execute()
    except: pass

def obtener_efemerides(mes, dia):
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
                res=[{"title":a.get("title","")[:130],"source":a.get("source",{}).get("name","")} for a in arts]
                set_cache("noticias",res,"newsapi"); return res
    except: pass
    return []

def obtener_reddit_crowd(loteria):
    """Reddit JSON público — sin autenticación requerida"""
    tipo=f"reddit_{loteria['id']}_{date.today()}"
    c=get_cache(tipo)
    if c: return c

    subs=loteria.get('reddit',['lottery'])
    headers={"User-Agent":"LuckSort/1.0 (lottery combination tool)"}
    nums_encontrados=[]
    mn,mx=loteria['min'],loteria['max']

    for sub in subs[:2]:
        try:
            url=f"https://www.reddit.com/r/{sub}/hot.json?limit=15"
            r=requests.get(url,headers=headers,timeout=8)
            if r.status_code==200:
                posts=r.json().get("data",{}).get("children",[])
                for post in posts:
                    texto=post.get("data",{}).get("title","")+\
                          " "+post.get("data",{}).get("selftext","")
                    found=re.findall(r'\b(\d{1,2})\b',texto)
                    for n in found:
                        v=int(n)
                        if mn<=v<=mx:
                            nums_encontrados.append(v)
        except: pass

    if not nums_encontrados:
        # Fallback con patrones conocidos
        base=[7,11,14,17,21,23,27,32,38,42,3,8,13,19,29,33,44]
        nums_encontrados=random.sample([n for n in base if mn<=n<=mx],
                                       min(8,len([n for n in base if mn<=n<=mx])))

    conteo=Counter(nums_encontrados)
    top=[n for n,_ in conteo.most_common(10)]
    set_cache(tipo,top,"reddit_json")
    return top

def obtener_google_trends():
    c=get_cache("trends")
    if c: return c
    try:
        from trendspyg import download_google_trends_rss
        trends=download_google_trends_rss(geo='US')
        nums=[]
        for t in trends[:10]:
            text=t.get('trend','')+' '+str(t.get('traffic',''))
            found=re.findall(r'\b(\d{1,2})\b',text)
            nums.extend([int(n) for n in found if 1<=int(n)<=70])
        if nums:
            set_cache("trends",nums[:15],"trendspyg"); return nums[:15]
    except: pass
    return []

def obtener_jackpot(loteria_nombre):
    """LotteryData.io — jackpots en tiempo real"""
    try:
        nombre_map={
            "Powerball":"powerball","Mega Millions":"megamillions",
            "EuroMillions":"euromillions","EuroJackpot":"eurojackpot",
        }
        slug=nombre_map.get(loteria_nombre)
        if not slug: return None
        if LOTTERY_KEY:
            r=requests.get(f"https://lotterydata.io/api/{slug}/latest",
                          headers={"Authorization":f"Bearer {LOTTERY_KEY}"},timeout=6)
        else:
            r=requests.get(f"https://lotterydata.io/api/{slug}/latest",timeout=6)
        if r.status_code==200:
            data=r.json()
            jackpot=data.get("data",[{}])[0].get("jackpot") or data.get("jackpot")
            return jackpot
    except: pass
    return None

# ==========================================
# 8. GENERACIÓN GROQ
# ==========================================
def generar_combinacion(loteria, inputs):
    lang=st.session_state['idioma']
    lang_map={"EN":"English","ES":"Spanish","PT":"Portuguese"}
    lang_full=lang_map[lang]
    hoy=datetime.now()

    efem_hoy=obtener_efemerides(hoy.month,hoy.day)
    noticias=obtener_noticias()
    crowd_reddit=obtener_reddit_crowd(loteria)
    crowd_trends=obtener_google_trends()

    efem_personal=[]
    nums_fecha=[]
    fecha_esp=inputs.get('fecha_especial','')
    if fecha_esp:
        partes=[x for x in re.split(r'[-/.]',fecha_esp) if x.isdigit()]
        if len(partes)>=2:
            try:
                d,m=int(partes[0]),int(partes[1])
                if 1<=d<=31 and 1<=m<=12:
                    efem_personal=obtener_efemerides(m,d)
                    nums_fecha=extraer_nums_fecha(fecha_esp,loteria['min'],loteria['max'])
            except: pass

    simbolicos=calcular_simbolicos(loteria,inputs)
    excluir=[]
    if inputs.get('excluir'):
        try: excluir=[int(x.strip()) for x in inputs['excluir'].split(',') if x.strip().isdigit()]
        except: pass

    sistemas_seleccionados=inputs.get('sistemas',[])

    bonus_inst=f"- 1 {loteria['bname']} between 1-{loteria['bmax']}" if loteria['bonus'] else "- No bonus"
    
    prompt=f"""You are LuckSort's data convergence engine. Generate a {loteria['nombre']} combination.

LOTTERY: {loteria['nombre']} | {loteria['n']} numbers ({loteria['min']}-{loteria['max']}) | {bonus_inst}
EXCLUDE: {excluir if excluir else 'none'}
CROWD: {inputs.get('crowd','balanced')}

REAL DATA SIGNALS:
1. TODAY'S WORLD EVENTS ({hoy.strftime('%B %d')}): {json.dumps(efem_hoy[:4],ensure_ascii=False)}
2. USER DATE ({fecha_esp}): events={json.dumps(efem_personal[:3],ensure_ascii=False)}, extracted_numbers={nums_fecha}
3. NEWS: {json.dumps(noticias[:4],ensure_ascii=False)}
4. COMMUNITY: reddit={crowd_reddit}, trends={crowd_trends[:6] if crowd_trends else []}
5. SYMBOLIC SYSTEMS SELECTED: {json.dumps(simbolicos,ensure_ascii=False)}
   IMPORTANT: Only use symbolic systems that appear in the SELECTED list above.
   If "fibonacci" not in selected → do NOT use fibonacci source.
   If "tesla" not in selected → do NOT use tesla source.
   If "sagrada" not in selected → do NOT use sagrada source.
   If "numerologia" not in selected → do NOT use numerologia source.

RULES:
1. Each number MUST have a REAL specific signal from data above
2. ONLY use symbolic systems that the user SELECTED — never impose unselected ones
3. Extract numbers from: years→last 2 digits, dates→day/month/sum, headlines→quantities mentioned
4. Use "complement" ONLY if truly no signal exists — be honest
5. Numbers must be unique, in valid range, not in exclude list
6. Be SPECIFIC in explanations — cite the exact data point, minimum 15 words
7. Crowd preference: follow=prioritize reddit/trends numbers, avoid=avoid them, balanced=mix

Respond ONLY in {lang_full}. Return ONLY valid JSON:
{{
  "numbers":[list of {loteria['n']} integers],
  "bonus":{f'integer 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources":[
    {{"number":N,"source":"historico|community|eventos|fecha_personal|numerologia|fibonacci|sagrada|tesla|fractal|complement","label":"short name","explanation":"specific real reason 15+ words"}}
  ]
}}"""

    try:
        resp=groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"LuckSort engine. Respond ONLY in {lang_full}. Return ONLY valid JSON."},
                {"role":"user","content":prompt}
            ],
            temperature=0.65,max_tokens=1400
        )
        raw=resp.choices[0].message.content.strip()
        if "```" in raw: raw=raw.split("```")[1].replace("json","").strip()
        res=json.loads(raw)

        nums=[n for n in res.get("numbers",[]) if loteria['min']<=n<=loteria['max'] and n not in excluir]
        pool=[n for n in range(loteria['min'],loteria['max']+1) if n not in nums and n not in excluir]
        while len(nums)<loteria['n'] and pool:
            p=random.choice(pool); nums.append(p); pool.remove(p)
        res['numbers']=list(dict.fromkeys(nums))[:loteria['n']]

        if loteria['bonus'] and res.get('bonus'):
            b=res['bonus']
            if not isinstance(b,int) or not (1<=b<=loteria['bmax']):
                res['bonus']=random.randint(1,loteria['bmax'])
        return res
    except:
        return generar_fallback(loteria,excluir)

def generar_fallback(loteria,excluir=[]):
    pool=[n for n in range(loteria['min'],loteria['max']+1) if n not in excluir]
    nums=random.sample(pool,min(loteria['n'],len(pool)))
    bonus=random.randint(1,loteria['bmax']) if loteria['bonus'] else None
    sources=[{"number":n,"source":"complement","label":"Random","explanation":"No specific signal found for this position — generated randomly as complement"} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","label":"Random","explanation":"Randomly generated bonus"})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

def generar_aleatorio(loteria):
    return generar_fallback(loteria)

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

def guardar_generacion(user_id,loteria_id,numeros,bonus,sources,inputs):
    try:
        supabase.table("generaciones").insert({
            "user_id":user_id,"loteria_id":loteria_id,
            "numeros":numeros,"bonus":bonus,
            "narrativa":json.dumps(sources,ensure_ascii=False),
            "inputs_usuario":json.dumps(inputs,ensure_ascii=False),
        }).execute()
    except: pass

def obtener_historial(user_id,limit=15):
    try:
        res=supabase.table("generaciones").select("*").eq("user_id",user_id).order("created_at",desc=True).limit(limit).execute()
        return res.data if res.data else []
    except: return []

def resetear_uso():
    hoy=str(date.today())
    if st.session_state.get('fecha_uso')!=hoy:
        st.session_state['generaciones_hoy']={}
        st.session_state['fecha_uso']=hoy

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
    t=T[st.session_state.get('idioma','EN')]
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
<div style="text-align:center;padding:24px 0 16px;">
<div style="display:inline-flex;align-items:center;gap:10px;">
<div style="width:34px;height:34px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:17px;color:#0a0a0f;">◆</div>
<span style="font-size:24px;font-weight:700;color:white;font-family:Georgia,serif;">LuckSort</span>
</div>
<p style="color:rgba(255,255,255,.25);font-size:10px;letter-spacing:3px;margin-top:5px;">SORT YOUR LUCK</p>
</div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,.2);margin:10px 0 22px;">
<h2 style="color:white;">Welcome ◆</h2>
<p style="color:rgba(255,255,255,.6);line-height:1.7;">Your LuckSort account is ready.</p>
<div style="background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:20px;margin:20px 0;">
<p style="color:#C9A84C;font-size:11px;letter-spacing:2px;margin-bottom:12px;">FREE PLAN</p>
<ul style="color:rgba(255,255,255,.6);line-height:2.2;margin:0;padding-left:18px;">
<li>5 random combinations per lottery per day</li><li>11 major lotteries — 3 languages</li><li>Upgrade for full data convergence</li>
</ul></div>
<div style="text-align:center;margin:26px 0;">
<a href="{APP_URL}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;font-size:15px;">Open LuckSort →</a>
</div>
<p style="color:rgba(255,255,255,.18);font-size:11px;font-style:italic;text-align:center;">"{t['disclaimer']}"</p>
<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:18px 0;">
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;">© 2025 LuckSort · lucksort.com</p>
</body></html>"""
    enviar_email(email,"Welcome to LuckSort ◆",html)

def email_combinacion(to, loteria, resultado):
    t=T[st.session_state.get('idioma','EN')]
    nums=resultado.get('numbers',[])
    bonus=resultado.get('bonus')
    sources=resultado.get('sources',[])
    nums_str=' · '.join([str(n).zfill(2) for n in nums])
    bonus_str=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    sources_html=""
    for s in sources:
        icon=t['icons'].get(s.get('source','complement'),'⚪')
        lbl=s.get('label','')
        exp=s.get('explanation','')
        num=s.get('number','')
        sources_html+=f"""<div style="padding:10px 14px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);margin-bottom:7px;">
<span style="font-size:14px;">{icon}</span> <strong style="color:rgba(255,255,255,.75);">{lbl}</strong><span style="color:#C9A84C;float:right;">→ {str(num).zfill(2)}</span>
<p style="color:rgba(255,255,255,.4);font-size:11px;margin:4px 0 0;">{exp}</p></div>"""
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
<div style="text-align:center;padding:20px 0 14px;">
<div style="display:inline-flex;align-items:center;gap:8px;">
<div style="width:28px;height:28px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px;color:#0a0a0f;">◆</div>
<span style="font-size:20px;font-weight:700;color:white;font-family:Georgia,serif;">LuckSort</span>
</div></div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,.2);margin:10px 0 20px;">
<div style="text-align:center;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:14px;padding:22px;margin-bottom:20px;">
<div style="font-family:monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;margin-bottom:10px;">{loteria['flag']} {loteria['nombre'].upper()}</div>
<div style="font-family:monospace;font-size:28px;font-weight:700;color:white;letter-spacing:4px;">{nums_str}{bonus_str}</div>
</div>
<p style="color:#C9A84C;font-size:11px;letter-spacing:2px;margin-bottom:12px;">{t['sources_title'].upper()}</p>
{sources_html}
<p style="color:rgba(255,255,255,.2);font-size:11px;font-style:italic;text-align:center;margin-top:20px;">"{t['disclaimer']}"</p>
<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:16px 0;">
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;">© 2025 LuckSort · lucksort.com</p>
</body></html>"""
    return enviar_email(to,f"◆ {loteria['nombre']} — LuckSort",html)

# ==========================================
# 11. UI COMPONENTS
# ==========================================
def render_balls_landing():
    st.markdown("""
<div style="margin:24px auto;max-width:440px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;text-align:center;margin-bottom:12px;">LIVE PREVIEW · POWERBALL</div>
  <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:18px;" id="balls-wrap">
    <div class="ball" id="b0">07</div><div class="ball" id="b1">14</div>
    <div class="ball" id="b2">23</div><div class="ball" id="b3">34</div>
    <div class="ball" id="b4">55</div><div class="ball ball-gold" id="b5">12</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px;">
    <div class="src-row"><div class="src-left"><span class="src-icon">📊</span><div><div class="src-label">Draw History</div><div class="src-desc">Appeared 31× in March draws (2010–2024)</div></div></div><span class="src-num">→ 07</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">🌀</span><div><div class="src-label">Fibonacci</div><div class="src-desc">34 is a Fibonacci number (21+13=34)</div></div></div><span class="src-num">→ 34</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">👥</span><div><div class="src-label">Community</div><div class="src-desc">Top 3 most picked on r/powerball today</div></div></div><span class="src-num">→ 23</span></div>
    <div class="src-row"><div class="src-left"><span class="src-icon">✦</span><div><div class="src-label">Your Date</div><div class="src-desc">Day extracted from birthday Mar 14</div></div></div><span class="src-num">→ 14</span></div>
  </div>
</div>
<script>
const S=[[7,14,23,34,55,12],[3,19,31,44,62,8],[11,22,35,47,68,17],[5,16,28,41,59,23],[9,21,33,46,63,4]];
let i=0;
setInterval(()=>{i=(i+1)%S.length;for(let j=0;j<6;j++){const el=document.getElementById('b'+j);if(!el)return;el.style.opacity='0';el.style.transform='scale(.75)';setTimeout(()=>{el.textContent=String(S[i][j]).padStart(2,'0');el.style.opacity='1';el.style.transform='scale(1)';},270+j*44);}},2800);
document.querySelectorAll('.ball').forEach(b=>{b.style.transition='opacity .27s ease,transform .27s ease';});
</script>""", unsafe_allow_html=True)

def render_gen_dots(gen_hoy, max_gen):
    dots=""
    for i in range(max_gen):
        cls="dot dot-used" if i<gen_hoy else "dot dot-empty"
        dots+=f'<div class="{cls}"></div>'
    st.markdown(f'<div class="gen-dots">{dots}</div>', unsafe_allow_html=True)

def render_resultado(resultado, loteria):
    t=tr()
    numeros=resultado.get("numbers",[])
    bonus=resultado.get("bonus")
    sources=resultado.get("sources",[])

    balls_html='<div class="balls-wrap">'
    for n in numeros: balls_html+=f'<div class="ball">{str(n).zfill(2)}</div>'
    if bonus: balls_html+=f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    balls_html+='</div>'
    bonus_lbl=f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.22);text-align:center;margin-top:2px;">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>' if bonus and loteria.get('bname') else ""

    st.markdown(f"""
<div class="ls-card-gold" style="text-align:center;">
  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:2px;">{loteria['flag']} {loteria['nombre']}</div>
  {balls_html}{bonus_lbl}
</div>""", unsafe_allow_html=True)

    if sources:
        st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;color:rgba(255,255,255,.28);letter-spacing:2px;text-transform:uppercase;margin:16px 0 10px;">{t["sources_title"]}</div>', unsafe_allow_html=True)
        for s in sources:
            src=s.get("source","complement")
            icon=t['icons'].get(src,"⚪")
            lbl=s.get("label") or t['sources'].get(src,src)
            exp=s.get("explanation","")
            num=s.get("number","")
            cls="src-row src-complement" if src=="complement" else "src-row"
            st.markdown(f"""<div class="{cls}"><div class="src-left"><span class="src-icon">{icon}</span><div><div class="src-label">{lbl}</div><div class="src-desc">{exp}</div></div></div><span class="src-num">→ {str(num).zfill(2)}</span></div>""", unsafe_allow_html=True)

    # Acciones
    t_data=tr()
    col1,col2=st.columns(2)
    with col1:
        # Compartir
        nums_str=" · ".join([str(n).zfill(2) for n in numeros])
        bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
        share_text=f"🎯 {loteria['nombre']}: {nums_str}{bonus_s}\n\nGenerated by LuckSort — Sort Your Luck\nlucksort.com"
        st.code(share_text, language=None)
    with col2:
        if st.session_state.get('user_email') and RESEND_KEY:
            if st.button(t_data['email_combo'], use_container_width=True, key="send_email"):
                ok=email_combinacion(st.session_state['user_email'],loteria,resultado)
                if ok: st.success(t_data['email_sent'])
                else: st.warning(t_data['email_err'])

    st.markdown(f'<div class="disclaimer">"{t_data["disclaimer"]}"</div>', unsafe_allow_html=True)

def render_paywall():
    t=tr()
    st.markdown(f"""
<div class="ls-card" style="border-color:rgba(201,168,76,.25);text-align:center;padding:28px;">
  <div style="font-size:26px;margin-bottom:10px;">◆</div>
  <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:20px;">{t['paywall_title']}</h3>
  <p style="color:rgba(255,255,255,.38);font-size:13px;max-width:320px;margin:0 auto 18px;line-height:1.65;">{t['paywall_msg']}</p>
  <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;">
    {"".join([f'<span style="font-size:11px;color:rgba(255,255,255,.35);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:4px 10px;">{i} {l}</span>' for l,i in [("Draw History","📊"),("Community","👥"),("World Events","🌍"),("Your Dates","✦"),("Numerology","🔢"),("Fibonacci","🌀"),("Sacred Geometry","⬡"),("Tesla 3·6·9","⚡")]])}
  </div>
</div>""", unsafe_allow_html=True)
    if st.button(t['upgrade_btn'], use_container_width=True, key="upgrade_btn"):
        pass

# ==========================================
# 12. SIDEBAR
# ==========================================
with st.sidebar:
    # LOGO
    st.markdown("""
<div style="padding:22px 16px 14px;border-bottom:1px solid rgba(201,168,76,.12);">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 18px rgba(201,168,76,.32);">
      <span style="font-size:17px;color:#0a0a0f;">◆</span>
    </div>
    <div>
      <div style="font-family:Georgia,'Times New Roman',serif;font-size:21px;font-weight:700;color:white;letter-spacing:-.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:'Courier New',monospace;font-size:8px;color:rgba(201,168,76,.5);letter-spacing:2.5px;margin-top:2px;">SORT YOUR LUCK</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # IDIOMA
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("🇺🇸 EN",key="l_en",use_container_width=True):
            st.session_state['idioma']='EN'; st.rerun()
    with c2:
        if st.button("🇪🇸 ES",key="l_es",use_container_width=True):
            st.session_state['idioma']='ES'; st.rerun()
    with c3:
        if st.button("🇧🇷 PT",key="l_pt",use_container_width=True):
            st.session_state['idioma']='PT'; st.rerun()

    lang_labels={"EN":"English","ES":"Español","PT":"Português"}
    st.markdown(f'<div style="text-align:center;font-family:\'DM Mono\',monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;margin:-4px 0 8px;">{lang_labels[st.session_state["idioma"]]}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-hr">', unsafe_allow_html=True)

    t=tr()

    if not st.session_state['logged_in']:
        tab_in,tab_up=st.tabs([t['login'],t['register']])
        with tab_in:
            em=st.text_input(t['email'],key="si_e")
            pw=st.text_input(t['password'],type="password",key="si_p")
            if st.button(t['btn_login'],use_container_width=True,key="btn_si"):
                if em==ADMIN_EMAIL and pw==ADMIN_PASS:
                    st.session_state.update({'logged_in':True,'user_role':'admin','user_email':em,'user_id':None,'vista':'app'}); st.rerun()
                else:
                    ok,datos=login_usuario(em,pw)
                    if ok:
                        st.session_state.update({'logged_in':True,'user_role':datos['role'],'user_email':datos['email'],'user_id':datos['id'],'vista':'app'})
                        resetear_uso(); st.rerun()
                    else: st.error(t['login_err'])
        with tab_up:
            re=st.text_input(t['email'],key="su_e")
            rp1=st.text_input(t['password'],type="password",key="su_p1")
            rp2=st.text_input(t['confirm_pass'],type="password",key="su_p2")
            if st.button(t['btn_register'],use_container_width=True,key="btn_su"):
                if rp1!=rp2: st.error(t['pass_mismatch'])
                elif len(rp1)<6: st.warning(t['pass_short'])
                elif "@" not in re: st.warning(t['email_invalid'])
                else:
                    ok,res=registrar_usuario(re,rp1)
                    if ok:
                        st.session_state.update({'logged_in':True,'user_role':'free','user_email':re,'user_id':res['id'],'vista':'app'})
                        email_bienvenida(re); st.rerun()
                    elif res=="exists": st.error(t['email_exists'])
                    else: st.error("⚠️ Error.")
    else:
        resetear_uso()
        role=st.session_state['user_role']
        role_lbl=t['paid'] if role not in ['free','invitado'] else t['free']
        role_color="#C9A84C" if role!='free' else "rgba(255,255,255,.3)"
        em_disp=st.session_state['user_email']
        if len(em_disp)>22: em_disp=em_disp[:20]+"…"
        st.markdown(f"""
<div style="padding:11px 13px;background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.15);border-radius:10px;margin-bottom:12px;">
  <div style="font-size:12px;color:rgba(255,255,255,.7);margin-bottom:3px;">{em_disp}</div>
  <div style="display:flex;align-items:center;gap:5px;">
    <div style="width:6px;height:6px;border-radius:50%;background:{role_color};"></div>
    <span style="font-family:'DM Mono',monospace;font-size:9px;color:{role_color};letter-spacing:1.5px;">{role_lbl.upper()}</span>
  </div>
</div>""", unsafe_allow_html=True)

        if st.button(f"◆ {t['tagline']}",use_container_width=True,key="nav_g"):
            st.session_state['vista']='app'; st.rerun()
        if st.button(f"📋 {t['history']}",use_container_width=True,key="nav_h"):
            st.session_state['vista']='history'; st.rerun()
        st.markdown('<hr class="sidebar-hr">',unsafe_allow_html=True)
        if st.button(t['logout'],use_container_width=True,key="btn_lo"):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
            st.rerun()

# ==========================================
# 13. LANDING
# ==========================================
if not st.session_state['logged_in']:
    t=tr()

    # HEADER — logo + idioma siempre visible móvil y desktop
    st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:14px 0 8px;border-bottom:1px solid rgba(201,168,76,0.1);margin-bottom:6px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:32px;height:32px;min-width:32px;
    background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 16px rgba(201,168,76,0.35);font-size:16px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
      color:white;letter-spacing:-0.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;
      color:rgba(201,168,76,0.5);letter-spacing:2px;">SORT YOUR LUCK</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    lc1,lc2,lc3,lc4=st.columns([3,1,1,1])
    with lc2:
        if st.button("EN",key="l_en2",use_container_width=True):
            st.session_state['idioma']='EN'; st.rerun()
    with lc3:
        if st.button("ES",key="l_es2",use_container_width=True):
            st.session_state['idioma']='ES'; st.rerun()
    with lc4:
        if st.button("PT",key="l_pt2",use_container_width=True):
            st.session_state['idioma']='PT'; st.rerun()
    t=tr()

    st.markdown(f"""
<div style="text-align:center;padding:36px 16px 18px;">
  <div class="tag-gold" style="margin-bottom:16px;">
    <span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>
    Data Convergence Engine
  </div>
  <h1 style="font-family:'Playfair Display',serif;font-size:clamp(34px,7vw,72px);font-weight:700;line-height:1.05;letter-spacing:-2px;margin-bottom:16px;">
    {t['hero_1']}<br><span class="shimmer-text">{t['hero_2']}</span><br>{t['hero_3']}
  </h1>
  <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);color:rgba(255,255,255,.38);max-width:490px;margin:0 auto;line-height:1.8;">{t['hero_sub']}</p>
</div>""", unsafe_allow_html=True)

    render_balls_landing()

    col1,col2,col3=st.columns([1,2,1])
    with col2:
        if st.button(t['cta_free'],use_container_width=True,key="land_cta"):
            st.session_state['mostrar_reg']=True; st.rerun()
        st.markdown('<p style="text-align:center;font-family:\'DM Mono\',monospace;font-size:9px;color:rgba(255,255,255,.16);letter-spacing:1.5px;margin-top:7px;">FREE · NO CREDIT CARD · ES / EN / PT</p>', unsafe_allow_html=True)

    if st.session_state.get('mostrar_reg'):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:20px 0;">', unsafe_allow_html=True)
        ca,cb,cc=st.columns([1,2,1])
        with cb:
            tab_r,tab_l=st.tabs([t['register'],t['login']])
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
<div style="text-align:center;padding:32px 0 16px;">
  <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.2);letter-spacing:3px;margin-bottom:10px;">HOW IT WORKS</div>
  <h2 style="font-family:'Playfair Display',serif;font-size:clamp(20px,3vw,36px);font-weight:700;letter-spacing:-1px;margin-bottom:4px;">Four signals. One combination.</h2>
  <div class="gold-line"></div>
</div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    for col,(icon,key,desc) in zip([c1,c2,c3,c4],[
        ("📊","historico","Official draw history analyzed by date, month and frequency"),
        ("👥","community","Reddit picks + Google Trends — what real players choose today"),
        ("🌍","eventos","Numbers hidden in today's Wikipedia history and headlines"),
        ("✦","fecha_personal","Your dates + numerology, Fibonacci and sacred geometry"),
    ]):
        with col:
            st.markdown(f"""<div class="ls-card" style="text-align:center;min-height:130px;">
<div style="font-size:22px;margin-bottom:8px;">{icon}</div>
<div style="font-family:'Playfair Display',serif;font-size:13px;font-weight:600;color:rgba(255,255,255,.85);margin-bottom:5px;">{t['sources'][key]}</div>
<div style="font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.3);line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;padding:24px 0 12px;"><div style="font-family:\'DM Mono\',monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;">GLOBAL COVERAGE · 11 LOTTERIES · 3 LANGUAGES</div></div>', unsafe_allow_html=True)
    cols=st.columns(4)
    for i,lot in enumerate(LOTERIAS):
        with cols[i%4]:
            st.markdown(f'<div style="padding:9px 11px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:8px;display:flex;align-items:center;gap:7px;margin-bottom:7px;"><span style="font-size:14px;">{lot["flag"]}</span><span style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(255,255,255,.58);">{lot["nombre"]}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:540px;margin:22px auto 0;">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 14. APP GENERADOR
# ==========================================
elif st.session_state.get('vista')=='app':
    t=tr()
    es_free=st.session_state['user_role']=='free'
    es_paid=st.session_state['user_role'] in ['paid','pro','convergence','admin']

    # Header con idioma visible
    col_h,col_lang2=st.columns([3,1])
    with col_h:
        st.markdown(f'<div style="padding:16px 0 4px;"><span class="tag-gold">◆ {t["tagline"]}</span></div>', unsafe_allow_html=True)
    with col_lang2:
        lang_now=st.session_state['idioma']
        options=["EN","ES","PT"]
        sel2=st.selectbox("",options,index=options.index(lang_now),key="app_lang",label_visibility="collapsed")
        if sel2!=lang_now:
            st.session_state['idioma']=sel2; st.rerun()

    st.markdown(f'<h2 style="font-family:\'Playfair Display\',serif;font-size:clamp(20px,3vw,34px);font-weight:700;letter-spacing:-1px;margin-top:8px;">{t["select_lottery"]}</h2>', unsafe_allow_html=True)

    # Selector lotería + jackpot
    lot_names=[f"{l['flag']} {l['nombre']}  ({l['pais']})" for l in LOTERIAS]
    sel=st.selectbox("",lot_names,label_visibility="collapsed",key="lot_sel")
    loteria=next(l for l in LOTERIAS if l['nombre'] in sel)

    # Jackpot en tiempo real
    jackpot=obtener_jackpot(loteria['nombre'])
    if jackpot:
        st.markdown(f'<div style="margin:4px 0 12px;"><span class="jackpot-badge">🏆 {t["jackpot_live"]}: {jackpot}</span></div>', unsafe_allow_html=True)

    # Contador visual
    gen_hoy=st.session_state['generaciones_hoy'].get(loteria['id'],0)
    restantes=max(0,MAX_GEN-gen_hoy)
    render_gen_dots(gen_hoy,MAX_GEN)
    st.markdown(f'<div style="text-align:center;margin:-8px 0 14px;"><span class="metric-pill">{t["gen_counter"]}: {gen_hoy}/{MAX_GEN}</span></div>', unsafe_allow_html=True)

    # Inputs plan pago
    inputs={}
    if es_paid or st.session_state['user_role']=='admin':
        with st.expander(f"✦ {t['personal_title']}",expanded=False):
            c1,c2=st.columns(2)
            with c1:
                fecha_esp=st.text_input(t['special_date'],placeholder="14/03/1990",key="fe")
                nombre=st.text_input(t['your_name'],placeholder="Your name",key="nm")
            with c2:
                momento=st.text_input(t['life_moment'],placeholder="I just started a business...",key="mm")
                excluir=st.text_input(t['exclude_numbers'],placeholder="4, 13",key="ex")
            crowd_pref=st.radio(t['crowd_pref'],[t['balanced'],t['follow'],t['avoid']],horizontal=True,key="cp")
            crowd_map={t['follow']:"follow",t['avoid']:"avoid",t['balanced']:"balanced"}
            inputs={"fecha_especial":fecha_esp,"nombre":nombre,"momento":momento,"excluir":excluir,"crowd":crowd_map.get(crowd_pref,"balanced")}

        with st.expander(f"⬡ {t['symbolic_title']}",expanded=False):
            st.caption(t['symbolic_help'])
            c1,c2=st.columns(2)
            with c1:
                u_num=st.checkbox(t['sys_num'],key="cb_n")
                u_fib=st.checkbox(t['sys_fib'],key="cb_f")
                u_sag=st.checkbox(t['sys_sag'],key="cb_s")
            with c2:
                u_tes=st.checkbox(t['sys_tes'],key="cb_t")
                u_fra=st.checkbox(t['sys_fra'],key="cb_r")
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
            with st.spinner(t['generating']):
                if es_paid or st.session_state['user_role']=='admin':
                    resultado=generar_combinacion(loteria,inputs)
                else:
                    resultado=generar_aleatorio(loteria)
                st.session_state['ultima_generacion']=resultado
                st.session_state['ultima_loteria']=loteria
                st.session_state['generaciones_hoy'][loteria['id']]=gen_hoy+1
                if st.session_state.get('user_id'):
                    guardar_generacion(st.session_state['user_id'],loteria['id'],
                        resultado.get('numbers',[]),resultado.get('bonus'),
                        resultado.get('sources',[]),inputs)

    if st.session_state.get('ultima_generacion') and st.session_state.get('ultima_loteria'):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:16px 0;">', unsafe_allow_html=True)
        render_resultado(st.session_state['ultima_generacion'],st.session_state['ultima_loteria'])

    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:20px 0;">', unsafe_allow_html=True)
        render_paywall()

# ==========================================
# 15. HISTORIAL
# ==========================================
elif st.session_state.get('vista')=='history':
    t=tr()
    st.markdown(f'<div style="padding:16px 0 12px;"><span class="tag-gold">◆ {t["history"]}</span></div>', unsafe_allow_html=True)

    if st.session_state.get('user_id'):
        hist=obtener_historial(st.session_state['user_id'])
        if not hist:
            st.markdown(f'<p style="color:rgba(255,255,255,.3);font-size:14px;">{t["no_history"]}</p>', unsafe_allow_html=True)
        else:
            for h in hist:
                lot=next((l for l in LOTERIAS if l['id']==h.get('loteria_id')),None)
                if lot:
                    nums_str="  ".join([str(n).zfill(2) for n in h['numeros']])
                    bonus_str=f"  ◆ {str(h['bonus']).zfill(2)}" if h.get('bonus') else ""
                    fecha=h.get('created_at','')[:10]
                    st.markdown(f"""<div class="ls-card" style="margin-bottom:10px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
<span style="font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;">{lot['flag']} {lot['nombre']}</span>
<span style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.2);">{fecha}</span>
</div>
<div style="font-family:'DM Mono',monospace;font-size:19px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Sign in to see your history.")
