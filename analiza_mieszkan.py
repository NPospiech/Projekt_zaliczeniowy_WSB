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
selected_city = st.sidebar.multiselect("Wybierz miasto:", available_cities,max_selections=1)

min_price, max_price = int(df['price'].min()), int(df['price'].max())
selected_price = st.sidebar.slider("Zakres cenowy (zł):", min_price, max_price, value = (min_price, max_price),format="%d")

min_area, max_area = int(df['squareMeters'].min()), int(df['squareMeters'].max())
selected_area = st.sidebar.slider("Metraż (m2):", min_area, max_area, (min_area, max_area))

min_distance, max_distance = int(df['centreDistance'].min()), int(df['centreDistance'].max())
selected_distance = st.sidebar.slider("Odległość od centrum (km):", min_distance, max_distance, (min_distance, max_distance))

min_buildYear, max_buildYear = int(df['buildYear'].min()), int(df['buildYear'].max())
selected_year = st.sidebar.slider("Rok budowy: ", min_buildYear, max_buildYear, (min_buildYear, max_buildYear))

st.sidebar.markdown("---") # Linia oddzielająca
st.sidebar.subheader("🏗️ Udogodnienia")

# Tworzymy zmienne, które przechowują True (zaznaczone) lub False (niezaznaczone)
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
    (df['squareMeters'] <= selected_area[1])&
    (df['centreDistance'] >= selected_distance[0]) &
    (df['centreDistance'] <= selected_distance[1])&
    (df['buildYear'] >= selected_year[0]) &
    (df['buildYear'] <= selected_year[1])
].copy()

if selected_city:
    miasta_napis = ", ".join(selected_city)
else:
    miasta_napis = "Wszystkie miasta"

# Jeśli df_selection jest puste, zatrzymaj kod z komunikatem
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

st.sidebar.header("📊 Porównaj 3 wybrane miasta")
cieties = df['city'].unique()
selected_cities = st.sidebar.multiselect("Wybierz 3 miasta:", cieties,max_selections=3)

#Cena za m2
df_selection['pricePerSquareMeters'] = round(df_selection['price']/df_selection['squareMeters'],2)

# Podział mieszkania na segmenty - kawalerka (<40 m2), srednie (40-70 m2), duze (>70 m2)
bins = [0, 40, 70, 200]
labels = ['Kawalerka', 'Średnie', 'Duże']
df_selection['type'] = pd.cut(df_selection['squareMeters'], bins=bins, labels=labels)

# Standard Score - suma punktów (1 punkt za każde 'yes' lub 0 gdy jest 'no')
amenities = ["hasParkingSpace", "hasBalcony", "hasElevator", "hasSecurity"]
df_selection['standardScore'] = df_selection[amenities].replace({'yes': True, 'no': False}).astype(bool).sum(axis=1)

# Dystanse - (0-0.5 km: Bardzo blisko), (0.5-1.5 km: Spacerem), (1.5-5 km: Autem), (5+: Daleko)
dist_bins = [0, 0.5, 1.5, 5, 50]
dist_labels = ['Blisko (<500m)', 'Spacerem (0.5-1.5km)', 'Autem (1.5-5km)', 'Daleko (>5km)']

df_selection['distCentreCategory'] = pd.cut(df_selection['centreDistance'], bins=dist_bins, labels=dist_labels)

# Stworzenie nowej tabeli dla miasta, pominięcie niepotrzebnych kolumn
final_table = df_selection[["city","type","buildYear","pricePerSquareMeters","standardScore","distCentreCategory"]]
final_table.reset_index(drop=True, inplace=True)

# Mediana - cena vs typ mieszkania
mediany = df_selection.groupby('type')['pricePerSquareMeters'].median()

# Wyświetlenie tabeli na stronie
st.subheader(f"Dane dla miasta {selected_city}")
st.dataframe(final_table)

# Cena vs metraż według 3 kategorii
st.subheader(f"Mediana cen w mieście {selected_city}")
plt.figure(figsize=(10, 5))
bars = plt.bar(mediany.index, mediany.values, color="royalblue", width=0.6)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 100,f'{yval:.2f} zł', ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.title(f"Mediana ceny za m2 dla poszczególnych kategorii", fontsize=10, fontweight='bold', pad=15)
plt.ylabel("Cena za m2 [PLN]")
plt.xlabel("Typ mieszkania")
plt.xticks(rotation=0) # Napisy na osi X poziomo

# Usunięcie górnej i prawej ramki
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
st.pyplot(plt)
plt.close()

# Cena vs odległość budynku od centrum według 3 kategorii
st.subheader("Wpływ odległości od centrum miasta")
plt.figure(figsize=(12, 6))

<<<<<<< HEAD
for t in df_city['type'].unique():
    subset = df_city[df_city['type'] == t]
=======
for t in df_selection['type'].unique():
    subset = df_selection[df_selection['type'] == t]
>>>>>>> ce156dc (Porównanie cen dla 3 miast)
    plt.scatter(subset['centreDistance'], subset['pricePerSquareMeters'], label=t, alpha=0.5, edgecolors='w')

