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

# надо скачать по версии chrome chromedriver по ссылке https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
def extract_complaint_info(complaint_url):
    try:
        response = requests.get(complaint_url, timeout=10)
        response.raise_for_status()  # Проверка успешности запроса
        soup = BeautifulSoup(response.content, 'html.parser')

        # Извлекаем телефон по метке "Контактный телефон"
        phone_label = soup.find('div', string=re.compile(r'Контактный телефон', re.I))
        phone = phone_label.find_next('input')['value'] if phone_label else "NULL"
        phone = phone.split(',')[0]
        cleaned_phone = re.sub(r'\D', '', phone)  
        
        
        if cleaned_phone.startswith('8'):
            cleaned_phone = '+7' + cleaned_phone[1:]
        elif cleaned_phone.startswith('7'):
            cleaned_phone = '+7' + cleaned_phone[1:]
        else:
            cleaned_phone = '+7' + cleaned_phone
        fio_label = soup.find('div', string=re.compile(r'ФИО представителя поставщика', re.I))
        fio = fio_label.find_next('input')['value'] if fio_label else "NULL"

        
        email_label = soup.find('div', string=re.compile(r'E-mail', re.I))
        email = email_label.find_next('input')['value'] if email_label else "NULL"

        return cleaned_phone, fio, email

    except requests.exceptions.RequestException as e:
        # Если возникла ошибка запроса, возвращаем значения по умолчанию и выводим сообщение об ошибке
        print(f"Ошибка при доступе к {complaint_url}: {e}")
        return "NULL", "NULL", "NULL"

# Функция для сбора данных с нескольких страниц
def scrape_complaint_numbers(base_url, start_range, end_range):
    all_complaints = []

    # Обходим жалобы в заданном диапазоне
    for complaint_number in range(start_range, end_range + 1):
        complaint_url = f"{base_url}/reestrcomplaint/preview/{complaint_number}"
        print(f"Извлечение данных с {complaint_url}")
        fio, phone, email = extract_complaint_info(complaint_url)

        # Добавляем данные в список
        all_complaints.append([complaint_number, fio, phone, email, False, "", False, ""])

    return all_complaints

def save_to_csv(data, filename="complaints_data.csv"):
    # Если файл уже существует, загружаем существующие данные
    if os.path.exists(filename):
        df_existing = pd.read_csv(filename)
        existing_numbers = df_existing['Номер жалобы'].tolist()
    else:
        existing_numbers = []

    #filtered_data = [entry for entry in data if entry[1].strip() and entry[3].strip()]
    # Добавляем только те записи, номера жалоб которых еще не сохранены
    new_data = [entry for entry in data if entry[0] not in existing_numbers]

    if new_data:
        df_new = pd.DataFrame(new_data, columns=["Номер жалобы", "Телефон", "ФИО", "Email", "Whatsapp_Sent", "Whatsapp_Sent_Date", "Email_Sent", "Email_Sent_Date"])
        df_new.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False, encoding='utf-8-sig')
        print(f"Данные добавлены в {filename}")
    else:
        print("Нет новых данных для добавления.")

# Функция для чтения данных из CSV по диапазону
def load_from_csv_by_range(start_value, end_value, csv_filename='complaints_data.csv'):
    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename)
        df = df.dropna(subset=['Телефон', 'Email'])
        # Фильтрация по диапазону номеров жалоб
        filtered_df = df[(df['Номер жалобы'] >= start_value) & (df['Номер жалобы'] <= end_value)]

        if not filtered_df.empty:
            return filtered_df
        else:
            st.write("Нет данных для отображения в данном диапазоне.")
    else:
        st.error(f"Файл {csv_filename} не найден.")
        return pd.DataFrame()  # Пустой DataFrame
    
def send_whatsapp_message(phone, message):
    """Открывает WhatsApp Web с нужным номером и текстом сообщения"""
    url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
    webbrowser.open(url)
    time.sleep(20)  # Даем пользователю время нажать "Отправить"
    pyautogui.press('enter')
    
