import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from mygeo import getgeo, geodist 
import itertools
import random
import pickle
import argparse

mu=1e9/8000 #link speed in pkts/sec
lightspeed=300000.0 #Km/sec

def listStats(L):
	#Returns the mean and maximum values of a list of numbers with generic keys
	#	returns also the key of the maximum value
	V=L.values()
	K=L.keys()
	meanL=np.mean(V)
	maxL=np.max(V)
	p=np.where(V==M)[0][0]
	maxLK=K[p]
	return meanL, maxL, maxLK


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', nargs='?', help='input network file', default='network.dat')
args=parser.parse_args()

filename=args.file 

with open(filename) as f:
	nodes, links, pos, tm = pickle.load(f)

print(tm)

net=nx.DiGraph()
for node in nodes:
	net.add_node(node)
	
for link in links:
	dist=geodist((pos[link[0]][1],pos[link[0]][0]),(pos[link[1]][1],pos[link[1]][0]))
	net.add_edge(link[0],link[1],distance=dist, load=0, delay=0)
	net.add_edge(link[1],link[0],distance=dist, load=0, delay=0)
	#print(link,dist,(pos[link[0]][1],pos[link[0]][0]),(pos[link[1]][1],pos[link[1]][0]))

nx.draw(net,pos,with_labels=True)
plt.show()

allpairs=list(itertools.permutations(nodes,2))
sol={}

for pair in allpairs:
	path=nx.shortest_path(net,pair[0],pair[1],weight='load')
	sol.update({pair:path})
	for i in range(0,len(path)-1):
		net[path[i]][path[i+1]]['load']+=tm[pair[0]][pair[1]]
		net[path[i]][path[i+1]]['delay'] += 1/(mu - net[path[i]][path[i+1]]['load'])
			

#print path3
print('---')
print('Solution:'+str(sol))
linkLodMean = 0
maxLinkLoad = 0
summ = 0
delayMean = 0
maxDelay = 0
print('---')
for link in links:
	print("#link %s-%s: %d pkts/sec, avg delay:%s"%(link[0],link[1],net[link[0]][link[1]]['load'],(1/(mu - net[link[0]][link[1]]['load']))))
	print("#link %s-%s: %d pkts/sec, avg delay:%s"%(link[1],link[0],net[link[1]][link[0]]['load'],(1/(mu - net[link[1]][link[0]]['load']))))
	print("Load both directions: %d"%(net[link[0]][link[1]]['load']+net[link[1]][link[0]]['load']))
	
	if ((net[link[0]][link[1]]['load']) > maxLinkLoad):
		maxLinkLoad = net[link[0]][link[1]]['load']
	
	if ((net[link[1]][link[0]]['load']) > maxLinkLoad):	
		maxLinkLoad = net[link[1]][link[0]]['load']
		
	if(1/(mu - net[link[0]][link[1]]['load']) > maxDelay):
		maxDelay = 1/(mu - net[link[0]][link[1]]['load'])
		#print("Pior fluxo: %s-%s"%(link[0],link[1]))
	
	if(1/(mu - net[link[1]][link[0]]['load']) > maxDelay):	
		maxDelay = 1/(mu - net[link[1]][link[0]]['load'])
		#print("Pior fluxo: %s-%s"%(link[1],link[0]))

	linkLodMean = linkLodMean + net[link[0]][link[1]]['load']
	linkLodMean = linkLodMean + net[link[1]][link[0]]['load']
	summ = summ + 2
	delayMean = delayMean + 1/(mu - net[link[0]][link[1]]['load'])
	delayMean = delayMean + 1/(mu - net[link[1]][link[0]]['load'])
	
print(" Average Link Load: %s"%(linkLodMean/summ) )
print(" Average Delay: %s"%(delayMean/summ))
print("Fluxo maior atraso (pior condicao): %s"%maxDelay)
print("Link Load maximo: %s"%maxLinkLoad);

#for s in sol:
	#if(len(s) > 1):
		#print("#link %s-%s: %d pkts/sec, avg delay:%s"%(s[0],s[-1],net[link[0]][link[1]]['load'],(1/(mu - net[link[0]][link[1]]['load']))))
		#print("#link %s-%s: %d pkts/sec, avg delay:%s"%(s[-1],s[0],net[link[1]][link[0]]['load'],(1/(mu - net[link[0]][link[1]]['load']))))
		#print("Load both directions: %d"%(net[link[0]][link[1]]['load']+net[link[1]][link[0]]['load']))
		
	#i = len(s)
	#interLoadAB=0
	#interLoadBA=0
	#a=0
	#b=1
	#if(len(s)>=3):
		#while(i > 0):
			#interLoadAB = interLoadAB + net[link[a]][link[b]]['load']
			#interLoadBA=interLoadBA +net[link[b]][link[a]]['load']
			#a = a+1
			#b=b+1
			#i=i-1
		#print("#link %s-%s: %d pkts/sec, avg delay:%s"%(s[0],s[-1],interLoadAB,(1/(mu -interLoadAB))))
		#print("#link %s-%s: %d pkts/sec, avg delay:%s"%(s[-1],s[0],interLoadBA,(1/(mu - interLoadAB))))


	
	
	
	
	
