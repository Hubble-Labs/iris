# Iris Protocol Comprehensive Implementation Plan

This document serves as the definitive engineering roadmap for the Iris Protocol (DtsON). It expands upon the theoretical architecture and outlines the specific libraries, data models, and technical workflows required to build the network from the ground up.

---

## Phase 1: P2P Networking Foundation
**Objective**: Build a resilient, encrypted, and decentralized peer-to-peer network to handle node discovery and message propagation without relying on centralized servers.

### 1.1 Core Networking Stack (libp2p)
* **Language/Framework**: Rust (`rust-libp2p`). Rust provides the memory safety and concurrency needed for a high-throughput oracle node.
* **Transport & Multiplexing**: TCP/IP base with `Yamux` for stream multiplexing, allowing multiple logical streams (ping, gossip, kademlia) over a single connection.
* **Security & Authentication**: Enforce the **Noise protocol** for all connections. Every node generates an `ed25519` keypair on startup. The public key derives the node's unique `PeerId`, ensuring all communications are cryptographically tied to the node's identity.

### 1.2 Discovery & Routing
* **Kademlia DHT**: Implement the Kademlia Distributed Hash Table for decentralized peer discovery.
* **Bootstrap Nodes**: Deploy 3-5 static bootstrap nodes (hosted by the Iris Foundation initially) hardcoded into the client software. New nodes connect to these to join the DHT and discover the rest of the network.

### 1.3 Message Propagation (GossipSub)
* **PubSub Protocol**: Utilize `GossipSub` v1.1 for efficient, mesh-based message propagation.
* **Topics**:
  * `iris/requests/v1`: Smart contract data requests forwarded to the network.
  * `iris/observations/v1`: Nodes broadcasting a lightweight manifest containing their Image Hash, Bounding Box, and TLS Proofs. (Note: Large GeoTIFF payloads are *not* gossiped to avoid network congestion. They are exchanged via direct libp2p streams such as Bitswap).
  * `iris/consensus/v1`: Leader node broadcasting the proposed aggregate and regular nodes replying with signature shares.

---

## Phase 2: Data Ingestion & Provenance Module
**Objective**: Fetch commercial satellite imagery and generate zero-knowledge proofs demonstrating the data's authenticity.

### 2.1 API Workers
* **Stateless Fetchers**: Implement asynchronous Rust workers (`tokio` + `reqwest`) to interface with providers.
* **Target Providers**: 
  * Maxar (SecureWatch API)
  * Planet (PlanetScope API)
  * Sentinel (Copernicus Open Access Hub)
* **Data Format**: Standardize all incoming imagery as multi-band **GeoTIFFs** to preserve geospatial metadata (bounding boxes, coordinate reference systems).
* **Payload Exchange**: Once fetched, large GeoTIFFs are temporarily stored locally. When the Leader node requires the full payload to calculate the Average Scenario, it requests the image directly from the node via a libp2p Bitswap stream, utilizing the Image Hash provided in the GossipSub manifest.

### 2.2 TLS Provenance Proofs (TLSNotary / DECO)
* **The Problem**: If a node fetches an image via HTTPS, the network has no way to guarantee the node didn't digitally alter the image before broadcasting it.
* **The Solution**: Integrate **TLSNotary** (or a similar MPC-based TLS protocol).
* **Workflow**:
  1. The Iris Node acts as the *Prover*.
  2. The Node initiates a TLS session with the satellite API.
  3. The Node generates a cryptographic commitment to the TLS session keys and the encrypted payload.
  4. The Node outputs a `.tlsn` proof file alongside the decrypted GeoTIFF.
  5. When the Node gossips its observation, it includes the `.tlsn` proof. Other nodes act as *Verifiers* to mathematically prove the GeoTIFF matches the payload signed by the API's SSL certificate.

---

## Phase 3: Data Normalization Engine
**Objective**: Implement the computer vision and tensor mathematics pipeline to compare disparate GeoTIFFs and calculate the Similarity Score $\mathcal{S}(\mu)$.

### 3.1 Environment & Libraries
* **Language**: Rust (Native). All computations must happen natively within the Rust binary to prevent the deployment complexities of managing Python virtual environments.
* **Libraries**: `ndarray` (for tensor math), `gdal` (Rust bindings for GeoTIFF parsing and coordinate transformations).

### 3.2 Orthorectification
* **DEM Fetching**: The engine automatically fetches a localized tile of the SRTM (Shuttle Radar Topography Mission) Digital Elevation Model.
* **Warping**: The 2D GeoTIFF is draped over the 3D DEM to correct for the satellite's specific viewing angle and the Earth's curvature, aligning the pixels into a unified target space $\mathbb{R}^{a \times N \times M}$.

