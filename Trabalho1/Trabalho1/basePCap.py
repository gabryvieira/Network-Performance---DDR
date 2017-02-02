import sys
import argparse
import pyshark
from netaddr import IPNetwork, IPAddress, IPSet

npkts=0
lastTime=0
pktUp =0
pktDown=0
byteUp = 0
byteDown = 0
strPktD = ""
strPktU = ""
interArrivalDown = 0
interArrivalUp = 0

def pkt_callback(pkt):
	global scnets
	global ssnets
	global interval
	global npkts
	global lastTime
	global pktUp
	global pktDown
	global byteUp
	global byteDown
	global strPktD
	global strPktU
	global interArrivalDown
	global interArrivalUp

	if IPAddress(pkt.ip.src) in scnets|ssnets and IPAddress(pkt.ip.dst) in scnets|ssnets:
		npkts=npkts+1
		correntTime = pkt.sniff_timestamp;
		if(float(correntTime) - float(lastTime)) < interval:
			if lastTime == 0:
				lastTime = correntTime
			if IPAddress(pkt.ip.src) in scnets:
				pktUp=pktUp+1
				byteUp = byteUp + int(pkt.ip.len)
				if pktUp == 1:
					interArrivalUp = correntTime
			else:
				pktDown=pktDown+1
				byteDown = byteDown + int(pkt.ip.len)
				if pktDown == 1:
					interArrivalDown = correntTime
			numZeros=0
		else:
			strPktD=strPktD+"[ Time: " + str(interArrivalDown)+" Number of Packets: "+ str(pktDown) + " Number of Bytes: "+str(byteDown)+"]"
			strPktU=strPktU+"[ Time: " + str(interArrivalUp)+" Number of Packets: "+ str(pktUp) + " Number of Bytes: "+str(byteUp)+"]"
			if lastTime == 0:
				lastTime = correntTime
			numZeros = int((float(correntTime) - float(lastTime)) *10)
			lastTime = correntTime
			while numZeros > 0:
				strPktD=strPktD+" 0"
				strPktU=strPktU+" 0"
				numZeros = numZeros-1		
			if IPAddress(pkt.ip.src) in scnets:			
				pktUp =1
				pktDown=0
				byteUp =int(pkt.ip.len)
				interArrivalUp = lastTime
			else:
				pktUp =0
				pktDown=1
				byteDown = int(pkt.ip.len)
				interArrivalDown = lastTime
		if pkt.ip.proto=='17':
			print('%s: IP packet from %s to %s (UDP:%s) %s'%(pkt.sniff_timestamp,pkt.ip.src,pkt.ip.dst,pkt.udp.dstport,pkt.ip.len))
		elif pkt.ip.proto=='6':
			print('%s: IP packet from %s to %s (TCP:%s) %s'%(pkt.sniff_timestamp,pkt.ip.src,pkt.ip.dst,pkt.tcp.dstport,pkt.ip.len))
		else:
			print('%s: IP packet from %s to %s (other) %s'%(pkt.sniff_timestamp, pkt.ip.src,pkt.ip.dst,pkt.ip.len))


def main():
	
	parser=argparse.ArgumentParser()
	parser.add_argument('-i', '--interface', nargs='?',required=True, help='capture interface')
	parser.add_argument('-c', '--cnet', nargs='+',required=True, help='client network(s)')
	parser.add_argument('-s', '--snet', nargs='+',required=True, help='service network(s)')
	parser.add_argument('-t', '--tcpport', nargs='?',help='service TCP port (or range)')
	parser.add_argument('-u', '--udpport', nargs='?',help='service UDP port (or range)')
	parser.add_argument('-l', '--loop', type=float, help='sampling interval (seconds)',default=0.1)
	args=parser.parse_args()
	
	global interval
	interval = args.loop
		
	cnets=[]
	for n in args.cnet:
		try:
			nn=IPNetwork(n)
			cnets.append(nn)
		except:
			print('%s is not a network prefix'%n)
	print(cnets)
	if len(cnets)==0:
		print("No valid client network prefixes.")
		sys.exit()
	global scnets
	scnets=IPSet(cnets)

	snets=[]
	for n in args.snet:
		try:
			nn=IPNetwork(n)
			snets.append(nn)
		except:
			print('%s is not a network prefix'%n)
	print(snets)
	if len(snets)==0:
		print("No valid service network prefixes.")
		sys.exit()
		
	global ssnets
	ssnets=IPSet(snets)
		
	if args.udpport is not None:
		cfilter='udp portrange '+args.udpport
	elif args.tcpport is not None:
		cfilter='tcp portrange '+args.tcpport
	else:
		cfilter='ip'
	
	cint=args.interface
	print('Filter: %s on %s'%(cfilter,cint))
	try:
		capture = pyshark.LiveCapture(interface=cint,bpf_filter=cfilter)
		capture.apply_on_packets(pkt_callback)
	except KeyboardInterrupt:
		global npkts
		global strPktD
		global strPktU
		fUp = open('upPktsBytes.txt','w')
		fDown = open('downPktsBytes.txt','w')			
		fUp.write(strPktU)
		fDown.write(strPktD)
		fUp.close()
		fDown.close()
		print('\n%d packets captured! Done!\n'%npkts)

if __name__ == '__main__':
    main()
