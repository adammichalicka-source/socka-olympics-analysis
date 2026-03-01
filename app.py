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
def load_countries():
    df = pd.read_csv("olympics2026.csv")
    df.columns = [c.strip().lower() for c in df.columns]

    # krajina
    if "country" not in df.columns:
        df = df.rename(columns={df.columns[0]: "country"})
    df["country"] = df["country"].astype(str).str.strip()

    # medaily
    for c in ["gold", "silver", "bronze"]:
        if c not in df.columns:
            st.error(f"V olympics2026.csv chýba stĺpec '{c}'.")
            st.stop()
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # total
    if "total" not in df.columns:
        df["total"] = df["gold"] + df["silver"] + df["bronze"]
    else:
        df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(df["gold"] + df["silver"] + df["bronze"])

    # body 3-2-1
    df["points_321"] = df["gold"] * 3 + df["silver"] * 2 + df["bronze"]

    # voliteľné metriky
    if "population" in df.columns:
        df["population"] = pd.to_numeric(df["population"], errors="coerce")
        df["medals_per_million"] = np.where(
            df["population"] > 0,
            df["total"] / (df["population"] / 1_000_000),
            np.nan
        )

    if "sport_invest" in df.columns:
        df["sport_invest"] = pd.to_numeric(df["sport_invest"], errors="coerce")
        df["medals_per_invest"] = np.where(df["sport_invest"] > 0, df["total"] / df["sport_invest"], np.nan)

    return df


@st.cache_data
def load_sports():
    # ak súbor neexistuje alebo je zle, vrátime None
    try:
        df_s = pd.read_csv("olympics2026_top10_by_sport.csv")
    except Exception:
        return None

    df_s.columns = [c.strip().lower() for c in df_s.columns]

    # nájdi stĺpec so športom
    sport_col = None
    for c in ["sport", "discipline", "event"]:
        if c in df_s.columns:
            sport_col = c
            break
    if sport_col is None:
        return None

    # nájdi stĺpec s krajinou
    if "country" in df_s.columns:
        country_col = "country"
    else:
        # prvý rozumný kandidát
        country_col = None
        for c in df_s.columns:
            if c not in [sport_col, "gold", "silver", "bronze", "total"]:
                country_col = c
                break
        if country_col is None:
            return None

    df_s[sport_col] = df_s[sport_col].astype(str).str.strip()
    df_s[country_col] = df_s[country_col].astype(str).str.strip()

    # medaily
    for c in ["gold", "silver", "bronze"]:
        if c not in df_s.columns:
            return None
        df_s[c] = pd.to_numeric(df_s[c], errors="coerce").fillna(0)

    # total
    if "total" not in df_s.columns:
        df_s["total"] = df_s["gold"] + df_s["silver"] + df_s["bronze"]
    else:
        df_s["total"] = pd.to_numeric(df_s["total"], errors="coerce").fillna(df_s["gold"] + df_s["silver"] + df_s["bronze"])

    return df_s, sport_col, country_col


df = load_countries()
sport_pack = load_sports()  # buď None alebo (df_sport, sport_col, country_col)

# =========================
# 3) Funkcia na graf
# =========================
C_GOLD = "#FFD700"
C_SILV = "#C0C0C0"
C_BRON = "#CD7F32"

