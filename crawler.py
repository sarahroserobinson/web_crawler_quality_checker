import requests, time
from bs4 import BeautifulSoup


class WebPageReport():
    """This is the class that defines the crawler, it's functions and attributes."""
    def __init__(self, url, crawl_limit):
        """This initialises the crawler and sets out the the metrics gathered by the page report."""
        
        self.url = url 
        self.crawl_limit = crawl_limit
        self.reports = []

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
        """Main function that runs the crawler."""
        # Lists to store visited links and links to visit
        checked_links = []
        links_to_check = [self.url]
        # Loops through links to crawl until there are either no further links to visit or the crawl limit has been reached.
        while len(links_to_check) and len(checked_links) < self.crawl_limit:
            current_url = links_to_check.pop(0)
            report = WebPageReport(current_url, self.crawl_limit)
            report.response_time = self.count_response_time(current_url)

            try:
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, "html.parser")
                report.title = soup.title.string if soup.title else "No title"
                checked_links.append(current_url)

                
                
            except Exception as e:
                print(f"Error fetching {current_url}: {e}")

            self.reports.append(report)

        for link in checked_links:
            print(f"Completing quality check of: {link}")
        
        for report in self.reports:
            print(f"Page: {report.url} \nPage Title: {report.title} \nResponse time: {report.response_time}")

        
        return checked_links

    def count_response_time(self, current_url):
        """Counts the time a http request to the page takes to complete."""
        start_time = time.time()
        response = requests.get(current_url)
        end_time = time.time()
        response_time = end_time - start_time
        return response_time


quality_checker = WebPageReport("https://developer.mozilla.org/", 10)
quality_checker.run()
