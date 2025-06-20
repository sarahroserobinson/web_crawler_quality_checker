import requests, time
from bs4 import BeautifulSoup


class WebPageReport():
    """This is the class that defines the crawler, it's functions and attributes."""
    def __init__(self, url):
        """This initialises the crawler and sets out the the metrics gathered by the page report."""
        
        self.url = url 
        # Content quality metrics
        self.word_count = 0
        self.too_short = False
        self.image_count = 0
        self.missing_h1 = False

        # SEO metrics
        self.title = None
        self.title_duplicate = False

        # Performance metrics
        self.status_code = None
        self.page_size = 0
        self.response_time = 0
        
        # Link health metics
        self.broken_links = []
        self.internal_links_count = 0
        self.external_links_count = 0
    
    def run(self):
        
        self.response_time = self.count_response_time()

    def count_response_time(self):
        """Counts the time a http request to the page takes to complete."""
        start_time = time.time()
        response = requests.get(self.url)
        end_time = time.time()
        response_time = end_time - start_time
        return response_time


quality_checker = WebPageReport("https://developer.mozilla.org")
