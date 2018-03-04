"""
    This program crawls information on restaurants on TripAdvisor.com
    It produces an output in with the info in csv format
    This program takes just one argument, the keyword you want to search
    on TripAdvisor. All the results are then scraped and all their subpages too.

    Written by Tomas Bortoli
"""

from sys import argv
from restaurants import *

def usage():
    print '********************************************************'
    print '*This program lets you crawl restaurants on TripAdvisor*'
    print '********************************************************'
    print 'Usage: python '+argv[0]+' <keyword>'
    print 'Example: python '+argv[0]+' Venezia'
    exit(1)

def main():
    if len(argv)!=2:
        usage()
    explore(search(argv[1]))

main()
