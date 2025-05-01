import streamlit as st
import pandas as pd
import altair as alt
import os
import numpy as np
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page et des options

st.set_page_config(
    page_title="Indicateurs Économiques - Communes Durables",
    page_icon="💰",
    layout="wide"
)

# Traduire les textes par défaut de Streamlit en français
st.markdown("""
<script>
// Traduction de "Choose an option" en "Choisir une option" et "Select..." en "Sélectionner..."
const mutationObserver = new MutationObserver(mutations => {
    // Traduction pour les selectbox
    const options = document.querySelectorAll('.stSelectbox div[data-baseweb="select"] > div > div:first-child');
    options.forEach(option => {
        if (option.textContent === 'Choose an option') {
            option.textContent = 'Choisir une option';
        }
    });
    
    // Traduction pour les multiselect
    const multiOptions = document.querySelectorAll('.stMultiSelect div[data-baseweb="select"] > div > div:first-child');
    multiOptions.forEach(option => {
        if (option.textContent === 'Select...') {
            option.textContent = 'Sélectionner...';
        }
    });
});

// Observer les changements dans le DOM
mutationObserver.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

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

# Ajouter un CSS personnalisé pour les titres d'indicateurs
st.markdown("""
<style>
.indicator-title {
    font-size: 24px;
    font-weight: bold;
    color: #F9A825;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Importer FontAwesome pour icônes
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Header personnalisé
st.markdown('<header><i class="fas fa-chart-line" style="margin-right: 10px;"></i>Indicateurs Économiques des Communes</header>', unsafe_allow_html=True)

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
population_path = find_file("donnee_population.csv")
prix_m2_path = find_file("donnee_prix_m2_mediane.csv")
revenu_path = find_file("donnee_revenu_brut_annuel.csv")

if not population_path:
    st.error("Impossible de trouver le fichier de données sur la population.")
    st.stop()
if not prix_m2_path:
    st.error("Impossible de trouver le fichier de données sur le prix du m².")
    st.stop()
if not revenu_path:
    st.error("Impossible de trouver le fichier de données sur les revenus bruts.")
    st.stop()

# Lecture des CSV
df_population = pd.read_csv(population_path)
df_prix_m2 = pd.read_csv(prix_m2_path)
df_revenu = pd.read_csv(revenu_path)

# S'assurer que les années sont des entiers
if "Année" in df_population.columns:
    df_population["Année"] = df_population["Année"].astype(int)
if "Année" in df_prix_m2.columns:
    df_prix_m2["Année"] = df_prix_m2["Année"].astype(int)
if "Année" in df_revenu.columns:
    df_revenu["Année"] = df_revenu["Année"].astype(int)

# Palette de couleurs cohérente (dans des tons dorés/orangés pour contraster avec les autres pages)
COLORS = ['#F9A825', '#FFA000', '#FF8F00', '#FF6F00', '#E65100', '#EF6C00', '#F57C00', 
          '#FB8C00', '#FF9800', '#FFA726', '#FFB74D', '#FFCC80', '#FFD180', '#FFE0B2',
          '#DAA520', '#CD853F', '#D2691E', '#A0522D', '#8B4513', '#CD5C5C']

# Fonction pour créer le bar chart race pour les années avec animation fluide
def render_bar_chart_race_annee(title, description, source, df, value_col, top_n=10, ascending=False, default_trend_communes=None):
    # Vérifier si la colonne existe
    if value_col not in df.columns:
        st.error(f"La colonne '{value_col}' n'existe pas dans le dataframe. Colonnes disponibles: {df.columns.tolist()}")
        return
    
    # Créer un ID sécurisé pour les clés Streamlit
    section_id = "".join(c if c.isalnum() else "_" for c in title)
    
    st.markdown(f"""
        <div class="info-card" style="border-left-color: #F9A825;">
            <div class="info-card-header">
                <i class="fas fa-chart-line"></i> <span class="indicator-title">{title}</span>
            </div>
            <p>{description}</p>
            <p><em>Source: {source}</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtrer pour exclure "Moyenne" pour l'animation
    df_filtered_anim = df[df["Commune"] != "Moyenne"].copy() if "Moyenne" in df["Commune"].unique() else df.copy()
    
    # Dataset complet pour les graphiques de tendance
    df_filtered = df.copy()
    
    # Obtenir la liste de toutes les communes
    all_communes = sorted(df_filtered["Commune"].unique().tolist())
    
    # Obtenir toutes les années disponibles
    years = sorted(df_filtered_anim["Année"].unique().tolist())
    
    # Créer des filtres pour sélectionner des communes spécifiques
    st.markdown("""
        <div style="background-color: #f5f7f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="font-weight: 600; color: #F9A825; margin-bottom: 10px;">Sélectionner des communes pour visualiser l'animation de graphique à barres:</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected_communes = st.multiselect(
        "Sélectionner des communes à comparer", 
        all_communes,
        default=[],
        key=f"{section_id}_select_communes",
        help="Sélectionnez au moins une commune pour visualiser le graphique"
    )
    
    # Créer un dictionnaire pour stocker les couleurs des communes
    commune_colors = {}
    for i, commune in enumerate(df_filtered_anim["Commune"].unique()):
        commune_colors[commune] = COLORS[i % len(COLORS)]
    
    # Préparer les données pour l'animation
    frames_data = []
    
    for year in years:
        year_data = df_filtered_anim[df_filtered_anim["Année"] == year].copy()
        
        # Filtrer pour les communes sélectionnées
        if selected_communes:
            year_data = year_data[year_data["Commune"].isin(selected_communes)]
            
            # Trier pour l'affichage
            year_data = year_data.sort_values(by=value_col, ascending=not ascending)
            
            frames_data.append({"year": year, "data": year_data})
    
    # Créer une figure Plotly avec animation fluide seulement si des communes sont sélectionnées
    if selected_communes and len(frames_data) > 0:
        # Obtenir toutes les communes uniques dans les frames pour définir les couleurs de manière cohérente
        all_frame_communes = set()
        for frame in frames_data:
            for commune in frame["data"]["Commune"]:
                all_frame_communes.add(commune)
        
        # Utiliser des couleurs cohérentes pour chaque commune
        color_map = {}
        for i, commune in enumerate(sorted(all_frame_communes)):
            color_map[commune] = COLORS[i % len(COLORS)]
        
        # Créer la figure de base avec les données de la première année
        first_frame = frames_data[0]
        
        # Obtenir les valeurs min et max pour toutes les frames pour une échelle cohérente
        all_values = []
        for frame in frames_data:
            all_values.extend(frame["data"][value_col].tolist())
        
        min_val = min(all_values) if all_values else 0
        max_val = max(all_values) if all_values else 100
        
        # Ajouter un peu de marge à l'échelle
        range_buffer = (max_val - min_val) * 0.1
        x_range = [min_val - range_buffer, max_val + range_buffer]
        
        fig = go.Figure(
            data=[
                go.Bar(
                    x=first_frame["data"][value_col],
                    y=first_frame["data"]["Commune"],
                    orientation='h',
                    text=first_frame["data"][value_col].round(2),
                    textposition='outside',
                    marker_color=[color_map[commune] for commune in first_frame["data"]["Commune"]],
                    width=0.7
                )
            ],
            layout=go.Layout(
                title=f"{title} ({first_frame['year']})",
                xaxis=dict(
                    title=title,
                    range=x_range,
                    autorange=False
                ),
                yaxis=dict(
                    title="Commune",
                    autorange="reversed",
                    categoryorder='total ascending'
                ),
                height=500,
                margin=dict(l=20, r=20, t=40, b=20),
                font=dict(size=14)
            )
        )
        
        # Ajouter les frames pour chaque année
        frames = []
        for frame_data in frames_data:
            year = frame_data["year"]
            data = frame_data["data"]
            
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=data[value_col],
                        y=data["Commune"],
                        orientation='h',
                        text=data[value_col].round(2),
                        textposition='outside',
                        marker_color=[color_map[commune] for commune in data["Commune"]],
                        width=0.7
                    )
                ],
                layout=go.Layout(
                    title=f"{title} ({year})"
                ),
                name=str(year)
            )
            frames.append(frame)
        
        fig.frames = frames# Configuration des boutons d'animation - vitesse moyenne par défaut
        playback_speed = 500  # 500ms entre frames = vitesse moyenne
        
        # Configuration des animations
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="▶️ Play",
                            method="animate",
                            args=[None, {
                                "frame": {"duration": playback_speed, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": playback_speed * 0.8, "easing": "cubic-in-out"}
                            }]
                        ),
                        dict(
                            label="⏸️ Pause",
                            method="animate",
                            args=[[None], {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0}
                            }]
                        )
                    ],
                    direction="left",
                    pad={"r": 10, "t": 10},
                    x=0.1,
                    y=0,
                    xanchor="right",
                    yanchor="top"
                )
            ],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 16},
                    "prefix": "Année: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": playback_speed * 0.5, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [
                            [str(year)],
                            {
                                "frame": {"duration": playback_speed, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": playback_speed * 0.5}
                            }
                        ],
                        "label": str(year),
                        "method": "animate"
                    }
                    for year in years
                ]
            }]
        )
        
        # Afficher le graphique
        st.plotly_chart(fig, use_container_width=True)
    elif not selected_communes:
        st.info("Veuillez sélectionner au moins une commune pour visualiser l'animation.")
    
    # Visualisation traditionnelle (graphique de tendance)
    st.markdown("""
        <div style="background-color: #f5f7f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="font-weight: 600; color: #F9A825; margin-bottom: 10px;">Évolution temporelle par commune:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Déterminer les communes par défaut
    if default_trend_communes is not None and all(commune in all_communes for commune in default_trend_communes):
        # Utiliser les communes spécifiées si elles existent dans les données
        default_communes = default_trend_communes
    else:
        # Sinon, utiliser la logique par défaut
        if "Genève" in all_communes and "Moyenne" in all_communes:
            default_communes = ["Genève", "Moyenne"]
        elif "Genève" in all_communes:
            default_communes = ["Genève"]
        elif "Moyenne" in all_communes:
            default_communes = ["Moyenne"]
        else:
            default_communes = all_communes[:3] if len(all_communes) >= 3 else all_communes
    
    # Sélection des communes pour le graphique de tendance
    trend_communes = st.multiselect(
        "Communes à comparer", 
        all_communes,
        default=default_communes,
        key=f"{section_id}_trend_communes"
    )
    
    if trend_communes:
        # Filtrer les données pour les communes sélectionnées
        df_trend = df_filtered[df_filtered["Commune"].isin(trend_communes)]
        
        # Création du graphique de tendance
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Graphique amélioré
            annees_sorted = sorted(df_trend["Année"].unique().tolist())
            
            # Création d'un graphique plus élaboré
            base = alt.Chart(df_trend).encode(
                x=alt.X('Année:O', title='Année', sort=annees_sorted)
            )
            
            # Ligne pour la tendance
            line = base.mark_line(strokeWidth=3).encode(
                y=alt.Y(f'{value_col}:Q', title=title),
                color=alt.Color('Commune:N', scale=alt.Scale(range=COLORS)),
                strokeDash=alt.StrokeDash('Commune:N', legend=None)
            )
            
            # Points pour les valeurs spécifiques
            points = base.mark_circle(size=100).encode(
                y=alt.Y(f'{value_col}:Q'),
                color=alt.Color('Commune:N', scale=alt.Scale(range=COLORS)),
                tooltip=[
                    alt.Tooltip('Commune:N', title='Commune'),
                    alt.Tooltip('Année:O', title='Année'),
                    alt.Tooltip(f'{value_col}:Q', title=title, format='.2f')
                ]
            )
            
            # Zone sous la courbe
            area = base.mark_area(opacity=0.2).encode(
                y=alt.Y(f'{value_col}:Q'),
                color=alt.Color('Commune:N', scale=alt.Scale(range=COLORS))
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
                <div style="font-weight: 600; color: #F9A825; margin-bottom: 10px;">Données détaillées:</div>
            """, unsafe_allow_html=True)
            
            df_display = df_trend.copy()
            df_display[value_col] = df_display[value_col].round(2)
            df_display = df_display[['Commune', 'Année', value_col]]
            df_display = df_display.rename(columns={value_col: 'Valeur'})
            df_display = df_display.sort_values(by=['Commune', 'Année'])
            
            st.dataframe(
                df_display,
                use_container_width=True,
                height=350
            )
    else:
        st.warning("Veuillez sélectionner au moins une commune pour visualiser l'évolution temporelle.")
    
    st.markdown("<hr>", unsafe_allow_html=True)

