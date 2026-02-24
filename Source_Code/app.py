import streamlit as st
import pandas as pd
import joblib
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Gaming Engagement Predictor", layout="wide")

# --- ARKA PLAN VE TASARIM ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_design():
    try:
        img_file = 'WhatsApp Image 2026-02-17 at 16.44.34.jpeg'
        bin_str = get_base64(img_file)
        


        
        design_css = f'''
        <style>
        .stApp {{
            /* Arkaya önce senin resmini koyuyoruz */
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center bottom 27%;
        }}

        /* Bu katman resmin üzerine 'Vignette' (köşelerden merkeze doğru hafif gölge) ekler */
        /* Bu sayede orta kısım aydınlık kalır, yazılar okunur, ama o çiğ beyazlık gider */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(0,0,0,0) 40%, rgba(0,0,0,0.3) 100%);
            z-index: -1;
        }}

        /* Ana içerik alanını (yazıları) bir 'cam' panelin içine alıyoruz (Glassmorphism) */
        /* Bu teknik, arkadaki resmi karartmadan yazıları okunabilir yapmanın en lüks yoludur */
        .main .block-container {{
            background: rgba(255, 255, 255, 0.15); 
            backdrop-filter: blur(5px); /* Resmi arkada hafifçe buğular, çok şık durur */
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 30px !important;
            margin-top: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        }}

        h1, h2, h3, h4, p, span, label {{
            color: #000000 !important;
            font-weight: 850 !important;
        }}




        header {{visibility: hidden; height: 0px;}}
        .main .block-container {{ padding-top: 0.5rem !important; }}

        /* TÜM YAZILAR SİYAH VE NET */
        h1, h2, h3, h4, p, span, label, .stMarkdown {{
            color: #000000 !important;
            font-weight: 800 !important;
        }}

        /* SLIDER MIN-MAX DEĞERLERİ: Siyah ve Kalın */
        [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {{
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 14px !important;
            opacity: 1 !important;
        }}

        /* Sidebar Sıkıştırma */
        section[data-testid="stSidebar"] > div:first-child {{
            padding-top: 0rem !important;
            margin-top: -60px !important;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(245, 245, 220, 0.98) !important; }}

        /* Selectbox Ayarları */
        div[data-baseweb="select"] > div {{
            background-color: #000000 !important;
            border: 2px solid #B8860B !important;
        }}
        div[data-baseweb="select"] span {{ color: #FFFFFF !important; }}

        /* ALTIN BUTON VE HOVER */
        div.stButton > button {{
            background-color: #C5A028 !important;
            color: #000000 !important;
            border: 3px solid #8B6B05 !important;
            height: 52px !important;
            width: 100% !important;
            border-radius: 14px !important;
            transition: all 0.3s ease !important;
        }}
        div.stButton > button:hover {{
            background-color: #B8860B !important;
            color: #FFFFFF !important;
            transform: scale(1.02) !important;
        }}
        
        /* Metric Confidence Değeri */
        [data-testid="stMetricValue"] div {{ color: #000000 !important; font-weight: 900 !important; }}
        </style>
        '''
        st.markdown(design_css, unsafe_allow_html=True)
    except:
        st.markdown("<style>.stApp { background-color: #F5F5F5; }</style>", unsafe_allow_html=True)

set_design()

