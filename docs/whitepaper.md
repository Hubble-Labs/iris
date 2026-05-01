Goal: Define the high-level vision and goals of the protocol. What is broken in the world that Iris fixes.

Key Sections:
- Introduction: What is Iris and why does it matter?
- Problem Statement: What is broken in the world that Iris fixes?
- Solution: How does Iris fix it?
- Vision: What is the long-term vision for Iris?


# Iris Whitepaper
_By Salvador Salcedo_

## Introduction
Iris is a Decentralized Terrestrial Satellite Oracle Network or DtsON. It will serve as the network that exists through the communication between the nodes working together to determine the provenance of the requested satellite imagery. Like current oracle networks, such as those built on Chainlink, Iris will allow developers to create new decentralized applications, or dapps, that were impractical or impossible before.  


### Problem Statement
Iris was born out of the desire to combine space and blockchain technologies together in a single solution or product. Cryptocurrency markets and DeFi as a whole are global markets where the action never stops. Assets like Bitcoin and Ethereum exist in extremely lively environments. Their prices have changed rapidly in the past and changes can typically be measured in seconds. For everyday people to interact with others through dapps, those services need to agree on what the prices of the said assets are. Oracles and the networks they comprise act to produce accurate external, real-world data for blockspace-bound smart contract logic. However, the applications of oracle networks extend far beyond the accurate reporting of Bitcoin prices. Iris aims to be the first project to extend oracle functionality beyond the use of single numerical values


Of course oracles aren’t new. Chainlink is the largest oracle network project and has arguably contributed the most to the development of oracle networks. As of May 2022, the TVL of projects that depend on the Chainlink network’s successful operation or Total Value Secured (TVS) is $38.3bn. That is 52% of all the value secured by oracle networks. It is no surprise then, that their oracle networks have allowed web3’s most popular defi applications to maintain accurate price data for years now.


They do so by creating and distributing software, known as a Chainlink Client, which runs on a user's computer and turns it into a Node. Nodes are the computers that comprise oracle networks and perform the computations required to report accurate data back to dapps and smart contracts. Dapps and their services are part of the DeFi world that never sleeps because their openness makes their use constant and ubiquitous. While they have developed ways for committees of nodes, or oracle networks, to reach consensus on the value of a single asset, they have yet to produce a way to do so for images. 


### Solution
Satellites, for reasons we will discuss shortly, are a great source for imagery data to use in decentralized applications. Therefore, satellite imagery is a good data-type for oracle networks to verify the provenance of. One of the biggest reasons for doing so is that the infrastructure to request satellite imagery, as long as you’re willing to wait a day or two, already exists from companies like Maxar, Planet and BlackSky. Of course these services aren’t free. Thankfully, the nodes in an oracle network are paid for participating and it is assumed that the node’s reward will cover the service fee. Another advantage is that all satellites inherently have a similar view of the target area. With the correct post-processing, it would be easy for nodes to produce similar images thereby making it easier to detect similarity or lack thereof. 


A DtsON as described above would create receipts in the form of hashes of what a part of the Earth looked like at a certain time. A blockchain in this case would serve as the database where the hashes will be publicly stored as long as the blockchain exists. 


A DtsON like Iris, and the photos it processes, will allow developers to build other Decentralized Oracle Networks or DONs, to distill information from the images and ultimately send simpler data for Smart Contracts (SCs) to react to. This paradigm of chaining DONs, like Iris, together to simplify real world data into actionable data points, like price data, could be the way future Decentralized Applications (dapps) are built. Iris will be the first solution to use a Byzantine Fault Tolerant (BFT) consensus mechanism to verify the similarity and therefore validity or provenance, of satellite imagery.

### Vision
Applications & Future


Iris is an infrastructure protocol. Thus the end user is never meant to see or interact with it. The technology behind Iris is nothing new. Blockchain, machine learning, image comparison algorithms and the other technologies behind Iris already exist, they just haven’t been combined together in this way before. Because oracle networks and the ways applications depend on them might not be well know by the average reader, I have listed some of my favorite dapp ideas one can build on top of Iris. 


Kokiri: Voluntary Carbon-Sequestering Asset Tokenization and Market

1. The Situation 
It is no secret that the Earth is warming up due to the over-accumulation of greenhouse gasses in the atmosphere. For years now activists have been sounding the alarm on the dangers of global warming. One of the things to come out of our new awareness and effort to slow, or optimistically reverse, the warming of the earth are carbon credits. 

One carbon credit represents one 1 ton of CO2 removed from the atmosphere. They are created when an individual’s or organization’s project reduces, avoids, destroys or captures carbon. Typically, mostly companies but individuals also buy carbon credits to offset their own emissions. There exist two types of carbon credit markets: voluntary and involuntary.


The voluntary carbon credits are bought by people or organizations that want to reduce their carbon footprint for any number of reasons. Certain industries, especially heavy polluters, have restrictions on how much carbon they can emit over a year. These companies are therefore forced to either reduce their carbon emissions or buy carbon credits to offset what they released. Carbon credits bought under the ¿previous circumstance are known as involuntary carbon credits.


