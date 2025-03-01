import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
#import pywhatkit
from datetime import datetime
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from settings import settings_page
from dataset import dataset_page
import time
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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
