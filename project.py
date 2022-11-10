"""
CS50’s Introduction to Programming with Python
Final Project: `Mini Reader for The Hacker News website`
Save time, manage and read more articles from `The Haker News` website
with this simple command line tool.

Usage:

Show the help message:
    python project.py -h
    python project.py --help

Display the latest article titles from `thehackernews.com` homepage
    python project.py -n
    python project.py --new

List the articles stored in the `the_haker_news.db` sqlite3 local database
    python project.py -l
    python project.py --list

Add article(s) to the `the_haker_news.db` sqlite3 local database
    python project.py -a id [id ...]
    python project.py --add id [id ...]
where id is an article id number

Delete article(s) from the `the_haker_news.db` sqlite3 local database
    python project.py -d id [id ...]
    ython project.py --del id [id ...]
where id is an article id number
"""

import os
import sqlite3
import requests
import argparse
from datetime import datetime

# pip install tabulate
from tabulate import tabulate

# pip install beautifulsoup4
from bs4 import BeautifulSoup


HACKER_NEWS_URL = "https://thehackernews.com/"
DB_PATH = os.path.join(os.getcwd(), "the_haker_news.db")


class Ansi:
    """class for Ansi color codes"""

    red = "\033[31m"
    orange = "\033[33m"
    green = "\033[32m"
    underline = "\033[4m"
    reset = "\033[0m"


def scrap_articles_and_urls():
    """scrap `thehackernews.com` homepage and get the articles titles,
    articles dates of publication, and articles url
    :return: list of dict. Each dict contains title, date, url and id number
    for one article
    :rtype: list
    """
    # inititate the articles list to be returned
    articles_list = []

    # get the home page html data and parse it with BeautifulSoup
    try:
        data = requests.get(HACKER_NEWS_URL)
    except:
        data = [{}]
    soup = BeautifulSoup(data.text, "html.parser")

    # get the articles titles and related articles urls
    urls = soup.find_all("a", "story-link")
    dates = soup.find_all("div", "item-label")
    titles = soup.find_all("h2", "home-title")
    ids = range(len(titles))
    for id, title, date, url in zip(ids, titles, dates, urls):
        articles_list.append(
            {
                "id": id + 1,
                "date": date.text.split("\ue804")[0].replace("\ue802", ""),
                "title": title.text,
                "url": url["href"],
            }
        )

    return articles_list


def new_articles():
    """display the latest articles from `thehackernews.com` homepage
    :return: None
    :rtype: NoneType
    """
    # get the latest articles data from `thehackernews.com` homepage
    homepage_articles = scrap_articles_and_urls()

    # if no article found on `thehackernews.com` homepage, print a message
    if len(homepage_articles) == 0:
        print(Ansi.red
              + "`thehackernews.com` homepage doesn't contain article."
              + Ansi.reset)

    # display the articles found on `thehackernews.com` homepage
    else:
        print(
            Ansi.underline
            + Ansi.orange
            + "\nLatest articles from `thehackernews.com` homepage"
            + Ansi.reset
        )
        print(tabulate(homepage_articles, tablefmt="heavy_grid"))


def list_articles(conn):
    """list the articles data stored in `articles` table of
    `the_haker_news.db` sqlite3 database
    :param conn: Connection object of `the_haker_news.db` sqlite3 database
    :type conn: sqlite3.Connection
    :return: None
    :rtype: NoneType
    """
    # set up the cursor
    cursor = conn.cursor()

    # build the sql request
    sql = """SELECT * FROM articles;"""

    # execute the request, convert articles from
    # list of tuples into list of lists
    articles = cursor.execute(sql).fetchall()
    articles = [[a for a in article] for article in articles]

    # if no article, print a message and return
    if not articles:
        print(
            Ansi.orange
            + "\nNo article stored in `the_haker_news.db` database\n"
            + Ansi.reset
        )
        return

    # if there are articles, convert the datetime objects to strings
    for i in range(len(articles)):
        articles[i][1] = articles[i][1].strftime("%B %d, %Y")

    # and display the result
    print(
        Ansi.underline
        + Ansi.orange
        + "\nArticles stored in `the_haker_news.db` database"
        + Ansi.reset
    )
    print(tabulate(articles, tablefmt="heavy_grid") + "\n")