# Introduction contextuelle
st.markdown("""
<div class="info-card" style="border-left-color: #F9A825;">
    <div class="info-card-header">
        <i class="fas fa-info-circle"></i> À propos des indicateurs économiques
    </div>
    <p>
        Les indicateurs économiques permettent de suivre les aspects liés au développement économique, au pouvoir d'achat et au coût de la vie dans les communes.
        Les données présentées ci-dessous sont issues de sources officielles et permettent de comparer la situation économique des différentes communes genevoises.
    </p>
    <p>
        Sélectionnez les communes qui vous intéressent pour visualiser leur évolution ou les comparer entre elles.
    </p>
</div>
""", unsafe_allow_html=True)

# Section 1: Population
render_bar_chart_race_annee(
    title="Population (nombre d'habitants)",
    description="La population représente le nombre total d'habitants résidant dans une commune. Cet indicateur démographique fondamental reflète la taille et l'attractivité d'une commune. Une population importante ou en croissance est généralement associée à un dynamisme économique, à une offre plus diversifiée de services publics et privés, et à un potentiel fiscal plus important. Elle peut aussi indiquer une bonne qualité de vie, des opportunités d'emploi ou un parc immobilier adapté. Toutefois, l'augmentation de la population peut également entraîner des défis en termes d'infrastructures, de mobilité et de pression sur les ressources naturelles. Cet indicateur doit donc être analysé en conjonction avec d'autres pour évaluer pleinement l'équilibre du développement d'une commune.",
    source="Office cantonal de la statistique - OCSTAT",
    df=df_population,
    value_col="Population_nombre-hbt",  # Nom corrigé de la colonne
    top_n=10,
    ascending=False,  # Les valeurs plus élevées sont meilleures pour la population
    default_trend_communes=["Genève", "Moyenne"]
)

