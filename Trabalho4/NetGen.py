import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from mygeo import getgeo, geodist 
import itertools
import random
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', nargs='?', help='output network file', default='network.dat')
args=parser.parse_args()

filename=args.file 

	
#Large Network
nodes={'Corunha','Vigo','Gijon','Porto','Aveiro','Lisboa','Portimao','Braganca','Vilar.Formoso','Badajoz','Sevilha','Bilbau','Andorra','Barcelona','Madrid','Valencia','Palma','Granada'}
links={('Corunha','Gijon'),('Gijon','Bilbau'),('Vigo','Corunha'),('Porto','Vigo'),('Porto','Braganca'),('Aveiro','Porto'),('Braganca','Gijon'),('Braganca','Bilbau'),('Braganca','Vilar.Formoso'),('Aveiro','Vilar.Formoso'),('Madrid','Vilar.Formoso'),('Badajoz','Vilar.Formoso'),('Aveiro','Lisboa'),('Badajoz','Lisboa'),('Portimao','Lisboa'),('Portimao','Sevilha'),('Badajoz','Sevilha'),('Badajoz','Valencia'),('Granada','Sevilha'),('Granada','Valencia'),('Granada','Palma'),('Palma','Valencia'),('Madrid','Valencia'),('Madrid','Barcelona'),('Barcelona','Valencia'),('Barcelona','Palma'),('Barcelona','Andorra'),('Bilbau','Andorra'),('Bilbau','Madrid')}

#Small Network
#nodes={'Aveiro','Porto','Lisboa','Viseu'}
#links={('Aveiro','Porto'),('Aveiro','Lisboa'),('Aveiro','Viseu'),('Viseu','Lisboa'),('Viseu','Porto')}

pos={}

if 'pos' not in locals() or pos=={}:
	pos={}
	for node in nodes:
		print(node)
		lat,lng,city,country=getgeo(node)
		pos.update({node:(lng,lat)})

net=nx.Graph()
for node in nodes:
	net.add_node(node)
	
for link in links:
	dist=geodist((pos[link[0]][1],pos[link[0]][0]),(pos[link[1]][1],pos[link[1]][0]))
	net.add_edge(link[0],link[1],distance=dist, load=0)
	#print(link,dist,(pos[link[0]][1],pos[link[0]][0]),(pos[link[1]][1],pos[link[1]][0]))

nx.draw(net,pos,with_labels=True)
plt.show()

allpairs=list(itertools.permutations(nodes,2))
tm={}

N=len(nodes)
if 'tm' not in locals() or tm=={}:
	print("Generating random traffic matric (tm)...\n")
	tm={}
	M=500e3/N**2
	for pair in allpairs:
		traffic=max(0,int(np.random.normal(M,M**0.5)))
		if pair[0] not in tm.keys():
			tm.update({pair[0]:{}})
		tm[pair[0]].update({pair[1]:traffic})
	print tm
	print pos
	print("Done!\n")

with open(filename,'w') as f:
    pickle.dump([nodes, links, pos, tm], f)
