# Iris Protocol Architecture (Draft)

## 1. Overview
Iris is an independent, decentralized terrestrial satellite oracle network (DtsON) for Geographic Information System (GIS) data. Originally conceptualized to run on top of external oracle infrastructure, this architecture defines a proprietary, standalone network built from scratch. It features its own peer-to-peer networking, a specialized consensus engine, and off-chain data verification mechanisms. It maintains the ability to broadcast securely to other oracle networks (e.g., Chainlink, Pyth) or blockchains in the future.

## 2. Core Components

### 2.1. Network Layer (P2P)
To remove external dependencies, Iris uses **libp2p** as its foundational networking stack.
*   **Bootnodes**: Maintained by the Iris Foundation and community members to facilitate reliable node discovery.
*   **GossipSub**: Used for rapid mempool propagation of data requests and peer observations.
*   **Encrypted Channels**: All off-chain node-to-node communication is encrypted (Noise protocol) and authenticated using the node's cryptographic identity (e.g., ed25519 keys).

### 2.2. The Consensus Engine: Iris-BFT
Iris implements a custom Byzantine Fault Tolerant (BFT) Off-Chain Reporting consensus designed specifically for rich data types like images.
1.  **Selection**: A Leader node is pseudo-randomly selected for a specific round based on an incoming data request.
2.  **Observation & Data Provenance**: Regular nodes fetch the requested GIS data from constellation APIs (Maxar, Planet, Sentinel, etc.). To prevent man-in-the-middle attacks and ensure the imagery is genuine, nodes must utilize TLS proof protocols (e.g., DECO, TLSNotary) to generate cryptographic proofs of the API payload. These proofs act as signatures verifying that the specific imagery came directly from the authenticated constellation endpoint without tampering.
3.  **Processing (Deterministic Hashing & ORB)**: Nodes process the imagery using computationally cheap and deterministic algorithms (e.g., ORB - Oriented FAST and Rotated BRIEF, or perceptual hashing) and locally compute similarity via Hamming distance to determine data provenance.
4.  **Reporting**: Nodes gossip their observations, TLS proofs, and signed image hashes over the P2P network.
5.  **Aggregation**: The Leader node compiles the "Average Scenario" (the image mathematically most similar to the consensus pool, acting as the most accurate representation of the Area of Interest).
6.  **Threshold Signatures**: Nodes verify the Leader's aggregate report. If the computation is valid, they provide partial signatures. The Leader combines these into a single BLS threshold signature (or Schnorr multi-sig) indicating a hyper-majority agreement (> 2/3 of the committee).

### 2.3. Distributed Storage
Images are far too large for on-chain or purely in-memory consensus storage.
*   **IPFS/Filecoin Integration**: The agreed-upon "Average Scenario" image is strictly pinned to decentralized storage (IPFS/Filecoin).
*   **CID Reporting**: The Iris network's final output payload consists of the IPFS Content Identifier (CID) and associated metadata (e.g., bounding box, timestamp, cloud cover percentage).

### 2.4. Smart Contract / On-Chain Layer
While Iris operates heavily off-chain for computation, it delivers verified data to smart contracts on host chains (e.g., Ethereum, Polygon).
*   **Iris Verifier Contract**: Deployed on target host chains. It is seeded with the public keys of the authorized Iris nodes or the network's aggregate public key.
*   **Report Verification**: It accepts the final report and the threshold signature. If the signature is valid, the on-chain state is updated with the new GIS data (CID), making it available to decentralized applications (dapps).

### 2.5. Interoperability & Broadcasting Module
Designed future-proof for cross-compatibility and broader decentralized participation:
*   **External Adapter/API Gateway**: Iris nodes can expose a standard RESTful endpoint or gRPC service. This allows Chainlink DONs to query Iris as a highly-trusted, decentralized data source for GIS attributes (fulfilling the "Data Distilling DON" concept).
*   **Cross-Chain Relayers**: Specialized roles that listen for Iris-BFT threshold events and relay the finalized signed packets to target blockchains via secure bridges or IBC (Inter-Blockchain Communication).

## 3. The Lifecycle of an Iris Request
1.  **Request Initiation**: A dApp Smart Contract on a host chain emits a `DataRequest` event for satellite imagery (e.g., for Crop Insurance claim verification).
2.  **Ingestion**: Iris nodes monitor the chain, detect the event, and initiate a new Iris-BFT consensus round.
3.  **Fetching**: Nodes independently pull imagery from external satellite APIs for the requested coordinates and time bounds, concurrently generating TLS proofs of the API payload origin.
4.  **Consensus**: Nodes use deterministic algorithms like ORB or perceptual hashing to assert image similarities and compute the Average Scenario.
5.  **Storage**: The elected node pins the validated image to IPFS.
6.  **Signature**: The committee provides BFT threshold signatures over the CID, the accompanied TLS data-provenance proofs, and requested metadata.
7.  **Finalize**: A relayer submits the signed deterministic report to the `Iris Verifier Contract` on the host chain.
8.  **Action**: The dApp's smart contract executes its internal logic utilizing the trustworthy GIS data.


## 4. Legacy Consensus Design (from Whitepaper v0.3)

Consensus


Iris nodes will be capable of fetching images, performing the SIFT Computer Vision algorithm on said images, creating cryptographically signed reports on a P2P off-chain network and reporting a single report to a blockchain network. We therefore have to create a way for the Leader Nodes to compute similarity and express it as a mathematical construct or numerical value. In other words, we have to devise a robust way for our DONs to determine image similarity using math. Luckily, there are a lot of people out there that are good at computer science and mathematics that devote their time to building out these algorithms.


