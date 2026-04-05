# Architecture

*(This document was populated from Iris Whitepaper v0.3)*

Oracle Network Architectures

An oracle network is a group of computers, or Nodes, that each fetch data representing a real-world attribute from one or more data sources. For Iris, we can have DONs that have access to multiple satellite imagery providers like Maxar and Planet Labs, or DONs that compare images of one constellation over a short period of time. For reasons discussed below, the features of the terrain will allow the DONs to compute the image’s similarities. The oracle network does so by collecting each image from participants and using a comparison algorithm to determine which ones can and cannot inform the final value. Before we dive into Iris’ consensus mechanism we will explore existing oracle paradigms.

* Basic Request Model (BRM)

Before the need and invention of the DDM, the only way to get data from off-chain to on-chain was to use a centralized oracle. A singular source of trust with a proven reputation. This singular source of data had to be completely trusted and reliable. If the oracle was compromised or malicious, the entire system would be at risk. Naturally they would have to be a party whose value came from providing honest and reliable data. Google is an example of a company that has built a reputation for providing reliable data and using that to bring people to their platform. This would include applications that some users might think are free or freemium like Google Maps, Google Search and even Youtube. Their business model of serving ads and therefore selling user data to advertisers is how people truly pay for these applications. This is all just to explain that sometimes centralized oracles are fine. But they are not always the best solution. 

No single source of infromation is completely reliable however. In the case of Google again we have seen a degredation in the quality of their search results over the years. One could call this a bias in this case since its a for profit megacorporation it has grown to prioritize profit over the quality of its service. One way to get rid of this bias is to use mathematics to get the right answer no matter the bias. 

* Decentralized Data Model (DDM)

A good example to convey how DONs of the Decentralized Data Model variety work is Chainlink’s Bitcoin price DON that reports the price of BTC/USD. As of May 10th, it has 31 nodes and agrees on a new aggregate or average value every minute or so. In a DON such as this one, each node reports the price of Bitcoin in dollars to an Aggregation Smart Contract (ASC). In addition, they must deposit some tokens, in this case LINK tokens, to serve as a deposit to be burned or returned based on their honesty. In the case that the node acts honestly they will be rewarded a small amount of LINK coins for participating and their deposit gets saved for the next round of aggregation. The rewards and penalties therefore serve as economic incentives for people to run oracle software on their computers and report data honestly. Once the data is submitted by all members of the network, otherwise known as a committee, the ASC finds the statistical average and defines it as the value of Bitcoin. Depending on the DON, the ASC might decide to penalize nodes that submitted data found to be too statistically dissimilar to the aggregate. In this case, the ASC will burn their deposited LINK. The value determined by the ASC can then be read by developers and integrated into their decentralized applications. This type of DON architecture is known as the Decentralized Data Model.

* Off-Chain Reporting Model (OCRM)

Since the release of Chainlink’s DDM, they have come up with a more gas-efficient variant named the Off-Chain Reporting Model. The main difference between the OCRM and DDM is that the computation and independent node reporting happen off-chain with only one report with the final answer being submitted on-chain. This is all thanks to OCRM adopting a peer-to-peer or P2P network separate from the main-chain the OCRM DON runs on. It works as follows. First, a node creates the P2P network with all the other nodes that are interested in being a part of it. Then, each node fetches information from a data-source and performs any number of computations on the data as decided by the DON. Now instead of the nodes submitting to an Aggregation Smart Contract (ASC) on-chain, the P2P network randomly selects a node, known as the Leader Node, to act as an off-chain version of the ASC. The leader node then collects the signatures of all participating nodes, their reported values and compares them to find an average and therefore aggregate value. If some values sit too far away from the average, perhaps a Standard Deviation or two, it may be considered a dishonest result. Finally, the selected node creates a single report containing the DON’s decided upon value and the signature of every participating node. The report is then sent on-chain to be recorded and used by developers. Off-Chain Reporting Model DONs, like Decentralized Data Model DONs, also reward honest nodes while penalizing dishonest nodes as decided by the comparison mechanism.

Due to the complexity required to compute the aggregate of images, Iris will be built using the OCR model. This way both the nodes and aggregator nodes can perform the necessary computations off-chain inexpensively compared to if they were done on-chain. 

Data-Feeds

1. Price Feeds

The most popular data-feeds are single value numerical values representing the worth of one asset versus another. For example, ETH/USD is a data-feed whose value represents the exchange ratio between Ethereum and the US Dollar and is used by lots of dapps. Feeds such as ETH/USD are created by aggregating the value of ETH/USD from different exchanges and markets. This includes centralized ones like Binance and Coinbase but also decentralized ones like Uniswap. This by far is the most popular data-type. So much so that new oracle projects reporting price data are being created without much in the way of differentiation. 

2. Non-Financial Data

Aside from financial data, DONs can also verify any type of real-world attribute or data-point. This includes weather data, sport outcomes, flight arrival/departure times, etc. For reasons unknown to me it seems that these data types haven't enjoyed as much use as price feeds. 

Most contemporary oracle networks that are formed only verify single numerical values. This is because smart contracts can only act upon simple or what I like to call Smart-Contract-Ready Data to save gas. Smart-Contract-Ready Data is a loose concept meant to describe real-world data that a smart contract can ingest and use to carry out decisions in a computationally efficient way. Iris will be the first project to verify the provenance of satellite imagery and offer a richer data type in the form of satellite images for new dapps to use.

