import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# 1) Nastavenie stránky
# =========================
st.set_page_config(page_title="Sočka Olympics Analysis", layout="wide")
st.title("🏅 Sočka Olympics Analysis")

# =========================
# 2) Načítanie dát
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("olympics2026.csv")
    df.columns = [c.strip().lower() for c in df.columns]

    # povinné stĺpce
    for c in ["gold", "silver", "bronze"]:
        if c not in df.columns:
            st.error(f"Chýba stĺpec '{c}' v olympics2026.csv")
            st.stop()

    # pretypovanie
    for c in ["gold", "silver", "bronze"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # total
    if "total" not in df.columns:
        df["total"] = df["gold"] + df["silver"] + df["bronze"]
    else:
        df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(df["gold"] + df["silver"] + df["bronze"])

    # krajina stĺpec
    if "country" not in df.columns:
        df = df.rename(columns={df.columns[0]: "country"})

    # metriky
    df["points_321"] = df["gold"] * 3 + df["silver"] * 2 + df["bronze"]

    if "population" in df.columns:
        df["population"] = pd.to_numeric(df["population"], errors="coerce")
        df["medals_per_million"] = np.where(df["population"] > 0, df["total"] / (df["population"] / 1_000_000), np.nan)

    if "sport_invest" in df.columns:
        df["sport_invest"] = pd.to_numeric(df["sport_invest"], errors="coerce")
        df["medals_per_invest"] = np.where(df["sport_invest"] > 0, df["total"] / df["sport_invest"], np.nan)

    return df

df = load_data()

# =========================
# 3) Sidebar – filtre
# =========================
st.sidebar.header("⚙️ Nastavenia")

countries = sorted(df["country"].astype(str).unique().tolist())
selected = st.sidebar.multiselect("Vyber krajiny", countries, default=countries[:5] if len(countries) >= 5 else countries)

metric = st.sidebar.selectbox(
    "Metrika zoradenia",
    [
        "🏅 Celkové medaily",
        "⭐ Body 3-2-1",
        "🌍 Medaily na 1 milión obyvateľov",
        "💶 Medaily na investície",
    ],
)

chart_type = st.sidebar.radio("Typ grafu", ["Skladaný (stacked)", "Skupinový (grouped)"])

filtered = df[df["country"].astype(str).isin(selected)].copy()

# vyber metriky + dropna (aby nepadalo)
if metric == "🏅 Celkové medaily":
    filtered["__metric"] = filtered["total"]
elif metric == "⭐ Body 3-2-1":
    filtered["__metric"] = filtered["points_321"]
elif metric == "🌍 Medaily na 1 milión obyvateľov":
    if "medals_per_million" not in filtered.columns:
        st.warning("Chýba 'population' v dátach.")
        st.stop()
    filtered = filtered.dropna(subset=["medals_per_million"])
    filtered["__metric"] = filtered["medals_per_million"]
else:
    if "medals_per_invest" not in filtered.columns:
        st.warning("Chýba 'sport_invest' v dátach.")
        st.stop()
    filtered = filtered.dropna(subset=["medals_per_invest"])
    filtered["__metric"] = filtered["medals_per_invest"]

if filtered.empty:
    st.warning("Po filtrovaní nezostali žiadne údaje (skús inú metriku alebo krajiny).")
    st.stop()

# Top N – bezpečne aj pri 1 krajine
count = len(filtered)
max_n = max(1, min(25, count))
default_n = max(1, min(10, count))

top_n = st.sidebar.slider("Koľko krajín zobraziť (Top N)", 1, max_n, default_n)

filtered = filtered.sort_values("__metric", ascending=False).head(top_n)

# =========================
# 4) Kreslenie grafu (fix farby + žiadne prekrytie)
# =========================
C_GOLD = "#FFD700"
C_SILV = "#C0C0C0"
C_BRON = "#CD7F32"

chart_df = filtered[["country", "gold", "silver", "bronze", "total"]].copy()

fig, ax = plt.subplots(figsize=(10, 5))  # NOVÝ fig vždy -> nič sa neprekrýva
x = np.arange(len(chart_df))

gold = chart_df["gold"].to_numpy(dtype=float)
silver = chart_df["silver"].to_numpy(dtype=float)
bronze = chart_df["bronze"].to_numpy(dtype=float)
total = chart_df["total"].to_numpy(dtype=float)

if chart_type == "Skladaný (stacked)":
    ax.bar(x, gold, color=C_GOLD, label="🥇 Zlaté")
    ax.bar(x, silver, bottom=gold, color=C_SILV, label="🥈 Strieborné")
    ax.bar(x, bronze, bottom=gold + silver, color=C_BRON, label="🥉 Bronzové")

    ax.set_ylim(0, float(np.max(total)) + 2)

    # TOTAL nad stĺpcom
    for i in range(len(chart_df)):
        ax.text(i, total[i] + 0.3, f"{int(total[i])}", ha="center", va="bottom", fontweight="bold")

else:  # grouped
    w = 0.25
    ax.bar(x - w, gold, w, color=C_GOLD, label="🥇 Zlaté")
    ax.bar(x,     silver, w, color=C_SILV, label="🥈 Strieborné")
    ax.bar(x + w, bronze, w, color=C_BRON, label="🥉 Bronzové")

    ymax = float(np.max([gold.max(), silver.max(), bronze.max()])) if len(chart_df) else 1.0
    ax.set_ylim(0, ymax + 2)

    # TOTAL nad najvyšším stĺpcom
    for i in range(len(chart_df)):
        top = max(gold[i], silver[i], bronze[i])
        ax.text(i, top + 0.3, f"{int(total[i])}", ha="center", va="bottom", fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(chart_df["country"].astype(str).tolist(), rotation=30, ha="right")
ax.set_ylabel("Počet medailí")
ax.legend()

# =========================
# 5) Zobrazenie (graf + tabuľka)
# =========================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📊 Graf")
    st.pyplot(fig)

with col2:
    st.subheader("📋 Tabuľka")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
