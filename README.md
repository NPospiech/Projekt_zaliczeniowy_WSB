**🏠 Interaktywna Analiza Rynku Mieszkań**

Aplikacja webowa zbudowana w Streamlit, służąca do analizy rynku mieszkań w Polsce (dane z czerwca 2024). 
Projekt łączy wizualizację danych z prostym modelem uczenia maszynowego, aby pomagać użytkownikom w identyfikacji prawdziwych okazji rynkowych.

**🚀 Kluczowe Funkcje**

**- Filtrowanie:** Przeszukiwanie ofert według miast, ceny, metrażu, odległości od centrum oraz udogodnień (winda, balkon, parking itp.).

**- Wizualizacja Statystyczna:** Wykresy mediany ceny w wybranym mieście, rozkładu cen względem roku budowy, standardu i lokalizacji (Matplotlib, Seaborn, Plotly).

**- Mapa Okazji:** Geolokalizacja 3 najlepszych ofert dla każdegoz 3 typów mieszkań (najtańsze mieszkania względem mediany w danej kategorii metrażowej).

**- Deal Score (ML):** System oceny ofert oparty na Regresji Liniowej. Model przewiduje "sprawiedliwą" cenę nieruchomości na podstawie jej cech fizycznych i porównuje ją z ceną rynkową.

**- System Rekomendacji:** Po wybraniu konkretnej oferty, aplikacja automatycznie znajduje podobne mieszkania w innych miastach w zbliżonym budżecie.

**- Porównanie median dla 3 wybranych miast:** Porównanie mediany cen dla 3 wskazanych mieszkań

**- Najdroższe vs Najtańsze miasto:** Porównanie najdroższego i najtańszego miasta w Polsce


**🧠 Jak działa Deal Score?**

Aplikacja wykorzystuje model LinearRegression z biblioteki scikit-learn.

Trening: Model uczy się na przefiltrowanym zbiorze danych, analizując relacje między squareMeters, centreDistance, standardScore i buildYear a ceną.

Predykcja: Dla każdej oferty wyliczana jest cena teoretyczna (predictedPrice).

Ocena:

🔥 OKAZJA: Cena rzeczywista < 90% ceny przewidzianej.

✅ DOBRA: Cena rzeczywista < 95% ceny przewidzianej.

⚖️ RYNKOWA: Cena zbliżona do modelu (+/- 5%).

🚩 DROGO: Cena znacznie powyżej modelu.


**📦 Wymagane biblioteki i uruchomienie Streamlit**

1. Biblioteki:

Bash
pip install streamlit pandas numpy matplotlib plotly seaborn scikit-learn

2. Uruchomienie StreamLit:

Bash
streamlit run analiza_mieszkan.py

**📊 Dane:**

Projekt korzysta z bazy danych apartments_pl_2024_06.csv - https://www.kaggle.com/datasets/krzysztofjamroz/apartment-prices-in-poland
