import datetime
import operator
from utils import *
import string


def myanimelist_related_entries(anime, excluded_category=[], excluded_text=[], included_text=[],
                                types=["anime", "manga"], sort="date"):

        # If there's only empty strings inside types, it appends "anime"
        types = [x for x in types if x]

        if len(types) == 0:
            types.append("anime")

        # The lists get proper format ("_" instead of " ", etc...)
        excluded_text = parse_inc_exc(excluded_text)
        included_text = parse_inc_exc(included_text)

        # Gets the first anime
        category = types[0]

        url = get_base_anime(anime, category.lower())

        first = datetime.datetime.now()

        hrefs = [url]  # List of strings
        visited = []  # List of Animes

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
        check_episodes(visited)

        # Sorts anime
        sorted_visited = sorted(visited, key=operator.attrgetter(sort))

        result = ""
        result_hrefs = ""
        total_duration = datetime.timedelta(0)
        total_episodes = 0
        # Creates resulting string
        for idx, visit in enumerate(sorted_visited):
            result += f"{idx + 1}. {visit.date} - {visit.name} ({visit.episodes}, {visit.average_duration}) {visit.score}\n"
            result_hrefs += f"{visit.url}\n"
            t = 0
            try:
                t = datetime.datetime.strptime(visit.average_duration, "%M min. per ep.").time()
            except:
                try:
                    t = datetime.datetime.strptime(visit.average_duration, "%M min.").time()
                except:
                    try:
                        t = datetime.datetime.strptime(visit.average_duration, "%H hr. %M min.").time()
                    except:
                        try:
                            t = datetime.datetime.strptime(visit.average_duration, "%H hr.").time()
                        except:
                            t = datetime.time(0)

            if (visit.episodes.isdigit()):
                total_episodes += int(visit.episodes)
                total_duration += ((datetime.datetime.combine(datetime.date.min, t) - datetime.datetime.min) * int(visit.episodes))

        list_result = [result, result_hrefs, total_duration, total_episodes]

        # Total duration of the process
        total_time = datetime.datetime.now() - first
        print(total_time, total_time.total_seconds() / len(visited))
        return list_result


if __name__ == "__main__":
    url = "dragon quest"
    excluded_category = [""]
    excluded_text = ["", "", ""]
    included_text = ["dragon quest"]
    types = ["Anime"]

    print(myanimelist_related_entries(url, types=types, included_text=included_text, excluded_category=excluded_category, excluded_text=excluded_text))



