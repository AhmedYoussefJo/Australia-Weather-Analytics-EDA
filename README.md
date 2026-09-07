# 🌦️ Australia Weather Analytics & EDA

A comprehensive **Exploratory Data Analysis (EDA)** study investigating continental weather dynamics and precipitation trigger mechanisms across Australia using historical records from the **Australian Bureau of Meteorology (BoM)**.

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

1. **Continental Precipitation Imbalance:**
   - 75.8% Dry days vs. 21.9% Rain days (Rainfall ≥ 1.0 mm) across 145,460 observations.
2. **Location-Specific Median Imputation:**
   - Addressed systemic missing data by calculating group-level medians per weather station (`df.groupby('Location')`), preserving local microclimates (from tropical Cairns to arid Alice Springs) without distorting physical baselines.
3. **Intra-Day Diurnal Delta Engineering:**
   - Engineered rate-of-change metrics between 9 AM and 3 PM (`PressureChange`, `HumidityChange`, `TempChange`) to capture approaching cyclonic fronts.
4. **The July 2017 Missing-Data Deduction:**
   - Dataset records terminate abruptly on June 25, 2017. Tracking the micro-trends of late June revealed a precipitous pressure drop (from 1021 to 1005 hPa) accompanied by overcast cloud cover (8.0 oktas), empirically demonstrating an inbound winter storm front entering July 2017.
5. **Atmospheric Rain Triggers:**
   - Strongest physical indicators preceding precipitation: 3 PM Barometric Pressure drop below 1012 hPa and a 3 PM Relative Humidity surge peaking near 72%.
   - Maritime wind corridors from the South-East and South delivering >32–35% rainfall incidence.

---

## 📊 Repository Contents
- `rain_analysis_copy.ipynb`: Complete exploratory data analysis, geospatial imputation logic, and statistical visualizations.
- `app.py`: Interactive production dashboard developed using Plotly and Dash (featuring 5 analytical workspaces and multi-level dynamic filtering).
- `report_eda_AUSWeather.pdf`: Publication-grade 16:9 widescreen executive presentation deck detailing the complete methodology and visual findings.

---

## 🚀 Running the Interactive Dashboard Locally

```bash
# Clone the repository
git clone https://github.com/AhmedYoussefJo/Australia-Weather-Analytics-EDA.git
cd Australia-Weather-Analytics-EDA

# Install dependencies
pip install dash dash-bootstrap-components pandas plotly numpy

# Launch dashboard
python app.py
```
Open `http://127.0.0.1:8050/` in your browser.
