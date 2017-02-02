from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy import mib
import time
import re
import argparse

def IPfromOctetString(t,s):
	if t==1 or t==3:	#IPv4 global, non-global
		return '.'.join(['%d' % ord(x) for x in s])
	elif t==2 or t==4:	#IPv6 global, non-global
		a=':'.join(['%02X%02X' % (ord(s[i]),ord(s[i+1])) for i in range(0,16,2)])
		return re.sub(':{1,}:','::',re.sub(':0*',':',a))

def main():
	mib.path(mib.path()+":/usr/share/mibs/cisco")
	load("SNMPv2-MIB")
	load("IF-MIB")
	load("IP-MIB")
	load("RFC1213-MIB")
	load("CISCO-QUEUE-MIB")
	#Requires MIB RFC-1212 (add to /usr/share/mibs/ietf/)
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--router', nargs='?',required=True, help='address of router to monitor')
	parser.add_argument('-s', '--sinterval', type=int, help='sampling interval (seconds)',default=5)
	args=parser.parse_args()
	
	
	print("time: ",args.sinterval)
	print("argumentos" ,args)

	#Creates SNMP manager for router with address args.router
	m=M(args.router,'private',3, secname='uDDR',authprotocol="MD5", authpassword="authpass",privprotocol="AES", privpassword="privpass")

	print(m.sysDescr)	#Gets sysDescr from SNMPv2-MIB

	print("===")

	print(m.ifDescr.items()) #Lists (order, name) interfaces in ifDescr from IF-MIB

	for i, name in m.ifDescr.items():
		print("Interface order %d: %s" % (i, name))

	print("===")

	print(m.ipAddressIfIndex.items()) #Lists ((adr.type,adr),order) interfaces in ipAddressIfIndex from IP-MIB

	ifWithAddr={};	#Stores (order, first adr.) of all interfaces
	PktsOut = {};
	
	tempo = args.sinterval
	print tempo
	#exercicio 4
	while True:
		time.sleep(args.sinterval)		
		for addr, i in m.ipAddressIfIndex.items():  # percorre todas as interfaces
			if not i in ifWithAddr:
				ifWithAddr.update({i:IPfromOctetString(addr[0],addr[1])})
				PktsOut.update({i:m.ifHCOutUcastPkts})
				PktsOut.update({i:m.ifHCInUcastPkts})
				PktsOut.update({i:m.ifHCOutOctets})
				PktsOut.update({i:m.ifHCInOctets})
				PktsOut.update({i:m.cQStatsDepth})

			#print('%s, Interface order: %d, %s'%(IPfromOctetString(addr[0],addr[1]),i,m.ifDescr[i]))
			print("")
			print("---------Initial values---------")
			print('%s, Interface order: %d, %s'%(IPfromOctetString(addr[0],addr[1]),i,m.ifDescr[i]))
			print("%s, Packets Out: %s"%(IPfromOctetString(addr[0],addr[1]), m.ifHCOutUcastPkts[i]))
			print("%s, Packets In: %s"%(IPfromOctetString(addr[0],addr[1]), m.ifHCInUcastPkts[i]))
			print("%s, Octets Out: %s"%(IPfromOctetString(addr[0],addr[1]), m.ifHCOutOctets[i]))
			print("%s, Octets In: %s"%(IPfromOctetString(addr[0],addr[1]), m.ifHCInOctets[i]))
			print("%s, Depth: %s"%(IPfromOctetString(addr[0],addr[1]), m.cQStatsDepth[i,2]))
			
			print("")
			print(ifWithAddr)
			print(PktsOut)

			print("===")
	
	#exercicio 5
if __name__ == "__main__":
	main()
