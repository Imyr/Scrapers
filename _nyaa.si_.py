from bs4 import BeautifulSoup
import mysql.connector as sqlconn
import requests  
import re

sqlclient = sqlconn.connect(
                            host = 'localhost',
                            user = 'root',
                            passwd = 'root',
                            database = 'nyaa'
                            )

if sqlclient.is_connected():
    print('Database connected.')

sqlcrsr = sqlclient.cursor()

def parsedPage(Link):
    grabbedPage = requests.get(Link)
    return (BeautifulSoup(grabbedPage.content, 'html.parser'))

idResult = 885087

while True:

    idResult += 1
    
    page = str(parsedPage("https://nyaa.animania.cf/view/{}".format(idResult)))
    
    if "<h1>404 Not Found</h1>" in page:
        print(idResult, "doesn't exist.")
        continue
    
    print(idResult)

    titleResult = re.search(r'<h3 class="panel-title">\n(.*)\n', page)
    if titleResult == None:
        title = "parse_error"
    else:
        title = titleResult.group(1)
    print (title)

    userResult = re.search(r'href="/user/(.*)" title="', page)
    if userResult == None:
        user = "Anonymous"
    else:
        user = userResult.group(1)
    print (user)

    sizeResult = re.search(r'<div class="col-md-1">File size:</div>\n<div class="col-md-5">(.*)</div>', page)
    if sizeResult == None:
        size = "parse_error"
    else:
        size = sizeResult.group(1)
    print (size)    
    
    datetimeResult = re.search(r'<div class="col-md-5" data-timestamp="(.*) UTC</div>', page)
    if datetimeResult == None :
        datetime = "parse_error"
    else:
        datetime = datetimeResult.group(1)
    print (datetime[12:])
    
    infoHashResult = re.search(r'<div class="col-md-5"><kbd>(.*)</kbd></div>', page)
    if infoHashResult == None:
        infoHash = "parse_error"
    else:
        infoHash = infoHashResult.group(1)
    print (infoHash)

    if title == "parse_error":
        idResult -= 1
        continue
    
    if '"' in title:
        feed = "INSERT INTO nyaa VALUES ({},'{}','{}','{}','{}','{}')".format(idResult, title, user, size, datetime[12:]+":00", infoHash)
    else:              
        feed = 'INSERT INTO nyaa VALUES ({},"{}","{}","{}","{}","{}")'.format(idResult, title, user, size, datetime[12:]+":00", infoHash)

    print(feed)
    
    sqlcrsr.execute(feed)

    sqlclient.commit()

    print("Done.")
