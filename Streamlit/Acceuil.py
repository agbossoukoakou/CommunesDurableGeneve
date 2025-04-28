import streamlit as st


st.set_page_config(
    page_title="Accueil - Analyse de la durabilité",
    layout="wide",
)




# Charger CSS local
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles/style.css")

# Importer FontAwesome pour icônes
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Header 

st.markdown('<header style="font-size: 46px;">Mes Communes durables - Genève</header>', unsafe_allow_html=True)


# Contenu principal
st.title(" Bienvenue sur notre plateforme")
st.markdown("""
    <div style="text-align: justify;">
        Ce projet répond à un besoin de transparence et d'accessibilité aux données liées au développement durable. En centralisant les indicateurs de développement durable des municipalités genevoises, nous offrons un outil de comparaison et de suivi temporel inédit qui servira aussi bien aux décideurs qu'aux citoyens. Notre solution transforme des données complexes en informations exploitables. Ce projet s'inscrit parfaitement dans la tendance croissante de demande de transparence sur les actions environnementales et sociales des institutions publiques.

    </div>
""", unsafe_allow_html=True)


st.write("""
                  
---

###  **Sources de données principales** :
- Statistique Genève
- Open Data Genève
- Bases publiques officielles

---

Utilisez le menu à gauche pour naviguer entre les pages !
""")


# Un bouton pour accéder directement aux indicateurs (environnementaux, sociaux et économiques)


if st.button("🔍 Explorer les Indicateurs Environnementaux"):
    st.switch_page("1_Indicateurs_Environnementaux") 



# Footer personnalisé
st.markdown("""
<footer>
Développé par [Josué Agbossou] © 2025 | Projet Nomades : Mes communes durables - Genève 
</footer>
""", unsafe_allow_html=True)
