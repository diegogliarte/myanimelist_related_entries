from bs4 import BeautifulSoup
import requests
from time import strptime, strftime
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

    # Cheks that the relation is not excluded
    if rel not in excluded_category:
        return rel

    return "No valid category"


def is_valid_type(ele, types):
    # Checks that the element is of the specified type (anime or manga)
    for i in types:
        if ele.find(f"/{i.lower()}/") > -1:
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


def get_base_anime(url, category):
    if url.find("?q=") != -1:
        return url[:url.find("?q=")]

    url = url.strip().lower().replace(" ", "%20").replace("_", "%20")

    if url.find("myanimelist.net") != -1:
        return url
    else:
        url = f"https://myanimelist.net/search/all?q={url}"

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2", id=category)
        return element.next_sibling.next_sibling.find("a")['href']


def scrape_name(soup):
    return soup.title.string.replace(" - MyAnimeList.net", "").strip()


def scrape_date(soup):
    content = soup.find_all("div", style='width: 225px')

    for all_info in content:
        if all_info.text == "Aired:" or all_info.text == "Published:":
            return parse_date(all_info.next_sibling.string.strip())
        for info in all_info.find_all("span", class_="dark_text"):

            if info.text == "Aired:" or info.text == "Published:":
                return parse_date(info.next_sibling.string.strip())


def scrape_episodes(soup):
    content = soup.find_all("div", style='width: 225px')

    for all_info in content:
        if all_info.text == "Episodes:" or all_info.text == "Chapters:":
            return all_info.next_sibling.string.strip()

        for info in all_info.find_all("span", class_="dark_text"):
            if info.text == "Episodes:" or info.text == "Chapters:":
                return info.next_sibling.string.strip()


def scrape_score(soup):
    content = soup.find_all("span", class_="score-label")
    return content[0].text  # Content is an array with a single element, dunno why they did it like this


def scrape_average_duration(soup):
    content = soup.find_all("span", class_="dark_text")

    for info in content:
        if info.text == "Duration:":
            return info.next_sibling.string.strip()


def check_dates(animes):
    for anime in animes:

        if anime.date == "":
            try:
                html = requests.get(anime.url).text
                soup = BeautifulSoup(html, "html.parser")
                anime.date = scrape_date(soup)
            except:
                anime.date = "Could not find the date"


def check_names(animes):
    for anime in animes:
        if anime.name == "":
            try:
                html = requests.get(anime.url).text
                soup = BeautifulSoup(html, "html.parser")
                anime.name = scrape_name(soup)
            except:
                anime.name = "Could not find the name"


def check_episodes(animes):
    for anime in animes:
        if anime.episodes == "":
            try:
                html = requests.get(anime.url).text
                soup = BeautifulSoup(html, "html.parser")
                anime.episodes = scrape_episodes(soup)
            except:
                anime.episodes = "Could not find the episodes count"


def check_average_duration(animes):
    for anime in animes:
        if anime.average_duration == "":
            try:
                html = requests.get(anime.url).text
                soup = BeautifulSoup(html, "html.parser")
                anime.average_duration = scrape_average_duration(soup)
            except:
                anime.average_duration = "Could not find the average duration per episode"


def get_relateds(anime, hrefs, visited, excluded_category, excluded_text, included_text, types):
    # Requests the page for the anime (this 3 lines are the most time expensive lines by far, can't optimize much more)
    html = requests.get(anime).text
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("table", class_="anime_detail_related_anime")

    # Since we've made sure that it's not a visited anime, we can append the anime without checking
    visited.append(Anime(anime))
    print(anime, "was added")
    visited[-1].set_params(soup)  # Sets the parameters, since I could not do it in the __init__ method

    i = 0
    for col in content.find_all('td'):
        # Every 2 cols there's a relation that we can use to filter with the excluded_category var
        if i % 2 == 0:
            relation = current_relation(col, excluded_category)
        i += 1
        for element in col.find_all('a'):
            if relation != "No valid category":
                href = "https://myanimelist.net" + element['href']
                # Appends hrefs that are:
                # 1. Valid types (manga, anime or both)
                # 2. Valid names: not in excluded names and in included names
                # 3. Not in hrefs, meaning that we don't repeat
                if is_valid_type(href, types) and is_valid_name(href, excluded_text,
                                                                included_text) and href not in hrefs:
                    hrefs.append(href)


class Anime:
    # TODO Can extend this Anime class to include things like score, members...
    def __init__(self, url):
        self.url = url
        self.list = []
        self.name = ""
        self.date = ""
        self.score = ""
        self.episodes = ""
        self.average_duration = ""

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return self.url == other

    def set_params(self, soup):
        self.name = scrape_name(soup)
        self.date = scrape_date(soup)
        self.score = scrape_score(soup)
        self.episodes = scrape_episodes(soup)
        self.average_duration = scrape_average_duration(soup)



class Threads:
    def __init__(self, func, hrefs, visited, excluded_category, excluded_text, included_text, types):

        self.list = []
        for url in hrefs:
            if url not in visited:
                self.list.append(url)

        am = len(self.list)

        self.threads = [threading.Thread(target=func, args=(
            self.list[i], hrefs, visited, excluded_category, excluded_text, included_text, types))
                        for i in range(am)]

    def start(self):
        for thread in self.threads:
            thread.start()

    def join(self):
        for thread in self.threads:
            thread.join()
