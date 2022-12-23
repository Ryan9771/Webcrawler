"""
This file is a basic implementation of a webcrawler that extracts unique urls
from a starting url, and so on. This implementation is designed to obey
robots.txt, and also implements threadpooling. For a more detailed list of 
features, feel free to check out README.md
"""

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
from robotexclusionrulesparser import RobotExclusionRulesParser
import validators


# CONSTANTS
MAX_LINKS = 100
MAX_THREADS = 5


def is_valid_url(url: str, url_set: set):
    '''
    Takes a link url, a set url_set, and returns if url is valid and not
    previously seen
    '''
    return url and validators.url(url) and url not in url_set


def web_crawl(url: str, robot: RobotExclusionRulesParser, url_set: set):
    '''
    Takes in a link (url), a robot (robot) and a set (url_set), returns 
    all contained links that are not in url_set
    '''
    # Parses the robots.txt file in the case it exists, otherwise set to None
    try:
        response = requests.get(f'{url}/robots.txt')
        robot.parse(response.text)
    except requests.exceptions.HTTPError:
        robot = None

    if robot and not robot.is_allowed('*', url):
        return []

    # Gets the webpage html and parses it with bs4
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Finds all href links in the page
    res_links = []
    for a in soup.find_all('a'):
        link = a.get('href')
        if link not in res_links and is_valid_url(link, url_set):
            res_links.append(link)

    return res_links


def main():
    # The starting url
    root_url = "https://news.ycombinator.com"

    # Initialises the urls queue, the url set and the robot class
    urls = [root_url]
    url_set = set()
    robot = RobotExclusionRulesParser()

    # Threadpooling
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        # Web crawls until the set of urls is the max size
        while (urls and len(url_set) < MAX_LINKS):
            tasks = []

            # Sends MAX_THREADS tasks at a time to execute in parallel
            for _ in range(MAX_THREADS):
                if not urls:
                    break
                url = urls.pop()
                tasks.append(executor.submit(web_crawl, url, robot, url_set))

            # Retrives all results, and flattens it into a list
            next_url_list = [task.result() for task in tasks]
            next_urls = [url for list in next_url_list for url in list]

            # Iterates through the next_urls list if it exists, and adds to the
            # set of result urls
            if next_urls:
                for next_url in next_urls:
                    if (len(url_set) == MAX_LINKS):
                        break
                    urls.append(next_url)
                    url_set.add(next_url)

    print('\n'.join(url_set))


if __name__ == "__main__":
    main()


"""
Execution times with a threadpool of 5:
    2.091s
    2.176s
    1.645s
    2.232s
    2.171s
    2.182s
    2.128s
    2.143s
    2.159s
    1.644s
    --------
    Average execution time: 2.094s

Execution times with a threadpool of 10:
    1.846s
    2.126s
    1.805s
    2.137s
    2.152s
    1.702s
    2.135s
    2.182s
    2.164s
    2.087s
    -------
    Average execution time: 2.113s

Execution times with no threadpooling:
    2.697s
    2.764s
    2.080s
    2.726s
    2.064s
    2.790s
    2.763s
    2.019s
    1.983s
    2.601s
    -------
    Average execution time: 2.6771s
"""