# --- ANA LOGO ALANI (Garamond & Letter Spacing Düzenlendi) ---
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; 
                background-color: rgba(255, 255, 255, 0.5); padding: 15px; 
                border-radius: 20px; border: 2px solid #B8860B;">
        <div style="font-size: 50px;">⚔️</div>
        <div style="text-align: center;">
            <h1 style="margin: 0; color: #B8860B !important; font-family: 'Garamond', serif; letter-spacing: 2px; font-size: 32px;">LEGENDARY ANALYTICS</h1>
            <p style="margin: 0; color: #2C3E50 !important; font-size: 18px; font-weight: bold; font-style: italic;">"Determine the fate of players with the power of data!"</p>
        </div>
        <div style="font-size: 50px;">👑</div>
    </div><br>""", unsafe_allow_html=True)

# --- MODEL YÜKLEME ---
@st.cache_resource
def load_assets():
    model = joblib.load('lgbm_final_model.pkl')
    features = joblib.load('feature_columns.pkl')
    target_map = joblib.load('engagement_map.pkl')
    return model, features, target_map

model, feature_cols, target_map = load_assets()

# --- SIDEBAR BAŞLIK ---
st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px; background-color: rgba(184, 134, 11, 0.3); border-radius: 10px;">
        <div style="font-size: 35px;">📜</div>
        <h2 style="color: #B8860B; margin: 0; font-size: 20px;">COMMAND CENTER</h2>
    </div>""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='text-align: center; font-size: 18px;'>🕹️ Player Parameters</h3>", unsafe_allow_html=True)

# --- GİRİŞ PARAMETRELERİ ---
def user_input_features():
    avg_duration = st.sidebar.slider('Average Session Duration (Minutes)', 0, 300, 45)
    sessions_per_week = st.sidebar.slider('Number of Weekly Sessions', 0, 50, 10)
    
    # OTOMATİK HESAPLAMA VE ŞIK KART
    total_weekly_time = sessions_per_week * avg_duration
    st.sidebar.markdown(f"""
        <div style="background-color: #F5F5DC; padding: 10px; border-radius: 10px; border: 2px solid #B8860B; text-align: center; margin: 15px 0;">
            <p style="color: #000000 !important; margin: 0; font-size: 13px; font-weight: 800;">📊 COMPUTED WEEKLY TOTAL</p>
            <p style="color: #B8860B !important; margin: 0; font-size: 22px; font-weight: 900;">{total_weekly_time} <span style="font-size: 13px;">MIN</span></p>
        </div>
    """, unsafe_allow_html=True)

    player_level = st.sidebar.slider('Player Level', 1, 150, 20)
    achievements = st.sidebar.slider('Achievements', 0, 100, 10)
    genre = st.sidebar.selectbox('Game Type', ['Action', 'RPG', 'Strategy', 'Sports', 'Simulation'])
    difficulty = st.sidebar.selectbox('Difficulty Level', ['Easy', 'Medium', 'Hard'])
    location = st.sidebar.selectbox('Location', ['USA', 'Europe', 'Asia', 'Other'])
    
    data = {
        'AvgSessionDurationMinutes': avg_duration,
        'SessionsPerWeek': sessions_per_week,
        'TotalWeeklyTime': total_weekly_time,
        'PlayerLevel': player_level,
        'AchievementsUnlocked': achievements,
        'Genre': genre,
        'GameDifficulty': difficulty,
        'Location': location
    }
    return pd.DataFrame([data])

input_df = user_input_features()

# --- GERİ GETİRİLEN ORTA PANEL BAŞLIĞI (KALKANLI) ---
st.markdown("""
    <h2 style="display: flex; align-items: center; gap: 10px; font-size: 28px; margin-top: -10px;">
        <span style="font-size: 35px;">🛡️</span> Gaming Engagement Predictor
    </h2>
