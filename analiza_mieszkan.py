# ABY URUCHOMIĆ, WPISZ W TERMINALU streamlit run analiza_mieszkan.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title="Analiza Mieszkań", layout="wide")
st.title(20*"-" + " Interaktywna Analiza Rynku Mieszkań "+20*"-")

# Wczytanie pliku csv
path = "apartments_pl_2024_06.csv"
df = pd.read_csv(path, encoding="utf-8-sig")

# Czyszczenie danych
df = df.drop_duplicates()
df.drop(["id","ownership","buildingMaterial","floor","poiCount","postOfficeDistance","pharmacyDistance","hasStorageRoom","condition","rooms","schoolDistance","kindergartenDistance","restaurantDistance","clinicDistance","collegeDistance"], axis=1, inplace=True)
df.dropna(inplace=True)

# Filtrowanie
st.sidebar.header("🔍 Filtry wyszukiwania")

available_cities = df['city'].unique()
selected_city = st.sidebar.multiselect("Wybierz miasto:", available_cities, max_selections=1)

min_price, max_price = int(df['price'].min()), int(df['price'].max())
selected_price = st.sidebar.slider("Zakres cenowy (zł):", min_price, max_price, value = (min_price, max_price), format="%d")

min_area, max_area = int(df['squareMeters'].min()), int(df['squareMeters'].max())
selected_area = st.sidebar.slider("Metraż (m2):", min_area, max_area, (min_area, max_area))

min_distance, max_distance = int(df['centreDistance'].min()), int(df['centreDistance'].max())
selected_distance = st.sidebar.slider("Odległość od centrum (km):", min_distance, max_distance, (min_distance, max_distance))

min_buildYear, max_buildYear = int(df['buildYear'].min()), int(df['buildYear'].max())
selected_year = st.sidebar.slider("Rok budowy: ", min_buildYear, max_buildYear, (min_buildYear, max_buildYear))

st.sidebar.markdown("---") # Linia oddzielająca
st.sidebar.subheader("🏗️ Udogodnienia")

filter_balcony = st.sidebar.checkbox("Balkon")
filter_elevator = st.sidebar.checkbox("Winda")
filter_parking = st.sidebar.checkbox("Parking")
filter_security = st.sidebar.checkbox("Ochrona")
filter_storage = st.sidebar.checkbox("Piwnica")

df_selection = df[
    (df['city'].isin(selected_city)) &
    (df['price'] >= selected_price[0]) &
    (df['price'] <= selected_price[1]) &
    (df['squareMeters'] >= selected_area[0]) &
    (df['squareMeters'] <= selected_area[1]) &
    (df['centreDistance'] >= selected_distance[0]) &
    (df['centreDistance'] <= selected_distance[1]) &
    (df['buildYear'] >= selected_year[0]) &
    (df['buildYear'] <= selected_year[1])
].copy()

if selected_city:
    miasta_napis = ", ".join(selected_city)
else:
    miasta_napis = "Wszystkie miasta"

if df_selection.empty:
    st.warning("Brak danych dla wybranych filtrów!")
    st.stop()

if filter_balcony:
    df_selection = df_selection[df_selection['hasBalcony'] == 'yes']
if filter_elevator:
    df_selection = df_selection[df_selection['hasElevator'] == 'yes']
if filter_parking:
    df_selection = df_selection[df_selection['hasParkingSpace'] == 'yes']
if filter_security:
    df_selection = df_selection[df_selection['hasSecurity'] == 'yes']
if filter_storage:
    df_selection = df_selection[df_selection['hasStorageRoom'] == 'yes']

# Nowy multiselect do porównania na dole
st.sidebar.header("📊 Porównaj 3 wybrane miasta")
cieties_list = df['city'].unique()
selected_cities = st.sidebar.multiselect("Wybierz do 3 miast do porównania:", cieties_list, max_selections=3, key="comp")

# Obliczenia
df_selection['pricePerSquareMeters'] = round(df_selection['price']/df_selection['squareMeters'], 2)
bins = [0, 40, 70, 200]
labels = ['Kawalerka', 'Średnie', 'Duże']
df_selection['type'] = pd.cut(df_selection['squareMeters'], bins=bins, labels=labels)

