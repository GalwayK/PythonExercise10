import datetime
import time
import requests
import re
import selectorlib
import os
import smtplib
import sqlite3
import email.message as message

USERNAME = "kyligalway@gmail.com"
PASSWORD = os.getenv("PASSWORD")
URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1'}
FILEPATH = "files/database.db"
CONNECTION = sqlite3.connect(FILEPATH)


def read_data_list():
    tuple_bands = CONNECTION.execute("SELECT * FROM events")
    list_bands = list(tuple_bands)
    return list_bands


def write_data(event_list):
    cursor = CONNECTION.cursor()
    cursor.execute("INSERT INTO events VALUES (?, ?, ?)", event_list)
    CONNECTION.commit()
    print("Successfully commit.")
    return None

def scape_data(url):
    """
    Scrape the webpage source from the URL.
    :return:
    """
    response = requests.get(url, headers=HEADERS)
    page_source_text = response.text
    return page_source_text


def get_tour_text(source_code):
    pattern = re.compile('<h1 align="right " id="displaytimer">.*</h1>')
    matches = re.findall(pattern, source_code)[0].strip('<h1 align="right " id="displaytimer">').strip('</h1>')
    return matches


def extract(source_code):
    """
    Note, this is an alternative method of scraping the tour information
    :return:
    """
    extractor = selectorlib.Extractor.from_yaml_file("files/extract.yaml")
    value = extractor.extract(source_code)["tours"]
    return value


def send_email(tour_info):
    email = message.EmailMessage()
    email["Subject"] = "There is an upcoming tour!"
    content = f"""Upcoming Tour!
Band: {tour_info[0]}
Location: {tour_info[1]}
Date: {datetime.datetime.strptime(tour_info[2], "%d.%m.%Y").strftime("%B %d, %Y")}
Have fun!
    """
    email.set_content(content)

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(USERNAME, PASSWORD)
    gmail.sendmail(USERNAME, USERNAME, email.as_string())
    gmail.quit()


if __name__ == "__main__":
    while True:
        source = scape_data(URL)
        tour_text = extract(source)
        # tour_text = get_tour_text(source)
        tours = []
        if tour_text != "No upcoming tours":
            print(f"Tour found: {tour_text}")
            tour_list = tuple(tour_text.split(","))
            tour_data_list = read_data_list()

            with open("files/tours.txt", "r") as tour_file:
                for tour_line in tour_file:
                    tours.append(tour_line.strip("\n"))

            if tour_text not in tours:
                with open("files/tours.txt", "a") as tour_file:
                    tour_file.write(f"{tour_text}\n")

                print(f"Sending information on tour.")
                send_email(tour_list)
            else:
                print("Tour notification already sent.")

            if tour_list not in tour_data_list:
                write_data(tour_list)
            else:
                print("Tour already recorded in database.")


        else:
            print("No info to send.")
        time.sleep(2)
