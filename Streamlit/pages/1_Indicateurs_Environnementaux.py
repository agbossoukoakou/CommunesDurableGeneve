import streamlit as st
import pandas as pd
import altair as alt
import os

# Configuration de la page
st.set_page_config(
    page_title="Indicateurs Environnementaux - Communes Durables",
    page_icon="🌿",
    layout="wide"
)

# Charger CSS local
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        try:
            with open(f"../{file_name}") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("Fichier CSS non trouvé. L'affichage peut être différent de celui attendu.")

# Chargement du CSS
local_css("styles/style.css")

# Importer FontAwesome pour icônes
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Header personnalisé
st.markdown('<header><i class="fas fa-leaf" style="margin-right: 10px;"></i>Indicateurs Environnementaux des Communes</header>', unsafe_allow_html=True)

# Fonction pour trouver le bon chemin de fichier
def find_file(file_name):
    possible_paths = [
        f"base_de_donnees/{file_name}",
        f"../base_de_donnees/{file_name}",
        f"Streamlit/base_de_donnees/{file_name}"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Chargement des fichiers CSV
dechet_path = find_file("donnees_dechet_par_habitant.csv")
env_path = find_file("donnee_environement.csv")

if not dechet_path:
    st.error("Impossible de trouver le fichier de données sur les déchets.")
    st.stop()
if not env_path:
    st.error("Impossible de trouver le fichier de données environnementales.")
    st.stop()

# Lecture des CSV
df_dechet = pd.read_csv(dechet_path)
df_env = pd.read_csv(env_path)

# S'assurer que les années du fichier déchets sont des entiers
df_dechet["Année"] = df_dechet["Année"].astype(int)

# Pour df_env, convertir les dates en format datetime
df_env["Date_Complète"] = pd.to_datetime(df_env["Année"])

# Fonction pour formater les dates
def format_date(date_obj):
    return date_obj.strftime("%d/%m/%Y")

# Configuration commune pour les indicateurs avec années simples (déchets)
def render_section_annee(title, description, source, df, value_col):
    st.markdown(f"""
        <div class="info-card" style="border-left-color: #2E8B57;">
            <div class="info-card-header">
                <i class="fas fa-chart-line"></i> {title}
            </div>
            <p>{description}</p>
            <p><em>Source: {source}</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Préparation des communes à sélectionner
    communes = sorted(df["Commune"].unique().tolist())
    
    # Forcer la sélection de Genève et Moyenne si elles existent
    default_communes = []
    if "Genève" in communes:
        default_communes.append("Genève")
    if "Moyenne" in communes:
        default_communes.append("Moyenne")
    
    st.markdown("""
        <div style="background-color: #f5f7f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Sélectionner les communes à comparer:</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected_communes = st.multiselect(
        "Communes à comparer", 
        communes, 
        default=default_communes, 
        key=f"{title}_select",
        help="Sélectionnez une ou plusieurs communes pour comparer leurs performances"
    )

    if not selected_communes:
        st.warning("Veuillez sélectionner au moins une commune pour visualiser les données.")
        return

    df_filtered = df[df["Commune"].isin(selected_communes)]
    df_filtered = df_filtered.sort_values(by=["Commune", "Année"])

    # Création de deux colonnes pour mettre le graphique et le tableau côte à côte
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Graphique amélioré
        colors = ['#2E8B57', '#4682B4', '#F9A825', '#E57373', '#9575CD', '#4DB6AC', '#FF8A65']
        annees_sorted = sorted(df_filtered["Année"].unique().tolist())
        
        # Création d'un graphique plus élaboré
        base = alt.Chart(df_filtered).encode(
            x=alt.X('Année:O', title='Année', sort=annees_sorted)
        )
        
        # Ligne pour la tendance
        line = base.mark_line(strokeWidth=3).encode(
            y=alt.Y(f'{value_col}:Q', title=title),
            color=alt.Color('Commune:N', scale=alt.Scale(range=colors)),
            strokeDash=alt.StrokeDash('Commune:N', legend=None)
        )
        
        # Points pour les valeurs spécifiques
        points = base.mark_circle(size=100).encode(
            y=alt.Y(f'{value_col}:Q'),
            color=alt.Color('Commune:N', scale=alt.Scale(range=colors)),
            tooltip=[
                alt.Tooltip('Commune:N', title='Commune'),
                alt.Tooltip('Année:O', title='Année'),
                alt.Tooltip(f'{value_col}:Q', title=title, format='.2f')
            ]
        )
        
        # Zone sous la courbe
        area = base.mark_area(opacity=0.2).encode(
            y=alt.Y(f'{value_col}:Q'),
            color=alt.Color('Commune:N', scale=alt.Scale(range=colors))
        )
        
        # Combinaison des couches
        chart = (area + line + points).properties(
            height=400
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            grid=True
        ).configure_legend(
            orient='bottom',
            titleFontSize=14,
            labelFontSize=12
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        # Tableau de données amélioré
        st.markdown("""
            <div style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Données détaillées:</div>
        """, unsafe_allow_html=True)
        
        df_display = df_filtered.copy()
        df_display[value_col] = df_display[value_col].round(2)
        df_display = df_display[['Commune', 'Année', value_col]]
        df_display = df_display.rename(columns={value_col: 'Valeur'})
        df_display = df_display.sort_values(by=['Commune', 'Année'])
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=350
        )
    
    st.markdown("<hr>", unsafe_allow_html=True)

# Configuration commune pour les indicateurs avec dates complètes (environnement)
def render_section_date(title, description, source, df, value_col):
    st.markdown(f"""
        <div class="info-card" style="border-left-color: #2E8B57;">
            <div class="info-card-header">
                <i class="fas fa-chart-line"></i> {title}
            </div>
            <p>{description}</p>
            <p><em>Source: {source}</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    communes = sorted(df["Commune"].unique().tolist())
    
    # Forcer la sélection de Genève et Moyenne si elles existent
    default_communes = []
    if "Genève" in communes:
        default_communes.append("Genève")
    if "Moyenne" in communes:
        default_communes.append("Moyenne")
    
    st.markdown("""
        <div style="background-color: #f5f7f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Sélectionner les communes à comparer:</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected_communes = st.multiselect(
        "Communes à comparer", 
        communes, 
        default=default_communes, 
        key=f"{title}_select",
        help="Sélectionnez une ou plusieurs communes pour comparer leurs performances"
    )

    if not selected_communes:
        st.warning("Veuillez sélectionner au moins une commune pour visualiser les données.")
        return

    df_filtered = df[df["Commune"].isin(selected_communes)]
    df_filtered = df_filtered.sort_values(by=["Commune", "Date_Complète"])
    df_filtered["Date_Affichage"] = df_filtered["Date_Complète"].apply(format_date)

    col1, col2 = st.columns([3, 1])
    
    with col1:
        colors = ['#2E8B57', '#4682B4', '#F9A825', '#E57373', '#9575CD', '#4DB6AC', '#FF8A65']
        dates_sorted = sorted(df_filtered["Date_Complète"].unique().tolist())
        dates_affichage_sorted = [format_date(date) for date in dates_sorted]
        
        base = alt.Chart(df_filtered).encode(
            x=alt.X('Date_Affichage:N', title='Date', sort=dates_affichage_sorted, 
                   axis=alt.Axis(labelAngle=45))
        )
        
        line = base.mark_line(strokeWidth=3).encode(
            y=alt.Y(f'{value_col}:Q', title=title),
            color=alt.Color('Commune:N', scale=alt.Scale(range=colors)),
            strokeDash=alt.StrokeDash('Commune:N', legend=None)
        )
        
        points = base.mark_circle(size=100).encode(
            y=alt.Y(f'{value_col}:Q'),
            color=alt.Color('Commune:N', scale=alt.Scale(range=colors)),
            tooltip=[
                alt.Tooltip('Commune:N', title='Commune'),
                alt.Tooltip('Date_Affichage:N', title='Date'),
                alt.Tooltip(f'{value_col}:Q', title=title, format='.2f')
            ]
        )
        
        area = base.mark_area(opacity=0.2).encode(
            y=alt.Y(f'{value_col}:Q'),
            color=alt.Color('Commune:N', scale=alt.Scale(range=colors))
        )
        
        chart = (area + line + points).properties(
            height=400
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            grid=True
        ).configure_legend(
            orient='bottom',
            titleFontSize=14,
            labelFontSize=12
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("""
            <div style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Données détaillées:</div>
        """, unsafe_allow_html=True)
        
        df_display = df_filtered.copy()
        df_display[value_col] = df_display[value_col].round(2)
        df_display = df_display[['Commune', 'Date_Affichage', value_col]]
        df_display = df_display.rename(columns={'Date_Affichage': 'Date', value_col: 'Valeur'})
        df_display = df_display.sort_values(by=['Commune', 'Date'])
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=350
        )
    
    st.markdown("<hr>", unsafe_allow_html=True)

# Introduction contextuelle
st.markdown("""
<div class="info-card" style="border-left-color: #4682B4;">
    <div class="info-card-header">
        <i class="fas fa-info-circle"></i> À propos des indicateurs environnementaux
    </div>
    <p>
        Les indicateurs environnementaux permettent de suivre les performances des communes en matière d'écologie et de développement durable.
        Les données présentées ci-dessous sont issues de sources officielles et permettent de comparer les efforts des différentes communes genevoises.
    </p>
    <p>
        Sélectionnez les communes qui vous intéressent pour chaque indicateur afin de visualiser et comparer leurs performances.
    </p>
</div>
""", unsafe_allow_html=True)

# Section 1: Déchets par habitant (utilise les années)
render_section_annee(
    title="Déchets par habitant (kg)",
    description="Cet indicateur mesure la quantité annuelle de déchets produits par habitant. Un chiffre plus bas indique une meilleure performance en matière de réduction des déchets.",
    source="Office fédéral de la statistique (OFS)",
    df=df_dechet,
    value_col="Dechet_par_habitant_kg"
)

# Section 2: Voitures électriques par borne (utilise les dates complètes)
render_section_date(
    title="Nombre de voitures électriques par borne de recharge",
    description="Ce ratio estime le nombre de véhicules électriques par borne publique disponible. Un ratio plus bas indique une meilleure disponibilité des infrastructures de recharge.",
    source="Statistique cantonale et Confédération suisse",
    df=df_env[["Commune", "Année", "Date_Complète", "electric_cars_per_charging_spot"]],
    value_col="electric_cars_per_charging_spot"
)

# Section 3: Consommation électrique annuelle (utilise les dates complètes)
render_section_date(
    title="Consommation électrique annuelle par habitant (MWh)",
    description="Consommation moyenne annuelle d'électricité par habitant en MWh. Une valeur plus basse indique une meilleure efficacité énergétique.",
    source="Services industriels des communes (SIG, etc.)",
    df=df_env[["Commune", "Année", "Date_Complète", "elec_consumption_mwh_per_year_per_capita"]],
    value_col="elec_consumption_mwh_per_year_per_capita"
)

# Section 4: Production d'électricité renouvelable (utilise les dates complètes)
render_section_date(
    title="Production annuelle d'électricité renouvelable par habitant (MWh)",
    description="Quantité moyenne annuelle d'électricité produite à partir de sources renouvelables par habitant. Une valeur plus élevée indique une meilleure performance en matière de transition énergétique.",
    source="Office fédéral de l'énergie (OFEN)",
    df=df_env[["Commune", "Année", "Date_Complète", "renelec_production_mwh_per_year_per_capita"]],
    value_col="renelec_production_mwh_per_year_per_capita"
)

# Footer personnalisé
st.markdown("""
<footer>
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="text-align: left;">
            <div style="font-weight: bold; margin-bottom: 5px;">Mes Communes Durables - Genève</div>
            <div style="font-size: 13px;">Développé par Josué Agbossou</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 13px;">© 2025 | Projet Nomades</div>
            <div style="font-size: 13px; margin-top: 5px;">
                <i class="fab fa-github" style="margin-right: 5px;"></i>
                <i class="fab fa-linkedin" style="margin-right: 5px;"></i>
                <i class="fas fa-envelope"></i>
            </div>
        </div>
    </div>
</footer>
""", unsafe_allow_html=True)