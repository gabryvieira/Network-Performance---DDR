import numpy as np
import scipy.stats as stats
import scipy.signal as signal
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import time
import sys
import warnings
warnings.filterwarnings('ignore')

def waitforEnter():
	if sys.version_info[0] == 2:
		raw_input("Press ENTER to continue.")
	else:
		input("Press ENTER to continue.")

def hellingerDist(pdf1, pdf2):
	return np.sqrt(np.sum((np.sqrt(pdf1) - np.sqrt(pdf2)) ** 2)) / np.sqrt(2)


plt.ion()
# -1- #
data1=np.loadtxt('data1')
data2 = np.loadtxt('data2')
#for dataset 0 (from 0 to 39)
plt.figure(1)
plt.plot(data1[:,0],marker='s',c='blue',label='dataset 0')
plt.show()

# -2- #
#M=np.mean(data1,axis=0) # media
#Md=np.median(data1,axis=0) # mediana
#V=np.var(data1,axis=0)
#S=stats.skew(data1)
#K=stats.kurtosis(data1)
#p=range(5,101,1)
#Pr=np.percentile(data1,p,axis=0)

#plt.figure(2)
#plt.subplot(5,1,1) 
#plt.plot(M)
#plt.ylabel('mean') # media
#plt.subplot(5,1,2) 
#plt.plot(Md)
#plt.ylabel('median')  # mediana
#plt.subplot(5,1,3) 
#plt.plot(V)
#plt.ylabel('variance') # variancia
#plt.subplot(5,1,4) 
#plt.plot(S)
#plt.ylabel('skewness') # skewness
#plt.subplot(5,1,5) 
#plt.plot(K)
#plt.ylabel('kurtosis') # kurtosis
#plt.show()

## -4- #
##for dataset 0 (from 0 to 39)
#pdf, bins = np.histogram(data1[:,0],bins=50,density=True)
#dbin=np.diff(bins)[0]
#cdf=np.cumsum(pdf)*dbin
#x=bins[:-1]
#plt.figure(3)
#plt.plot(x,pdf,marker='s',c='blue',label='dataset 0 PDF')
#plt.show()
#plt.figure(4)
#plt.plot(x,cdf,marker='s',c='blue',label='dataset 0 CDF')
#plt.show()

## -5- #
##Q-Q plot for dataset 0 and dataset 1
#plt.figure(4)
#plt.clf()
#p=range(5,101,1)
#Pr0=np.percentile(data1[:,0],p)
#Pr1=np.percentile(data1[:,1],p)
#plt.scatter(Pr0,Pr1,marker='o',c='blue')
#lp=[0,max(Pr0[-1],Pr1[-1])]
#plt.plot(lp,lp,c='red')
#plt.show()
##P-P plot for dataset 0 and dataset 1
#plt.figure(5)
#plt.clf()
#pdf0, bins = np.histogram(data1[:,0],bins=50,density=True)
#dbin=np.diff(bins)[0]
#cdf0=np.cumsum(pdf0)*dbin
##bins/xvalues of the CDF should be the same
#pdf1, bins = np.histogram(data1[:,1],bins=bins,density=True)
#dbin=np.diff(bins)[0]
#cdf1=np.cumsum(pdf1)*dbin
#plt.scatter(cdf0,cdf1,marker='o',c='blue')
#lp=[min(cdf0[0],cdf1[0]),1]
#plt.plot(lp,lp,c='red')
#plt.show()

## -7- #
##for dataset 0
#stats.kstest(data1[:,0],'expon') 
#stats.kstest(data1[:,0],'norm')
##for dataset 0 and dataset 1
#stats.ks_2samp(data1[:,0],data1[:,1])
##for dataset 0 and dataset 30
#stats.ks_2samp(data1[:,0],data1[:,30])

## -8- #
#data2=np.loadtxt('data2')
#plt.figure(6)
#pdf,x,y=np.histogram2d(data1[:,0],data2[:,0],bins=10)
#xx,yy = np.meshgrid(x, y)
#plt.pcolormesh(xx, yy, pdf)
#plt.show()

## -9- #
#plt.figure(7)
#data1All=np.loadtxt('data1All')
#for a in range(20,501,20):
	#plt.clf()
	#Agg=np.sum(data1All[:,0:a],axis=1)
	#pdf,x=np.histogram(Agg,bins=20,density=True)
	#m=np.mean(Agg)
	#std=np.std(Agg)		#standard deviation = sqrt( variance )
	#plt.plot(x[:-1],pdf,'k',label='empirical PDF ('+str(a)+' users)')
	#plt.plot(x,mlab.normpdf(x,m,std),'r',label='inferred Gaussian PDF')
	#plt.show()
	#plt.legend()
	#waitforEnter()

## -10- #
#plt.figure(8)
#traff=np.loadtxt('traff')
#C=abs(np.corrcoef(traff,rowvar=0))
#plt.pcolormesh(C)
#plt.show()

## -11- #
## for dataset 2
#plt.figure(9)
#x=data1[:,2]
#lag=np.arange(0,100,1)
#xcorr=np.zeros(100)
#xcorr[0]=np.correlate(x,x)
#for l in lag[1:]:
	#xcorr[l]=np.correlate(x[:-l],x[l:])
#plt.plot(lag,xcorr)
#plt.show()

## -12- #
##for dataset 2 (with modulus-squared of FFT)
#plt.figure(10)
#x=data1[:,2]
#fft=np.fft.fft(x)
#psd=abs(fft)**2
#plt.plot(psd[:50])
#plt.show()
## for dataset 2 (with Welch's method )
#f,psd=signal.periodogram(x)
#plt.plot(1/f[:50],psd[:50])
#plt.show()

