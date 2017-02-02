import simpy
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import factorial


class NodeStats:
#"""
	#Node stats recording
	#bw: Link bandwidth 
#"""
	def __init__(self,bw):
		self.vcs_total=0
		self.vcs_acc=0
		self.vcs_blk=0
		self.bw=bw
		self.available_bw=bw
		self.lastloadchange=0
		self.loadint=0

def vc_generator(env,av_rate,av_duration,b,stats):
#"""
	#VC generator
	#env: SimPy environment
	#av_rate: Average VC requests rate
	#av_duration: Average VC duration
	#b: VC required bandwidth
	#stats: Node stats recording (NodeStats class)
#"""

	while True:
		yield env.timeout(np.random.exponential(1.0/av_rate))
		stats.vcs_total += 1
		if stats.available_bw>=b:
			stats.vcs_acc += 1
			stats.loadint += (1.0/stats.bw)*(stats.bw-stats.available_bw)*(env.now-stats.lastloadchange)
			stats.lastloadchange=env.now
			stats.available_bw -= b
			print("time %f: VC %d started"%(env.now,stats.vcs_total))
			env.process(vc(env,stats.vcs_total,av_duration,b,stats))
		else:
			stats.vcs_blk += 1
			print("time %f: VC %d blocked"%(env.now,stats.vcs_total))

def vc(env,id,av_duration,b,stats):
#"""
	#VC object
	#env: SimPy environment
	#id: VC identifier
	#av_duration: Average VC duration
	#b: VC required bandwidth
	#stats: Global stats recording (NodeStats class)
#"""

	
	yield env.timeout(np.random.exponential(av_duration))
	stats.loadint += (1.0/stats.bw)*(stats.bw-stats.available_bw)*(env.now-stats.lastloadchange)
	stats.lastloadchange=env.now
	stats.available_bw += b
	print("time %f: VC %d ended"%(env.now,id))
T_listBlock =[]
T_listAvgCap =[]
S_listBlock =[]
S_listAvgCap =[]
listLamb = [1,1.5,2,2.5,3]
for val in listLamb:
	lamb= val
	invmu=10
	b=2
	B=16
	C=B/b
	simtime=3000

	stats=NodeStats(B)
	env = simpy.Environment()
	env.process(vc_generator(env,lamb,invmu,b,stats))
	env.run(simtime)
	print("Simulated Block Probability=%f"%(1.0*stats.vcs_blk/stats.vcs_total))
	S_listBlock = S_listBlock + [1.0*stats.vcs_blk/stats.vcs_total]	
	print("Simulated Average Link Load=%.2f%%"%(100.0*stats.loadint/simtime))
	S_listAvgCap = S_listAvgCap + [100.0*stats.loadint /simtime]
	rho=lamb*invmu
	i=np.arange(0,C+1)
	blkp=(np.power(1.0*rho,C)/factorial(C))/np.sum(np.power(1.0*rho,i)/factorial(i))
	#print("Theoretical Block Probability=%f"%(blkp))
	T_listBlock = T_listBlock+[blkp]
	i1=np.arange(1,C+1)
	linkload=(1.0/C)*np.sum(np.power(1.0*rho,i1)/factorial(i1-1))/np.sum(np.power(1.0*rho,i)/factorial(i))
	#print("Theoretical Average Link Load=%.2f%%"%(100*linkload))
	T_listAvgCap = T_listAvgCap +[100*linkload]

plt.figure(1)
plt.subplot(2,1,1)	
plt.plot(listLamb,S_listBlock,'blue', label = 'Probability of block')
plt.plot(listLamb,T_listBlock, 'r--')
plt.ylabel('P block')
plt.subplot(2,1,2)
plt.plot(listLamb,S_listAvgCap,'blue', label = 'Avg capability')
plt.plot(listLamb,T_listAvgCap,'r--')
plt.ylabel('AVG cap')
plt.show()
