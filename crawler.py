import requests, time, json, csv, datetime
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
        self.broken_links = None
        self.redirected_links = None
        self.internal_links_count = 0
        self.external_links_count = 0

    def run(self):
        """Main function that runs the crawler."""
        # Lists to store visited links and links to visit
        
        checked_links = []
        links_to_check = [self.url]
        titles = []
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
                response = requests.get(current_url, timeout=5)
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
                report.title_duplicate = self._check_for_duplicate_title(soup, titles)
                


                # Extracts the links from the current url and adds them to the links to check list.
                extracted_links = self._extract_links(soup, current_url, report)
                for link in extracted_links:
                    if link not in checked_links and link not in links_to_check:
                        links_to_check.append(link)
                
                broken_and_redirected_links = self._check_link_health(extracted_links)
                report.broken_links = broken_and_redirected_links[0]
                report.redirected_links = broken_and_redirected_links[1]

            except Exception as e:
                print(f"Error fetching {current_url}: {e}")

            # Adds the completed report to the reports list.
            self.reports.append(report)

        for link in checked_links:
            print(f"Completing quality check of: {link}")
        
        for report in self.reports:
            self._print_report(report)
        

           
        return checked_links
        
    
    def _check_if_already_visited(self, current_url, checked_links):
        """Returns boolean value depending on whether the current link has been checked before."""
        return any(link == current_url for link in checked_links)
    
    def _ask_permission_to_crawl(self, current_url):
        """Returns boolean value depending on whether robots.txt grants access to crawl the page."""
        rp = RobotFileParser()
        parsed_url = urlparse(current_url)
        robot_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp.set_url(robot_url)
        rp.read()
        return rp.can_fetch("*", current_url)
    
    def _extract_links(self, soup, current_url, report):
        """Finds the links from the current page and returns them."""
        links = []
        parsed_url = urlparse(current_url)
        domain = parsed_url.netloc
        for url in soup.findAll('a'):
            href = url.get("href")
            if href and not href.startswith(("mailto:", "javascript:", "#")):
                full_url = urljoin(current_url, href)
                links.append(full_url)

                if urlparse(full_url).netloc == domain:
                    report.internal_links_count += 1
                else:
                    report.external_links_count += 1

        return links

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
    
    def _check_for_h1(self, soup):
        """Returns boolean value depending on whether a h1 title is found."""
        return False if soup.find_all('h1') else True
    
    def _get_page_size(self, response):
        """Returns the length of bytes in the response."""
        return len(response.content)

    def _check_for_duplicate_title(self, soup, titles):
        """Returns boolean value depending on whether the title has already been used."""
        title = soup.title.string
        if title not in titles:
            titles.append(title)
            return False
        else:
            return True

    def _check_link_health(self, extracted_links):
        """Returns broken links and redirected links."""
        broken_links = []
        redirected_links = []
        for link in extracted_links[:10]:
            try:
                response = requests.get(link, stream=True, allow_redirects=False, timeout=5)
                if response.status_code >= 400 and response.status_code < 600:
                    broken_links.append(link)
                elif response.status_code >= 300 and response.status_code < 400:
                    redirected_links.append(link)
            except requests.exceptions.TooManyRedirects:
                redirected_links.append(link)
            except:
                requests.RequestException
                broken_links.append(link)
        return (broken_links, redirected_links)
    
    def _print_report(self, report):
        """Structures and prints the report."""
        print(f"Webpage Quality Report \nPage: {report.url} \nSEO \nPage title: {report.title} \nDuplicated title: {report.title_duplicate} \nContent Quality \nMissing H1 title: {report.missing_h1} \nWord count: {report.word_count} \nToo short: {report.too_short} \nImage count: {report.image_count} \nPerformance \nResponse time: {report.response_time} \nStatus code: {report.status_code} \nPage size: {report.page_size} \nLink Health \nBroken Links: {report.broken_links} \nRedirected Links: {report.redirected_links} \nNumber of external links: {report.external_links_count} \nNumber of internal links: {report.internal_links_count}")
    
    def create_filename(self):
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc.replace('.', '-')
        todays_date = datetime.datetime.now().date()
        filename = f"Quality-Report-{domain}-{todays_date}"
        return filename

    def export_as_csv(self):
        data = self.get_serialised_data()
        filename = f"{self.create_filename()}.csv"
        with open(filename, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        print(f"Data has been imported to a csv file named {filename}")
    
    def export_as_json(self):
        data = self.get_serialised_data()
        filename = f"{self.create_filename()}.json"
        with open(filename, 'w') as file:
            json.dump(data, file)
        
        print(f"Data has been imported to a json file named {filename}")

    def get_serialised_data(self):
        """Serialises all reports into dictionaries for export."""
        data = []
        for report in self.reports:
            data.append({
                "url": report.url,
                "title": report.title,
                "title_duplicate": report.title_duplicate,
                "missing_h1": report.missing_h1,
                "word_count": report.word_count,
                "too_short": report.too_short,
                "image_count": report.image_count,
                "response_time": report.response_time,
                "status_code": report.status_code,
                "page_size": report.page_size,
                "broken_links": report.broken_links,
                "redirected_links": report.redirected_links,
                "external_links": report.external_links_count,
                "internal_links": report.internal_links_count
            })
        return data
        


            

quality_checker = WebPageReport("https://developer.mozilla.org/", 10)
quality_checker.run()
quality_checker.export_as_csv()
quality_checker.export_as_json()