## -13- #
#import scalogram
#x=data1[:,2]
#scales=np.arange(1,50)
#plt.ion()
#plt.figure(11)
#cwt=scalogram.CWTfft(x, scales)
#plt.imshow(abs(cwt), cmap=plt.cm.Blues, aspect='auto')
#plt.show()
#plt.figure(12)
#S,scales=scalogram.scalogramCWT(x,scales)
#plt.plot(scales,S)
#plt.show()

# -14- #
#features
#M1=np.mean(data1,axis=0)
#Md1=np.median(data1,axis=0)
#V1=np.var(data1,axis=0)
#S1=stats.skew(data1)
#K1=stats.kurtosis(data1)
#p=[25,50,75,90,95]
#Pr1=np.array(np.percentile(data1,p,axis=0)).T
#M2=np.mean(data2,axis=0)
#Md2=np.median(data2,axis=0)
#V2=np.var(data2,axis=0)
#S2=stats.skew(data2)
#K2=stats.kurtosis(data2)
#Pr2=np.array(np.percentile(data2,p,axis=0)).T
#features=np.c_[M1,M2,Md1,Md2,V1,V2,S1,S2,K1,K2,Pr1,Pr2]
##PCA
#from sklearn.decomposition import PCA
#pca = PCA(n_components=2)
#rcp = pca.fit(features).transform(features)
#plt.figure(13)
#plt.scatter(rcp[0:19,0], rcp[0:19,1],marker='o',c='r',label='datasets 0-19')
#plt.scatter(rcp[20:,0], rcp[20:,1],marker='s',c='b',label='datasets 20-39')
#plt.legend()
#plt.show()
#waitforEnter()


# -15- #
from sklearn.cluster import KMeans
rcp = PCA(n_components=2).fit_transform(features)
#K-means assuming 2 clusters
kmeans = KMeans(init='k-means++', n_clusters=2)
kmeans.fit(rcp)
kmeans.labels_
#vizualization plot
x_min, x_max = 1.5*rcp[:, 0].min(), 1.5*rcp[:, 0].max()
y_min, y_max = 1.5*rcp[:, 1].min(), 1.5*rcp[:, 1].max()
N=20
hx=(x_max-x_min)/N
hy=(y_max-y_min)/N
xx, yy = np.meshgrid(np.arange(x_min, x_max, hx), np.arange(y_min, y_max, hy))
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.figure(14)
plt.imshow(Z, interpolation='nearest',extent=(xx.min(), xx.max(),yy.min(), yy.max()),cmap=plt.cm.Blues,aspect='auto', origin='lower',alpha=0.7)
plt.plot(rcp[:, 0], rcp[:, 1], 'ko')
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],marker='x', color='r')
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.xticks(())
plt.yticks(())
plt.show()

# -16- #
from sklearn.cluster import DBSCAN
rcp = PCA(n_components=2).fit_transform(features)
#DBSCAN assuming a neighborhood maximum distance of 1e11
dbscan = DBSCAN(eps=1e11)
dbscan.fit(rcp)
L=dbscan.labels_
print(L)
colors = plt.cm.Blues(np.linspace(0, 1, len(set(L))))
plt.figure(15)
for l in set(L):
	p=(L==l)
	if l==-1:
		color='r'
	else:
		color=colors[l]
	plt.plot(rcp[p,0],rcp[p,1],'o',c=color,markersize=10)
plt.show()

# -17- #
from sklearn.covariance import EllipticEnvelope
anom_perc=20
clf=EllipticEnvelope(contamination=.1)
clf.fit(rcp)
clf.decision_function(rcp).ravel()
pred=clf.decision_function(rcp).ravel()
threshold = stats.scoreatpercentile(pred,anom_perc)
Anom=pred>threshold
print(Anom)
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.figure(16)
plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), threshold, 7),cmap=plt.cm.Blues_r)
plt.contour(xx, yy, Z, levels=[threshold],linewidths=2, colors='red')
plt.plot(rcp[:, 0], rcp[:, 1], 'ko')
plt.show()
waitforEnter()

# -18- #
x=data1[:,2]
M=np.mean(x)
V=np.var(x)
H,bins=np.histogram(x,bins=20)
probs=1.0*H/np.sum(H)
#Exponential
ye=np.random.exponential(M,(300,20))
#Gaussian/Normal
yg=np.random.normal(M,V**0.5,(300,20))
#Empirical discrete
yd=np.random.choice(bins[:-1],(300,20),p=probs)

# -20- #
import json
from scipy.optimize import curve_fit
with open('ams-ix-traffic.json') as data_file:
	data=json.load(data_file)
Xout=[]
for monthT in data:
	Xout.append(monthT['out_traffic'])

def linearG(t,Y0,R):
	return Y0+R*t

def expG(t,Y0,A0,R):
	return Y0+A0*np.exp(R*t)

t=np.arange(0,len(Xout))
paramsL, cov = curve_fit(linearG,t,Xout)
paramsE, cov = curve_fit(expG,t,Xout,[500,1,.01])
plt.figure(17)
plt.plot(t,Xout,'k')
plt.plot(t,linearG(t,paramsL[0],paramsL[1]),'b')
plt.plot(t,expG(t,paramsE[0],paramsE[1],paramsE[2]),'r')
plt.show()

#End
waitforEnter()




















