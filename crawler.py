import requests
from bs4 import BeautifulSoup


class WebPageReport():
    """This is the class that defines the crawler, it's functions and attributes"""
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


quality_checker = WebPageReport("https://developer.mozilla.org")
