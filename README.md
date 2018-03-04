# Restaurants crawler - Trip Advisor

This script crawls the structure of the site to get info such as `names`,`addresses`,`ratings` and `phone numbers` of **restaurants** with a search key that you provide!

## Logic

Trip Advisor's web-site is structured in a hierarchy of pages where macro areas (e.g states and regions) are located on the top of the hierarchy and micro-areas (e.g cities) at the bottom. Micro areas list restaurants in their search results whilst macro areas list locations. Then, locations might list other locations or restaurants, etc. A location is an area (macro or micro).

The program here is able to search for restaurants on the website, retrieve the link of results, scroll all the results' pages and recursively analyze them to find all child pages and all the restaurants resulting from the initial search in the end.

### Requirements
```
sudo apt install python pip
sudo pip install requests json
```

### Run

Output in **csv** format

Be aware it can run for days if you use a very generic search term..

Command to run a *detachable* task `screen -L restaurants.csv python main.py $SEARCH_TERM`

Then, remove the duplicates with `awk '!a[$0]++' restaurants.csv > unique_restaurants.csv`
