
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

# =========================
# Nastavenie stránky
# =========================
st.set_page_config(page_title="SOČ Olympiáda", layout="wide")
st.title(" Inteligentná medailová analýza krajín – ZOH 2026")

# =========================
# Preklady športov
# =========================
sport_translation = {
    "biathlon": "Biatlon",
    "skating": "Korčuľovanie",
    "skiing": "Lyžovanie",
}

reverse_sport_translation = {v: k for k, v in sport_translation.items()}

# =========================
# Vlajky krajín
# =========================
country_flags = {
    "Spojené štáty": "🇺🇸",
    "Čína": "🇨🇳",
    "Slovensko": "🇸🇰",
    "Nórsko": "🇳🇴",
    "Taliansko": "🇮🇹",
    "Nemecko": "🇩🇪",
    "Japonsko": "🇯🇵",
    "Francúzsko": "🇫🇷",
    "Švajčiarsko": "🇨🇭",
    "Kanada": "🇨🇦",
    "Holandsko": "🇳🇱",
    "Švédsko": "🇸🇪",
    "Rakúsko": "🇦🇹",
    "Južná Kórea": "🇰🇷",
    "Austrália": "🇦🇺",
    "Fínsko": "🇫🇮",
    "Česko": "🇨🇿",
    "Veľká Británia": "🇬🇧",
    "Slovinsko": "🇸🇮",
    "Španielsko": "🇪🇸",
    "Brazília": "🇧🇷",
    "Kazachstan": "🇰🇿",
    "Argentína": "🇦🇷",
    "Bulharsko": "🇧🇬",
    "Belgicko": "🇧🇪",
    "Dánsko": "🇩🇰",
    "Estónsko": "🇪🇪",
    "Lotyšsko": "🇱🇻",
    "Poľsko": "🇵🇱",
    "Gruzínsko": "🇬🇪",
    "Nový Zéland": "🇳🇿",
    "Maďarsko": "🇭🇺",
    "Portugalsko": "🇵🇹",
    "Rumunsko": "🇷🇴",
    "Chorvátsko": "🇭🇷",
    "Srbsko": "🇷🇸",
    "Ukrajina": "🇺🇦",
    "Turecko": "🇹🇷",
    "Grécko": "🇬🇷",
    "Írsko": "🇮🇪",
    "Litva": "🇱🇹",
    "Luxembursko": "🇱🇺",
    "Izrael": "🇮🇱",
    "India": "🇮🇳",
    "Irán": "🇮🇷",
    "Mexiko": "🇲🇽",
    "Kolumbia": "🇨🇴",
    "Južná Afrika": "🇿🇦",
    "Keňa": "🇰🇪",
    "Jamajka": "🇯🇲",
    "Thajsko": "🇹🇭",
    "Malajzia": "🇲🇾",
    "Singapur": "🇸🇬",
    "Filipíny": "🇵🇭",
    "Hongkong": "🇭🇰",
    "Čínsky Tchaj-pej": "🇹🇼",
    "Saudská Arábia": "🇸🇦",
    "Spojené arabské emiráty": "🇦🇪",
    "Uzbekistan": "🇺🇿",
    "Mongolsko": "🇲🇳",
    "Arménsko": "🇦🇲",
    "Azerbajdžan": "🇦🇿",
    "Kirgizsko": "🇰🇬",
    "Moldavsko": "🇲🇩",
    "Kosovo": "🇽🇰",
    "Cyprus": "🇨🇾",
    "Malta": "🇲🇹",
    "Island": "🇮🇸",
    "Lichtenštajnsko": "🇱🇮",
    "Monako": "🇲🇨",
    "San Maríno": "🇸🇲",
    "Andorra": "🇦🇩",
    "Albánsko": "🇦🇱",
    "Bosna a Hercegovina": "🇧🇦",
    "Čierna Hora": "🇲🇪",
    "Severné Macedónsko": "🇲🇰",
    "Čile": "🇨🇱",
    "Uruguaj": "🇺🇾",
    "Venezuela": "🇻🇪",
    "Ekvádor": "🇪🇨",
    "Bolívia": "🇧🇴",
    "Portoriko": "🇵🇷",
    "Pakistan": "🇵🇰",
    "Nigéria": "🇳🇬",
    "Benin": "🇧🇯",
    "Eritrea": "🇪🇷",
    "Guinea-Bissau": "🇬🇼",
    "Madagaskar": "🇲🇬",
    "Haiti": "🇭🇹",
    "Libanon": "🇱🇧",
    "Neutrálni športovci": "🏳️",
}

