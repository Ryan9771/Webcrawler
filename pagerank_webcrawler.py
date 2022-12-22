"""
This implementation of a webcrawler is one that makes use of data, the 
collected urls, to calculate the pageranks of each url in the MAX_LINKS urls. It then 
sorts the urls in descending order of its pagerank, and prints it. Use of 
comments wherever possible was done to make the code's purpose clear to the 
evaluator.

This implementation also follows a website's robots.txt, just like the basic
webcrawler implementation.

Since this implementation involves the creation and repeated iteration of 
dictionaries to calculate pagerank, it is slower than the basic implementation 
of the webcrawler. Possible room for improvements could be to optimise the space 
complexity and to use multithreading to divide up tasks.
"""

from bs4 import BeautifulSoup
import numpy as np
import requests
from robotexclusionrulesparser import RobotExclusionRulesParser
import validators


# CONSTANTS
MAX_LINKS = 100
CONVERGENCE_DELTA = 0.001
MAX_PAGERANK_ITERATIONS = 200


def is_valid_url(url: str):
    '''
    Takes a link url, and returns if url is valid
    '''
    return url and validators.url(url)
    

def web_crawl(url: str, robot: RobotExclusionRulesParser):
    '''
    Takes in a url, a robot result and returns all links in the url
    '''
    if not robot or not robot.is_allowed('*', url):
        return []

    # Gets the webpage html and parses it with bs4
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Finds all href links in the page
    res_links = []
    for a in soup.find_all('a'):
        link = a.get('href')
        if is_valid_url(link):
            res_links.append(link)

    return res_links



def main():
    # Stores the unique websites that has been visited, along with its 
        # inbound and outbound links
    webpages = {}

    # The starting url 
    root_url = "https://news.ycombinator.com"
    webpages[root_url] = {
        'inbound_links': 1,
        'outbound_links': []
    }

    # Initialises the queue with the first link, and initalises the robot object
    queue = [root_url]
    robot = RobotExclusionRulesParser()

    # Webcrawls urls in the queue until the list of unique websites is the max
        # The plus 1 is to account for the root_url already in the urls set
    while (queue and len(webpages) < MAX_LINKS + 1):
        next_link = queue.pop()

        # Parses the robots.txt file, if it exists
        try:
            response = requests.get(f"{next_link}/robots.txt")
            robot.parse(response.text)
        except requests.exceptions.HTTPError:
            robot = None

        # Gets the list of valid links in the url and sets the outbound links
            # of that url to the list of links
        next_urls = web_crawl(next_link, robot)
        webpages[next_link]['outbound_links'] = next_urls

        if next_urls:
            for url in next_urls:
                if len(webpages) == MAX_LINKS + 1:
                    break 

                # The url is a new unique url: add to queue and webpages
                if url not in webpages:
                    queue.append(url)
                    webpages[url] = {
                        'inbound_links': 1,
                        'outbound_links': []
                    }
                # The url is seen again, increment the inbound links of that url
                else:
                    webpages[url]['inbound_links'] += 1 

    # Initialises pageranks (pr) of each webpage to 1 
    for webpage in webpages:
        webpages[webpage]['pr'] = 1.0

    # Applies the pagerank algorithm to convergence, or max 200 iterations
    converged = False
    iterations = 0
    while not converged and iterations < MAX_PAGERANK_ITERATIONS:
        iterations += 1

        # Computes the sum of the prs of the inbound links for each webpage
        for webpage in webpages:
            sum = 0.0
            for inbound_link in webpages:
                if webpage in webpages[inbound_link]['outbound_links']:
                    sum += webpages[inbound_link]['pr'] / len(webpages[inbound_link]['outbound_links'])
                    webpages[webpage]['new_pr'] = sum
        
        # Tests convergence of all prs
        delta = 0
        for webpage in webpages:
            delta += abs(webpages[webpage]['pr'] - webpages[webpage]['new_pr'])

        if delta < CONVERGENCE_DELTA:
            converged = True 
        else:
            for webpage in webpages:
                webpages[webpage]['pr'] = webpages[webpage]['new_pr']

    # Normalises the pageranks
    pageranks = np.array([webpages[webpage]['pr'] for webpage in webpages])
    pageranks /= pageranks.sum()

    # Creates a [(url, pagerank)] list to print
    pagerank_pairs = []
    i = 0
    for webpage in webpages:
        pagerank_pairs.append((webpage, pageranks[i]))
        i += 1

    # Sort the webpages by pagerank
    sorted_webpages = sorted(pagerank_pairs, key = lambda x: x[1], reverse = True)

    # Prints webpages in order of decreasing pagerank, excluding the root url
    for (url, num) in sorted_webpages:
        if url == root_url:
            continue
        print(f"URL: {url} || (PageRank: {num:.4f})")
            

if __name__ == "__main__":
    main()
    

