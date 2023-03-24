
import os
import urllib.request
import bs4
import sqlite3
from datetime import datetime
import time

old_file = 'imdb_checklist.txt'
imdb_url = 'https://www.imdb.com/chart/top/?ref_=ats_top250badge_intop250_to_top250chart'

class DBRunner:

    def __init__(self, db='mymdb.sqlite'):
        self.db = db
        self.con = None
        self.start_dt = datetime.utcnow()

    def __del__(self):
        #self.findOldRecords()
        print("Should delete records older than " + str(self.start_dt))
        self.cleanRemainingRecords(self.start_dt)
        self.__dbclose()

    def dbconnect(self):
        self.con = sqlite3.connect(self.db)
    
    def __dbclose(self):
        self.con.close()

    def hasWatched(self, title):
        sql = ''' SELECT watched
                  FROM MOVIES
                  WHERE title = ? '''
        cur = self.con.cursor()
        result = cur.execute(sql, (title,))
        return result.fetchone()

    def selectMovie(self, title):
        sql = ''' SELECT rank, title, watched
                  FROM MOVIES
                  WHERE title = ? '''
        cur = self.con.cursor()
        result = cur.execute(sql, (title,))
        return result.fetchall()

    def insertNewMovie(self, rank, title, watched=False):
        sql = ''' INSERT INTO movies
                  (rank, title, watched, created_dt)
                  values
                  (?, ?, ?, ?) '''
        cur = self.con.cursor()
        cur.execute(sql, (rank, title, watched, self.start_dt))
        self.con.commit()

    def updateRank(self, rank, title):
        sql = ''' UPDATE movies
                  SET rank = ?,
                  created_dt = ?
                  WHERE title = ? '''
        cur = self.con.cursor()
        cur.execute(sql, (rank, self.start_dt, title))
        self.con.commit()

    def updateTimestamp(self, title):
        sql = ''' UPDATE movies
                  SET created_dt = ?
                  WHERE title = ? '''
        cur = self.con.cursor()
        cur.execute(sql, (self.start_dt, title))
        self.con.commit()

    def watchMovie(self, title):
        sql = ''' UPDATE movies
                  SET watched = true,
                  created_dt = ?
                  WHERE title = ? '''
        cur = self.con.cursor()
        cur.execute(sql, (title, self.start_dt))
        self.con.commit()
        
    def insertMovie(self, rank, title, watched=False):
        current = self.selectMovie(title)
        if not current:
            self.insertNewMovie(rank, title, watched)
        elif current[0][0] != rank:
            self.updateRank(rank, title)
        else:
            self.updateTimestamp(title)

    def pruneMovie(self, title, newest_dt=None):
        if not newest_dt:
            sql = ''' SELECT created_dt
                      FROM movies
                      WHERE title = ?
                      ORDER BY created_dt DESC '''
            cur = self.con.cursor()
            newest_dt = cur.execute(sql, (title,)).fetchone()

        sql = ''' DELETE FROM movies
                  WHERE title = ?
                  AND created_dt < ? '''
        cur = self.con.cursor()
        cur.execute(sql, (title, newest_dt))
        self.con.commit()

    def findOldRecords(self):
        sql = ''' SELECT rank
                  FROM movies
                  GROUP BY rank 
                  HAVING count(*) > 1 '''
        cur = self.con.cursor()
        for title in cur.execute(sql).fetchall():
            self.pruneMovie(title)

    def cleanRemainingRecords(self, run_date):
        sql = ''' DELETE FROM movies
                  WHERE created_dt < ? '''
        cur = self.con.cursor()
        cur.execute(sql, (run_date,))
        self.con.commit()

def url_to_soup(url):
    #print(url, flush=True)
    try:
        req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = urllib.request.urlopen(req).read()
        #soup = bs4.BeautifulSoup(html)
        soup = bs4.BeautifulSoup(html, 'html.parser')
    except urllib.error.HTTPError:
        print('they think they can stop me?')
        time.sleep(5)
        req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = urllib.request.urlopen(req).read()
        #soup = bs4.BeautifulSoup(html)
        soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup

def upd_from_web():
    imdb_soup = url_to_soup(imdb_url)
    titles = imdb_soup.find_all('td', class_='titleColumn')
    dbr = DBRunner()
    dbr.dbconnect()
    rank = 1
    for title in titles:
        movie_title = title.find('a').text.strip()
        dbr.insertMovie(rank, movie_title)
        rank = rank + 1

def upd_from_file():
    fid = open(old_file, 'r')
    dbr = DBRunner()
    dbr.dbconnect()
    lines = fid.readlines()
    rank = 1
    for line in lines:
        if line[0] == 'x':
            dbr.insertMovie(rank, line[2:].strip(), True)
        else:
            dbr.insertMovie(rank, line[2:].strip())
        rank = rank + 1
    fid.close()
            
#upd_from_file()
#time.sleep(5)
upd_from_web()