# =========================
# Režim + načítanie dát
# =========================
st.sidebar.header("⚙️ Nastavenia")
mode = st.sidebar.radio("Režim:", ["Celkové medaily", "TOP 10 podľa športov"])

if mode == "Celkové medaily":
    data = pd.read_csv("olympics2026.csv")
    selected_sport = None
else:
    sport_data = pd.read_csv("olympics2026_top10_by_sport.csv")

    sport_data["sport"] = sport_data["sport"].astype(str).str.strip()
    sport_data = sport_data[~sport_data["sport"].str.lower().str.contains("hockey")].copy()

    sports_en = sorted(sport_data["sport"].unique().tolist())
    sports_sk = [sport_translation.get(s.lower(), s) for s in sports_en]

    selected_sport_sk = st.sidebar.selectbox("Vyber šport:", sports_sk)
    selected_sport = reverse_sport_translation.get(selected_sport_sk, selected_sport_sk).lower()

    data = sport_data[sport_data["sport"].str.lower() == selected_sport].copy()

# =========================
# Doplnkové údaje
# population = počet obyvateľov
# sport_invest = približné ročné investície do športu v mil. €
# =========================
extra = {
    "Spojené štáty": {"population": 331_000_000, "sport_invest": 30_000},
    "Čína": {"population": 1_440_000_000, "sport_invest": 16_000},
    "Slovensko": {"population": 5_450_000, "sport_invest": 80},
    "Nórsko": {"population": 5_400_000, "sport_invest": 1_200},
    "Taliansko": {"population": 59_000_000, "sport_invest": 1_500},
    "Nemecko": {"population": 83_000_000, "sport_invest": 2_500},
    "Japonsko": {"population": 125_800_000, "sport_invest": 2_000},
    "Francúzsko": {"population": 67_000_000, "sport_invest": 2_200},
    "Švajčiarsko": {"population": 8_700_000, "sport_invest": 900},
    "Kanada": {"population": 38_000_000, "sport_invest": 1_800},
    "Holandsko": {"population": 17_400_000, "sport_invest": 800},
    "Švédsko": {"population": 10_400_000, "sport_invest": 700},
    "Rakúsko": {"population": 8_900_000, "sport_invest": 600},
    "Južná Kórea": {"population": 52_000_000, "sport_invest": 1_000},
    "Austrália": {"population": 26_000_000, "sport_invest": 1_200},
    "Fínsko": {"population": 5_500_000, "sport_invest": 400},
    "Česko": {"population": 10_700_000, "sport_invest": 350},
    "Veľká Británia": {"population": 67_000_000, "sport_invest": 2_500},
    "Slovinsko": {"population": 2_100_000, "sport_invest": 150},
    "Španielsko": {"population": 47_000_000, "sport_invest": 900},
    "Brazília": {"population": 213_000_000, "sport_invest": 2_000},
    "Kazachstan": {"population": 19_000_000, "sport_invest": 300},

    "Argentína": {"population": 45_800_000, "sport_invest": 180},
    "Bulharsko": {"population": 6_400_000, "sport_invest": 95},
    "Belgicko": {"population": 11_800_000, "sport_invest": 420},
    "Dánsko": {"population": 6_000_000, "sport_invest": 300},
    "Estónsko": {"population": 1_370_000, "sport_invest": 70},
    "Lotyšsko": {"population": 1_870_000, "sport_invest": 75},
    "Poľsko": {"population": 37_500_000, "sport_invest": 320},
    "Gruzínsko": {"population": 3_700_000, "sport_invest": 85},
    "Nový Zéland": {"population": 5_300_000, "sport_invest": 300},
    "Maďarsko": {"population": 9_600_000, "sport_invest": 260},
    "Portugalsko": {"population": 10_400_000, "sport_invest": 150},
    "Rumunsko": {"population": 19_000_000, "sport_invest": 170},
    "Chorvátsko": {"population": 3_900_000, "sport_invest": 95},
    "Srbsko": {"population": 6_600_000, "sport_invest": 110},
    "Ukrajina": {"population": 37_000_000, "sport_invest": 140},
    "Turecko": {"population": 86_000_000, "sport_invest": 300},
    "Grécko": {"population": 10_400_000, "sport_invest": 250},
    "Írsko": {"population": 5_300_000, "sport_invest": 170},
    "Litva": {"population": 2_900_000, "sport_invest": 85},
    "Luxembursko": {"population": 680_000, "sport_invest": 40},
    "Izrael": {"population": 9_900_000, "sport_invest": 240},
    "India": {"population": 1_430_000_000, "sport_invest": 900},
    "Irán": {"population": 89_000_000, "sport_invest": 220},
    "Mexiko": {"population": 129_000_000, "sport_invest": 260},
    "Kolumbia": {"population": 53_000_000, "sport_invest": 130},
    "Južná Afrika": {"population": 63_000_000, "sport_invest": 180},
    "Keňa": {"population": 55_000_000, "sport_invest": 90},
    "Jamajka": {"population": 2_800_000, "sport_invest": 65},
    "Thajsko": {"population": 71_000_000, "sport_invest": 140},
    "Malajzia": {"population": 35_000_000, "sport_invest": 150},
    "Singapur": {"population": 6_000_000, "sport_invest": 260},
    "Filipíny": {"population": 115_000_000, "sport_invest": 120},
    "Hongkong": {"population": 7_500_000, "sport_invest": 180},
    "Čínsky Tchaj-pej": {"population": 23_500_000, "sport_invest": 260},
    "Saudská Arábia": {"population": 38_000_000, "sport_invest": 350},
    "Spojené arabské emiráty": {"population": 10_200_000, "sport_invest": 280},
    "Uzbekistan": {"population": 37_000_000, "sport_invest": 110},
    "Mongolsko": {"population": 3_500_000, "sport_invest": 30},
    "Arménsko": {"population": 2_800_000, "sport_invest": 40},
    "Azerbajdžan": {"population": 10_400_000, "sport_invest": 110},
    "Kirgizsko": {"population": 7_200_000, "sport_invest": 22},
    "Moldavsko": {"population": 2_500_000, "sport_invest": 20},
    "Kosovo": {"population": 1_600_000, "sport_invest": 18},
    "Cyprus": {"population": 1_300_000, "sport_invest": 30},
    "Malta": {"population": 560_000, "sport_invest": 18},
    "Island": {"population": 390_000, "sport_invest": 45},
    "Lichtenštajnsko": {"population": 40_000, "sport_invest": 10},
    "Monako": {"population": 39_000, "sport_invest": 22},
    "San Maríno": {"population": 34_000, "sport_invest": 5},
    "Andorra": {"population": 82_000, "sport_invest": 12},
    "Albánsko": {"population": 2_800_000, "sport_invest": 35},
    "Bosna a Hercegovina": {"population": 3_200_000, "sport_invest": 28},
    "Čierna Hora": {"population": 620_000, "sport_invest": 20},
    "Severné Macedónsko": {"population": 1_820_000, "sport_invest": 15},
    "Čile": {"population": 19_700_000, "sport_invest": 90},
    "Uruguaj": {"population": 3_400_000, "sport_invest": 55},
    "Venezuela": {"population": 28_500_000, "sport_invest": 65},
    "Ekvádor": {"population": 18_400_000, "sport_invest": 55},
    "Bolívia": {"population": 12_500_000, "sport_invest": 22},
    "Portoriko": {"population": 3_200_000, "sport_invest": 55},
    "Pakistan": {"population": 247_000_000, "sport_invest": 60},
    "Nigéria": {"population": 229_000_000, "sport_invest": 140},
    "Benin": {"population": 14_000_000, "sport_invest": 18},
    "Eritrea": {"population": 3_700_000, "sport_invest": 8},
    "Guinea-Bissau": {"population": 2_200_000, "sport_invest": 4},
    "Madagaskar": {"population": 31_000_000, "sport_invest": 15},
    "Haiti": {"population": 11_700_000, "sport_invest": 8},
    "Libanon": {"population": 5_500_000, "sport_invest": 25},
    "Neutrálni športovci": {"population": None, "sport_invest": None},
}

