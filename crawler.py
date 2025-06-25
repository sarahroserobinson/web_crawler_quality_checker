import requests, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
            # Removes the first link to create the report on.
            current_url = links_to_check.pop(0)
            # Creates report instance for checking each url.
            report = WebPageReport(current_url, self.crawl_limit)
            # Saves the response time to the report.
            report.response_time = self._count_response_time(current_url)

            try:
                # Submits a HTTP request to the url and parses the response.
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, "html.parser")
                # Adds the url to the checked links list.
                checked_links.append(current_url)

                # Saves the title and word count to the report and if there is no title, adds a No title string instead.
                report.title = soup.title.string if soup.title else "No title"
                report.word_count = self._count_words(soup)
                report.image_count = self._count_images(soup)

                extracted_links = self._extract_links(soup, current_url)
                for link in extracted_links:
                    if link not in checked_links and link not in links_to_check:
                        links_to_check.append(link)

            except Exception as e:
                print(f"Error fetching {current_url}: {e}")

            # Adds the completed report to the reports list.
            self.reports.append(report)

        for link in checked_links:
            print(f"Completing quality check of: {link}")
        
        for report in self.reports:
            print(f"Page: {report.url} \nPage Title: {report.title} \nResponse time: {report.response_time} \nWord count: {report.word_count} \nImage count: {report.image_count}")

        
        return checked_links

    def _count_response_time(self, current_url):
        """Counts the time a http request to the page takes to complete."""
        start_time = time.time()
        response = requests.get(current_url)
        end_time = time.time()
        response_time = end_time - start_time
        return response_time

    def _count_words(self, soup):
        """Counts the words in the text of the page."""
        word_count = 0
        text = soup.get_text()
        for _ in text:
            word_count += 1
        return word_count
    
    def _count_images(self, soup):
        """Counts the images in the page."""
        images = soup.find_all("img")
        image_count = len(images)
        return image_count
    
    def _extract_links(self, soup, current_url):
        """Finds the links from the current page and returns them."""
        links = []
        for url in soup.findAll('a'):
            href = url.get("href")
            if href and not href.startswith(("mailto:", "javascript:", "#")):
                full_url = urljoin(current_url, href)
                links.append(full_url)
        return links



quality_checker = WebPageReport("https://developer.mozilla.org/", 10)
quality_checker.run()