First proposed by David Lowe in 2004, the SIFT or Scale Invariant Feature Transform algorithm is the perfect first candidate for the basis of Iris’ comparison algorithm. It works by first ingesting black and white images and searching for features or keypoints. These keypoints are found by scanning the images and looking for changes in image pixel intensity. Depending on the direction scanned, the SIFT algorithm we will use for Iris from the open source library OpenCV, will find a direction associated with a region where 


pixels are changing intensity. It is essentially creating blobs and assigning them to pixels as it scans the image. The scale of the blob and the resolution of the images change as it applies Gaussian blurs of high and high sigma allowing the algorithm to find interesting points or features at various scales in all directions. 
  

Farms and orbital landscapes are typically feature rich with displays of life below. The curves and corners of the roads, houses, orchards, groves, forests, they all contribute to the features of the scene. The SIFT algorithm picks up on these features and creates keypoints which then form into descriptors. They are vectors whose scale in higher dimensions correspond to the change in intensity of the image in that direction. The implementation of SIFT that we use has 128 dimensional vectors. This means it can detect changes keypoints in 128 directions.


The Leader Node of the committee of Regular Nodes uses the SIFT algorithm to not only detect the features, keypoints but also compare descriptors. The images of the same Area of Interest (AoI) will generate the same keypoints and therefore descriptors. When comparing two images, the leader node therefore will receive higher scores for very similar images than for ones of different areas. The SIFT algorithm itself is very robust and can give us a useful and compute-effective way to measure image similarity.


When the Leader and by extension, the DON finds the image that is most similar to all the others, this image represents the Average Scenario of the AoI. That is, it represents the state that one is most likely to find the AoI around the time requested. The advantages in time flexibility and data variability when using SIFT and images as a data source are several.


1. Multiple images: When finding the Average Scenario of an Area of Interest, the Nodes request many images of the same area. They may vary in time, brightness, weather conditions, etc. If the Nodes ever chose an image that has the most similar features to all other images but it has concealed or difficult to extract application-specific data, we may be able to extract the concealed data from the other images. It would probably be difficult for an application specific DON to extract harvest information if it is raining or thick clouds are overhead. It may be necessary to wait or use information from the next day for example.


2. Data Rich Images: A single image may contain multiple data points for use in different dapps. That is, users and the companies building on top of Iris can use one image for different purposes. Ultimately resulting in price savings for other users or dapps since the data would exist on an AWS DB or IPFS server and would not need to be requested, processed and extracted.


Lecture Slides on SIFT: https://cave.cs.columbia.edu/Statics/monographs/Edge%20Detection%20FPCV-2-1.pdf


Iris will operate as a DON with three kinds of nodes: Regular, Bootstrap and Leader nodes.
1. Bootstrap Node: A node that connects to Normal Nodes, establishes connections between them and begins an OCR round. 
2. Regular Node: A node that acts as a web server to fetch satellite imagery through authenticated API calls.
3. Leader Node: A node that collects image data from Regular Nodes. It then performs computer vision powered image similarity comparisons and creates a general report capturing the Area of Interest’s Average Scenario.


The consensus mechanism Iris will employ is known as an Off-Chain Report (OCR) network. They use an off-chain Peer-to-Peer (P2P) network to communicate before creating one report to submit on-chain. Because it is a network where node operators vote on the state of the Area of Interest (AoI), in the form of a report, at the time requested by providing said imagery it is helpful to think of our algorithmic approach as providing the best guess of the state of AoI. 


It is critical to understand that we may create representations of these states on blockchains like Ethereum because they are global state machines. When deployed, smart contracts perform changes on the state of user’s and their associated wallets. These wallets however can also hold information beyond transactional data because most EVM compatible blockchains like Ethereum are general purpose blockchains. That is, any reasonable computation can be performed by an Ethereum node and participate in the Ethereum Virtual Machine or EVM on behalf of users and their wallets. 


Because smart contracts are like scripts from other computer languages, you can write smart contracts to execute functions under certain conditions. Those conditions can and will relate to elements of the real world. The conditions can range from the mundanity of asset prices and ratios to disaster insurance applications. If a hurricane blows through New Orleans and destroys a families home, a DON would be able to recognize the house before and after to understand there has been a disaster and issue a payout. 


By being critical of the data our network participants exchange we can better adapt Iris to handle malicious actors, their attacks and any inaccurate information. The Average Scenario of a location is therefore the best estimate we have for an image of the AoI requested.


Steps:
1. Bootstrap Node finds other Iris nodes looking to participate in a committee of nodes for one round. The logic is processed through a smart contract by which users will be rewarded. 
2. All nodes are required to stake IRIS tokens in order to participate.
3. The smart contract then picks a random node from the committee and assigns it as the Leader Node. This aggregator node sends requests to the other nodes in the committee. All of whom at this point are considered Regular Nodes.
4. The Regular Nodes fetch the satellite imagery requested and generate their hash. They create a final report off-chain that includes the image hash, database web address of the image and the Regular Node’s  signature.
5. The Leader Node receives the reports from all the other nodes in the committee. It fetches the images from the web addresses provided in the reports. The images are compared against each other and results in the capturing of the area’s Average Scenario.
   1. The Regular Nodes that provided images close to the Average Scenario are more likely to be honest because they were close to the majority of all other images. Therefore the smart contract rewards the regular nodes.
   2. The Regular Nodes whose images are statistically dissimilar to the Average Scenario have their stakes tokens burnt as punishment. Again the smart contract executes the penalty.
6. The Leader Node creates a report which includes the hash and the web address of the image chosen as the Average Scenario, along with the regular and aggregator nodes signatures. The report is sent to the requesting smart contract and recorded on-chain. The Leader Node is rewarded extra for performing the computation.


