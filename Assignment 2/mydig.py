# Daniel Garcia
# ID: 111157499

import dns.name
import dns.message
import dns.query
import sys
import time
import datetime

# Set DNS Server to check (Currenty set to a.root-servers.net)
rootServer = "198.41.0.4"

def main():

    # Output to a separate file
    sys.stdout = open('mydig_output.txt', 'w')

    # Create list for list of domains to check
    domainList = []

    # Check if no domains are entered in the command line
    if len(sys.argv) < 2:
        domainList.append("")
    # Else, add all domains from the command line
    else:
        for i in range(1, len(sys.argv)):
            domainList.append(sys.argv[i])

    # Call myDig for each domain
    for domain in domainList:

        # Take the domain name and make it into dns.name.Name object
        domainName = dns.name.from_text(domain)

        # Make a query using the domain name of type A
        dnsRequest = dns.message.make_query(domainName, dns.rdatatype.A)

        # Output the question
        print("QUESTION SECTION:")
        for question in dnsRequest.question:
            print(str(question),"\n")

        # Start the timer
        startTime = time.time()

        # Perform the DNS lookup (Recursion possible)
        dnsAnswerList = []
        myDig(dnsRequest, rootServer, dnsAnswerList)

        # End the timer
        endTime = time.time()

        # Output the answer section
        print("ANSWER SECTION:")
        length = 0
        for answer in dnsAnswerList:
            length += len(answer)
            print(answer)
        print("")

        # Output time it took to resolve query
        mSecs = int((endTime - startTime) * 1000)
        print("Query time:", mSecs, "msec")

        # Output the current date
        currentDate = datetime.datetime.now()
        currentDate = currentDate.strftime("%a %b %d %H:%M:%S %Y")
        print("WHEN:", currentDate)

        # Output the answer length
        print("MSG SIZE rcvd:", length, "\n")

# Recursive function to do a DNS lookup for each server
def myDig(dnsRequest, dnsServer, dnsAnswerList):

    # Get the UDP response for this server
    dnsResponse = dns.query.udp(dnsRequest, dnsServer, timeout=60)
    for answer in dnsResponse.answer:
        strAnswer = str(answer.to_text())
        allAnswers = strAnswer.split("\n")
        for indivAnswer in allAnswers:
            if (indivAnswer not in dnsAnswerList):
                dnsAnswerList.append(indivAnswer)
    
    # Iterate through each additional response
    for answer in dnsResponse.additional:
        strAnswer = str(answer.to_text())
        
        # Skip answer if it is an AAAA record
        if (strAnswer.find("IN AAAA") != -1):
            continue
        elif (strAnswer.find("IN A") != -1):
            ip = str(answer[0])
            myDig(dnsRequest, ip, dnsAnswerList)

    # Return the function if there are answers
    if len(dnsAnswerList) != 0:
        return

    # Otherwise, iterate through authority Responses
    for answer in dnsResponse.authority:
        strAnswer = str(answer.to_text())
        if (strAnswer.find("IN NS") != -1):
            hostname = str(answer[0])
            NSList = []
            domainName = dns.name.from_text(hostname)
            newRequest = dns.message.make_query(domainName, dns.rdatatype.A)
            myDig(newRequest, rootServer, NSList)
            for nsAnswer in NSList:
                if (nsAnswer.find("IN A") != -1):
                    ip = nsAnswer[nsAnswer.find("IN A") + 5:]
                    myDig(dnsRequest, ip, dnsAnswerList)

# Start program
main()