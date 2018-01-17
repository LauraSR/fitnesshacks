#!/usr/bin/env python
#
# file: tcx.py
#
# description: functions to parse garmin tcx files
#
# usage: import in other scripts
#
# requires: ElementTree, BeautifulSoup
#
# author: jake hofman (gmail: jhofman)
#

from xml.etree.ElementTree import fromstring
from time import strptime, strftime
from optparse import OptionParser
import sys
import re


def findtext(e, name, default=None):
    """
    findtext

    helper function to find sub-element of e with given name and
    return text value

    returns default=None if sub-element isn't found
    """
    try:
        return e.find(name).text
    except:
        return default


def parsetcx(xml):
    """
    parsetcx

    parses tcx data, returning a list of all Trackpoints where each
    point is a tuple of

      (activity, lap, timestamp, seconds, lat, long, alt, dist, heart, cad)

    xml is a string of tcx data
    """

    # remove xml namespace (xmlns="...") to simplify finds
    # note: do this using ET._namespace_map instead?
    # see http://effbot.org/zone/element-namespaces.htm

    xml = re.sub('xmlns=".*?"','',xml)
    #print "xml = " + str(xml)

    # parse xml
    tcx=fromstring(xml)

    #print "tcx = " + str(tcx)

    activity = tcx.find('.//Activity').attrib['Sport']

    lapnum=1
    points=[]
    for lap in tcx.findall('.//Lap/'):

        """
        totaltime = findtext(elem, 'TotalTimeSeconds')
        totaldist = findtext(lap, 'DistanceMeters')
        maxspeed = findtext(lap, 'MaximumSpeed')
        calories = findtext(lap, 'Calories')
        averageHR = findtext(lap, 'AverageHeartRateBpm')
        maxHR = findtext(lap, 'MaximumHeartRateBpm')
        intensity = findtext(lap, 'Intensity')
        cadence = findtext(lap, 'Cadence')
        triggerMtd = findtext(lap, 'TriggerMethod')
"""

        for point in lap.findall('.//Trackpoint'):

            # time, both as string and in seconds GMT
            # note: adjust for timezone?
            timestamp = findtext(point, 'Time')
            if timestamp:
                #seconds = strftime('%s', strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ'))
                seconds = timestamp
            else:
                seconds = None

            # latitude and longitude
            position = point.find('Position')
            lat = findtext(position, 'LatitudeDegrees')
            longitude = findtext(position, 'LongitudeDegrees')

            # altitude
            alt = float(findtext(point, 'AltitudeMeters',0))

            # cummulative distance
            dist = findtext(point, 'DistanceMeters')

            # heart rate
            heart = int(findtext(point.find('HeartRateBpm'),'Value',0))

            # cadence
            cad = int(findtext(point, 'Cadence',0))

            # append to list of points
            points.append((activity,
                           lapnum,
                           timestamp,
                           seconds,
                           lat,
                           longitude,
                           alt,
                           dist,
                           heart,
                           cad))

    # next lap
    lapnum+=1

    return points

    hr = []
    for point in points:
        hr.append(point[8])
        

if __name__=='__main__':
    delim = "\t"

    # set input and output streams
    #istream = open('exampleBeautifulSoup.tcx','r')
    istream = open('example.tcx','r')
    ostream = sys.stdout

    # read xml contents
    xml = istream.read()

    # parse tcx file
    points = parsetcx(xml)

    # print results
    # (activity, lap, timestamp, seconds, lat, long, alt, dist, heart, cad)
    for point in points:
        ostream.write(delim.join(map(str, point))+'\n')
