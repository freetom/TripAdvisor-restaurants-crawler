import requests
import sys
import json
from collections import OrderedDict

# Given a link (left,right) returns its Nth page
# TripAdvisor is crawlable by using links of the following form:
# Base link:    /Restaurants-g187870-Venice_Veneto.html
# Second page:  /Restaurants-g187870-oa20-Venice_Veneto.html
# Third page:   /Restaurants-g187870-oa40-Venice_Veneto.html
# etc
def compose(left, right, i):
    return left+'-oa'+str(i)+'-'+right

def explore(base_link):
    if base_link=='':
        print 'Can\'t explore an empty link!'
        exit(1)
    j = base_link.rindex('-')
    left = base_link[0:j]
    right = base_link[j+1:]

    # Crawl the first 20 locations from the first page results
    parse_first_result_page(base_link)

    # Crawl the rest of the locations
    i = 20
    res = True
    while res:
        r = requests.get('https://www.tripadvisor.com'+compose(left, right, i))
        if r.status_code != 200:
            res = False
        elif r.content:
            """ This two level condition differentiates searches from marco areas
            (e.g Italy, or whole regions such as Veneto, Puglia) and searches to
            cities of the like (Venice, Milan) as their results' page changes
            """
            if '<ul class="geoList">' in r.content: #macro area
                parse_result_page(r.content)
            else:                                   #micro area
                parse_restaurants(r.content, base_link)
        else:
            print 'content cannot be empty!'
            exit(1)
        i += 20

# Search a keyword on TripAdvisor and return the first link for the restaurants
def search(keyword):
    url = 'https://www.tripadvisor.com/TypeAheadJson?action=API&types=geo%2Cnbrhd%2Ceat%2Ctheme_park&filter=&legacy_format=true&urlList=true&strictParent=true&query='+keyword+'&max=6&name_depth=3&interleaved=true&scoreThreshold=0.5&strictAnd=false&typeahead1_5=true&disableMaxGroupSize=true&geoBoostFix=true&neighborhood_geos=true&details=true&link_type=hotel%2Cvr%2Ceat%2Cattr&rescue=true&uiOrigin=trip_search_Restaurants&source=trip_search_Restaurants&nearPages=true'
    r = requests.get(url)
    content = json.loads(r.content)
    for category in content[0]['urls']:
        if category['type']=='EATERY':
            return category['url']
    return ''

# Parse a field from a restaurant page (it's encoded in json in the js)
def parse_field(content, keyword):
    i = content.index(keyword)+len(keyword)
    j = content[i:].index('",')
    return content[i:i+j]

# Parse a single restaurant page and print its info
def parse_restaurant(link):
    #print link
    #   To prevent wrong links from being parsed..
    if '/Restaurant' != link[:len('/Restaurant')]:
        return
    r = requests.get('https://tripadvisor.com'+link)
    #   Temp fix to detect redirects that send us in undesired pages
    if len(r.history)>1:
        return
    if r.status_code != 200:
        print link+' returned status code '+str(r.status_code)
    else:
        content = r.content
        name = parse_field(content, '"name" : "')
        address = parse_field(content, '"streetAddress" : "')
        location = parse_field(content, '"addressLocality" : "')

        try:
            tmp = content.split('<span class="overallRating">')[1]
            rating = tmp[:tmp.index('</span>')]
        except:
            rating = 'n\\a'

        try:
            tmp = content.split('data-phonenumber="')[1]
            phone_number = tmp[:tmp.index('"')]
        except:
            phone_number = 'n\\a'

        print name+' ; '+address+' ; '+location+' ; '+rating+' ; '+phone_number
        sys.stdout.flush()

# Parse a collection of restaurants from the Nth pagparse_restaurantse of results
# N>1 (or 0 if you start counting from 0, cause the first page of res is different)
def parse_restaurants(content, link):
    #print 'Restaurant: '+link
    splice = list(set(content.split('<a target="_blank"')[1:]))
    for piece in splice:
        piece = piece[piece.index('href="')+6:]
        i = piece.index('"')
        parse_restaurant(piece[:i])

# Find all restaurants from a location page https://www.tripadvisor.com/RestaurantSearch?Action=PAGE&geo=1969509&ajax=1&sortOrder=relevance&o=a30&availSearchEnabled=false
def find_all_restaurants(link):
    #print 'Location: '+link
    i = link.index('-') + 1
    j = i+1
    while link[j]!='-':
        j += 1
    geo = link[i:j]

    #calculate max
    r = requests.get('https://tripadvisor.com'+link)
    splice = r.content.split('data-offset="')[1:]
    max_page = 0
    for piece in splice:
        num = int(piece[:piece.index('"')])
        max_page = num if num > max_page else max_page
    #print 'max for '+link+' is '+str(max_page)

    i = 0
    end = False
    while not end and i<=max_page:
        """ This query scrolls the restaurant for a certain location """
        """ Note the `geo` parameter for location and `i` for the offset"""
        endpoint = 'https://www.tripadvisor.com/RestaurantSearch?Action=PAGE&geo='+geo+'&ajax=1&sortOrder=relevance&o=a'+str(i)+'&availSearchEnabled=false'
        #print endpoint
        r = requests.get(endpoint)
        if r.status_code != 200:
            end = True
        else:
            parse_restaurants(r.content, link)
        i += 30

# Helper function
def parse(links):
    for link in links:
        find_all_restaurants(link)

# Parse geo(locations) from a result page (not the first one)
def parse_locations(content):
    ret = []
    links = content.split('href="')[1:]
    for link in links:
        tmp = link[:link.index('"')]
        ret.append( tmp )
    i = 0
    # Remove potentially unwanted link ("assertion")
    while i<len(ret):
        if '/Restaurants-g' not in ret[i]:
            ret.remove(ret[i])
        else:
            i += 1
    #for link in ret:
    #    print link
    return ret

# Parse a result page (it must not be the first one) to get the geo(locations)
def parse_result_page(content):
    splice = content.split('<ul class="geoList">')[1].split('</ul><!--/ geoList-->')[0]
    parse(parse_locations(splice))

# Parse the first page of results
def parse_first_result_page(link):
    #print 'Root page: '+link
    content = requests.get('https://www.tripadvisor.com'+link).content
    locations = content.split('<div class="geo_name">')[1:]
    for location in locations:
        tmp = location.split('<a href="')[1]
        loc = tmp[:tmp.index('"')]
        if '/Restaurants-g' not in loc:
            continue
        # Distinguish between regions and cities
        elif '_' not in loc:    #   region
            explore(loc)
        else:                   #   city
            find_all_restaurants(loc)
