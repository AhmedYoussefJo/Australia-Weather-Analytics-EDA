# 🌦️ Australia Weather Analytics & EDA

An end-to-end weather analytics project that explores rainfall behavior across Australia using historical data from the **Australian Bureau of Meteorology (BoM)**, then packages insights into an interactive **Dash** application.

---

## 💼 Why this project is portfolio-ready
- Works on a **real, large-scale dataset** (145k+ weather observations).
- Covers complete analytics flow: **data preparation → EDA → feature engineering → insight delivery**.
- Produces both:
  - technical analysis (`rain_analysis_copy.ipynb`)
  - stakeholder-facing product (`app.py` dashboard + PDF presentation)

---

## 📌 Project Overview
- **Initiative:** Digital Egypt Pioneers Initiative (DEPI)
- **Supervised by:** Eng. Sarah Abdelmoaty (Senior Technical Instructor)
- **Research Team:** 
  - Ahmed Yousef
  - Ahmed Hamdy
  - Seif Eldeen Mohamed
  - Ziad Desoki
  - Saeid Abdelmoneim

---

## 🔍 Key Findings & Analytical Highlights
1. **Continental precipitation imbalance**
   - 75.8% dry days vs. 21.9% rain days (Rainfall ≥ 1.0 mm).
2. **Location-specific median imputation**
   - Missing values treated per station (`groupby('Location')`) to preserve microclimate behavior.
3. **Intra-day feature engineering**
   - Delta features between 9 AM and 3 PM helped expose approaching weather shifts.
4. **Pressure + humidity as rain triggers**
   - Rain likelihood rises with low pressure at 3 PM and high humidity.
5. **Wind corridor signal**
   - South-East and South wind directions show stronger rain incidence.

---

## 📊 Repository Contents
- `rain_analysis_copy.ipynb` — Complete EDA workflow and visual analysis.
- `app.py` — Interactive dashboard with filtering by location, year, and month.
- `report_eda_AUSWeather.pdf` — Presentation-ready summary of methods and findings.

---

## 🧩 My Contributions (Portfolio Section)
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
