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

st.subheader(f"Dane dla miasta {selected_city}")
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
statisctic = df_selection.groupby(['city','type'], observed=False)['pricePerSquareMeters'].agg(['median', 'std']).reset_index()
statisctic.columns = ['city','type', 'median_price', 'std_price']
df_city = df_selection.merge(statisctic, on=['city','type'])
df_city['is_bargain'] = df_city['pricePerSquareMeters'] < (df_city['median_price'] - 0.5 * df_city['std_price'])
top_bargains = df_city[(df_city['is_bargain']) & (df_city['standardScore'] > 0)].sort_values(by='pricePerSquareMeters')

if not top_bargains.empty:
    df_top_map = top_bargains.groupby(['city', 'type'], observed=False).head(3).reset_index(drop=True)
    st.subheader(f"Mapa okazji cenowych: {miasta_napis}")
    map_zoom = 10 if len(selected_city) == 1 else 5
    fig = px.scatter_map(df_top_map, lat="latitude", lon="longitude", size="standardScore", color="type", zoom=map_zoom, height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_top_map[['city', 'type', 'price', 'pricePerSquareMeters', 'standardScore', 'distCentreCategory']])

# --- PORÓWNANIE 3 MIAST ---
if selected_cities:
    df_comp = df[df['city'].isin(selected_cities)].copy()
    df_comp['type'] = pd.cut(df_comp["squareMeters"], bins=bins, labels=labels)
    df_comp['pricePerSquareMeters'] = df_comp['price']/df_comp['squareMeters']

    # Grupujemy po mieście i typie
    stats_comp = df_comp.groupby(['city', 'type'], observed = False)['pricePerSquareMeters'].median().unstack(level = 0)

    st.subheader(f"Porównanie mediany cen: {', '.join(selected_cities)}")
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
    st.info("Wybierz miasta w panelu bocznym, aby zobaczyć porównanie.")