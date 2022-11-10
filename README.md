# Mini Reader for The Hacker News website
#### Video Demo: <https://youtu.be/rOTgbj21BLI>
#### Description:
  Save time, manage and read more articles from `The Haker News` website
  with this simple command line tool.

  The user can display in the terminal the list of the `thehackernews.com` homepage articles.
  He can also save any article data (date, title and url) in a local sqlite3 database.
  Finally, the user can display the content of this database, read articles by clicking on the associated urls and delete the non relevant articles.

  This is the final project of the `CS50’s Introduction to Programming
  with Python` course from Harvard University.
  https://cs50.harvard.edu/python/2022/project/

  Link to `The Haker News` website: https://thehackernews.com/


  ## Installation
  - It is recommended to use a virtual environment to install this project.
  - Fork this repository and install the required librairies from `requirements.txt`
  - Use the command lines below.

  ### Usage:

  - Show the help message:
  ```
  python project.py -h
  python project.py --help
  ```

  - Display the latest article titles from `thehackernews.com` homepage:
  ```
  python project.py -n
  python project.py --new
  ```

  - List the articles stored in the `the_haker_news.db` sqlite3 local database:
  ```
  python project.py -l
  python project.py --list
  ```

  - Add article(s) to the `the_haker_news.db` sqlite3 local database
  (where `id` is an article id number from the latest articles list):
  ```
  python project.py -a id [id ...]
  python project.py --add id [id ...]
  ```

  - Delete article(s) from the `the_haker_news.db` sqlite3 local database
  (where `id` is an article id number from the latest articles list):
  ```
  python project.py -d id [id ...]
  python project.py --del id [id ...]
  ```
    where `id` is an article id number from the stored articles list

  - Full syntax:
  ```
  project.py [-h] [-n | -l | -a ADD [ADD ...] | -d DEL [DEL ...]]
  ```

### Files description:
  - `project.py` : this file contains all the code of the command line tool.

  - `test_project.py` : this file contains all the tests for project.py, using `pytest`

  - `requirements.txt` : required libraries

  - `the_hacker_news.db` sqlite3 database path is set by using the global variable `DB_PATH` in `project.py`. By default, `the_hacker_news.db` will be created at the root of the project.
