#!/usr/bin/python
#
# simpledesktops.py
#
# A script to grab all the desktop images from simpledesktops.com

import sys
from HTMLParser import HTMLParser
from httplib import HTTPConnection

class LinkExtractor(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.handler(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.handler(tag, attrs)

    def handler(self, tag, attrs):
        if tag == "a":
            self.tags.append(self.find_href(attrs))

    def find_href(self, attrs):
        for attr in attrs:
            if attr[0] == "href":
                return attr[1]
        return None

    def extract(self):
        return self.tags


def clone(path):
    cxn = HTTPConnection("simpledesktops.com")
    lx = LinkExtractor()
    page_index = 1

    while True:
        path = "/browse/" + str(page_index) + "/"
        cxn.request("GET", path)
        resp = cxn.getresponse()
        if resp.status == 404:
            break
        html = resp.read()
        html = html.replace("</scr' + 'ipt>", "") # hack around parser error
        lx.feed(html)
        page_index += 1

    cxn.close()
    lx.close()

    links = lx.extract()
    desktops = []
    for link in links:
        if link.find("static.simpledesktops.com/desktops/") != -1:
            desktops.append(link[42:])

    cxn = HTTPConnection("static.simpledesktops.com")

    for desktop in desktops:
        cxn.request("GET", "/desktops/" + desktop)
        resp = cxn.getresponse()
        image = resp.read()
        filename = desktop.rsplit("/", 1)[1]
        with open(filename, "wb") as f:
            f.write(image)


def update(path):
    print "This feature is currently broken."
    return


def print_usage():
    print """
    simpledesktops.py -- a script to scrape simpledesktops.com

    Usage: python simpledesktops.py task [path]

    Tasks:
        clone  -- Download all desktops. Puts image files in 'path', if included,
                  otherwise uses present working directory. Overwrites all duplicates.
        update -- Scans for existing desktops in 'path', if included, or present
                  working directory. Downloads all new desktops more recent than the
                  most recent desktop that exists in 'path'.

    Note: "Path" argument is currently broken in all modes. Deal with it.
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
    else:
        print_usage()


if __name__ == "__main__":
    main()
