from bs4 import BeautifulSoup, NavigableString
from pprint import pprint

baseURL = r'https://www.oxfordlearnersdictionaries.com/definition/english/{}'
fileName = 'oald'

def getEntry(text):
    soup = BeautifulSoup(text, 'html.parser')
    for item in soup.find_all(id='main_column'):
        # get words, pos
        words = set()
        pos = set()
        for div1 in item.find_all(class_='webtop'):
            for div2 in div1.find_all(class_='headword'):
                words.add(div2.get_text(strip=True))
            for div2 in div1.find_all(class_='pos'):
                pos.add(div2.get_text(strip=True))
        
        for div1 in item.find_all('td', attrs={'class': 'verb_form'}):
            for div2 in div1:
                if isinstance(div2, NavigableString):
                    strippedWord = div2.strip()
                    if strippedWord != '':
                        words.add(strippedWord)

        # get IPA
        #ipa = {'BrE':[('ipa', 'voiceURL')], 'NAmE':[('ipa', 'voiceURL')]}
        ipa = {}
        # BrE
        brePhonList = []
        for div1 in item.find_all(class_='phons_br'):
            voiceURL = None
            IPA = None
            for div2 in div1.find_all(class_='pron-uk'):
                voiceURL = div2['data-src-mp3']
            for div2 in div1.find_all(class_='phon'):
                IPA = div2.get_text(strip=True)
            brePhonList.append((IPA, voiceURL))

        # NAmE
        namePronList = []
        for div1 in item.find_all(class_='phons_n_am'):
            voiceURL = None
            IPA = None
            for div2 in div1.find_all(class_='pron-us'):
                voiceURL = div2['data-src-mp3']
            for div2 in div1.find_all(class_='phon'):
                IPA = div2.get_text(strip=True)
            namePronList.append((IPA, voiceURL))
        
        ipa = {'BrE': brePhonList, 'NAmE': namePronList}


        # get SENSES
        senses = {}
        for div1 in item.find_all(class_='sense'):
            sense = []
            egs = []
            
            # get INFO
            for div2 in div1.find_all(class_='grammar'):
                for item1 in div2.get_text(strip=True).replace('[', '').replace(']', '').split(', '):
                    pos.add(item1)
            
            # get sense
            for div2 in div1.find_all(class_='def'):
                sense.append(div2.get_text(' ', strip=True).replace(' ,', ','))
            
            # get examples
            for div2 in div1.find_all(class_='examples'):
                for div3 in div2.find_all(class_='x'):
                    egs.append(div3.get_text(' ', strip=True).replace(' ,', ','))
            
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

with open('work.html', 'r') as fh:
    txt = fh.read()

k = getEntry(txt)

pprint(k)
