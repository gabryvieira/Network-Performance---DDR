# -*- coding: UTF-8 -*-
import sys
import socket
import struct
import argparse
from netaddr import IPNetwork, IPAddress

def int_to_ipv4(addr):
	return "%d.%d.%d.%d" % \
	   (addr >> 24 & 0xff, addr >> 16 & 0xff, \
	    addr >> 8 & 0xff, addr & 0xff)

def getNetFlowData(data,flowMatrix):
	sdata=struct.unpack("!H", data[:2])
	version = sdata[0]
	
	if version==1 or version == 5 :
		if version==1:
			hformat="!HHIII" 		# ! - network (= big-endian), H – C unsigned short (2 bytes), I – C unsigned int (4 bytes)
			fformat="!IIIHHIIIIHHHBBBBBBI"		# B – C unsigned char (1 byte)
		if version == 5:
			hformat="!HHIIIIBBH" 		# ! - network (= big-endian), H – C unsigned short (2 bytes), I – C unsigned int (4 bytes)
			fformat="!IIIHHIIIIHHBBBBHHBBH"		# B – C unsigned char (1 byte)
		print("NetFlow version %d:"%version)
		hlen = struct.calcsize(hformat)
		if len(data) < hlen:
			print("Truncated packet (header)")
			return 0,0
		sheader= struct.unpack(hformat, data[:hlen])
		version = sheader[0]
		num_flows = sheader[1]
		#more header
		
		print(num_flows)
		
		flen=struct.calcsize(fformat)
		
		if len(data) - hlen != num_flows * flen:
			print("Packet truncated (flows data)")
			return 0,0
			
		# Flow Matrix Ex 10	
		myMatrix = flowMatrix
		flows={}
		for n in range(num_flows):
			flow={}
			offset = hlen + flen*n
			fdata = data[offset:offset + flen]
			sflow=struct.unpack(fformat, fdata)
			flow.update({'Pkts send ': (sflow[5])})
			flow.update({'Bytes send': (sflow[6])})
			flow.update({'Output Interface Idx': (sflow[4])})
			flow.update({'Input Interface Idx': (sflow[3])})
			flow.update({'Next_hoop':int_to_ipv4(sflow[2])})
			flow.update({'Dest_addr':int_to_ipv4(sflow[1])})
			flow.update({'Src_addr':int_to_ipv4(sflow[0])})
			#myIpSource = int_to_ipv4(sflow[0])
			flag = False
			tmpM = []
			for maElem in myMatrix:
				ma_NetSource,ma_NetDest,numFluxos,  ma_PkBy = maElem
				ipNetS = IPNetwork((int_to_ipv4(sflow[0])+"/255.255.255.0"))
				ipNetD = IPNetwork((int_to_ipv4(sflow[1])+"/255.255.255.0"))
				if(ma_NetSource == ipNetS and ma_NetDest == ipNetD):
					pbPk, pkBy =  ma_PkBy
					pbPk = sflow[5] + pbPk
					pkBy = sflow[6] + pkBy
					ma_PkBy = pbPk,pkBy
					numFluxos = numFluxos +1 
					maElem = ma_NetSource,ma_NetDest, numFluxos, ma_PkBy
					tmpM = tmpM + [maElem]
					flag = True
				else:
					tmpM = tmpM + [maElem]	
			if(flag != True):
				tmpM=[]
				flag = False
				for maElem in myMatrix:
					ma_NetSource,ma_NetDest,numFluxos, ma_PkBy = maElem
					ipNetS = IPNetwork((int_to_ipv4(sflow[0])+"/255.255.255.0"))
					ipNetD = IPNetwork((int_to_ipv4(sflow[1])+"/255.255.255.0"))
					if(ma_NetSource == ipNetS and ma_NetDest == 'other'):
						pbPk, pkBy =  ma_PkBy
						pbPk = sflow[5] + pbPk
						pkBy = sflow[6] + pkBy
						numFluxos = numFluxos +1 
						ma_PkBy = pbPk,pkBy
						maElem = ma_NetSource,ma_NetDest, numFluxos, ma_PkBy
						tmpM = tmpM + [maElem]
						flag = True
					else:
						tmpM = tmpM + [maElem]
			if(flag != True):
				tmpM=[]
				flag = False
				for maElem in myMatrix:
					ma_NetSource,ma_NetDest, numFluxos, ma_PkBy = maElem
					ipNetS = IPNetwork((int_to_ipv4(sflow[0])+"/255.255.255.0"))
					ipNetD = IPNetwork((int_to_ipv4(sflow[1])+"/255.255.255.0"))
					if(ma_NetSource == 'other' and ma_NetDest == ipNetD):
						pbPk, pkBy =  ma_PkBy
						pbPk = sflow[5] + pbPk
						pkBy = sflow[6] + pkBy
						numFluxos = numFluxos +1 
						ma_PkBy = pbPk,pkBy
						maElem = ma_NetSource,ma_NetDest, numFluxos, ma_PkBy
						tmpM = tmpM + [maElem]
						flag = True
					else:
						tmpM = tmpM + [maElem]
			if(flag != True):
				tmpM=[]
				flag = False
				for maElem in myMatrix:
					ma_NetSource,ma_NetDest, numFluxos, ma_PkBy = maElem
					if(ma_NetSource == 'other' and ma_NetDest == 'other'):
						pbPk, pkBy =  ma_PkBy
						pbPk = sflow[5] + pbPk
						pkBy = sflow[6] + pkBy
						numFluxos = numFluxos +1 
						ma_PkBy = pbPk,pkBy
						maElem = ma_NetSource,ma_NetDest, numFluxos, ma_PkBy
						tmpM = tmpM + [maElem]
						flag = True
					else:
						tmpM = tmpM + [maElem]
			myMatrix = tmpM
			#more flow
			flows.update({n:flow})
	else:
		print("NetFlow version %d not supported!"%version)
	out=version,flows, myMatrix
	return out

