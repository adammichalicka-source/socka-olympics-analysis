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

# Top N (aby graf nebol preplnený)
count = len(filtered)
max_n = max(3, min(25, count))   # aby max nebolo menšie než 3
default_n = min(10, count)       # default nemôže byť väčší než počet krajín

top_n = st.slider(
    "Koľko krajín zobraziť (Top N):",
    min_value=1,
    max_value=max_n,
    value=default_n,
)

chart_df = filtered.sort_values("total", ascending=False).head(top_n)

# Figure + axis (profi ovládanie štýlu)
plt.figure(figsize=(10, 5))
ax = plt.gca()

# Stacked stĺpce
ax.bar(chart_df["country"], chart_df["gold"], label="Gold", color="#FFD700")
ax.bar(
    chart_df["country"],
    chart_df["silver"],
    bottom=chart_df["gold"],
    label="Silver",
    color="#C0C0C0",
)
ax.bar(
    chart_df["country"],
    chart_df["bronze"],
    bottom=chart_df["gold"] + chart_df["silver"],
    label="Bronze",
    color="#CD7F32",
)
for i in range(len(chart_df)):

    gold = chart_df.iloc[i]["gold"]
    silver = chart_df.iloc[i]["silver"]
    bronze = chart_df.iloc[i]["bronze"]
    total = chart_df.iloc[i]["total"]

    # Zlaté číslo
    if gold > 0:
        ax.text(i, gold/2, str(int(gold)), ha="center", va="center", fontsize=9)

    # Strieborné číslo
    if silver > 0:
        ax.text(i, gold + silver/2, str(int(silver)), ha="center", va="center", fontsize=9)

    # Bronzové číslo
    if bronze > 0:
        ax.text(i, gold + silver + bronze/2, str(int(bronze)), ha="center", va="center", fontsize=9)

    # Celkový počet nad stĺpcom
    ax.text(i, total + 0.3, str(int(total)), ha="center", va="bottom", fontsize=10, fontweight="bold")

# Čistý "dashboard" look
ax.set_axisbelow(True)
ax.yaxis.grid(True, alpha=0.25)     # jemná mriežka
ax.spines["top"].set_visible(False) # odstráni rámik hore
ax.spines["right"].set_visible(False) # odstráni rámik vpravo

# Popisy
ax.set_ylabel("Počet medailí", fontsize=11)

# Ak máš športový režim, dá title podľa športu. Ak nie, bude všeobecný.
title = "Rozdelenie medailí podľa typu" if "selected_sport" not in globals() or selected_sport is None else f"Rozdelenie medailí – {selected_sport}"


plt.xticks(rotation=35, ha="right")

# Legenda hore (vyzerá moderne)
ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12))

# Čísla nad stĺpcami (total)
for i, total in enumerate(chart_df["total"].tolist()):
    ax.text(i, total + 0.2, str(int(total)), ha="center", va="bottom", fontsize=10)

plt.tight_layout()
st.pyplot(plt)
# 9) Tabuľka výsledkov
st.subheader("📋 Analytická tabuľka")

table_df = chart_df.copy()

# Preklad názvov stĺpcov
rename_columns = {
    "country": "Krajina",
    "gold": "🥇 Zlaté medaily",
    "silver": "🥈 Strieborné medaily",
    "bronze": "🥉 Bronzové medaily",
    "total": "🏅 Spolu medailí",
    "points": "⭐ Body (3-2-1)",
    "population": "👥 Populácia",
    "sport_invest": "💰 Investície do športu (mil. USD)",
    "medals_per_million": "📊 Medaily na 1 milión obyv.",
    "medals_per_invest": "📈 Medaily na 1 milión USD"
}

# Premenuj iba tie, ktoré existujú
existing_cols = {k: v for k, v in rename_columns.items() if k in table_df.columns}
table_df = table_df.rename(columns=existing_cols)

# Zaokrúhlenie (ak existujú)
if "📊 Medaily na 1 milión obyv." in table_df.columns:
    table_df["📊 Medaily na 1 milión obyv."] = table_df["📊 Medaily na 1 milión obyv."].round(3)

if "📈 Medaily na 1 milión USD" in table_df.columns:
    table_df["📈 Medaily na 1 milión USD"] = table_df["📈 Medaily na 1 milión USD"].round(4)

# Reset index pre krajší vzhľad
table_df = table_df.reset_index(drop=True)

st.dataframe(table_df, use_container_width=True)




