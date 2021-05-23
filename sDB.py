import sqlite3
from sqlite3 import Error
import json
from json_minify import json_minify
from bs4 import BeautifulSoup
import unicodedata, re, itertools, sys
import htmlmin

#https://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python
all_chars = (chr(i) for i in range(sys.maxunicode))
categories = {'Cc'}
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) in categories)
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def remove_control_chars(s):
    return control_char_re.sub('', s)


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)


def start(database):
    sql_create_entries_table = """
    CREATE TABLE IF NOT EXISTS entries(
      entryID INTEGER PRIMARY KEY,
      JSON text,
      MARKUP text
    );
    """

    sql_create_words_table = """
    CREATE TABLE IF NOT EXISTS words(
      definitionID INTEGER,
      word text,
      FOREIGN KEY(definitionID) REFERENCES entry(entryID)
    );
    """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_entries_table)
        create_table(conn, sql_create_words_table)
    else:
        print("Error! cannot create the database connection.")

    return conn

def end(conn):
    return conn.close()

def insertEntry(entryDict, conn):
    cursor = conn.cursor()
    commitFlag = False
    
    markupText = htmlmin.minify(entryDict['markup'], remove_empty_space=True)
    del entryDict['markup']

    jsonText = json_minify(json.dumps(entryDict))

    cursor.execute('''INSERT INTO entries VALUES(NULL, ?, ?)''', (jsonText, markupText))

    definitionID = cursor.lastrowid

    words = []

    for item in entryDict['words']:
        words.append(item)

    words = list(set(words))

    for word in words:
        word = remove_control_chars(word).replace(r'\n ', '')
        cursor.execute('''INSERT INTO words VALUES(?, ?)''', (definitionID, word))
        commitFlag = True

        if ' ' in word:
            word = word.replace(' ', '')
            cursor.execute('''INSERT INTO words VALUES(?, ?)''', (definitionID, word))
            commitFlag = True

    if commitFlag:
        conn.commit()

def getEntry(entry, conn, showErr = True):
    rs = []
    cursor = conn.cursor()

    cursor.execute('''SELECT * from words WHERE word=?''', (entry,))
    rows = cursor.fetchall()

    if len(rows) == 0:
        cursor.execute('''SELECT * from words WHERE word=?''', (entry.replace(' ', ''), ))
        rows = cursor.fetchall()

    if len(rows) > 0:
        for row in rows:
            definitionID = row[0]
            cursor.execute('''SELECT * from entries WHERE entryID=?''', (definitionID,))
            rows2 = cursor.fetchall()

            if len(rows2) > 0:
                for row2 in rows2:
                    rs.append(row2)
            else:
                if showErr:
                    print('ERR2: No such entry:', entry)
                else:
                    pass
    else:
        if showErr:
            print('ERR1: No such entry:', entry)
        else:
            pass
    
    return rs

def checkEntry(entry, conn):
    if getEntry(entry, conn, showErr = False) != []:
        return True
    else:
        return False