# Section 2: Prix du m²
render_bar_chart_race_annee(
    title="Prix médian du m² (CHF)",
    description="Le prix médian du mètre carré mesure la valeur immobilière médiane dans une commune, exprimée en francs suisses par mètre carré. Cet indicateur reflète directement le coût du logement et l'accessibilité de la propriété immobilière pour les ménages. Un prix au mètre carré plus bas est généralement considéré comme favorable pour l'accessibilité au logement et le pouvoir d'achat des résidents. Cependant, il peut aussi signaler une moindre attractivité économique ou une qualité de vie perçue comme inférieure. À l'inverse, un prix élevé témoigne souvent d'une forte demande liée à l'attractivité de la commune, mais peut entraîner des difficultés d'accès au logement et une gentrification. Cet indicateur constitue un baromètre important de la pression immobilière et des dynamiques socio-économiques à l'œuvre dans une commune.",
    source="Office cantonal de la statistique - OCSTAT",
    df=df_prix_m2,
    value_col="prix_m2_marche_libre_Mediane",  # Nom corrigé de la colonne
    top_n=10,
    ascending=True,  # Les valeurs plus basses sont meilleures pour le prix du m²
    default_trend_communes=["Genève", "Moyenne"]
)

# Section 3: Revenu brut - Couples mariés
render_bar_chart_race_annee(
    title="Revenu brut annuel médian des couples mariés (CHF)",
    description="Le revenu brut annuel médian des couples mariés représente le niveau de revenu pour lequel la moitié des couples mariés de la commune gagne plus et l'autre moitié gagne moins. Cet indicateur reflète le pouvoir d'achat et la santé économique des ménages composés de couples mariés. Un revenu médian élevé suggère généralement une meilleure qualité de vie potentielle, une plus grande capacité à épargner et à investir, ainsi qu'une contribution fiscale plus importante pour la commune. Il peut également indiquer la présence d'emplois qualifiés et bien rémunérés dans la région. Toutefois, cet indicateur doit être interprété en tenant compte du coût de la vie local, notamment des prix de l'immobilier, pour évaluer le véritable pouvoir d'achat des ménages.",
    source="Office cantonal de la statistique - OCSTAT",
    df=df_revenu,
    value_col="Médiane_couples_mariés",
    top_n=10,
    ascending=False,  # Les valeurs plus élevées sont meilleures pour le revenu
    default_trend_communes=["Genève", "Moyenne"]
)

