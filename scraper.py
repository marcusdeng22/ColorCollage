# import libraries
import sys
import urllib.request
import webcolors
from bs4 import BeautifulSoup

def get_color_name(r, g, b):
    min_colors = {}
    for key, name in webcolors.css21_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - r) ** 2
        gd = (g_c - g) ** 2
        bd = (b_c - b) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def getUrls():
    # read arguments
    labels = sys.argv[1]
    #print(labels)
    rgbs = sys.argv[2]
    rgb = rgbs[0]
    rgb = rgb.split(",")
    #print(rgb)
    
    color = get_color_name(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    #print(color)

    # construct url
    quote_page = 'https://unsplash.com/search/photos/' + color + "-" + str(labels[0])
    print(quote_page)

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