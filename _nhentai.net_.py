from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import shutil
import re
import os


def pageParser(Link):
    
    grabbedPage = requests.get(Link)
    return (BeautifulSoup(grabbedPage.content, 'html.parser'))

def infoScraper(itemCode):

    parsedPage = pageParser("https://nhentai.net/g/{}".format(itemCode))

    mangaTitle = re.search(r'">(.*)<', str(parsedPage.find_all('span', 'before')[0])).group(1) + re.search(r'">(.*)<', str(parsedPage.find_all('span', 'pretty')[0])).group(1) + re.search(r'">(.*)<', str(parsedPage.find_all('span', 'after')[0])).group(1)
    mangaPages = re.search(r'Pages:\n\t\t\t\t\t\t\t\t(.*)\n\t\t\t\t\t\t\t\tUploaded:', parsedPage.get_text()).group(1)

    print('{} - {}'.format(itemCode, mangaTitle))
    print(mangaPages + ' pages')
    
    return (['{} - {}'.format(itemCode, mangaTitle), mangaPages])

def idScraper(itemCode):

    parsedPage = pageParser("https://nhentai.net/g/{}/1/".format(itemCode))
    imageId = re.search(r'https://i.nhentai.net/galleries/(.*)/1.jpg', str(parsedPage)).group(1)
    print(imageId)

    return (imageId)
    
itemCode = 1

while True:

    if requests.get('https://nhentai.net/g/{}/'.format(itemCode)).status_code == 404 :
        print('Page not found.\n')
        itemCode += 1
        continue

    info = infoScraper(itemCode)
    image = idScraper(itemCode)

    if not os.path.exists(info[0]):
        os.makedirs(info[0])
    
    for i in range(1, int(info[1])+1):    
        try:
            if os.path.exists(info[0]+("/{}.jpg".format(i))): 
                print("Exists - " + "https://i.nhentai.net/galleries/{}/{}.jpg".format(image, i))
                continue
            imgFile = urlopen("https://i.nhentai.net/galleries/{}/{}.jpg".format(image, i))
            with open(info[0]+("/{}.jpg".format(i)), 'wb') as saveFile:
                saveFile.write(imgFile.read())
            print("https://i.nhentai.net/galleries/{}/{}.jpg".format(image, i))
        except:
            if os.path.exists(info[0]+("/{}.png".format(i))): 
                print("Exists - " + "https://i.nhentai.net/galleries/{}/{}.png".format(image, i))
                continue
            imgFile = urlopen("https://i.nhentai.net/galleries/{}/{}.png".format(image, i))
            with open(info[0]+("/{}.png".format(i)), 'wb') as saveFile:
                saveFile.write(imgFile.read())
            print("https://i.nhentai.net/galleries/{}/{}.png".format(image, i))

    if not os.path.exists(info[0]+'.zip'):
        shutil.make_archive(info[0], 'zip', info[0])
    else:
        print('Exists - ' + info[0] + '.zip')

    print()
    itemCode += 1
