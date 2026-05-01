# Iris Whitepaper

**Version 0.2 — May 2026 — Pre-launch design draft**
_By Salvador Salcedo_

> **Status:** Pre-launch design draft. The technical architecture this document summarizes is fully specified in [`architecture.md`](./architecture.md); the adversarial assumptions are catalogued in [`threat_model.md`](./threat_model.md). Where this whitepaper and those documents diverge, the technical documents are authoritative.

## Abstract

Iris is a decentralized oracle network for satellite imagery. Smart contracts on existing blockchains can request a verified picture of any bounded patch of Earth at a chosen point in time and receive, in return, a BLS-threshold-signed reference to a satellite image whose authenticity is provable end-to-end. Iris combines TLSNotary attestations of each node's commercial imagery fetch with a BFT consensus over the medoid of independently-fetched images — yielding a single, original satellite image whose provenance can be checked by any third party. The protocol is the first oracle network to apply BFT consensus to satellite imagery in this way, opening a class of decentralized applications — verifiable carbon-sequestration accounting, parametric crop insurance, ground-truth dispute resolution — that today depend on trusted intermediaries.

## 1. Introduction

Iris secures and verifies the provenance of satellite imagery for smart contracts. Through a stake-gated committee of nodes operating under a Byzantine Fault Tolerant (BFT) consensus protocol, Iris turns commercial satellite imagery — purchased from existing providers like Maxar, Planet, and BlackSky — into a cryptographically verifiable input for on-chain logic. Much like Chainlink made price feeds reliable enough for decentralized finance, Iris aims to make geospatial data reliable enough to be the foundation of a new class of decentralized applications.

Iris is infrastructure. End users never interact with it directly; the protocol's consumers are smart contracts and the Decentralized Oracle Networks (DONs) built on top of them. The technical novelty is not the consensus primitive — Iris uses standard BLS threshold signatures over an Iris-specific BFT round — but the *application* of consensus to imagery. Nodes independently fetch the same scene from different providers, the network selects the medoid as canonical, and the result carries individual TLS proofs of provenance along with a committee threshold signature.

## 2. Problem Statement

Oracle networks exist because smart contracts cannot reach off-chain data on their own. Chainlink and its peers have demonstrated, at substantial scale, that decentralized committees can agree on numerical values like asset prices reliably enough for billions of dollars of value to depend on the result. The technique works because numerical values are small, easy to compare, and have well-defined notions of agreement (median, time-weighted average, and similar).

Imagery has none of these properties. A satellite image is tens of megabytes to tens of gigabytes; two images of the same scene from different satellites are never byte-identical; there is no obvious "median" of an image. As a result, no oracle network has previously delivered satellite imagery with the kind of cryptographic provenance and Byzantine-fault-tolerant agreement that on-chain consumers require. This gap blocks an entire class of applications — anything where a smart contract's behavior should depend on what a place on Earth actually looks like.

## 3. Solution

Iris fills this gap with a five-part design. Each part is summarized below; the full technical specification is in [`architecture.md`](./architecture.md), with the section anchors noted in each subsection.

### 3.1 Geodesic Reconstruction

