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

    sourcePorts = []
    tcpFlows = []
    
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
        # Check if packet is from sender
        if sourcePort != 80:
            # Append source port and new TCP Flow
            if sourcePort not in sourcePorts:
                sourcePorts.append(sourcePort)
                tcpFlows.append([])
        # Append packet to corresponding TCP Flow
        if sourcePort in sourcePorts:
            sourceIndex = sourcePorts.index(sourcePort)
        elif destinationPort in sourcePorts:
            sourceIndex = sourcePorts.index(destinationPort)
        tcpFlows[sourceIndex].append([ts, buf])

    # Check how many flows are initiated from sender
    flowsFromSender = 0
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
        flowTime = 0
        totalFlowSize = 0
        packetsSent = 0
        packetsReceived = 0
        prev1Packet = 0
        prev2Packet = 0
        prev3Packet = 0
        prevSenderSeq = 0
        tripleDupAckRT = 0
        timeoutRT = 0

        # Print flow number and its source port
        print("\nFlow #" + str(i+1) +  ": Source Port =", sourcePorts[i])
        # Iterate through each packet in this flow
        for packet in range(len(tcpFlows[i])):
            ts = tcpFlows[i][packet][0]
            buf = tcpFlows[i][packet][1]
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            tcp = ip.data
            sourceIP = socket.inet_ntoa(ip.src)

            # Get the flow time once it reaches the last packet
            if packetIndex == len(tcpFlows[i]) - 1:
                flowTime = ts - startTime

            # If this is the first packet (SYN), get startTime
            if packetIndex == 0:
                startTime = ts
                # If this first packet is from the sender, get appropriate sequence number
                if sourceIP == sender:
                    senderSynSequenceNumber = tcp.seq
                    prevSenderSeq = tcp.seq
                    windowSizeShiftCount = tcp.opts[len(tcp.opts) - 1]

            # Else if this is the SYN/ACK packet and from receiver, get appropriate sequence number
            elif packetIndex == 1:
                if sourceIP == receiver:
                    receiverSynSequenceNumber = tcp.seq

            # Else handle packets after the 3-Way handshake
            elif packetIndex > 2:

                # Get sender packet length and append to total flow size
                if sourceIP == sender:
                    totalFlowSize += len(buf)
                    # If this packet is still before FIN, increment packets sent
                    if packetIndex < len(tcpFlows[i]) - 3:
                        packetsSent += 1
                else:
                    # If this packet is still before FIN, increment packets received
                    if packetIndex < len(tcpFlows[i]) - 3:
                        packetsReceived += 1

                # Ignore PSH, ACK packet in transactions
                if not ((tcp.flags & dpkt.tcp.TH_PUSH) and (tcp.flags & dpkt.tcp.TH_ACK)):
                    
                    # Get the window size of the packet
                    windowSize = tcp.win << windowSizeShiftCount
                    
                    # Sender to receiver packet
                    if tcp.sport != 80:
                        # Get sequence and ack number of packet,and package packet
                        sequenceNumber = abs(tcp.seq - senderSynSequenceNumber)
                        ackNumber = abs(tcp.ack - receiverSynSequenceNumber)
                        packet = [tcp.sport, tcp.dport, tcp.flags, sequenceNumber, ackNumber, windowSize, ts, len(buf)]
                        # Add a new transaction (Only worry about the first 5 transactions)
                        if len(transactions) < 5:
                            transactions.append([])
                        # Add this packet in all unfinished transactions
                        for j in range(transactionIndex, len(transactions)):
                            transactions[j].append(packet)
                        # Check if packet was retransmitted
                        if packetIndex > 6:
                            if sequenceNumber < prevSenderSeq:
                                # Check if retransmission was caused by three duplicate ACKS
                                if prev3Packet[4] == prev2Packet[4] == prev1Packet[4]:
                                    tripleDupAckRT += 1
                                else:
                                    timeoutRT += 1
                            prevSenderSeq = sequenceNumber

                    # Receiver to sender packet
                    else:
                        # Get sequence and ack number of packet, and package packet
                        sequenceNumber = abs(tcp.seq - receiverSynSequenceNumber)
                        ackNumber = abs(tcp.ack - senderSynSequenceNumber)
                        packet = [tcp.sport, tcp.dport, tcp.flags, sequenceNumber, ackNumber, windowSize, ts, len(buf)]
                        # End transactions that are fulfilled by the received packet
                        for j in range(transactionIndex, len(transactions)):
                            senderSeq = transactions[j][0][3]
                            if ackNumber == senderSeq:
                                transactions[j].append(packet)
                                transactionIndex += 1
                                break

                    # Record previous packets (For checking triple duplicate ACKS)
                    
                    prev3Packet = prev2Packet
                    prev2Packet = prev1Packet
                    prev1Packet = packet
                    
            
            # Increment index packet
            packetIndex += 1
        
        # Calculate throughput, packets not received, and loss rate
        throughput = totalFlowSize/flowTime
        packetsNotReceived = packetsSent - packetsReceived
        lossRate = packetsNotReceived/packetsSent

        # Print summary for each flow
        print("Total Time =", float("{0:.4f}".format(flowTime)), "seconds")
        print("Sender Throughput:", float("{0:.2f}".format(throughput)), "B/s =", float("{0:.2f}".format(throughput/1000)), "kB/s =", float("{0:.2f}".format(throughput/1000000)), "MB/s")
        print("Packets Sent:", packetsSent)
        print("Packets Received:", packetsReceived)
        print("LossRate:", str(float("{0:.2f}".format(lossRate*100))) + "%")
        
        # Print summary for all transactions
        for j in range(len(transactions)):
            # Only worry about the first two transactions
            if j < 2:
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

        # PART B
        print("First Five Congestion Window Sizes:")
        for j in range(len(transactions)):
            if j < 5:
                packetSent = transactions[j][0]
                packetReceived = transactions[j][len(transactions[j])-1]
                rtt =  packetReceived[6] - packetSent[6]
                totalPackets = len(transactions[j])
                totalBytes = 0
                for k in range(totalPackets):
                    totalBytes += transactions[j][k][7]
                print("\tRTT #" + str(j+1) + ":", float("{0:.4f}".format(rtt)), "seconds")
                print("\t\tTotal Packets in cwnd:", totalPackets)
                print("\t\tTotal Bytes in cwnd:", totalBytes, "B =", float("{0:.2f}".format(totalBytes/1000)), "kB")
        
        print("Total Number of Retransmissions:")
        print("\tDue to Triple Duplicate Ack:", tripleDupAckRT)
        print("\tDue to Timeout:", timeoutRT)

    # Close the PCAP file
    pcapFile.close()

# Run the program
main()