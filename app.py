import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

# =========================
# Nastavenie stránky
# =========================
st.set_page_config(page_title="SOC Olympiada", layout="wide")
st.title("Inteligentná medailová analýza krajín – ZOH 2026")

# =========================
# Sidebar nastavenia
# =========================
st.sidebar.header("⚙️ Nastavenia")
mode = st.sidebar.radio("Režim:", ["Celkové medaily", "TOP 10 podľa športov"])

# =========================
# Načítanie dát
# =========================
if mode == "Celkové medaily":
    data = pd.read_csv("olympics2026.csv")
else:
    sport_data = pd.read_csv("olympics2026_top10_by_sport.csv")

    sport_data = sport_data.rename(columns={
        "krajina": "country",
        "zlato": "gold",
        "striebro": "silver",
        "bronz": "bronze",
        "spolu": "total"
    })

    sport_data["sport"] = sport_data["sport"].astype(str).str.strip()
    sports = sorted(sport_data["sport"].unique().tolist())

    selected_sport = st.sidebar.selectbox("Vyber šport:", sports)

    data = sport_data[sport_data["sport"] == selected_sport].copy()

# =========================
# Doplnkové údaje
# =========================
extra = {
    "Spojené štáty": {"population": 331_000_000, "sport_invest": 30000},
    "Čína": {"population": 1_440_000_000, "sport_invest": 16000},
    "Slovensko": {"population": 5_450_000, "sport_invest": 80},
    "Nórsko": {"population": 5_400_000, "sport_invest": 1200},
    "Taliansko": {"population": 59_000_000, "sport_invest": 1500},
    "Nemecko": {"population": 83_000_000, "sport_invest": 2500},
    "Francúzsko": {"population": 67_000_000, "sport_invest": 2200},
    "Švajčiarsko": {"population": 8_700_000, "sport_invest": 900},
    "Kanada": {"population": 38_000_000, "sport_invest": 1800},
    "Holandsko": {"population": 17_400_000, "sport_invest": 800},
    "Švédsko": {"population": 10_400_000, "sport_invest": 700},
    "Rakúsko": {"population": 8_900_000, "sport_invest": 600},
    "Južná Kórea": {"population": 52_000_000, "sport_invest": 1000},
    "Austrália": {"population": 26_000_000, "sport_invest": 1200},
    "Fínsko": {"population": 5_500_000, "sport_invest": 400},
    "Česko": {"population": 10_700_000, "sport_invest": 350},
    "Veľká Británia": {"population": 67_000_000, "sport_invest": 2500},
}

data["population"] = data["country"].map(lambda c: extra.get(c, {}).get("population"))
data["sport_invest"] = data["country"].map(lambda c: extra.get(c, {}).get("sport_invest"))
data["country_label"] = data["country"]

# =========================
# Výpočty metrík
# =========================
data["points"] = data["gold"] * 3 + data["silver"] * 2 + data["bronze"]

data["medals_per_million"] = data["total"] / (data["population"] / 1_000_000)
data["medals_per_invest"] = data["total"] / data["sport_invest"]
data["investment_per_medal"] = data["sport_invest"] / data["total"]

data.loc[data["population"].isna(), "medals_per_million"] = None
data.loc[data["sport_invest"].isna(), "medals_per_invest"] = None
data.loc[data["sport_invest"].isna(), "investment_per_medal"] = None

# =========================
# Výber krajín
# =========================
all_countries = sorted(data["country_label"].unique())

chosen = st.sidebar.multiselect(
    "Vyber krajiny na porovnanie:",
    all_countries,
    default=all_countries[:3]
)

if not chosen:
    st.warning("Vyber aspoň jednu krajinu.")
    st.stop()

filtered = data[data["country_label"].isin(chosen)].copy()

# =========================
# Výber metriky
# =========================
metric = st.sidebar.selectbox(
    "Vyber metriku:",
    [
        "Počet medailí",
        "Body (3-2-1)",
        "Medaily na 1 milión obyvateľov",
        "Medaily na 1 milión € investícií",
        "Investície na 1 medailu"
    ]
)

# =========================
# Zoradenie
# =========================
if metric == "Počet medailí":
    filtered = filtered.sort_values("total", ascending=False)

elif metric == "Body (3-2-1)":
    filtered = filtered.sort_values("points", ascending=False)

elif metric == "Medaily na 1 milión obyvateľov":
    filtered = filtered.dropna(subset=["medals_per_million"])
    filtered = filtered.sort_values("medals_per_million", ascending=False)

elif metric == "Medaily na 1 milión € investícií":
    filtered = filtered.dropna(subset=["medals_per_invest"])
    filtered = filtered.sort_values("medals_per_invest", ascending=False)

else:
    filtered = filtered.dropna(subset=["investment_per_medal"])
    filtered = filtered.sort_values("investment_per_medal")

# =========================
# Graf
# =========================
st.subheader("Graf")

fig, ax = plt.subplots(figsize=(10,5))

if metric == "Počet medailí":

    ax.bar(filtered["country_label"], filtered["gold"], label="Zlaté", color="#FFD700")
    ax.bar(filtered["country_label"], filtered["silver"], bottom=filtered["gold"], label="Strieborné", color="#C0C0C0")
    ax.bar(
        filtered["country_label"],
        filtered["bronze"],
        bottom=filtered["gold"] + filtered["silver"],
        label="Bronzové",
        color="#CD7F32"
    )

    ax.set_ylabel("Počet medailí")

else:

    if metric == "Body (3-2-1)":
        y = filtered["points"]
        label = "Body"

    elif metric == "Medaily na 1 milión obyvateľov":
        y = filtered["medals_per_million"]
        label = "Medaily / milión obyv."

    elif metric == "Medaily na 1 milión € investícií":
        y = filtered["medals_per_invest"]
        label = "Medaily / milión €"

    else:
        y = filtered["investment_per_medal"]
        label = "Investície / medaila"

    ax.bar(filtered["country_label"], y)
    ax.set_ylabel(label)

plt.xticks(rotation=35)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.grid(axis="y", alpha=0.3)

st.pyplot(fig)

# =========================
# Tabuľka
# =========================
st.subheader("Analytická tabuľka")

table = filtered.copy()

table = table.rename(columns={
    "country_label": "Krajina",
    "gold": "Zlaté",
    "silver": "Strieborné",
    "bronze": "Bronzové",
    "total": "Spolu",
    "points": "Body",
    "population": "Populácia",
    "sport_invest": "Investície (mil €)",
    "medals_per_million": "Medaily / mil obyv.",
    "medals_per_invest": "Medaily / mil €",
    "investment_per_medal": "Investícia / medaila"
})

st.dataframe(table, use_container_width=True)
