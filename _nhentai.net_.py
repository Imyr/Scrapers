from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import shutil
import time
import re
import os


def pageParser(Link):
    
    grabbedPage = requests.get(Link)
    return (BeautifulSoup(grabbedPage.content, 'html.parser'))

def infoScraper(itemCode):

    grabbedPage = requests.get("https://nhentai.net/g/{}".format(itemCode))
    print(grabbedPage.status_code)
    if grabbedPage.status_code == 429:
      print('Retrying info page grab (429)')
      return('e429')
    parsedPage = BeautifulSoup(grabbedPage.content, 'html.parser')
    textPage = str(parsedPage.get_text())
    if not (('Languages:\n\t\t\t\t\t\t\t\ttranslated' in textPage) or ('Languages:\n\t\t\t\t\t\t\t\tenglish' in textPage)):
      return ('lang')
    if 'chinese' in textPage:
      return ('lang')
    if 'yaoi' in textPage:
      return ('seku')
    mangaTitle = re.search(r'">(.*)<', str(parsedPage.find_all('span', 'before')[0])).group(1) + re.search(r'">(.*)<', str(parsedPage.find_all('span', 'pretty')[0])).group(1) + re.search(r'">(.*)<', str(parsedPage.find_all('span', 'after')[0])).group(1)
    mangaPages = re.search(r'Pages:\n\t\t\t\t\t\t\t\t(.*)\n\t\t\t\t\t\t\t\tUploaded:', parsedPage.get_text()).group(1)

    print('{} - {}'.format(itemCode, mangaTitle))
    print(mangaPages + ' pages')
    
    return (mangaTitle, mangaPages)

def idScraper(itemCode):

    grabbedPage = requests.get("https://nhentai.net/g/{}/1/".format(itemCode))
    print(grabbedPage.status_code)
    if grabbedPage.status_code == 429:
      print('Retrying id page grab (429)')
      return('e429')
    parsedPage = BeautifulSoup(grabbedPage.content, 'html.parser')
    try: 
      imageId = re.search(r'https://i.nhentai.net/galleries/(.*)/1.jpg', str(parsedPage)).group(1)
      print(imageId)
    except:
        try: 
          imageId = re.search(r'https://i.nhentai.net/galleries/(.*)/1.png', str(parsedPage)).group(1)
          print(imageId)
        except:
          imageId = re.search(r'https://i.nhentai.net/galleries/(.*)/1.gif', str(parsedPage)).group(1)
          print(imageId)

    return (imageId)

itemCode = 300000

while True:
    itemCode -= 1
    check = requests.get('https://nhentai.net/g/{}/'.format(itemCode))
    if check.status_code == 404:
        print(str(itemCode) + ' not found.\n')
    if check.status_code == 429:
        itemCode += 1
        print('Retrying main page grab (429)')
        time.sleep(1)
        continue
    else:
        info = infoScraper(itemCode)
        if info == 'lang':
          print(str(itemCode) + " isn't English.\n")
          continue
        if info == 'seku':
          print(str(itemCode) + " is Yaoi.\n")
          continue
        if info == 'e429':
          itemCode += 1
          time.sleep(1)
          continue
        image = idScraper(itemCode)
        if image == 'e429':
          itemCode += 1
          time.sleep(1)
          continue
        

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
              try:      
                  if os.path.exists(info[0]+("/{}.png".format(i))): 
                      print("Exists - " + "https://i.nhentai.net/galleries/{}/{}.png".format(image, i))
                      continue
                  imgFile = urlopen("https://i.nhentai.net/galleries/{}/{}.png".format(image, i))
                  with open(info[0]+("/{}.png".format(i)), 'wb') as saveFile:
                      saveFile.write(imgFile.read())
                  print("https://i.nhentai.net/galleries/{}/{}.png".format(image, i))
              except:
                  if os.path.exists(info[0]+("/{}.gif".format(i))): 
                      print("Exists - " + "https://i.nhentai.net/galleries/{}/{}.gif".format(image, i))
                      continue
                  imgFile = urlopen("https://i.nhentai.net/galleries/{}/{}.gif".format(image, i))
                  with open(info[0]+("/{}.gif".format(i)), 'wb') as saveFile:
                      saveFile.write(imgFile.read())
                  print("https://i.nhentai.net/galleries/{}/{}.gif".format(image, i))
        if not os.path.exists('drive/Shareddrives/Scrapes/NHentaiArchives/' + info[0] + '/' + str(itemCode)+'.zip'):
            shutil.make_archive('drive/Shareddrives/Scrapes/NHentaiArchives/' + info[0] + '/' + str(itemCode), 'zip', info[0])
        else:
            print('Exists - ' + info[0] + '.zip')

        print()
