from langchain_core.documents import Document
from langchain_community.document_loaders.url_selenium import SeleniumURLLoader
from typing import List, Tuple
import logging
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

#Modified SeleniumURLLoader class to support waiting time and recursive loads
class SeleniumURLLoaderWithWait(SeleniumURLLoader):
    def load(self, wait_time: int = 3, recursive: bool = False, paths: List = []) -> Tuple[List[Document], List[str]]:
        from unstructured.partition.html import partition_html

        start_time = time.time()
        docs: List[Document] = list()
        driver = self._get_driver()
        child_links = set()
        visited_urls = []


        def scrape_recursive(url):
            nonlocal driver
            try:
                driver.get(url)
                visited_urls.append(url)
                time.sleep(wait_time)

                page_content = driver.page_source
                soup = BeautifulSoup(page_content, 'html.parser')

                #cleans the irrelevant data
                lixos = soup.find_all(['nav', 'footer']) 
                for l in lixos:
                    l.decompose()
                cookies = soup.find_all('div', id='onetrust-consent-sdk') 
                for cookie in cookies:
                    cookie.decompose()
                
                page_content = soup.encode_contents().decode('utf-8')
                elements = partition_html(text=page_content)
                text = "   ".join([str(el) for el in elements])
                metadata = self._build_metadata(url, driver)
                docs.append(Document(page_content=text, metadata=metadata))
                print(url)

                # Get links
                base_url = urlparse(url)
                
                links = [link.get('href') for link in soup.find_all('a')]
                if '/curso/' in base_url.path: 
                    course_id = base_url.path.split('/')[-1]
                    plan = f"/pt/c/{course_id}/p"
                    links.append(f"{base_url.scheme}://{base_url.netloc}{plan}")

                # Get childs
                for link in links:
                    if link:
                        absolute_link = urljoin(base_url.geturl(), link)
                        if urlparse(absolute_link).netloc == base_url.netloc and any(p in absolute_link.split('/') for p in paths):
                            child_links.add(absolute_link)
                            if recursive and absolute_link not in visited_urls:
                                scrape_recursive(absolute_link)

            except Exception as e:
                logger.error(f"Error fetching or processing {url}, exception: {e}")
                # Restart the driver in case of session issues
                driver.quit()
                driver = self._get_driver()
                if self.continue_on_failure:
                    logger.info(f"Retrying {url} after restarting the driver.")
                    scrape_recursive(url)
                else:
                    raise e

        try:
            for url in self.urls:
                scrape_recursive(url)
        finally:
            driver.quit()
   
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to execute load: {elapsed_time:.2f} seconds")
        return docs, visited_urls

    def _get_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        # Setting driver to run on docker
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        return webdriver.Chrome(options=options)