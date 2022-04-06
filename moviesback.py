''' By Apollo Hodges and Laura Finkelstein'''
''' This code scrapes the Rotten Tomatoes 2021 articles and  puts that info into a json file'''
''' The second part of the code loads the movie title, URL, directors, actors and date into a database'''


import urllib.request as ur
import requests
import unicodedata
from bs4 import BeautifulSoup
import re
import json
import sqlite3

'''
#This can be ignored, unless you want to create a new json file.
movie = ""
url = ""
date = ""
director = ""
actor = ""
actorList = []
movieList = []
page = requests.get('https://editorial.rottentomatoes.com/article/most-anticipated-movies-of-2021/')
soup = BeautifulSoup(page.content, "lxml")
tag = soup.find('div', class_='articleContentBody')
i = 1
j = 1
k = 1
r = 1
n = 1
for link in tag.find_all('p') :
#    print(link.text)
    if len(link.find_all('a')) == 1:
        try:
            movie = link.strong.a.text
         #   print(i, "Movie: ", movie)
            i += 1

        except:
            pass
        try:
            url = link.strong.a['href']
        #    print(n, "URL: ", url)
            n += 1
        except:
            pass

    elif link.select_one("b"):
        a = link
        if a.next_element.next_element.find("Starring:"):
            # print(i, link.select_one("strong").text)
            movie = link.select_one("b").text
        #    print(i, "Movie: ", movie)
            i += 1
        #    print(n, "URL: N/A")
            movie = link.select_one("b").text
            n += 1

    elif link.select_one("strong"):
        a = link
        if a.next_element.next_element.find("Starring:"):
            # print(i, link.select_one("strong").text)
            movie = link.select_one("strong").text
         #   print(i, "Movie: ", movie)
            i += 1
        #    print(n, "URL: N/A")
            n += 1
            movie = link.select_one("strong").text

    string = link.text.replace(u'\xa0', u' ')
    m = re.search('Direct.*:\s?(.*)', string)
    m1 = re.search('.*Starring:\s?[\xa0]?[\u00a0]?(.*)', string)
    if m is not None:
        m.group()
        director = m.group(1)
     #   print(j, "Director:",  director)
        j += 1
    if m1 is not None:
        m1.group()
        actor = m1.group(1)
     #   print(k, "Actor: ", actor)
        k += 1

    m3 = re.search('Open.*:\s*[\xa0]?([A-Z0-9]\S*)', link.text)
    if m3 is not None:
        # print(l, "group 1", m3.group(1))
        # print(i, "group 2", m3.group(2))
        date = m3.group(1)
    #    print(r, "date", date)

        r += 1


    if movie != "" and actor != "":
        movieu = unicodedata.normalize("NFKD", movie)
        actorList = actor.split(", ")
        tempList = [movieu, url, director.strip(), actorList, date]
        # print(tempList)
        movieList.append(tempList)

    movie = ""
    url = ""
    director =  ""
    date = ""
    actor = ""
    actorList = []

ind = 1
for line in movieList:
    print(ind, line)
    ind += 1

j = json.dumps(movieList)

with open('movies.json', 'w') as fh:
    json.dump(j, fh, indent=3)

'''


with open('movies.json', 'r') as fh:
    data = json.load(fh)

movies = json.loads(data)

conn = sqlite3.connect('Movies.db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS MoviesDB")
cur.execute('''CREATE TABLE MoviesDB(
                title TEXT UNIQUE ON CONFLICT IGNORE,
                url TEXT,
                director TEXT,
                month INTEGER)''')

cur.execute("DROP TABLE IF EXISTS MonthsDB")
cur.execute('''CREATE TABLE MonthsDB(
                id INTEGER NOT NULL PRIMARY KEY,
                months TEXT UNIQUE ON CONFLICT IGNORE)''')

actorLength = [len(item[3]) for item in movies]
maxActor = max(actorLength)

for i in range(maxActor) :
    cur.execute('''ALTER  TABLE  MoviesDB  ADD COLUMN {}  TEXT''' \
                .format('actor'  +  str(i) ))


for item in movies:
    cur.execute('''INSERT INTO MonthsDB
                (months)
                VALUES
                (?)''', (item[4],))
    cur.execute("SELECT id FROM MonthsDB WHERE months = ? ", (item[4],))
    month_id = cur.fetchone()[0]

    cur.execute('''INSERT INTO MoviesDB
                (title, url, director, month)
                VALUES
                (?, ?, ?, ?)''', (item[0], item[1], item[2], month_id))

    list_actors = item[3]
    for i in range(len(list_actors)):

        cur_statement = "UPDATE MoviesDB SET (actor%s) = \"%s\" WHERE title = \"%s\";" % (str(i), list_actors[i], (item[0]))
        cur.execute(cur_statement)

conn.commit()

