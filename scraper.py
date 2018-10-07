# import libraries
import sys
import urllib.request
from bs4 import BeautifulSoup

def getUrls():
    # construct url
    arguments = str(sys.argv[1])
    arguments = arguments.split(" ")
    arguments = "-".join(arguments)
    quote_page = 'https://unsplash.com/search/photos/' + arguments

    # query the website and return the html to the variable ‘page’
    page = urllib.request.urlopen(quote_page)

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')

    pictures = soup.find_all('figure')
    urls = []
    for x in range(8):
        picture = pictures[x]
        image = picture.img.findNext('img')
        src = image['src']
        urls.append(src)

    print(urls)
    return urls

if __name__ == "__main__":
    getUrls()