A consensus round reconstructs a single **panel** — a bounded Area of Interest (AoI) at a single timestamp. The Earth is treated as a notional geodesic mosaic, with each AoI as a discrete facet that can be independently requested, verified, and stored. Resolution is demand-driven: panels are reconstructed only where Requesters request them ([`architecture.md` §2](./architecture.md#2-the-geodesic-reconstruction-model)).

### 3.2 Committee, Leader, and Medoid Selection

Iris is operated by a stake-gated **Committee** of Regular Nodes. For each round, a **Leader** is deterministically elected by stake-weighted Keccak-256 hash of the request ID and host-chain block hash. Each Regular Node independently fetches the panel from a commercial Data Provider; the Leader collects the resulting manifests, computes pairwise similarity over the normalized images, and selects the **medoid** — the single existing image most similar to all others — as the canonical reconstruction. Critically, the medoid is an *original, unaltered image* fetched by one of the nodes, not a synthetic average; this preserves the per-node TLS proof end-to-end ([`architecture.md` §3](./architecture.md#3-state-machine-architecture), [§6.4](./architecture.md#64-average-scenario-medoid-selection), [§7](./architecture.md#7-consensus-engine-iris-bft)).

### 3.3 Provenance via TLSNotary

Each Regular Node's fetch is attested by a TLSNotary proof: a two-party MPC between the node (Prover) and a Notary that produces a third-party-verifiable transcript of the TLS session with the Data Provider. The Notary never sees plaintext; it only co-signs that the session occurred. The resulting `.tlsn` proof is what binds a specific image hash to a specific commercial source ([`architecture.md` §5](./architecture.md#5-data-provenance--ingestion)).

### 3.4 BFT Consensus via BLS Threshold Signing

Once the Leader proposes a medoid, every Regular Node independently re-runs the similarity check against its own local fetch and, on agreement, contributes a BLS signature share. A `t > ⌊2n/3⌋` threshold of shares aggregates into a single 48-byte BLS signature over `(request_id, ipfs_cid)`. The threshold key is established by a Distributed Key Generation (DKG) ceremony at every committee rotation, not per-request ([`architecture.md` §7.5](./architecture.md#75-threshold-cryptography)).

### 3.5 Settlement via the Relayer

The proposal, once threshold-signed, is delivered on-chain to the `IrisVerifier` contract by a **Relayer** — a transport role that bridges the Iris network and the host blockchain. The Relayer holds no BLS shares and cannot forge consensus; its role is liveness, not safety. The host-chain contract verifies the BLS signature against the committee's aggregate public key (via the EIP-2537 precompile where available, or a Solidity BLS library otherwise) and emits the panel's IPFS CID for the Requester to consume ([`architecture.md` §8](./architecture.md#8-smart-contract-integration)).

The end result, from the Requester's perspective, is an on-chain reference to an unmodified, originally-fetched satellite image carrying an end-to-end chain of cryptographic provenance: TLS-attested at ingest, medoid-selected by deterministic normalization, and threshold-signed by the Iris committee.

## 4. Trust Model

Iris is BFT, not trustless. The protocol's safety and liveness rest on a small set of explicit assumptions; this section names them so that a reader can evaluate the security claim. The companion document [`threat_model.md`](./threat_model.md) catalogs the attacks against each assumption and the corresponding mitigations.

### 4.1 Committee — Honest Majority

Iris assumes fewer than `n/3` of the active committee is malicious at any time. If this assumption holds, the BLS threshold signature is a reliable witness of committee consensus. If it is violated, a coordinated `≥ n/3` adversary can forge threshold signatures or stall the network — a failure mode shared with all BFT systems. Stake-weighted admission, per-operator caps, and epoch-based rotation reduce the probability of violation but do not eliminate it ([`threat_model.md` §3.5](./threat_model.md#35-bft-threshold-violation-f-geq-n3)).

### 4.2 Notary — Phased Decentralization

The TLSNotary proof requires a Notary that does not collude with the Prover. Iris addresses this in four phases:

- **Phase 1 (MVP):** TLSNotary's hosted PSE/EF Notary — open-source, non-profit, third-party — with a whitelist of approved keys enforced on-chain.
- **Phase 2:** Iris-Foundation-operated Notary fleet, with per-round Notary diversity (no two nodes in a round use the same Notary).
- **Phase 3:** Permissionless staked Notary pool with slashing for provable misbehavior.
- **Phase 4 (research):** k-of-m threshold MPC notarization, eliminating single-Notary collusion entirely.

A single colluding `(Prover, Notary)` pair is absorbed by the BFT threshold; the residual risk is `≥ n/3` Provers all colluding with the same Notary, which is the explicit motivation for the phase roadmap ([`architecture.md` §5.5](./architecture.md#55-trust-assumptions--the-notary), [`threat_model.md` §2.1](./threat_model.md#21-notary-collusion-with-prover)).

### 4.3 Relayer — Liveness, Not Safety

A Relayer cannot forge consensus — it lacks the threshold BLS shares. It can, however, censor by silent drop: refusing to forward a `DataRequest` event or withholding a finalized report. Iris addresses this in three phases:

- **Phase 1 (MVP):** Iris Foundation operates the sole Relayer; on-chain allowlist of one. This is honestly framed as a liveness compromise, not a solution.
- **Phase 2:** Reputation-gated opt-in Relayers compete with the Foundation; an on-chain timeout (`requestSubmissionDeadline`, ~600s) lets any reputation-qualified address step in if the primary stalls.
- **Phase 3:** Foundation steps away; the role becomes permissionless above the reputation threshold.

Across all phases, **safety is unchanged** — only liveness varies ([`architecture.md` §8.1](./architecture.md#81-relayer-trust-model--phase-roadmap), [`threat_model.md` §4.1](./threat_model.md#41-relayer-censorship)).

### 4.4 Host Chain

Iris assumes the host blockchain (Ethereum, Polygon, or other EVM-compatible chain) provides standard finality guarantees and that the EIP-2537 BLS precompile is available — or that a Solidity fallback is acceptable on chains where it is not. Catastrophic host-chain reorgs deeper than the configured `k`-confirmation wait are out of scope ([`threat_model.md` §4.2](./threat_model.md#42-host-chain-reorg)).

## 5. Reference Applications

The following are example dapps that *consumers* of Iris could build. They are not part of Iris itself: per [`architecture.md` §1.4](./architecture.md#14-non-goals--scope-boundaries), Iris does not interpret pixel content, broker data-provider subscriptions, or solve application-layer ownership-verification problems. The applications below describe what becomes possible once those layers are built on top of a verified Iris panel.

### 5.1 Carbon-Sequestering Asset Tokenization (Kokiri)

The voluntary carbon-credit market is opaque. A buyer cannot easily verify that a credit's underlying ton of CO₂ was actually sequestered, prices vary widely across jurisdictions, and individuals find it impractical to issue credits for personal sequestration projects.

Iris enables a different design. A user-facing dapp would accept an Area of Interest, the type of vegetation grown, evidence of land ownership, and a fee, then issue a `DataRequest` to Iris. Iris returns a verified panel of the AoI; a downstream application-specific DON (operated separately) extracts a vegetation-coverage metric from the image and writes the result to the dapp's smart contract, which mints carbon-sequestration tokens proportional to the result.

> **Open problem:** Land-ownership verification is not solved by Iris. Whether a Requester actually owns the AoI they claim is an application-layer question that requires additional infrastructure — cadastral records, custom hardware, ground-truth photography, or other approaches. Three endogenous and three exogenous solutions are sketched in [`threat_model.md` Appendix A](./threat_model.md#appendix-a--application-layer-open-questions-out-of-scope-for-protocol-threats), but none is committed; this is an open research area for downstream dapp builders.

### 5.2 Parametric Crop Insurance

Crop insurance is unevenly distributed. Farmers in developed countries can typically access it, while smallholders in developing countries often cannot — premiums are too high, the geography is uncovered, or the actuarial work is unprofitable for traditional insurers.

A parametric insurance dapp on Iris could let any farmer with internet access buy a policy by submitting an AoI, ownership evidence, the crop type, and the premium. Each month, the dapp requests an Iris panel of the AoI; an application-specific DON extracts a soil-moisture or vegetation-health metric and writes it on-chain. If a claim is filed, the contract evaluates the metric history against the policy terms and pays out automatically.

> **Open problem:** The same land-ownership dependency as §5.1 applies. Without verifiable ownership, a parametric policy can be claimed against arbitrary coordinates.

## 6. Vision

Iris is one layer of a stack. Above it sit application-specific DONs that distill verified panels into actionable scalar data; above those sit dapps that turn the scalars into on-chain economic actions. This pattern — chained DONs that progressively reduce real-world signal into smart-contract-consumable inputs — is, in the authors' view, the shape of how decentralized applications will increasingly interact with the physical world.

In the near term, Iris focuses on launching a stake-gated MVP committee on a single host chain, demonstrating the end-to-end Chain of Provenance for a small set of commercial Data Providers, and onboarding reference dapps that exercise the request-response model. Over time, the trust roadmaps in §4 progressively decentralize the Notary and Relayer roles, the committee grows, and host-chain coverage expands.

## 7. Adjacent Initiative: Imaging Cubesats

> **Scope note:** This section describes a **separate organizational initiative** — not part of the Iris protocol MVP and not a precondition for Iris to function. Iris's MVP relies on existing commercial Data Providers (Maxar, Planet, BlackSky, Sentinel) for imagery.

A medium-term constraint on Iris is the accessibility of satellite imagery itself. Commercial provider APIs are gated, expensive, and individually rate-limited. A complementary initiative — a separate legal entity associated with the Iris team — proposes to design and launch compact imaging cubesats whose imagery is sold to Iris node operators on open terms. Cubesats are inexpensive by space-industry standards (low single-digit thousands of dollars per unit), and rideshare launches keep orbital costs accessible.

A second goal of this initiative is to publish reference designs that allow other organizations — commercial businesses, DAOs, research groups — to build and operate their own imaging cubesats. A diverse pool of independently-operated imagery sources strengthens the decentralization properties of any DON that consumes them, including Iris.

This work is independent of the Iris protocol roadmap. Iris ships and operates without it.

## Glossary

* **Actionable Data:** Real-world data that a smart contract can ingest and use to carry out decisions in a computationally efficient way.
* **AoI (Area of Interest):** A bounded patch of Earth's surface, defined by a bounding box and timestamp, that constitutes the subject of one Iris consensus round.
* **Average Scenario:** The image selected by the medoid procedure as the canonical reconstruction for a panel. Synonymous with "the medoid image" in Iris terminology.
* **BFT (Byzantine Fault Tolerant):** A property of a consensus mechanism that guarantees agreement among honest participants in the presence of arbitrary malicious behavior, up to some bounded fraction (in Iris, fewer than `n/3` of the committee).
* **BLS (Boneh–Lynn–Shacham):** A signature scheme on the BLS12-381 curve that supports threshold signing and aggregation. Iris uses BLS for its committee threshold signature.
* **Committee:** The set of staked Regular Nodes participating in Iris consensus during a given epoch.
* **Cubesat:** A class of miniaturized satellite based around a 10 cm cube form factor.
* **Dapp (Decentralized Application):** A web application whose backend execution depends on smart contracts and the underlying blockchain rather than a centralized server.
* **Data Provider:** A commercial satellite imagery service (Maxar, Planet, BlackSky, Sentinel) that Iris nodes fetch from. Not part of the Iris network.
* **DKG (Distributed Key Generation):** The cryptographic ceremony by which the committee jointly generates the BLS aggregate public key and individual private shares without any party seeing the full private key.
* **DON (Decentralized Oracle Network):** A committee of nodes that delivers off-chain data to smart contracts. Iris is a DON specialized for satellite imagery.
* **GeoTIFF:** A geospatial raster format used for satellite imagery; the on-the-wire payload that nodes fetch from Data Providers.
* **IPFS (InterPlanetary File System):** Content-addressed storage. Iris pins finalized panel imagery to IPFS and writes the resulting CID on-chain.
* **Leader:** The Regular Node deterministically elected to aggregate manifests, run the normalization pipeline, and propose the medoid for a given round.
* **Manifest:** A signed message published by a Regular Node containing the BLAKE2b hash of its fetched image, AoI metadata, and a reference to its TLSNotary proof.
* **Medoid:** The single, existing data point most similar to all others in a set. Iris uses the medoid (rather than a synthetic average) to preserve cryptographic provenance.
* **Node:** A computer that runs Iris software and participates in the network.
* **Notary:** The third party that co-signs TLS session transcripts in the TLSNotary protocol, enabling third-party verification of a node's commercial fetch.
* **OCRM (Off-Chain Reporting Model):** A pattern in which a DON aggregates and signs values off-chain before submitting a single result on-chain. Iris's BLS threshold signature is an OCRM-style commitment.
* **Oracle:** A node that participates in providing off-chain data to a DON.
* **Panel:** A single AoI-and-timestamp pair, finalized by one Iris consensus round; the unit of geodesic reconstruction.
* **Provenance:** The traceable origin of data and the verifiable record of its journey from source to consumer.
* **Regular Node:** A staked committee member that fetches imagery, generates TLSNotary proofs, and contributes BLS shares to consensus.
* **Relayer:** A transport role that bridges the host blockchain and the Iris network, forwarding `DataRequest` events inbound and finalized reports outbound.
* **Requester:** A dapp or smart contract that initiates an Iris round by paying a fee and submitting an on-chain request.
* **Smart Contract (SC):** Code deployed on a blockchain that executes deterministically in response to transactions.
* **TLSNotary:** A cryptographic protocol that uses two-party MPC to produce a third-party-verifiable proof of a TLS session's contents without giving the Notary access to plaintext.

## References

* Iris Architecture Specification — [`docs/architecture.md`](./architecture.md). Full technical specification of the protocol, including state machine, network layer, consensus, and contract integration.
* Iris Threat Model — [`docs/threat_model.md`](./threat_model.md). Per-layer attack catalog, mitigations, and slashing rules.
* Iris Architecture Review — [`docs/architecture_review.md`](./architecture_review.md). Open issues and design decisions tracked against the architecture spec.
* Iris Data Normalization Specification — [`docs/data_normalization.md`](./data_normalization.md). Mathematical formulation of the similarity metrics and medoid selection.
* TLSNotary — https://tlsnotary.org. Reference implementation and protocol documentation for the MPC-based TLS attestation scheme used by Iris.
* EIP-2537: Precompile for BLS12-381 curve operations — https://eips.ethereum.org/EIPS/eip-2537. The Ethereum precompile that Iris uses for on-chain BLS signature verification, with a Solidity fallback on chains lacking the precompile.
* Chainlink — https://chain.link. Reference oracle network whose architecture for numerical data feeds inspired the design of Iris for imagery.
* Commercial satellite Data Providers referenced in this document: Maxar (https://www.maxar.com), Planet Labs (https://www.planet.com), BlackSky (https://www.blacksky.com), Sentinel/Copernicus (https://www.copernicus.eu).