amenities = ["hasParkingSpace", "hasBalcony", "hasElevator", "hasSecurity"]
df_selection['standardScore'] = df_selection[amenities].replace({'yes': True, 'no': False}).astype(bool).sum(axis=1)

dist_bins = [0, 0.5, 1.5, 5, 50]
dist_labels = ['Blisko (<500m)', 'Spacerem (0.5-1.5km)', 'Autem (1.5-5km)', 'Daleko (>5km)']
df_selection['distCentreCategory'] = pd.cut(df_selection['centreDistance'], bins=dist_bins, labels=dist_labels)

# Statystyki główne
mediany = df_selection.groupby('type', observed=False)['pricePerSquareMeters'].median()

st.header(f"Dane dla miasta {selected_city}")
st.dataframe(df_selection[["city","type","buildYear","pricePerSquareMeters","standardScore","distCentreCategory"]].reset_index(drop=True))

# Wykres 1: Mediana

st.subheader(f"Mediana cen w mieście {selected_city}")
plt.figure(figsize=(10, 5))
bars = plt.bar(mediany.index, mediany.values, color="royalblue", width=0.6)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 100, f'{yval:.2f} zł', ha='center', va='bottom', fontweight='bold')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
st.pyplot(plt)
plt.close()

# Wykres 2: Odległość
st.subheader("Wpływ odległości od centrum miasta")
plt.figure(figsize=(12, 6))
for t in df_selection['type'].unique():
    subset = df_selection[df_selection['type'] == t]
    plt.scatter(subset['centreDistance'], subset['pricePerSquareMeters'], label=t, alpha=0.5)
plt.legend(title='Typ:')
st.pyplot(plt)
plt.close()

# Wykres 3: Rok budowy
st.subheader("Rozkład cen względem roku budowy")
plt.figure(figsize=(20, 6))
for t in df_selection['type'].unique():
    subset = df_selection[df_selection['type'] == t]
    plt.scatter(subset['buildYear'], subset['pricePerSquareMeters'], label=t, alpha=0.5)
st.pyplot(plt)
plt.close()

# Wykres 4: Boxplot
st.subheader("Rozkład cen względem udogodnień")
plt.figure(figsize=(18, 6))
sns.boxplot(x='standardScore', y='pricePerSquareMeters', data=df_selection, palette="Set2", hue='type')
st.pyplot(plt)
plt.close()

# --- OKAZJE ---

#TOP 3 w wybranym mieście poniżej mediany z każdej kategorii
statisctic = df_selection.groupby('type')['pricePerSquareMeters'].agg(['median', 'std']).reset_index()
statisctic.columns = ['type', 'median_price', 'std_price']
df_city = df_selection.merge(statisctic, on='type')

# Definicja okazji: Cena za m2 < (Mediana - 1 * Odchylenie Standardowe)
df_city['is_bargain'] = df_city['pricePerSquareMeters'] < (df_city['median_price'] - 1 * df_city['std_price'])

top_bargains = df_city[df_city['is_bargain']].sort_values(by='pricePerSquareMeters')

kawalerka = pd.DataFrame()
srednie = pd.DataFrame()
duze = pd.DataFrame()

if top_bargains.empty:
    st.write("Brak okazji cenowych.")
else:
    top = top_bargains[(top_bargains['standardScore'] > 0) ].sort_values(by='pricePerSquareMeters')
    if top.empty:
        st.write("Brak mieszkań spełniających kryteria udogodnień i odległości.")
    else:
        # 2. Grupowanie i wybieranie top 3 po typie mieszkania
        top_3_by_type = top.sort_values('pricePerSquareMeters').groupby('type').head(3).reset_index(drop=True)

        # 3. Wyświetlenie wyników
        kawalerka = top_3_by_type[top_3_by_type['type'] == 'Kawalerka'].reset_index(drop=True)
        srednie = top_3_by_type[top_3_by_type['type'] == 'Średnie'].reset_index(drop=True)
        duze = top_3_by_type[top_3_by_type['type'] == 'Duże'].reset_index(drop=True)

        kolumny_do_pokazania = ['pricePerSquareMeters','standardScore','distCentreCategory']

