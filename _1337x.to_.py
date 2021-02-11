from bs4 import BeautifulSoup
import requests  
import re

file = open("1337x-partially-scraped.txt", "w")

usr_list = ['FitGirl']

def parsedPage(Link):
    grabbedPage = requests.get(Link)
    return (BeautifulSoup(grabbedPage.content, 'html.parser'))

def Parser(storePage):
    for Link in storePage.find_all('a'):
        StrLink = str(Link)
        regexResult = re.search(r'"/(.*)/"', StrLink)
        if regexResult == None:
            continue
        if not 'torrent/' in regexResult.group(1):
            continue
        magnet_link = ("magnet" + re.search(r'href="magnet(.*)" onclick', str(parsedPage("https://1337x.to/" + regexResult.group(1) + "/"))).group(1)).replace("&amp;","&")
        print(magnet_link, end = "\n\n")
        file.write(magnet_link + "\n\n")

def main(username):
    for i in range (1, int(re.search(r'-torrents/(.*)/">Last</a>', str(parsedPage("https://1337x.to/" + username + "-torrents/1/"))).group(1))+1):
        Parser(parsedPage("https://1337x.to/" + username + "-torrents/" + str(i) + "/"))

for i in usr_list:
    main(i)

file.close()