USD_TO_EUR = 0.92
for c in extra:
    if extra[c]["sport_invest"] is not None:
        extra[c]["sport_invest"] = extra[c]["sport_invest"] * USD_TO_EUR

# =========================
# Doplnenie údajov do dataframe
# =========================
data["population"] = data["country"].map(lambda c: extra.get(c, {}).get("population"))
data["sport_invest"] = data["country"].map(lambda c: extra.get(c, {}).get("sport_invest"))
data["flag"] = data["country"].map(lambda c: country_flags.get(c, "🏳️"))
data["country_label"] = data["flag"] + " " + data["country"]

# =========================
# Výpočty metrík
# =========================
data["points"] = data["gold"] * 3 + data["silver"] * 2 + data["bronze"]
data["medals_per_million"] = data["total"] / (data["population"] / 1_000_000)
data["medals_per_invest"] = data["total"] / data["sport_invest"]
data["investment_per_medal"] = data["sport_invest"] / data["total"]

data.loc[data["sport_invest"].isna() | (data["sport_invest"] == 0), "medals_per_invest"] = None
data.loc[data["population"].isna() | (data["population"] == 0), "medals_per_million"] = None
data.loc[
    data["sport_invest"].isna() | data["total"].isna() | (data["total"] == 0),
    "investment_per_medal"
] = None

