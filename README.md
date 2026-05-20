# 🏠 Analiza cen mieszkań

---

## 📊 O Projekcie
Interaktywna aplikacja webowa zbudowana w frameworku **Streamlit**, służąca do analizy rynku mieszkań w Polsce (na podstawie danych z czerwca 2024). Projekt łączy wizualizację danych z modelem uczenia maszynowego, aby pomagać użytkownikom w precyzyjnej identyfikacji okazji rynkowych.

---

## 🚀 Kluczowe Funkcje

* **Interaktywne Filtrowanie:** Przeszukiwanie ofert według miast, ceny, metrażu, roku budowy, odległości od centrum oraz udogodnień (winda, balkon, parking itp.).
* **Wizualizacja Statystyczna:** Wykresy rozkładu cen względem roku budowy, standardu i lokalizacji. 
* **Mapa Okazji:** Geolokalizacja okazji cenowych względem metrażu, wyświetlana na interaktywnej mapie.
* **Deal Score (ML):** System oceny ofert oparty na Regresji Liniowej. Model przewiduje "sprawiedliwą" cenę mieszkań na podstawie jej cech i porównuje ją z ceną rynkową.
* **System Rekomendacji:** Po wybraniu konkretnej oferty, aplikacja automatycznie znajduje podobne mieszkania w innych miastach w zbliżonym budżecie.
* **Analiza Ekstremów:** Porównanie najdroższego i najtańszego miasta w Polsce.

---
## 🛠️ Technologia

* **Język:** Python
* **Obróbka danych:** Pandas
* **Interfejs użytkownika:** Streamlit Framework
* **Uczenie maszynowe:** Scikit-learn (Linear Regression)
* **Wizualizacja danych:** Plotly Express, Matplotlib, Seaborn

---

## 📦 Uruchomienie

### 
```bash
streamlit run analiza_mieszkan.py
