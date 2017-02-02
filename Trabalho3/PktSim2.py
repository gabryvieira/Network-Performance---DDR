import simpy
import matplotlib.pyplot as plt
import random 
import numpy as np

class Packet(object):
	"""
	Packet Object
	time: packet creation time/ID (float)
	size: packet size (integer)
	dst: packet destination (string) - pkt_Receiver ID
	"""
	def __init__(self,time,size,dst):
		self.time=time
		self.size=size
		self.dst=dst
	
	def __repr__(self):
		return 'Pkt %f [%d] to %s'%(self.time,self.size,self.dst)

class Node(object):
	"""
	Node Object
	env: SimPy environment
	id: Node ID (string)
	speed: Node routing speed (float, pkts/sec)
	qsize: Node input queue size (integer, number of packets, default inf)
	"""
	def __init__(self,env,id,speed,qsize=np.inf):
		self.env=env
		self.id=id
		self.speed=speed
		self.qsize=qsize
		self.queue = simpy.Store(env)
		self.lost_pkts=0
		self.out={} #list with obj {'dest1':[elem1,elem3],'dest2':[elem1,elem2],...}
		self.action = env.process(self.run())
		
	def add_conn(self,elem,dsts):
		"""
		Defines node output connections to other simulation elements
		elem: Next element (object)
		dsts: list with destination(s) ID(s) accessible via elem (string or list of strings)
		"""
		for d in dsts:
			if self.out.has_key(d):
				self.out[d].append(elem)
			else:
				self.out.update({d:[elem]})
	
	def run(self):
		while True:
			pkt = (yield self.queue.get())
			yield self.env.timeout(1.0/self.speed)
			if self.out.has_key(pkt.dst):
				#random routing over all possible paths to dst
				outobj=self.out[pkt.dst][random.randint(0,len(self.out[pkt.dst])-1)]
				print(str(self.env.now)+': Packet out node '+self.id+' - '+str(pkt))
				outobj.put(pkt)
			else:
				print(str(self.env.now)+': Packet lost in node '+self.id+'- No routing path - '+str(pkt))
	
	def put(self,pkt):
		if len(self.queue.items)<self.qsize:
			self.queue.put(pkt)
		else:
			self.lost_pkts += 1
			print(str(env.now)+': Packet lost in node '+self.id+' queue - '+str(pkt))

class Link(object):
	"""
	Link Object
	env: SimPy environment
	id: Link ID (string)
	speed: Link transmission speed (float, bits/sec)
	qsize: Node to Link output queue size (integer, number of packets, default inf)
	"""
	def __init__(self,env,id,speed,qsize=np.inf):
		self.env=env
		self.id=id
		self.speed=1.0*speed/8
		self.qsize=qsize
		self.queue = simpy.Store(env)
		self.lost_pkts=0
		self.out=None
		self.action = env.process(self.run())
		
	def run(self):
		while True:
			pkt = (yield self.queue.get())
			yield self.env.timeout(1.0*pkt.size/self.speed)
			print(str(self.env.now)+': Packet out link '+self.id+' - '+str(pkt))
			self.out.put(pkt)
				
	def put(self,pkt):
		if len(self.queue.items)<self.qsize:
			self.queue.put(pkt)
		else:
			self.lost_pkts += 1
			print(str(self.env.now)+': Packet lost in link '+self.id+' queue - '+str(pkt))
		
		
class pkt_Sender(object):
	"""
	Packet Sender
	env: SimPy environment
	id: Sender ID (string)
	rate: Packet generation rate (float, packets/sec)
	dst: List with packet destinations (list of strings, if size>1 destination is random among all possible destinations)
	"""
	def __init__(self,env,id,rate,dst):
		self.env=env
		self.id=id
		self.rate=rate
		self.out=None	
		self.dst=dst
		self.packets_sent=0	
		self.action = env.process(self.run())
		
	def run(self):
		while True:
			yield self.env.timeout(np.random.exponential(1.0/self.rate))
			self.packets_sent += 1
			#size=random.randint(64,1500)
			#size=int(np.random.exponential(500))
			size=int(np.random.choice([64,1500],1,[.5,.5]))
			if len(self.dst)==1:
				dst=self.dst[0]
			else:
				dst=self.dst[random.randint(0,len(self.dst)-1)]
			pkt = Packet(self.env.now,size,dst)
			print(str(self.env.now)+': Packet sent by '+self.id+' - '+str(pkt))
			self.out.put(pkt)
		