def whatsapp_send():
    # File paths
    csv_file = "complaints_data_test.csv"
    settings_file = "settings.txt"
    df = pd.read_csv(csv_file, encoding="utf-8", dtype={"Телефон": str})

    with open(settings_file, "r", encoding="utf-8") as file:
        lines = file.read().split("---")
        message_template = lines[0].strip()

    existing_sent_status = (
        df[df["Whatsapp_Sent"].astype(str).str.lower() == "true"] 
        .groupby("Телефон")["Whatsapp_Sent_Date"]
        .first()
        .to_dict()
    )
    
        # Обработка каждой строки
    for idx, complaint in df.iterrows():
        phone = str(complaint["Телефон"]).strip()  # Убедиться, что телефон в строковом формате
        name = (
            complaint["ФИО"].split()[1]
            if isinstance(complaint["ФИО"], str) and len(complaint["ФИО"].split()) > 1
            else "Уважаемый клиент"
        )
        whatsapp_sent = str(complaint["Whatsapp_Sent"]).strip().lower()

        # Check if the phone number has already been marked as sent
        if phone in existing_sent_status:
            # Assign True and the existing timestamp to all rows with this phone number
            df.loc[df["Телефон"] == phone, "Whatsapp_Sent"] = "True"
            df.loc[df["Телефон"] == phone, "Whatsapp_Sent_Date"] = existing_sent_status[phone]
            st.success(f'Номер {phone} {name} уже был в базе данных и сообщение было отправлено ранее!')
            continue

        # Пропустить, если сообщение уже отправлено или номер отсутствует
        if whatsapp_sent == "true" or not phone or phone.lower() == "null":
            continue

        # Персонализировать сообщение
        personalized_message = message_template.replace("NAME", name)

        try:
            # Отправить сообщение
            # pywhatkit.sendwhatmsg_instantly(phone, personalized_message, wait_time=30, tab_close=True)
            # time.sleep(30)
            send_whatsapp_message(phone,personalized_message)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing_sent_status[phone] = timestamp
            # Update all rows with this phone number
            df.loc[df["Телефон"] == phone, "Whatsapp_Sent"] = "True"
            df.loc[df["Телефон"] == phone, "Whatsapp_Sent_Date"] = timestamp

            st.success(f"Сообщение отправлено на номер {phone} ({name}).")
        except Exception as e:
            st.error(f"Не получилось отправить сообщение на номер {phone} ({name}): {e}")

    # Сохранить обновленный CSV
    df.to_csv(csv_file, index=False, encoding="utf-8")
    st.success("Сообщения отправлены, и CSV файл обновлен.")

def check_website_status(url):
    """Проверяет доступность сайта"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False

# 🛠 Инициализация session_state для хранения данных
if "start_value" not in st.session_state:
    st.session_state.start_value = 0

if "end_value" not in st.session_state:
    st.session_state.end_value = 100

if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = pd.DataFrame()

def main_page():
    whatsapp_send()
    # numbers = ["+77017120164", "+77017120164"]
    # number1 = "+77017120164"
    # text = 'HELLO TUMAR! I LOVE YOU!'
    # send_whatsapp_message(number1, text)
    base_url = "https://goszakup.gov.kz/ru/complaint/"
    st.title("Сбор данных по жалобам")
    st.markdown('[Посетите сайт госзакупок для ознакомления с диапозоном](https://goszakup.gov.kz/ru/registry/complaint)')
    #st.markdown("### Выберите диапазон согласно номерам жалоб :point_down:")
    st.header("Выберите диапазон согласно номерам жалоб :point_down:")

    # Ввод чисел "От" и "До"
    st.session_state.start_value = st.number_input('Введите значение "От":', value=st.session_state.start_value)
    st.session_state.end_value = st.number_input('Введите значение "До":', value=st.session_state.start_value)

    # Кнопка для подтверждения выбора
    if st.button('Выбрать'):
            # Проверяем доступность сайта
        if not check_website_status(base_url):
            st.error("Ошибка: Сайт гос закупок не доступен! Попробуйте позже.")
        else:
        # Проверяем, чтобы "До" было больше или равно "От"
            if st.session_state.start_value > st.session_state.end_value:
                st.error('Ошибка: Значение "До" должно быть больше или равно значению "От".')
            else:
                st.success(f"Вы выбрали диапазон: от {st.session_state.start_value} до {st.session_state.end_value}")
                complaints_data = scrape_complaint_numbers(base_url, st.session_state.start_value, st.session_state.end_value)
                if complaints_data:
                    save_to_csv(complaints_data)
                    st.success(f"Данные сохранены в файл.")
                st.session_state.filtered_data = load_from_csv_by_range(st.session_state.start_value, st.session_state.end_value)
                if not st.session_state.filtered_data.empty:
                    st.write("Собранные данные:")
                    st.dataframe(st.session_state.filtered_data) 
                    whatsapp_send()
                else:
                    st.write("Данные не найдены в указанном диапазоне.")

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
