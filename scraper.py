import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

'''
    Need to check for:
        traps/infinite loops
        Possibly filter in the extract next links
        Maybe check for validity in extract next links for speed? (may not be necessary)
        Something wrong with excluding files, will need to check
'''
def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    #print("Extracting... " + str(resp.status))
    if resp.status != 200 or not resp.raw_response.content or resp.raw_response.content == "":
        return []
    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    #for link in soup.find_all('a'):
    #    print(link.get('href'))

    #Possibly use meta tags (search for robots meta tag and exclude if it has a no content)

    pageText = soup.get_text()
    if len(pageText) == 0:
        return []
    

    links = [link.get('href') for link in soup.find_all('a')]
    processedLinks = []
    for link in links:
        if link: #Possible encoding error, so far only 12 occurences in the beginning
            #print("Processing link... " + link)
            fragmentIndex = link.find("#")
            if fragmentIndex >= 0:
                processedLinks.append(link[0:fragmentIndex])
            else:
                processedLinks.append(link)
    return processedLinks


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        '''print(parsed.netloc)
        print(re.search(r"ics.uci.edu" 
                    + r"|cs.uci.edu" 
                    + r"|informatics.uci.edu"
                    + r"|stat.uci.edu", parsed.netloc))'''
        if (re.search(r"(^|\.)ics.uci.edu" 
                    + r"|(^|\.)cs.uci.edu" 
                    + r"|(^|\.)informatics.uci.edu"
                    + r"|(^|\.)stat.uci.edu", parsed.netloc)
            or re.match(r"today.uci.edu/department/information_computer_sciences", parsed.netloc)):

            if (re.search(r"\&eventDate="
                        + r"|eventDisplay=day"
                        + r"|ical="
                        #+ r"|\d{4}-\d{2}-\d{2}"
                        + r"|events.*\d{4}-\d{2}"
                        + r"|5bpartnerships_posts"
                        + r"|5bresearch_areas_ics"
                        + r"|share="
                        + r"|happening/news/filter"
                        + r"|wp-content/uploads"
                        + r"|action=login"
                        + r"|filter\%"
                        + r"|redirect_to"
                        + r"|action=download", parsed.path.lower() + parsed.query.lower())):
                return False

            return not re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|ppsx"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1|bib"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower() + parsed.query.lower())

        return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise