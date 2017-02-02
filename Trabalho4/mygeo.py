import math
import numpy
import urllib2
import json
import time

def getgeo(string):
	response = urllib2.urlopen('http://maps.google.com/maps/api/geocode/json?address='+string)
	
	data={'status':''}
	while data['status']!='OK':
		data = json.load(response) 
		if data['status']!='OK':
			time.sleep(60)
		else:
			time.sleep(1)

	lat=data['results'][0]['geometry']['location']['lat']
	lng=data['results'][0]['geometry']['location']['lng']
	city=""
	country=""

	for a in  data['results'][0]['address_components']:
		if a['types'][0]=="locality" :
			city=a['long_name'].encode('utf-8')
		elif a['types'][0]=="country" :
			country=a['long_name'].encode('utf-8')
	return lat, lng, city, country

def geodist(c1,c2):
	R=6371 #km
	af1 = c1[0]/180.*numpy.pi
	af2 = c2[0]/180.*numpy.pi
	adf = (c2[0]-c1[0])/180.*numpy.pi
	adl = (c2[1]-c1[1])/180.*numpy.pi

	#Rhumb Line Navigation (angle from true north, north to east)
	#http://williams.best.vwh.net/avform.htm#Rhumb

	tc= numpy.mod(math.atan2(adl,numpy.log(math.tan(af2/2+numpy.pi/4)/numpy.tan(af1/2+numpy.pi/4))),2*numpy.pi)

	if (abs(adf) < 1e-10):
		D=R*numpy.cos(af1)*adl
	else:
		D=R*(1./numpy.cos(tc))*adf
	
	D=abs(D)

	tc=tc/numpy.pi*180; #True course (degrees)

	adl=adl-numpy.sign(adl)*2*numpy.pi;

	tc2= numpy.mod(math.atan2(adl,numpy.log(numpy.tan(af2/2+numpy.pi/4)/numpy.tan(af1/2+numpy.pi/4))),2*numpy.pi)
	if (abs(adf) < 0.2):
		D2=R*numpy.cos(af1)*adl;
	else:
		D2=R*(1./numpy.cos(tc2))*adf;
	
	D2=abs(D2);
	tc2=tc2/numpy.pi*180; #True course (degrees)

	if(D<D2):
		Do1=D
	else:
		Do1=D2

	return Do1