""", unsafe_allow_html=True)

# --- TAHMİN BUTONU VE SONUÇLAR ---
if st.sidebar.button('Guess'):
    # Feature Engineering
    input_df['NEW_Weekly_Intensity'] = input_df['TotalWeeklyTime'] / (input_df['SessionsPerWeek'] + 1)
    input_df['NEW_Time_Efficiency'] = input_df['AchievementsUnlocked'] / (input_df['TotalWeeklyTime'] + 1)
    input_df['NEW_Skill_Hard_Diff'] = ((input_df['GameDifficulty'] == 'Hard') & (input_df['PlayerLevel'] > 50)).astype(int) 
    
    final_df = pd.get_dummies(input_df)
    for col in feature_cols:
        if col not in final_df.columns: final_df[col] = 0
    final_df = final_df[feature_cols]
    
    prediction = model.predict(final_df)[0]
    prediction_proba = model.predict_proba(final_df).max()
    res_label = target_map[prediction]
    
    st.markdown("<h3 style='text-align: center; color: #B8860B; margin-top: 10px;'>🔮 PREDICTION RESULT</h3>", unsafe_allow_html=True)
    
    # Sonuç Kartları
    if res_label == "High":
        # Balon yerine daha 'sihirli' bir parıltı/kar efekti
        st.snow() 
        st.markdown(f'''
            <div style="background: linear-gradient(135deg, #D4AF37, #F1C40F); 
                        padding: 15px; border-radius: 15px; border: 3px solid #8B4513; 
                        text-align: center; box-shadow: 0px 0px 20px rgba(212, 175, 55, 0.6);">
                <h2 style="color: white !important; margin: 0; font-size: 24px; text-shadow: 2px 2px 4px #000;">💎 EPIC LOYALTY 💎</h2>
                <p style="color: white !important; font-size: 18px; font-weight: bold;">This player is the kingdom\'s most loyal hero!</p>
            </div>''', unsafe_allow_html=True)
    elif res_label == "Medium":
        st.markdown(f'<div style="background: linear-gradient(135deg, #BDC3C7, #95A5A6); padding: 15px; border-radius: 15px; border: 3px solid #2C3E50; text-align: center;"><h2 style="color: #2C3E50 !important; margin: 0; font-size: 24px;">🛡️ EXPERIENCED WARRIOR 🛡️</h2><p style="color: #2C3E50 !important; font-size: 18px;">Its commitment is stable, and its potential is high.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background: linear-gradient(135deg, #E67E22, #C0392B); padding: 15px; border-radius: 15px; border: 3px solid #3E1F11; text-align: center;"><h2 style="color: white !important; margin: 0; font-size: 24px;">🌑 LOST SOUL 🌑</h2><p style="color: white !important; font-size: 18px;">Warning: The player is about to cross over to the dark side!</p></div>', unsafe_allow_html=True)
    
    # Bilgi Şeridi
    st.markdown(f'<div style="background-color: rgba(184, 134, 11, 0.15); border-left: 5px solid #B8860B; padding: 10px 20px; border-radius: 8px; margin: 10px 0;"><p style="margin: 0; font-size: 20px; color: #000000 !important; font-weight: 800;">📜 Estimated Commitment Level: <span style="color: #B8860B;">{res_label}</span></p></div>', unsafe_allow_html=True)
    st.metric(label="📊 Prediction Confidence", value=f"{round(prediction_proba * 100, 2)}%")

# --- ALT BİLGİ ALANI (TEMİZLENMİŞ GÖRÜNÜM) ---
st.markdown('<h3 style="font-size: 20px; margin-top: 15px; margin-bottom: 5px;">Player Information You Entered</h3>', unsafe_allow_html=True)

# Efficiency ve Intensity gibi değerleri yuvarlayıp tabloyu öyle gösteriyoruz
display_df = input_df.copy()
for col in display_df.select_dtypes(include=['float64', 'float32']).columns:
    display_df[col] = display_df[col].round(4) # Efficiency çok küçük olduğu için 4 basamak bıraktım

st.write(display_df)

st.markdown("""
    <div style="
        text-align: center; 
        padding: 15px; 
        background: linear-gradient(135deg, #f3e5ab 0%, #d4af37 100%); 
        border-radius: 20px; 
        margin-top: 15px;
        border: 1px solid #b8860b;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
    ">
        <p style="
            font-size: 21px; 
            color: #4b3621 !important; 
            font-weight: 700; 
            font-style: italic; 
            margin: 0;
        ">
            ✨ Perform AI-powered loyalty analysis using player data... ✨
        </p>
    </div>
""", unsafe_allow_html=True)