class pkt_Receiver(object):
	"""
	Packet Receiver
	env: SimPy environment
	id: Sender ID (string)
	"""
	def __init__(self,env,id):
		self.env=env
		self.id=id
		self.queue = simpy.Store(env)
		self.packets_recv=0
		self.overalldelay=0
		self.overallbytes=0
		self.action = env.process(self.run())
		
	def run(self):
		while True:
			pkt = (yield self.queue.get())
			self.packets_recv += 1
			self.overalldelay += self.env.now-pkt.time
			self.overallbytes += pkt.size
			print(str(self.env.now)+': Packet received by '+self.id+' - '+str(pkt))
	
	def put(self,pkt):
		self.queue.put(pkt)

env = simpy.Environment()

#Sender (tx) ->Link -> Node1 ->  Receiver (rx)
listLoss64=[]
listAvg64=[]
listTB64 = []
listLoss96=[]
listAvg96=[]
listTB96 = []
listLoss128=[]
listAvg128=[]
listTB128 = []
listLoss10k=[]
listAvg10k=[]
listTB10k= []
listQueueS=[64, 96, 128, 10000]
listLamb = [150,300,450]
for lamb in listLamb:
	for queueS in listQueueS:
		env = simpy.Environment()
		rx=pkt_Receiver(env,'B')
		tx=pkt_Sender(env,'A',lamb,'B')
		node1=Node(env,'N1',350,queueS)
		link=Link(env,'L',10e9,np.inf)
		tx.out=link
		link.out = node1
		node1.add_conn(rx,'B')
		#node1.out = rx
		print(node1.out)
		simtime=100
		env.run(simtime)
		if(queueS ==64):
			listLoss64 += [100.0*node1.lost_pkts/tx.packets_sent]
			listAvg64 += [1.0*rx.overalldelay/rx.packets_recv]
			listTB64 += [1.0*rx.overallbytes/simtime]
		if(queueS ==96):
			listLoss96 += [100.0*link.lost_pkts/tx.packets_sent]
			listAvg96 += [1.0*rx.overalldelay/rx.packets_recv]
			listTB96 += [1.0*rx.overallbytes/simtime]
		if(queueS ==128):
			listLoss128 += [100.0*link.lost_pkts/tx.packets_sent]
			listAvg128 += [1.0*rx.overalldelay/rx.packets_recv]
			listTB128 += [1.0*rx.overallbytes/simtime]
		if(queueS ==10000):
			listLoss10k += [100.0*link.lost_pkts/tx.packets_sent]
			listAvg10k += [1.0*rx.overalldelay/rx.packets_recv]
			listTB10k += [1.0*rx.overallbytes/simtime]
		print('Loss probability: %.2f%%'%(100.0*link.lost_pkts/tx.packets_sent))
		print('Average delay: %f sec'%(1.0*rx.overalldelay/rx.packets_recv))
		print('Transmitted bandwidth: %.1f Bytes/sec'%(1.0*rx.overallbytes/simtime))
plt.figure(1)
plt.subplot(3,1,1)	
plt.plot(listLamb,listLoss64,'blue', label = 'Probability of loss')
plt.plot(listLamb,listLoss96,'r--', label = 'Probability of loss')
plt.plot(listLamb,listLoss128,'g--', label = 'Probability of loss')
plt.plot(listLamb,listLoss10k,'y--', label = 'Probability of loss')
plt.ylabel('P loss')
plt.subplot(3,1,2)	
plt.plot(listLamb,listAvg64,'blue', label = 'Avg delay')
plt.plot(listLamb,listAvg96,'r--', label = 'Avg delay')
plt.plot(listLamb,listAvg128,'g--', label = 'Avg delay')
plt.plot(listLamb,listAvg10k,'y--', label = 'Avg delay')
plt.ylabel('AVG delay')
plt.subplot(3,1,3)	
plt.plot(listLamb,listTB64,'blue', label = 'TB')
plt.plot(listLamb,listTB96,'r--', label = 'TB')
plt.plot(listLamb,listTB128,'g--', label = 'TB')
plt.plot(listLamb,listTB10k,'y--', label = 'TB')
plt.ylabel('TB')
plt.show()







