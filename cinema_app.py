#Import des librairies Python nécessaires

import pandas as pd
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from PIL import Image

#Configuration de l'appication Streamlit : Titre, icône, mise en page
st.set_page_config(page_title="Cinémas de France", page_icon="🍿", layout="centered")

#Import du jeu de données 
dataset = pd.read_excel("dataset.xlsx")


#Ce sidebar contient le menu et une brève description de l'application 

with st.sidebar:
    popcorn_logo = Image.open('popcorn.png')
    st.image(popcorn_logo, width=200)

    st.title("Les cinémas de France")

    #Sauter la ligne 
    st.markdown('##')

    menu = st.selectbox("Menu",("Statistiques", "Distribution des données", "Carte intéractive"))

    st.markdown('##')

    st.markdown("Cette application explore les données des cinémas de la France métropolitaine. Elle présente les statistiques, la distribution des variables retenues et une carte interactive.<br></br> Réalisée par <strong style=color:#FF1919;> Walid GOUMI</strong>",unsafe_allow_html=True)

    st.markdown('##')

    efrei_logo = Image.open('LOGO_EFREI-PRINT_EFREI-WEB.png')
    st.image(efrei_logo, width=150)


#Première page
if menu == 'Statistiques':
    st.header("📈 Statistiques")

    st.subheader("Le jeu de données")
    st.markdown("Le jeu de données a été produit par le <b>Centre national du cinéma et de l'image animée</b>. Il comporte 2041 lignes qui correspondent aux cinémas de la France métropolitaine. Certains cinémas sont peut-être manquants mais cela relève de la collecte de données par le producteur. Je l'ai complété manuellement par l'acceptabilité  des cartes d'abonnement aux cinémas les plus utilisées, la carte UGC et la carte Cinepass (Pathé).", unsafe_allow_html=True )
    st.markdown("Source du jeu de données : https://www.data.gouv.fr/fr/datasets/r/cdb918e7-7f1a-44fc-bf6f-c59d1614ed6d ")
    st.markdown("Source des données concernant les cartes d'abonnement : https://salles-cinema.com/")
   
    st.markdown('##')

    list_cinema = dataset['nom'].tolist() #contient la liste des cinémas stockés dans la variable "nom"
    selected_cinema = st.multiselect('Rechercher un cinéma', sorted(list_cinema))
    all_optionscine = st.checkbox("Cocher pour tout sélectionner", value=True)

    #Renvoyer une erreur si aucun cinéma n'est sélectionné
    if all_optionscine:
        selected_cinema = list_cinema
    elif not selected_cinema:
        st.error(
            "Veuillez sélectionner un ou plusieurs cinémas dans le bandeau de sélection")

    dfcinema = dataset.loc[dataset['nom'].isin(selected_cinema)]
    
    st.write(dfcinema)

    st.markdown("##")
    st.subheader("La description statistique du jeu de données")

    st.write(dataset.describe())

    st.markdown("##")
    st.subheader("Représentation de la corrélation entre les variables quantitatives ")
    corr_heatmap = px.imshow(dataset[['population de la commune (2015)','population unité urbaine (2015)','écrans','fauteuils','séances 2020','entrées 2020', 'entrées 2019','nombre de films programmés 2020','nombre de films programmés 2020','nombre de films inédits 2020']].corr(), 
                  text_auto=False)
    st.plotly_chart(corr_heatmap,use_container_width=True)
    

