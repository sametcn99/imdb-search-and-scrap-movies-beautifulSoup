import sys
import textwrap
import pyshorteners
import requests
import os
from bs4 import BeautifulSoup
from pyshorteners.exceptions import ShorteningErrorException

line_separator = "/////////////////////////////"
u_input: str = ""
try:
    while True:
        name = []
        link = []
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
        print("movie title: ")
        # Collect and parse search page
        response = requests.get('https://www.imdb.com/find?q=' + input().replace(" ", "+"))
        soup = BeautifulSoup(response.text, 'lxml')
        for detail in soup.find_all('td', attrs={"class": "result_text"}):
            imdb_link = detail.a.get("href")
            full_link = "https://www.imdb.com/" + imdb_link
            # for print only movie pages
            if full_link.__contains__("//title"):
                link.append(full_link)
                name.append(detail.get_text())
        for i in range(len(name)):
            print(i + 1, link[i], name[i])
        # Collect and parse movie page
        print("0 for search again\ncode: ")
        u_input = input()
        if u_input == "0":
            os.system("python main.py")
        responseDetails = requests.get(link[int(u_input) - 1])
        soup = BeautifulSoup(responseDetails.content, 'lxml')
        # pull movie details
        try:
            s_name = soup.find('h1', attrs={"data-testid": "hero-title-block__title"}).text
        except:
            print("Name is missing...")
        try:
            s_year = soup.find('a', attrs={
                "class": "ipc-link ipc-link--baseAlt ipc-link--inherit-color TitleBlockMetaData__StyledTextLink-sc-12ein40-1 rgaOW"}).text
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
            responseWriters = requests.get(responseDetails.url + "fullcredits")
            soupWriters = BeautifulSoup(responseWriters.text, 'lxml')
            writers = soupWriters.find_all(attrs={"class": "simpleTable simpleCreditsTable"})
            writersCheck = []
            writersCheck = soupWriters.find_all(id="writer")
            if len(writersCheck) > 0:
                writers = writers[1].text.replace(" ", "").replace("...", "").replace("\n", "")
                # print("writers is not none" + str(writersCheck))
            if len(writersCheck) < 1:
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
                "class": "ipc-media ipc-media--poster ipc-image-media-ratio--poster ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img"}).img[
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
        movie_details = line_separator + "\n🔑 Title: " + s_name + f" ({s_year}) {s_runtime}" + \
                        "\n" + "⭐ Rate: " + s_rate + \
                        "\n" + "🎥 Director: " + s_director + \
                        "\n" + textwrap.fill(
            textwrap.shorten("✏ Writers: " + ''.join(str(e) for e in writers), width=110,
                             placeholder=" Too many writers..."),
            width=70) + \
                        "\n" + textwrap.fill("🕶 Cast: " + ''.join(str(e) + ", " for e in cast), width=70) + \
                        "\n" + textwrap.fill("📚 Summary: " + s_summary, width=70) + \
                        "\n" + textwrap.fill("📚 Storyline: " + s_line, width=70) + \
                        "\n" + "📷 Movie Poster: " + shortened_poster_link + \
                        "\n" + "🔗 IMDb Link: " + responseDetails.url + "\n" + line_separator
        print(movie_details)
except Exception as e:
    print(f"An error occured. \nHere is Error message: {e}\nRestarted program.")
    os.system("python main.py")
