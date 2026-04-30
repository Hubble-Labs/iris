# Iris

## Overview

Iris is an independent, decentralized terrestrial satellite oracle network (DtsON) for Geographic Information System (GIS) data. It enables decentralized applications (dapps) to reliably ingest, verify, and utilize satellite imagery and other geospatial data directly on-chain.

Unlike traditional oracles that relay simple numerical values, Iris features its own peer-to-peer networking stack and a custom Byzantine Fault Tolerant consensus engine (**Iris-BFT**) optimized for rich data types. 

## How It Works

Iris operates primarily off-chain while delivering cryptographic proofs on-chain:

1. **P2P Networking**: Built natively in Rust using `libp2p` for encrypted communication, peer discovery (Kademlia DHT), and heavy-payload streaming.
2. **Data Provenance**: Nodes fetch imagery from commercial satellite APIs (Maxar, Planet, Sentinel) and use TLS multi-party computation (like TLSNotary) to generate cryptographic proofs that the payload came directly from the source without tampering.
3. **Data Normalization Engine**: Disparate imagery is orthorectified to a shared 3D Digital Elevation Model (DEM). The network calculates similarity across aligned tensor metrics (Mean Absolute Distance, Mean Squared Error, Spectral Angle Mapper).
4. **Consensus (Iris-BFT)**: A Leader node mathematically determines the "Average Scenario" of an Area of Interest. The committee validates this calculation and produces a single BLS threshold signature.
5. **Decentralized Storage**: Finalized images are pinned to IPFS, ensuring permanent availability.
6. **Smart Contracts**: An on-chain `IrisVerifier` contract accepts the off-chain report, verifying the threshold signature before delivering the IPFS CID to the requesting dapp.

## Documentation

For a deep dive into the protocol, please refer to the documents in the `docs/` directory:
- [Architecture](docs/architecture.md)
- [Protocol Design](docs/protocol_design.md)
- [Data Normalization Specification](docs/data_normalization.md)
- [Detailed Execution Plan](docs/execution_plan.md)

> **© 2026 Hubble Labs. All Rights Reserved.**
> This codebase is available for review, education, and inspiration. For direct usage rights, commercial applications, or integrations, please contact Hubble Labs for explicit permission.

