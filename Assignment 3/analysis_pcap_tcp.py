# Daniel Garcia
# ID: 111157499

import dpkt
import socket
import sys


# Name of PCAP file to be parsed through
fileName = 'assignment3.pcap'

def main():

    # Output results to a separate file
    sys.stdout = open('pcapsummary.txt', 'w')

    # Open and read the PCAP file in bytes
    pcapFile = open(fileName, "rb")
    pcap = dpkt.pcap.Reader(pcapFile)

    # IP Addresses of sender and receiver
    sender = '130.245.145.12'
    receiver = '128.208.2.198'

    # Variables
    sourcePorts = []
    tcpFlows = []
    senderPackets = 0
    flowsFromSender = 0

    # Iterate through each packet in the PCAP file
    for ts, buf in pcap:

        # Parse the bytes into an Ethernet object
        eth = dpkt.ethernet.Ethernet(buf)

        # Check if this is an IP packet
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue
        ip = eth.data
        
        # Check if this is a TCP packet
        if ip.p != dpkt.ip.IP_PROTO_TCP:
            continue
        tcp = ip.data

        sourcePort = tcp.sport
        destinationPort = tcp.dport
        # Check
        if sourcePort != 80:
            if sourcePort not in sourcePorts:
                sourcePorts.append(sourcePort)
                tcpFlows.append([])
        sourceIndex = 0
        if sourcePort in sourcePorts:
            sourceIndex = sourcePorts.index(sourcePort)
        elif destinationPort in sourcePorts:
            sourceIndex = sourcePorts.index(destinationPort)
        tcpFlows[sourceIndex].append([ts, buf])

    # Check how many flows are initiated from sender
    for i in range(len(tcpFlows)):
        buf = tcpFlows[i][0][1]
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        tcp = ip.data
        # Check if this flow is initiated from sender
        sourceIP = socket.inet_ntoa(ip.src)
        if sourceIP == sender:
            flowsFromSender += 1

    print("TCP Flows initiated from the sender:", flowsFromSender)

    # Iterate through each packet in each flow from sender
    for i in range(flowsFromSender):
        packetIndex = 0
        senderSynSequenceNumber = 0
        receiverSynSequenceNumber = 0
        transactions = []
        transactionIndex = 0
        startTime = 0
        endTime = 0
        flowTime = 0
        totalFlowSize = 0
        packetsSent = 0
        packetsReceived = 0

        print("\nFlow #" + str(i+1) +  ": Source Port =", sourcePorts[i])

        for packet in range(len(tcpFlows[i])):
            ts = tcpFlows[i][packet][0]
            buf = tcpFlows[i][packet][1]
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            tcp = ip.data
            sourceIP = socket.inet_ntoa(ip.src)

            if packetIndex == len(tcpFlows[i]) - 1:
                endTime = ts
                flowTime = endTime - startTime

            if packetIndex == 0:
                startTime = ts
                if sourceIP == sender:
                    senderSynSequenceNumber = tcp.seq
                    windowSizeShiftCount = tcp.opts[len(tcp.opts) - 1]
            
            elif packetIndex == 1:
                if sourceIP == receiver:
                    receiverSynSequenceNumber = tcp.seq
            
            # Skip the 3-Way Handshake
            elif packetIndex > 2:
                # Get sender packet length and append to total flow size
                if sourceIP == sender:
                    totalFlowSize += len(buf)
                    if packetIndex < len(tcpFlows[i]) - 3:
                        packetsSent += 1
                else:
                    if packetIndex < len(tcpFlows[i]) - 3:
                        packetsReceived += 1
                # Ignore PSH, ACK packet in transactions
                if not ((tcp.flags & dpkt.tcp.TH_PUSH) and (tcp.flags & dpkt.tcp.TH_ACK)):
                    # Get the window size of the packet
                    windowSize = tcp.win << windowSizeShiftCount
                    # Get sequence and ack number of packet
                    if tcp.sport != 80:
                        # Sender to receiver packet
                        sequenceNumber = abs(tcp.seq - senderSynSequenceNumber)
                        ackNumber = abs(tcp.ack - receiverSynSequenceNumber)
                        if len(transactions) < 2:
                            transactions.append([])
                        packet = [tcp.sport, tcp.dport, tcp.flags, sequenceNumber, ackNumber, windowSize]
                        for j in range(transactionIndex, len(transactions)):
                            transactions[j].append(packet)
                        
                    else:
                        # Receiver to sender packet
                        sequenceNumber = abs(tcp.seq - receiverSynSequenceNumber)
                        ackNumber = abs(tcp.ack - senderSynSequenceNumber)
                        packet = [tcp.sport, tcp.dport, tcp.flags, sequenceNumber, ackNumber, windowSize]
                        for j in range(transactionIndex, len(transactions)):
                            senderSeq = transactions[j][0][3]
                            if ackNumber == senderSeq:
                                transactions[j].append(packet)
                                transactionIndex += 1
                                break
                    
            packetIndex += 1
        
        throughput = totalFlowSize/flowTime
        packetsNotReceived = packetsSent - packetsReceived
        lossRate = packetsNotReceived/packetsSent
        print("Total Time =", float("{0:.4f}".format(flowTime)), "seconds")
        print("Sender Throughput:", float("{0:.2f}".format(throughput)), "B/s =", float("{0:.2f}".format(throughput/1000)), "kB/s =", float("{0:.2f}".format(throughput/1000000)), "MB/s")
        print("Packets Sent:", packetsSent)
        print("Packets Received:", packetsReceived)
        print("LossRate:", str(float("{0:.2f}".format(lossRate*100))) + "%")
        
        for j in range(len(transactions)):
            if j == 2:
                break
            print("Transaction #" + str(j+1) + ":")
            packetSent = transactions[j][0]
            packetReceived = transactions[j][len(transactions[j])-1]
            print("\tPacket Sent:")
            print("\t\tSequence Number:", packetSent[3])
            print("\t\tAck Number:", packetSent[4])
            print("\t\tReceive Window Size:", packetSent[5])
            print("\tPacket Received:")
            print("\t\tSequence Number:", packetReceived[3])
            print("\t\tAck Number:", packetReceived[4])
            print("\t\tReceive Window Size:", packetReceived[5])

    pcapFile.close()

main()