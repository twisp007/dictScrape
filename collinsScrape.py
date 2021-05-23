from bs4 import BeautifulSoup
from pprint import pprint

baseURL = r'https://www.collinsdictionary.com/dictionary/english/{}'
fileName = 'collins'

def getEntry(text):
    soup = BeautifulSoup(text, 'html.parser')
    for item in soup.find_all(class_='cB cB-def cobuild br'):
        # get words
        words = []
        orthList = item.find_all(class_='orth')
        for orth in orthList:
            if len(orth['class']) == 1:
                words.append(orth.get_text(strip=True))
        
        
        # get IPA
        ipa = []
        for IPASoup in item.find_all(class_='pron type-'):
            ipa.append(IPASoup.get_text(strip=True))
        
        # get SENSES
        senses = {}
        for hom in item.find_all(class_='hom'):
            pos = []
            sense = []
            egs = []
            
            # get POS
            for posSoup in hom.find_all(class_='pos'):
                pos.append(posSoup.get_text(strip=True))
            
            # get sense
            for senseSoup in hom.find_all(class_='def'):
                sense.append(senseSoup.get_text(' ', strip=True).replace(' ,', ','))
            
            # get examples
            for egSoup in hom.find_all(class_='quote'):
                egs.append(egSoup.get_text(' ', strip=True).replace(' ,', ','))
            
            # sense dict
            senseDict = {
                'pos' : pos,
                'sense' : sense,
                'egs' : egs
            }
            
            if senseDict['sense'] != []:
                senses[len(senses)] = senseDict
        
        # entry dict
        entry = {
            'words' : words,
            'ipa' : ipa,
            'senses' : senses,
            'markup' : str(item)
        }
        
        return entry