def add_article(article_ids, conn):
    """add title, date of publication and url for each article's id
    to the `articles` table of `the_haker_news.db` sqlite3 database
    :param article_ids: ids of the articles to be added
    :type article_ids: list
    :param conn: Connection object of `the_haker_news.db` sqlite3 database
    :type conn: sqlite3.Connection
    :return:
    """
    # set up the cursor
    cursor = conn.cursor()

    # get the latest articles data from `thehackernews.com` homepage
    homepage_articles = scrap_articles_and_urls()

    # set a list of the articles to be added
    to_be_added = []

    # loop through the `thehackernews.com` homepage articles
    for article in homepage_articles:

        # the article id must be in homepage_articles
        if article["id"] in article_ids:

            # the article url must not already be in the `articles` table of
            # `the_haker_news.db` database (to avoid duplicates)
            # build the sql request and execute the request
            sql = """ SELECT * FROM articles WHERE url = ?"""
            in_db = cursor.execute(sql, [article["url"]]).fetchall()

            # if the article is not already in the `articles` table of
            # `the_haker_news.db` database, add it to the `to_be_added` list
            if not in_db:
                to_be_added.append(article)

            # print a message if article already in the `articles` table of
            # `the_haker_news.db` database
            else:
                print(
                    Ansi.orange
                    + f"\nArticle #{article['id']} already in database"
                    + Ansi.reset
                )

    # print a message if article id not in `homepage_articles`
    homepage_ids = [article["id"] for article in homepage_articles]
    ids_not_in_homepage = list(set(article_ids) - set(homepage_ids))
    if ids_not_in_homepage:
        print(
            Ansi.orange
            + f"\nArticle {' '.join([f'#{id}' for id in ids_not_in_homepage])}"
            + " not in the `thehackernews.com` homepage articles list."
            + Ansi.reset
        )

    # if no article to be added, display a message and return
    if not to_be_added:
        print(Ansi.orange + "\nNo article to be added.\n" + Ansi.reset)
        return

    # display the related data of the articles to be added and
    # ask for confirmation
    print(
        Ansi.underline
        + Ansi.orange
        + "\nArticle(s) to be added in `the_haker_news.db`"
        + Ansi.reset
    )
    print(tabulate(to_be_added, tablefmt="heavy_grid"))
    choice = ""
    while choice not in ("y", "yes", "n", "no"):
        choice = input(Ansi.red + "Are you sure (y/n) ? " + Ansi.reset).lower()

    # if confirmation, add the data to the `the_haker_news.db` sqlite3 database
    if choice in ("y", "yes"):

        # loop through each article to be added
        for article in to_be_added:

            # convert date into datetime object and build the sql requestproject.py
            date = datetime.strptime(article["date"], "%B %d, %Y")
            columns = "date, title, url"
            values = [date, article["title"], article["url"]]
            sql = f"INSERT INTO articles ({columns}) VALUES (?, ?, ?);"

            # execute the request
            cursor.execute(sql, values)
            conn.commit()

        # print a confirmation message
        print(Ansi.orange + f"Added: {len(to_be_added)} article(s).\n" + Ansi.reset)

    # if no confirmation, print a message
    else:
        print(Ansi.orange + f"No article has been added.\n" + Ansi.reset)


