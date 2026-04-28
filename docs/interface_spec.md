# Interface Specification

*(This document was populated from Iris Whitepaper v0.3)*

## Network Node Types

Iris will operate as a DON with three kinds of nodes: Regular, Bootstrap and Leader nodes.
1. Bootstrap Node: A node that connects to Normal Nodes, establishes connections between them and begins an OCR round. 
2. Regular Node: A node that acts as a web server to fetch satellite imagery through authenticated API calls.
3. Leader Node: A node that collects image data from Regular Nodes. It then performs computer vision powered image similarity comparisons and creates a general report capturing the Area of Interest’s Average Scenario.




## OCR Consensus Steps

Steps:
1. Bootstrap Node finds other Iris nodes looking to participate in a committee of nodes for one round. The logic is processed through a smart contract by which users will be rewarded. 
2. All nodes are required to stake IRIS tokens in order to participate.
3. The smart contract then picks a random node from the committee and assigns it as the Leader Node. This aggregator node sends requests to the other nodes in the committee. All of whom at this point are considered Regular Nodes.
4. The Regular Nodes fetch the satellite imagery requested and generate their hash. They create a final report off-chain that includes the image hash, database web address of the image and the Regular Node’s  signature.
5. The Leader Node receives the reports from all the other nodes in the committee. It fetches the images from the web addresses provided in the reports. The images are compared against each other and results in the capturing of the area’s Average Scenario.
   1. The Regular Nodes that provided images close to the Average Scenario are more likely to be honest because they were close to the majority of all other images. Therefore the smart contract rewards the regular nodes.
   2. The Regular Nodes whose images are statistically dissimilar to the Average Scenario have their stakes tokens burnt as punishment. Again the smart contract executes the penalty.
6. The Leader Node creates a report which includes the hash and the web address of the image chosen as the Average Scenario, along with the regular and aggregator nodes signatures. The report is sent to the requesting smart contract and recorded on-chain. The Leader Node is rewarded extra for performing the computation.



## Dapp Integration Steps

They operate together in the following steps:
1. A user interacts with the dapp through a traditional web 2.0 frontend web app.
2. An executable or operator contract receives the request for information from the data specified on the frontend. Sends requests to data distilling DON for actionable data.
3. Data Distilling DON or DD-DON requests image data from Iris DON.
4. Iris DON nodes request imagery data on Area of Interest (AoI) from satellite constellations.
5. Iris DON compares node images, chooses the image closest to all others to be hashed, saves image on database and image hash on blockchain.
6. The DD-DON receives image hash from Iris DON and verifies the hash provided. The DD-DON’s nodes compute, compare and produce a single-value real-world attribute - otherwise known as Actionable Data and send it to the Executable.
7. The Executable is the Chainlink 2.0 whitepaper’s definition of a smart contract whose actions change pre programmed states - otherwise known as a smart contract(s). The executable relays the state changes over to the frontend to inform the user.  
  