# Linia trendu
z = np.polyfit(df_selection['centreDistance'], df_selection['pricePerSquareMeters'], 1)
p = np.poly1d(z)

plt.plot(df_selection['centreDistance'].sort_values(), p(df_selection['centreDistance'].sort_values()), "r--")

plt.title("Wpływ odległości budynku od centrum na cenę m²", fontsize=14, fontweight='bold')
plt.xlabel("Odległośc od centrum [km]")
plt.ylabel("Cena za m² [PLN]")
plt.legend(title='Typ:')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
st.pyplot(plt)
plt.close()

# Cena vs rok budowy budynku według 3 kategorii
st.subheader("Rozkład cen względem roku budowy")
plt.figure(figsize=(20, 6))

for t in df_selection['type'].unique():
    subset = df_selection[df_selection['type'] == t]
    plt.scatter(subset['buildYear'], subset['pricePerSquareMeters'], label=t, alpha=0.5, edgecolors='w')

# Linia trendu
<<<<<<< HEAD
z = np.polyfit(df_city['buildYear'], df_city['pricePerSquareMeters'], 1)
=======
z = np.polyfit(df_selection['buildYear'], df_selection['pricePerSquareMeters'], 1)
>>>>>>> ce156dc (Porównanie cen dla 3 miast)
p = np.poly1d(z)

plt.plot(df_selection['buildYear'].sort_values(), p(df_selection['buildYear'].sort_values()), "r--")

plt.title("Wpływ roku budowy budynku na cenę m²", fontsize=14, fontweight='bold')
plt.xlabel("Rok budowy")
plt.ylabel("Cena za m² [PLN]")
plt.legend(title='Typ:')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
st.pyplot(plt)
plt.close()

# Cena vs udogodnienia według 3 kategorii mieszkań
st.subheader("Rozkład cen względem udogodnień")
plt.figure(figsize=(18, 6))

# Boxplot pokazuje rozkład cen dla każdej liczby punktów
sns.boxplot(x='standardScore', y='pricePerSquareMeters', data=df_selection, palette="Set2", hue='type', legend=True)

plt.title("Rozkład ceny m² względem liczby udogodnień", fontsize=14, fontweight='bold')
plt.xlabel("Liczba udogodnień (winda, parking, balkon, ochrona) [pkt]")
plt.ylabel("Cena za m² [PLN]")
plt.legend(title='Typ:')
plt.grid(True, axis='y', linestyle='--', alpha=0.5)
st.pyplot(plt)
plt.close()

#TOP 3 w wybranym mieście poniżej mediany z każdej kategorii
<<<<<<< HEAD
statisctic = df_city.groupby('type')['pricePerSquareMeters'].agg(['median', 'std']).reset_index()
statisctic.columns = ['type', 'median_price', 'std_price']
df_city = df_city.merge(statisctic, on='type')
=======
statisctic = df_selection.groupby(['city','type'],observed=False)['pricePerSquareMeters',].agg(['median', 'std']).reset_index()
statisctic.columns = ['city','type', 'median_price', 'std_price']
df_city = df_selection.merge(statisctic, on=['city','type'])
>>>>>>> ce156dc (Porównanie cen dla 3 miast)

# Definicja okazji: Cena za m2 < (Mediana - 1 * Odchylenie Standardowe)
df_city['is_bargain'] = df_city['pricePerSquareMeters'] < (df_city['median_price'] - 0.5 * df_city['std_price'])

top_bargains = df_city[(df_city['is_bargain']) & (df_city['standardScore'] > 0)].sort_values(by='pricePerSquareMeters')

if top_bargains.empty:
    st.warning(f"Brak wyraźnych okazji cenowych dla lokalizacji: {miasta_napis}")
    df_top_map = pd.DataFrame()
else:
    # 4. Wybieramy top 3 okazje dla każdego Miasta i każdego Typu
    df_top_map = top_bargains.groupby(['city', 'type'], observed=False).head(3).reset_index(drop=True)

if not df_top_map.empty:
    st.subheader(f"Mapa okazji cenowych: {miasta_napis}")

    # 5. Dynamiczny Zoom: jeśli miast jest dużo, oddalamy mapę
    map_zoom = 10 if len(selected_city) == 1 else 5

    fig = px.scatter_map(
        df_top_map,
        lat="latitude",
        lon="longitude",
        size="standardScore",
        color="type",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data=['city', 'type', 'price', 'pricePerSquareMeters', 'standardScore'],
        zoom=map_zoom,
        height=600
    )

    fig.update_layout(map_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 60, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Szczegóły wybranych okazji")
    # Formatuje tabelę, aby była czytelna
    st.dataframe(df_top_map[['city', 'type', 'price', 'pricePerSquareMeters', 'standardScore',
                             'distCentreCategory']].reset_index(drop=True))
else:
    st.info("Spróbuj zmienić filtry (np. zakres cen lub udogodnienia), aby system mógł znaleźć okazje.")


# Cena vs metraż według 3 kategorii dla 3 miast

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

