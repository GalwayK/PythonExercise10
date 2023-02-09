import datetime
import time
import requests
import selectorlib
import pandas
import streamlit
import sqlite3
import plotly.express as express

URL = "https://programmer100.pythonanywhere.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
CONNECTION = sqlite3.Connection("files/database.db")


def clear_temp_table():
    CONNECTION.execute("Delete from temperatures")
    return None


def get_temp_data():
    cursor = CONNECTION.cursor()
    temp_data_list = cursor.execute("SELECT * FROM temperatures")
    list_temps = []
    list_times = []
    for temp_data in temp_data_list:
        list_temps.append(temp_data[0])
        list_times.append(temp_data[1])

    return list_temps, list_times


def write_temp_data(temp_data):
    CONNECTION.execute("INSERT INTO temperatures VALUES (?, ?)", temp_data)
    CONNECTION.commit()
    return None


def get_source(url):
    source_code = requests.get(URL, headers=HEADERS)
    source_code = source_code.text
    print(source_code)
    return source_code


def get_temperature(source_code):
    selector = selectorlib.Extractor.from_yaml_file("files/extract.yaml")
    temp = selector.extract(source)["temp"]
    current_time = datetime.datetime.now().strftime("%B %d %Y %H:%M:%S")
    return {current_time: temp}


def get_temp_dict_from_file(filename):
    temp_dict = {}
    dataframe = pandas.read_csv(filename)
    for index, row in dataframe.iterrows():
        temp_dict[row["TIME"]] = row["TEMP"]
    return temp_dict


def make_streamlit_page(temp_dict):
    list_temps, list_times = get_temp_data()
    streamlit.title("Temperature plot")
    first_time = list(temp_dict.keys())[0]
    last_time = list(temp_dict.keys())[len(list(temp_dict.keys())) - 1]
    streamlit.subheader(f"Temperature between {first_time} and {last_time}")
    plotly_figure = express.line(y=list_temps, x=list_times, labels={"x": "Time", "y": "Temperature"})
    streamlit.plotly_chart(plotly_figure)


if __name__ == "__main__":
    clear_temp_table()
    with open("files/temps.txt", "w") as temperature_file:
        temperature_file.write("TIME,TEMP\n")
    for i in range(10):
        source = get_source(URL)
        temperature_dict = get_temperature(source)

        for key, value in temperature_dict.items():
            with open("files/temps.txt", "a") as temperature_file:
                temperature_file.write(f"{key},{value}\n")
                write_temp_data((value, key))
        time.sleep(1)

    temps = get_temp_dict_from_file("files/temps.txt")
    make_streamlit_page(temps)

