import streamlit as st
import requests
import time
import pandas as pd
from io import BytesIO

st.title("📱 App Store Review Parser")

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
            all_reviews.append({
                "review_id": entry.get("id", {}).get("label"),
                "author": entry.get("author", {}).get("name", {}).get("label"),
                "title": entry.get("title", {}).get("label"),
                "text": entry.get("content", {}).get("label"),
                "rating": entry.get("im:rating", {}).get("label"),
                "version": entry.get("im:version", {}).get("label"),
                "date": entry.get("updated", {}).get("label"),
            })
        
        page += 1
        progress.progress(min(page / 10, 1.0))
        time.sleep(0.3)
    
    st.success(f"Собрано отзывов: {len(all_reviews)}")
    
    # 📊 DataFrame
    df = pd.DataFrame(all_reviews)
    
    # 💾 Excel в памяти
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reviews')
    
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Скачать Excel",
        data=excel_data,
        file_name=f"app_{app_id}_reviews.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
