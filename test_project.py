"""
CS50’s Introduction to Programming with Python
Final Project: `Mini Reader for The Hacker News website`

Test Functions with Pytest
"""

import os
import pytest
import sqlite3
from datetime import datetime
from unittest.mock import patch
from project import scrap_articles_and_urls
from project import new_articles
from project import list_articles
from project import add_article
from project import del_article


TEST_DATA = [
    {"id": 1, "date": "January 01, 2022", "title": "test1", "url": "test1.html"},
    {"id": 2, "date": "January 01, 2022", "title": "test2", "url": "test2.html"},
    {"id": 3, "date": "January 01, 2022", "title": "test3", "url": "test3.html"},
    {"id": 4, "date": "January 01, 2022", "title": "test4", "url": "test4.html"},
    {"id": 5, "date": "January 01, 2022", "title": "test5", "url": "test5.html"},
]


@pytest.fixture
def generate_test_data_base():
    def create():
        # create set up connector to the test database
        DB_PATH = os.path.join(os.getcwd(), "the_haker_news_test.db")
        conn = sqlite3.connect(
            DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # create `articles` table in the test database
        columns = "id integer PRIMARY KEY, date timestamp, title string, url string"
        sql_create_table = f"CREATE TABLE IF NOT EXISTS articles ({columns});"
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
        # return the test database connector
        return conn

    return create


@pytest.fixture
def delete_test_data_base():
    def delete():
        # delete test database
        DB_PATH = os.path.join(os.getcwd(), "the_haker_news_test.db")
        os.remove(DB_PATH)

    return delete


def test_scrap_articles_and_urls_return_a_list():
    articles_list = scrap_articles_and_urls()
    assert type(articles_list) == list


def test_scrap_articles_and_urls_return_a_list_of_dict():
    articles_list = scrap_articles_and_urls()
    assert all(isinstance(n, dict) for n in articles_list)


def test_scrap_articles_and_urls_check_each_dict_keys():
    articles_list = scrap_articles_and_urls()
    assert all(["date" in n and "title" in n and "url" in n for n in articles_list])


def test_scrap_articles_and_urls_each_dict_date_is_string():
    articles_list = scrap_articles_and_urls()
    assert all(isinstance(n["date"], str) for n in articles_list)


def test_scrap_articles_and_urls_each_dict_title_is_string():
    articles_list = scrap_articles_and_urls()
    assert all(isinstance(n["title"], str) for n in articles_list)


def test_scrap_articles_and_urls_each_dict_url_is_string():
    articles_list = scrap_articles_and_urls()
    assert all(isinstance(n["url"], str) for n in articles_list)


def test_scrap_articles_and_urls_each_dict_url_has_html_extension():
    articles_list = scrap_articles_and_urls()
    assert all(n["url"][-5:] == ".html" for n in articles_list)


def test_new_articles_return_none():
    assert new_articles() == None


def test_list_articles_return_none(generate_test_data_base, delete_test_data_base):
    conn = generate_test_data_base()
    assert list_articles(conn) == None
    delete_test_data_base()  # delete test database


@patch("builtins.input", lambda _: "y")
@patch("project.scrap_articles_and_urls", lambda: TEST_DATA)
def test_add_article_one_article(generate_test_data_base, delete_test_data_base):
    # get the test data simulating articles data from `thehackernews.com` homepage
    articles = TEST_DATA

    # this test will be done with the first article
    new_article_id = [1]

    # add that article to the database
    conn = generate_test_data_base()
    add_article(new_article_id, conn)

    # check if only that article is in the test database
    cursor = conn.cursor()
    data = cursor.execute("""SELECT title FROM articles""").fetchall()
    check = [row[0] for row in data]
    assert (
        len(check) == len(new_article_id)
        and check[0] == articles[new_article_id[0] - 1]["title"]
    )
    delete_test_data_base()  # delete test database


@patch("builtins.input", lambda _: "y")
@patch("project.scrap_articles_and_urls", lambda: TEST_DATA)
def test_add_article_three_articles(generate_test_data_base, delete_test_data_base):
    # get the test data simulating articles data from `thehackernews.com` homepage
    articles = TEST_DATA

    # this test will be done with the articles #1 #3 #4
    new_article_id = [1, 3, 4]

    # add those articles to the database
    conn = generate_test_data_base()
    add_article(new_article_id, conn)

    # check if only those articles are in the test database
    cursor = conn.cursor()
    data = cursor.execute("""SELECT title FROM articles""").fetchall()
    check = [row[0] for row in data]
    assert (
        len(check) == len(new_article_id)
        and check[0] == articles[new_article_id[0] - 1]["title"]
        and check[1] == articles[new_article_id[1] - 1]["title"]
        and check[2] == articles[new_article_id[2] - 1]["title"]
    )
    delete_test_data_base()  # delete test database


@patch("builtins.input", lambda _: "y")
@patch("project.scrap_articles_and_urls", lambda: TEST_DATA)
def test_del_article_one_article(generate_test_data_base, delete_test_data_base):
    # get the test data simulating articles data from `thehackernews.com` homepage
    articles = TEST_DATA
    nb_articles_before_del = len(articles)

    # get the test database connector
    conn = generate_test_data_base()
    cursor = conn.cursor()

    # add all the test data articles in the test database
    for article in articles:
        date = datetime.strptime(article["date"], "%B %d, %Y")
        columns = "date, title, url"
        values = [date, article["title"], article["url"]]
        sql = f"INSERT INTO articles ({columns}) VALUES (?, ?, ?);"
        cursor.execute(sql, values)
        conn.commit()

    # this test will be done with the first article
    deleted_id = [1]

    # delete that article from the database
    del_article(deleted_id, conn)

    # check number of article and if the deleted article is not in test database
    data = cursor.execute("""SELECT title FROM articles""").fetchall()
    check = [row[0] for row in data]
    assert (
        len(check) == nb_articles_before_del - len(deleted_id)
        and articles[deleted_id[0] - 1] not in check
    )
    delete_test_data_base()  # delete test database


@patch("builtins.input", lambda _: "y")
@patch("project.scrap_articles_and_urls", lambda: TEST_DATA)
def test_del_article_three_articles(generate_test_data_base, delete_test_data_base):
    # get the test data simulating articles data from `thehackernews.com` homepage
    articles = TEST_DATA
    nb_articles_before_del = len(articles)

    # get the test database connector
    conn = generate_test_data_base()
    cursor = conn.cursor()

    # add all the test data articles in the test database
    for article in articles:
        date = datetime.strptime(article["date"], "%B %d, %Y")
        columns = "date, title, url"
        values = [date, article["title"], article["url"]]
        sql = f"INSERT INTO articles ({columns}) VALUES (?, ?, ?);"
        cursor.execute(sql, values)
        conn.commit()

    # this test will be done with articles #2, #4, #5
    deleted_id = [2, 4, 5]

    # delete that article from the database
    del_article(deleted_id, conn)

    # check number of article and if the deleted article is not in test database
    data = cursor.execute("""SELECT title FROM articles""").fetchall()
    check = [row[0] for row in data]
    assert (
        len(check) == nb_articles_before_del - len(deleted_id)
        and articles[deleted_id[0] - 1] not in check
        and articles[deleted_id[1] - 1] not in check
        and articles[deleted_id[2] - 1] not in check
    )
    delete_test_data_base()  # delete test database


@patch("builtins.input", lambda _: "y")
@patch("project.scrap_articles_and_urls", lambda: TEST_DATA)
def test_del_article_check_reseted_id(generate_test_data_base, delete_test_data_base):
    # get the test data simulating articles data from `thehackernews.com` homepage
    articles = TEST_DATA
    nb_articles_before_del = len(articles)

    # get the test database connector
    conn = generate_test_data_base()
    cursor = conn.cursor()

    # add all the test data articles in the test database
    for article in articles:
        date = datetime.strptime(article["date"], "%B %d, %Y")
        columns = "date, title, url"
        values = [date, article["title"], article["url"]]
        sql = f"INSERT INTO articles ({columns}) VALUES (?, ?, ?);"
        cursor.execute(sql, values)
        conn.commit()

    # this test will be done with articles #1, #3, #5
    deleted_id = [1, 3, 5]

    # delete that article from the database
    del_article(deleted_id, conn)

    # check if the id is reseted (starting from 1)
    data = cursor.execute("""SELECT id FROM articles""").fetchall()
    check = [row[0] for row in data]
    assert check == list(range(1, len(check) + 1))
    delete_test_data_base()  # delete test database
