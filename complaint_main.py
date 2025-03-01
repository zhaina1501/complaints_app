import streamlit as st
import os
import webbrowser
from settings import settings_page
from dataset import dataset_page

def main_page():

    url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
    webbrowser.open(url)
    st.success("Сообщение отправлено на номер")

def main():
    st.sidebar.title("Меню")
    page = st.sidebar.radio("Перейти на:", ["Главная", "Настройки", "База клиентов"])

    if page == "Главная":
        main_page()
    elif page == "Настройки":
        settings_page()     
    elif page == "База клиентов":
        dataset_page()

if __name__ == "__main__":
    main()
