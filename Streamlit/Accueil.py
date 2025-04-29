import streamlit as st
import os
import pandas as pd

st.set_page_config(
    page_title="Mes Communes Durables - Genève",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Charger CSS local
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles/style.css")

# Importer FontAwesome pour icônes
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Header 
st.markdown('<header>Mes Communes Durables <span style="font-size: 32px; margin-left: 10px;">Genève</span></header>', unsafe_allow_html=True)

# Structure en colonnes pour la page d'accueil
col1, col2 = st.columns([2, 1])

with col1:
    # Contenu principal
    st.markdown("""
        <h1><i class="fas fa-leaf" style="color: #F9A825;"></i> Bienvenue sur notre plateforme</h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-card">
            <div class="info-card-header">
                <i class="fas fa-info-circle"></i> À propos du projet
            </div>
            <p style="text-align: justify;">
                Ce projet répond à un besoin de <span class="highlight-text">transparence</span> et d'<span class="highlight-text">accessibilité</span> 
                aux données liées au développement durable. En centralisant les indicateurs de développement durable des municipalités genevoises, 
                nous offrons un outil de comparaison et de suivi temporel inédit qui servira aussi bien aux décideurs qu'aux citoyens. 
                Notre solution transforme des données complexes en informations exploitables. Ce projet s'inscrit parfaitement dans la tendance 
                croissante de demande de transparence sur les actions environnementales et sociales des institutions publiques.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # Carte d'information sur les indicateurs
    st.markdown("""
        <div class="info-card" style="border-left-color: #4682B4;">
            <div class="info-card-header">
                <i class="fas fa-chart-line"></i> Nos Indicateurs
            </div>
            <ul style="padding-left: 1.5rem;">
                <li><strong>Environnementaux</strong>: Dechets par habitants , Nombre de voitures électrique/ de borne de chargement, etc.</li>
                <li><strong>Sociaux</strong>:   Densité de la population,Logements subventionnée, etc.</li>
                <li><strong>Économiques</strong>:Revenu brute, Prix du m2 à l'achat d'un bien immobilier , etc.</li>
            </ul>
            <div style="text-align: center; margin-top: 1rem;">
                <i class="fas fa-link" style="font-size: 0.9rem;"></i> Utilisez le menu latéral pour explorer
            </div>
        </div>
    """, unsafe_allow_html=True)
    
# Section des accès rapides
st.markdown("""
    <hr>
    <h2><i class="fas fa-compass" style="color: #F9A825;"></i> Accès Rapide</h2>
""", unsafe_allow_html=True)

# Utilisation de colonnes pour les accès rapides
col_env, col_soc, col_eco = st.columns(3)

with col_env:
    if st.button("🌿 Indicateurs Environnementaux", key="env_button", use_container_width=True):
        st.switch_page("pages/1_Indicateurs_Environnementaux.py")

with col_soc:
    if st.button("👥 Indicateurs Sociaux", key="soc_button", use_container_width=True):
        st.switch_page("pages/2_Indicateurs_Sociaux.py")

with col_eco:
    if st.button("💹 Indicateurs Économiques", key="eco_button", use_container_width=True):
        st.switch_page("pages/3_Indicateurs_Economiques.py")



# Section des sources de données
st.markdown("""
    <hr>
    <h2><i class="fas fa-database" style="color: #4682B4;"></i> Sources de données</h2>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
        <div class="info-card" style="height: 150px;">
            <div class="info-card-header">
                <i class="fas fa-chart-pie"></i> Office cantonal de la statistique - OCSTAT
            </div>
            <p>Données démographiques et statistiques officielles du canton de Genève, incluant des indicateurs socio-économiques et environnementaux.</p>
        </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
        <div class="info-card" style="height: 150px;">
            <div class="info-card-header">
                <i class="fas fa-bolt"></i> Reporter Énergie
            </div>
            <p>Données sur la consommation énergétique, l'utilisation des ressources et la transition écologique des communes genevoises.</p>
        </div>
    """, unsafe_allow_html=True)

# Section objectifs
st.markdown("""
    <hr>
    <h2><i class="fas fa-bullseye" style="color: #4682B4;"></i> Objectifs du projet</h2>
""", unsafe_allow_html=True)

# Utilisation de colonnes pour les objectifs
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="info-card">
            <div class="info-card-header">
                <i class="fas fa-search"></i> Pour les citoyens et chercheurs
            </div>
            <ul>
                <li>Accès facilité aux données de durabilité</li>
                <li>Comparaison entre communes</li>
                <li>Suivi de l'évolution temporelle des indicateurs</li>
                <li>Base pour la recherche académique</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="info-card">
            <div class="info-card-header">
                <i class="fas fa-users-cog"></i> Pour les décideurs
            </div>
            <ul>
                <li>Outil d'aide à la décision</li>
                <li>Identification des bonnes pratiques</li>
                <li>Visualisation des domaines nécessitant des améliorations</li>
                <li>Support pour la communication publique</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

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