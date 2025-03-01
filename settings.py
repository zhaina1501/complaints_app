import streamlit as st
import os

def select_folder():
    folder_selected = filedialog.askdirectory()
    return folder_selected

# Функция для сохранения настроек в файл
def save_settings_to_file(filename="settings.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        # Сохраняем первое сообщение
        file.write(f"{st.session_state.get('send_message_value_1', '')}\n---\n")
        # Сохраняем значение времени
        file.write(f"{st.session_state.get('send_time_value', 20)}\n---\n")
        # Сохраняем второе сообщение
        file.write(f"{st.session_state.get('send_message_value_2', '')}\n---\n")
        # Сохраняем ссылку на сайт списком номеров жалоб
        file.write(f"{st.session_state.get('page_url', '')}\n")


# Функция для загрузки настроек из файла
def load_settings_from_file(filename="settings.txt"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
            parts = content.split('\n---\n')  # Разделяем файл на части по маркеру

            if len(parts) >= 4:
                # Загружаем первое сообщ
                # 
                # ение
                st.session_state['send_message_value_1'] = parts[0].strip()
                
                # Загружаем значение времени и обрабатываем возможную ошибку
                try:
                    st.session_state['send_time_value'] = int(parts[1].strip())
                except ValueError:
                    st.session_state['send_time_value'] = 20  # Значение по умолчанию
                
                # Загружаем второе сообщение
                st.session_state['send_message_value_2'] = parts[2].strip()
                
                # Загружаем значение ссылки на сайт
                st.session_state['page_url'] = parts[3].strip()


def settings_page():
    st.title("Настройки сообщений")

    # Загружаем настройки при инициализации
    load_settings_from_file()

    send_message_value_1 = st.text_area(
        'Введите текст первого сообщения: :point_down:',
        st.session_state.get('send_message_value_1', 'Добрый день, NAME! Меня зовут Степан...'),
        height=150
    )

    send_time_value = st.number_input('### Задайте период времени в МИНУТАХ, по истечении которого отправляется второе сообщение: :point_down:', value=st.session_state.get('send_time_value', 20))

    send_message_value_2 = st.text_area(
        '### Введите текст второго сообщения: :point_down:',
        st.session_state.get('send_message_value_2', 'Также направляем Вам памятку...'),
        height=150
    )

    page_url = st.text_input(
        '### Введите новую ссылку на сайт жалоб, если она поменяется: :point_down:',
        st.session_state.get('page_url', 'https://goszakup.gov.kz/ru/registry/complaint')
    )
    st.file_uploader
    # Сохранение настроек в сессионное состояние и файл
    if st.button('Сохранить настройки'):
        st.session_state['send_message_value_1'] = send_message_value_1
        st.session_state['send_time_value'] = send_time_value
        st.session_state['send_message_value_2'] = send_message_value_2
        st.session_state['page_url'] = page_url
        
        # Сохранение в файл
        save_settings_to_file()
        
        st.success("Настройки сохранены.")