df_top_map = pd.concat([kawalerka, srednie, duze]).reset_index(drop=True)

# 4. Mapa tylko z tymi 9 okazjami
fig = px.scatter_map(
    df_top_map,
    lat="latitude",
    lon="longitude",
    size="standardScore",
    color = "type",
    color_discrete_map= {"Kawalerka": "#00FF00", "Średnie": "#0000FF", "Duże": "#FF0000"},
    hover_data=['type', 'price', 'pricePerSquareMeters', 'standardScore'],
    labels={"type": "Rodzaj mieszkania"},
    zoom=10,
    height=600
)

# 5. Styl mapy i wyświetlenie
fig.update_layout(map_style="open-street-map")
fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0})

if not df_top_map.empty:
    st.subheader(f"Mapa okazji cenowych: {selected_city}")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Szczegóły wybranych okazji")
    st.write(df_top_map[['type', 'price', 'pricePerSquareMeters', 'standardScore', 'distCentreCategory']])
else:
    st.warning(f"Brak ofert spełniających kryteria okazji w mieście {selected_city}.")

# --- ANALIZA WYBRANEJ OFERTY I PODOBNE OFERTY ---
st.markdown("---")
st.header("🧐 Analiza wybranej oferty")

# 1. Wybór oferty z tabeli 'df_top_map' (którą już masz w kodzie)
if not df_top_map.empty:
    selected_index = st.selectbox(
        "Wybierz numer oferty z tabeli powyżej (Index), aby zobaczyć szczegóły:",
        options=df_top_map.index,
        format_func=lambda x: f"Oferta nr {x} - {df_top_map.loc[x, 'type']} w mieście {df_top_map.loc[x, 'city']}"
    )

    selected_offer = df_top_map.loc[selected_index]

    # 2. Wyświetlenie podsumowania wybranej oferty w kolumnach
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cena", f"{selected_offer['price']:,} zł")
    with col2:
        st.metric("Cena za m²", f"{selected_offer['pricePerSquareMeters']:.2f} zł")
    with col3:
        st.metric("Metraż", f"{selected_offer['squareMeters']} m²")

    st.write(
        f"📍 **Lokalizacja:** {selected_offer['city']}, odległość od centrum: {selected_offer['distCentreCategory']}")
    st.write(f"🛠️ **Standard (0-4):** {selected_offer['standardScore']}")

    # 3. Szukanie podobnych ofert w INNYCH miastach
    st.subheader("🤖 Podobne oferty w innych miastach")

    # Kryteria podobieństwa: ten sam typ mieszkania, cena +/- 10%, inne miasto
    price_min = selected_offer['price'] * 0.90
    price_max = selected_offer['price'] * 1.10

    similar_offers = df[
        (df['city'] != selected_offer['city']) &
        (df['price'] >= price_min) &
        (df['price'] <= price_max)
        ].copy()

    # Ponownie musimy przypisać 'type' dla całego df, żeby móc filtrować po typie
    similar_offers['type'] = pd.cut(similar_offers['squareMeters'], bins=bins, labels=labels)
    similar_offers = similar_offers[similar_offers['type'] == selected_offer['type']]

    if not similar_offers.empty:
        # Wybieramy 2 losowe lub 2 najbliższe cenowo
        recommendations = similar_offers.sample(min(2, len(similar_offers)))

        # Obliczamy cenę za m2 dla rekomendacji, żeby tabela była spójna
        recommendations['pricePerSquareMeters'] = round(recommendations['price'] / recommendations['squareMeters'], 2)

        st.table(recommendations[['city', 'price', 'pricePerSquareMeters', 'squareMeters']])
    else:
        st.info("Nie znaleziono podobnych ofert w innych miastach w tym zakresie cenowym.")
else:
    st.info("Najpierw wybierz miasto i parametry, aby wygenerować tabelę okazji.")

