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

# Wybór miasta w panelu bocznym
available_cities = df['city'].unique()
selected_city = st.sidebar.selectbox("Wybierz miasto:", sorted(available_cities))

# Dynamiczne filtrowanie danych
df_city = df[df['city'] == selected_city].copy()

#Cena za m2
df_city['pricePerSquareMeters'] = round(df_city['price']/df_city['squareMeters'],2)

# Podział mieszkania na segmenty - kawalerka (<40 m2), srednie (40-70 m2), duze (>70 m2)
bins = [0, 40, 70, 200]
labels = ['Kawalerka', 'Średnie', 'Duże']
df_city['type'] = pd.cut(df_city['squareMeters'], bins=bins, labels=labels)

# Standard Score - suma punktów (1 punkt za każde 'yes' lub 0 gdy jest 'no')
amenities = ["hasParkingSpace", "hasBalcony", "hasElevator", "hasSecurity"]
df_city['standardScore'] = df_city[amenities].replace({'yes': True, 'no': False}).astype(bool).sum(axis=1)

# Dystanse - (0-0.5 km: Bardzo blisko), (0.5-1.5 km: Spacerem), (1.5-5 km: Autem), (5+: Daleko)
dist_bins = [0, 0.5, 1.5, 5, 50]
dist_labels = ['Blisko (<500m)', 'Spacerem (0.5-1.5km)', 'Autem (1.5-5km)', 'Daleko (>5km)']

df_city['distCentreCategory'] = pd.cut(df_city['centreDistance'], bins=dist_bins, labels=dist_labels)

# Stworzenie nowej tabeli dla miasta, pominięcie niepotrzebnych kolumn
final_table = df_city[["type","buildYear","pricePerSquareMeters","standardScore","distCentreCategory"]]
final_table.reset_index(drop=True, inplace=True)

# Mediana - cena vs typ mieszkania
mediany = df_city.groupby('type')['pricePerSquareMeters'].median()

# Wyświetlenie tabeli na stronie
st.subheader(f"Dane dla miasta {selected_city.capitalize()}")
st.dataframe(final_table)

# Cena vs metraż według 3 kategorii
st.subheader(f"Mediana cen w mieście {selected_city.capitalize()}")
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

for t in df_city['type'].unique():
    subset = df_city[df_city['type'] == t]
    plt.scatter(subset['centreDistance'], subset['pricePerSquareMeters'], label=t, alpha=0.5, edgecolors='w')

# Linia trendu
z = np.polyfit(df_city['centreDistance'], df_city['pricePerSquareMeters'], 1)
p = np.poly1d(z)

plt.plot(df_city['centreDistance'].sort_values(), p(df_city['centreDistance'].sort_values()), "r--")

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

for t in df_city['type'].unique():
    subset = df_city[df_city['type'] == t]
    plt.scatter(subset['buildYear'], subset['pricePerSquareMeters'], label=t, alpha=0.5, edgecolors='w')

# Linia trendu
z = np.polyfit(df_city['buildYear'], df_city['pricePerSquareMeters'], 1)
p = np.poly1d(z)

plt.plot(df_city['buildYear'].sort_values(), p(df_city['buildYear'].sort_values()), "r--")

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
sns.boxplot(x='standardScore', y='pricePerSquareMeters', data=df_city, palette="Set2", hue='type', legend=True)

plt.title("Rozkład ceny m² względem liczby udogodnień", fontsize=14, fontweight='bold')
plt.xlabel("Liczba udogodnień (winda, parking, balkon, ochrona) [pkt]")
plt.ylabel("Cena za m² [PLN]")
plt.legend(title='Typ:')
plt.grid(True, axis='y', linestyle='--', alpha=0.5)
st.pyplot(plt)
plt.close()

#TOP 3 w wybranym mieście poniżej mediany z każdej kategorii
statisctic = df_city.groupby('type')['pricePerSquareMeters'].agg(['median', 'std']).reset_index()
statisctic.columns = ['type', 'median_price', 'std_price']
df_city = df_city.merge(statisctic, on='type')

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
    st.subheader(f"Mapa okazji cenowych: {selected_city.capitalize()}")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Szczegóły wybranych okazji")
    st.write(df_top_map[['type', 'price', 'pricePerSquareMeters', 'standardScore', 'distCentreCategory']])
else:
    st.warning(f"Brak ofert spełniających kryteria okazji w mieście {selected_city.capitalize()}.")