Iris DON Overview

The Iris-powered dapp paradigm will be made up of five major parts. The dapp frontend, executable or operator contract, data distilling DON, the Iris DON and the imagery data source. 

They operate together in the following steps:
1. A user interacts with the dapp through a traditional web 2.0 frontend web app.
2. An executable or operator contract receives the request for information from the data specified on the frontend. Sends requests to data distilling DON for actionable data.
3. Data Distilling DON or DD-DON requests image data from Iris DON.
4. Iris DON nodes request imagery data on Area of Interest (AoI) from satellite constellations.
5. Iris DON compares node images, chooses the image closest to all others to be hashed, saves image on database and image hash on blockchain.
6. The DD-DON receives image hash from Iris DON and verifies the hash provided. The DD-DON’s nodes compute, compare and produce a single-value real-world attribute - otherwise known as Actionable Data and send it to the Executable.
7. The Executable is the Chainlink 2.0 whitepaper’s definition of a smart contract whose actions change pre programmed states - otherwise known as a smart contract(s). The executable relays the state changes over to the frontend to inform the user.  

1. Dapps

Of all conceptualizations of EVM and the Ethereum blockchain, none is more helpful than that of the state machine. The Ethereum network is essentially one large database or ledger known as a blockchain that holds information about the state of all participants in the network. These participants are represented by wallets and principally referred to on the network by their wallet's address. The wallets may be personal wallets managed by real people or part of smart contracts managed by other smart contracts. 

Smart contracts are programs that run on the Ethereum state machine and execute changes to the states of wallets. A change to the state of the Ethereum state machine is carried out by executing a transaction. These transactions are codified through smart contracts and are executed by special types of network participants named Miners. Miners bundle up these transactions and have the opportunity to submit them to the Blockchain. It is easy to see why this technology lends itself easily to computations of financial transactions. 

A dapp is a collection of software or software stack that performs a computation on a state-space computer on the behalf of a user. In DeFi, these dapps are used to change the states of users’ wallets in the form of financial products and tools.

Among the many popular DeFi products and services that exist, very few rely heavily on data generated solely off-chain. Because such applications rely on data that must be 100% accurate all the time, trust is the most essential element an oracle service can provide. Thankfully, images are a data type that humans understand very well without needing much context. Dapp developers can easily choose to show the images their dapps are using to inform the smart contracts. 

2. Iris DON

The heart of the project will be the Iris DON. It is intended to be an infrastructure layer for dapps. It will receive requests from a data distilling DON or DD-DON and establish the provenance of satellite imagery so that the information kept within them can be used for decentralized applications. 

    In the MVP’s most ideal form, the Iris DON nodes will be able to:
    1. Fetch satellite images through constellation service APIs off-chain
    2. Submit the images for comparison to an OCR committee
    3. Compute satellite image similarity
    4. Reward and/or punish DON participants
    5. Produce image data hash 
    6. Store the hash on-chain
    7. Store the image in a decentralized database solution
    8. Return the results to the requesting DD-DON.         

3. Sequentials DONS

Decentralized applications or dapps built upon Iris will follow a paradigm different from other dapps for receiving actionable data. Actionable data is data that is ready to be processed or consumed by a smart contract to inform a decision. Typically these decisions take the form of financial transactions. The reason we have to consider the consumability of data in the first place, is because smart contracts do not perform complex computations cost effectively. These are caused by inherent limitations to current blockchain networks. While these limitations might generally be overcome soon by the Ethereum foundation’s first major redesign of the Ethereum network since its invention, we must still move the bulk of computations off-chain.   

The idea is for decentralized applications to incorporate a secondary DON to perform specialized application-specific computations. In the example of a Carbon Sequestering Market, which we explore more in-depth later on, the secondary DON first receives a satellite image. It is forwarded by the Iris DON as a hash code to the secondary DON along with a distributed database (IPFS) address of the image at the request of the dapp controlling smart contract. The secondary DON then instructs its nodes to compute the images hash and compare it from that recorded by Iris. If they are equivalent, the secondary DON nodes calculate the carbon sequestering potential of that land. The nodes may use different ML models to come up with a result but at the end a single-value numerical result is produced. In this case, it is the number of tons of carbon sequestered per year of the requested plot of land or how many tons of C02/Year/km². By using a similar statistical data comparison mechanism to that of Chainlink’s price-feeds, we can calculate averages and reward honest nodes for their contributions. 

The secondary DON then reports the aggregate value generated by the nodes to the dapp’s operating or controlling smart contract. In effect, the secondary DON is distilling valuable information from a more complicated form of data. This is why I like to refer to these DONs as Data Distilling DONs. They essentially distill actionable data - data that can be consumed and computed cost-effectively upon by smart contracts.

From a dapp developer’s perspective, when a user submits a request to perform an Iris dependent function of the dapp, the dapp will request an image from Iris. After generating the satellite imagery requested, Iris will send the data to a dapp specific DON. This new DON will be used to extract actionable data or distill other data-types from to be used by other DONs down the line. 

Ultimately, Iris will act to provide the information rich data in the form of satellite images. Dapps on the other hand are responsible for building DONs and other decentralized computation systems to extract smart contract actionable data. 

Using sequential DONs will allow all computation aspects of Iris and Iris dependent dapps to be performed in a decentralized fashion.