def del_article(article_ids, conn):
    """delete article, date of publication and url to the `articles` table
    of `the_haker_news.db` sqlite3 database and reset the id column
    :param article_ids: ids of the articles to be deleted
    :type article_ids: list
    :param conn: Connection object of `the_haker_news.db` sqlite3 database
    :type conn: sqlite3.Connection
    :return:
    """
    # set up the cursor
    cursor = conn.cursor()

    # set a list of the articles id to be deleted
    id_to_be_deleted = []

    # loop through the article ids to be deleted
    for id in article_ids:

        # the article id must be in in the `articles` table of
        # `the_haker_news.db` database
        # build the sql request and execute the request
        sql = """ SELECT * FROM articles WHERE id = ?"""
        in_db = cursor.execute(sql, [id]).fetchall()

        # if the article is in the `articles` table of
        # `the_haker_news.db` database, add it to the `to_be_deleted` list
        if in_db:
            id_to_be_deleted.append(id)

        # print a message if article not in the `articles` table of
        # `the_haker_news.db` database
        else:
            print(Ansi.orange + f"\nArticle #{id} not in database" + Ansi.reset)

    # set a list of the articles to be deleted
    question_marks = ", ".join("?" * len(article_ids))
    sql = f"SELECT * FROM articles WHERE id IN ({question_marks});"
    cursor = conn.cursor()
    data = conn.execute(sql, article_ids).fetchall()
    to_be_deleted = [
        {
            "id": row[0],
            "date": row[1].strftime("%B %d, %Y"),
            "title": row[2],
            "url": row[3],
        }
        for row in data
    ]

    # if no article to be deleted, display a message and return
    if not to_be_deleted:
        print(Ansi.orange + "\nNo article to be deleted.\n" + Ansi.reset)
        return

    # display the related data of the articles to be deleted and
    # ask for confirmation.
    print(
        Ansi.underline
        + Ansi.orange
        + "\nArticle(s) to be deleted in `the_haker_news.db`"
        + Ansi.reset
    )
    print(tabulate(to_be_deleted, tablefmt="heavy_grid"))
    choice = ""
    while choice not in ("y", "yes", "n", "no"):
        choice = input(Ansi.red + "Are you sure (y/n) ? " + Ansi.reset).lower()

    # if confirmation, delete article(s) from `the_haker_news.db` sqlite3 database
    if choice in ("y", "yes"):

        # loop through each article to be added
        for article in to_be_deleted:

            # build the sql request, execute the request

            id = [article["id"]]
            sql = """DELETE FROM articles WHERE id = ?;"""
            cursor.execute(sql, id)
            conn.commit()

        # print a confirmation message
        print(Ansi.orange + f"Deleted: {len(to_be_deleted)} article(s).\n" + Ansi.reset)

        # reset id: get the list ids, the number of rows and update the ids
        list_ids = conn.execute("""SELECT id FROM articles;""").fetchall()
        list_ids = [id[0] for id in list_ids]
        nb_rows = len(conn.execute("""SELECT * FROM articles;""").fetchall())
        sql = """UPDATE articles SET id = ? WHERE id = ?"""
        for current_id, new_id in zip(list_ids, range(1, nb_rows + 1)):
            cursor.execute(sql, [new_id, current_id])
            conn.commit()

    # if no confirmation, print a message
    else:
        print(Ansi.orange + f"No article has been deleted.\n" + Ansi.reset)


def main():
    # connect to the `the_haker_News` sqlite3 database
    try:
        conn = sqlite3.connect(
            DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
    except sqlite3.Error as e:
        print(f"Can't connect to the `the_haker_news.db` database: {e}")

    # if not already exists, create `articles` table
    columns = "id integer PRIMARY KEY, date timestamp, title string, url string"
    sql_create_table = f"CREATE TABLE IF NOT EXISTS articles ({columns});"
    cursor = conn.cursor()
    cursor.execute(sql_create_table)

    # set up the parser
    description = "`Mini Reader for The Haker News`: manage your articles with \
        simple command lines"
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()

    # set up `-n --new` argument: display the latest articles
    # from `thehackernews.com` homepage
    group.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="display the article titles from `thehackernews.com` homepage",
    )

    # set up `-l --list` argument: display the articles stored in the `articles`
    # table of `the_haker_news.db` sqlite3 database
    group.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list the articles stored in the `the_haker_news.db` sqlite3 database",
    )

    # set up `-a --add` argument: add article(s) data to the `articles` table
    # of `the_haker_news.db` sqlite3 database
    group.add_argument(
        "-a",
        "--add",
        type=int,
        nargs="+",
        help="add article(s) to the `the_haker_news.db` database",
    )

    # set up `-d --del` argument: delete article(s) data from the `articles`
    # table of `the_haker_news.db` sqlite3 database
    group.add_argument(
        "-d",
        "--del",
        type=int,
        nargs="+",
        help="delete article(s) from the `the_haker_news.db` database",
    )

    # parse the command line into a dict
    args = vars(parser.parse_args())

    # command line is `-n --new`
    if args["new"]:
        new_articles()

    # command line id `-l --list`
    elif args["list"]:
        list_articles(conn)

    # command line is `-a --add`
    elif args["add"]:
        article_ids = args["add"]
        add_article(article_ids, conn)

    # command line id `-d --del`
    elif args["del"]:
        article_ids = args["del"]
        del_article(article_ids, conn)


if __name__ == "__main__":
    main()
