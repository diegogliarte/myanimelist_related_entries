from flask import Flask, render_template, request
from main import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    if (request.method == 'POST'):
        print("Starting request...")

        url = request.form['url']
        print("Url: ", url)

        types = request.form.getlist('types')
        if "Both" in types:
            types = ["Anime", "Manga"]
        print("Types: ", types)

        excluded_category = request.form.getlist('excluded_category')
        print("Excl category: ", excluded_category)

        excluded_text = request.form['excluded_text'].strip().split(",")
        print("Excl text: ", excluded_text)

        included_text = request.form['included_text'].strip().split(",")
        print("Incl text: ", included_text)

        result, result_hrefs, total_duration, total_episodes = myanimelist_related_entries(url, excluded_category, excluded_text, included_text, types)

        result = result.split("\n")
        result_hrefs_print = result_hrefs.split("\n")

        zipped_data = zip(result, result_hrefs_print)
        print("Success!")
        return render_template('main.html', name='myanimelist', zipped_data=zipped_data, url=url, total_duration=total_duration, total_episodes=total_episodes)
    else:
        return render_template('main.html', name='myanimelist')


if __name__ == "__main__":
    app.run()
