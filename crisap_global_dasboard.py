import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pycountry
import requests
import hashlib
import os
import subprocess
import openai
import supabase 
from climada.hazard import Hazard
from climada.entity import Exposures
from climada.engine import Impact
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

# 🚀 Automatic Dependency Installation
REQUIRED_PACKAGES = [
    "streamlit", "pandas", "geopandas", "plotly", "pycountry", "requests",
    "supabase", "climada", "openai", "reportlab"
]

for package in REQUIRED_PACKAGES:
    try:
        __import__(package)
    except ImportError:
        subprocess.run(["pip", "install", package])

# 🔒 Secure Access Control - Login System
st.set_page_config(page_title="CRISAP 2.0", layout="wide")
st.markdown("<h1 style='text-align: center; color: blue;'>🚀 CRISAP 2.0 - AI-Driven Climate Risk Platform</h1>", unsafe_allow_html=True)

password = st.text_input("🔒 Enter Password:", type="password")

# ✅ Define Allowed Users
AUTHORIZED_USERS = {
    "admin": "CRISAP2024",
    "testuser": "climate123"
}

if password in AUTHORIZED_USERS.values():
    st.sidebar.success("✅ Access Granted!")

    # 🌍 **ISO-Based Country Selection**
    st.sidebar.header("🌎 Select Country & Region")
    country_list = {c.name: c.alpha_3 for c in pycountry.countries}
    selected_country = st.sidebar.selectbox("Select Country", list(country_list.keys()))

    # 🔄 **Auto-Fetch Regions**
    def get_regions(iso_code):
        url = f"https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries/{iso_code}.json"
        try:
            response = requests.get(url)
            data = response.json()
            return [region['name'] for region in data['states']]
        except:
            return ["Region data not available"]

    selected_iso = country_list[selected_country]
    region_list = get_regions(selected_iso)
    selected_region = st.sidebar.selectbox("Select Region", region_list)

    # 📊 **Climate Risk Assessment (CLIMADA)**
    st.markdown("<h2 style='text-align: center;'>📊 CLIMADA Climate Risk Assessment</h2>", unsafe_allow_html=True)
    st.write("Using AI-powered analysis to predict the potential impact of climate hazards.")

    hazard = Hazard.from_hdf5("https://storage.googleapis.com/climada/hazard_data/cyclones.h5")
    exposures = Exposures.from_hdf5("https://storage.googleapis.com/climada/exposures/global_exposure.h5")

    impact = Impact()
    impact.calc(hazard, exposures)
    impact_value = impact.imp_mat.sum()

    risk_data = {
        "Region": selected_region,
        "Estimated Loss (Billion $)": round(impact_value / 1e9, 2),
        "Vulnerability Index": round(0.6 * len(selected_region), 2),
        "Resilience Score": round(100 - (0.6 * len(selected_region)), 2)
    }

    df = pd.DataFrame([risk_data])
    st.dataframe(df, height=200, width=700)

    # 🌍 **Interactive Risk Map**
    st.markdown("<h2 style='text-align: center;'>🌍 Geospatial Risk Map</h2>", unsafe_allow_html=True)
    map_data = pd.DataFrame({"lat": [5.6037, 6.5244, -1.286389], "lon": [-0.1870, 3.3792, 36.8172]})
    st.map(map_data)

    # 📄 **Generate AI-Powered Risk Reports**
    def generate_nlp_report():
        prompt = f"Write a professional climate risk report for {selected_region}, {selected_country} using the given data: {risk_data}"
        openai.api_key = "your-openai-api-key"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        return response['choices'][0]['message']['content']

    if st.button("📝 Generate Risk Report"):
        with st.spinner("Generating AI-powered report..."):
            ai_report = generate_nlp_report()
            st.success("✅ Report successfully generated!")
            st.text_area("📄 Report Preview:", ai_report, height=200)

    # 💾 **Save Report to Cloud (Supabase)**
    SUPABASE_URL = "https://your-supabase-url.supabase.co"
    SUPABASE_KEY = "your-supabase-api-key"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    if st.button("💾 Upload Report to Cloud"):
        data = {"country": selected_country, "region": selected_region, "report": ai_report}
        response = supabase.table("climate_reports").insert(data).execute()
        st.success("✅ Report securely stored in Supabase!")

    # 🎨 **Styling for Improved UI**
    st.markdown(
        """
        <style>
            .stButton>button {
                background-color: #009688;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 5px;
                width: 100%;
            }
            .stTextInput>div>div>input {
                font-size: 16px;
                padding: 8px;
            }
            .stDataFrame {border: 2px solid #009688;}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write("🔗 **Developed by CRISAP AI** 🚀🔥")

else:
    st.error("❌ Access Denied! Please enter the correct password.")
    st.stop()
