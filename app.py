import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import date, datetime
import requests, random, json, re, math
from collections import Counter

# ==========================================
# 1. CONFIG + IDIOMA
# ==========================================
st.set_page_config(
    page_title="LuckSort | Sort Your Luck",
    page_icon="◆", layout="wide",
    initial_sidebar_state="collapsed"
)

params = st.query_params
if "lang" in params and params["lang"] in ["EN","ES","PT"]:
    st.session_state["idioma"] = params["lang"]

DEFAULTS = {
    "logged_in": False, "user_role": "invitado",
    "user_email": "", "user_id": None,
    "idioma": "EN", "fecha_uso": str(date.today()),
    "generaciones_hoy": {}, "ultima_generacion": None,
    "ultima_loteria": None, "vista": "landing",
    "mostrar_reg": False, "historial_sesion": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def set_lang(lang):
    st.session_state["idioma"] = lang
    st.query_params["lang"] = lang
    st.rerun()

# ==========================================
# 2. CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:#0a0a0f!important;color:white!important;font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}

section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d0d1a,#0a0a0f)!important;border-right:1px solid rgba(201,168,76,0.15)!important;}
section[data-testid="stSidebar"]>div:first-child{padding-top:0!important;}

.stButton>button{background:linear-gradient(135deg,#C9A84C,#F5D68A)!important;color:#0a0a0f!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;border:none!important;border-radius:10px!important;width:100%!important;transition:all .2s!important;box-shadow:0 4px 14px rgba(201,168,76,.22)!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 22px rgba(201,168,76,.36)!important;}

.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;color:white!important;border-radius:8px!important;}
.stTextInput>div>div>input:focus{border-color:rgba(201,168,76,.45)!important;}
.stSelectbox>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;color:white!important;}

.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03)!important;border-radius:8px!important;gap:2px!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.4)!important;font-size:13px!important;border-radius:6px!important;}
.stTabs [aria-selected="true"]{color:#C9A84C!important;background:rgba(201,168,76,.1)!important;}

.stRadio>div{flex-direction:row!important;flex-wrap:wrap!important;gap:8px!important;}
.stRadio>div>label{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important;padding:6px 12px!important;color:rgba(255,255,255,.5)!important;font-size:13px!important;}

.stExpander{border:1px solid rgba(201,168,76,.15)!important;border-radius:12px!important;background:rgba(255,255,255,.02)!important;}

@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes goldPulse{0%,100%{box-shadow:0 0 12px rgba(201,168,76,.3);transform:scale(1)}50%{box-shadow:0 0 26px rgba(201,168,76,.6);transform:scale(1.05)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

.shimmer-text{background:linear-gradient(90deg,#C9A84C 0%,#F5D68A 35%,#C9A84C 65%,#F5D68A 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:shimmer 3s linear infinite;}

.ls-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:20px;margin-bottom:14px;}
.ls-card-gold{background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.22);border-radius:16px;padding:22px;margin-bottom:14px;}

.balls-wrap{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:16px 0;}
.ball{width:50px;height:50px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:16px;font-weight:600;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);color:rgba(255,255,255,.88);transition:all .3s;}
.ball-gold{background:linear-gradient(135deg,#C9A84C,#F5D68A);border:none;color:#0a0a0f;animation:goldPulse 2.5s ease-in-out infinite;}

.gen-dots{display:flex;gap:6px;justify-content:center;margin:8px 0 6px;}
.dot{width:10px;height:10px;border-radius:50%;transition:all .3s;}
.dot-on{background:linear-gradient(135deg,#C9A84C,#F5D68A);box-shadow:0 0 8px rgba(201,168,76,.4);}
.dot-off{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);}

.src-row{display:flex;align-items:flex-start;justify-content:space-between;padding:12px 14px;border-radius:10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);margin-bottom:8px;gap:12px;}
.src-complement{background:rgba(255,255,255,.01);border-color:rgba(255,255,255,.04);}
.src-left{display:flex;align-items:flex-start;gap:10px;flex:1;min-width:0;}
.src-icon{font-size:16px;margin-top:1px;flex-shrink:0;font-family:'DM Mono',monospace;}
.src-label{font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:rgba(255,255,255,.78);}
.src-math{font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;margin-top:2px;letter-spacing:.5px;}
.src-desc{font-family:'DM Sans',sans-serif;font-size:11px;color:rgba(255,255,255,.35);line-height:1.5;margin-top:2px;}
.src-num{font-family:'DM Mono',monospace;font-size:16px;color:#C9A84C;font-weight:700;flex-shrink:0;margin-top:1px;}
.src-complement .src-num{color:rgba(255,255,255,.25);}

.lp{padding:3px 10px;border-radius:20px;font-family:'DM Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1px;text-decoration:none;border:1px solid;}
.lp-on{background:rgba(201,168,76,.15);border-color:rgba(201,168,76,.4);color:#C9A84C;}
.lp-off{background:transparent;border-color:rgba(255,255,255,.1);color:rgba(255,255,255,.3);}

.tag-gold{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;}
.metric-pill{display:inline-block;padding:4px 12px;border-radius:20px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.18);font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.jackpot-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:20px;padding:4px 12px;font-family:'DM Mono',monospace;font-size:11px;color:#C9A84C;}
.disclaimer{background:rgba(201,168,76,.04);border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:13px 15px;font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,.3);line-height:1.65;font-style:italic;margin-top:16px;}
.gold-line{width:36px;height:2px;margin:10px auto;background:linear-gradient(90deg,transparent,#C9A84C,transparent);}

.conv-wrap{text-align:center;padding:24px 0;}
.conv-ring{width:64px;height:64px;border-radius:50%;border:2px solid rgba(201,168,76,.2);border-top-color:#C9A84C;animation:spin 1s linear infinite;margin:0 auto 12px;}
.conv-label{font-family:'DM Mono',monospace;font-size:11px;color:rgba(255,255,255,.4);letter-spacing:1px;}

@media(max-width:768px){.ball{width:44px;height:44px;font-size:14px;}.src-desc{font-size:10px;}}
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

# Iconos Unicode premium — no emojis genéricos
ICONS = {
    "historico":      "⊞",  # histograma
    "community":      "⊛",  # red/comunidad
    "eventos":        "⊕",  # mundo/historia
    "fecha_personal": "✦",  # estrella personal
    "numerologia":    "ᚨ",  # runa
    "fibonacci":      "ϕ",  # phi griego
    "sagrada":        "⬡",  # hexágono sagrado
    "tesla":          "⌁",  # símbolo eléctrico
    "fractal":        "※",  # referencia fractal
    "sueno":          "∞",  # infinito/sueños
    "clima":          "≋",  # ondas clima
    "lunar":          "◐",  # fase lunar
    "cambio":         "⇌",  # tasa de cambio
    "primos":         "∴",  # números primos
    "complement":     "·",  # punto neutro
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
    "dream_title":"Dream Mode ∞","dream_placeholder":"Tell me your dream... water, the number 7, a golden door...",
    "dream_help":"Describe your dream and we extract numbers from its symbols",
    "symbolic_title":"Symbolic Systems","symbolic_help":"Select which systems to include",
    "sys_num":"ᚨ Numerology","sys_fib":"ϕ Fibonacci","sys_sag":"⬡ Sacred Geometry",
    "sys_tes":"⌁ Tesla (3·6·9)","sys_fra":"※ Fractals","sys_pri":"∴ Prime Numbers",
    "crowd_pref":"Crowd","follow":"Follow","avoid":"Avoid","balanced":"Balanced",
    "generate_btn":"Generate Combination","generating":"Converging data sources...",
    "conv_step1":"Analyzing world events...","conv_step2":"Reading community signals...",
    "conv_step3":"Computing your mathematics...","conv_step4":"Converging into your numbers...",
    "sources_title":"Where each number comes from",
    "gen_counter":"Today","email_combo":"Send to my email",
    "email_sent":"✅ Sent!","email_err":"⚠️ Configure Resend first.",
    "share_label":"Copy & share:",
    "disclaimer":"We gather and synthesize real-world data so you can play with more than just luck. Maybe you'll need a little less of it — but either way, may it always be on your side.",
    "paywall_title":"Convergence Plan","upgrade_btn":"Upgrade — $9.99/month",
    "paywall_msg":"Unlock full data convergence: historical analysis, community intelligence, world events, personal mathematics and Dream Mode.",
    "history":"My History","no_history":"No combinations yet.",
    "login_err":"❌ Incorrect credentials.","pass_mismatch":"⚠️ Passwords don't match.",
    "pass_short":"⚠️ Minimum 6 characters.","email_invalid":"⚠️ Invalid email.",
    "email_exists":"⚠️ Email already registered.",
    "sources":{
        "historico":"Draw History","community":"Community","eventos":"World Events",
        "fecha_personal":"Your Date","numerologia":"Numerology","fibonacci":"Fibonacci",
        "sagrada":"Sacred Geometry","tesla":"Tesla 3·6·9","fractal":"Fractal",
        "sueno":"Dream","clima":"Climate","lunar":"Lunar Cycle","cambio":"Exchange Rate",
        "primos":"Prime Numbers","complement":"Complement"
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
    "gen_counter":"Hoy","email_combo":"Enviar a mi correo",
    "email_sent":"✅ ¡Enviado!","email_err":"⚠️ Configura Resend primero.",
    "share_label":"Copia y comparte:",
    "disclaimer":"Recopilamos y sintetizamos información real del mundo para ponérsela en tus manos. Con esta herramienta quizás necesites un poco menos de suerte — aunque de igual forma, ¡que te acompañe siempre!",
    "paywall_title":"Plan Convergencia","upgrade_btn":"Actualizar — $9.99/mes",
    "paywall_msg":"Desbloquea la convergencia completa: análisis histórico, inteligencia de comunidad, eventos mundiales, matemática personal y Modo Sueños.",
    "history":"Mi Historial","no_history":"Aún no has generado combinaciones.",
    "login_err":"❌ Credenciales incorrectas.","pass_mismatch":"⚠️ Las contraseñas no coinciden.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ El correo ya está registrado.",
    "sources":{
        "historico":"Histórico","community":"Comunidad","eventos":"Eventos",
        "fecha_personal":"Tu Fecha","numerologia":"Numerología","fibonacci":"Fibonacci",
        "sagrada":"Geometría Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal",
        "sueno":"Sueño","clima":"Clima","lunar":"Ciclo Lunar","cambio":"Tasa de Cambio",
        "primos":"Números Primos","complement":"Complemento"
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
    "gen_counter":"Hoje","email_combo":"Enviar para meu email",
    "email_sent":"✅ Enviado!","email_err":"⚠️ Configure o Resend primeiro.",
    "share_label":"Copie e compartilhe:",
    "disclaimer":"Reunimos e sintetizamos informações reais do mundo para colocá-las nas suas mãos. Com esta ferramenta talvez você precise de um pouco menos de sorte — mas de qualquer forma, que ela sempre te acompanhe!",
    "paywall_title":"Plano Convergência","upgrade_btn":"Atualizar — $9.99/mês",
    "paywall_msg":"Desbloqueie a convergência completa: análise histórica, inteligência da comunidade, eventos mundiais, matemática pessoal e Modo Sonhos.",
    "history":"Meu Histórico","no_history":"Ainda não gerou combinações.",
    "login_err":"❌ Credenciais incorretas.","pass_mismatch":"⚠️ As senhas não coincidem.",
    "pass_short":"⚠️ Mínimo 6 caracteres.","email_invalid":"⚠️ Email inválido.",
    "email_exists":"⚠️ Email já cadastrado.",
    "sources":{
        "historico":"Histórico","community":"Comunidade","eventos":"Eventos",
        "fecha_personal":"Sua Data","numerologia":"Numerologia","fibonacci":"Fibonacci",
        "sagrada":"Geometria Sagrada","tesla":"Tesla 3·6·9","fractal":"Fractal",
        "sueno":"Sonho","clima":"Clima","lunar":"Ciclo Lunar","cambio":"Taxa de Câmbio",
        "primos":"Números Primos","complement":"Complemento"
    },
},
}
def tr(): return T[st.session_state["idioma"]]

# ==========================================
# 6. CÁLCULOS MATEMÁTICOS PUROS
# ==========================================
def calc_fibonacci(mn, mx):
    """Fibonacci reales en rango con posición y fórmula"""
    seq=[]; a,b=1,1; pos=1
    while a<=mx:
        if a>=mn: seq.append({"n":a,"pos":pos,"prev_a":b-a if pos>1 else 0,"prev_b":a})
        a,b=b,a+b; pos+=1
    # Enriquecer con fórmula
    result=[]
    for i,item in enumerate(seq):
        if i>=2:
            item["formula"]=f"{seq[i-2]['n']}+{seq[i-1]['n']}={item['n']}"
        else:
            item["formula"]=f"F{item['pos']}={item['n']}"
        result.append(item)
    return result

def calc_tesla(mn, mx):
    """Múltiplos de 3 con su multiplicación visible"""
    result=[]
    for n in range(mn, mx+1):
        if n%3==0:
            k=n//3
            result.append({"n":n,"formula":f"3×{k}={n}","cycle":n%9 if n%9!=0 else 9})
    return result

def calc_sagrada(mn, mx):
    """Números de geometría sagrada con su origen"""
    PHI=1.6180339887; PI=3.14159265358979
    result=[]
    seen=set()
    for i in range(1,50):
        v=int(PHI*i)
        if mn<=v<=mx and v not in seen:
            result.append({"n":v,"formula":f"ϕ×{i}={PHI*i:.3f}→{v}","origen":"φ"})
            seen.add(v)
        v=int(PI*i)
        if mn<=v<=mx and v not in seen:
            result.append({"n":v,"formula":f"π×{i}={PI*i:.3f}→{v}","origen":"π"})
            seen.add(v)
        v=round(PHI**2*i)
        if mn<=v<=mx and v not in seen:
            result.append({"n":v,"formula":f"ϕ²×{i}={PHI**2*i:.3f}→{v}","origen":"ϕ²"})
            seen.add(v)
    return sorted(result, key=lambda x: x["n"])

def calc_primos(mn, mx):
    """Números primos en rango"""
    def es_primo(n):
        if n<2: return False
        for i in range(2,int(n**0.5)+1):
            if n%i==0: return False
        return True
    return [n for n in range(mn,mx+1) if es_primo(n)]

def calc_numerologia(nombre, fecha_str):
    """Numerología con pasos visibles"""
    result={}
    if nombre:
        tabla={c:((ord(c.lower())-ord('a'))%9)+1 for c in 'abcdefghijklmnopqrstuvwxyz'}
        letras=[(c.upper(),tabla.get(c.lower(),0)) for c in nombre if c.isalpha()]
        suma=sum(v for _,v in letras)
        formula=" + ".join([f"{c}({v})" for c,v in letras])+f" = {suma}"
        orig=suma
        while suma>9 and suma not in [11,22,33]:
            prev=suma; suma=sum(int(d) for d in str(suma))
            formula+=f" → {suma}"
        result["nombre"]={"n":suma,"formula":formula,"maestro":suma in [11,22,33]}
    if fecha_str:
        digitos=[c for c in fecha_str if c.isdigit()]
        suma=sum(int(d) for d in digitos)
        formula=" + ".join(digitos)+f" = {suma}"
        while suma>9 and suma not in [11,22,33]:
            prev=suma; suma=sum(int(d) for d in str(suma))
            formula+=f" → {suma}"
        result["fecha"]={"n":suma,"formula":formula,"maestro":suma in [11,22,33]}
    return result

def calc_lunar():
    """Fase lunar actual — cálculo astronómico"""
    known_new=datetime(2000,1,6,18,14)
    cycle=29.53058867
    now=datetime.now()
    diff=(now-known_new).total_seconds()/(24*3600)
    phase=diff%cycle
    day=int(phase)+1
    return {"day":day,"cycle":cycle,"formula":f"Ciclo lunar día {day}/29","phase_name":
            "Nueva" if day<=2 else "Creciente" if day<=7 else "Cuarto C" if day<=9 else
            "Gibosa C" if day<=14 else "Llena" if day<=16 else "Gibosa M" if day<=22 else
            "Cuarto M" if day<=24 else "Menguante" if day<=28 else "Nueva"}

def calc_nums_fecha(fecha_str, mn, mx):
    """Extrae números reales de una fecha con su origen"""
    result=[]
    if not fecha_str: return result
    partes=[x for x in re.split(r'[-/.]',fecha_str) if x.isdigit()]
    seen=set()
    for p in partes:
        v=int(p)
        if mn<=v<=mx and v not in seen:
            result.append({"n":v,"formula":f"Día/mes/año {p} directo","origen":"fecha"})
            seen.add(v)
        if len(p)==4:
            s=int(p[-2:])
            if mn<=s<=mx and s not in seen:
                result.append({"n":s,"formula":f"{p}[-2:]={s}","origen":"año"})
                seen.add(s)
        sd=sum(int(d) for d in p)
        if mn<=sd<=mx and sd not in seen:
            result.append({"n":sd,"formula":f"Σ({'+'.join(list(p))})={sd}","origen":"suma"})
            seen.add(sd)
    return result

# ==========================================
# 7. FUENTES EXTERNAS REALES
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

def obtener_efemerides(mes, dia):
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
    """Open-Meteo — gratis, sin key, 99% uptime"""
    c=get_cache("clima")
    if c: return c
    try:
        # New York como referencia global
        r=requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01"
            "&current=temperature_2m,surface_pressure,relative_humidity_2m&timezone=auto",
            timeout=8)
        if r.status_code==200:
            curr=r.json().get("current",{})
            res={
                "temp":round(curr.get("temperature_2m",0)),
                "pressure":round(curr.get("surface_pressure",1013)),
                "humidity":round(curr.get("relative_humidity_2m",50)),
                "temp_formula":f"Temp NY hoy: {round(curr.get('temperature_2m',0))}°C",
                "pressure_formula":f"Presión: {round(curr.get('surface_pressure',1013))} hPa → {str(round(curr.get('surface_pressure',1013)))[-2:]}",
                "humidity_formula":f"Humedad: {round(curr.get('relative_humidity_2m',50))}%",
            }
            set_cache("clima",res,"open-meteo"); return res
    except: pass
    return {}

def obtener_tasa_cambio():
    """Tasa USD/EUR — gratis, sin key"""
    c=get_cache("tasa")
    if c: return c
    try:
        r=requests.get("https://api.exchangerate-api.com/v4/latest/USD",timeout=8)
        if r.status_code==200:
            rates=r.json().get("rates",{})
            eur=rates.get("EUR",0.92)
            cop=rates.get("COP",4000)
            # Extrae números del rate
            eur_str=f"{eur:.4f}".replace(".","")
            res={
                "usd_eur":eur,
                "usd_cop":cop,
                "formula_eur":f"USD/EUR={eur:.4f} → dígitos: {eur_str}",
                "nums_eur":[int(eur_str[i:i+2]) for i in range(0,len(eur_str)-1,2) if int(eur_str[i:i+2])>0],
            }
            set_cache("tasa",res,"exchangerate-api"); return res
    except: pass
    return {}

def obtener_reddit(loteria):
    """Reddit JSON público — sin autenticación"""
    tipo=f"reddit_{loteria['id']}_{date.today()}"
    c=get_cache(tipo)
    if c: return c
    headers={"User-Agent":"LuckSort/1.0 (lottery tool)"}
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
        top=[{"n":n,"count":c,"formula":f"Mencionado {c}× en r/{loteria['reddit'][0]} hoy"} for n,c in conteo.most_common(12)]
        set_cache(tipo,top,"reddit"); return top
    return []

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
# 8. PREPROCESADOR — Python calcula todo
# ==========================================
def preparar_datos(loteria, inputs):
    """
    Python pre-calcula TODOS los candidatos reales.
    Groq solo narra — nunca inventa.
    """
    mn,mx=loteria["min"],loteria["max"]
    hoy=datetime.now()
    sistemas=inputs.get("sistemas",[])

    datos={
        "fecha_hoy": {
            "texto": hoy.strftime("%B %d, %Y"),
            "dia": hoy.day,
            "mes": hoy.month,
            "anio": hoy.year,
            "nums_directos": [n for n in [hoy.day,hoy.month,hoy.year%100,hoy.day+hoy.month] if mn<=n<=mx],
            "formula_dia": f"Día {hoy.day} → {hoy.day}",
            "formula_mes": f"Mes {hoy.month} → {hoy.month}",
            "formula_suma": f"Día+Mes={hoy.day}+{hoy.month}={hoy.day+hoy.month}",
        },
        "lunar": calc_lunar(),
        "simbolicos": {},
        "candidatos_disponibles": [],
    }

    # Sistemas simbólicos — SOLO si seleccionados
    if "fibonacci" in sistemas:
        fibs=calc_fibonacci(mn,mx)
        datos["simbolicos"]["fibonacci"]=fibs
        for f in fibs:
            datos["candidatos_disponibles"].append({
                "n":f["n"],"fuente":"fibonacci",
                "math":f["formula"],
                "peso":3
            })

    if "tesla" in sistemas:
        teslas=calc_tesla(mn,mx)
        datos["simbolicos"]["tesla"]=teslas
        for t in teslas:
            datos["candidatos_disponibles"].append({
                "n":t["n"],"fuente":"tesla",
                "math":t["formula"],
                "peso":2
            })

    if "sagrada" in sistemas:
        sagrada=calc_sagrada(mn,mx)
        datos["simbolicos"]["sagrada"]=sagrada
        for s in sagrada:
            datos["candidatos_disponibles"].append({
                "n":s["n"],"fuente":"sagrada",
                "math":s["formula"],
                "peso":3
            })

    if "numerologia" in sistemas:
        num_data=calc_numerologia(inputs.get("nombre",""),inputs.get("fecha_especial",""))
        datos["simbolicos"]["numerologia"]=num_data
        for key,val in num_data.items():
            n=val["n"]
            if mn<=n<=mx:
                datos["candidatos_disponibles"].append({
                    "n":n,"fuente":"numerologia",
                    "math":val["formula"],
                    "peso":4
                })

    if "primos" in sistemas:
        primos=calc_primos(mn,mx)
        datos["simbolicos"]["primos"]=primos
        for p in primos:
            datos["candidatos_disponibles"].append({
                "n":p,"fuente":"primos",
                "math":f"{p} es primo (indivisible)",
                "peso":1
            })

    # Fecha personal
    fecha_esp=inputs.get("fecha_especial","")
    if fecha_esp:
        nums_f=calc_nums_fecha(fecha_esp,mn,mx)
        datos["fecha_personal"]=nums_f
        for nf in nums_f:
            datos["candidatos_disponibles"].append({
                "n":nf["n"],"fuente":"fecha_personal",
                "math":nf["formula"],
                "peso":4
            })

    # Lunar — siempre disponible
    luna=datos["lunar"]
    if mn<=luna["day"]<=mx:
        datos["candidatos_disponibles"].append({
            "n":luna["day"],"fuente":"lunar",
            "math":f"Luna día {luna['day']}/29 · {luna['phase_name']}",
            "peso":2
        })

    # Clima
    clima=obtener_clima()
    if clima:
        datos["clima"]=clima
        for key,val_key in [("temp","temp"),("humidity","humidity")]:
            v=clima.get(key,0)
            if mn<=v<=mx:
                datos["candidatos_disponibles"].append({
                    "n":v,"fuente":"clima",
                    "math":clima.get(f"{val_key}_formula",""),
                    "peso":2
                })
        # Presión — últimos 2 dígitos
        p_str=str(clima.get("pressure",1013))
        p2=int(p_str[-2:])
        if mn<=p2<=mx:
            datos["candidatos_disponibles"].append({
                "n":p2,"fuente":"clima",
                "math":clima.get("pressure_formula",""),
                "peso":2
            })

    # Tasa de cambio
    tasa=obtener_tasa_cambio()
    if tasa:
        datos["tasa"]=tasa
        for n in tasa.get("nums_eur",[]):
            if mn<=n<=mx:
                datos["candidatos_disponibles"].append({
                    "n":n,"fuente":"cambio",
                    "math":tasa.get("formula_eur",""),
                    "peso":1
                })

    # Fecha de hoy
    for n in datos["fecha_hoy"]["nums_directos"]:
        datos["candidatos_disponibles"].append({
            "n":n,"fuente":"eventos",
            "math":datos["fecha_hoy"]["formula_dia"] if n==hoy.day else datos["fecha_hoy"]["formula_mes"],
            "peso":1
        })

    # Wikipedia
    efem=obtener_efemerides(hoy.month,hoy.day)
    datos["efemerides_hoy"]=efem
    for ev in efem[:5]:
        year=ev.get("year",0)
        if year:
            y2=year%100
            if mn<=y2<=mx:
                datos["candidatos_disponibles"].append({
                    "n":y2,"fuente":"eventos",
                    "math":f"{year}: {ev.get('text','')[:60]}... → {year}[-2:]={y2}",
                    "peso":2
                })
            yd=sum(int(d) for d in str(year))
            if mn<=yd<=mx:
                datos["candidatos_disponibles"].append({
                    "n":yd,"fuente":"eventos",
                    "math":f"Σ({'+'.join(list(str(year)))})={yd}",
                    "peso":1
                })

    # Reddit
    reddit=obtener_reddit(loteria)
    datos["reddit"]=reddit
    for item in reddit[:8]:
        n=item.get("n",0)
        if mn<=n<=mx:
            datos["candidatos_disponibles"].append({
                "n":n,"fuente":"community",
                "math":item.get("formula",""),
                "peso":2
            })

    # Noticias
    noticias=obtener_noticias()
    datos["noticias"]=noticias
    for art in noticias[:4]:
        for n in re.findall(r'\b(\d{1,2})\b',art.get("title","")):
            v=int(n)
            if mn<=v<=mx:
                datos["candidatos_disponibles"].append({
                    "n":v,"fuente":"eventos",
                    "math":f"'{art['title'][:50]}...' → {v}",
                    "peso":1
                })

    # Fecha personal efemérides
    if fecha_esp:
        partes=[x for x in re.split(r'[-/.]',fecha_esp) if x.isdigit()]
        if len(partes)>=2:
            try:
                d_p,m_p=int(partes[0]),int(partes[1])
                if 1<=d_p<=31 and 1<=m_p<=12:
                    efem_p=obtener_efemerides(m_p,d_p)
                    datos["efemerides_personal"]=efem_p
                    for ev in efem_p[:3]:
                        year=ev.get("year",0)
                        if year:
                            y2=year%100
                            if mn<=y2<=mx:
                                datos["candidatos_disponibles"].append({
                                    "n":y2,"fuente":"fecha_personal",
                                    "math":f"Tu fecha {d_p}/{m_p}: año {year} → {y2}",
                                    "peso":3
                                })
            except: pass

    # Excluir números ya usados en sesión
    historial=st.session_state.get("historial_sesion",[])[-3:]
    usados_recientes=set()
    for gen in historial:
        usados_recientes.update(gen)

    # Marcar como ya_usado
    for cand in datos["candidatos_disponibles"]:
        cand["ya_usado"]=cand["n"] in usados_recientes

    return datos

# ==========================================
# 9. GENERACIÓN GROQ
# ==========================================
def generar_combinacion(loteria, inputs):
    lang=st.session_state["idioma"]
    lang_full={"EN":"English","ES":"Spanish","PT":"Portuguese"}[lang]

    datos=preparar_datos(loteria,inputs)

    excluir=[]
    if inputs.get("excluir"):
        try: excluir=[int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    # Filtrar candidatos válidos
    candidatos_validos=[c for c in datos["candidatos_disponibles"]
                       if c["n"] not in excluir and loteria["min"]<=c["n"]<=loteria["max"]]

    # Eliminar duplicados manteniendo mayor peso
    mejor_por_num={}
    for c in candidatos_validos:
        n=c["n"]
        if n not in mejor_por_num or c["peso"]>mejor_por_num[n]["peso"]:
            mejor_por_num[n]=c

    candidatos_unicos=list(mejor_por_num.values())
    random.shuffle(candidatos_unicos)

    # Separar: preferidos (no usados recientemente) vs usados
    preferidos=[c for c in candidatos_unicos if not c.get("ya_usado",False)]
    ya_usados=[c for c in candidatos_unicos if c.get("ya_usado",False)]
    candidatos_ordenados=preferidos+ya_usados

    historial_reciente=st.session_state.get("historial_sesion",[])[-3:]
    sueno=inputs.get("sueno","")
    bonus_inst=f"1 {loteria['bname']} (1-{loteria['bmax']})" if loteria["bonus"] else "no bonus number"
    sistemas_sel=inputs.get("sistemas",[])

    seed=random.randint(1000,9999)

    prompt=f"""You are a team of specialized experts generating a {loteria['nombre']} lottery combination.
Seed #{seed} — each generation must be unique.

LOTTERY: {loteria['nombre']} | {loteria['n']} numbers ({loteria['min']}-{loteria['max']}) | {bonus_inst}
EXCLUDE: {excluir}
CROWD PREFERENCE: {inputs.get('crowd','balanced')}
RECENT COMBINATIONS TO AVOID REPEATING: {historial_reciente}
DREAM DESCRIPTION: "{sueno if sueno else 'none'}"

═══ PRE-CALCULATED REAL DATA (Python verified) ═══
{json.dumps(candidatos_ordenados[:40], ensure_ascii=False, indent=2)}

═══ RULES — NON-NEGOTIABLE ═══
1. Choose ONLY numbers from the pre-calculated list above
2. Each number from a DIFFERENT fuente when possible
3. Maximum 1 number from "community" source
4. Maximum 1 number from "fibonacci" (if selected: {sistemas_sel})
5. Maximum 1 number from "tesla" (if selected: {sistemas_sel})
6. NEVER use a symbolic system NOT in this list: {sistemas_sel}
7. Prefer numbers where ya_usado=false
8. If dream provided → extract numbers from dream symbols as extra source "sueno"
9. All numbers must be unique and within {loteria['min']}-{loteria['max']}

═══ EXPERT VOICE RULES ═══
Each source has its specialist:
- fibonacci → mathematician: precise, references sequence position
- tesla → physicist: references the 3-6-9 cycle and reduction
- sagrada → sacred geometer: references φ or π formula
- numerologia → numerologist: shows reduction steps
- eventos/historico → historian: names the specific event/year
- community → data analyst: cites exact mention count
- clima → meteorologist: cites exact measurement
- lunar → astronomer: cites cycle day and phase
- cambio → financial analyst: cites exact rate
- sueno → dream interpreter: explains symbol meaning
- fecha_personal → personal data analyst: shows extraction math

═══ RESPONSE FORMAT ═══
Respond ONLY in {lang_full}. Return ONLY valid JSON:
{{
  "numbers": [list of {loteria['n']} integers],
  "bonus": {f'integer 1-{loteria["bmax"]}' if loteria['bonus'] else 'null'},
  "sources": [
    {{
      "number": N,
      "source": "source_type",
      "label": "expert role in {lang_full}",
      "math": "one-line formula or calculation shown",
      "explanation": "expert voice, specific, 15+ words, NO generic AI language"
    }}
  ]
}}"""

    try:
        resp=groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Expert team generating real lottery data. Respond ONLY in {lang_full}. Return ONLY valid JSON. Never fabricate data not in the pre-calculated list."},
                {"role":"user","content":prompt}
            ],
            temperature=round(random.uniform(0.65,0.88),2),
            max_tokens=1600
        )
        raw=resp.choices[0].message.content.strip()
        if "```" in raw: raw=raw.split("```")[1].replace("json","").strip()
        res=json.loads(raw)

        # Validar números
        nums=[n for n in res.get("numbers",[]) if loteria["min"]<=n<=loteria["max"] and n not in excluir]
        # Si faltan, completar con candidatos disponibles
        disponibles=[c["n"] for c in candidatos_ordenados if c["n"] not in nums and c["n"] not in excluir]
        while len(nums)<loteria["n"] and disponibles:
            nums.append(disponibles.pop(0))
        # Último recurso: aleatorio dentro del rango
        pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in nums and n not in excluir]
        while len(nums)<loteria["n"] and pool:
            p=random.choice(pool); nums.append(p); pool.remove(p)
        res["numbers"]=list(dict.fromkeys(nums))[:loteria["n"]]

        # Validar bonus
        if loteria["bonus"]:
            b=res.get("bonus")
            if not isinstance(b,int) or not (1<=b<=loteria["bmax"]):
                res["bonus"]=random.randint(1,loteria["bmax"])

        # Guardar en historial de sesión
        historial=st.session_state.get("historial_sesion",[])
        historial.append(res["numbers"])
        st.session_state["historial_sesion"]=historial[-5:]

        return res
    except:
        return generar_fallback(loteria,excluir,candidatos_ordenados)

def generar_fallback(loteria,excluir=[],candidatos=[]):
    """Fallback con candidatos reales si los hay"""
    pool_real=[c["n"] for c in candidatos if c["n"] not in excluir]
    if len(pool_real)>=loteria["n"]:
        nums=random.sample(pool_real,loteria["n"])
        sources=[]
        for n in nums:
            cand=next((c for c in candidatos if c["n"]==n),None)
            if cand:
                sources.append({"number":n,"source":cand["fuente"],"label":cand["fuente"].title(),"math":cand["math"],"explanation":"Seleccionado de fuente real verificada."})
    else:
        pool=[n for n in range(loteria["min"],loteria["max"]+1) if n not in excluir]
        nums=random.sample(pool,min(loteria["n"],len(pool)))
        sources=[{"number":n,"source":"complement","label":"·","math":"—","explanation":"Sin señal específica disponible."} for n in nums]
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    if bonus: sources.append({"number":bonus,"source":"complement","label":"·","math":"—","explanation":"Generado como complemento."})
    return {"numbers":nums,"bonus":bonus,"sources":sources}

def generar_aleatorio(loteria):
    pool=list(range(loteria["min"],loteria["max"]+1))
    nums=random.sample(pool,loteria["n"])
    bonus=random.randint(1,loteria["bmax"]) if loteria["bonus"] else None
    sources=[{"number":n,"source":"complement","label":"·","math":"—","explanation":"Generación aleatoria — plan gratuito."} for n in nums]
    if bonus: sources.append({"number":bonus,"source":"complement","label":"·","math":"—","explanation":"Bonus aleatorio."})
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
<div style="text-align:center;padding:20px 0;"><div style="display:inline-flex;align-items:center;gap:10px;">
<div style="width:32px;height:32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#0a0a0f;">◆</div>
<span style="font-size:22px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div>
<p style="color:rgba(255,255,255,.25);font-size:9px;letter-spacing:3px;margin-top:4px;">SORT YOUR LUCK</p></div>
<hr style="border:none;border-top:1px solid rgba(201,168,76,.2);margin:10px 0 20px;">
<h2>Welcome ◆</h2><p style="color:rgba(255,255,255,.6);line-height:1.7;">Your LuckSort account is ready.</p>
<div style="background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:20px;margin:20px 0;">
<ul style="color:rgba(255,255,255,.6);line-height:2.2;margin:0;padding-left:18px;">
<li>5 combinations per lottery per day</li><li>11 lotteries · 3 languages</li><li>Upgrade for full convergence + Dream Mode</li></ul></div>
<div style="text-align:center;margin:24px 0;"><a href="{APP_URL}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#C9A84C,#F5D68A);color:#0a0a0f;font-weight:700;border-radius:10px;text-decoration:none;">Open LuckSort →</a></div>
<p style="color:rgba(255,255,255,.18);font-size:11px;font-style:italic;text-align:center;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;margin-top:14px;">© 2025 LuckSort · lucksort.com</p></body></html>"""
    enviar_email(email,"Welcome to LuckSort ◆",html)

def email_combinacion(to,loteria,resultado):
    t=T[st.session_state.get("idioma","EN")]
    nums=resultado.get("numbers",[]); bonus=resultado.get("bonus"); sources=resultado.get("sources",[])
    nums_str=" · ".join([str(n).zfill(2) for n in nums])
    bonus_s=f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    src_html=""
    for s in sources:
        icon=ICONS.get(s.get("source","complement"),"·")
        src_html+=f'<div style="padding:9px 12px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);margin-bottom:6px;"><span style="font-family:monospace;">{icon}</span> <strong style="color:rgba(255,255,255,.75);">{s.get("label","")}</strong><span style="color:#C9A84C;float:right;">→ {str(s.get("number","")).zfill(2)}</span><div style="color:#C9A84C;font-family:monospace;font-size:11px;margin:2px 0;">{s.get("math","")}</div><p style="color:rgba(255,255,255,.4);font-size:11px;margin:2px 0 0;">{s.get("explanation","")}</p></div>'
    html=f"""<!DOCTYPE html><html><body style="background:#0a0a0f;color:white;font-family:Arial,sans-serif;padding:30px;max-width:580px;margin:0 auto;">
<div style="text-align:center;padding:14px 0 10px;"><div style="display:inline-flex;align-items:center;gap:8px;"><div style="width:26px;height:26px;background:linear-gradient(135deg,#C9A84C,#F5D68A);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;color:#0a0a0f;">◆</div><span style="font-size:18px;font-weight:700;font-family:Georgia,serif;">LuckSort</span></div></div>
<div style="text-align:center;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:14px;padding:20px;margin:14px 0;">
<div style="font-family:monospace;font-size:10px;color:#C9A84C;letter-spacing:3px;margin-bottom:8px;">{loteria['flag']} {loteria['nombre'].upper()}</div>
<div style="font-family:monospace;font-size:26px;font-weight:700;letter-spacing:4px;">{nums_str}{bonus_s}</div></div>
<p style="color:#C9A84C;font-size:10px;letter-spacing:2px;margin-bottom:10px;">{t['sources_title'].upper()}</p>
{src_html}<p style="color:rgba(255,255,255,.18);font-size:11px;font-style:italic;text-align:center;margin-top:16px;">"{t['disclaimer']}"</p>
<p style="text-align:center;color:rgba(255,255,255,.15);font-size:10px;margin-top:12px;">© 2025 LuckSort · lucksort.com</p></body></html>"""
    return enviar_email(to,f"◆ {loteria['nombre']} — LuckSort",html)

# ==========================================
# 12. COMPONENTES UI
# ==========================================
def render_header():
    lang=st.session_state["idioma"]
    pills={l:"lp lp-on" if l==lang else "lp lp-off" for l in ["EN","ES","PT"]}
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:14px 0 10px;border-bottom:1px solid rgba(201,168,76,0.1);margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:32px;height:32px;min-width:32px;background:linear-gradient(135deg,#C9A84C,#F5D68A);
    border-radius:9px;display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 16px rgba(201,168,76,.32);font-size:16px;color:#0a0a0f;">◆</div>
    <div>
      <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;color:white;letter-spacing:-.5px;line-height:1.1;">LuckSort</div>
      <div style="font-family:monospace;font-size:8px;color:rgba(201,168,76,.5);letter-spacing:2.5px;">SORT YOUR LUCK</div>
    </div>
  </div>
  <div style="display:flex;gap:5px;">
    <a href="?lang=EN" class="{pills['EN']}" style="text-decoration:none;">EN</a>
    <a href="?lang=ES" class="{pills['ES']}" style="text-decoration:none;">ES</a>
    <a href="?lang=PT" class="{pills['PT']}" style="text-decoration:none;">PT</a>
  </div>
</div>""", unsafe_allow_html=True)

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
            icon=ICONS.get(src,"·")
            lbl=s.get("label") or t["sources"].get(src,src)
            math_line=s.get("math","")
            exp=s.get("explanation","")
            num=s.get("number","")
            cls="src-row src-complement" if src=="complement" else "src-row"
            st.markdown(f"""
<div class="{cls}">
  <div class="src-left">
    <span class="src-icon">{icon}</span>
    <div>
      <div class="src-label">{lbl}</div>
      {f'<div class="src-math">{math_line}</div>' if math_line and math_line!="—" else ""}
      <div class="src-desc">{exp}</div>
    </div>
  </div>
  <span class="src-num">→ {str(num).zfill(2)}</span>
</div>""", unsafe_allow_html=True)

    # Compartir
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
    features=[("⊞","Draw History"),("⊛","Community"),("⊕","World Events"),("✦","Your Dates"),("ᚨ","Numerology"),("ϕ","Fibonacci"),("⬡","Sacred Geo"),("⌁","Tesla"),("◐","Lunar"),("≋","Climate"),("∞","Dream Mode")]
    pills="".join([f'<span style="font-size:11px;color:rgba(255,255,255,.35);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:4px 10px;font-family:monospace;">{i} {l}</span>' for i,l in features])
    st.markdown(f"""
<div class="ls-card" style="border-color:rgba(201,168,76,.25);text-align:center;padding:26px;">
  <div style="font-size:24px;margin-bottom:10px;">◆</div>
  <h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;font-size:19px;">{t['paywall_title']}</h3>
  <p style="color:rgba(255,255,255,.38);font-size:13px;max-width:300px;margin:0 auto 16px;line-height:1.65;">{t['paywall_msg']}</p>
  <div style="display:flex;gap:7px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;">{pills}</div>
</div>""", unsafe_allow_html=True)
    if st.button(t["upgrade_btn"],use_container_width=True,key="upgrade_btn"):
        pass

# ==========================================
# 13. SIDEBAR
# ==========================================
with st.sidebar:
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

    lang_opts={"🇺🇸 English":"EN","🇪🇸 Español":"ES","🇧🇷 Português":"PT"}
    cur=next(k for k,v in lang_opts.items() if v==st.session_state["idioma"])
    sel=st.selectbox("",list(lang_opts.keys()),index=list(lang_opts.keys()).index(cur),key="sb_lang",label_visibility="collapsed")
    if lang_opts[sel]!=st.session_state["idioma"]:
        set_lang(lang_opts[sel])
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
        if st.button(f"◆ {t['tagline']}",use_container_width=True,key="nav_g"): st.session_state["vista"]="app"; st.rerun()
        if st.button(f"📋 {t['history']}",use_container_width=True,key="nav_h"): st.session_state["vista"]="history"; st.rerun()
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:8px 0;">', unsafe_allow_html=True)
        if st.button(t["logout"],use_container_width=True,key="btn_lo"):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
            st.query_params.clear(); st.rerun()

# ==========================================
# 14. LANDING
# ==========================================
if not st.session_state["logged_in"]:
    t=tr()
    render_header()

    st.markdown(f"""
<div style="text-align:center;padding:30px 16px 14px;">
  <div class="tag-gold" style="margin-bottom:14px;"><span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span> Data Convergence Engine</div>
  <h1 style="font-family:'Playfair Display',serif;font-size:clamp(34px,7vw,70px);font-weight:700;line-height:1.05;letter-spacing:-2px;margin-bottom:14px;">
    {t['hero_1']}<br><span class="shimmer-text">{t['hero_2']}</span><br>{t['hero_3']}
  </h1>
  <p style="font-family:'DM Sans',sans-serif;font-size:clamp(14px,2vw,17px);color:rgba(255,255,255,.38);max-width:480px;margin:0 auto;line-height:1.8;">{t['hero_sub']}</p>
</div>""", unsafe_allow_html=True)

    render_balls_landing()

    col1,col2,col3=st.columns([1,2,1])
    with col2:
        if st.button(t["cta_free"],use_container_width=True,key="land_cta"):
            st.session_state["mostrar_reg"]=True; st.rerun()
        st.markdown('<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.16);letter-spacing:1.5px;margin-top:7px;">FREE · NO CREDIT CARD · ES / EN / PT</p>', unsafe_allow_html=True)

    if st.session_state.get("mostrar_reg"):
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.06);margin:18px 0;">', unsafe_allow_html=True)
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
<div style="text-align:center;padding:26px 0 14px;">
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.2);letter-spacing:3px;margin-bottom:8px;">HOW IT WORKS</div>
  <h2 style="font-family:'Playfair Display',serif;font-size:clamp(20px,3vw,34px);font-weight:700;letter-spacing:-1px;margin-bottom:4px;">Many signals. One authentic number.</h2>
  <div class="gold-line"></div>
</div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    for col,(icon,key,desc) in zip([c1,c2,c3,c4],[
        ("⊞","historico","Official draw frequencies analyzed by date and month"),
        ("⊛","community","Reddit + Google Trends — real player picks today"),
        ("⊕","eventos","Wikipedia history, headlines, climate and exchange rates"),
        ("✦","fecha_personal","Your dates · numerology · Fibonacci · Tesla · lunar cycle"),
    ]):
        with col:
            st.markdown(f'<div class="ls-card" style="text-align:center;min-height:128px;"><div style="font-family:\'DM Mono\',monospace;font-size:22px;margin-bottom:7px;color:#C9A84C;">{icon}</div><div style="font-family:\'Playfair Display\',serif;font-size:13px;font-weight:600;color:rgba(255,255,255,.85);margin-bottom:4px;">{t["sources"][key]}</div><div style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(255,255,255,.3);line-height:1.5;">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;padding:20px 0 10px;"><div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.18);letter-spacing:3px;">11 LOTTERIES · 3 LANGUAGES · DREAM MODE ∞</div></div>', unsafe_allow_html=True)
    cols=st.columns(4)
    for i,lot in enumerate(LOTERIAS):
        with cols[i%4]:
            st.markdown(f'<div style="padding:8px 10px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:8px;display:flex;align-items:center;gap:7px;margin-bottom:6px;"><span style="font-size:14px;">{lot["flag"]}</span><span style="font-size:12px;color:rgba(255,255,255,.55);">{lot["nombre"]}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="disclaimer" style="text-align:center;max-width:520px;margin:18px auto 0;">"{t["disclaimer"]}"</div>', unsafe_allow_html=True)

# ==========================================
# 15. APP
# ==========================================
elif st.session_state.get("vista")=="app":
    t=tr()
    es_free=st.session_state["user_role"]=="free"
    es_paid=st.session_state["user_role"] in ["paid","pro","convergence","admin"]

    render_header()
    st.markdown(f'<h2 style="font-family:\'Playfair Display\',serif;font-size:clamp(20px,3vw,32px);font-weight:700;letter-spacing:-1px;margin:6px 0 10px;">{t["select_lottery"]}</h2>', unsafe_allow_html=True)

    lot_names=[f"{l['flag']} {l['nombre']}  ({l['pais']})" for l in LOTERIAS]
    sel=st.selectbox("",lot_names,label_visibility="collapsed",key="lot_sel")
    loteria=next(l for l in LOTERIAS if l["nombre"] in sel)

    jackpot=obtener_jackpot(loteria["nombre"])
    if jackpot:
        st.markdown(f'<div style="margin:4px 0 10px;"><span class="jackpot-badge">◈ {t["jackpot_live"]}: {jackpot}</span></div>', unsafe_allow_html=True)

    gen_hoy=st.session_state["generaciones_hoy"].get(loteria["id"],0)
    restantes=max(0,MAX_GEN-gen_hoy)
    render_gen_dots(gen_hoy)
    st.markdown(f'<div style="text-align:center;margin:-6px 0 12px;"><span class="metric-pill">{t["gen_counter"]}: {gen_hoy}/{MAX_GEN}</span></div>', unsafe_allow_html=True)

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
                import time
                for step in [t["conv_step1"],t["conv_step2"],t["conv_step3"],t["conv_step4"]]:
                    placeholder.markdown(f'<div class="conv-wrap"><div class="conv-ring"></div><div class="conv-label">{step}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.6)
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
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:14px 0;">', unsafe_allow_html=True)
        render_resultado(st.session_state["ultima_generacion"],st.session_state["ultima_loteria"])

    if es_free:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:18px 0;">', unsafe_allow_html=True)
        render_paywall()

# ==========================================
# 16. HISTORIAL
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
                    st.markdown(f'<div class="ls-card" style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;"><span style="font-family:\'DM Mono\',monospace;font-size:11px;color:#C9A84C;">{lot["flag"]} {lot["nombre"]}</span><span style="font-family:\'DM Mono\',monospace;font-size:10px;color:rgba(255,255,255,.2);">{fecha}</span></div><div style="font-family:\'DM Mono\',monospace;font-size:18px;color:white;letter-spacing:3px;">{nums_str}{bonus_str}</div></div>', unsafe_allow_html=True)
    else:
        st.info("Sign in to see your history.")