# =========================
# Výber krajín + typ grafu
# =========================
all_country_labels = sorted(data["country_label"].unique().tolist())

default_labels = []
for country in ["Spojené štáty", "Čína", "Slovensko"]:
    row = data[data["country"] == country]
    if not row.empty:
        default_labels.append(row.iloc[0]["country_label"])

chosen_labels = st.sidebar.multiselect(
    "Vyber krajiny na porovnanie:",
    all_country_labels,
    default=default_labels
)

chart_type = st.sidebar.selectbox(
    "Typ grafu:",
    ["Skladaný ( spolu)", "Skupinový ( vedľa seba)"]
)

if not chosen_labels:
    st.warning("Vyber aspoň jednu krajinu.")
    st.stop()

filtered = data[data["country_label"].isin(chosen_labels)].copy()

# =========================
# Výber metriky
# =========================
metric = st.sidebar.selectbox(
    "Vyber metriku porovnania:",
    [
        " Počet medailí (spolu)",
        "⭐ Body (3-2-1)",
        " Medaily na 1 milión obyvateľov",
        " Medaily na 1 milión € investícií",
        " Investície na 1 medailu (mil. €)",
    ]
)

# =========================
# Dropna podľa metriky
# =========================
if metric == " Počet medailí (spolu)":
    pass
elif metric == "⭐ Body (3-2-1)":
    pass
elif metric == " Medaily na 1 milión obyvateľov":
    filtered = filtered.dropna(subset=["medals_per_million"])
elif metric == " Medaily na 1 milión € investícií":
    filtered = filtered.dropna(subset=["medals_per_invest"])
else:
    filtered = filtered.dropna(subset=["investment_per_medal"])

if filtered.empty:
    st.warning("Pre zvolenú metriku nemajú vybrané krajiny potrebné údaje.")
    st.stop()

# =========================
# Graf + Top N
# =========================
st.subheader(" Graf")

count = len(filtered)
if count == 1:
    top_n = 1
else:
    max_n = min(25, count)
    default_n = min(10, count)
    top_n = st.sidebar.slider(
        "Koľko krajín zobraziť (Top N):",
        min_value=1,
        max_value=max_n,
        value=default_n,
    )

chart_df = filtered.copy()

if metric == " Počet medailí (spolu)":
    chart_df = chart_df.sort_values("total", ascending=False)
elif metric == "⭐ Body (3-2-1)":
    chart_df = chart_df.sort_values("points", ascending=False)
elif metric == " Medaily na 1 milión obyvateľov":
    chart_df = chart_df.sort_values("medals_per_million", ascending=False)
elif metric == " Medaily na 1 milión € investícií":
    chart_df = chart_df.sort_values("medals_per_invest", ascending=False)
else:
    chart_df = chart_df.sort_values("investment_per_medal", ascending=True)

chart_df = chart_df.head(top_n)

fig, ax = plt.subplots(figsize=(10, 5))

