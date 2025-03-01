import streamlit as st
import os
import webbrowser
from settings import settings_page
from dataset import dataset_page

def main_page():
    phone = "+77017120164"
    text = "Hello"
    url = f"https://web.whatsapp.com/send?phone={phone}&text={text}"

    st.title("Отправка WhatsApp сообщений")

    # Автоматически открываем WhatsApp Web в новом окне
    st.markdown(f"""
        <script>
            window.open("{url}", "_blank");
        </script>
    """, unsafe_allow_html=True)

    st.success("Открытие WhatsApp Web...")

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
