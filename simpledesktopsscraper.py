#!/usr/bin/python
#
# simpledesktops.py
#
# A script to grab all the desktop images from simpledesktops.com

import os.path
from cPickle import dump, load
from optparse import OptionParser
from shutil import copyfileobj
from urllib2 import HTTPError, urlopen

METADATA_FILE_NAME = ".sdscache"
CUTOFF = 50;
SCRAPE_URI = "http://simpledesktops.com/download/"

def scrape(dir=os.path.curdir, dry_run=False, force=False, verbose=False):
    metadata = []

    # read metadata cache
    if not dir:
        dir = os.path.curdir
    if not os.path.isdir(dir):
        dir = os.path.dirname(dir)

    metadata_file = os.path.join(dir, METADATA_FILE_NAME)
    if not force:
        try:
            with open(metadata_file, "rb") as f:
                metadata = load(f)
        except IOError:
            pass

    # scrape new data
    if metadata:
        last_success = metadata[-1][0]
    else:
        last_success = 0
    ii = last_success + 1

    while (ii - last_success <= CUTOFF):
        try:
            uri = SCRAPE_URI + "?desktop=" + str(ii)
            if verbose:
                print "  GET " + uri,
            resource = urlopen(SCRAPE_URI + "?desktop=" + str(ii))
        except HTTPError:
            if verbose:
                print " => 404" 
        else:
            row = (ii, resource.geturl())
            if verbose:
                print " => 200"
                print "    > " + str(row)
            metadata.append(row)
            if not dry_run:
                image_file = os.path.join(dir, os.path.basename(resource.geturl()))
                with open(image_file, "wb") as f:
                    copyfileobj(resource, f, -1)
            last_success = ii
        ii += 1

    # update metadata cache
    with open(metadata_file, "wb") as f:
        dump(metadata, f)

def main():
    usage = "Usage: %prog [options] [path]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dry-run", action="store_true", dest="dry_run")
    parser.add_option("-f", "--force", action="store_true", dest="force")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")

    (options, args) = parser.parse_args()
    try:
        path = args[0]
    except IndexError:
        path = None

    scrape(path, options.dry_run, options.force, options.verbose)

if __name__ == "__main__":
    main()
