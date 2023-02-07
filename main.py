import datetime

import requests
import re
import selectorlib
import os
import smtplib
import email.message as message

USERNAME = "kyligalway@gmail.com"
PASSWORD = os.getenv("PASSWORD")
URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1'}


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
    source = scape_data(URL)
    print(source)
    tour_text = extract(source)
    print(tour_text)
    # tour_text = get_tour_text(source)
    tours = []
    if tour_text != "No upcoming tours":
        with open("files/tours.txt", "r") as tour_file:
            for tour_line in tour_file:
                tours.append(tour_line.strip("\n"))

        if tour_text not in tours:
            with open("files/tours.txt", "a") as tour_file:
                tour_file.write(f"{tour_text}\n")

            print("Sending information.")
            send_email(tour_text.split(","))

        else:
            print("Tour notification already sent.")
    else:
        print("No info to send.")
