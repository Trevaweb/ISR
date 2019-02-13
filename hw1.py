from scraper import fetchFromURL
from bs4 import BeautifulSoup 
import json
import os
import nltk
nltk.download('punkt')

def main():
    
    #downloadAllWorks()
    directory = "UnitDocumentsHTML"
    count = 0
    for subDir in os.listdir(directory):
        if count < 1:
            count1 = 0
            for fileName in os.listdir(directory + "/" + subDir):
                if count1 < 1:
                    filePath = directory + "/" + subDir + "/" + fileName
                    print(filePath)
                    f = open(filePath,"r")
                    contents = f.read()
                    soup = BeautifulSoup(contents, 'html.parser')
                    normalizedTokens = []
                    for row in soup.find_all('blockquote'):
                        #TODO: add exception for poetry all content in blockquotes not a
                        for sentence in row.find_all('a'):
                            #TODO: ignore last for sentences. They are not part of the work
                            sentenceText = sentence.text
                            #print(sentenceText)
                            tokens = nltk.word_tokenize(sentenceText)
                            #print(tokens)
                            porter = nltk.PorterStemmer()
                            for t in tokens:
                               normalizedToken = porter.stem(t)
                               normalizedTokens.append(normalizedToken)

                count1 += 1
        count += 1

    print(normalizedTokens)

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
            #jsonText = json.dumps(raw_html.decode("utf-8"))
            cwd = os.getcwd()
            #filename = cwd + "/UnitDocuments/" + page[26:] + ".json"
            
            filename = cwd + "/UnitDocumentsHTML/" + page[26:]
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename,"w") as f:
                #f.write(jsonText)
                f.write(raw_html.decode("utf-8"))
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