def plot_chart(chart_df: pd.DataFrame, chart_type: str, title: str):
    if chart_df.empty:
        st.warning("Nie sú dáta na vykreslenie grafu.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))  # vždy nový graf -> nič sa neprekrýva

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
            ax.text(i, total[i] + 0.3, f"{int(total[i])}",
                    ha="center", va="bottom", fontweight="bold")

    else:  # Skupinový (grouped)
        w = 0.25
        ax.bar(x - w, gold, w, color=C_GOLD, label="🥇 Zlaté")
        ax.bar(x,     silver, w, color=C_SILV, label="🥈 Strieborné")
        ax.bar(x + w, bronze, w, color=C_BRON, label="🥉 Bronzové")

        ymax = float(np.max([gold.max(), silver.max(), bronze.max()])) if len(chart_df) else 1.0
        ax.set_ylim(0, ymax + 2)

        # TOTAL nad najvyšším stĺpcom v skupine
        for i in range(len(chart_df)):
            top = max(gold[i], silver[i], bronze[i])
            ax.text(i, top + 0.3, f"{int(total[i])}",
                    ha="center", va="bottom", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(chart_df["country"].astype(str).tolist(), rotation=30, ha="right")
    ax.set_ylabel("Počet medailí")
    ax.set_title(title)
    ax.legend()

    st.pyplot(fig)

# =========================
# 4) Sidebar – nastavenia
# =========================
st.sidebar.header("⚙️ Nastavenia")

modes = ["Krajiny"]
if sport_pack is not None:
    modes.append("Top 10 podľa športu")

mode = st.sidebar.radio("Režim", modes)

chart_type = st.sidebar.radio("Typ grafu", ["Skladaný (stacked)", "Skupinový (grouped)"])

# =========================
# 5) REŽIM: KRAJINY
# =========================
if mode == "Krajiny":
    all_countries = sorted(df["country"].unique().tolist())
    selected = st.sidebar.multiselect(
        "Vyber krajiny",
        all_countries,
        default=all_countries[:5] if len(all_countries) >= 5 else all_countries
    )

    metric = st.sidebar.selectbox(
        "Metrika zoradenia",
        [
            "🏅 Celkové medaily",
            "⭐ Body 3-2-1",
            "🌍 Medaily na 1 milión obyvateľov",
            "💶 Medaily na investície",
        ],
    )

    filtered = df[df["country"].isin([str(x).strip() for x in selected])].copy()

    # metrika + dropna (aby nevzniklo 0/NaN)
    if metric == "🏅 Celkové medaily":
        filtered["__metric"] = filtered["total"]
    elif metric == "⭐ Body 3-2-1":
        filtered["__metric"] = filtered["points_321"]
    elif metric == "🌍 Medaily na 1 milión obyvateľov":
        if "medals_per_million" not in filtered.columns:
            st.warning("V dátach chýba 'population' → nejde vypočítať medaily na 1 milión.")
            st.stop()
        filtered = filtered.dropna(subset=["medals_per_million"])
        filtered["__metric"] = filtered["medals_per_million"]
    else:
        if "medals_per_invest" not in filtered.columns:
            st.warning("V dátach chýba 'sport_invest' → nejde vypočítať medaily na investície.")
            st.stop()
        filtered = filtered.dropna(subset=["medals_per_invest"])
        filtered["__metric"] = filtered["medals_per_invest"]

    if filtered.empty:
        st.warning("Po filtrovaní nezostali žiadne údaje (skús inú krajinu alebo metriku).")
        st.stop()

    # bezpečný Top N (pri 1 krajine sa slider ani nezobrazí)
    count = len(filtered)
    if count == 1:
        top_n = 1
        st.sidebar.info("Top N: iba 1 krajina (automaticky 1).")
    else:
        max_n = min(25, count)
        default_n = min(10, count)
        top_n = st.sidebar.slider("Koľko krajín zobraziť (Top N)", 1, max_n, default_n)

    filtered = filtered.sort_values("__metric", ascending=False).head(top_n)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        plot_chart(
            filtered[["country", "gold", "silver", "bronze", "total"]],
            chart_type,
            f"{metric} – Top {top_n}"
        )

    with col2:
        st.subheader("📋 Tabuľka")
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# =========================
# 6) REŽIM: TOP 10 PODĽA ŠPORTU
# =========================
else:
    df_sport, sport_col, country_col = sport_pack

    sports = sorted(df_sport[sport_col].unique().tolist())
    chosen_sport = st.sidebar.selectbox("Vyber šport", sports)

    sdf = df_sport[df_sport[sport_col] == chosen_sport].copy()
    if sdf.empty:
        st.warning("Pre zvolený šport nie sú dáta.")
        st.stop()

    sdf = sdf.sort_values("total", ascending=False)

    # bezpečný Top N
    count = len(sdf)
    if count == 1:
        top_n = 1
        st.sidebar.info("Top N: iba 1 krajina (automaticky 1).")
    else:
        max_n = min(10, count)  # pri športoch dáva zmysel max 10
        top_n = st.sidebar.slider("Koľko krajín zobraziť (Top N)", 1, max_n, max_n)

    sdf = sdf.head(top_n)

    # zjednotíme názov krajiny na "country"
    if country_col != "country":
        sdf = sdf.rename(columns={country_col: "country"})
    sdf["country"] = sdf["country"].astype(str).str.strip()

    col1, col2 = st.columns([1.2, 1])

    with col1:
        plot_chart(
            sdf[["country", "gold", "silver", "bronze", "total"]],
            chart_type,
            f"{chosen_sport} – Top {top_n}"
        )

    with col2:
        st.subheader("📋 Tabuľka")
        st.dataframe(sdf[["country", "gold", "silver", "bronze", "total"]].reset_index(drop=True), use_container_width=True)
