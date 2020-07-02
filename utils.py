from bs4 import BeautifulSoup
import requests
from time import strptime, strftime, sleep
import threading


def current_relation(rel, excluded_category):
    rel = str(rel)

    # relations = ["Adaptation:",
    #              "Alternative setting:",
    #              "Prequel:",
    #              "Sequel:",
    #              "Other:",
    #              "Alternative version:",
    #              "Summary:",
    #              "Side story:",
    #              "Full story:",
    #              "Character:"
    #              ]

    if rel not in excluded_category:
        return rel

    return "No valid category"


def is_valid_type(ele, types):
    for i in types:
        if ele.find(f"/{i}/") > -1:
            return True
    return False

def is_valid_name(ele, excluded_text, included_text):


    for excluded in excluded_text:
        if excluded.lower() in ele.lower():
            return False

    for included in included_text:
        if included.lower() not in ele.lower():
            return False

    return True


def get_name(soup):
    return soup.title.string.replace(" - MyAnimeList.net", "").strip()

def get_base_anime(url, category):
    if url.find("?q=") != -1:
        return url[:url.find("?q=")]

    url = url.strip().lower().replace(" ", "%20").replace("_", "%20")

    if url.find("myanimelist.net") != -1:
        return url
    else:
        url = f"https://myanimelist.net/search/all?q={url}"
        html = requests.get(url).text  # TODO anime can be only the name
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2", id=category)
        return element.next_sibling.next_sibling.find("a")['href']

def parse_inc_exc(list):
    new_excluded = []
    for excluded in list:
        if excluded != "":
            new_excluded.append(excluded.replace(" ", "_").strip())
    return new_excluded

def parse_date(date):
    try:
        parsed_date = date

        if "to" in parsed_date:
            parsed_date = parsed_date[:parsed_date.find("to")]

        if "Not available" in parsed_date:
            return "Not available"

        length = len(parsed_date.split())
        parsed_date = " ".join(parsed_date.split())
        if length == 3:
            parsed_date = strptime(parsed_date, "%b %d, %Y")
            parsed_date = strftime("%Y/%m/%d", parsed_date)
        elif length == 2:
            if "," in parsed_date:
                parsed_date = strptime(parsed_date, "%b, %Y")
            else:
                parsed_date = strptime(parsed_date, "%b %Y")

            parsed_date = strftime("%Y/%m", parsed_date) + "/??"
        elif length == 1:
            parsed_date = strptime(parsed_date, "%Y")
            parsed_date = strftime("%Y", parsed_date) + "/??/??"
        else:
            return "The date format is not valid"

        return parsed_date

    except:
        return "Could not find the date"


def get_date(soup):
    content = soup.find_all("div", style='width: 225px')

    for all_info in content:
        if all_info.text == "Aired:" or all_info.text == "Published:":
            return parse_date(all_info.next_sibling.string.strip())
        for info in all_info.find_all("span", class_="dark_text"):

            if info.text == "Aired:" or info.text == "Published:":
                return parse_date(info.next_sibling.string.strip())

def check_dates(animes):

    for anime in animes:
        if anime.date == "":
            html = requests.get(anime.url).text
            soup = BeautifulSoup(html, "html.parser")
            anime.date = get_date(soup)

def check_names(animes):

    for anime in animes:
        if anime.name == "":
            html = requests.get(anime.url).text
            soup = BeautifulSoup(html, "html.parser")
            anime.name = get_name(soup)




def get_relateds(anime, hrefs, visited, excluded_category, excluded_text, included_text, types):

    anime = Anime(anime)

    html = requests.get(anime.url).text
    soup = BeautifulSoup(html, "html.parser")

    content = soup.find("table", class_="anime_detail_related_anime")


    if anime not in visited and is_valid_type(str(anime.url), types):
        visited.append(anime)
        visited[-1].set_params(soup)

    if anime not in hrefs and is_valid_type(str(anime.url), types):
        hrefs.append(anime)

    i = 0
    for col in content.find_all('td'):
        if i % 2 == 0:
            relation = current_relation(col, excluded_category)
        i += 1
        for element in col.find_all('a'):
            if relation != "No valid category":
                href = "https://myanimelist.net" + element['href']
                if is_valid_type(href, types) and is_valid_name(href, excluded_text, included_text) and Anime(href) not in hrefs:
                    print(href + "added")
                    hrefs.append(Anime(href))



class Anime:
    def __init__(self, url):
        self.url = url
        self.list = []
        self.name = ""
        self.date = ""

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return self.url == other

    def set_params(self, soup):
        self.name = get_name(soup)
        self.date = get_date(soup)



class Threads:
    def __init__(self, func, href, hrefs, visited, excluded_category, excluded_text, included_text, types):

        self.list = []
        for url in hrefs:
            if url not in visited:
                self.list.append(url.url)

        am = len(self.list)

        self.threads = [threading.Thread(target=func, args=(self.list[i], hrefs, visited, excluded_category, excluded_text, included_text, types))
                        for i in range(am)]

    def start(self):
        for thread in self.threads:
            thread.start()

    def join(self):
        for thread in self.threads:
            thread.join()
