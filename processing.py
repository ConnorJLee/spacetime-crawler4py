import re
from urllib.parse import urlparse

def processWords():
    wordDict = dict()
    urlFreq = dict()
    totalUrls = 0
    stopwords = {'any', 'their', "when's", 'themselves', "don't", 'while', "there's", 'them', 'have', 'but', 'no', 'do', 'if', 'having', "i've", 'be', 'yourself', "couldn't", 'into', 'nor', "he'd", "you're", 'are', "we'll", 'ought', "doesn't", 'under', 'they', 'too', 'our', 'down', 'all', 'did', 'and', 'both', 'does', "weren't", 'each', 'there', 'from', 'she', 'could', "they'd", "wouldn't", "hasn't", 'below', 'other', 'yourselves', 'your', 'am', 'off', 'in', "she'll", 'then', "how's", "you'd", 'this', 'most', 'being', 'few', "he's", 'not', 'he', "can't", 'as', "you'll", "wasn't", 'once', 'on', "didn't", "who's", 'that', 'myself', 'it', "hadn't", 'during', 'further', 'doing', 'how', 'of', "shan't", 'through', 'would', 'i', "they'll", 'again', 'has', "we'd", 'cannot', 'these', 'was', 'ours\tourselves', 'above', 'him', 'you', 'after', 'me', 'before', 'between', 'been', 'same', 'theirs', 'whom', "won't", "let's", 'to', 'very', 'such', 'or', 'so', "aren't", 'those', "what's", 'who', 'which', 'against', 'hers', 'over', 'by', "we're", "it's", "she'd", 'should', 'a', 'where', "she's", 'what', "haven't", 'yours', 'because', 'his', 'why', 'were', 'is', 'its', "we've", 'own', 'at', 'only', "he'll", "you've", "here's", "i'd", "i'm", 'here', "that's", "they're", 'up', 'her', 'itself', 'than', 'until', 'about', "why's", "shouldn't", 'herself', 'we', 'the', 'my', "i'll", 'out', "isn't", "where's", 'had', "they've", 'when', "mustn't", 'for', 'an', 'some', 'himself', 'more', 'with'}
    with open("downloadPageReal1.txt", "r", encoding="utf8") as file:
        text = file.read()
        text = text.split("#3e5d3752-f4a1-4417-a0ea-631ac7b91200#")
        for i in range(1, len(text)-1, 2): #Exclude first split since there was nothing before it
            url = text[i].strip()
            if url:
                domain = urlparse(url).netloc
                if re.match("www\.", domain):
                    domain = domain[4:]
                if domain not in urlFreq:
                    urlFreq[domain] = 1
                else:
                    urlFreq[domain] += 1
            
            line = text[i+1].strip()
            for word in line.split():
                if word and word not in stopwords and len(word) > 1:
                    word = word.lower()
                    if word not in wordDict:
                        wordDict[word] = 1
                    else:
                        wordDict[word] += 1
            totalUrls += 1

    print(totalUrls)
    print(len(urlFreq))
    return wordDict, urlFreq

def processWorkerLog():
    longest = ["", -1]
    with open("WorkerReal1.txt", "r", encoding="utf8") as file:
        for line in file:
            textWords = re.findall("NumWords=\d*", line)
            #textWords = re.findall("PageLen=\d*", line)
            if textWords:
                numWords = int(textWords[0][9:])
                #numWords = int(textWords[0][8:])
                if numWords > longest[1]:
                    longest[0] = line
                    longest[1] = numWords

    return longest
    


if __name__ == "__main__":
    processed = processWords()
    processedWords = processed[0]
    processedUrls = processed[1]
    
    words = sorted(processedWords.items(), key = lambda item : -1 * item[1])
    print(words[:50])
    print()
    print(sorted(processedUrls.items(), key = lambda item : item[0]))
    print()
    print(processWorkerLog())
