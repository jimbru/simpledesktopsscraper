#!/usr/bin/python
#
# simpledesktops.py
#
# A script to grab all the desktop images from simpledesktops.com

import feedparser
import sys
from HTMLParser import HTMLParser
from httplib import HTTPConnection
from urlparse import urlparse

RSS_FEED_URL = "feed://feeds.feedburner.com/simpledesktops"

class TagExtractor(HTMLParser):

    def __init__(self, tag, attr):
        HTMLParser.__init__(self)
        self.target_tag = tag
        self.target_attr = attr
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.handler(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.handler(tag, attrs)

    def handler(self, tag, attrs):
        if tag == self.target_tag:
            self.tags.append(self.find_attr(attrs))

    def find_attr(self, attrs):
        for attr in attrs:
            if attr[0] == self.target_attr:
                return attr[1]
        return None

    def extract(self):
        return self.tags


def scrape(path):
    cxn = HTTPConnection("simpledesktops.com")
    tx = TagExtractor("a", "href")
    page_index = 1

    while True:
        path = "/browse/" + str(page_index) + "/"
        cxn.request("GET", path)
        resp = cxn.getresponse()
        if resp.status == 404:
            break
        html = resp.read()
        html = html.replace("</scr' + 'ipt>", "") # hack around parser error
        tx.feed(html)
        page_index += 1

    cxn.close()
    tx.close()

    links = tx.extract()
    desktops = []
    for link in links:
        if link.find("static.simpledesktops.com/desktops/") != -1:
            desktops.append(link[42:])

    from pprint import pprint
    pprint(desktops)

    cxn = HTTPConnection("static.simpledesktops.com")

    for desktop in desktops:
        cxn.request("GET", "/desktops/" + desktop)
        resp = cxn.getresponse()
        image = resp.read()
        filename = desktop.rsplit("/", 1)[1]
        with open(filename, "wb") as f:
            f.write(image)


def clone(path):
    print "This feature is currently broken."
    return

    rss = feedparser.parse(RSS_FEED_URL)
    tx = TagExtractor()

    for entry in rss.entries:
        tx.feed(entry.summary)

    tx.close()

    print tx.extract()


def update(path):
    print "This feature is currently broken."
    return


def print_usage():
    print """
    simpledesktops.py -- a script to scrape simpledesktops.com

    Usage: python simpledesktops.py task [path]

    Tasks:
        scrape -- Scrape the website and download everything.
        clone  -- Download all desktops. Puts image files in 'path', if included,
                  otherwise uses present working directory. Overwrites all duplicates.
        update -- Scans for existing desktops in 'path', if included, or present
                  working directory. Downloads all new desktops more recent than the
                  most recent desktop that exists in 'path'.
    """


def main():
    try:
        task = sys.argv[1]
    except IndexError:
        print "  Error: Must include task. What do you want me to do?!"
        print_usage()
        return

    try:
        path = sys.argv[2]
    except IndexError:
        path = "" # use default

    if task == "clone":
        clone(path)
    elif task == "update":
        update(path)
    elif task == "scrape":
        scrape(path)
    else:
        print_usage()


if __name__ == "__main__":
    main()