#Deuxième page
elif menu == 'Distribution des données':
    st.header("🎬  Distribution des données")

    st.markdown('##')
    st.subheader("Analyse de l'activité des salles de cinéma")

    """ 
    entree = Les entrées au cinéma
    seance = Les séances de cinéma
    """
    #Configurer deux colonnes pour les deux métriques qu'on s'apprête à calculer
    col1_entree, col2_seances = st.columns(2)
    col1_entree.metric("Nombre d'entrées 2020", dataset['entrées 2020'].sum(),
     "{0:.2f}".format(dataset['évolution entrées 2020/2019'].mean()))
    col2_seances.metric("Nombre de séances 2020", dataset['séances 2020'].sum())


    options_entree = ["entrées 2020","entrées 2019"]
    select_entree = st.multiselect("Sélectionner une variable : ", options_entree,default='entrées 2020')

    if select_entree : 
        dataset[select_entree].fillna(0, inplace = True)
        entree_cinema = px.bar(
            dataset.sort_values(by=select_entree, ascending=False)[:20], 
            x='nom', 
            y=select_entree,
            title='Top 20 des cinémas par nombre d\'entrées')

        entree_cinema.update_layout(barmode='group')

        st.plotly_chart(entree_cinema, use_container_width=True)
        st.markdown("Le nombre d'entrée aux cinémas a baissé en 2020. La Covid est l'une des raisons pouvant expliquer cette baisse. <br> </br><b>UGC CINE CITE LES HALLES</b> est le cinéma dont le nombre d'entrées est le plus élevé suivi du <b>KINEPOLIS</b>.",unsafe_allow_html=True)
    else:
        st.error('Aucun élément selectionné')

    seances_cine = px.bar(
        dataset.sort_values(by='séances 2020', ascending=False)[:20], 
        x='nom', 
        y='séances 2020', 
        text_auto=True,
        title='Top 20 des cinémas par nombre de séances en 2020')

    seances_cine.update_traces(marker_color='red')

    st.plotly_chart(seances_cine,use_container_width=True)

    

    st.markdown('##')
    st.subheader("Analyse des équipements des salles de cinéma")

    list_equip = ["écrans", "fauteuils"]
    selected_equip = st.selectbox("Sélectionner un équipement : ", list_equip)

    equip_fig = px.bar(
    dataset.sort_values(by=selected_equip, ascending=False)[:20], 
    x='nom', 
    y=selected_equip,
    text_auto=True,
    title='Nombre de {} par cinéma'.format(selected_equip))

    equip_fig.update_traces(marker_color='red')
    
    st.plotly_chart(equip_fig, use_container_width=True)

    st.markdown("##")

    #Répartition des caractéristiques techniques des cinémas
    st.subheader("Les caractéristiques techniques")

    list_caract = ["genre", "multiplexe","Art et Essai"]
    selected_caract = st.selectbox("Sélectionner une caractéristique : ", list_caract)

    #Définir un commentaire pour chaque sélection
    if selected_caract == "genre":
        st.markdown("La quasi totalité des cinémas sont fixes à hauteur de 95%.")
    elif selected_caract =="multiplexe":
        st.markdown("La majorité des cinémas disposent de plusieurs écrans à hauteur de 89%")
    else :
        st.markdown("Seulement '60%' des cinémas de France disposent de la mention Art et Essai et proposent des films indépendants.")


    fig_caract = px.pie(dataset.groupby(selected_caract, as_index=False)['nom'].count(), 
               values='nom', 
               names=selected_caract)

    st.plotly_chart(fig_caract,use_container_width=True )

    st.markdown("##")
    
    # Répartition des abonnements UGC et CINEPASS respectivement
    st.subheader("Les abonnements")

    list_carte = ["carte ugc", "cinepass"]
    selected_carte = st.selectbox("Sélectionner un abonnement : ", list_carte)

    fig_carte = px.pie(dataset.groupby(selected_carte, as_index=False)['nom'].count(), 
    values='nom', 
    names=selected_carte)

    st.plotly_chart(fig_carte,use_container_width=True )


    #Création d'un dataframe pour analyse par région 
    df_region = pd.DataFrame(dataset.groupby('région administrative', as_index=False)['écrans', 'fauteuils'].sum())

    #Création d'un datefrome pour compter le nombre de cinémas par région
    df_region1 = pd.DataFrame(dataset.groupby('région administrative', as_index=False)['nom'].count())

    #Jointure des deux dataframe précentes pour obtenir le nb d'écrans, fauteils et cinémas par région 
    df_region2 = df_region.set_index('région administrative').join(df_region1.set_index('région administrative'))

    df_region2.rename(columns = {'nom':'nombre de cinémas'}, inplace = True)

    df_reg = df_region2.reset_index()

    #Réécrire le nom des régions pour pouvoir réaliser la jointure avec le fichier geojson des régions de France qui contient les coordonnées géographiques
    df_reg['régions'] = df_reg['région administrative'].map({'AUVERGNE / RHONE-ALPES':'Auvergne-Rhône-Alpes',
                                                                                'BOURGOGNE / FRANCHE-COMTE':'Bourgogne-Franche-Comté',
                                                                                'BRETAGNE':'Bretagne',
                                                                                'CENTRE-VAL DE LOIRE':'Centre-Val de Loire',
                                                                                'CORSE':'Corse',
                                                                                'GRAND EST':'Grand Est',
                                                                                'HAUTS DE FRANCE':'Hauts-de-France',
                                                                                'ILE-DE-FRANCE':'Île-de-France',
                                                                                'NORMANDIE':'Normandie',
                                                                                'NOUVELLE AQUITAINE':'Nouvelle-Aquitaine',
                                                                                'OCCITANIE':'Occitanie',
                                                                                'PAYS DE LA LOIRE':'Pays de la Loire',
                                                                                'PROVENCE-ALPES-COTE D\'AZUR':'Provence-Alpes-Côte d\'Azur',
                                                                                np.nan:'NY'},na_action=None)
    
    #import de la librairie geopandas non importé auparavant pour traiter le fichier geojson
    import geopandas as gpd
    regions = gpd.read_file('regions.geojson')
    regions1 = regions.set_index('nom').join(df_reg.set_index('régions'))
    regions2 =regions1.reset_index()

    st.markdown('##')
    st.subheader("Analyse par région")

    list_var= ["nombre de cinémas","écrans", "fauteuils"]
    selected_var = st.selectbox("Sélectionner une variable : ", list_var)

    #Répartition des variables choisies par région de France
    region_map = folium.Map(
                location=[46.8534, 2.3488],
                zoom_start=6)

    if selected_var == "nombre de cinémas":
        color_var = "YlGn"
    elif selected_var == "écrans":
        color_var = "OrRd"
    else :
        color_var = "BuPu"

    reg_cinema = folium.Choropleth(
    columns=['régions', selected_var],
    data=df_reg,
    key_on='feature.properties.nom',
    legend_name=selected_var,
    fill_color=color_var,
    fill_opacity=0.7,
    line_opacity=.1,
    geo_data=regions2,
    name='Nombre de cinémas par région',
    ).add_to(region_map)

    style_function = "font-size: 14px; font-weight:"
    reg_cinema.geojson.add_child(
        folium.features.GeoJsonTooltip(fields= ['nom',selected_var], style=style_function, labels=True,sticky=True, aliases = ['Région :',"{} : ".format(selected_var)]))

    #Afficher la carte dans streamlit
    st_folium(region_map, width=700)

    #Créer une table 
    st.table(df_reg[['régions',selected_var]].sort_values(by=selected_var, ascending=False))

