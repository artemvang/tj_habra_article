import requests
import simplejson as json
from bs4 import BeautifulSoup
import threading

url = "https://tjournal.ru/{article_id}"


def process_url(html):
    tree = BeautifulSoup(html, "lxml")
    article = tree.find("article")
    rating = tree.find(
        "div", attrs={"class": "b-articles__b__rating"}).find("b").text
    date = tree.find("span", attrs={"class": "b-article__infoline__date"}).text
    hits = tree.find(
        "span", attrs={"class": "b-article__infoline__views"}).find("b").text
    title = tree.find(
        "div", attrs={"class": "b-article__title"}).find("h1").text
    comments = tree.find(
        "span",
        attrs={"class": "b-article__infoline__comments"}).find("b").text

    if rating != "0":
        rating_int = int(rating[1:])
        rating_int = rating_int if rating[0] != "–" else -rating_int
    else:
        rating_int = 0
    return {
        "article": str(article),
        "rating": rating_int,
        "date": date,
        "title": title,
        "hits": int(hits.replace(" ", "")),
        "comments": int(comments.replace(" ", ""))
    }


class MyThread(threading.Thread):
    def __init__(self, url):
        super(MyThread, self).__init__()
        self.url = url
        self.result = None

    def run(self):
        data = requests.get(self.url)
        if data.status_code == 404:
            return
        try:
            self.result = process_url(data.text)
        except ValueError:
            print(self.url)


def main(count):
    all_data = []
    threads = []
    for art_id in range(1, 42324, count):
        for thr in range(count):
            thread = MyThread(url.format(article_id=art_id + thr))
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()

        all_data += [i.result for i in threads if i.result]
        threads = []
        with open("data/tj_site.json", "w") as f:
            json.dump(all_data, f)


main(10)
