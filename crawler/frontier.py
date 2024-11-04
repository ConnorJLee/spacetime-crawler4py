import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty
from time import time, sleep
from re import match, findall

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = {".*(\.|\/)ics.uci.edu" : list(),
                                 ".*(\.|\/)cs.uci.edu" : list(),
                                 ".*(\.|\/)informatics.uci.edu" : list(),
                                 ".*(\.|\/)stat.uci.edu" : list(),
                                 "#other#" : list()}
        self.last_popped = {".*(\.|\/)ics.uci.edu" : time(),
                            ".*(\.|\/)cs.uci.edu" : time(),
                            ".*(\.|\/)informatics.uci.edu" : time(),
                            ".*(\.|\/)stat.uci.edu" : time(),
                            "#other#" : time()}
        
        self.rLock = RLock()
        self.saveLock = RLock()

        self.workerStatus = [True for i in range(self.config.threads_count)]
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

        #print(self.to_be_downloaded)

    def _storeUrl(self, url):
        matched = False
        for domain in self.to_be_downloaded.keys():
            if match(domain, url):
                self.to_be_downloaded[domain].append(url)
                matched = True
        if not matched:
            self.to_be_downloaded["#other#"].append(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self._storeUrl(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        with self.rLock:
            while True:
                try:
                    currentTime = time()
                    emptyLists = 0
                    for domain, lastTime in self.last_popped.items():
                        if (currentTime - lastTime > self.config.time_delay 
                            and self.to_be_downloaded[domain]):
                            self.last_popped[domain] = time()
                            return self.to_be_downloaded[domain].pop()
                        elif not self.to_be_downloaded[domain]:
                            emptyLists += 1
                    
                    #Need to tell worker when to wait in case not all urls gotten, may not be necessary
                    if emptyLists == len(self.to_be_downloaded):
                        return None
                except IndexError:
                    return None
                
                sleep(self.config.time_delay / 2)

    def add_url(self, url):
        with self.rLock:
            url = normalize(url)
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                self._storeUrl(url)
                self.workerStatus = [True for i in range(self.config.threads_count)]
    
    def mark_url_complete(self, url):
        with self.rLock:
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = (url, True)
            self.save.sync()

    def isDone(self, workerId):
        with self.rLock:
            self.workerStatus[workerId] = False
            return not any(self.workerStatus)
        # once all false then log something? maybe process stored URLs (for subdomain # pages -> self.save.values())
        # gives unique number of pages
        # urlparse -> url.netloc = subdomain counter thingy
        # also count total amount of unique links visited (values totaled up or just count as you process ?)
        # make ics.uci.edu and www.ics.uci.edu the same subdomain ~ remove www. -> say that in comments for TAs?

    def savePage(self, url, pageContent):
        with self.saveLock:
            with open("downloadPage.txt", "a") as pageFile:
                pageFile.write("#3e5d3752-f4a1-4417-a0ea-631ac7b91200#" + 
                                url +"#3e5d3752-f4a1-4417-a0ea-631ac7b91200#" + "\n" + 
                                " ".join(pageContent) + "\n\n")

    # processPage?
        # maybe keep track of subdomains?
        # Tokens are alphanumeric but can include hyphens/apostrophes. Use regex?
        # [a-zA-Z0-9]*(\'|\-)*[a-zA-Z0-9]*|\(\d{3}\) \d{3}-\d{4}