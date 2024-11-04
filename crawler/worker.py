from threading import Thread

from bs4 import BeautifulSoup
from inspect import getsource
from utils.download import download
from utils import get_logger
from re import findall
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.workerId = worker_id
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                if (not self.frontier.isDone(self.workerId)):
                    time.sleep(self.config.time_delay)
                    continue
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            if (resp.status == 200):
                soup = BeautifulSoup(resp.raw_response.content, "lxml")
                pageText = soup.get_text()
                words = findall(r"[a-zA-Z0-9]+[\'|\-]{,1}[a-zA-Z0-9]*", pageText)
                if len(pageText) > 0:
                    self.logger.info(tbd_url + ": NumWords=" + str(len(words)))
                    self.frontier.savePage(tbd_url, words)
                    pass
                    
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        
