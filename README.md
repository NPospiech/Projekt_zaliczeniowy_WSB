# 🏠 Analiza cen nieruchomości

---

## 📊 O Projekcie
Interaktywna aplikacja webowa zbudowana w frameworku **Streamlit**, służąca do analizy rynku nieruchomości w Polsce (na podstawie danych z czerwca 2024). Projekt łączy wizualizację danych z modelem uczenia maszynowego, aby pomagać użytkownikom w precyzyjnej identyfikacji prawdziwych okazji rynkowych.

---

## 🚀 Kluczowe Funkcje

* **Interaktywne Filtrowanie:** Przeszukiwanie ofert według miast, ceny, metrażu, odległości od centrum oraz udogodnień (winda, balkon, parking itp.).
* **Wizualizacja Statystyczna:** Wykresy rozkładu cen względem roku budowy, standardu i lokalizacji (Matplotlib, Seaborn, Plotly).
* **Mapa Okazji:** Geolokalizacja ofert typu "Top 3" (najtańsze względem mediany w danej kategorii metrażowej) wyświetlana na interaktywnej mapie.
* **Deal Score (ML):** System oceny ofert oparty na Regresji Liniowej. Model przewiduje "sprawiedliwą" cenę nieruchomości na podstawie jej cech fizycznych i porównuje ją z ceną rynkową.
* **System Rekomendacji:** Po wybraniu konkretnej oferty, aplikacja automatycznie znajduje podobne mieszkania w innych miastach w zbliżonym budżecie.
* **Analiza Ekstremów:** Porównanie najdroższego i najtańszego miasta w Polsce.

---

## 🧠 Jak działa Deal Score?
Aplikacja wykorzystuje model `LinearRegression` z biblioteki `scikit-learn`. Proces analizy przebiega następująco:

1. **Trening:** Model uczy się "w locie" na przefiltrowanym przez użytkownika zbiorze danych, analizując relacje między zmiennymi `squareMeters`, `centreDistance`, `standardScore` i `buildYear` a ceną końcową.
2. **Predykcja:** Dla każdej oferty wyliczana jest statystyczna cena teoretyczna (`predictedPrice`).
3. **Ocena Algorytmiczna:** System porównuje cenę rzeczywistą z predykcją i nadaje odpowiednią etykietę:
   * 🔥 **OKAZJA:** Cena rzeczywista < 90% ceny przewidzianej przez model.
   * ✅ **DOBRA:** Cena rzeczywista < 95% ceny przewidzianej przez model.
   * ⚖️ **RYNKOWA:** Cena zbliżona do modelu (w przedziale +/- 5%).
   * 🚩 **DROGO:** Cena znacznie powyżej wyceny modelu.

---

## 🛠️ Technologia

* **Język:** Python
* **Obróbka danych:** Pandas, NumPy
* **Interfejs użytkownika:** Streamlit Framework
* **Uczenie maszynowe:** Scikit-learn (Linear Regression)
* **Wizualizacja danych:** Plotly Express, Matplotlib, Seaborn

---

## 📦 Uruchomienie

### 
```bash
streamlit run analiza_mieszkan.py