### 3.3 The Math Engine (Similarity Metrics)
Implement the three core tensor operations to analyze the difference between two aligned image tensors ($\bar{A}$ and $\bar{B}$):
1. **Mean Absolute Distance ($\mu_1$)**: The linear spatial mean of the absolute difference tensor.
2. **Mean Squared Error ($\mu_2$)**: The statistical variance, heavily penalizing localized, severe anomalies (e.g., malicious pixel manipulation).
3. **Spectral Angle Mapper ($\mu_3$)**: Calculates the N-dimensional angle between pixel vectors. This isolates changes in actual physical materials while ignoring benign changes in lighting or shadows.

### 3.4 Similarity Scoring
* Implement the physics-based exponential decay function: $\mathcal{S}(\mu) = 100 \cdot e^{-(\beta_1 \mu_1 + \beta_2 \mu_2 + \beta_3 \mu_3)}$.
* **Tuning Parameters ($\beta$)**: Define the default $\beta$ vector in a config file, to be empirically tuned during testnet based on the natural noise of specific API providers.

---

## Phase 4: Consensus Engine (Iris-BFT)
**Objective**: Coordinate the network to select the "Average Scenario" image and cryptographically sign the result.

### 4.1 State Machine
Implement the Iris-BFT state machine inside the Rust node:
* `Idle`: Listening for `iris/requests/v1`.
* `Observing`: Fetching API data, generating TLS proofs, and gossiping a manifest to `iris/observations/v1`.
* `Aggregating`: The Leader calculates similarities natively in Rust.
* `Pre-Commit`: The Leader broadcasts the proposed Average Scenario.
* `Commit`: Nodes verify the proposal by re-running the Rust tensor pipeline locally on the proposed image hash. If valid, they broadcast signature shares.

### 4.2 Leader Election
* Use a deterministic, stake-weighted round-robin algorithm based on the block hash of the requesting smart contract event. This ensures all nodes independently know who the Leader is for a specific round without extra communication overhead.

### 4.3 Threshold Cryptography
* **Curve**: Implement BLS signatures (BLS12-381 curve).
* **Key Generation (DKG)**: DKG is a heavy, asynchronous event. It is *only* run when a committee is updated (e.g., node onboarding/offboarding), not on a per-request basis. Once the DKG concludes, the committee shares a single aggregate Public Key, and each node holds a private key share.
* **Aggregation**: When the Leader proposes the final CID and metadata, nodes sign it with their private share. The Leader collects $t$ out of $n$ shares (where $t$ is a >2/3 hyper-majority threshold) and aggregates them into a single, standard 48-byte BLS signature.

### 4.4 Decentralized Storage (IPFS)
* Integrate an IPFS HTTP client (e.g., `ipfs-api` in Rust).
* The Leader node uploads the finalized "Average Scenario" GeoTIFF to IPFS, pins it via a service like Pinata or Filecoin, and retrieves the resulting Content Identifier (CID).

---

## Phase 5: Smart Contract Verifier
**Objective**: Build the Solidity infrastructure to verify off-chain network consensus and deliver the CID to dapps.

### 5.1 Contract Architecture
* **Framework**: Foundry (for fast Solidity compilation and Rust-like testing).
* **Contract**: `IrisVerifier.sol`.

### 5.2 State and Access Control
* Store the `aggregatePublicKey` of the authorized Iris committee.
* Implement an `updateCommittee()` function restricted to a governance multisig to rotate keys when node operators join or leave.

### 5.3 Verification Logic
* **Function**: `function deliverReport(bytes32 requestId, string calldata ipfsCid, bytes calldata signature)`
* **Validation**: The contract hashes the `requestId` and `ipfsCid` to recreate the message digest.
* **BLS Precompile**: Utilize the target blockchain's BLS precompiles (or a reliable Solidity BLS library) to verify that `signature` is a valid signature over the digest by the `aggregatePublicKey`.

### 5.4 Tokenomics: Staking, Rewards & Slashing
To ensure BFT guarantees and subsidize expensive commercial API costs, the network enforces strict cryptoeconomics:
* **Staking**: Node operators must deposit and lock a required amount of IRIS tokens in the `IrisVerifier` contract to join the active committee.
* **Rewards**: Dapps pay a fee (in ETH/MATIC or IRIS) to initiate a request. When a valid report is delivered, the fee is distributed among the honest nodes that provided data close to the "Average Scenario".
* **Slashing**: If a node maliciously provides anomalous data, fails to provide a valid TLS proof, or signs an invalid report, a portion of their staked IRIS tokens is slashed (burned or redistributed) to penalize the Byzantine behavior.

### 5.5 Dapp Interface
* Create an `IIrisReceiver.sol` interface.
* Upon successful verification, the `IrisVerifier` contract calls `targetContract.onIrisDataReceived(requestId, ipfsCid)`, cleanly injecting the verified GIS data into the dapp's ecosystem.
