import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏅 Inteligentná medailová analýza krajín – ZOH 2026")

# Načítanie dát zo súboru v repozitári
data = pd.read_csv("olympics2026.csv")

# Doplnkové údaje: populácia + investície do športu (milióny USD/rok – odhad)
extra = {
    "United States": {"population": 331_000_000, "sport_invest": 30_000},
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

# Pridáme stĺpce do tabuľky
data["population"] = data["country"].map(lambda c: extra.get(c, {}).get("population"))
data["sport_invest"] = data["country"].map(lambda c: extra.get(c, {}).get("sport_invest"))

# Výpočty
data["points"] = data["gold"]*3 + data["silver"]*2 + data["bronze"]
data["medals_per_million"] = data["total"] / (data["population"] / 1_000_000)
data["medals_per_invest"] = data["total"] / data["sport_invest"]

# UI – výber krajín
all_countries = sorted(data["country"].unique().tolist())
default = [c for c in ["United States", "China", "Slovakia"] if c in all_countries]

chosen = st.multiselect("Vyber krajiny na porovnanie:", all_countries, default=default)

if not chosen:
    st.warning("Vyber aspoň jednu krajinu.")
    st.stop()

filtered = data[data["country"].isin(chosen)].copy()

# UI – výber metriky
metric = st.selectbox(
    "Vyber metriky porovnania:",
    ["Total medals", "Points (3-2-1)", "Medals per 1M population", "Medals per 1M USD sport invest"]
)

# Hodnoty pre graf
if metric == "Total medals":
    filtered = filtered.sort_values("total", ascending=False)
    y = filtered["total"]
    ylabel = "Počet medailí"
elif metric == "Points (3-2-1)":
    filtered = filtered.sort_values("points", ascending=False)
    y = filtered["points"]
    ylabel = "Body"
elif metric == "Medals per 1M population":
    filtered = filtered.dropna(subset=["population"]).sort_values("medals_per_million", ascending=False)
    y = filtered["medals_per_million"]
    ylabel = "Medaily / 1 milión obyvateľov"
else:
    filtered = filtered.dropna(subset=["sport_invest"]).sort_values("medals_per_invest", ascending=False)
    y = filtered["medals_per_invest"]
    ylabel = "Medaily / 1 milión USD investícií"

# Graf
st.subheader("📊 Graf")
plt.figure()
plt.bar(filtered["country"], y)
plt.xticks(rotation=45, ha="right")
plt.ylabel(ylabel)
plt.title(metric)
st.pyplot(plt)

# Tabuľka
st.subheader("📋 Tabuľka (vybrané krajiny)")
cols = ["country","gold","silver","bronze","total","points","population","sport_invest","medals_per_million","medals_per_invest"]
st.dataframe(filtered[cols], use_container_width=True)

st.caption("Pozn.: investície do športu sú odhady (milióny USD/rok) – vhodné na porovnávaciu analýzu v SOČ.")
