from datetime import datetime
import operator
from utils import *


def main(anime, excluded_category=[], excluded_text=[], included_text=[], types=["anime", "manga"]):
    types = [x for x in types if x]  # If there's only empty strings inside types, it appends "anime"
    if len(types) == 0:
        types.append("anime")

    # The lists get proper format ("_" instead of " ", etc...)
    excluded_text = parse_inc_exc(excluded_text)
    included_text = parse_inc_exc(included_text)

    # Gets the first anime
    url = get_base_anime(anime, types[0])

    first = datetime.now()

    hrefs = []
    visited = []

    # Gets first related animes without multi threading
    get_relateds(url, hrefs, visited, excluded_category, excluded_text, included_text, types)

    # If the lenght is not equal, it means we have to continue iterating
    # I think that because we do the thread.join(), this is useless, since it will be iterating
    # at the "for href in hrefs" level, not here
    while len(hrefs) != len(visited):
        for href in hrefs:
            if href not in visited:
                thrd = Threads(get_relateds, href, hrefs, visited, excluded_category, excluded_text, included_text,
                               types)
                thrd.start()
                thrd.join()

    print("Checking dates and names that were not added...")

    # In case there was some problem with settings the parametters, we check the dates and the names again
    check_dates(visited)
    check_names(visited)

    sorted_visited = sorted(visited, key=operator.attrgetter('date'))

    for idx, visit in enumerate(sorted_visited):
        print(f"{idx + 1} {visit.date} - {visit.name} ({visit.url})")

    total_time = datetime.now() - first
    print(total_time, total_time.total_seconds() / len(visited))


# url = "one piece"
# excluded_category = [""]
# excluded_text = [""]
# included_text = ["one piece"]
# types = [""]
#
# main(url, excluded_category, excluded_text, included_text, types)

# anime_test = Anime("https://myanimelist.net/anime/23831/Mahou_Shoujo_Madoka★Magica_Movie_3__Hangyaku_no_Monogatari_-_Magica_Quartet_x_Nisioisin")
# anime_test.name = "anime name"
# anime_test.date = ""
#
# print(anime_test.name, "date: ", anime_test.date)
# check_dates([anime_test])
# print(anime_test.name, "date: ", anime_test.date)
