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

#Sender (tx) -> Node1 -> Link -> Receiver (rx)
listLoss64=[]
listAvg64=[]
listTB64 = []
listLoss96=[]
listAvg96=[]
listTB96 = []
listLoss128=[]
listAvg128=[]
listTB128 = []
listLoss256=[]
listAvg256=[]
listTB256= []
listQueueS=[64.0, 96.0, 128.0, 256.0]
listLamb = [150.0,300.0,450.0,600.0]
for lamb in listLamb:
	for queueS in listQueueS:
		env = simpy.Environment()
		rx=pkt_Receiver(env,'Int')
		rxA=pkt_Receiver(env,'A')
		rxB=pkt_Receiver(env,'B')
		txA=pkt_Sender(env,'A',lamb,'Int')
		txB=pkt_Sender(env,'B',lamb,'Int')
		txIntToA = pkt_Sender(env,'Int',lamb,'A')
		txIntToB = pkt_Sender(env,'Int',lamb,'B')
		node1 = Node(env,'N1',750,queueS)
		node2 = Node(env,'N2',750,queueS)
		node3 = Node(env,'N3',750,queueS)
		node4 = Node(env,'N4',750,queueS)
		#links A/B to Int
		link1=Link(env,'L1',10e6,queueS)
		link2=Link(env,'L2',10e6,queueS)
		link3=Link(env,'L3',10e6,queueS)
		link4=Link(env,'L4',10e6,queueS)
		#link Int to A/B
		link5=Link(env,'L5',10e6,queueS)
		link6=Link(env,'L6',10e6,queueS)
		link7=Link(env,'L7',10e6,queueS)
		link8=Link(env,'L8',10e6,queueS)
		link9=Link(env,'L9',10e6,queueS)
		#conections A/B to Int
		txA.out = node1
		txB.out = node2
		node1.add_conn(link1,'Int')	
		link1.out=node3
		node2.add_conn(link2,'Int') 
		link2.out = node3
		node3.add_conn(link3,'Int')
		link3.out = node4
		node4.add_conn(link4,'Int')
		link4.out= rx
		#conections Int to A/B
		txIntToA.out = node4
		txIntToB.out = node4
		node4.add_conn(link5,'A')
		node4.add_conn(link5,'B')
		link5.out = node3
		node3.add_conn(link6,'A')
		node3.add_conn(link7,'B')
		link6.out = node1
		link7.out = node2
		node1.add_conn(link8,'A')
		node2.add_conn(link9,'B')
		link8.out = rxA
		link9.out = rxB
		print(node1.out)
		print(node2.out)
		print(node3.out)
		print(node4.out)
		#print('Lambda:%f'%lamb)
		#print('Queue:%f'%queueS)
		simtime=100
		env.run(simtime)
		if(queueS ==64):
			listLoss64 +=[(1-(1.0*(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)/(1.0*(txA.packets_sent+txB.packets_sent+txIntToA.packets_sent+txIntToB.packets_sent))))*100.0]
			listAvg64 += [1.0*(rx.overalldelay+rxA.overalldelay+rxB.overalldelay)/(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)*1.0]
			listTB64 += [1.0*(rx.overallbytes+rxA.overallbytes+rxB.overallbytes)/simtime]
		if(queueS ==96):
			listLoss96 +=[(1-(1.0*(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)/(1.0*(txA.packets_sent+txB.packets_sent+txIntToA.packets_sent+txIntToB.packets_sent))))*100.0]
			listAvg96 += [1.0*(rx.overalldelay+rxA.overalldelay+rxB.overalldelay)/(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)*1.0]
			listTB96 += [1.0*(rx.overallbytes+rxA.overallbytes+rxB.overallbytes)/simtime]
		if(queueS ==128):
			listLoss128 +=[(1-(1.0*(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)/(1.0*(txA.packets_sent+txB.packets_sent+txIntToA.packets_sent+txIntToB.packets_sent))))*100.0]
			listAvg128 += [1.0*(rx.overalldelay+rxA.overalldelay+rxB.overalldelay)/(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)*1.0]
			listTB128 += [1.0*(rx.overallbytes+rxA.overallbytes+rxB.overallbytes)/simtime]
		if(queueS ==256):
			listLoss256 +=[(1-(1.0*(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)/(1.0*(txA.packets_sent+txB.packets_sent+txIntToA.packets_sent+txIntToB.packets_sent))))*100.0]
			listAvg256 += [1.0*(rx.overalldelay+rxA.overalldelay+rxB.overalldelay)/(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)*1.0]
			listTB256 += [1.0*(rx.overallbytes+rxA.overallbytes+rxB.overallbytes)/simtime]
		print('Loss probability: %.2f%%'%((1-(1.0*(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)/(1.0*(txA.packets_sent+txB.packets_sent+txIntToA.packets_sent+txIntToB.packets_sent))))*100.0))
		print('Average delay: %f sec'%(1.0*(rx.overalldelay+rxA.overalldelay+rxB.overalldelay)/(rx.packets_recv+rxA.packets_recv+rxB.packets_recv)*1.0))
		print('Transmitted bandwidth: %.1f Bytes/sec'%(1.0*(rx.overallbytes+rxA.overallbytes+rxB.overallbytes)/simtime))	
		print(listLoss64)	
		print(listAvg64)
		print(listTB64)
plt.figure(1)
plt.subplot(3,1,1)	
plt.plot(listLamb,listLoss64,'blue', label = 'Probability of loss')
plt.plot(listLamb,listLoss96,'r--', label = 'Probability of loss')
plt.plot(listLamb,listLoss128,'g--', label = 'Probability of loss')
plt.plot(listLamb,listLoss256,'y--', label = 'Probability of loss')
plt.ylabel('P loss')
plt.subplot(3,1,2)	
plt.plot(listLamb,listAvg64,'blue', label = 'Avg delay')
plt.plot(listLamb,listAvg96,'r--', label = 'Avg delay')
plt.plot(listLamb,listAvg128,'g--', label = 'Avg delay')
plt.plot(listLamb,listAvg256,'y--', label = 'Avg delay')
plt.ylabel('AVG delay')
plt.subplot(3,1,3)	
plt.plot(listLamb,listTB64,'blue', label = 'TB')
plt.plot(listLamb,listTB96,'r--', label = 'TB')
plt.plot(listLamb,listTB128,'g--', label = 'TB')
plt.plot(listLamb,listTB256,'y--', label = 'TB')
plt.ylabel('TB')
plt.show()







