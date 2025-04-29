import streamlit as st
import pandas as pd
import altair as alt
import os
# === Titre principal ===
st.title("Indicateurs Environnementaux des Communes")


# === Correction du chemin d'accès ===
current_dir = os.path.dirname(__file__)  # Dossier 'pages'
project_root = os.path.dirname(current_dir)  # Racine du projet
data_dir = os.path.join(project_root, "base_de_donnees")

# === Chargement des données ===
try:
    #df_dechet = pd.read_csv(os.path.join(data_dir, "donnees_dechet_par_habitant"))
    df_env = pd.read_csv(os.path.join(data_dir, "donnée_environement.csv"))
except FileNotFoundError as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.stop()




# Conversion des colonnes "Année" en datetime ou int selon format
df_dechet["Année"] = df_dechet["Année"].astype(int)
df_env["Année"] = pd.to_datetime(df_env["Année"]).dt.year

# === Configuration commune ===
def render_section(title, description, source, df, value_col):
    communes = df["Commune"].unique().tolist()
    communes_default = ["Genève", "Moyenne"] if "Genève" in communes and "Moyenne" in communes else communes[:2]
    selected_communes = st.multiselect(f"Communes à afficher – {title}", communes, default=communes_default, key=title)

    df_filtered = df[df["Commune"].isin(selected_communes)]

    st.subheader(title)
    st.write(description)
    st.caption(f"*{source}*")

    # Affichage du DataFrame filtré
    st.dataframe(df_filtered)

    # Graphique
    chart = (
        alt.Chart(df_filtered)
        .mark_area(opacity=0.3)
        .encode(
            x=alt.X("Année:T", title="Année"),
            y=alt.Y(f"{value_col}:Q", stack=None, title=value_col),
            color=alt.Color("Commune:N"),
        )
    )
    st.altair_chart(chart, use_container_width=True)
    st.markdown("---")  # séparation visuelle entre les indicateurs

# === Section 1: Déchets par habitant ===
render_section(
    title="Déchets par habitant (kg)",
    description="Cet indicateur mesure la quantité annuelle de déchets produits par habitant.",
    source="Office fédéral de la statistique (OFS)",
    df=df_dechet,
    value_col="Dechet_par_habitant_kg"
)

# === Section 2: Voitures électriques par borne ===
render_section(
    title="Nombre de voitures électriques par borne de recharge",
    description="Ce ratio estime le nombre de véhicules électriques par borne publique disponible.",
    source="Statistique cantonale et Confédération suisse",
    df=df_env[["Commune", "Année", "electric_cars_per_charging_spot"]],
    value_col="electric_cars_per_charging_spot"
)

# === Section 3: Consommation électrique annuelle ===
render_section(
    title="Consommation électrique annuelle par habitant (MWh)",
    description="Consommation moyenne annuelle d'électricité par habitant en MWh.",
    source="Services industriels des communes (SIG, etc.)",
    df=df_env[["Commune", "Année", "elec_consumption_mwh_per_year_per_capita"]],
    value_col="elec_consumption_mwh_per_year_per_capita"
)

# === Section 4: Production d'électricité renouvelable ===
render_section(
    title="Production annuelle d'électricité renouvelable par habitant (MWh)",
    description="Quantité moyenne annuelle d'électricité produite à partir de sources renouvelables par habitant.",
    source="Office fédéral de l’énergie (OFEN)",
    df=df_env[["Commune", "Année", "renelec_production_mwh_per_year_per_capita"]],
    value_col="renelec_production_mwh_per_year_per_capita"
)