2. The Problem 
While the carbon credit markets have continued to grow as we realize the error of our ways, its current incarnation is far from perfect.


First, there is no way for the entity buying carbon credits to verify that each ton of CO2 the credits represent was actually removed from the atmosphere. Therefore the issuing of carbon credits by individuals, organizations and governments is susceptible to fraud through every pair of hands the credits passed through before reaching the buyer. 


Another issue is that the current carbon credit markets are difficult to access and assess. Different markets across different countries have very different prices for their carbon credits. If the current system was truly open and available to everyone then there wouldn’t be such large differences in price due to the arbitrage opportunities the difference creates. If an individual wants to buy a carbon credit, they don’t go to an exchange like you do for stocks and crypto. One has to trust the organizations creating and selling the carbon credits are being honest. 


Finally, it is difficult for people to create carbon credits on their own. Today, if someone wants to create and sell carbon credits based on a personal carbon reduction project, they have to reach out to an organization that buys it off of them. 




3. The Solution 


With Iris, developers could use the imagery provided by the DtsON to extract information on forestry and agricultural efforts to capture carbon and therefore mint tokens representing those assets.


Developers could build a user-facing dapp, that requires 4 pairs of coordinates detailing the Area of Interest (AoI), the type of vegetation grown, verification that they own the AoI and the gas required for the dapp. Once a user submits the information required, their request will be sent from the dapp to Iris. Iris nodes then fetch and decide which image is closest to all the others and sends it back to the dapp. The dapp would then use their own OCRM DON where the nodes run a data science or machine learning model off-chain to distill a figure, such as vegetation percentage, from the image returned by Iris. Once the aggregate value is decided and the aggregation round ends their DON then send the aggregate to the dapp’s smart contract. The dapps smart contract then uses this numerical data to decide what action to take. In this scenario, the contract has to decide how many tokens representing carbon sequestering assets to mint. 


A solution such as the one described above would not only get rid of the fraud and inaccessibility of the current carbon credit market but create an entirely new global decentralized market. 






Global Crop Insurance


1. The Situation


Since the dawn of civilization, humanity has had to deal with poor weather causing poor harvests. Through our history we have devised ways to counter poor harvests through communal grain storage, trade and finally crop insurance. 


2. The Problem


Farmers in most developed countries today can buy crop insurance from organizations that offer those services. However, many farmers in developing countries do not have access to crop insurance for one reason or another. Often farmers can’t afford the insurance, live in areas not covered by any companies or the crop insurance companies won’t serve them since it wouldn’t be profitable enough to do so. 


With the majority of the world’s farmers being among the poorest people in the world, a solution to the current issues with crop insurance would go a long way in helping the hands that feed us.


3. The Solution


With Iris, developers can create a dapp where farmers can sign up for crop insurance using 4 coordinate points representing the AoI, proof they own AoI, what type of crop they’re crowing, the premium and claim amount and the gas required. Assuming the user pays their premium on time, every monththe dapp can request Iris to acquire an image of the AoI. Once Iris sends back the image of the AoI, the dapp devs feed it to an application specific DON that determines the moisture in the ground and sends it to the dapp’s smart contract. 


If the farmer submits a claim, the smart contract will go through the data fed it by the application specific DON and determine whether or not to payout.
Because it is a dapp, anyone with an internet connection and enough money to pay for gas and the premiums would be able to take out a crop insurance policy and receive a payout in the event of poor harvest.


Research Lab and Distributed Constellations


An active barrier to the successful implementation of Iris is the accessibility of satellite imagery. Though it is true that some companies sell satellite imagery as a service, access to these services is relatively limited to individuals. Therefore in the spirit of decentralization and accessibility, the Iris team's legal entity/company will also create and launch compact imagery satellites with the intent of selling the imagery collected by them to Iris node operators. Thankfully, cubesats can be made for as little as a couple thousand dollars. Launches for cubesats on rideshare missions also offer competitive pricing for launching small cubesats. Such endeavors would easily be within the reach of an organization like Chainlink with their millions of dollars in funding from their LINK tokens and business dealings.


Another goal of this future project will be to provide the resources necessary for other organizations, such as traditional business or DAOs, to build and launch their own imaging cubesats. Having multiple open image data services will be instrumental in securing the decentralization of Iris and will prove higher levels of confidence in our DON's data sources.




## Glossary

* Actionable Data: Describes real-world data that a smart contract can ingest and use to carry out decisions in a computationally efficient way.
* Byzantine Fault Tolerant: A description assigned to a consensus mechanism designed to guarantee the authenticity of communications between honest and potentially adversarial participants. 
* Cubesat: A class of miniaturized satellite based around a form factor consisting of 10 cm cubes.
* Decentralized Applications: Web applications that users access through the internet that rely on smart contracts and underlying blockchain technology to execute an economic transaction or function.
* Node: A computer that runs specialized software meant only to request and send data from a real-world data-source.
* Oracle: A node/computer that participates in providing data to a larger set of nodes known as an oracle network.
* Provenance: The origin of data and the process by which it arrived at the database.
