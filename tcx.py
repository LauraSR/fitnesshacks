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
import time
from optparse import OptionParser
import sys
import re
import numpy as np



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

#smoothing using convolution from scipy cookbook
    import np

def smooth(x,window_len=11,window='flat'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y


def get_hr_time(points,plot_flag = True):
    """
    Function to obtain hr and time in seconds from points readed using tcx
    """
    t = [] #time in seconds
    # bb = strptime(points[-2][3], '%Y-%m-%dT%H:%M:%S.%fZ')
    #  aa = strptime(point[3], '%Y-%m-%dT%H:%M:%S.%fZ')
    #import time

    #t1 = time.mktime(aa)

    #t2 = time.mktime(bb)

#   t2-t1
    hr = [] #hear rate in beat per minutes
    t = [0]
    t_old = []
    for i,point, in enumerate(points):
        hr.append(point[8])
        t_curr = strptime(point[3], '%Y-%m-%dT%H:%M:%S.%fZ') #get actual time stamp
        if i == 0:
            #pass
            pass
        #avoid first timestamp
        else:
            t_secs = time.mktime(t_curr) - time.mktime(t_old) #diff in seconds with previous timestamp
            t.append(t_secs + t[i-1])
            
        t_old = t_curr #update t_old
            
            
#plotting heart rate
    if plot_flag == True:
        plt.close('all')
        plt.plot(t,hr,'.-')
        win_size = 25
   # window = np.ones((win_size,1))
   # hr_mean = np.convolve(np.array(hr),window.flatten(),'same') /sum(window)
        hr_mean = smooth(np.array(hr), window_len = win_size) 
        plt.plot(t,hr_mean[win_size-1:],'.-')
    
    return t,hr
        

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


    #plot heart rate
    t,hr = get_hr_time(points)
    
    
    