# =========================
# Graf: medaily spolu
# =========================
if metric == " Počet medailí (spolu)":
    if chart_type == "Skladaný ( spolu)":
        ax.bar(chart_df["country_label"], chart_df["gold"], label=" Zlaté", color="#FFD700")
        ax.bar(chart_df["country_label"], chart_df["silver"], bottom=chart_df["gold"], label=" Strieborné", color="#C0C0C0")
        ax.bar(
            chart_df["country_label"],
            chart_df["bronze"],
            bottom=chart_df["gold"] + chart_df["silver"],
            label=" Bronzové",
            color="#CD7F32"
        )

        for i in range(len(chart_df)):
            g = int(chart_df.iloc[i]["gold"])
            s = int(chart_df.iloc[i]["silver"])
            b = int(chart_df.iloc[i]["bronze"])
            t = int(chart_df.iloc[i]["total"])

            if g > 0:
                ax.text(i, g / 2, str(g), ha="center", va="center", fontsize=9)
            if s > 0:
                ax.text(i, g + s / 2, str(s), ha="center", va="center", fontsize=9)
            if b > 0:
                ax.text(i, g + s + b / 2, str(b), ha="center", va="center", fontsize=9)

            ax.text(i, t + 0.3, str(t), ha="center", va="bottom", fontsize=10, fontweight="bold")

        plt.xticks(rotation=35, ha="right")

    else:
        x = np.arange(len(chart_df))
        w = 0.25

        gold = chart_df["gold"].to_numpy(dtype=float)
        silver = chart_df["silver"].to_numpy(dtype=float)
        bronze = chart_df["bronze"].to_numpy(dtype=float)
        total = chart_df["total"].to_numpy(dtype=float)

        ax.bar(x - w, gold, w, label=" Zlaté", color="#FFD700")
        ax.bar(x, silver, w, label=" Strieborné", color="#C0C0C0")
        ax.bar(x + w, bronze, w, label=" Bronzové", color="#CD7F32")

        ax.set_xticks(x)
        ax.set_xticklabels(chart_df["country_label"], rotation=35, ha="right")

        for i in range(len(chart_df)):
            top = max(gold[i], silver[i], bronze[i])
            ax.text(i, top + 0.3, str(int(total[i])), ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("Počet medailí", fontsize=11)

# =========================
# Graf: ostatné metriky
# =========================
else:
    if metric == "⭐ Body (3-2-1)":
        y = chart_df["points"]
        ylabel = "Body"
        fmt = "{:.0f}"
    elif metric == " Medaily na 1 milión obyvateľov":
        y = chart_df["medals_per_million"]
        ylabel = "Medaily / 1 milión obyvateľov"
        fmt = "{:.3f}"
    elif metric == " Medaily na 1 milión € investícií":
        y = chart_df["medals_per_invest"]
        ylabel = "Medaily / 1 milión € investícií"
        fmt = "{:.4f}"
    else:
        y = chart_df["investment_per_medal"]
        ylabel = "Investície / 1 medailu (mil. €)"
        fmt = "{:.2f}"

    ax.bar(chart_df["country_label"], y)
    plt.xticks(rotation=35, ha="right")
    ax.set_ylabel(ylabel, fontsize=11)

    y_max = float(y.max()) if len(y) else 0
    pad = y_max * 0.02 if y_max > 0 else 0.1

    for i, val in enumerate(y.tolist()):
        ax.text(i, float(val) + pad, fmt.format(float(val)), ha="center", va="bottom", fontsize=9)

# =========================
# Štýl grafu
# =========================
ax.set_axisbelow(True)
ax.yaxis.grid(True, alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

if metric == " Počet medailí (spolu)":
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))

ax.yaxis.set_major_locator(MaxNLocator(integer=True))

plt.tight_layout()
st.pyplot(fig)

# =========================
# Tabuľka výsledkov
# =========================
st.subheader(" Analytická tabuľka")

table_df = chart_df.copy()
table_df = table_df.drop(columns=["country", "flag"], errors="ignore").rename(columns={"country_label": "Krajina"})

rename_columns = {
    "gold": " Zlaté medaily",
    "silver": " Strieborné medaily",
    "bronze": " Bronzové medaily",
    "total": "Spolu medailí",
    "points": "⭐ Body (3-2-1)",
    "population": "Populácia",
    "sport_invest": "Investície do športu (mil. €)",
    "medals_per_million": "Medaily na 1 milión obyv.",
    "medals_per_invest": "Medaily na 1 milión €",
    "investment_per_medal": "Investície na 1 medailu (mil. €)",
}

table_df = table_df.rename(columns={k: v for k, v in rename_columns.items() if k in table_df.columns})

if "Medaily na 1 milión obyv." in table_df.columns:
    table_df["Medaily na 1 milión obyv."] = table_df["Medaily na 1 milión obyv."].round(3)

if "Medaily na 1 milión €" in table_df.columns:
    table_df["Medaily na 1 milión €"] = table_df["Medaily na 1 milión €"].round(4)

if "Investície na 1 medailu (mil. €)" in table_df.columns:
    table_df["Investície na 1 medailu (mil. €)"] = table_df["Investície na 1 medailu (mil. €)"].round(2)

table_df = table_df.reset_index(drop=True)
st.dataframe(table_df, use_container_width=True)
