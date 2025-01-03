import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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

    if resp.status != 200 or not resp.raw_response.content or resp.raw_response.content == "":
        return []
    soup = BeautifulSoup(resp.raw_response.content, "lxml")

    MIN_CHARS = 0

    pageText = soup.get_text()
    if len(pageText) == MIN_CHARS: # If page has no visible text, low information value
        return []
    

    links = [link.get('href') for link in soup.find_all('a')]
    processedLinks = []
    for link in links:
        if link:
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

        if (re.search(r"(^|\.)ics.uci.edu" 
                    + r"|(^|\.)cs.uci.edu" 
                    + r"|(^|\.)informatics.uci.edu"
                    + r"|(^|\.)stat.uci.edu", parsed.netloc)
            or re.match(r"today.uci.edu/department/information_computer_sciences", parsed.netloc)):

            if (re.search(r"\&eventdate="
                        + r"|eventdisplay="
                        + r"|ical="
                        + r"|\d{4}-\d{2}-\d{2}"
                        + r"|events.*\d{4}-\d{2}"
                        + r"|5bpartnerships_posts"
                        + r"|5bresearch_areas_ics"
                        + r"|share="
                        + r"|happening/news/filter"
                        + r"|wp-content/uploads"
                        + r"|filter\%"
                        + r"|redirect_to"
                        + r"|login"
                        + r"|input\.in"
                        + r"|files/pdf"
                        + r"|action=download", parsed.path.lower() + parsed.query.lower())):
                return False

            return not re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico|txt|rkt|nb|sas|scm|py|java|war|ss"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|ppsx"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1|bib|odc"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower() + parsed.query.lower())

        return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise