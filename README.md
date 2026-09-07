# 🌦️ Australia Weather Analytics & EDA

End-to-end weather analytics project exploring rainfall behavior across Australia using historical data from the **Australian Bureau of Meteorology (BoM)**, then translating insights into an interactive **Dash** application.

---

## 💼 Why this project is portfolio-ready
- Works on a **real, large-scale dataset** (145k+ weather records).
- Covers full analytics flow: **data preparation → EDA → feature engineering → insight delivery**.
- Includes both technical and product-facing deliverables:
  - analytical notebook (`rain_analysis_copy.ipynb`)
  - interactive dashboard (`app.py`)
  - presentation deck (`report_eda_AUSWeather.pdf`)

---

## 🎯 Problem Statement
Weather behavior in Australia is highly variable across regions.  
The project answers: **Which atmospheric patterns and local conditions are most associated with rainfall, and how can these insights be communicated clearly for decision-making?**

---

## 📊 Dataset
- Source: **Australian Bureau of Meteorology (BoM) weather dataset**
- Coverage: **145k+ observations** across multiple locations
- Core fields used: temperature, humidity, pressure, wind direction/speed, rainfall labels, timestamps

---

## 🧪 Methodology
### 1) Data Preparation
- Converted date fields and engineered time attributes (year, month).
- Encoded rain labels for analysis consistency.

### 2) Missing Data Strategy
- Applied **location-level median imputation** to preserve microclimate behavior by station.

### 3) Feature Engineering
- Created aggregated and delta-style atmospheric indicators (temperature, humidity, pressure, wind).

### 4) Exploratory Analysis
- Compared rain behavior across location, time, and weather indicators.
- Analyzed directional wind and rainfall relationship.

---

## 🔍 Key Insights
1. **Continental precipitation imbalance**
   - 75.8% dry days vs. 21.9% rain days (Rainfall ≥ 1.0 mm).
2. **Pressure + humidity signal**
   - Rain likelihood rises with lower afternoon pressure and higher afternoon humidity.
3. **Wind corridor effect**
   - South-East and South wind directions show stronger rain incidence.
4. **Microclimate-aware imputation value**
   - Station-level treatment preserves local climate patterns better than global fill methods.

---

## 💡 Business Impact
- Helps non-technical stakeholders quickly interpret rainfall drivers.
- Supports location-aware weather risk understanding using explainable indicators.
- Demonstrates how raw meteorological records can be converted into practical analytics outputs.

---

## 🖼️ Project Visuals
- Interactive dashboard: run `app.py` locally.
- Executive visuals and charts: [`report_eda_AUSWeather.pdf`](./report_eda_AUSWeather.pdf)
- Full analytical workflow: [`rain_analysis_copy.ipynb`](./rain_analysis_copy.ipynb)

---

## 🛠️ Tech Stack
- Python
- Pandas
- NumPy
- Plotly
- Dash + Dash Bootstrap Components

---

## 👥 Project Overview
- **Initiative:** Digital Egypt Pioneers Initiative (DEPI)
- **Supervised by:** Eng. Sarah Abdelmoaty (Senior Technical Instructor)
- **Research Team:** 
  - Ahmed Yousef
  - Ahmed Hamdy
  - Seif Eldeen Mohamed
  - Ziad Desoki
  - Saeid Abdelmoneim

---

## 📁 Repository Structure
- `rain_analysis_copy.ipynb` — complete EDA workflow and analysis narrative
- `app.py` — interactive dashboard with location/year/month filtering
- `report_eda_AUSWeather.pdf` — presentation-ready summary of findings
- `requirements.txt` — dependencies for local execution

---

## 🧩 My Contributions
Use this section in your portfolio/resume to highlight your impact:
- Built and validated data-cleaning workflow for weather observations.
- Engineered weather delta features for stronger rainfall interpretation.
- Developed interactive Dash dashboard for exploratory decision support.
- Translated technical findings into executive-ready visuals and report artifacts.

---

## 🚀 Run Locally
```bash
git clone https://github.com/AhmedYoussefJo/Australia-Weather-Analytics-EDA.git
cd Australia-Weather-Analytics-EDA
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8050/` in your browser.
