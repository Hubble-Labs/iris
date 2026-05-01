# Iris Threat Model

A per-layer catalog of protocol-level attacks, mitigations, and residual risks for the Iris Protocol. Companion to [`architecture.md` §1.3 Trust Model](./architecture.md#13-trust-model).

## Goal & Scope

**Goal:** Define what Iris is protecting against, and from whom — so that operators, integrators, and downstream auditors have a single reference for the network's adversarial assumptions and the mechanisms that uphold them.

**In scope (this document):**

- **Network-layer threats** — Sybil, eclipse, GossipSub mesh poisoning, Kademlia DHT poisoning.
- **Provenance-layer threats** — Notary collusion, TLS proof forgery, Data Provider response spoofing, replay of stale proofs.
- **Consensus-layer threats** — Leader equivocation, sub-optimal medoid selection, DKG sabotage, BLS share withholding, BFT threshold violation.
- **Settlement-layer threats** — Relayer censorship, host-chain reorg, BLS precompile failure, signature replay across epochs.
- **Slashing rules** — Confirmed and proposed slashable offenses, detection mechanisms, and attribution requirements.

**Out of scope (deferred elsewhere):**

- **Cryptographic primitive analysis** — BLS12-381, BLAKE2b, TLSNotary MPC primitives are treated as black boxes whose security follows from their published analyses. See [`architecture.md` §10.1](./architecture.md#101-cryptographic-compute-hashing) for primitive selection rationale.
- **Application-layer threats** — Dapp-side ownership-proof problems, AoI authentication, downstream interpretation correctness. Sketches and open research questions are preserved in **Appendix A** but are not Iris protocol concerns.
- **Smart contract code review** — The full audit of `IrisVerifier.sol` access control, reentrancy patterns, and storage layouts is deferred to a dedicated security review tied to architecture review item 2.8.
- **Cross-chain bridge security** — Iris does not relay across chains; if a Relayer composes Iris with a bridge, that bridge's security is outside Iris's trust boundary (per architecture.md §1.4 Non-Goals).
- **Concrete penalty parameters** — Slashing amounts, decay constants, and threshold values are governance-tunable per epoch and live in a tokenomics/governance document, not here.

## Trust Assumptions Baseline

The threats catalogued below are organized as *violations of the trust assumptions* enumerated in [`architecture.md` §1.3 Trust Model](./architecture.md#13-trust-model). The aggregate invariants that this document treats as the security floor:

- **BFT honest majority** — fewer than $n/3$ committee members are malicious at any time.
- **DKG security** — at least $t$ honest participants present and correct at every committee DKG ceremony.
- **Notary non-collusion** — phase-dependent (see [architecture.md §5.5](./architecture.md#55-trust-assumptions--the-notary)).
- **At-least-one-honest-Relayer** — phase-dependent (see [architecture.md §8.1](./architecture.md#81-relayer-trust-model--phase-roadmap)).
- **Host-chain safety and finality** — the underlying blockchain provides standard finality guarantees.

When any of these is violated, the resulting failure mode is described inline below.

---

## 1. Network Layer Threats

The Iris network is a libp2p overlay built on GossipSub v1.1 (consensus messages) and Kademlia DHT (peer discovery). Network-layer attacks aim to partition the mesh, isolate honest nodes, or poison the routing tables that nodes use to find each other. See [architecture.md §4](./architecture.md#4-network-layer) for the protocol stack.

### 1.1 Sybil Attack

- **Attack:** An adversary spawns many libp2p peers (each with its own `PeerId`) without staking, hoping to flood the GossipSub mesh and outvote or out-forward honest peers.
- **Attacker capability:** Cheap PeerId generation (Ed25519 keypair); IP addresses across cloud providers; no stake required to join the libp2p network.
- **Detection:** GossipSub peer scoring (per architecture.md §4.4) tracks per-peer message validity, mesh churn, and IP colocation. Sybil clusters typically share IP ranges and exhibit poor scoring profiles.
- **Mitigation:**
  - **Stake-gated committee membership** — Sybil peers can spam the libp2p layer but cannot vote in consensus or hold a BLS share without staking via `IrisStaking`.
  - **GossipSub peer scoring** — peers below a score threshold are pruned from the mesh.
  - **IP colocation penalty** — multiple peers sharing the same `/24` (IPv4) or `/64` (IPv6) range receive a score penalty.
  - **Bootstrap peer diversity** — operators are expected to configure multiple bootstrap nodes from independent operators.
- **Residual risk:** A wealthy attacker can stake to acquire committee membership, but that attack is governed by the **BFT honest majority** assumption ($f < n/3$) and the slashing rules in §5, not by Sybil mitigation.

### 1.2 Eclipse Attack

- **Attack:** An adversary surrounds a target node with malicious peers in its routing table, isolating it from the honest network. The target sees only attacker-controlled views of GossipSub topics and the DHT.
- **Attacker capability:** Persistent presence near the target's PeerId in Kademlia space; ability to respond to the target's discovery queries faster than honest peers.
- **Detection:** A node's bootstrap reachability check (per architecture.md §4.3.2) tests whether known-good bootstrap peers are reachable via the current routing table; persistent failure indicates eclipse.
- **Mitigation:**
  - **Kademlia $k$-bucket diversity** — $k = 20$ peers per bucket, with periodic refresh from the bootstrap list.
  - **Persistent bootstrap connections** — at least one bootstrap peer is always pinned outside the regular DHT churn.
  - **GossipSub flood publishing** — control messages are flood-published initially, making single-path eclipse insufficient to suppress all traffic.
- **Residual risk:** An adversary who simultaneously controls a victim's network path (e.g., a malicious ISP or BGP hijack) can still eclipse them; this is outside Iris's trust boundary and falls into the host-chain / network-infrastructure assumption.

### 1.3 GossipSub Message Poisoning

- **Attack:** A peer publishes invalid messages (malformed payloads, invalid signatures, spoofed `request_id`) to GossipSub topics to amplify network noise or trigger downstream parser bugs.
- **Attacker capability:** Any peer connected to a topic mesh can publish.
- **Detection:** Each GossipSub message carries a publisher signature and is validated against topic-level rules (`iris/requests/v1`, `iris/observations/v1`, `iris/consensus/v1`) before forwarding.
- **Mitigation:**
  - **Validating message handlers** — invalid messages are dropped and never re-forwarded.
  - **Peer score decrement** — repeated invalid publishing penalizes the peer's score and eventually removes it from the mesh.
  - **Strict schema validation** at the message-deserialization layer (CBOR via `ciborium`) before any downstream processing.
- **Residual risk:** A burst of invalid messages between detection and score-driven pruning consumes bandwidth and CPU. Bounded but not zero.

### 1.4 Kademlia DHT Poisoning

- **Attack:** Malicious peers respond to `FIND_NODE` queries with bogus peer records, polluting the routing tables of honest nodes.
- **Attacker capability:** Any peer can respond to DHT queries; the protocol does not sign DHT records by default.
- **Detection:** Returned peer records are exercised — if a returned `(PeerId, Multiaddr)` pair fails to authenticate via Noise handshake at connection time, it is dropped from the routing table.
- **Mitigation:**
  - **Authenticated peer records** — every accepted record must be reachable and authenticate via Noise XX before being added to a $k$-bucket.
  - **$k$-bucket replacement policy** — preference for long-lived, recently-validated peers reduces the value of injected fakes.
- **Residual risk:** Slow-burn DHT poisoning can degrade discovery latency, but cannot break consensus because consensus messages flow over GossipSub topic meshes (not DHT lookups).

---

## 2. Provenance Layer Threats

The provenance layer turns a TLS session with a Data Provider into a verifiable proof that the served bytes really came from that Provider at that time. See [architecture.md §5](./architecture.md#5-data-provenance--ingestion).

### 2.1 Notary Collusion with Prover

- **Attack:** A node (Prover) and the Notary jointly construct a `.tlsn` proof for a TLS session that never actually occurred — the Notary co-signs a fabricated transcript that the Prover supplies.
- **Attacker capability:** The Prover controls its own MPC participation; the Notary controls its signing key. If both are dishonest and collaborate, no third party can detect the fabrication from the proof alone.
- **Detection:**
  - **Cross-referencing across Providers** — the medoid filter at the consensus layer rejects images that diverge from the consensus pool. A fabricated image must match real images closely enough to pass the similarity threshold, which is a high bar for arbitrary fabrications.
  - **Notary key whitelisting** — only proofs signed by approved Notary public keys are accepted on-chain (see architecture.md §5.5 phase roadmap).
- **Mitigation:**
  - **Phase 1 (MVP):** TLSNotary's hosted PSE/EF Notary — open-source, non-profit operator with reputational stake.
  - **Phase 2:** Foundation-operated Notary fleet with per-round Notary diversity (no two nodes in the same round use the same Notary).
  - **Phase 3:** Permissionless staked Notary pool with slashing for provable misbehavior.
  - **Phase 4 (Research):** $k$-of-$m$ threshold MPC notarization, eliminating single-Notary collusion entirely.
- **Residual risk:** A single colluding `(Prover, Notary)` pair is absorbed by the BFT threshold ($f < n/3$). A coordinated attack involving $\geq n/3$ Provers all colluding with the same Notary breaks safety — this is the fundamental TLSNotary trust assumption and the reason the phase roadmap exists.

### 2.2 TLS Proof Forgery

- **Attack:** A Prover constructs a `.tlsn` proof over a transcript the Provider never produced, without Notary collusion.
- **Attacker capability:** Bounded by the cryptographic assumptions of TLSNotary's MPC protocol — the Prover does not learn the Notary's signing key, and the Notary's signature commits to the joint transcript.
- **Detection:** Verification of the `.tlsn` proof checks the Notary's signature over the transcript commitment. A forged transcript without a valid Notary signature fails verification immediately.
- **Mitigation:** Cryptographic — TLSNotary's security proof. No Iris-specific mitigation needed beyond verifying the proof correctly.
- **Residual risk:** Bugs in the TLSNotary verifier implementation. Mitigated by depending on the upstream `tlsn-verifier` crate rather than rolling our own; tracked via dependency version pinning.

### 2.3 Data Provider Response Spoofing

- **Attack:** A Data Provider serves different content to different nodes (e.g., one fabricated image to a paid attacker, the real image to everyone else). All proofs are individually valid; the medoid then has to choose between divergent images.
- **Attacker capability:** A Data Provider has full control over its own server responses; TLS proves *fact of delivery*, not content correctness.
- **Detection:**
  - **Multi-provider observation** — nodes are configured to query multiple Providers per round, so divergent responses surface as outliers in the similarity matrix.
  - **Medoid selection** — the Average Scenario is the image *most similar to all others*. Outliers (whether fabricated or simply low-quality) lose the medoid race.
  - **Anomaly-driven slashing** — nodes whose images fall below the similarity threshold are slashed (§5).
- **Mitigation:** No cryptographic prevention; this is the reason consensus exists. The medoid mechanism transforms pixel-level honesty into a statistical property of the committee.
- **Residual risk:** A coordinated Provider+attacker can serve the same fabricated image to $\geq n/3$ committee nodes, biasing the medoid. This violates the BFT honest-majority assumption and is treated as such.

### 2.4 Replay of Stale Proofs

- **Attack:** An attacker submits a `.tlsn` proof from an earlier successful round (with valid Notary signature) for a current `DataRequest`, hoping to be rewarded for "honest" observation without actually fetching new data.
- **Attacker capability:** Any node has access to its own historical proofs; proofs may be observable on-chain or in IPFS.
- **Detection:** Each `.tlsn` proof embeds a Notary-signed timestamp. The verifier checks that the timestamp falls within an acceptable window relative to the `DataRequest` event's block timestamp (per architecture.md §5).
- **Mitigation:**
  - **Timestamp freshness check** — proofs older than the round-start timestamp by more than a configurable margin are rejected.
  - **`request_id` binding** — committed manifests embed the `request_id`, making cross-request replay detectable.
- **Residual risk:** Proofs replayed within the freshness window appear valid but are filtered by the medoid (the underlying image won't match the consensus pool unless the AoI conditions are stable). Additional risk if the freshness window is set too generously by governance.

---

## 3. Consensus Layer Threats

The Iris-BFT consensus protocol drives the round state machine (architecture.md §3.1, §7). Consensus-layer threats target the Leader, the BFT signing process, or the DKG ceremony that maintains the aggregate key.

### 3.1 Leader Equivocation

- **Attack:** A Byzantine Leader broadcasts conflicting `Proposal` messages to different subsets of the committee, hoping to split the BLS share contributions across two CIDs and deadlock the round.
- **Attacker capability:** The Leader is a single committee member with one BLS share; it cannot forge consensus alone.
- **Detection:**
  - **GossipSub mesh** — proposals propagate over a single topic mesh, so most peers see all proposals from a given Leader. Equivocating proposals surface as duplicate `(request_id, leader_id)` pairs with different CIDs.
  - **Per-round, per-Leader dedup** — Regular Nodes accept only the first valid proposal per `(request_id, leader_id)`; subsequent equivocations are ignored.
- **Mitigation:**
  - **Independent verification** — each Regular Node re-runs the medoid pipeline locally, so a Leader cannot push an arbitrary CID through; the proposed CID must match an image with valid TLS provenance and similarity above threshold.
  - **Threshold gating** — the round only finalizes when $t > 2n/3$ shares converge on the same `(request_id, ipfs_cid)` pair.
  - **Slashable offense (proposed)** — provable equivocation can be slashed via a fraud-proof that submits both signed conflicting proposals.
- **Residual risk:** A round can be stalled (no proposal achieves $t$ shares) but cannot be safety-violated. Stalled rounds are recovered by leader timeout / re-election (proposed mechanism — see architecture review item 2.1).

### 3.2 Sub-Optimal Medoid Selection

- **Attack:** A Leader colludes with one or more Regular Nodes to propose the colluder's image as the Average Scenario, even though it is not the true medoid — only "good enough" to pass the similarity threshold of >2n/3 honest verifiers.
- **Attacker capability:** A Leader + $\geq 1$ Regular Node working together; the proposed image must still have a valid `.tlsn` proof and pass the similarity threshold checks.
- **Detection:** Currently weak. The O(1) verification shortcut described in architecture.md §7.4 has each Regular Node check only the proposed image against its *own local image*, not against all other manifests. This means a sub-optimally-selected image can pass verification if it is "good enough" relative to most local images.
- **Mitigation (current):**
  - **Similarity threshold floor** — the proposed image must score above the $\beta$-tuned threshold against $> 2n/3$ verifiers, bounding how far from the true medoid the proposed image can be.
  - **TLS proof requirement** — the proposed image must have a valid `.tlsn` proof, ruling out arbitrary fabrications.
- **Mitigation (proposed — review item 2.2):** Either (a) formal economic argument that sub-optimal-but-threshold-passing selection has negligible value, or (b) periodic spot-checks where Regular Nodes verify against a random sample of *other* manifests (not just their own), or (c) require Leader to publish the full similarity matrix for off-line audit.
- **Residual risk:** Tracked as an open issue in [architecture_review.md item 2.2](./architecture_review.md#22-the-verification-shortcut-in-74-has-an-acknowledged-but-unresolved-attack-vector). The economic value of this attack appears low (the colluder gains a marginal reward, not full control), but it is not formally bounded.

### 3.3 DKG Sabotage

- **Attack:** A node in the DKG ceremony submits malformed or inconsistent shares, hoping to abort the ceremony and prevent the new committee from functioning.
- **Attacker capability:** Any DKG participant; cost is the ceremony participation gas + reputational impact.
- **Detection:** Each share is verified against published commitments at the receiving end. Invalid shares are attributable to the publishing PeerId.
- **Mitigation:**
  - **Per-round timeout** (60s default per architecture.md §3.4) — wedged ceremonies are aborted and retried.
  - **Bounded retry budget** — up to 3 retries within a 15-minute wall-clock window.
  - **DkgAborted terminal state** — after exhausting retries, the prior committee is retained (the network keeps signing panels), the pending node is returned to the unstaked pool, and any attributable misbehavior is slashed per §5.
  - **Liveness preservation** — a wedged DKG cannot halt request processing, only stall committee membership churn.
- **Residual risk:** Persistent DKG sabotage by a stake-rich attacker delays committee rotation. Bounded by retry budget and the cooldown period that prevents repeated attempts by the same candidate.

### 3.4 BLS Share Withholding

- **Attack:** Honest-looking nodes selectively withhold their BLS shares during the Voting phase to stall specific rounds, especially those involving a particular Requester or AoI.
- **Attacker capability:** Each node controls its own share; signaling is lazy (no positive obligation to send).
- **Detection:** The Leader observes which committee members fail to deliver shares within the Voting timeout. Patterns of selective withholding are detectable over many rounds.
- **Mitigation:**
  - **Threshold with margin** — $t > 2n/3$ allows up to $\lfloor n/3 \rfloor$ non-responders without round failure.
  - **Reputation impact** — the Relayer reputation system (architecture.md §8.1) factors in successful BLSShare contributions; chronic withholders lose reputation eligibility.
  - **Slashable offense (proposed)** — provable selective withholding can be slashed via cross-round statistical detection (currently unspecified).
- **Residual risk:** A coordinated $> n/3$ withholding attack stalls the network. This violates the BFT honest-majority assumption.

### 3.5 BFT Threshold Violation ($f \geq n/3$)

- **Attack:** Not really a single attack — this is the failure mode that occurs when the foundational honest-majority assumption is violated. A coordinated $\geq n/3$ malicious committee can:
  - Forge threshold signatures on arbitrary `(request_id, ipfs_cid)` pairs.
  - Reject valid proposals.
  - Equivocate at scale.
- **Attacker capability:** Either compromise of $\geq n/3$ committee nodes, or coordinated stake acquisition by a single entity to that level.
- **Detection:** None within the protocol — once $f \geq n/3$, the threshold signature itself becomes an unreliable witness. External monitoring (off-chain anomaly detection, governance) is required.
- **Mitigation:**
  - **Stake-weighted committee admission** with per-operator caps (governance-tunable).
  - **Geographic / organizational diversity requirements** for committee members (governance-driven, not enforced on-chain in MVP).
  - **Epoch-based rotation** — the committee composition changes over time, raising the cost of sustained majority capture.
- **Residual risk:** Inherent to BFT systems. Iris's security floor is the BFT honest-majority assumption; mitigations reduce the probability of violation but cannot eliminate it.

---

## 4. Settlement Layer Threats

The settlement layer is the bridge from the off-chain consensus to the on-chain `IrisVerifier` contract. See [architecture.md §8](./architecture.md#8-smart-contract-integration).

### 4.1 Relayer Censorship

- **Attack:** A Relayer refuses to forward `DataRequest` events from chain → off-chain, or refuses to submit finalized reports off-chain → chain, censoring specific Requesters or AoIs.
- **Attacker capability:** Any party operating Relayer infrastructure; censorship-by-omission leaves no on-chain proof of refusal.
- **Detection:**
  - **Direct observation** — Requesters who don't receive responses in the expected window can publicly flag the censorship.
  - **Multiple Relayers** (Phase 2+) — competing Relayers naturally cover for each other; a single censor is bypassed automatically.
- **Mitigation:**
  - **Reputation-gated opt-in role** (architecture.md §8.1) — multiple Relayers above the reputation threshold compete; no single Relayer has a privileged position from Phase 2 onward.
  - **On-chain timeout fallback** — `requestSubmissionDeadline[requestId]` allows any reputation-qualified Relayer to step in after `T1 ≈ 600s`.
  - **Phase 1 fallback** — the Foundation Relayer's published uptime SLA is the bootstrap-phase liveness guarantee.
- **Residual risk:** During Phase 1, Foundation Relayer outage is a single point of failure for liveness (not safety). Tracked as a phase-roadmap concern.

### 4.2 Host-Chain Reorg

- **Attack:** The host blockchain reorgs past the block where a `DataRequest` event was emitted or where a `deliverReport` transaction was confirmed.
- **Attacker capability:** Outside Iris's trust boundary — depends on the host chain's finality model (Ethereum PoS, Polygon, etc.).
- **Detection:** Standard chain-reorg detection at the Relayer's chain-monitoring layer.
- **Mitigation:**
  - **Finality wait** — Relayers monitor for $k$ confirmations (host-chain-specific) before treating an event as committed.
  - **Idempotent on-chain submission** — `IrisVerifier.deliverReport` rejects duplicates by `request_id`, so a re-org-then-resubmit is safe.
- **Residual risk:** Catastrophic host-chain reorgs (deeper than the configured $k$) are out of scope; this is the **host-chain safety and finality** assumption from §1.3.

### 4.3 BLS Precompile Failure or Absence

- **Attack:** Not adversarial per se, but a deployment risk: a target host chain may not support the EIP-2537 BLS12-381 precompile, or a future chain upgrade may break it.
- **Attacker capability:** N/A — this is an environment risk.
- **Detection:** Static — known at deployment time per chain.
- **Mitigation:**
  - **Solidity BLS library fallback** — for chains lacking EIP-2537, a Solidity-implemented BLS verifier is used at higher gas cost (per architecture.md §8).
  - **Deployment gating** — Iris will not deploy on chains where BLS verification is infeasible at any gas cost.
- **Residual risk:** Higher gas cost on fallback chains; tracked under architecture review item 2.8 (smart contract section).

### 4.4 Signature Replay Across Epochs

- **Attack:** An attacker captures a valid threshold signature from epoch $E$ and submits it during epoch $E + k$, hoping the contract accepts it as a current panel.
- **Attacker capability:** All threshold signatures are publicly observable on-chain or via IPFS.
- **Detection:** `IrisVerifier` stores a monotonically-increasing `current_epoch` counter and binds every accepted report to the current aggregate key, which changes on every committee rotation.
- **Mitigation:**
  - **Epoch counter in `IrisVerifier`** — verification uses the current-epoch aggregate key; signatures from prior epochs fail verification because the corresponding aggregate key is no longer stored.
  - **Per-request `request_id` uniqueness** — a `request_id` can only be settled once; replay against the same `request_id` fails the dedup check.
- **Residual risk:** None at the protocol level. Replay is cryptographically prevented by the epoch-bound aggregate key.

---

## 5. Slashing Catalog

A slashable offense is one that destroys the offender's stake (fully or partially), and on which the protocol's economic security depends. The following table catalogs both **confirmed** offenses (specified in `architecture.md`) and **proposed** offenses (acknowledged but not yet specified).

| Offense | Status | Detection mechanism | Penalty | Attribution mechanism |
|---------|--------|--------------------|---------|-----------------------|
| **Invalid TLS proof** | **Confirmed** | Verifier rejects `.tlsn` proof at the manifest-acceptance step | Stake slash (governance-tunable amount) | PeerId of the manifest publisher; signature on the manifest binds the offender |
| **Anomalous data** | **Confirmed** | Similarity score below $\beta$-tuned threshold against $> 2n/3$ peers | Stake slash + reward forfeiture for the round | Manifest signature binds the image hash to the publisher's PeerId / staking address |
| **Attributable DKG misbehavior** | **Confirmed** | Receiver-side share verification fails against published commitment | Stake slash; one-epoch cooldown before retry; pending node returned to unstaked pool | Publisher signs each share; invalid share is provably attributable |
| **BLS share equivocation** | **Proposed (spec pending)** | Two valid BLS shares from the same node on conflicting `(request_id, ipfs_cid)` pairs in the same round | Stake slash via fraud proof (both shares submitted on-chain) | Per-share signature binds to PeerId; equivocation is provable by submitting both shares |
| **Selective BLS share withholding** | **Proposed (spec pending)** | Statistical detection across many rounds — chronic non-response in the Voting phase, especially for specific Requesters | Reputation decay (immediate); stake slash (proposed, requires attribution algorithm) | Hard problem — distinguishing withholding from network failure requires a yet-unspecified attribution method |
| **Attributable Relayer censorship** | **Proposed (spec pending)** | Foundation-flagged Phase 1; reputation drop for missed timeout-fallback opportunities Phase 2+ | Stake slash on the Relayer's underlying staking address | Requires a fraud proof scheme (currently unspecified); see architecture review item 2.7 |
| **Sub-optimal medoid selection** | **Proposed (spec pending)** | Off-line audit comparing the Leader's published proposal against the full similarity matrix | Stake slash on the Leader (or the Leader+Regular Node colluding pair) | Requires Leader to publish the full similarity matrix or for verifiers to spot-check; see architecture review item 2.2 |
| **Leader equivocation** | **Proposed (spec pending)** | Two valid `Proposal` messages signed by the same Leader for the same `request_id` with different CIDs | Stake slash via fraud proof (both proposals submitted on-chain) | Per-proposal signature binds to Leader PeerId |

**Penalty parameter governance:** Concrete penalty amounts (what fraction of stake is slashed for each offense), reputation decay rates, and proof-submission windows are *governance-tunable per epoch* and are specified in a tokenomics/governance document, not here. The architecture spec fixes the *offenses and detection logic*; the tokenomics doc fixes the *parameters*.

---

## Appendix A — Application-Layer Open Questions (out of scope for protocol threats)

> These sketches address dapp-layer ownership-verification problems built *on top of* Iris, not Iris protocol threats. Preserved as research notes; they predate the structured threat catalog above and are retained for reference. Iris itself does not implement any of the schemes below; downstream applications building on verified Iris panels may.

### Need: tamper-proof land-ownership assignment (downstream application)

Need a tamper-proof way of assigning land ownership.

- **Endogenous Solution #1 (Feature-Based Verification):** We can use the network (Iris) to recognize owner-made terrestrial features. This could be something like writing a specific code or word that is only given to the requesting user/owner. Similar to the concept of writing your name OR "SOS" in the sand, but with a code that is only visible from space.
   - Problems: This would be difficult if not negligent to have as a system for users whose lands are heavily forested or otherwise covered by natural features that would obscure the code. This includes small areas that might not have the same required for the code to be visible. Nor would it work for land that is protected legally or cannot sustain further modification.

- **Exogenous Solution #1 (Mobile Device Verification):** Use a cellphone or similar geospatially aware device to ping the edges or walk continuously through the property boundaries to prove ownership. Having the user verify the boundaries of their land using either point or continuous line data based on geographical information wouldn't necessarily prove that they are the owner but it would prove that they have access to the land and can traverse it.
   - Problems:
      - Geospatial information can be spoofed.
      - Mobile or consumer-grade devices with geospatial capabilities are not always accurate.
      - Someone could trace the landowner's property from the outside and not actually have access to the land.

- **Exogenous Solution #2 (Custom Hardware):** Use of bespoke / custom hardware that is in constant communication with the internet using something like Starlink. Could be a part of an extension to the Iris network or a separate network entirely. Fundamentally it is a different verification architecture and would have to be passed down from a 3rd-party, in this case the manufacturer of the hardware, to the user.
   - Problems:
      - Expensive to produce and distribute.
      - Expensive to buy.
      - Doesn't have the averaging benefit from multiple data sources; instead it only relies on one.
      - Custom hardware can be tampered with and with enough resources could be spoofed.

- **Exogenous Solution #3 (Ground-based Landmark Imagery):** The Iris network can request the user looking for ownership of property verification take multiple randomly designated pictures of features visible from space. The images would then have to be cross-referenced with the satellite imagery to verify the user's ownership.
   - Problems:
      - We would have to extend the Iris network to include nodes that can take pictures of the ground.
      - Single source of truth for the ground-based imagery.
      - If the area is small enough the imagery can be taken from outside the bounds of the property.
      - If the area is large enough, and the land is not densely populated or has limited resources, it would allow bad actors to come in and take pictures of the landmarks to spoof the system.