def main():
	parser=argparse.ArgumentParser()
	parser.add_argument('-p', '--port', nargs='?',type=int,help='listening UDP port',default=9996)
	parser.add_argument('-n', '--net', nargs='+',required=True, help='networks')
	parser.add_argument('-r', '--router', nargs='+',required=True, help='IP address(es) of NetFlow router(s)')
	args=parser.parse_args()

	nets=[]
	for n in args.net:
		try:
			nn=IPNetwork(n)
			nets.append(nn)
		except:
			print('%s is not a network prefix'%n)
	print(nets)
	if len(nets)==0:
		print("No valid network prefixes.")
		sys.exit()

	router=[]
	for r in args.router:
		try:
			rr=IPAddress(r)
			router.append(rr)
		except:
			print('%s is not an IP address'%r)
	print(router)
	if len(router)==0:
		print("No valid router IP address.")
		sys.exit()	
	udp_port=args.port
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
	sock.bind(('0.0.0.0', udp_port))
	print("listening on '0.0.0.0':%d"%udp_port) 
	myNetworks = ['other']+nets
	flowMatrix = []
	listFlows = []
	for myNetI in myNetworks:
		for myNetJ in myNetworks:
			flowMatrix = flowMatrix + [(myNetI,myNetJ,0,(0,0))]
	fileMatrix = open ('trafficMatrixV5.txt','w')
	try: 
		while 1:
			count = 0
			data, addr = sock.recvfrom(8192)		# buffer size is 8192 bytes
			version,flows,fMatrix=getNetFlowData(data,flowMatrix)		#version=0 reports an error!
			flowMatrix = fMatrix
			print('Version: %d'%version)
			fileMatrix.write('Version: %d\n'%version)
			print(flows)
			fileMatrix.write("Number of flows: %d\n"%len(flows))
			for i,name in flows.items():
				fileMatrix.write(str(i)+":"+str(name)+"\n")
			fileMatrix.write("\n===========================================================================\n")
			print("====================")
			print("[Source Net IP, Dest Net IP,Numero de Fluxos(Pkts send, Bytes send)]")
			print(flowMatrix)
			fileMatrix.write("[Source Net IP, Dest Net IP,Numero de Fluxos(Pkts send, Bytes send)]\n")
			for content in flowMatrix:
				if count%(len(myNetworks)) == 0:
					fileMatrix.write("\n"+str(content))
				else:
					fileMatrix.write(str(content))
				count = count +1
			print("====================")
			fileMatrix.write("\n===========================================================================\n")
	except KeyboardInterrupt:
		fileMatrix.close()
		sock.close()
		print("\nDone!")

if __name__ == "__main__":
	main()
