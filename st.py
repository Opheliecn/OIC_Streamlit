import folium
import piexif
from PIL import Image
import streamlit as st
from streamlit_folium import st_folium

# Convertir les coordonnées GPS en format EXIF
def convert_to_deg(value):
    deg, min, sec = value
    return [(int(deg), 1), (int(min), 1), (int(sec * 10000), 10000)]

st.title("Gestion des métadonnées EXIF d'une image")

# Charger une image
uploaded_image = st.file_uploader("Choisissez une image", type=["jpg", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image) 
    st.image(image, width=350) # Affichage de l'image choisie

    exif_data = piexif.load(image.info.get('exif', b'')) # Récupéartion des données EXIF sous forme de dictionnaire

    # Afficher les métadonnées actuelles
    st.subheader("Métadonnées EXIF actuelles :")
    st.write(exif_data)

    # Formulaire pour modifier les métadonnées
    st.subheader("Modifier les métadonnées EXIF :")

    st.write('Informations Système :') 
    # Les données de base sont utilisées pour remplir les cases par défaut
    make = st.text_input('Maker', exif_data['0th'].get(piexif.ImageIFD.Make, b"").decode(errors='ignore'))
    model = st.text_input('Modèle', exif_data['0th'].get(piexif.ImageIFD.Model, b"").decode(errors='ignore'))
    date_time = st.text_input('Datage (aaaa:mm:jj hh:mm:ss)', exif_data['Exif'].get(piexif.ExifIFD.DateTimeOriginal, b"").decode(errors='ignore'))

    st.write("Coordonnées GPS :")
    # Entrée des coordonnées avec 4 décimales
    lat_deg = st.number_input('Latitude (degrés)', min_value=-90.0, max_value=90.0, step=0.0001, format="%.4f")
    lon_deg = st.number_input('Longitude (degrés)', min_value=-180.0, max_value=180.0, step=0.0001, format="%.4f")
        
    # Lorsque l'on clique sur le bouton
    if st.button('Enregistrer les modifications'):
        # Modifie les données exif par les nouvelles
        exif_data['0th'][piexif.ImageIFD.Make] = make.encode('utf-8')
        exif_data['0th'][piexif.ImageIFD.Model] = model.encode('utf-8')
        exif_data['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_time.encode('utf-8')

        # Convertir les coordonnées GPS en format EXIF
        lat_exif = convert_to_deg((abs(lat_deg), int((abs(lat_deg) % 1) * 60), ((abs(lat_deg) * 3600) % 60)))
        lon_exif = convert_to_deg((abs(lon_deg), int((abs(lon_deg) % 1) * 60), ((abs(lon_deg) * 3600) % 60)))

        exif_data["GPS"][piexif.GPSIFD.GPSLatitude] = lat_exif
        exif_data["GPS"][piexif.GPSIFD.GPSLatitudeRef] = ('N' if lat_deg >= 0 else 'S').encode('utf-8')
        exif_data["GPS"][piexif.GPSIFD.GPSLongitude] = lon_exif
        exif_data["GPS"][piexif.GPSIFD.GPSLongitudeRef] = ('E' if lon_deg >= 0 else 'W').encode('utf-8')

        exif_bytes = piexif.dump(exif_data)  # Mise en forme des données EXIF sous forme d'octets pour être intégrés à l'image
        
        # Enregistrement des nouvelles EXIF dans un fichier jpeg
        image_path = "new_exif.jpg"
        image.save(image_path, 'jpeg', exif=exif_bytes)

        # Création d'un bouton de téléchargement
        with open(image_path, "rb") as fp:
            st.download_button(
                label="Télécharger l'image modifiée",
                data=fp,
                file_name=image_path,
                mime="image/jpeg"
            )

    # Créer une carte folium avec un point
    m = folium.Map(location=(lat_deg, lon_deg), zoom_start=3)
    folium.Marker(
        location=[lat_deg, lon_deg],
        icon=folium.Icon(color="blue")
    ).add_to(m)

    # Affichage de la carte avec les coordonnées GPS
    st.subheader("Coordonnées GPS modifiées de l'image:")
    st_folium(m, width=700, height=500)

    # Endroits visités 
    cities = [
        {"Ville": "Paris, France", "lat": 48.8566, "lon": 2.3522},
        {"Ville": "Los Angeles, États-Unis", "lat": 34.05334, "lon": -118.24235},
        {"Ville": "Séoul, Corée du Sud", "lat": 37.56698, "lon": 126.97824},
        {"Ville": "Santander, Espagne", "lat": 43.46167, "lon": -3.81047},
        {"Ville": "Tulum, Mexique", "lat": 20.21187, "lon": -87.45805},
        {"Ville": "PLaya Del Carmen, Mexique", "lat": 20.65459, "lon": -87.07764},
        {"Ville": "Dublin, Irlande", "lat": 53.34412, "lon": -6.26734},
        {"Ville": "Londres, Angleterre", "lat": 51.50335, "lon": 0.07940},
        {"Ville": "Djerba, Tunisie", "lat": 33.87612, "lon": 10.85175},
        {"Ville": "Zagreb, Croatie", "lat": 45.81057, "lon": 15.97214},
        {"Ville": "Dubrovnik, Croatie", "lat": 42.64846, "lon": 18.08554},
        {"Ville": "Munich, Allemagne", "lat": 48.13799, "lon": 11.57518}
    ]
    
    m2 = folium.Map(location=[0, 0], zoom_start=2)
    for city in cities:
        folium.Marker([city["lat"], city["lon"]], tooltip=city["Ville"], icon=folium.Icon(icon='plane', color='#ea698b')).add_to(m2)
        
    for i in range(len(cities) - 1):
        city1 = cities[i]
        city2 = cities[i + 1]
        points = [[city1["lat"], city1["lon"]], [city2["lat"], city2["lon"]]]
        folium.PolyLine(points, color="#c05299", weight=2.5, opacity=1).add_to(m2)

    st.subheader("Carte des lieux visités:")
    st_folium(m2, width=700, height=500)