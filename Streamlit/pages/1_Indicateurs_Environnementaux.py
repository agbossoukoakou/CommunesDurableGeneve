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
    page_title="Indicateurs Environnementaux - Communes Durables",
    page_icon="🌿",
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
    color: #2E8B57;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

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

# Palette de couleurs cohérente
COLORS = ['#2E8B57', '#4682B4', '#F9A825', '#E57373', '#9575CD', '#4DB6AC', '#FF8A65',
          '#7CB342', '#5C6BC0', '#FFA726', '#EF5350', '#AB47BC', '#26A69A', '#FF7043', 
          '#66BB6A', '#42A5F5', '#FFCA28', '#EC407A', '#7E57C2', '#29B6F6', '#FFA000']

# Fonction pour créer le bar chart race pour les années avec animation fluide
def render_bar_chart_race_annee(title, description, source, df, value_col, top_n=10, ascending=False):
    # Créer un ID sécurisé pour les clés Streamlit
    section_id = "".join(c if c.isalnum() else "_" for c in title)
    
    st.markdown(f"""
        <div class="info-card" style="border-left-color: #2E8B57;">
            <div class="info-card-header">
                <i class="fas fa-chart-line"></i> <span class="indicator-title">{title}</span>
            </div>
            <p>{description}</p>
            <p><em>Source: {source}</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtrer pour exclure "Moyenne" pour l'animation
    df_filtered_anim = df[df["Commune"] != "Moyenne"].copy()
    
    # Dataset complet pour les graphiques de tendance
    df_filtered = df.copy()
    
    # Obtenir la liste de toutes les communes
    all_communes = sorted(df_filtered["Commune"].unique().tolist())
    
    # Obtenir toutes les années disponibles
    years = sorted(df_filtered_anim["Année"].unique().tolist())
    
    # Créer des filtres pour sélectionner des communes spécifiques
    st.markdown("""
        <div style="background-color: #f5f7f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Sélectionner des communes pour visualiser l'animation de graphique à barres:</p>
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
            <p style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Évolution temporelle par commune:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sélection des communes pour le graphique de tendance
    trend_communes = st.multiselect(
        "Communes à comparer", 
        all_communes,
        default=["Genève", "Moyenne"] if all(commune in all_communes for commune in ["Genève", "Moyenne"]) 
                else (["Genève"] if "Genève" in all_communes 
                      else (["Moyenne"] if "Moyenne" in all_communes 
                            else all_communes[:3])),
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
                <div style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Données détaillées:</div>
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

# Fonction pour créer le bar chart race pour les dates (environnement) avec animation fluide
def render_bar_chart_race_date(title, description, source, df, value_col, top_n=10, ascending=False):
    # Créer un ID sécurisé pour les clés Streamlit
    section_id = "".join(c if c.isalnum() else "_" for c in title)
    
    st.markdown(f"""
        <div class="info-card" style="border-left-color: #2E8B57;">
            <div class="info-card-header">
                <i class="fas fa-chart-line"></i> <span class="indicator-title">{title}</span>
            </div>
            <p>{description}</p>
            <p><em>Source: {source}</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtrer pour exclure "Moyenne" pour l'animation
    df_filtered_anim = df[df["Commune"] != "Moyenne"].copy()
    
    # Dataset complet pour les graphiques de tendance
    df_filtered = df.copy()
    
    # Obtenir la liste de toutes les communes
    all_communes = sorted(df_filtered["Commune"].unique().tolist())
    
    # Obtenir toutes les dates disponibles
    dates = sorted(df_filtered_anim["Date_Complète"].unique().tolist())
    date_labels = [format_date(date) for date in dates]
    
    # Créer des filtres pour sélectionner des communes spécifiques
    st.markdown("""
        <div style="background-color: #f5f7f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Sélectionner des communes pour visualiser l'animation de graphique à barres:</p>
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
    
    for i, date in enumerate(dates):
        date_data = df_filtered_anim[df_filtered_anim["Date_Complète"] == date].copy()
        
        # Filtrer pour les communes sélectionnées
        if selected_communes:
            date_data = date_data[date_data["Commune"].isin(selected_communes)]
            
            # Trier pour l'affichage
            date_data = date_data.sort_values(by=value_col, ascending=not ascending)
            
            frames_data.append({"date": date, "date_label": date_labels[i], "data": date_data})
    
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
        
        # Créer la figure de base avec les données de la première date
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
                title=f"{title} ({first_frame['date_label']})",
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
        
        # Ajouter les frames pour chaque date
        frames = []
        for i, frame_data in enumerate(frames_data):
            date_label = frame_data["date_label"]
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
                    title=f"{title} ({date_label})"
                ),
                name=str(i)  # Use index as name to ensure uniqueness
            )
            frames.append(frame)
        
        fig.frames = frames
        
        # Configuration des boutons d'animation - vitesse moyenne par défaut
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
                    "prefix": "Date: ",
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
                            [str(i)],
                            {
                                "frame": {"duration": playback_speed, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": playback_speed * 0.5}
                            }
                        ],
                        "label": date_label,
                        "method": "animate"
                    }
                    for i, date_label in enumerate(date_labels)
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
            <p style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Évolution temporelle par commune:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sélection des communes pour le graphique de tendance
    trend_communes = st.multiselect(
        "Communes à comparer", 
        all_communes,
        default=["Genève", "Moyenne"] if all(commune in all_communes for commune in ["Genève", "Moyenne"]) 
                else (["Genève"] if "Genève" in all_communes 
                      else (["Moyenne"] if "Moyenne" in all_communes 
                            else all_communes[:3])),
        key=f"{section_id}_trend_communes"
    )
    
    if trend_communes:
        # Filtrer les données pour les communes sélectionnées
        df_trend = df_filtered[df_filtered["Commune"].isin(trend_communes)]
        df_trend["Date_Affichage"] = df_trend["Date_Complète"].apply(format_date)
        
        # Création du graphique de tendance
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Graphique amélioré
            dates_sorted = sorted(df_trend["Date_Complète"].unique().tolist())
            dates_affichage_sorted = [format_date(date) for date in dates_sorted]
            
            base = alt.Chart(df_trend).encode(
                x=alt.X('Date_Affichage:N', title='Date', sort=dates_affichage_sorted, 
                       axis=alt.Axis(labelAngle=45))
            )
            
            line = base.mark_line(strokeWidth=3).encode(
                y=alt.Y(f'{value_col}:Q', title=title),
                color=alt.Color('Commune:N', scale=alt.Scale(range=COLORS)),
                strokeDash=alt.StrokeDash('Commune:N', legend=None)
            )
            
            points = base.mark_circle(size=100).encode(
                y=alt.Y(f'{value_col}:Q'),
                color=alt.Color('Commune:N', scale=alt.Scale(range=COLORS)),
                tooltip=[
                    alt.Tooltip('Commune:N', title='Commune'),
                    alt.Tooltip('Date_Affichage:N', title='Date'),
                    alt.Tooltip(f'{value_col}:Q', title=title, format='.2f')
                ]
            )
            
            area = base.mark_area(opacity=0.2).encode(
                y=alt.Y(f'{value_col}:Q'),
                color=alt.Color('Commune:N', scale=alt.Scale(range=COLORS))
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
            # Tableau de données
            st.markdown("""
                <div style="font-weight: 600; color: #2E8B57; margin-bottom: 10px;">Données détaillées:</div>
            """, unsafe_allow_html=True)
            df_display = df_trend.copy()
            df_display[value_col] = df_display[value_col].round(2)
            df_display = df_display[['Commune', 'Date_Affichage', value_col]]
            df_display = df_display.rename(columns={'Date_Affichage': 'Date', value_col: 'Valeur'})
            df_display = df_display.sort_values(by=['Commune', 'Date'])
            
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
<div class="info-card" style="border-left-color: #4682B4;">
    <div class="info-card-header">
        <i class="fas fa-info-circle"></i> À propos des indicateurs environnementaux
    </div>
    <p>
        Les indicateurs environnementaux permettent de suivre les performances des communes en matière d'écologie et de développement durable.
        Les données présentées ci-dessous sont issues de sources officielles et permettent de comparer les efforts des différentes communes genevoises.
    </p>
    <p>
        Sélectionnez les communes qui vous intéressent pour visualiser leur évolution ou les comparer entre elles.
    </p>
</div>
""", unsafe_allow_html=True)

# Section 1: Déchets par habitant (utilise les années) - Description améliorée
render_bar_chart_race_annee(
    title="Déchets par habitant (kg)",
    description="Cet indicateur mesure la quantité annuelle totale de déchets produits par habitant, incluant les déchets incinérés et recyclés. Il englobe les déchets urbains des ménages qui regroupent tous les déchets dont la collecte fait l'objet d'un monopole communal, comprenant les ordures ménagères, les déchets recyclables et les encombrants. Selon les normes fédérales de l'Office fédéral de l'environnement (OFEV), certains déchets recyclables ne sont pas comptabilisés dans les déchets urbains, notamment : les déchets encombrants transitant par un centre de tri (seule la part non-recyclable est prise en compte), les bouteilles en PET, le fer-blanc et l'aluminium (y compris les capsules de café à partir de 2017), le matériel OREA (appareils électriques et électroniques), les textiles, les piles et les batteries. Un chiffre plus bas indique une meilleure performance en matière de réduction des déchets.",
    source="Office cantonal de la statistique (OCSTAT)",
    df=df_dechet,
    value_col="Dechet_par_habitant_kg",
    top_n=10,
    ascending=True  # Les valeurs plus basses sont meilleures pour les déchets
)

# Section 2: Voitures électriques par borne (utilise les dates complètes) - Description améliorée
render_bar_chart_race_date(
    title="Nombre de voitures électriques par borne de recharge",
    description="Ce ratio mesure le nombre de véhicules électriques en circulation par rapport au nombre de bornes de recharge publiques disponibles dans chaque commune. Il constitue un indicateur important de l'infrastructure de mobilité durable et de la transition énergétique des transports. Un ratio plus bas indique une meilleure disponibilité des infrastructures de recharge par rapport au parc de véhicules électriques, ce qui favorise l'adoption de la mobilité électrique et réduit l'anxiété liée à l'autonomie. Cette métrique permet d'évaluer l'adéquation entre le développement du parc automobile électrique et le déploiement des infrastructures nécessaires à son fonctionnement optimal.",
    source="opendata.swiss - Confédération suisse",
    df=df_env,
    value_col="electric_cars_per_charging_spot",
    top_n=10,
    ascending=True  # Les valeurs plus basses sont meilleures (moins de voitures par borne)
)

# Section 3: Consommation électrique annuelle (utilise les dates complètes) - Description améliorée
render_bar_chart_race_date(
    title="Consommation électrique annuelle par habitant (MWh)",
    description="Cet indicateur représente la consommation moyenne annuelle d'électricité par habitant, exprimée en mégawattheures (MWh). Il permet d'évaluer l'efficacité énergétique globale d'une commune et les habitudes de consommation de ses résidents. Cette métrique prend en compte l'ensemble de la consommation électrique, incluant les usages résidentiels, commerciaux et les services publics, rapportée au nombre d'habitants. Une valeur plus basse indique une meilleure efficacité énergétique, qui peut résulter de diverses initiatives telles que l'utilisation d'appareils à basse consommation, l'amélioration de l'isolation des bâtiments, la sensibilisation des citoyens ou l'optimisation des infrastructures publiques.",
    source="opendata.swiss - Confédération suisse",
    df=df_env,
    value_col="elec_consumption_mwh_per_year_per_capita",
    top_n=10,
    ascending=True  # Les valeurs plus basses sont meilleures (moins de consommation)
)

# Section 4: Production d'électricité renouvelable (utilise les dates complètes) - Description améliorée
render_bar_chart_race_date(
    title="Production annuelle d'électricité renouvelable par habitant (MWh)",
    description="Cet indicateur mesure la quantité moyenne d'électricité produite à partir de sources renouvelables (solaire, éolienne, hydraulique, biomasse, etc.) par habitant et par an, exprimée en mégawattheures (MWh). Il reflète directement les efforts d'une commune en matière de transition énergétique et son engagement vers l'autonomie énergétique durable. Une valeur plus élevée indique une meilleure performance dans le développement des énergies renouvelables locales. Cette production décentralisée contribue à réduire la dépendance aux énergies fossiles, à diminuer l'empreinte carbone du territoire et à renforcer la résilience énergétique de la commune face aux fluctuations des marchés et aux défis climatiques.",
    source="opendata.swiss - Confédération suisse",
    df=df_env,
    value_col="renelec_production_mwh_per_year_per_capita",
    top_n=10,
    ascending=False  # Les valeurs plus élevées sont meilleures (plus de production renouvelable)
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