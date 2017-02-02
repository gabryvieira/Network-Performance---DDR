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

def getNetFlowData(data):
	sdata=struct.unpack("!H", data[:2])
	version = sdata[0]
	
	if version==1:
		print("NetFlow version %d:"%version)
		hformat="!HHIII" 		# ! - network (= big-endian), H – C unsigned short (2 bytes), I – C unsigned int (4 bytes)
		hlen = struct.calcsize(hformat)
		if len(data) < hlen:
			print("Truncated packet (header)")
			return 0,0
		sheader= struct.unpack(hformat, data[:hlen])
		version = sheader[0]
		num_flows = sheader[1]
		#more header
		
		print(num_flows)
		fformat="!IIIHHIIIIHHHBBBBBBI"		# B – C unsigned char (1 byte)
		flen=struct.calcsize(fformat)
		
		if len(data) - hlen != num_flows * flen:
			print("Packet truncated (flows data)")
			return 0,0
		
		flows={}
		for n in range(num_flows):
			flow={}
			offset = hlen + flen*n
			fdata = data[offset:offset + flen]
			sflow=struct.unpack(fformat, fdata)
			flow.update({'src_addr':int_to_ipv4(sflow[0])})
			#more flow
			flow.update({'dest_addr':int_to_ipv4(sflow[1])})
			flow.update({'next-hop ip address':int_to_ipv4(sflow[2])})
			flow.update({'input/output intf. index':sflow[3]}) # numero da interface por qual o trafego entra ou sai
			flow.update({'Num of packets':sflow[4]}) # num pacotes
			flow.update({'Num of bytes':sflow[5]})
			flow.update({'Start time of flow':sflow[6]})
			flow.update({'End time of flow':sflow[7]})
			flow.update({'Source/Destination port':sflow[8]})
			flow.update({'PAD/IP Protocol/ TOS':sflow[9]})
			flow.update({'flags/padding':sflow[10]})
			flow.update({'reserved':sflow[11]})
			
			flows.update({n:flow})
			
	
	
	elif version==5:
		print("NetFlow version %d:"%version)
		hformat="!HHIIIIBBH" 		# ! - network (= big-endian), H – C unsigned short (2 bytes), I – C unsigned int (4 bytes)
		hlen = struct.calcsize(hformat)
		if len(data) < hlen:
			print("Truncated packet (header)")
			return 0,0
		sheader= struct.unpack(hformat, data[:hlen])
		version = sheader[0]
		num_flows = sheader[1]
		#more header
		
		print(num_flows)
		fformat="!IIIHHIIIIHHBBBBHHBBH"		# B – C unsigned char (1 byte)
		flen=struct.calcsize(fformat)
		
		if len(data) - hlen != num_flows * flen:
			print("Packet truncated (flows data)")
			return 0,0
		
		flows={}
		for n in range(num_flows):
			flow={}
			offset = hlen + flen*n
			fdata = data[offset:offset + flen]
			sflow=struct.unpack(fformat, fdata)
			flow.update({'src_addr':int_to_ipv4(sflow[0])})
			#more flow
			flow.update({'dest_addr':int_to_ipv4(sflow[1])})
			flow.update({'next-hop ip address':int_to_ipv4(sflow[2])})
			flow.update({'input intf. index':sflow[3]}) # numero da interface por qual o trafego entra ou sai
			flow.update({'Output intf. index':sflow[4]}) # num pacotes
			flow.update({'Num packets':sflow[5]})
			flow.update({'Num of bytes':sflow[6]})
			flow.update({'Start time of flow':sflow[7]})
			flow.update({'End time of flow':sflow[8]})
			flow.update({'Source port':sflow[9]})
			flow.update({'Destination port':sflow[10]})
			flow.update({'Pad':sflow[11]})
			flow.update({'TCP flags':sflow[12]})
			flow.update({'IP Protocol':sflow[13]})
			flow.update({'TOS':sflow[14]})
			flow.update({'Source AS':sflow[15]})
			flow.update({'Destination AS':sflow[16]})
			flow.update({'source netmask':sflow[17]})
			flow.update({'destination netmask':sflow[18]})
			flow.update({'Pad':sflow[19]})
			
			flows.update({n:flow})		
			
		
			
	else:
		print("NetFlow version %d not supported!"%version)
	
	out=version,flows
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

	try: 
		while 1:
			data, addr = sock.recvfrom(8192)		# buffer size is 8192 bytes
			version,flows=getNetFlowData(data)		#version=0 reports an error!
			print('Version: %d'%version)
			print(flows)
	except KeyboardInterrupt:
		sock.close()
		print("\nDone!")

if __name__ == "__main__":
	main()
