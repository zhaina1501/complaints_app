import streamlit as st
import os
import time
import webbrowser
import pyautogui
from time import sleep

def send_whatsapp_message(phone, message):
    """Открывает WhatsApp Web с нужным номером и текстом сообщения"""
    url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
    webbrowser.open(url)
    time.sleep(20)  # Даем пользователю время нажать "Отправить"
    pyautogui.press('enter')

def main_page():
    phone = "+77017120164"
    message = 'HELLO TUMAR! I LOVE YOU!'
    send_whatsapp_message(phone, message)

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
