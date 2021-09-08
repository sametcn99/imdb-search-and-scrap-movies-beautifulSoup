import os
import sys
import textwrap
import traceback

import pyshorteners
import requests
from bs4 import BeautifulSoup
from pyshorteners.exceptions import ShorteningErrorException

line_separator = "/////////////////////////////"
u_input: str = ""


def search():
    global link
    name = []
    link = []
    print("movie title: ")
    # Collect and parse search page
    response = requests.get('https://www.imdb.com/find?q=' + input().replace(" ", "+"))
    soup = BeautifulSoup(response.text, 'lxml')
    for detail in soup.find_all('td', attrs={"class": "result_text"}):
        imdb_link = detail.a.get("href")
        full_link = 'https://www.imdb.com/' + imdb_link
        # for print only movie pages
        if full_link.__contains__("//title"):
            link.append(full_link)
            name.append(detail.get_text())
    for i in range(len(name)):
        print(i + 1, link[i], name[i])
    print("0 for search again\ncode: ")
    u_input = input()
    if u_input == "0":
        os.system("python main.py")
    # link_s.append(link[int(u_input) - 1])
    link = link[int(u_input) - 1]


def collect_details():
    cast = ["NA"]
    s_name = "NA"
    s_year = "NA"
    s_rate = "NA"
    s_director = "NA"
    s_summary = "NA"
    s_line = "NA"
    s_poster = "NA"
    s_runtime = "NA"
    shortened_poster_link = "NA"
    writers = []
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'lxml', )
    response_details_url = response.url
    # pull movie details
    try:
        s_name = soup.find('h1', attrs={"data-testid": "hero-title-block__title"}).text
    except:
        print("Name is missing...")
    try:
        s_year = soup.find('a', attrs={
            "class": "ipc-link ipc-link--baseAlt ipc-link--inherit-color "
                     "TitleBlockMetaData__StyledTextLink-sc-12ein40-1 rgaOW"}).text
    except:
        print("Year is missing...")
    try:
        s_rate = soup.find('span', attrs={"class": "AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV"}).text
    except:
        print("Rate is missing...")
    try:
        s_director = soup.find('a', attrs={
            "class": "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}).text
    except:
        print("Director is missing...")
    try:
        response_writers = requests.get(response.url + "fullcredits")
        soup_writers = BeautifulSoup(response_writers.text, 'lxml')
        writers = soup_writers.find_all(attrs={"class": "simpleTable simpleCreditsTable"})
        writers_check = []
        writers_check = soup_writers.find_all(id="writer")
        if len(writers_check) > 0:
            writers = writers[1].text.replace(" ", "").replace("...", "").replace("\n", "")
            # print("writers is not none" + str(writers_check))
        if len(writers_check) < 1:
            writers = "NA"
            print("writers is missing...")
    except:
        pass
    try:
        s_summary = soup.find('span',
                              attrs={"class": "GenresAndPlot__TextContainerBreakpointXL-cum89p-2 gCtawA"}).text
        if s_summary == "":
            s_summary = "NA"
            print("Summary is missing...")
    except:
        print("Summary is missing...")
    try:
        s_line = soup.find('div',
                           attrs={"class": "ipc-html-content ipc-html-content--base"}).text
    except:
        print("Storyline is missing...")
    try:
        cast_element = soup.find_all('a', attrs={"class": "StyledComponents__ActorName-y9ygcu-1 eyqFnv"})
        if len(cast_element) > 0:
            cast = []
        for i in cast_element:
            cast.append(i.get_text())
    except:
        print("Cast is missing...")
    try:
        s_poster = soup.find('div', attrs={
            "class": "ipc-media ipc-media--poster ipc-image-media-ratio--poster ipc-media--baseAlt "
                     "ipc-media--poster-l ipc-poster__poster-image ipc-media__img"}).img[
            'src']
    except:
        print("Poster is missing...")
    if s_poster != "NA":
        try:
            shorten_poster_link = pyshorteners.Shortener()
            shortened_poster_link = shorten_poster_link.tinyurl.short(s_poster)
        except ShorteningErrorException:
            print("An error occurred while shortening the url")
            shortened_poster_link = s_poster
    element_year_rate_runtime_ul = soup.select(
        "div[class='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-2 hWHMKr'] > ul")
    if len(element_year_rate_runtime_ul) > 0:
        list_items = element_year_rate_runtime_ul[0].find_all("li", recursive=False)
        list_item_length = len(list_items)
        s_runtime = list_items[list_item_length - 1]
        s_runtime = s_runtime.text
    return s_name, s_year, s_runtime, s_rate, s_director, writers, cast, s_summary, s_line, shortened_poster_link, response_details_url, writers_check


def print_details():
    s_name, s_year, s_runtime, s_rate, s_director, writers, cast, s_summary, s_line, shortened_poster_link, response_details_url, writersCheck = collect_details()
    movie_details = line_separator + "\n🔑 Title: " + s_name + f" ({s_year}) {s_runtime}" + \
                    "\n⭐ Rate: " + s_rate + \
                    "\n🎥 Director: " + s_director + \
                    textwrap.fill(
                        textwrap.shorten("\n✏ Writers: " + ''.join(str(e) for e in writers), width=110,
                                         placeholder=" Too many writers..."),
                        width=70) + \
                    textwrap.fill("\n🕶 Cast: " + ''.join(str(e) + ", " for e in cast), width=70) + \
                    textwrap.fill("\n📚 Summary: " + s_summary, width=70) + \
                    textwrap.fill("\n📚 Storyline: " + s_line, width=70) + \
                    "\n📷 Movie Poster: " + shortened_poster_link + \
                    "\n🔗 IMDb Link: " + response_details_url + "\n" + line_separator
    print(movie_details)


if __name__ == "__main__":
    try:
        while True:
            search()
            collect_details()
            print_details()
    except ValueError as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(traceback.format_tb(exc_traceback)))
        print(f"An error occured. \nHere is Error message: {e}\nRestarted program.\n")
        os.system("python test.py")
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(traceback.format_tb(exc_traceback)))
        print(f"Something happened.\n{e}\nRestarted program.")
        os.system("python test.py")
