import streamlit as st
from groq import Groq
from supabase import create_client
from datetime import date, datetime
import requests, random, json, re, math, time
from collections import Counter

st.set_page_config(page_title="LuckSort", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")

for k, v in {
    "idioma": "ES", "logged_in": False, "user_role": "invitado",
    "user_email": "", "user_id": None, "ultima_gen": None,
    "ultima_lot": None, "ultima_mod": [], "historial": [],
    "favoritos": [], "gen_hoy": 0, "gen_fecha": str(date.today())
}.items():
    if k not in st.session_state: st.session_state[k] = v

if st.session_state["gen_fecha"] != str(date.today()):
    st.session_state["gen_hoy"] = 0
    st.session_state["gen_fecha"] = str(date.today())

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: #07070f !important; color: #e8e4d9 !important; font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0c0c1a, #07070f) !important; border-right: 1px solid rgba(201,168,76,.1) !important; }
.stButton > button { background: linear-gradient(135deg, #C9A84C, #F0C84A) !important; color: #07070f !important; font-weight: 700 !important; border: none !important; border-radius: 12px !important; width: 100% !important; padding: 13px !important; transition: all .2s !important; box-shadow: 0 4px 24px rgba(201,168,76,.2) !important; font-size: 14px !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 32px rgba(201,168,76,.38) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: rgba(255,255,255,.04) !important; border: 1px solid rgba(201,168,76,.18) !important; border-radius: 10px !important; color: #e8e4d9 !important; padding: 10px 14px !important; }
.stSelectbox > div > div { background: rgba(255,255,255,.04) !important; border: 1px solid rgba(201,168,76,.18) !important; border-radius: 10px !important; }
.streamlit-expanderHeader { background: rgba(255,255,255,.025) !important; border: 1px solid rgba(201,168,76,.1) !important; border-radius: 12px !important; color: #e8e4d9 !important; font-weight: 500 !important; padding: 14px 16px !important; transition: all .2s !important; }
.streamlit-expanderHeader:hover { border-color: rgba(201,168,76,.28) !important; }
.streamlit-expanderContent { background: rgba(255,255,255,.015) !important; border: 1px solid rgba(201,168,76,.07) !important; border-top: none !important; border-radius: 0 0 12px 12px !important; padding: 16px !important; }
.stMultiSelect > div { background: rgba(255,255,255,.04) !important; border: 1px solid rgba(201,168,76,.18) !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(201,168,76,.12) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: rgba(232,228,217,.4) !important; font-family: 'DM Mono', monospace !important; font-size: 12px !important; letter-spacing: 1px !important; border: none !important; }
.stTabs [aria-selected="true"] { color: #C9A84C !important; border-bottom: 2px solid #C9A84C !important; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes glow { 0%, 100% { box-shadow: 0 0 18px rgba(201,168,76,.2); } 50% { box-shadow: 0 0 36px rgba(201,168,76,.5); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes ballIn { from { opacity: 0; transform: scale(.7); } to { opacity: 1; transform: scale(1); } }
.ball { width: 54px; height: 54px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, rgba(255,255,255,.14), rgba(255,255,255,.03)); border: 1px solid rgba(255,255,255,.18); display: inline-flex; align-items: center; justify-content: center; font-family: 'DM Mono', monospace; font-size: 16px; font-weight: 700; color: #e8e4d9; margin: 4px; animation: ballIn .4s ease forwards; box-shadow: 0 2px 16px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.12); transition: transform .2s; }
.ball:hover { transform: scale(1.1); }
.ball-gold { background: radial-gradient(circle at 35% 30%, #F5D878, #B8922A) !important; color: #07070f !important; border: none !important; box-shadow: 0 0 28px rgba(201,168,76,.6), inset 0 1px 0 rgba(255,255,255,.5) !important; animation: ballIn .4s ease forwards, glow 2.5s ease-in-out infinite !important; }
.src-card { background: rgba(255,255,255,.02); border: 1px solid rgba(201,168,76,.1); border-radius: 14px; padding: 14px 16px; margin-bottom: 8px; display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; animation: fadeUp .4s ease forwards; transition: border-color .2s; }
.src-card:hover { border-color: rgba(201,168,76,.22); }
.src-card.comp { border-color: rgba(255,255,255,.05); opacity: .55; }
.src-icon { font-size: 17px; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: 8px; background: rgba(201,168,76,.07); flex-shrink: 0; }
.src-label { font-family: 'DM Mono', monospace; font-size: 10px; color: #C9A84C; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }
.src-math { font-family: 'DM Mono', monospace; font-size: 11px; color: rgba(201,168,76,.65); margin-bottom: 5px; }
.src-exp { font-size: 13px; color: rgba(232,228,217,.62); line-height: 1.5; }
.src-num { font-family: 'DM Mono', monospace; font-size: 24px; font-weight: 700; color: #C9A84C; flex-shrink: 0; }
.conv-wrap { text-align: center; padding: 24px 0; }
.conv-ring { width: 42px; height: 42px; border: 2px solid rgba(201,168,76,.18); border-top-color: #C9A84C; border-radius: 50%; animation: spin .8s linear infinite; margin: 0 auto 10px; }
.conv-icon { font-size: 20px; color: rgba(201,168,76,.3); margin: 6px 0; }
.conv-label { font-family: 'DM Mono', monospace; font-size: 11px; color: rgba(201,168,76,.55); letter-spacing: 2px; }
hr.g { border: none; border-top: 1px solid rgba(201,168,76,.1); margin: 14px 0; }
</style>""", unsafe_allow_html=True)

# ── CREDENCIALES ──
try:
    GROQ_KEY    = st.secrets["GROQ_API_KEY"]
    SB_URL      = st.secrets["SUPABASE_URL"]
    SB_KEY      = st.secrets["SUPABASE_KEY"]
    STRIPE_LINK = st.secrets.get("STRIPE_LINK", "#")
    ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL", "hello@lucksort.com")
    ADMIN_PASS  = st.secrets.get("ADMIN_PASS", "lucksort123")
    RAPIDAPI_KEY= st.secrets.get("RAPIDAPI_KEY", "")
except:
    st.error("Configura los secrets en Streamlit Cloud"); st.stop()

groq_cl = Groq(api_key=GROQ_KEY)
sb      = create_client(SB_URL, SB_KEY)

# ── TRADUCCIONES ──
T = {
    "ES": {
        "tag": "Ordena tu suerte", "sub": "Datos reales del mundo convergiendo en tus numeros",
        "sel": "Selecciona tu loteria", "next": "Proximo sorteo",
        "fav_t": "Favoritos", "fav_h": "Numeros que quieres incluir", "fav_sel": "Selecciona favoritos",
        "real_t": "Datos Reales", "real_h": "Historico oficial + comunidad + eventos",
        "hol_t": "Holistico", "hol_h": "Numerologia - Lunar - Suenos",
        "mat_t": "Matematico", "mat_h": "Fibonacci - Tesla - Sagrada - Primos",
        "nombre": "Tu nombre completo", "fecha": "Fecha especial (DD/MM/AA)", "sueno": "Cuentame tu sueno...",
        "excluir": "Excluir numeros (ej: 4, 13)", "gen": "Generar Combinacion",
        "donde": "DE DONDE VIENE CADA NUMERO",
        "disc": "Recopilamos informacion real del mundo. Quizas necesites un poco menos de suerte.",
        "login": "Entrar", "reg": "Crear cuenta", "email": "Correo",
        "pass": "Contrasena", "pass2": "Confirmar contrasena",
        "login_btn": "Entrar", "reg_btn": "Crear Cuenta Gratis", "logout": "Cerrar sesion",
        "exists": "Este correo ya esta registrado", "mismatch": "Las contrasenas no coinciden",
        "login_err": "Correo o contrasena incorrectos", "gen_hoy": "combinaciones hoy",
        "steps": ["Analizando senales historicas...", "Convergiendo datos...", "Calculando combinacion...", "Ordenando tu suerte..."],
        "src": {
            "historico": "Historiador", "fibonacci": "Matematico", "tesla": "Fisico",
            "sagrada": "Geometra", "primos": "Matematico", "numerologia": "Numerologo",
            "lunar": "Astronomo", "eventos": "Historiador", "community": "Analista",
            "fecha": "Tu Fecha", "favorito": "Favorito", "complement": ""
        }
    },
    "EN": {
        "tag": "Sort Your Luck", "sub": "Real world data converging into your numbers",
        "sel": "Select your lottery", "next": "Next draw",
        "fav_t": "Favourites", "fav_h": "Numbers you want to include", "fav_sel": "Select favourites",
        "real_t": "Real Data", "real_h": "Official history + community + events",
        "hol_t": "Holistic", "hol_h": "Numerology - Lunar - Dreams",
        "mat_t": "Mathematical", "mat_h": "Fibonacci - Tesla - Sacred - Primes",
        "nombre": "Your full name", "fecha": "Special date (DD/MM/YY)", "sueno": "Tell me your dream...",
        "excluir": "Exclude numbers (e.g. 4, 13)", "gen": "Generate Combination",
        "donde": "WHERE EACH NUMBER COMES FROM",
        "disc": "We gather real information from the world. You might need a little less luck.",
        "login": "Sign In", "reg": "Create Account", "email": "Email",
        "pass": "Password", "pass2": "Confirm password",
        "login_btn": "Sign In", "reg_btn": "Create Free Account", "logout": "Sign Out",
        "exists": "This email is already registered", "mismatch": "Passwords do not match",
        "login_err": "Incorrect email or password", "gen_hoy": "combinations today",
        "steps": ["Analyzing historical signals...", "Converging data...", "Calculating combination...", "Sorting your luck..."],
        "src": {
            "historico": "Historian", "fibonacci": "Mathematician", "tesla": "Physicist",
            "sagrada": "Geometer", "primos": "Mathematician", "numerologia": "Numerologist",
            "lunar": "Astronomer", "eventos": "Historian", "community": "Analyst",
            "fecha": "Your Date", "favorito": "Favourite", "complement": ""
        }
    },
    "PT": {
        "tag": "Ordene sua sorte", "sub": "Dados reais do mundo convergindo nos seus numeros",
        "sel": "Selecione sua loteria", "next": "Proximo sorteio",
        "fav_t": "Favoritos", "fav_h": "Numeros que voce quer incluir", "fav_sel": "Selecione favoritos",
        "real_t": "Dados Reais", "real_h": "Historico oficial + comunidade + eventos",
        "hol_t": "Holistico", "hol_h": "Numerologia - Lunar - Sonhos",
        "mat_t": "Matematico", "mat_h": "Fibonacci - Tesla - Sagrada - Primos",
        "nome": "Seu nome completo", "fecha": "Data especial (DD/MM/AA)", "sueno": "Me conte seu sonho...",
        "excluir": "Excluir numeros (ex: 4, 13)", "gen": "Gerar Combinacao",
        "donde": "DE ONDE VEM CADA NUMERO",
        "disc": "Coletamos informacoes reais do mundo. Talvez precise de um pouco menos de sorte.",
        "login": "Entrar", "reg": "Criar conta", "email": "E-mail",
        "pass": "Senha", "pass2": "Confirmar senha",
        "login_btn": "Entrar", "reg_btn": "Criar Conta Gratis", "logout": "Sair",
        "exists": "Este e-mail ja esta cadastrado", "mismatch": "As senhas nao coincidem",
        "login_err": "E-mail ou senha incorretos", "gen_hoy": "combinacoes hoje",
        "steps": ["Analisando sinais historicos...", "Convergindo dados...", "Calculando combinacao...", "Ordenando sua sorte..."],
        "src": {
            "historico": "Historiador", "fibonacci": "Matematico", "tesla": "Fisico",
            "sagrada": "Geometra", "primos": "Matematico", "numerologia": "Numerologo",
            "lunar": "Astronomo", "eventos": "Historiador", "community": "Analista",
            "fecha": "Sua Data", "favorito": "Favorito", "complement": ""
        }
    }
}
def t(): return T[st.session_state["idioma"]]

ICONS = {
    "historico": "⊞", "fibonacci": "ϕ", "tesla": "⌁", "sagrada": "⬡",
    "primos": "∴", "numerologia": "ᚨ", "lunar": "◐", "eventos": "⊕",
    "community": "⊛", "fecha": "◈", "favorito": "★", "complement": "·"
}

LOTERIAS = [
    {"id": 1, "nombre": "Powerball",    "flag": "🇺🇸", "min": 1, "max": 69, "n": 5, "bonus": True,  "bmax": 26, "bname": "Powerball",  "dias": ["Lun","Mie","Sab"], "hora": "22:59 ET"},
    {"id": 2, "nombre": "Mega Millions","flag": "🇺🇸", "min": 1, "max": 70, "n": 5, "bonus": True,  "bmax": 25, "bname": "Mega Ball",  "dias": ["Mar","Vie"],       "hora": "23:00 ET"},
    {"id": 3, "nombre": "EuroMillions", "flag": "🇪🇺", "min": 1, "max": 50, "n": 5, "bonus": True,  "bmax": 12, "bname": "Lucky Star", "dias": ["Mar","Vie"],       "hora": "21:00 CET"},
    {"id": 4, "nombre": "UK Lotto",     "flag": "🇬🇧", "min": 1, "max": 59, "n": 6, "bonus": False, "bmax": None,"bname": None,        "dias": ["Mie","Sab"],       "hora": "19:45 GMT"},
    {"id": 5, "nombre": "El Gordo",     "flag": "🇪🇸", "min": 1, "max": 54, "n": 5, "bonus": True,  "bmax": 10, "bname": "Reintegro", "dias": ["Dom"],             "hora": "21:25 CET"},
    {"id": 6, "nombre": "Mega-Sena",    "flag": "🇧🇷", "min": 1, "max": 60, "n": 6, "bonus": False, "bmax": None,"bname": None,        "dias": ["Mie","Sab"],       "hora": "20:00 BRT"},
    {"id": 7, "nombre": "Lotofacil",    "flag": "🇧🇷", "min": 1, "max": 25, "n": 15,"bonus": False, "bmax": None,"bname": None,        "dias": ["L-S"],             "hora": "20:00 BRT"},
    {"id": 8, "nombre": "Baloto",       "flag": "🇨🇴", "min": 1, "max": 43, "n": 6, "bonus": True,  "bmax": 16, "bname": "Balota",    "dias": ["Mie","Sab"],       "hora": "22:00 COT"},
    {"id": 9, "nombre": "La Primitiva", "flag": "🇪🇸", "min": 1, "max": 49, "n": 6, "bonus": False, "bmax": None,"bname": None,        "dias": ["Jue","Sab"],       "hora": "21:30 CET"},
    {"id": 10,"nombre": "EuroJackpot",  "flag": "🇪🇺", "min": 1, "max": 50, "n": 5, "bonus": True,  "bmax": 12, "bname": "Euro Num",  "dias": ["Mar","Vie"],       "hora": "21:00 CET"},
    {"id": 11,"nombre": "Canada Lotto", "flag": "🇨🇦", "min": 1, "max": 49, "n": 6, "bonus": True,  "bmax": 49, "bname": "Bonus",     "dias": ["Mie","Sab"],       "hora": "22:30 ET"},
]

HIST = {
    "Powerball":    {"top":[26,41,16,28,22,23,32,42,36,61,39,20,53,19,66],"cal":[26,41,16,28,22],"fri":[53,64,69,18,15],"dia":{"Mon":[26,32,22],"Wed":[41,28,23],"Sat":[26,61,22]},"mes":{1:[26,32],2:[41,22],3:[23,16],4:[26,41],5:[32,28],6:[16,61],7:[22,41],8:[28,23],9:[26,42],10:[41,36],11:[22,28],12:[16,41]}},
    "Mega Millions":{"top":[17,31,10,4,46,20,14,39,2,29,70,35,23,25,8],"cal":[17,31,10,4,46],"fri":[70,48,53,38,11],"dia":{"Tue":[17,31,4],"Fri":[31,20,14]},"mes":{1:[17,31],2:[4,46],3:[14,39],4:[17,31],5:[20,29],6:[10,35],7:[31,25],8:[17,48],9:[46,20],10:[31,39],11:[10,4],12:[46,20]}},
    "EuroMillions": {"top":[23,44,19,50,5,17,27,35,48,38,20,6,43,3,15],"cal":[23,44,19,5,17],"fri":[50,48,43,33,15],"dia":{"Tue":[23,44,5],"Fri":[44,17,27]},"mes":{1:[23,44],2:[5,17],3:[27,35],4:[48,38],5:[20,6],6:[43,3],7:[15,28],8:[37,42],9:[23,11],10:[44,33],11:[19,27],12:[35,48]}},
    "UK Lotto":     {"top":[23,38,31,25,33,11,2,40,6,39,28,44,17,1,48],"cal":[23,38,31,25,33],"fri":[48,47,44,34,13],"dia":{"Wed":[23,38,11],"Sat":[38,25,33]},"mes":{1:[23,38],2:[25,33],3:[2,40],4:[6,39],5:[28,44],6:[17,1],7:[48,13],8:[22,34],9:[23,47],10:[38,25],11:[31,11],12:[40,2]}},
    "El Gordo":     {"top":[11,23,7,33,4,15,28,6,19,35,42,2,22,38,17],"cal":[11,23,7,33,4],"fri":[54,45,42,38,35],"dia":{"Sun":[11,23,7]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[42,2],6:[22,38],7:[17,45],8:[54,31],9:[11,8],10:[23,7],11:[4,15],12:[28,23]}},
    "Mega-Sena":    {"top":[10,53,23,4,52,33,43,37,41,25,5,34,8,20,42],"cal":[10,53,23,4,52],"fri":[60,58,56,55,54],"dia":{"Wed":[10,53,23],"Sat":[33,43,37]},"mes":{1:[10,53],2:[4,52],3:[43,37],4:[41,25],5:[5,34],6:[8,20],7:[42,53],8:[11,16],9:[10,30],10:[53,23],11:[4,37],12:[25,41]}},
    "Lotofacil":    {"top":[20,5,7,12,23,11,18,24,15,3,25,9,2,13,22],"cal":[20,5,7,12,23],"fri":[25,24,22,21,19],"dia":{"Mon":[20,5],"Tue":[12,23],"Wed":[18,24],"Thu":[3,25],"Fri":[2,13],"Sat":[17,10]},"mes":{1:[20,5],2:[12,23],3:[18,24],4:[20,5],5:[3,25],6:[2,13],7:[17,10],8:[16,21],9:[5,7],10:[23,11],11:[24,15],12:[25,9]}},
    "Baloto":       {"top":[11,23,7,33,4,15,28,6,19,35,43,2,22,38,17],"cal":[11,23,7,33,4],"fri":[43,41,38,35,30],"dia":{"Wed":[11,23,7],"Sat":[15,28,6]},"mes":{1:[11,23],2:[33,4],3:[28,6],4:[19,35],5:[43,2],6:[22,38],7:[17,12],8:[30,41],9:[11,8],10:[23,7],11:[4,15],12:[28,23]}},
    "La Primitiva": {"top":[28,36,14,3,25,42,7,16,33,48,21,9,38,45,11],"cal":[28,36,14,3,25],"fri":[49,48,45,43,38],"dia":{"Thu":[28,36,14],"Sat":[42,7,16]},"mes":{1:[28,36],2:[3,25],3:[7,16],4:[33,48],5:[21,9],6:[38,45],7:[11,5],8:[19,27],9:[28,43],10:[36,14],11:[42,7],12:[16,33]}},
    "EuroJackpot":  {"top":[19,49,32,18,7,23,17,40,3,37,50,29,44,11,22],"cal":[19,49,32,18,7],"fri":[50,48,44,40,37],"dia":{"Tue":[19,49,32],"Fri":[23,17,40]},"mes":{1:[19,49],2:[18,7],3:[17,40],4:[3,37],5:[50,29],6:[44,11],7:[22,34],8:[48,15],9:[19,26],10:[49,32],11:[18,7],12:[40,3]}},
    "Canada Lotto": {"top":[20,33,34,40,44,6,19,32,43,39,7,13,24,37,16],"cal":[20,33,34,40,44],"fri":[49,48,47,46,45],"dia":{"Wed":[20,33,34],"Sat":[6,19,32]},"mes":{1:[20,33],2:[40,44],3:[19,32],4:[43,39],5:[7,13],6:[24,37],7:[16,3],8:[28,42],9:[20,14],10:[33,34],11:[40,6],12:[19,32]}},
}

# ── CALCULOS MATEMATICOS ──
def calc_fibs(mn, mx):
    result = {}; a, b = 1, 1; pos = 1
    while b <= mx:
        if mn <= b <= mx:
            result[b] = {"math": f"F{pos}: {a}+{b-a}={b}", "fuente": "fibonacci"}
        a, b = b, a + b; pos += 1
    return result

def calc_teslas(mn, mx):
    return {n: {"math": f"{n}/3={n//3} multiplo 3-6-9", "fuente": "tesla"} for n in range(mn, mx+1) if n % 3 == 0}

def calc_sagradas(mn, mx):
    result = {}
    for mult, sym in [(1.6180339887,"phi"), (math.pi,"pi"), (math.sqrt(2),"sqrt2"), (math.sqrt(3),"sqrt3")]:
        for k in range(1, 60):
            v = round(mult * k)
            if mn <= v <= mx and v not in result:
                result[v] = {"math": f"{sym}x{k}={v}", "fuente": "sagrada"}
    return result

def calc_primos(mn, mx):
    return {n: {"math": f"{n} es primo", "fuente": "primos"} for n in range(max(2,mn), mx+1) if all(n%i!=0 for i in range(2, int(n**.5)+1))}

def calc_numerologia(nombre, fecha):
    result = {}
    if nombre:
        vals = {chr(97+i): i%9+1 for i in range(26)}
        total = sum(vals.get(c.lower(), 0) for c in nombre if c.isalpha())
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(d) for d in str(total))
        if 1 <= total <= 33:
            result["nombre"] = {"n": total, "math": f"{nombre[:8]}={total}", "fuente": "numerologia"}
    if fecha:
        digits = re.findall(r'\d+', fecha)
        if digits:
            total = sum(int(d) for d in ''.join(digits))
            while total > 9 and total not in [11, 22, 33]:
                total = sum(int(d) for d in str(total))
            if 1 <= total <= 33:
                result["fecha"] = {"n": total, "math": f"{fecha}={total}", "fuente": "numerologia"}
    return result

def calc_lunar():
    dias = (datetime.now() - datetime(2000, 1, 6)).days
    fase = round(dias % 29.53)
    return {"n": min(fase, 28), "math": f"Luna dia {fase} del ciclo", "fuente": "lunar"}

# ── CACHE ──
def get_cache(tipo):
    try:
        r = sb.table("cache_diario").select("contenido").eq("fecha", str(date.today())).eq("tipo", tipo).execute()
        if r.data:
            c = r.data[0]["contenido"]
            return json.loads(c) if isinstance(c, str) else c
    except: pass
    return None

def set_cache(tipo, data):
    try:
        hoy = str(date.today()); val = json.dumps(data, ensure_ascii=False)
        ex = sb.table("cache_diario").select("id").eq("fecha", hoy).eq("tipo", tipo).execute()
        if ex.data: sb.table("cache_diario").update({"contenido": val}).eq("id", ex.data[0]["id"]).execute()
        else: sb.table("cache_diario").insert({"fecha": hoy, "tipo": tipo, "contenido": val}).execute()
    except: pass

def obtener_reddit(loteria):
    tipo = f"reddit_{loteria['id']}"; c = get_cache(tipo)
    if c: return c
    mn, mx = loteria["min"], loteria["max"]
    subs = {"Powerball":"powerball","Mega Millions":"megamillions","EuroMillions":"euromillions",
            "UK Lotto":"uklottery","Baloto":"colombia","Mega-Sena":"megasena","El Gordo":"spain",
            "La Primitiva":"spain","EuroJackpot":"eurojackpot","Canada Lotto":"lottery","Lotofacil":"brasil"}
    sub = subs.get(loteria["nombre"], "lottery"); nums = []
    headers = {"User-Agent": "Mozilla/5.0 LuckSort/1.0"}

    # Fuente 1: Arctic Shift (Pushshift alternativo gratuito, sin API key)
    try:
        r = requests.get(
            f"https://arctic-shift.photon-reddit.com/api/posts/search",
            params={"subreddit": sub, "limit": "25", "sort": "desc"},
            headers=headers, timeout=8)
        if r.status_code == 200:
            posts = r.json().get("data", [])
            for p in posts:
                txt = str(p.get("title","")) + str(p.get("selftext",""))
                for n in re.findall(r"(\d{1,2})", txt):
                    v = int(n)
                    if mn <= v <= mx: nums.append(v)
    except: pass

    # Fuente 2: RapidAPI Reddit (si tiene key)
    if not nums and RAPIDAPI_KEY:
        try:
            r = requests.get(
                "https://reddit34.p.rapidapi.com/getPostsBySubreddit",
                headers={"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "reddit34.p.rapidapi.com"},
                params={"subreddit": sub, "sort": "hot", "limit": "20"},
                timeout=8)
            if r.status_code == 200:
                posts = r.json().get("data", {}).get("children", [])
                for p in posts:
                    txt = str(p.get("data",{}).get("title","")) + str(p.get("data",{}).get("selftext",""))
                    for n in re.findall(r"(\d{1,2})", txt):
                        v = int(n)
                        if mn <= v <= mx: nums.append(v)
        except: pass

    # Fuente 3: Reddit JSON directo
    if not nums:
        try:
            r = requests.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=20",
                headers=headers, timeout=6)
            if r.status_code == 200:
                for p in r.json().get("data", {}).get("children", []):
                    txt = str(p.get("data",{}).get("title","")) + str(p.get("data",{}).get("selftext",""))
                    for n in re.findall(r"(\d{1,2})", txt):
                        v = int(n)
                        if mn <= v <= mx: nums.append(v)
        except: pass

    if nums:
        top = [{"n": n, "count": c} for n, c in Counter(nums).most_common(10)]
        set_cache(tipo, top); return top
    return []

def obtener_efemerides(mes, dia):
    tipo = f"efem_{mes}_{dia}"; c = get_cache(tipo)
    if c: return c
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{mes}/{dia}", timeout=6)
        if r.status_code == 200:
            evs = [{"year": e.get("year"), "text": e.get("text","")[:100]} for e in r.json().get("events",[])[:8]]
            set_cache(tipo, evs); return evs
    except: pass
    return []

# ── PREPARAR CONTEXTO ──
def preparar_contexto(loteria, inputs, modulos):
    """
    Prepara los datos para Groq Y los sets matematicos para la asignacion
    de fuentes DESPUES de que Groq responda.
    Retorna: (candidatos_para_groq, sets_matematicos, datos_extras)
    """
    mn, mx = loteria["min"], loteria["max"]
    hoy = datetime.now()
    dia_str = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][hoy.weekday()]
    mes = hoy.month
    hist = HIST.get(loteria["nombre"], {})

    # Calcular sets matematicos AQUI - son la verdad absoluta
    FIBS     = calc_fibs(mn, mx)     if "math" in modulos else {}
    TESLAS   = calc_teslas(mn, mx)   if "math" in modulos else {}
    SAGRADAS = calc_sagradas(mn, mx) if "math" in modulos else {}
    PRIMOS   = calc_primos(mn, mx)   if "math" in modulos else {}

    # Calcular numerologia
    NUMS_HOL = {}
    LUNAR_N  = None
    if "holistic" in modulos:
        nombre = inputs.get("nombre","")
        fecha  = inputs.get("fecha","")
        for v in calc_numerologia(nombre, fecha).values():
            if mn <= v["n"] <= mx: NUMS_HOL[v["n"]] = v
        lu = calc_lunar()
        if mn <= lu["n"] <= mx: LUNAR_N = lu

    # Comunidad
    COMMUNITY = {}
    if "real" in modulos:
        for item in obtener_reddit(loteria)[:8]:
            COMMUNITY[item["n"]] = {"count": item.get("count",0), "math": f"Mencionado {item.get('count',0)}x en comunidad"}

    # Eventos
    EVENTOS = {}
    if "real" in modulos:
        efem = obtener_efemerides(hoy.month, hoy.day)
        for ev in efem[:5]:
            yr = ev.get("year", 0)
            if yr:
                y2 = yr % 100
                if mn <= y2 <= mx:
                    EVENTOS[y2] = {"math": f"{yr}: {ev.get('text','')[:35]}...", "year": yr}

    # Construir lista de candidatos para Groq
    candidatos = []
    usados = set()
    for g in st.session_state.get("historial",[])[-3:]: usados.update(g)

    favoritos = st.session_state.get("favoritos", [])

    # Favoritos primero
    for n in favoritos:
        if mn <= n <= mx:
            candidatos.append({"n": n, "fuente": "favorito", "peso": 8, "ya_usado": n in usados,
                                "math": "Tu numero favorito"})

    # Matematicos (si activo)
    if "math" in modulos:
        for n, d in FIBS.items():
            candidatos.append({"n": n, "fuente": "fibonacci", "peso": 7, "ya_usado": n in usados, "math": d["math"]})
        for n, d in TESLAS.items():
            candidatos.append({"n": n, "fuente": "tesla", "peso": 6, "ya_usado": n in usados, "math": d["math"]})
        for n, d in SAGRADAS.items():
            candidatos.append({"n": n, "fuente": "sagrada", "peso": 6, "ya_usado": n in usados, "math": d["math"]})
        for n, d in PRIMOS.items():
            candidatos.append({"n": n, "fuente": "primos", "peso": 6, "ya_usado": n in usados, "math": d["math"]})

    # Holistico (si activo)
    if "holistic" in modulos:
        for n, d in NUMS_HOL.items():
            candidatos.append({"n": n, "fuente": "numerologia", "peso": 7, "ya_usado": n in usados, "math": d["math"]})
        if LUNAR_N:
            candidatos.append({"n": LUNAR_N["n"], "fuente": "lunar", "peso": 5, "ya_usado": LUNAR_N["n"] in usados, "math": LUNAR_N["math"]})

    # Real (si activo)
    if "real" in modulos:
        for n, d in COMMUNITY.items():
            candidatos.append({"n": n, "fuente": "community", "peso": 4, "ya_usado": n in usados, "math": d["math"]})
        for n, d in EVENTOS.items():
            candidatos.append({"n": n, "fuente": "eventos", "peso": 3, "ya_usado": n in usados, "math": d["math"]})
        for i, n in enumerate(hist.get("top",[])[:10]):
            candidatos.append({"n": n, "fuente": "historico", "peso": 4, "ya_usado": n in usados,
                                "math": f"Top historico #{i+1} en {loteria['nombre']}"})
        for n in hist.get("dia",{}).get(dia_str,[])[:3]:
            candidatos.append({"n": n, "fuente": "historico", "peso": 5, "ya_usado": n in usados,
                                "math": f"Mas frecuente los {dia_str}"})
        for n in hist.get("mes",{}).get(mes,[])[:3]:
            candidatos.append({"n": n, "fuente": "historico", "peso": 5, "ya_usado": n in usados,
                                "math": f"Lidera frecuencia mes {mes}"})
        for n in hist.get("cal",[])[:3]:
            candidatos.append({"n": n, "fuente": "historico", "peso": 4, "ya_usado": n in usados,
                                "math": "Numero caliente - salio recientemente"})

    # Fallback si no hay modulos
    if not any(m in modulos for m in ["real","math","holistic"]):
        for i, n in enumerate(hist.get("top",[])[:10]):
            candidatos.append({"n": n, "fuente": "historico", "peso": 3, "ya_usado": n in usados,
                                "math": f"Top historico #{i+1}"})

    # Deduplicar por mejor peso
    mejor = {}
    for c in candidatos:
        n = c["n"]
        if mn <= n <= mx and (n not in mejor or c["peso"] > mejor[n]["peso"]):
            mejor[n] = c

    candidatos_unicos = sorted(mejor.values(), key=lambda x: -x["peso"])

    # Sets matematicos para post-proceso
    sets_mat = {
        "fibs": set(FIBS.keys()),
        "teslas": set(TESLAS.keys()),
        "sagradas": set(SAGRADAS.keys()),
        "primos": set(PRIMOS.keys()),
        "numerologia": set(NUMS_HOL.keys()),
        "lunar": {LUNAR_N["n"]} if LUNAR_N else set(),
        "community": set(COMMUNITY.keys()),
        "eventos": set(EVENTOS.keys()),
        "favoritos": set(n for n in favoritos if mn<=n<=mx),
        "fibs_data": FIBS,
        "teslas_data": TESLAS,
        "sagradas_data": SAGRADAS,
        "primos_data": PRIMOS,
        "numerologia_data": NUMS_HOL,
        "lunar_data": LUNAR_N,
        "community_data": COMMUNITY,
        "eventos_data": EVENTOS,
        "historico_data": {n: {"math": c["math"]} for n, c in mejor.items() if c["fuente"] == "historico"},
    }

    return candidatos_unicos, sets_mat

def determinar_fuente(numero, sets_mat, modulos):
    """
    Determina la fuente real de un numero mirando los sets matematicos.
    Esta es la UNICA fuente de verdad - no Groq.
    """
    # Prioridad: favorito > fibonacci > numerologia > tesla > sagrada > primos > lunar > community > eventos > historico
    if numero in sets_mat["favoritos"]:
        data = sets_mat["fibs_data"].get(numero, {})
        return "favorito", "Tu numero favorito"

    if "math" in modulos:
        if numero in sets_mat["fibs"]:
            return "fibonacci", sets_mat["fibs_data"][numero]["math"]
        if numero in sets_mat["teslas"]:
            return "tesla", sets_mat["teslas_data"][numero]["math"]
        if numero in sets_mat["sagradas"]:
            return "sagrada", sets_mat["sagradas_data"][numero]["math"]
        if numero in sets_mat["primos"]:
            return "primos", sets_mat["primos_data"][numero]["math"]

    if "holistic" in modulos:
        if numero in sets_mat["numerologia"]:
            return "numerologia", sets_mat["numerologia_data"][numero]["math"]
        if numero in sets_mat["lunar"]:
            return "lunar", sets_mat["lunar_data"]["math"] if sets_mat["lunar_data"] else ""

    if "real" in modulos:
        if numero in sets_mat["community"]:
            return "community", sets_mat["community_data"][numero]["math"]
        if numero in sets_mat["eventos"]:
            return "eventos", sets_mat["eventos_data"][numero]["math"]

    hist_data = sets_mat.get("historico_data", {})
    if numero in hist_data:
        return "historico", hist_data[numero]["math"]

    return "complement", ""

# ── GENERAR ──
def generar(loteria, inputs, modulos):
    lang = st.session_state["idioma"]
    lang_full = {"ES":"Spanish","EN":"English","PT":"Portuguese"}[lang]
    mn, mx = loteria["min"], loteria["max"]

    candidatos, sets_mat = preparar_contexto(loteria, inputs, modulos)

    excluir = []
    if inputs.get("excluir"):
        try: excluir = [int(x.strip()) for x in inputs["excluir"].split(",") if x.strip().isdigit()]
        except: pass

    validos = [c for c in candidatos if c["n"] not in excluir]
    fav = st.session_state.get("favoritos", [])
    seed = random.randint(1000, 9999)
    bonus_txt = f"1 {loteria['bname']} 1-{loteria['bmax']} (pool SEPARADO)" if loteria["bonus"] else "sin bonus"
    hist = HIST.get(loteria["nombre"], {})

    # ── PRE-SELECCIÓN PYTHON — garantiza distribución entre módulos ──
    preseleccion = []
    usados_pre = set(fav) & set(c["n"] for c in validos)

    # 1. Favoritos primero
    for n in fav:
        if any(c["n"]==n for c in validos) and n not in [p["n"] for p in preseleccion]:
            preseleccion.append({"n":n,"fuente":"favorito"})

    # 2. Un número obligatorio de cada módulo activo
    if "math" in modulos:
        for fuente in ["fibonacci","tesla","sagrada","primos"]:
            candidatos_f = [c for c in validos if c["fuente"]==fuente and c["n"] not in [p["n"] for p in preseleccion]]
            if candidatos_f and len(preseleccion) < loteria["n"]:
                elegido = random.choice(candidatos_f[:3])
                preseleccion.append({"n":elegido["n"],"fuente":fuente})
                break

    if "holistic" in modulos:
        for fuente in ["numerologia","lunar"]:
            candidatos_f = [c for c in validos if c["fuente"]==fuente and c["n"] not in [p["n"] for p in preseleccion]]
            if candidatos_f and len(preseleccion) < loteria["n"]:
                elegido = candidatos_f[0]
                preseleccion.append({"n":elegido["n"],"fuente":fuente})
                break

    if "real" in modulos:
        # Comunidad primero
        candidatos_comm = [c for c in validos if c["fuente"]=="community" and c["n"] not in [p["n"] for p in preseleccion]]
        if candidatos_comm and len(preseleccion) < loteria["n"]:
            preseleccion.append({"n":candidatos_comm[0]["n"],"fuente":"community"})
        # Histórico
        candidatos_hist = [c for c in validos if c["fuente"]=="historico" and c["n"] not in [p["n"] for p in preseleccion]]
        if candidatos_hist and len(preseleccion) < loteria["n"]:
            preseleccion.append({"n":candidatos_hist[0]["n"],"fuente":"historico"})

    # 3. Completar con mejores candidatos disponibles
    nums_pre = [p["n"] for p in preseleccion]
    restantes = [c for c in validos if c["n"] not in nums_pre]
    while len(preseleccion) < loteria["n"] and restantes:
        preseleccion.append({"n":restantes[0]["n"],"fuente":restantes[0]["fuente"]})
        restantes.pop(0)

    # Lista final para Groq — ya distribuida
    nums_fijos = [p["n"] for p in preseleccion]

    prompt = f"""Genera narrativas expertas para esta combinacion de loteria.
LOTERIA: {loteria['nombre']} | IDIOMA: {lang_full}
MODULOS: {modulos}
SUENO: "{inputs.get('sueno','ninguno')}"

NUMEROS YA ELEGIDOS (no cambiar): {nums_fijos}
BONUS SEPARADO: {f'elige 1 numero entre 1-{loteria["bmax"]}' if loteria["bonus"] else 'null'}

DATOS DE CANDIDATOS:
{json.dumps([c for c in validos if c["n"] in nums_fijos], ensure_ascii=False)}

INSTRUCCION: Escribe una narrativa experta en {lang_full} para cada numero segun su fuente:
- fibonacci: formula exacta F(n-1)+F(n-2)=N y posicion en la secuencia
- tesla: N es multiplo de 3, patron 3-6-9
- sagrada: N = phi x K proporcion aurea  
- primos: N es primo — sus propiedades matematicas
- numerologia: reduccion paso a paso del nombre/fecha
- lunar: fase lunar actual dia N del ciclo
- community: mencionado X veces en la comunidad
- historico: frecuencia especifica en {loteria['nombre']} — mes, dia de sorteo
- favorito: confirmar preferencia del usuario
5. Bonus de pool SEPARADO: {f'elige entre 1-{loteria["bmax"]}' if loteria["bonus"] else 'null'}

Para cada numero, escribe una narrativa experta en {lang_full}:
- fibonacci: menciona la posicion en la secuencia y la formula
- tesla: menciona el patron 3-6-9
- sagrada: menciona la proporcion aurea phi
- primos: menciona la indivisibilidad
- numerologia: menciona la reduccion del nombre o fecha
- lunar: menciona el ciclo lunar
- community: menciona las menciones en la comunidad
- historico: menciona la frecuencia historica
- favorito: confirma la preferencia del usuario

Responde SOLO JSON sin markdown:
{{"bonus": {"entero 1-" + str(loteria["bmax"]) if loteria["bonus"] else "null"}, "explanations": {{"N": "narrativa experta en {lang_full} para el numero N"}}}}"""

    try:
        resp = groq_cl.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Eres LuckSort. Solo JSON valido sin markdown. En {lang_full}."},
                {"role":"user","content":prompt}
            ],
            temperature=round(random.uniform(0.65, 0.85), 2),
            max_tokens=1200
        )
        raw = resp.choices[0].message.content.strip()
        if "```" in raw: raw = raw.split("```")[1].replace("json","").strip()
        groq_res = json.loads(raw)

        # Validar y completar numeros
        nums = [n for n in groq_res.get("numbers",[]) if mn<=n<=mx and n not in excluir]
        for f in fav:
            if mn<=f<=mx and f not in excluir and f not in nums and len(nums)<loteria["n"]:
                nums.insert(0, f)
        pool = [c["n"] for c in validos if c["n"] not in nums]
        while len(nums) < loteria["n"] and pool: nums.append(pool.pop(0))
        pool2 = [n for n in range(mn, mx+1) if n not in nums and n not in excluir]
        while len(nums) < loteria["n"] and pool2:
            p = random.choice(pool2); nums.append(p); pool2.remove(p)
        nums = list(dict.fromkeys(nums))[:loteria["n"]]

        # Validar bonus
        bonus = None
        if loteria["bonus"]:
            b = groq_res.get("bonus")
            if isinstance(b, int) and 1<=b<=loteria["bmax"]: bonus = b
            else:
                bc = [c["n"] for c in validos if 1<=c["n"]<=loteria["bmax"] and c["n"] not in nums]
                bonus = bc[0] if bc else random.randint(1, loteria["bmax"])

        explanations = groq_res.get("explanations", {})

        # ── POST-PROCESO: fuente por Python, narrativa por Groq ──
        sources = []
        for p in preseleccion:
            n = p["n"]
            fuente, math_txt = determinar_fuente(n, sets_mat, modulos)
            expl = explanations.get(str(n), explanations.get(n, ""))
            # Si Groq no dio narrativa, generar una automatica
            if not expl:
                expl = {
                    "fibonacci": f"El {n} pertenece a la secuencia de Fibonacci — aparece de forma natural en la matematica",
                    "tesla": f"El {n} es multiplo de 3, alineado con el patron 3-6-9 de Tesla",
                    "sagrada": f"El {n} sigue la proporcion aurea phi — numero de la geometria sagrada",
                    "primos": f"El {n} es primo — indivisible, unico en su posicion matematica",
                    "numerologia": f"El {n} emerge de la reduccion numerologica de tus datos personales",
                    "lunar": f"El {n} corresponde al dia {n} del ciclo lunar actual",
                    "community": f"El {n} fue destacado por la comunidad de jugadores",
                    "historico": f"El {n} lidera la frecuencia historica en {loteria['nombre']}",
                    "favorito": f"El {n} es tu numero favorito — incluido por tu preferencia",
                    "eventos": f"El {n} esta vinculado a eventos historicos de esta fecha",
                }.get(fuente, f"El {n} fue seleccionado por convergencia de datos")
            sources.append({
                "number": n,
                "source": fuente,
                "math": math_txt,
                "explanation": expl
            })

        # Bonus tambien
        if bonus:
            fuente_b, math_b = determinar_fuente(bonus, sets_mat, modulos)
            sources.append({
                "number": bonus,
                "source": fuente_b,
                "math": math_b,
                "explanation": f"Bonus {loteria['bname']}"
            })

        h = st.session_state.get("historial",[]); h.append(nums); st.session_state["historial"] = h[-5:]
        return {"numbers": nums, "bonus": bonus, "sources": sources}

    except Exception as e:
        # Fallback
        top = [c for c in validos if c["n"] not in excluir][:loteria["n"]+3]
        nums = [c["n"] for c in top[:loteria["n"]]]
        bonus = random.randint(1, loteria["bmax"]) if loteria["bonus"] else None
        sources = []
        for c in top[:loteria["n"]]:
            fuente, math_txt = determinar_fuente(c["n"], sets_mat, modulos)
            narrativa_fallback = {
                "fibonacci": f"El {c['n']} pertenece a la secuencia de Fibonacci — aparece de forma natural en la matematica universal",
                "tesla": f"El {c['n']} es multiplo de 3, alineado con el patron 3-6-9 de Tesla",
                "sagrada": f"El {c['n']} sigue la proporcion aurea phi — numero de la geometria sagrada",
                "primos": f"El {c['n']} es primo — indivisible, unico en su posicion matematica",
                "numerologia": f"El {c['n']} emerge de la reduccion numerologica de tus datos personales",
                "lunar": f"El {c['n']} corresponde al dia del ciclo lunar actual",
                "community": f"El {c['n']} fue mencionado por la comunidad de jugadores esta semana",
                "historico": f"El {c['n']} lidera la frecuencia historica en {loteria['nombre']}",
                "favorito": f"El {c['n']} es tu numero favorito — incluido por tu preferencia",
                "eventos": f"El {c['n']} esta vinculado a eventos historicos de esta fecha",
            }.get(fuente, f"El {c['n']} fue seleccionado por convergencia de datos")
            sources.append({"number":c["n"],"source":fuente,"math":math_txt,"explanation":narrativa_fallback})
        if bonus:
            fuente_b, math_b = determinar_fuente(bonus, sets_mat, modulos)
            sources.append({"number":bonus,"source":fuente_b,"math":math_b,"explanation":f"Bonus {loteria.get('bname','')} seleccionado por frecuencia"})
        return {"numbers": nums, "bonus": bonus, "sources": sources}

# ── SUPABASE ──
def registrar(email, pw):
    try:
        if sb.table("usuarios").select("email").eq("email",email).execute().data: return False,"exists"
        sb.table("usuarios").insert({"email":email,"password":pw,"role":"free"}).execute()
        r = sb.table("usuarios").select("*").eq("email",email).execute()
        return (True,r.data[0]) if r.data else (False,"error")
    except Exception as e: return False,str(e)

def login_db(email, pw):
    try:
        r = sb.table("usuarios").select("*").eq("email",email).eq("password",pw).execute()
        return (True,r.data[0]) if r.data else (False,None)
    except: return False,None

# ── RENDER RESULTADO ──
def render_resultado(res, loteria, modulos):
    t_ = t(); nums = res.get("numbers",[]); bonus = res.get("bonus"); sources = res.get("sources",[])
    if "math" in modulos: tema="MATHEMATICAL"; tc="#7B9FCC"
    elif "holistic" in modulos: tema="HOLISTIC"; tc="#9B8FCC"
    else: tema="REAL DATA"; tc="#C9A84C"

    balls = "".join([f'<div class="ball">{str(n).zfill(2)}</div>' for n in nums])
    if bonus: balls += f'<div class="ball ball-gold">{str(bonus).zfill(2)}</div>'
    bonus_lbl = f'<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.22);text-align:center;margin-top:4px;">◆ {loteria["bname"]}: {str(bonus).zfill(2)}</div>' if bonus and loteria.get("bname") else ""

    st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.18);border-radius:18px;padding:20px;text-align:center;animation:fadeUp .5s ease;margin-bottom:16px;">
<div style="font-family:DM Mono,monospace;font-size:9px;color:{tc};letter-spacing:3px;margin-bottom:8px;">{loteria['flag']} {loteria['nombre'].upper()} · {tema}</div>
<div style="display:flex;flex-wrap:wrap;justify-content:center;">{balls}</div>{bonus_lbl}
</div>""", unsafe_allow_html=True)

    if sources:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(201,168,76,.35);letter-spacing:3px;margin:16px 0 10px;">{t_["donde"]}</div>', unsafe_allow_html=True)
        for src in sources:
            fuente = src.get("source","complement")
            icon   = ICONS.get(fuente,"·")
            label  = t_["src"].get(fuente, fuente)
            math_txt = src.get("math","")
            expl   = src.get("explanation","")
            num    = src.get("number","")
            cls    = "src-card comp" if fuente=="complement" else "src-card"
            st.markdown(f"""<div class="{cls}">
<div style="display:flex;align-items:flex-start;gap:12px;flex:1;">
<span class="src-icon">{icon}</span><div>
<div class="src-label">{label}</div>
<div class="src-math">{math_txt}</div>
<div class="src-exp">{expl}</div>
</div></div><div class="src-num">→ {str(num).zfill(2)}</div></div>""", unsafe_allow_html=True)

    st.markdown(f'<div style="font-style:italic;font-size:12px;color:rgba(232,228,217,.25);text-align:center;padding:14px 8px;">"{t_["disc"]}"</div>', unsafe_allow_html=True)
    nums_str = " · ".join([str(n).zfill(2) for n in nums])
    bonus_str = f" ◆ {str(bonus).zfill(2)}" if bonus else ""
    st.code(f"LuckSort {loteria['nombre']}: {nums_str}{bonus_str}\nlucksort.com", language=None)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""<div style="padding:14px 0 8px;text-align:center;">
<div style="font-family:'Playfair Display',serif;font-size:17px;color:#C9A84C;font-weight:700;">◆ LuckSort</div>
<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(201,168,76,.3);letter-spacing:2px;margin-top:2px;">SORT YOUR LUCK</div>
</div>""", unsafe_allow_html=True)
    st.markdown('<hr class="g">', unsafe_allow_html=True)
    lang_act = st.session_state["idioma"]
    nuevo = st.selectbox("Idioma / Language", ["ES","EN","PT"], index=["ES","EN","PT"].index(lang_act), key="sel_idioma")
    if nuevo != lang_act: st.session_state["idioma"]=nuevo; st.rerun()
    st.markdown('<hr class="g">', unsafe_allow_html=True)
    if not st.session_state["logged_in"]:
        tab1, tab2 = st.tabs([t()["login"], t()["reg"]])
        with tab1:
            em = st.text_input(t()["email"], key="l_em")
            pw = st.text_input(t()["pass"], type="password", key="l_pw")
            if st.button(t()["login_btn"], key="btn_li"):
                if em==ADMIN_EMAIL and pw==ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":em,"user_id":None}); st.rerun()
                else:
                    ok,d = login_db(em,pw)
                    if ok: st.session_state.update({"logged_in":True,"user_role":d.get("role","free"),"user_email":d["email"],"user_id":d.get("id")}); st.rerun()
                    else: st.error(t()["login_err"])
        with tab2:
            re_em = st.text_input(t()["email"],key="r_em"); re_pw=st.text_input(t()["pass"],type="password",key="r_pw"); re_pw2=st.text_input(t()["pass2"],type="password",key="r_pw2")
            if st.button(t()["reg_btn"],key="btn_ri"):
                if re_pw!=re_pw2: st.error(t()["mismatch"])
                elif re_em and len(re_pw)>=6:
                    ok,res=registrar(re_em,re_pw)
                    if ok: st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_em,"user_id":res.get("id")}); st.rerun()
                    elif res=="exists": st.error(t()["exists"])
                    else: st.error(f"Error: {res}")
    else:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.55);text-align:center;">{st.session_state["user_email"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;margin:6px 0;"><span style="font-family:DM Mono,monospace;font-size:10px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);padding:3px 10px;border-radius:20px;color:#C9A84C;">{st.session_state["user_role"].upper()}</span></div>', unsafe_allow_html=True)
        if st.button(t()["logout"],key="btn_lo"):
            for k,v in {"logged_in":False,"user_role":"invitado","user_email":"","user_id":None,"ultima_gen":None,"ultima_lot":None,"ultima_mod":[]}.items():
                st.session_state[k]=v
            st.rerun()

# ── HEADER ──
lang = st.session_state["idioma"]
st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid rgba(201,168,76,.08);margin-bottom:12px;">
<div style="display:flex;align-items:center;gap:10px;">
<div style="width:34px;height:34px;background:linear-gradient(135deg,#C9A84C,#F0C84A);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#07070f;box-shadow:0 0 18px rgba(201,168,76,.3);animation:glow 3s ease-in-out infinite;">◆</div>
<div><div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:white;line-height:1.1;">LuckSort</div>
<div style="font-family:DM Mono,monospace;font-size:8px;color:rgba(201,168,76,.4);letter-spacing:2.5px;">SORT YOUR LUCK</div></div></div>
<span style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.45);letter-spacing:1px;">{lang}</span>
</div>""", unsafe_allow_html=True)

# ── LANDING ──
if not st.session_state["logged_in"]:
    t_ = t()
    st.markdown(f"""<div style="text-align:center;padding:20px 16px 12px;">
<div style="display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;background:rgba(201,168,76,.07);border:1px solid rgba(201,168,76,.18);font-family:DM Mono,monospace;font-size:10px;color:#C9A84C;letter-spacing:2px;margin-bottom:16px;">
<span style="width:5px;height:5px;border-radius:50%;background:#C9A84C;display:inline-block;box-shadow:0 0 6px #C9A84C;"></span>DATA CONVERGENCE ENGINE</div>
<h1 style="font-family:'Playfair Display',serif;font-size:clamp(28px,7vw,52px);font-weight:700;line-height:1.05;letter-spacing:-1.5px;color:white;margin-bottom:10px;">{t_['tag']}</h1>
<p style="font-size:15px;color:rgba(232,228,217,.38);max-width:400px;margin:0 auto;line-height:1.8;">{t_['sub']}</p>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="text-align:center;margin:16px 0 20px;">
<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(255,255,255,.14);letter-spacing:3px;margin-bottom:12px;">LIVE PREVIEW · POWERBALL</div>
<div style="display:flex;justify-content:center;flex-wrap:wrap;margin-bottom:14px;">
<div class="ball" id="pb0">07</div><div class="ball" id="pb1">14</div><div class="ball" id="pb2">23</div>
<div class="ball" id="pb3">34</div><div class="ball" id="pb4">55</div><div class="ball ball-gold" id="pb5">12</div>
</div>
<div style="display:flex;flex-direction:column;gap:6px;max-width:360px;margin:0 auto;">
<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:10px;padding:10px 14px;">
<div style="display:flex;align-items:center;gap:8px;"><span style="font-size:15px;">ϕ</span><div>
<div style="font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">FIBONACCI</div>
<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.5);">F9+F10=34 posicion 11</div>
</div></div><span style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 34</span></div>
<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:10px;padding:10px 14px;">
<div style="display:flex;align-items:center;gap:8px;"><span style="font-size:15px;">⊞</span><div>
<div style="font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">DRAW HISTORY</div>
<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.5);">Top historico #1 Powerball</div>
</div></div><span style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 07</span></div>
<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.1);border-radius:10px;padding:10px 14px;">
<div style="display:flex;align-items:center;gap:8px;"><span style="font-size:15px;">⊛</span><div>
<div style="font-family:DM Mono,monospace;font-size:9px;color:#C9A84C;letter-spacing:1px;">COMMUNITY</div>
<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(201,168,76,.5);">47x en r/powerball esta semana</div>
</div></div><span style="font-family:DM Mono,monospace;font-size:18px;font-weight:700;color:#C9A84C;">→ 23</span></div>
</div></div>
<script>
const s=[[7,14,23,34,55],[8,15,22,33,44],[5,12,27,38,52],[3,18,29,41,60],[11,21,32,43,57]];
const g=[12,6,11,8,22,19];let i=0;
setInterval(()=>{i=(i+1)%s.length;for(let j=0;j<5;j++){const e=document.getElementById('pb'+j);if(e)e.textContent=String(s[i][j]).padStart(2,'0');}
const eg=document.getElementById('pb5');if(eg)eg.textContent=String(g[i%g.length]).padStart(2,'0');},2800);
</script>""", unsafe_allow_html=True)

    st.markdown('<hr class="g">', unsafe_allow_html=True)
    _, cc, _ = st.columns([1,2,1])
    with cc:
        st.markdown('<p style="text-align:center;font-family:monospace;font-size:9px;color:rgba(255,255,255,.15);letter-spacing:1.5px;margin-bottom:10px;">FREE · NO CREDIT CARD · ES / EN / PT</p>', unsafe_allow_html=True)
        tab_r, tab_l = st.tabs([t_["reg"], t_["login"]])
        with tab_r:
            re_em = st.text_input(t_["email"],key="lr_em",placeholder="tu@email.com")
            re_pw = st.text_input(t_["pass"],key="lr_pw",type="password")
            re_pw2= st.text_input(t_["pass2"],key="lr_pw2",type="password")
            if st.button(t_["reg_btn"],key="lr_btn"):
                if re_pw!=re_pw2: st.error(t_["mismatch"])
                elif re_em and len(re_pw)>=6:
                    ok,res=registrar(re_em,re_pw)
                    if ok: st.session_state.update({"logged_in":True,"user_role":"free","user_email":re_em,"user_id":res.get("id")}); st.rerun()
                    elif res=="exists": st.error(t_["exists"])
                    else: st.error(f"Error: {res}")
        with tab_l:
            le = st.text_input(t_["email"],key="ll_em",placeholder="tu@email.com")
            lp = st.text_input(t_["pass"],key="ll_pw",type="password")
            if st.button(t_["login_btn"],key="ll_btn"):
                if le==ADMIN_EMAIL and lp==ADMIN_PASS:
                    st.session_state.update({"logged_in":True,"user_role":"admin","user_email":le,"user_id":None}); st.rerun()
                else:
                    ok,d=login_db(le,lp)
                    if ok: st.session_state.update({"logged_in":True,"user_role":d.get("role","free"),"user_email":d["email"],"user_id":d.get("id")}); st.rerun()
                    else: st.error(t_["login_err"])
    st.stop()

# ── APP PRINCIPAL ──
t_ = t()
MAX_GEN = 99 if st.session_state["user_role"] in ["admin","paid","pro"] else 3
gen_hoy = st.session_state.get("gen_hoy", 0)

lot_names = [f"{l['flag']} {l['nombre']}" for l in LOTERIAS]
sel_idx = st.selectbox(t_["sel"], range(len(lot_names)), format_func=lambda i: lot_names[i], key="sel_lot")
loteria = LOTERIAS[sel_idx]; mn, mx = loteria["min"], loteria["max"]

st.markdown(f'<div style="display:inline-block;padding:5px 12px;border-radius:20px;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.12);font-family:DM Mono,monospace;font-size:11px;color:rgba(201,168,76,.65);margin-bottom:12px;">Proximo: {" · ".join(loteria["dias"])} · {loteria["hora"]}</div>', unsafe_allow_html=True)

if MAX_GEN < 99:
    dots = "".join([f'<span style="width:8px;height:8px;border-radius:50%;background:{"#C9A84C" if i<gen_hoy else "rgba(255,255,255,.08)"};display:inline-block;margin:0 2px;"></span>' for i in range(MAX_GEN)])
    st.markdown(f'<div style="text-align:center;margin:4px 0 10px;">{dots} <span style="font-family:DM Mono,monospace;font-size:10px;color:rgba(255,255,255,.28);margin-left:6px;">{gen_hoy}/{MAX_GEN} {t_["gen_hoy"]}</span></div>', unsafe_allow_html=True)

st.markdown('<hr class="g">', unsafe_allow_html=True)

modulos = []; inputs = {}

# FAVORITOS
favs = st.session_state.get("favoritos", []); favs_v = [n for n in favs if mn<=n<=mx]
fav_lbl = f'{t_["fav_t"]} — {len(favs_v)} sel.' if favs_v else t_["fav_t"]
with st.expander(fav_lbl, expanded=False):
    st.caption(t_["fav_h"])
    sel = st.multiselect(t_["fav_sel"], list(range(mn, mx+1)), default=favs_v,
                         format_func=lambda n: str(n).zfill(2), key=f"ms_fav_{loteria['id']}")
    if sorted(sel) != sorted(favs_v): st.session_state["favoritos"]=sorted(sel); st.rerun()
    if favs_v:
        st.markdown("".join([f'<div class="ball" style="width:38px;height:38px;font-size:13px;display:inline-flex;">{str(n).zfill(2)}</div>' for n in favs_v]), unsafe_allow_html=True)
        if st.button("Limpiar",key="clr"): st.session_state["favoritos"]=[]; st.rerun()

# DATOS REALES
with st.expander(t_["real_t"], expanded=True):
    st.caption(t_["real_h"])
    c1, c2 = st.columns(2)
    with c1:
        cb_h = st.checkbox("Historico oficial", value=True, key="cb_hist")
        cb_c = st.checkbox("Comunidad",         value=True, key="cb_comm")
    with c2:
        cb_e = st.checkbox("Efemerides",        value=True, key="cb_efem")
        cb_d = st.checkbox("Fecha de hoy",      value=True, key="cb_hoy")
    if any([cb_h, cb_c, cb_e, cb_d]):
        modulos.append("real")
        inputs.update({"use_hist":cb_h,"use_comm":cb_c,"use_efem":cb_e,"use_hoy":cb_d})
    inputs["excluir"] = st.text_input(t_["excluir"], placeholder="4, 13", key="ex_inp")

# HOLISTICO
with st.expander(t_["hol_t"], expanded=False):
    st.caption(t_["hol_h"])
    c1, c2 = st.columns(2)
    with c1: inputs["nombre"] = st.text_input(t_["nombre"], key="h_nm", placeholder="Juan Garcia")
    with c2: inputs["fecha"]  = st.text_input(t_["fecha"],  key="h_fe", placeholder="14/03/92")
    inputs["sueno"] = st.text_area(t_["sueno"], key="h_dr", height=70,
                                   placeholder=t_["sueno"], label_visibility="collapsed")
    if inputs.get("nombre") or inputs.get("fecha") or inputs.get("sueno"): modulos.append("holistic")

# MATEMATICO
with st.expander(t_["mat_t"], expanded=False):
    st.caption(t_["mat_h"])
    c1, c2 = st.columns(2)
    with c1:
        uf = st.checkbox("Fibonacci",          key="cb_fib")
        ut = st.checkbox("Tesla 3-6-9",        key="cb_tes")
    with c2:
        us = st.checkbox("Geometria Sagrada",  key="cb_sag")
        up = st.checkbox("Numeros Primos",     key="cb_pri")
    if any([uf, ut, us, up]):
        modulos.append("math")
        inputs.update({"use_fib":uf,"use_tes":ut,"use_sag":us,"use_pri":up})

st.markdown('<hr class="g">', unsafe_allow_html=True)

# GENERAR
if gen_hoy >= MAX_GEN and MAX_GEN < 99:
    st.warning(f"{gen_hoy}/{MAX_GEN} {t_['gen_hoy']}")
    st.markdown(f"""<div style="background:rgba(255,255,255,.02);border:1px solid rgba(201,168,76,.18);border-radius:16px;padding:20px;text-align:center;">
<h3 style="font-family:'Playfair Display',serif;color:#C9A84C;margin-bottom:8px;">LuckSort Pro</h3>
<p style="color:rgba(232,228,217,.45);font-size:13px;margin-bottom:14px;">Generaciones ilimitadas</p>
<a href="{STRIPE_LINK}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#F0C84A);color:#07070f;font-weight:700;font-size:14px;padding:12px 28px;border-radius:12px;text-decoration:none;">$9.99/mes</a>
</div>""", unsafe_allow_html=True)
else:
    if st.button(t_["gen"], key="gen_btn"):
        ph = st.empty(); icons = ["⊞","⊛","ϕ","◆"]
        for i, step in enumerate(t_["steps"]):
            ph.markdown(f'<div class="conv-wrap"><div class="conv-ring"></div><div class="conv-icon">{icons[i%len(icons)]}</div><div class="conv-label">{step}</div></div>', unsafe_allow_html=True)
            time.sleep(0.55)
        ph.empty()
        res = generar(loteria, inputs, modulos)
        st.session_state.update({"ultima_gen":res,"ultima_lot":loteria,"ultima_mod":modulos,"gen_hoy":gen_hoy+1})
        st.rerun()

if st.session_state.get("ultima_gen") and st.session_state.get("ultima_lot"):
    render_resultado(st.session_state["ultima_gen"], st.session_state["ultima_lot"], st.session_state.get("ultima_mod",[]))
