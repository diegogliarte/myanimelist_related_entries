from datetime import datetime
import operator
from utils import *


def myanimelist_related_entries(anime, excluded_category=[], excluded_text=[], included_text=[], types=["anime", "manga"], sort="date"):

    try:
        # If there's only empty strings inside types, it appends "anime"
        types = [x for x in types if x]

        if len(types) == 0:
            types.append("anime")


        # The lists get proper format ("_" instead of " ", etc...)
        excluded_text = parse_inc_exc(excluded_text)
        included_text = parse_inc_exc(included_text)

        # Gets the first anime
        category = types[0]
        print(category)
        url = get_base_anime(anime, category.lower())


        first = datetime.now()

        hrefs = [url] # List of strings
        visited = [] # List of Animes


        # For each href, we create a thread that visits each thread. Once everything has been joint(), hrefs is filled
        # with more href, meaning that we can iterate again through the lasts ones. If there's been an iteration without
        # adding more href, it means that the cycle is closed, and there are no more related entries
        for href in hrefs:
            if href not in visited:
                thrd = Threads(get_relateds, hrefs, visited, excluded_category, excluded_text, included_text,
                               types)
                thrd.start()

                # Waits until all the href have been processed
                thrd.join()


        print("\nChecking dates and names that were not added...")

        # In case there was some problem with settings the parameters, we check the dates and the names again
        check_dates(visited)
        check_names(visited)

        # Sorts anime
        sorted_visited = sorted(visited, key=operator.attrgetter(sort))

        result = ""
        result_hrefs = ""
        # Prints anime
        for idx, visit in enumerate(sorted_visited):
            result += f"{idx + 1}. {visit.date} - {visit.name}\n"
            result_hrefs += f"{visit.url}\n"

<<<<<<< HEAD
        # Total duration of the process
        total_time = datetime.now() - first
        print(total_time, total_time.total_seconds() / len(visited))

        return result, result_hrefs
=======
# url = "one piece"
# excluded_category = [""]
# excluded_text = [""]
# included_text = ["one piece"]
# types = [""]
#
# main(url, excluded_category, excluded_text, included_text, types)
>>>>>>> ca717e5907aaaf3a8d0cd110161d17fce3e2e319

    except:
        return "There was a problem", "There was a problem"
#
# url = "steins gate"
# excluded_category = [""]
# excluded_text = []
# included_text = []
# types = []
#
#
# myanimelist_related_entries(url, excluded_category, excluded_text, included_text, types)

