from bs4 import BeautifulSoup
import requests  
import re

file = open("thehylia-scraped.txt", "w")

def parsedPage(Link):
    grabbedPage = requests.get(Link)
    return (BeautifulSoup(grabbedPage.content, 'html.parser'))

def stringLink(Link):
    regexResult = re.search('<a href=(.*)">', str(Link))  
    return (regexResult.group(1)[1:])

def checkLink(Page, String):
    for x in Page:
        if String in stringLink(x)


for hyperLink in parsedPage('https://anime.thehylia.com/soundtracks/browse/all').find_all('a'):
    
    if 'album' in stringLink(hyperLink):
        
        for hyperLink1 in parsedPage(stringLink(hyperLink)).find_all('a'):
        
            if 'mp3' in stringLink(hyperLink1): 
                
                for hyperLink2 in parsedPage(stringLink(hyperLink1)).find_all('a'):
        
                    if 'anidl.vgmdownloads.com' in stringLink(hyperLink2):
        
                        theLink = stringLink(hyperLink2)[:-20]
                        print(theLink)
                        file.write(theLink + "\n")
                        
file.close()                       