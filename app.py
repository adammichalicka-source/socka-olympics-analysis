import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏅 Inteligentná medailová analýza krajín – ZOH 2026")

# 1) Načítame CSV
mode = st.radio("Režim:", ["Celkové medaily", "TOP 10 podľa športov"])

if mode == "Celkové medaily":
    data = pd.read_csv("olympics2026.csv")
    selected_sport = None
else:
    sport_data = pd.read_csv("olympics2026_top10_by_sport.csv")
    sports = sorted(sport_data["sport"].unique().tolist())
    selected_sport = st.selectbox("Vyber šport:", sports)
    data = sport_data[sport_data["sport"] == selected_sport].copy()

# 2) Doplnkové údaje (populácia + investície do športu)
extra = {
    "United States": {"population": 331_000_000, "sport_invest": 30_000},  # mil. USD/rok (odhad)
    "China": {"population": 1_440_000_000, "sport_invest": 16_000},
    "Slovakia": {"population": 5_450_000, "sport_invest": 80},

    "Norway": {"population": 5_400_000, "sport_invest": 1_200},
    "Italy": {"population": 59_000_000, "sport_invest": 1_500},
    "Germany": {"population": 83_000_000, "sport_invest": 2_500},
    "Japan": {"population": 125_800_000, "sport_invest": 2_000},
    "France": {"population": 67_000_000, "sport_invest": 2_200},
    "Switzerland": {"population": 8_700_000, "sport_invest": 900},
    "Canada": {"population": 38_000_000, "sport_invest": 1_800},
    "Netherlands": {"population": 17_400_000, "sport_invest": 800},
    "Sweden": {"population": 10_400_000, "sport_invest": 700},
    "Austria": {"population": 8_900_000, "sport_invest": 600},
    "South Korea": {"population": 52_000_000, "sport_invest": 1_000},
    "Australia": {"population": 26_000_000, "sport_invest": 1_200},
    "Finland": {"population": 5_500_000, "sport_invest": 400},
    "Czechia": {"population": 10_700_000, "sport_invest": 350},
    "Great Britain": {"population": 67_000_000, "sport_invest": 2_500},
    "Slovenia": {"population": 2_100_000, "sport_invest": 150},
    "Spain": {"population": 47_000_000, "sport_invest": 900},
    "Brazil": {"population": 213_000_000, "sport_invest": 2_000},
    "Kazakhstan": {"population": 19_000_000, "sport_invest": 300},
}

# 3) Doplň stĺpce population a sport_invest do tabuľky
data["population"] = data["country"].map(lambda c: extra.get(c, {}).get("population"))
data["sport_invest"] = data["country"].map(lambda c: extra.get(c, {}).get("sport_invest"))

# 4) Výpočty
data["points"] = data["gold"] * 3 + data["silver"] * 2 + data["bronze"]
data["medals_per_million"] = data["total"] / (data["population"] / 1_000_000)
data["medals_per_invest"] = data["total"] / data["sport_invest"]  # medaily na 1 mil. USD investícií

# 5) UI – výber krajín
all_countries = sorted(data["country"].unique().tolist())
default = [c for c in ["United States", "China", "Slovakia"] if c in all_countries]

chosen = st.multiselect("Vyber krajiny na porovnanie:", all_countries, default=default)
chart_type = st.selectbox(
    "Typ grafu:",
    ["Stacked (zlato+striebro+bronz)", "Grouped (3 vedľa seba)"]
)
if not chosen:
    st.warning("Vyber aspoň jednu krajinu.")
    st.stop()

filtered = data[data["country"].isin(chosen)].copy()

# 6) UI – výber metriky
metric = st.selectbox(
    "Vyber metriky porovnania:",
    ["Total medals", "Points (3-2-1)", "Medals per 1M population", "Medals per 1M USD sport invest"]
)

# 7) Priprav hodnoty pre graf
if metric == "Total medals":
    y = filtered["total"]
    ylabel = "Počet medailí"
elif metric == "Points (3-2-1)":
    y = filtered["points"]
    ylabel = "Body"
elif metric == "Medals per 1M population":
    # Ak niekto nemá populáciu, vyhodíme ho z grafu
    filtered = filtered.dropna(subset=["population"])
    y = filtered["medals_per_million"]
    ylabel = "Medaily / 1 milión obyvateľov"
else:
    filtered = filtered.dropna(subset=["sport_invest"])
    y = filtered["medals_per_invest"]
    ylabel = "Medaily / 1 milión USD investícií"

# 8) Graf
st.subheader("📊 Graf – rozdelenie medailí (🥇🥈🥉)")


chart_df = filtered.sort_values("total", ascending=False)

plt.figure()

plt.bar(chart_df["country"], chart_df["gold"], label="Gold" , color="#FFD700")
plt.bar(chart_df["country"], chart_df["silver"], bottom=chart_df["gold"], label="Silver", color="#C0C0C0")
plt.bar(chart_df["country"], chart_df["bronze"], bottom=chart_df["gold"] + chart_df["silver"], label="Bronze", color="#CD7F32")
plt.bar
 

plt.xticks(rotation=45, ha="right")
plt.ylabel("Počet medailí")
plt.title("Rozdelenie medailí podľa typu")
plt.legend()

st.pyplot(plt)
# 9) Tabuľka výsledkov
st.subheader("📋 Tabuľka (vybrané krajiny)")
cols = ["country", "gold", "silver", "bronze", "total", "points", "population", "sport_invest", "medals_per_million", "medals_per_invest"]
st.dataframe(filtered[cols].sort_values(by="points", ascending=False), use_container_width=True)

st.caption("Pozn.: 'sport_invest' sú odhadované ročné investície do športu (v miliónoch USD) – vhodné pre porovnávaciu analýzu v SOČ.")
