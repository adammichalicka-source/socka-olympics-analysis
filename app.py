import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title="SOČ Olympiáda", layout="wide")

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
USD_TO_EUR = 0.92  

for c in extra:
    if "sport_invest" in extra[c] and extra[c]["sport_invest"] is not None:
        extra[c]["sport_invest"] = extra[c]["sport_invest"] * USD_TO_EUR

# 3) Doplň stĺpce population a sport_invest do tabuľky
data["population"] = data["country"].map(lambda c: extra.get(c, {}).get("population"))
data["sport_invest"] = data["country"].map(lambda c: extra.get(c, {}).get("sport_invest"))

# 4) Výpočty
data["points"] = data["gold"] * 3 + data["silver"] * 2 + data["bronze"]
data["medals_per_million"] = data["total"] / (data["population"] / 1_000_000)
data["medals_per_invest"] = data["total"] / data["sport_invest"]  # medaily na 1 mil. USD investícií
data.loc[data["sport_invest"].isna() | (data["sport_invest"] == 0), "medals_per_invest"] = None
data.loc[data["population"].isna() | (data["population"] == 0), "medals_per_million"] = None

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
st.subheader("📊 Graf")

# Top N (aby graf nebol preplnený)
count = len(filtered)
max_n = max(1, min(25, count))
default_n = min(10, count)

top_n = st.slider(
    "Koľko krajín zobraziť (Top N):",
    min_value=1,
    max_value=max_n,
    value=default_n,
)

# priprav chart_df podľa metriky (a tiež zoradenie)
chart_df = filtered.copy()

if metric == "Total medals":
    chart_df = chart_df.sort_values("total", ascending=False)
elif metric == "Points (3-2-1)":
    chart_df = chart_df.sort_values("points", ascending=False)
elif metric == "Medals per 1M population":
    chart_df = chart_df.dropna(subset=["medals_per_million"]).sort_values("medals_per_million", ascending=False)
else:
    chart_df = chart_df.dropna(subset=["medals_per_invest"]).sort_values("medals_per_invest", ascending=False)

chart_df = chart_df.head(top_n)

import numpy as np
plt.figure(figsize=(10, 5))
ax = plt.gca()

# --- 1) Ak je metrika Total medals, tak zmysel dáva stacked/grouped podľa typov medailí ---
if metric == "Total medals":
    if chart_type == "Stacked (zlato+striebro+bronz)":
        ax.bar(chart_df["country"], chart_df["gold"], label="🥇", color="#FFD700")
        ax.bar(chart_df["country"], chart_df["silver"], bottom=chart_df["gold"], label="🥈", color="#C0C0C0")
        ax.bar(
            chart_df["country"],
            chart_df["bronze"],
            bottom=chart_df["gold"] + chart_df["silver"],
            label="🥉",
            color="#CD7F32"
        )

        # čísla vnútri + total hore
        for i in range(len(chart_df)):
            g = int(chart_df.iloc[i]["gold"])
            s = int(chart_df.iloc[i]["silver"])
            b = int(chart_df.iloc[i]["bronze"])
            t = int(chart_df.iloc[i]["total"])
            if g > 0: ax.text(i, g/2, str(g), ha="center", va="center", fontsize=9)
            if s > 0: ax.text(i, g + s/2, str(s), ha="center", va="center", fontsize=9)
            if b > 0: ax.text(i, g + s + b/2, str(b), ha="center", va="center", fontsize=9)
            ax.text(i, t + 0.3, str(t), ha="center", va="bottom", fontsize=10, fontweight="bold")

        plt.xticks(rotation=35, ha="right")

    else:
        x = np.arange(len(chart_df))
        w = 0.25
        ax.bar(x - w, chart_df["gold"], w, label="🥇", color="#FFD700")
        ax.bar(x,     chart_df["silver"], w, label="🥈", color="#C0C0C0")
        ax.bar(x + w, chart_df["bronze"], w, label="🥉", color="#CD7F32")

        ax.set_xticks(x)
        ax.set_xticklabels(chart_df["country"], rotation=35, ha="right")

        # total nad skupinou
        for i in range(len(chart_df)):
            t = int(chart_df.iloc[i]["total"])
            ax.text(i, t + 0.3, str(t), ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("Počet medailí", fontsize=11)

# --- 2) Iné metriky: kreslíme len 1 stĺpec na krajinu ---
else:
    if metric == "Points (3-2-1)":
        y = chart_df["points"]
        ylabel = "Body"
        fmt = "{:.0f}"
    elif metric == "Medals per 1M population":
        y = chart_df["medals_per_million"]
        ylabel = "Medaily / 1 milión obyvateľov"
        fmt = "{:.3f}"
    else:
        y = chart_df["medals_per_invest"]
        ylabel = "Medaily / 1 milión € investícií"
        fmt = "{:.4f}"

    ax.bar(chart_df["country"], y)
    plt.xticks(rotation=35, ha="right")
    ax.set_ylabel(ylabel, fontsize=11)

    # čísla nad stĺpcami
    y_max = float(y.max()) if len(y) else 0
    pad = y_max * 0.02 if y_max > 0 else 0.1
    for i, val in enumerate(y.tolist()):
        ax.text(i, float(val) + pad, fmt.format(float(val)), ha="center", va="bottom", fontsize=9)

# Čistý vzhľad
ax.set_axisbelow(True)
ax.yaxis.grid(True, alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# titul iba cez streamlit (nech nezavadzia hore)
# ax.set_title(... )  <-- nedávame

ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))

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
    "sport_invest": "💰 Investície do športu (mil. €)",
    "medals_per_million": "📊 Medaily na 1 milión obyv.",
   "medals_per_invest": "📈 Medaily na 1 milión €"
}

# Premenuj iba tie, ktoré existujú
existing_cols = {k: v for k, v in rename_columns.items() if k in table_df.columns}
table_df = table_df.rename(columns=existing_cols)


if "📊 Medaily na 1 milión obyv." in table_df.columns:
    table_df["📊 Medaily na 1 milión obyv."] = table_df["📊 Medaily na 1 milión obyv."].round(3)

if "📈 Medaily na 1 milión €" in table_df.columns:
    table_df["📈 Medaily na 1 milión €"] = table_df["📈 Medaily na 1 milión €"].round(4)


table_df = table_df.reset_index(drop=True)

st.dataframe(table_df, use_container_width=True)
