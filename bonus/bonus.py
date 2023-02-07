import datetime
import time
import requests
import selectorlib
import pandas
import streamlit
import plotly.express as express

URL = "https://programmer100.pythonanywhere.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


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
    streamlit.title("Temperature plot")
    first_time = list(temp_dict.keys())[0]
    last_time = list(temp_dict.keys())[len(list(temp_dict.keys())) - 1]
    streamlit.subheader(f"Temperature between {first_time} and {last_time}")
    plotly_figure = express.line(y=temp_dict.values(), x=temp_dict.keys(), labels={"x": "Temperature", "y": "Time"})
    streamlit.plotly_chart(plotly_figure)


if __name__ == "__main__":
    with open("files/temps.txt", "w") as temperature_file:
        temperature_file.write("TIME,TEMP\n")
    for i in range(10):
        source = get_source(URL)
        temperature_dict = get_temperature(source)

        for key, value in temperature_dict.items():
            with open("files/temps.txt", "a") as temperature_file:
                temperature_file.write(f"{key},{value}\n")
        time.sleep(1)

    temps = get_temp_dict_from_file("files/temps.txt")
    make_streamlit_page(temps)

