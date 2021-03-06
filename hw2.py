'''
Trevor Weber
ISR
hw2
Mar 21, 2019
'''
from scraper import fetchFromURL
from bs4 import BeautifulSoup 
import json
import os
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')
def main():
    customStopWords = [",",";",".",":","!","?",
                    "'s","'d","thou","thy","'",
                    "thee","--","hath","let","'ll"]
    stopWords = set(stopwords.words('english') + customStopWords)
    downloadAllWorks()
    print("Processing Unit Documents...")
    directory = "UnitDocumentsHTML"
    termIndex = {}
    #run through all the downloaded files
    for subDir in os.listdir(directory):
        for fileName in os.listdir(directory + "/" + subDir):
            filePath = directory + "/" + subDir + "/" + fileName
            #filePath = "UnitDocumentsHTML/Poetry/LoversComplaint.html"
            #print(filePath)
            f = open(filePath,"r")
            contents = f.read()
            f.close()
            soup = BeautifulSoup(contents, 'html.parser')
            #for each file find all the text
            for row in soup.find_all('blockquote'):
                #poetry is laid out diffrently so make an exception
                if "Poetry" in filePath:
                    sentenceText = row.text.lower()
                    #print(sentenceText)
                    #tokenize the sentence
                    tokens = nltk.word_tokenize(sentenceText)
                    termDict = generateTermDict(tokens,termIndex,fileName)
                else:
                    scene = row.find_all('a')
                    counter = 0
                    for sentence in scene:
                        #ignore the last 4 sentences
                        #they are not part of the scene
                        if counter < len(scene) - 4:
                            sentenceText = sentence.text.lower()
                            #print(sentenceText)
                            tokens = nltk.word_tokenize(sentenceText)
                            termDict = generateTermDict(tokens,termIndex,fileName)
                            #print(tokens)
                            counter += 1
    
    bigramIndex = createBigramIndex(termIndex)
    
    writeToJSON(termIndex,"TermIndex.json")
    writeToJSON(bigramIndex,"BigramIndex.json")
    #wait for user queries
    while(1):
        #get user query
        userQuery = input("\nEnter a search term or type \"exit\" to exit: ")
        if userQuery == "exit":
            return 
        #normalize token
        porter = nltk.PorterStemmer()
        normalizedQuery = porter.stem(userQuery.lower())
        #check if query is in stop list
        if normalizedQuery in stopWords:
            print("\nThe term \"" + userQuery + "\" is too common to be searched for.\nPlease try again.\n")

        #elseif query in inverted index
        elif normalizedQuery in termIndex:
            postingList = termIndex[normalizedQuery]
            count = 0
            #return formatted posting
            print("The term \"" + userQuery + "\" is found in the following documents:\n*****************************************************")
            for posting in postingList:
                #ignore the first posting as its the freq
                if count > 0:
                    print(posting)
                count += 1

        #else check for spelling corrections
        else:
            userQueryList = []
            userQueryList.append(userQuery)
            queryBigrams = createBigramIndex(userQueryList)
            associatedTermsList = []
            correctedTerms = []
            #for bigram in querybigrams
            for bigram in queryBigrams:
                if bigram in bigramIndex:
                    associatedTerms = bigramIndex[bigram]
                    associatedTermsList.extend(associatedTerms)
            #create set of terms associated with bigram from bigram index
            associatedTermsSet = set(associatedTermsList)
            #for terms, calc the jaccard coefficient against query
            for term in associatedTermsSet:
                termSet = set(term)
                querySet = set(userQuery)
                jDistance = nltk.jaccard_distance(termSet,querySet)
                #if within threshold, add to spelling corrected list
                if round(jDistance,2) <= 0.25:
                    correctedTerms.append(term)

            if len(correctedTerms) == 0:
                print("The term \"" + userQuery + "\" is too vague to be searched for.\nPlease try again.\n")
            else:
                #return spelling correct list
                print("The term \"" + userQuery +  "\" could not be found. Did you mean:\n*************************************************")
                for correctedTerm in correctedTerms:
                    print(correctedTerm)


def writeToJSON(data,fileName):

    cwd = os.getcwd()
    filePath = cwd + "/Output/" + fileName
    os.makedirs(os.path.dirname(filePath),exist_ok=True)
    
    with open(filePath,"w") as outputFile:
        json.dump(data,outputFile)
        
        #Pretty Print
        #json.dump(data,outputFile,indent=4)

    return

def createBigramIndex(termIndex):

    bigramIndex = {}
    for term in termIndex:
        bigramList = nltk.bigrams(term)
        count = 1
        for bigram in bigramList:
            #bigram -> ["a","b"]
            if count == 1:
                bigramString = "$" + str(bigram[0]) + str(bigram[1])
            
            elif count == len(str(term)) - 1:
                bigramString = str(bigram[0]) + str(bigram[1]) + "$"
            
            else:        
                bigramString = str(bigram[0]) + str(bigram[1])
            count += 1
            
            if bigramString not in bigramIndex:
                termList = [term]
                bigramIndex[bigramString] = termList
            else:
                bigramIndex[bigramString].append(term)
        else:
            exit
            
    return bigramIndex

def generateTermDict(tokens,termIndex,fileName):
    
    customStopWords = [",",";",".",":","!","?",
                    "'s","'d","thou","thy","'",
                    "thee","--","hath","let","'ll"]
    stopWords = set(stopwords.words('english') + customStopWords)
    porter = nltk.PorterStemmer()
    
    for t in tokens:
        #if the word isnt a stop word 
        #normalize it and add it to the dict
        if t not in stopWords:
            normalizedToken = porter.stem(t)
            keyList = []
            #add token if not there, increase freq, add document found in
            if normalizedToken not in termIndex:
                #print(normalizedToken + " not in bigram")
                keyList = [1,fileName]
                termIndex[normalizedToken] = keyList
            #otherwise it is there so increase freq and add new document
            elif normalizedToken in termIndex:
                #print(normalizedToken + " in bigram")
                #print(keyList)
                keyList = termIndex[normalizedToken]
                keyList[0] += 1
                #dont want repeat document IDs
                if fileName not in keyList:
                    keyList.append(fileName)
                termIndex[normalizedToken] = keyList

    return termIndex

def downloadAllWorks():
    print("Downloading Unit Documents...")

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
            cwd = os.getcwd()
            filename = cwd + "/UnitDocumentsHTML/" + page[26:]
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            #copy the html text to a file
            with open(filename,"w") as f:
                f.write(raw_html.decode("utf-8"))
            f.close()
    return

def get_works_urls(target):

    soup = BeautifulSoup(target, 'html.parser')
    targeturls = []
    for row in soup.find_all('td'):
        for link in row.find_all('a'):
            linkString = link.get('href')
            if linkString != "http://tech.mit.edu/" and linkString != "http://www.python.org/~jeremy/":
                targeturls.append(linkString)
            
    return targeturls

def get_scene_urls(target,baseURL):

    soup = BeautifulSoup(target, 'html.parser')
    targeturls = []
    for row in soup.find_all('p'):
        for link in row.find_all('a'):
            linkString = link.get('href')
            if "amazon" not in linkString and "full" not in linkString:
                targeturls.append(baseURL + "/" + linkString)

    return targeturls

def get_sonnet_urls(target,baseURL):

    soup = BeautifulSoup(target, 'html.parser')
    targeturls = []
    for row in soup.find_all('dl'):
        for link in row.find_all('a'):
            linkString = link.get('href')
            if "amazon" not in linkString:
                targeturls.append(baseURL[0:-13] + "/" + linkString)
            
    return targeturls

main()