#3ème page : objectif de l'application
else:
    st.header("🗺️ Carte intéractive")

    with st.container():
        st.markdown("Vous pouvez visualiser les cinémas d'une ou plusieurs localités. En passant le pointeur sur le marqueur rouge, il vous est possible de consulter les informations liées à un cinéma.")

        #sélectionner une commune
        list_commune = dataset['commune'].unique().tolist() #contient la liste des communes stockées dans la variable "commune"
        selected_commune = st.multiselect('Rechercher une localité', sorted(list_commune))
        all_optionscom = st.checkbox("Cocher pour tout sélectionner", value=True)
        st.write("Vous avez sélectionné", len(selected_commune), 'localité(s)')

        if all_optionscom:
            selected_commune = list_commune
        elif not selected_commune:
            st.error(
                "Veuillez sélectionner une ou plusieurs localités dans le bandeau de sélection")
            st.stop()

        #Création d'un nouvel dataset pour afficher les communes sélectionnées 
        dfcommune = dataset.loc[dataset['commune'].isin(selected_commune)]

        st.markdown('##')
        #Configurer les colonnes streamlit pour affichage des métriques
        col1_cine, col2_ecran, col3_fauteuil = st.columns(3)
        col1_cine.metric("Nombre de cinémas", dfcommune['nom'].count())
        col2_ecran.metric("Nombre d'écrans", dfcommune['écrans'].sum())
        col3_fauteuil.metric("Nombre de fauteuils", dfcommune['fauteuils'].sum())

        st.markdown('##')
        #Sélectionner un cinéma

        cinemas_france2 = folium.Map(
                location=[46.8534, 2.3488],
                zoom_start=6)

        #Ce plugin importé au début permet de regrouper les cinémas en Cluster selon la proximité géographique 
        cluster = plugins.MarkerCluster(name='Cinémas de France')

        cinemas_france2.add_child(cluster)

        for lat,lon,name,tip1,tip2,ecrans,fauteuils, commune in zip(dfcommune['latitude'], dfcommune['longitude'], dfcommune['nom'], dfcommune['carte ugc'],dfcommune['cinepass'], dfcommune['écrans'], dfcommune['fauteuils'], dfcommune['commune']):
            tooltip_text = '<i><b>Commune :</b></i> {}<br></br><b>Cinéma :</b> {}<br></br><b>Ecrans :</b> {}<br></br><b>Fauteuils :</b> {}<br></br><b>Carte UGC :</b> {}<br></br><b>Cinepass</b> : {}'.format(commune,name, ecrans, fauteuils, tip1, tip2)
            #Créer un marqueur avec une icone "film"
            folium.Marker(
                location=[lat,lon], 
                tooltip = tooltip_text,icon=folium.Icon(color='red', icon='film', 
                prefix='fa')).add_to(cluster)


        st_folium(cinemas_france2, width=700)
        st.markdown('##')
        st.subheader("Explorer le détail des cinémas")

        list_cinema2 = dfcommune['nom'].tolist()
        selected_cinema2 = st.multiselect('Sélectionner un cinéma', sorted(list_cinema2))
        all_optionscine2 = st.checkbox("Tout sélectionner", value=True)

        if all_optionscine2:
            selected_cinema2 = list_cinema2
        elif not selected_cinema2:
            st.error(
                "Veuillez sélectionner un ou plusieurs cinémas dans le bandeau de sélection")
            st.stop()

        dfcinema2 = dfcommune.loc[(dfcommune['commune'].isin(selected_commune)) & (dfcommune['nom'].isin(selected_cinema2)) ]

        st.write(dfcinema2[['nom','commune','écrans','fauteuils','carte ugc','cinepass','Art et Essai','multiplexe']])

      



        