# --- PORÓWNANIE 3 MIAST ---
st.markdown("---")
st.header(f"Porównanie mediany cen: {', '.join(selected_cities)}")

if selected_cities:
    df_comp = df[df['city'].isin(selected_cities)].copy()
    df_comp['type'] = pd.cut(df_comp["squareMeters"], bins=bins, labels=labels)
    df_comp['pricePerSquareMeters'] = df_comp['price']/df_comp['squareMeters']

    # Grupujemy po mieście i typie
    stats_comp = df_comp.groupby(['city', 'type'], observed = False)['pricePerSquareMeters'].median().unstack(level = 0)

    plt.figure(figsize=(16, 8))
    ax = stats_comp.plot(kind='bar', figsize=(16, 8), color=['royalblue', 'orange', 'forestgreen'], width=0.8)

    for bar in ax.patches:
        yval = bar.get_height()
        if yval > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 100, f'{yval:.2f} zł', ha='center', va='bottom', fontweight='bold', fontsize=10)

    plt.title(f"Mediana ceny za m2 dla poszczególnych kategorii", fontsize=10, fontweight='bold', pad=15)
    plt.ylabel("Cena za m2 [PLN]")
    plt.xlabel("Typ mieszkania")
    plt.xticks(rotation=0) # Napisy na osi X poziomo

    # Usunięcie górnej i prawej ramki
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    st.pyplot(plt)
    plt.close()

else:
    st.warning("Wybierz miasta w panelu bocznym, aby zobaczyć porównanie.")

# --- NAJTAŃSZE I NAJDROŻSZE MIASTO W POLSCE ---
st.markdown("---")
st.header("🏆 Najdroższe vs Najtańsze miasto")

# 1. Obliczamy ogólną medianę dla każdego miasta, żeby znaleźć liderów
# Robimy to na oryginalnym 'df', żeby pokazać prawdę o całym rynku
df_all = df.copy()
df_all['pricePerSquareMeters'] = df_all['price'] / df_all['squareMeters']
city_medians = df_all.groupby('city')['pricePerSquareMeters'].median().sort_values()

najtansze_miasto = city_medians.index[0]
najdrozsze_miasto = city_medians.index[-1]

# 2. Przygotowujemy dane tylko dla tych dwóch miast
df_extremes = df_all[df_all['city'].isin([najtansze_miasto, najdrozsze_miasto])].copy()
df_extremes['type'] = pd.cut(df_extremes['squareMeters'], bins=bins, labels=labels)

# 3. Obliczamy mediany z podziałem na typy
stats_extremes = df_extremes.groupby(['city', 'type'], observed=False)['pricePerSquareMeters'].median().unstack(level=0)

# 4. Wykres (Twoja stylistyka)
st.subheader(f"Zestawienie: {najtansze_miasto} (Najtańsze) vs {najdrozsze_miasto} (Najdroższe)")

fig, ax = plt.subplots(figsize=(12, 6))
# Ustawiamy konkretne kolory: czerwony dla drogiego, zielony dla taniego
stats_extremes.plot(kind='bar', ax=ax, color=['#e74c3c', '#2ecc71'], width=0.7)

# Dodanie Twoich etykiet
for p in ax.patches:
    yval = p.get_height()
    if yval > 0:
        ax.text(p.get_x() + p.get_width()/2, yval + 100, f'{yval:.0f} zł', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.title(f"Różnica w cenach za m² między ekstremami", fontsize=12, fontweight='bold')
plt.ylabel("Cena za m² [PLN]")
plt.xlabel("Typ mieszkania")
plt.xticks(rotation=0)
plt.legend(title="Miasto")

# Twoje usuwanie ramek
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

st.pyplot(fig)
plt.close()

# Krótka ciekawostka pod wykresem
roznica = city_medians.max() / city_medians.min()
st.info(f"💡 Ciekawostka: Mediana cen w mieście **{najdrozsze_miasto}** jest o **{roznica:.1f}x** wyższa niż w mieście **{najtansze_miasto}**.")