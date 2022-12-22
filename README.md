# A Webcrawler

A basic webcrawler that performs these steps starting with a root url:
1. Finds all urls in the root url
2. In each of these urls, finds all urls
3. Adds all unique urls to a structure
4. Outputs 100 unique urls

## 2 Implementations

### A basic webcrawler (`basic_webcrawler.py`)
A basic implementation of a webcrawler that extracts unique urls from a starting url, and so on. 
**Features Include**
    - This crawler obeys **robots.txt** to scrape urls that can be scraped
    - This crawler makes use of a **threadpool** to maximise use of the machine's resources
    - At the end of the file `basic_webcrawler.py`, a short experiment comparing the execution times of the program with 3 different threadpool sizes are shown, and the average execution time calculated.
    - By default, the threadpool with the lowest execution time is chosen


### A pagerank webcrawler (`pagerank_webcrawler.py`)
What better way to make use of the data available with this task than to find
some way to sort these URLs in a special order. Thankfully, the pagerank algorithm exists, and is what I have chosen to use in this implementation of a webcrawler. This crawler calculates the pageranks of each url in the 100 urls. 

It then sorts the urls in descending order of its pagerank, and prints it. It also obeys **robots.txt** to ensure that a website is scraped if it is allowed, just like the *basic webcrawler* implementation.

**Features Include**
    - Obeys robots.txt to scrape urls that can be scraped
    - Keeps track of all *inbound* and *outbound* links for each url, which enables the calculation of each url's pagerank.
    - Prints the urls in decreasing order of pageranks, hence showing the url with most importance first.
