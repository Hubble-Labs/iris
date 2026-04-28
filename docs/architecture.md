# Iris Protocol Architecture

This document defines the high-level architecture of the Iris Protocol, a proprietary, standalone Decentralized Terrestrial Satellite Oracle Network (DtsON). Iris enables decentralized applications (dapps) to reliably ingest, verify, and utilize Geographical Information System (GIS) data, such as satellite imagery.

## 1. System Overview
Iris operates as an independent decentralized network specifically optimized for rich data types like imagery. Unlike early oracle models that relied solely on singular numerical values or basic off-chain reporting, Iris employs a custom Byzantine Fault Tolerant consensus mechanism (**Iris-BFT**) to securely reach agreement on the provenance and similarity of satellite imagery.

The network fetches imagery off-chain, proves the authenticity of the data source without trusting the node, mathematically calculates the "Average Scenario" using tensor comparison algorithms, and reports the verified data back to a host blockchain via threshold signatures.

## 2. Network Layer
To remove dependencies on external oracle infrastructures, Iris is built with its own peer-to-peer (P2P) networking stack:
* **libp2p**: The foundational networking protocol used for peer discovery, routing, and connection management.
* **GossipSub**: Enables rapid, scalable mempool propagation of data requests, peer observations, and consensus messages across the network.
* **Encrypted Channels**: All node-to-node communication is strictly encrypted using the Noise protocol and authenticated via the nodes' cryptographic identities (e.g., ed25519 keys).

## 3. Data Provenance & Ingestion
To prevent man-in-the-middle attacks and ensure that the GIS data is genuine, nodes must provide cryptographically secure data provenance. 
1. **API Fetching**: Regular nodes request satellite imagery from commercial APIs (e.g., Maxar, Planet, Sentinel).
2. **TLS Proofs**: Nodes utilize zero-knowledge or multi-party computation TLS protocols (like DECO or TLSNotary) during the data ingestion phase. This generates a cryptographic proof that the data payload was received directly from the authenticated satellite endpoint without tampering.

## 4. Data Normalization Engine
Images received from different satellite constellations possess varying spectral bands, resolutions, and perspectives. Before the network can compare these images, they undergo a rigorous normalization pipeline. 

**Summary of the Pipeline:**
Nodes perform orthorectification to align the 2D imagery with a shared 3D Digital Elevation Model (DEM). The network then computes similarity across three core metrics:
* **Mean Absolute Distance**: Penalizes total absolute spatial deviation.
* **Mean Squared Error (MSE)**: Heavily penalizes isolated, extreme noise or anomalies.
* **Spectral Angle Mapper (SAM)**: Measures changes in physical materials/spectral signatures, ignoring differences in illumination or shadows.

These metrics are combined into a final **Similarity Score** using a physics-based exponential decay model. This score allows the consensus engine to mathematically group the most accurate representations of the requested location.

> **Note:** For the complete mathematical formulation and definitions of the tensors used in this pipeline, refer to the [Data Normalization Specification](./data_normalization.md).

## 5. Consensus Engine (Iris-BFT)
The Iris-BFT consensus operates over specific rounds to finalize an image request:
1. **Leader Election**: A Leader node is pseudo-randomly selected for a given request.
2. **Observation**: Nodes gossip a lightweight manifest containing their Image Hash, Bounding Box, and TLS proofs over GossipSub. Full GeoTIFFs are requested directly via libp2p streams.
3. **Aggregation**: The Leader node utilizes the Data Normalization Engine to find the "Average Scenario"—the image mathematically most similar to the consensus pool, acting as the most accurate representation of the Area of Interest.
4. **Storage**: The finalized Average Scenario image is pinned to decentralized storage (IPFS/Filecoin) to acquire a Content Identifier (CID).
5. **Threshold Signature**: The committee verifies the Leader's aggregation and IPFS pin. If valid, they provide partial signatures. The Leader aggregates these into a single BLS threshold signature (or Schnorr multi-sig) representing a hyper-majority agreement.

## 6. Smart Contract Integration
While the heavy computation (fetching, TLS proof generation, tensor comparisons) happens off-chain, the final results must be verifiable on-chain for dapps to consume.
* **Iris Verifier Contract**: Deployed on target host chains (e.g., Ethereum, Polygon), this contract is seeded with the network's aggregate public key.
* **State Updates**: The contract accepts the final report (containing the IPFS CID and relevant metadata) and the threshold signature. If the signature is cryptographically valid, the contract updates the on-chain state, making the verified GIS data available to ecosystem dapps.
* **Tokenomics (Staking & Slashing)**: Node operators are required to stake IRIS tokens to participate in the network. Dapps pay request fees, which reward honest nodes. Nodes providing malicious or anomalous data have their stakes slashed, ensuring cryptoeconomic security.
* **Data Distillation**: External networks (like Chainlink DONs) can also query the Iris API Gateway to ingest this highly-trusted GIS data and further distill it into simpler, numerical actionable data for smart contracts.