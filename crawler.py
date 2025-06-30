import requests, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser



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
        
        # Link health metrics
        self.broken_links = []
        self.internal_links_count = 0
        self.external_links_count = 0
    
    def run(self):
        """Main function that runs the crawler."""
        # Lists to store visited links and links to visit
        
        checked_links = []
        links_to_check = [self.url]
        # Loops through links to crawl until there are either no further links to check or the crawl limit has been reached.
        while len(links_to_check) and len(checked_links) < self.crawl_limit:
            # Removes the first link to create the report on.
            current_url = links_to_check.pop(0)
            # Creates report instance for checking each url.

            if self._check_if_already_visited(current_url, checked_links):
                continue 
            
            if not self._ask_permission_to_crawl(current_url):
                print(f"Permission denied by robots.txt. Unable to crawl: {current_url}")
                continue

            report = WebPageReport(current_url, self.crawl_limit)

            try:
                # Submits a HTTP request to the url and parses the response. Saves the response time to the report.
                start_time = time.time()
                response = requests.get(current_url)
                end_time = time.time()
                report.response_time = end_time - start_time

                soup = BeautifulSoup(response.text, "html.parser")
                # Adds the url to the checked links list.
                checked_links.append(current_url)

                # Saves metrics to the report
                report.title = soup.title.string if soup.title else "No title"
                report.missing_h1 = self._check_for_h1(soup)
                report.word_count = self._count_words(soup)
                report.too_short = True if report.word_count < 100 else False
                report.image_count = self._count_images(soup)
                report.status_code = f"{response.status_code} {response.reason}"
                report.page_size = self._get_page_size(response)

                # Extracts the links from the current url and adds them to the links to check list.
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
            print(f"Webpage Quality Report \nPage: {report.url}\n SEO \nPage Title: {report.title} \nContent Quality \nMissing H1 Title: {report.missing_h1} \nWord count: {report.word_count} \nToo short: {report.too_short} \nImage count: {report.image_count} \nPerformance \nResponse time: {report.response_time} \nStatus code: {report.status_code} \nPage size: {report.page_size} \nLink Health \n")

        
        return checked_links
    
    def _check_if_already_visited(self, current_url, checked_links):
        return any(link == current_url for link in checked_links)

    def _count_words(self, soup):
        """Counts the words in the text of the page."""
        word_count = 0
        text = soup.get_text()
        split_words = text.split()
        for _ in split_words:
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
    
    def _ask_permission_to_crawl(self, current_url):
        rp = RobotFileParser()
        parsed_url = urlparse(current_url)
        robot_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp.set_url(robot_url)
        rp.read()
        return rp.can_fetch("*", current_url)
    
    def _check_for_h1(self, soup):
        return False if soup.find_all('h1') else True
    
    def _get_page_size(self, response):
        return len(response.content)





quality_checker = WebPageReport("https://developer.mozilla.org/", 10)
quality_checker.run()