# Section 4: Revenu brut - Célibataires
render_bar_chart_race_annee(
    title="Revenu brut annuel médian des célibataires (CHF)",
    description="Le revenu brut annuel médian des célibataires représente le niveau de revenu pour lequel la moitié des personnes célibataires de la commune gagne plus et l'autre moitié gagne moins. Cet indicateur est révélateur du pouvoir d'achat et de la situation économique des ménages composés d'une seule personne. Un revenu médian élevé peut indiquer de meilleures opportunités professionnelles, une plus grande autonomie financière et une meilleure qualité de vie potentielle pour les personnes vivant seules. Cet indicateur est particulièrement pertinent dans un contexte d'augmentation du nombre de ménages unipersonnels et permet d'évaluer la capacité des célibataires à faire face au coût de la vie local, notamment en matière de logement. Il complète l'indicateur sur les couples mariés et permet une analyse plus fine des disparités économiques au sein des différentes typologies de ménages.",
    source="Office cantonal de la statistique - OCSTAT",
    df=df_revenu,
    value_col="Médiane_celibataire",
    top_n=10,
    ascending=False,  # Les valeurs plus élevées sont meilleures pour le revenu
    default_trend_communes=["Genève", "Moyenne"]
)

# Footer personnalisé modifié (sans logos)
st.markdown("""
<footer>
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="text-align: left;">
            <div style="font-weight: bold; margin-bottom: 5px;">Mes Communes Durables - Genève</div>
            <div style="font-size: 13px;">Développé par Josué Agbossou</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 13px;">© 2025 | Projet Nomades</div>
        </div>
    </div>
</footer>
""", unsafe_allow_html=True)