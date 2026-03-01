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

    # stĺpec krajiny
    if "country" not in df.columns:
        df = df.rename(columns={df.columns[0]: "country"})
    df["country"] = df["country"].astype(str).str.strip()

    # povinné medailové stĺpce
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
    try:
        df_s = pd.read_csv("olympics2026_top10_by_sport.csv")
    except Exception:
        return None

    df_s.columns = [c.strip().lower() for c in df_s.columns]

    # nájdi stĺpec športu
    sport_col = None
    for c in ["sport", "discipline", "event"]:
        if c in df_s.columns:
            sport_col = c
            break
    if sport_col is None:
        return None

    # nájdi stĺpec krajiny
    if "country" in df_s.columns:
        country_col = "country"
    else:
        # prvý "rozumný" stĺpec čo nie je šport a nie sú medaily
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
sport_pack = load_sports()  # None alebo (df_sport, sport_col, country_col)

# =========================
# 3) Funkcie na anotácie
# =========================
C_GOLD = "#FFD700"
C_SILV = "#C0C0C0"
C_BRON = "#CD7F32"

def annotate_grouped(ax, bars):
    """Napíše číslo na vrch každého stĺpca (ak > 0)."""
    for b in bars:
        h = b.get_height()
        if h and h > 0:
            ax.text(b.get_x() + b.get_width()/2, h + 0.15, f"{int(h)}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

def annotate_stacked_segment(ax, x_positions, bottoms, values):
    """Napíše číslo do stredu segmentu (ak > 0)."""
    for i, v in enumerate(values):
        if v and v > 0:
            y = bottoms[i] + v/2
            ax.text(x_positions[i], y, f"{int(v)}",
                    ha="center", va="center", fontsize=9, fontweight="bold")

def plot_chart(chart_df: pd.DataFrame, chart_type: str, title: str, show_total_on_top: bool = True):
    if chart_df.empty:
        st.warning("Nie sú dáta na vykreslenie grafu.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))  # vždy nový graf

    x = np.arange(len(chart_df))
    gold = chart_df["gold"].to_numpy(dtype=float)
    silver = chart_df["silver"].to_numpy(dtype=float)
    bronze = chart_df["bronze"].to_numpy(dtype=float)
    total = chart_df["total"].to_numpy(dtype=float)

    if chart_type == "Skladaný (stacked)":
        b1 = ax.bar(x, gold, color=C_GOLD, label="🥇 Zlaté")
        b2 = ax.bar(x, silver, bottom=gold, color=C_SILV, label="🥈 Strieborné")
        b3 = ax.bar(x, bronze, bottom=gold + silver, color=C_BRON, label="🥉 Bronzové")

        ax.set_ylim(0, float(np.max(total)) + 3)

        # čísla pre každý segment
        annotate_stacked_segment(ax, x, np.zeros_like(gold), gold)
        annotate_stacked_segment(ax, x, gold, silver)
        annotate_stacked_segment(ax, x, gold + silver, bronze)

        # voliteľne total hore
        if show_total_on_top:
            for i in range(len(chart_df)):
                ax.text(i, total[i] + 0.25, f"{int(total[i])}",
                        ha="center", va="bottom", fontsize=10, fontweight="bold")

    else:  # Skupinový (grouped)
        w = 0.25
        bars_g = ax.bar(x - w, gold, w, color=C_GOLD, label="🥇 Zlaté")
        bars_s = ax.bar(x,     silver, w, color=C_SILV, label="🥈 Strieborné")
        bars_b = ax.bar(x + w, bronze, w, color=C_BRON, label="🥉 Bronzové")

        ymax = float(np.max([gold.max(), silver.max(), bronze.max()])) if len(chart_df) else 1.0
        ax.set_ylim(0, ymax + 3)

        # čísla na stĺpcoch
        annotate_grouped(ax, bars_g)
        annotate_grouped(ax, bars_s)
        annotate_grouped(ax, bars_b)

        # voliteľne total nad skupinou
        if show_total_on_top:
            for i in range(len(chart_df)):
                top = max(gold[i], silver[i], bronze[i])
                ax.text(i, top + 0.7, f"{int(total[i])}",
                        ha="center", va="bottom", fontsize=10, fontweight="bold")

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
# 5) Režim: KRAJINY (bez default výberu)
# =========================
if mode == "Krajiny":
    all_countries = sorted(df["country"].unique().tolist())

    selected = st.sidebar.multiselect(
        "Vyber krajiny",
        all_countries,
        default=[]  # nič sa nevyberie automaticky
    )

    if len(selected) == 0:
        st.info("Vyber aspoň jednu krajinu vľavo v nastaveniach.")
        st.stop()

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

    # metrika
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
        st.warning("Po filtrovaní nezostali žiadne údaje.")
        st.stop()

    # Top N len ak chceš (zmysel pri veľa vybraných)
    count = len(filtered)
    if count == 1:
        top_n = 1
    else:
        max_n = min(25, count)
        top_n = st.sidebar.slider("Koľko krajín zobraziť (Top N)", 1, max_n, max_n)

    filtered = filtered.sort_values("__metric", ascending=False).head(top_n)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        plot_chart(
            filtered[["country", "gold", "silver", "bronze", "total"]],
            chart_type,
            f"{metric} – zvolené krajiny"
        )

    with col2:
        st.subheader("📋 Tabuľka")
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# =========================
# 6) Režim: TOP 10 PODĽA ŠPORTU (výber športu + výber krajín)
# =========================
else:
    df_sport, sport_col, country_col = sport_pack

    sports = sorted(df_sport[sport_col].unique().tolist())
    chosen_sport = st.sidebar.selectbox("Vyber šport", sports)

    sdf = df_sport[df_sport[sport_col] == chosen_sport].copy()
    if sdf.empty:
        st.warning("Pre zvolený šport nie sú dáta.")
        st.stop()

    # zjednotíme názov krajiny na country
    if country_col != "country":
        sdf = sdf.rename(columns={country_col: "country"})
    sdf["country"] = sdf["country"].astype(str).str.strip()

    # výber krajín, ktoré chceš sledovať (bez defaultu)
    sport_countries = sorted(sdf["country"].unique().tolist())
    selected_sport_countries = st.sidebar.multiselect(
        "Vyber krajiny (v tomto športe)",
        sport_countries,
        default=[]
    )

    if len(selected_sport_countries) == 0:
        st.info("Vyber aspoň jednu krajinu vľavo (Top 10 podľa športu).")
        st.stop()

    filtered = sdf[sdf["country"].isin([str(x).strip() for x in selected_sport_countries])].copy()
    if filtered.empty:
        st.warning("Po filtrovaní nezostali žiadne údaje.")
        st.stop()

    # zoradenie (napr. podľa total)
    filtered = filtered.sort_values("total", ascending=False)

    # Top N len ak máš veľa vybraných (inak to netreba)
    count = len(filtered)
    if count == 1:
        top_n = 1
    else:
        max_n = min(10, count)
        top_n = st.sidebar.slider("Koľko krajín zobraziť (Top N)", 1, max_n, max_n)

    filtered = filtered.head(top_n)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        plot_chart(
            filtered[["country", "gold", "silver", "bronze", "total"]],
            chart_type,
            f"{chosen_sport} – zvolené krajiny"
        )

    with col2:
        st.subheader("📋 Tabuľka")
        st.dataframe(filtered[["country", "gold", "silver", "bronze", "total"]].reset_index(drop=True),
                     use_container_width=True)
