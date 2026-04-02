import streamlit as st
import requests
import csv
import time
from io import StringIO

st.title("📱 App Store Review Parser")

st.write("Сбор отзывов из App Store по APP ID")

app_id = st.text_input("Введите APP ID", value="570060128")

if st.button("Собрать отзывы"):
    BASE_URL = "https://itunes.apple.com/ru/rss/customerreviews/id={}/sortBy=mostRecent/page={}/json"
    
    all_reviews = []
    page = 1
    progress = st.progress(0)
    status = st.empty()
    
    while True:
        status.text(f"Загружаю страницу {page}...")
        
        url = BASE_URL.format(app_id, page)
        response = requests.get(url)
        
        if response.status_code != 200:
            st.error("Ошибка запроса")
            break
        
        data = response.json()
        
        if "feed" not in data or "entry" not in data["feed"]:
            break
        
        entries = data["feed"]["entry"]
        
        if page == 1:
            entries = entries[1:]
        
        if not entries:
            break
        
        for entry in entries:
            review = {
                "review_id": entry.get("id", {}).get("label"),
                "author": entry.get("author", {}).get("name", {}).get("label"),
                "title": entry.get("title", {}).get("label"),
                "text": entry.get("content", {}).get("label"),
                "rating": entry.get("im:rating", {}).get("label"),
                "version": entry.get("im:version", {}).get("label"),
                "date": entry.get("updated", {}).get("label"),
            }
            all_reviews.append(review)
        
        page += 1
        progress.progress(min(page / 10, 1.0))  # просто визуальный прогресс
        time.sleep(0.3)
    
    st.success(f"Собрано отзывов: {len(all_reviews)}")
    
    # Создаём CSV в памяти
    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    
    writer.writerow([
        "review_id",
        "author",
        "title",
        "text",
        "rating",
        "version",
        "date"
    ])
    
    for r in all_reviews:
        writer.writerow([
            r["review_id"],
            r["author"],
            r["title"],
            r["text"],
            r["rating"],
            r["version"],
            r["date"]
        ])
    
    csv_data = output.getvalue()
    
    st.download_button(
        label="📥 Скачать CSV",
        data=csv_data,
        file_name=f"app_{app_id}_reviews.csv",
        mime="text/csv"
    )
