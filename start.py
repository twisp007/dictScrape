from selenium import webdriver
from pprint  import pprint
import json
import random
import time
from pathlib import Path

import sDB

import collinsScrape
import oaldScrape

def waitx():
    sr = random.SystemRandom()
    waitTimeSec = sr.randrange(180, 300)
    time.sleep(int(waitTimeSec))


#get words from list
payload = []

fileList = []

for item in Path('lists/').rglob('*'):
    if item.is_file():
        fileList.append(str(item))

for item in fileList:
    worldList = []
    with open(item, 'r') as fh:
        fileLines = fh.readlines()
    for line in fileLines:
        worldList.append(line.split(" ")[0].strip())
    payload.append({
        'listName' : item,
        'worldList' : worldList
    })

PROXY = "localhost:80"
webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
    "httpProxy": PROXY,
    "ftpProxy": PROXY,
    "sslProxy": PROXY,
    "proxyType": "DIRECT",

}


def logErr(fileName, word, errorMsg=''):
    errorTxt = word + ' |||| ' + str(errorMsg)
    with open(fileName + '.log', 'a') as fh:
        fh.write(errorTxt)    


with webdriver.Firefox() as driver:
    for dk in [collinsScrape, oaldScrape]:
        baseURL = dk.baseURL
        fileName = dk.fileName
        
        for item in payload:
            worldList = item['worldList']

            dbFile = fileName + '.sqlite'
            dbConn = sDB.start(dbFile)
            
            index = 0
            while index < len(worldList):
                word = worldList[index]
                if sDB.checkEntry(word, dbConn):
                    print('Duplicate Entry::', index, ':', word)
                    index += 1
                    continue
                print('Extracting::', index, ':', word)
                url = baseURL.format(word)
                # Open URL
                try:
                    driver.get(url)
                    source = driver.page_source
                except Exception as e:
                    print(e)
                    waitx()
                    index = 0
                    continue
                else:
                    try:
                        entry = dk.getEntry(source)
                    except Exception as e1:
                        print("UNABLE TO EXTRACT ENTRY::", e1)
                        pprint(source)
                        index += 1
                        logErr(fileName, word, str(e1))
                        continue
                    if entry is not None:
                        sDB.insertEntry(entry, dbConn)
                    else:
                        errMsg = 'Entry not Found in ' + fileName
                        print(errMsg, "::", word)
                        logErr(fileName, word, errMsg)
                    index += 1
            sDB.end(dbConn)
