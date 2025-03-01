import streamlit as st
import pandas as pd
import os


FILE_PATH = "complaints_data.csv"  # Путь к файлу

def load_data():
    """Загружает данные из CSV, если файл существует"""
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    else:
        return pd.DataFrame(columns=["id", "complaint"])  # Пример колонок

def save_data(df):
    """Сохраняет обновленные данные в CSV"""
    df.to_csv(FILE_PATH, index=False)

def dataset_page():
    st.title("Сохраненные данные")

    # Загружаем данные
    dataset = load_data()

    if dataset.empty:
        st.warning("Нет данных для отображения!")
        return

    # Добавляем колонку с уникальными индексами для удобства выбора
    dataset.reset_index(inplace=True)  # Добавляем индекс как отдельный столбец
    dataset.rename(columns={"index": "row_id"}, inplace=True)

    # Создаём столбец с чекбоксами
    selected_rows = st.multiselect("Выберите записи для удаления:", dataset["row_id"])

    # Отображаем таблицу без индекса
    st.dataframe(dataset.drop(columns=["row_id"]))

    # Если есть выделенные строки, показываем кнопку удаления
    if selected_rows and st.button("Удалить выбранные"):
        dataset = dataset[~dataset["row_id"].isin(selected_rows)]  # Фильтруем
        dataset.drop(columns=["row_id"], inplace=True)  # Убираем вспомогательный индекс
        save_data(dataset)  # Сохраняем новый датасет
        st.success("Выбранные записи удалены!")
        st.experimental_rerun()  # Обновляем страницу

