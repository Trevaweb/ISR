from scraper import fetchFromURL
from bs4 import BeautifulSoup 
import json
import os

def main():
    
    downloadAllWorks()


def downloadAllWorks():

    baseurl = 'http://shakespeare.mit.edu'
    raw_html = fetchFromURL(baseurl) 
    targeturls= []
    targeturls = get_works_urls(raw_html)
    newTargetURLS = []

    #for each link in the homepage go to it and get the links from the next page
    for item in targeturls:
        newTargetURLSTemp = []
        if "sonnets" in item:
            url = baseurl + "/" + item
            raw_html = fetchFromURL(url)
            newTargetURLSTemp = get_sonnet_urls(raw_html,url)
            newTargetURLS.append(newTargetURLSTemp)
        elif "Poetry" in item:
            url = baseurl + "/" + item
            newTargetURLS.append([url])
        else:
            url = baseurl + "/" + item[0:-11]
            raw_html = fetchFromURL(url)
            newTargetURLSTemp = get_scene_urls(raw_html,url)
            newTargetURLS.append(newTargetURLSTemp)
    for work in newTargetURLS:
        for page in work:
            raw_html = fetchFromURL(page)
            jsonText = json.dumps(raw_html.decode("utf-8"))
            cwd = os.getcwd()
            filename = cwd + "/UnitDocuments/" + page[26:] + ".json"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename,"w") as f:
                f.write(jsonText)
            f.close()

    return

def get_works_urls(target):

    """

    Example of isolating different parent elements to gather subsequent URLs

    """

    soup = BeautifulSoup(target, 'html.parser')
    targeturls = []
    #print(soup.prettify())
    for row in soup.find_all('td'):

        for link in row.find_all('a'):
            linkString = link.get('href')
            if linkString != "http://tech.mit.edu/" and linkString != "http://www.python.org/~jeremy/":
                targeturls.append(linkString)
            
    return targeturls

def get_scene_urls(target,baseURL):

    """

    Example of isolating different parent elements to gather subsequent URLs

    """

    soup = BeautifulSoup(target, 'html.parser')
    targeturls = []
    #print(soup.prettify())
    for row in soup.find_all('p'):

        for link in row.find_all('a'):
            linkString = link.get('href')
            if "amazon" not in linkString and "full" not in linkString:
                targeturls.append(baseURL + "/" + linkString)
            
    return targeturls

def get_sonnet_urls(target,baseURL):

    """

    Example of isolating different parent elements to gather subsequent URLs

    """

    soup = BeautifulSoup(target, 'html.parser')
    targeturls = []
    #print(soup.prettify())
    for row in soup.find_all('dl'):
        for link in row.find_all('a'):
            linkString = link.get('href')
            if "amazon" not in linkString:
                targeturls.append(baseURL[0:-13] + "/" + linkString)
            
    return targeturls

main()
