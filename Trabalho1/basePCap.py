import sys
import argparse
import pyshark
from netaddr import IPNetwork, IPAddress, IPSet

npkts=0

last_interval = 0;

def pkt_callback(pkt):
	global scnets
	global ssnets
	global npkts

	if IPAddress(pkt.ip.src) in scnets|ssnets and IPAddress(pkt.ip.dst) in scnets|ssnets:
		npkts=npkts+1
		
		nPackets_sameInterval = 0;
		current_interval = pkt.sniff.timestamp
		if(current_interval - last_interval < 0.1)		
			nPackets_sameInterval++;
		
		
		else if(current_interval - last_interval >= 0.1)
			nPackets_sameInterval++;
					
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
	args=parser.parse_args()
	
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
		print('\n%d packets captured! Done!\n'%npkts)

if __name__ == '__main__':
    main()
