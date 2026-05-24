import streamlit as st
import pandas as pd
import os
from streamlit_echarts import st_echarts

# =========================================================
# CONFIGURATION PAGE
# =========================================================

st.set_page_config(
    page_title="Lupia Analytics | Enterprise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
DATA_PATH = os.path.join(BASE_DIR, "campagnes_data.csv")

HAS_LOGO = os.path.exists(LOGO_PATH)

# =========================================================
# STYLE GLOBAL
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 2.7rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
    color: #0F172A;
}

.enterprise-badge {
    font-size: 0.85rem;
    background-color: rgba(37,99,235,0.12);
    color: #2563EB;
    padding: 5px 10px;
    border-radius: 999px;
    font-weight: 700;
    margin-left: 10px;
}

.sub-title {
    color: #64748B;
    font-size: 1rem;
    margin-bottom: 28px;
}

.section-block {
    margin-bottom: 14px;
}

.section-label {
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #2563EB;
    background: rgba(37,99,235,0.08);
    padding: 6px 12px;
    border-radius: 999px;
    margin-bottom: 10px;
}

.section-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.03em;
    margin-bottom: 6px;
}

.section-description {
    font-size: 0.95rem;
    color: #64748B;
    line-height: 1.6;
    margin-bottom: 24px;
}
@media print {
    /* Cache la barre latérale et le menu du haut Streamlit */
    [data-testid="stSidebar"], 
    header[data-testid="stHeader"],
    .stApp > header {
        display: none !important;
    }
    
    /* Force le fond principal en blanc */
    .stApp {
        background-color: white !important;
    }
    
    /* Évite que les graphiques soient coupés en deux sur deux pages */
    .stMainBlockContainer {
        page-break-inside: avoid;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(DATA_PATH)

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

# Colonnes numériques
for col in [
    "CA_Genere",
    "Budget_Depense",
    "Nombre_Leads",
    "Nombre_Ventes"
]:

    if col not in df.columns:
        df[col] = 0

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    if HAS_LOGO:
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.title("⚡ LUPIA AGENCY")

    st.write("---")

    st.subheader("Filtres de Contrôle")

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    date_range = st.date_input(
        "Période d'analyse",
        value=(min_date, max_date)
    )

    date_debut, date_fin = (
        date_range
        if len(date_range) == 2
        else (min_date, max_date)
    )

    clients_choisis = st.multiselect(
        "Comptes / Marchés",
        options=df["Client"].unique(),
        default=df["Client"].unique()
    )

    plateformes_choisies = st.multiselect(
        "Canaux d'Acquisition",
        options=df["Plateforme"].unique(),
        default=df["Plateforme"].unique()
    )

# =========================================================
# FILTER
# =========================================================

df_filtre = df[
    (df["Date"].dt.date >= date_debut) &
    (df["Date"].dt.date <= date_fin) &
    (df["Client"].isin(clients_choisis)) &
    (df["Plateforme"].isin(plateformes_choisies))
]

if df_filtre.empty:
    st.warning("Aucune donnée disponible.")
    st.stop()

# =========================================================
# AGREGATION
# =========================================================

df_grouped = (
    df_filtre
    .groupby(df_filtre["Date"].dt.strftime("%Y-%m-%d"))
    .agg({
        "CA_Genere": "sum",
        "Budget_Depense": "sum",
        "Nombre_Leads": "sum"
    })
    .reset_index()
)

dates_axes = df_grouped["Date"].tolist()

ca_par_jour = df_grouped["CA_Genere"].tolist()
budget_par_jour = df_grouped["Budget_Depense"].tolist()
leads_par_jour = df_grouped["Nombre_Leads"].tolist()

# =========================================================
# KPI
# =========================================================

total_budget = df_filtre["Budget_Depense"].sum()
total_ca = df_filtre["CA_Genere"].sum()
total_leads = df_filtre["Nombre_Leads"].sum()
total_ventes = df_filtre["Nombre_Ventes"].sum()

benefice_net = total_ca - total_budget

roi_global = (
    (benefice_net / total_budget) * 100
    if total_budget > 0 else 0
)

cpl_moyen = (
    total_budget / total_leads
    if total_leads > 0 else 0
)

cac_moyen = (
    total_budget / total_ventes
    if total_ventes > 0 else 0
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div class="main-title">
    Lupia Analytics
    <span class="enterprise-badge">
        Enterprise Console
    </span>
</div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="sub-title">
    Réconciliation des données multi-canaux et pilotage du ROI en temps réel.
</div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TABS
# =========================================================

tab_showcase, tab_charts, tab_data = st.tabs([
    "📊 Vue d'Ensemble",
    "📈 Analyses Avancées",
    "🗄️ Registre de Données"
])

# =========================================================
# SPARKLINES
# =========================================================

def get_sparkline_config(data, line, area):

    return {

        "grid": {
            "left": 0,
            "right": 0,
            "top": 4,
            "bottom": 0
        },

        "xAxis": {
            "type": "category",
            "show": False,
            "data": list(range(len(data)))
        },

        "yAxis": {
            "type": "value",
            "show": False
        },

        "series": [{
            "data": data,
            "type": "line",
            "smooth": True,
            "showSymbol": False,

            "lineStyle": {
                "color": line,
                "width": 2
            },

            "areaStyle": {
                "color": area
            }
        }]
    }

# =========================================================
# ONGLET 1 : VUE D'ENSEMBLE
# =========================================================

with tab_showcase:

    st.subheader("Résumé Financier Exécutif")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):

            st.metric(
                "Revenue",
                f"${total_ca:,.0f}",
                "+26.8%"
            )

            st_echarts(
                options=get_sparkline_config(
                    ca_par_jour,
                    "#10B981",
                    "rgba(16,185,129,0.1)"
                ),
                height=50,
                key="spark_ca"
            )

    with col2:
        with st.container(border=True):

            st.metric(
                "Marketing Spend",
                f"${total_budget:,.0f}",
                "-11.4%",
                delta_color="inverse"
            )

            st_echarts(
                options=get_sparkline_config(
                    budget_par_jour,
                    "#EF4444",
                    "rgba(239,68,68,0.1)"
                ),
                height=50,
                key="spark_budget"
            )

    with col3:
        with st.container(border=True):

            profit_par_jour = [
                c - b
                for c, b in zip(
                    ca_par_jour,
                    budget_par_jour
                )
            ]

            st.metric(
                "Net Profit",
                f"${benefice_net:,.0f}",
                "+27.4%"
            )

            st_echarts(
                options=get_sparkline_config(
                    profit_par_jour,
                    "#2563EB",
                    "rgba(37,99,235,0.1)"
                ),
                height=50,
                key="spark_profit"
            )

    with col4:
        with st.container(border=True):

            st.metric(
                "Global ROI",
                f"{roi_global:.1f}%",
                "Optimal"
            )

            st_echarts(
                options=get_sparkline_config(
                    leads_par_jour,
                    "#F59E0B",
                    "rgba(245,158,11,0.1)"
                ),
                height=50,
                key="spark_roi"
            )

    st.write("")

    st.subheader("Acquisition & Unit Economics")

    sub_col1, sub_col2, sub_col3 = st.columns(3)

    with sub_col1:
        with st.container(border=True):

            st.metric(
                "Cost Per Lead (CPL)",
                f"${cpl_moyen:.2f}",
                "Target < $15"
            )

    with sub_col2:
        with st.container(border=True):

            st.metric(
                "Customer Acquisition Cost",
                f"${cac_moyen:.2f}",
                "Healthy LTV Ratio"
            )

    with sub_col3:
        with st.container(border=True):

            st.metric(
                "Conversion Pipeline",
                f"{total_ventes:,.0f} Sales",
                f"{total_leads:,.0f} Total Leads"
            )

# =========================================================
# ONGLET 2 : ANALYSES AVANCÉES
# =========================================================

with tab_charts:

    # =====================================================
    # TRAJECTOIRE GLOBALE
    # =====================================================

    st.markdown("""
<div class="section-block">
    <div class="section-label">Financial Analytics</div>
    <div class="section-title">Revenue & Marketing Performance</div>
    <div class="section-description">Consolidated evolution of revenue generation and marketing investments across all acquisition channels.</div>
</div>
    """, unsafe_allow_html=True)

    with st.container(border=True):

        main_chart = {

            "backgroundColor": "transparent",

            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "#0F172A",
                "borderWidth": 0,
                "textStyle": {
                    "color": "#FFFFFF"
                }
            },

            "legend": {
                "top": 10,
                "textStyle": {
                    "color": "#64748B"
                }
            },

            "grid": {
                "left": "3%",
                "right": "3%",
                "top": "18%",
                "bottom": "5%",
                "containLabel": True
            },

            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": dates_axes,

                "axisLine": {
                    "lineStyle": {
                        "color": "#CBD5E1"
                    }
                },

                "axisLabel": {
                    "color": "#64748B"
                }
            },

            "yAxis": {
                "type": "value",

                "splitLine": {
                    "lineStyle": {
                        "color": "rgba(148,163,184,0.15)"
                    }
                },

                "axisLabel": {
                    "color": "#64748B"
                }
            },

            "series": [

                {
                    "name": "Revenue",

                    "type": "line",

                    "smooth": True,

                    "showSymbol": False,

                    "data": ca_par_jour,

                    "lineStyle": {
                        "width": 4,
                        "color": "#2563EB"
                    },

                    "areaStyle": {
                        "color": "rgba(37,99,235,0.12)"
                    }
                },

                {
                    "name": "Marketing Spend",

                    "type": "line",

                    "smooth": True,

                    "showSymbol": False,

                    "data": budget_par_jour,

                    "lineStyle": {
                        "width": 3,
                        "type": "dashed",
                        "color": "#0F172A"
                    }
                }

            ]
        }

        st_echarts(
            options=main_chart,
            height="460px",
            key="macro_chart"
        )

    st.write("")

    # =====================================================
    # GRID 2 COLONNES
    # =====================================================

    left_chart, right_chart = st.columns(2)

    # =====================================================
    # PERFORMANCE PAR CANAL
    # =====================================================

    with left_chart:

        st.markdown("""
<div class="section-block">
    <div class="section-label">Channel Analytics</div>
    <div class="section-title">Comparative Channel Performance</div>
    <div class="section-description">Comparative analysis of generated revenue and marketing expenses by acquisition platform.</div>
</div>
        """, unsafe_allow_html=True)

        canal = (
            df_filtre
            .groupby("Plateforme")
            .agg({
                "CA_Genere": "sum",
                "Budget_Depense": "sum"
            })
            .reset_index()
        )

        with st.container(border=True):

            canal_chart = {

                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "shadow"
                    }
                },

                "legend": {
                    "top": 10
                },

                "grid": {
                    "left": "5%",
                    "right": "5%",
                    "top": "20%",
                    "bottom": "8%",
                    "containLabel": True
                },

                "xAxis": {
                    "type": "category",
                    "data": canal["Plateforme"].tolist()
                },

                "yAxis": {
                    "type": "value"
                },

                "series": [

                    {
                        "name": "Revenue",

                        "type": "bar",

                        "barWidth": 28,

                        "data": canal["CA_Genere"].tolist(),

                        "itemStyle": {
                            "borderRadius": [8,8,0,0],
                            "color": "#2563EB"
                        }
                    },

                    {
                        "name": "Spend",

                        "type": "bar",

                        "barWidth": 28,

                        "data": canal["Budget_Depense"].tolist(),

                        "itemStyle": {
                            "borderRadius": [8,8,0,0],
                            "color": "#0F172A"
                        }
                    }

                ]
            }

            st_echarts(
                options=canal_chart,
                height="420px",
                key="canal_chart"
            )

    # =====================================================
    # CPL PAR CLIENT
    # =====================================================

    with right_chart:

        st.markdown("""
<div class="section-block">
    <div class="section-label">Acquisition Efficiency</div>
    <div class="section-title">Cost Per Lead by Client</div>
    <div class="section-description">Evaluation of lead acquisition efficiency and profitability by customer account.</div>
</div>
        """, unsafe_allow_html=True)

        cpl_df = (
            df_filtre
            .groupby("Client")
            .agg({
                "Budget_Depense": "sum",
                "Nombre_Leads": "sum"
            })
            .reset_index()
        )

        cpl_df["CPL"] = (
            cpl_df["Budget_Depense"] /
            cpl_df["Nombre_Leads"]
        ).fillna(0)

        with st.container(border=True):

            cpl_chart = {

                "tooltip": {
                    "trigger": "axis"
                },

                "grid": {
                    "left": "5%",
                    "right": "5%",
                    "top": "10%",
                    "bottom": "10%",
                    "containLabel": True
                },

                "xAxis": {
                    "type": "category",
                    "data": cpl_df["Client"].tolist(),

                    "axisLabel": {
                        "rotate": 15
                    }
                },

                "yAxis": {
                    "type": "value"
                },

                "series": [

                    {
                        "type": "bar",

                        "barWidth": 34,

                        "data": cpl_df["CPL"].round(2).tolist(),

                        "itemStyle": {
                            "borderRadius": [10,10,0,0],
                            "color": "#14B8A6"
                        }
                    }

                ]
            }

            st_echarts(
                options=cpl_chart,
                height="420px",
                key="cpl_chart"
            )

# =========================================================
# ONGLET 3 : DATA
# =========================================================

with tab_data:

    st.subheader("Raw Marketing Data")

    st.dataframe(
        df_filtre,
        use_container_width=True,
        height=500
    )
