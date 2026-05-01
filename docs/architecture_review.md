# Architecture Document Review — `docs/architecture.md`

> Comprehensive critique of the Iris Protocol Architecture document.
> Organized by severity: **Structural → Technical → Polish**.

---

## Overall Assessment

This is a remarkably strong architecture document — especially for a pre-implementation specification. The "Geodesic Reconstruction Model" framing (§2) is genuinely inventive and gives the reader a powerful mental model before any machinery is introduced. The Rust struct definitions ground the abstract design in concrete data types, and the Mermaid diagrams are well-placed throughout.

The critiques below are intended to take it from "excellent draft" to "audit-ready reference specification."

---

## Progress Tracker

### TODO
- [ ] 2.1 Leader election is under-specified for adversarial analysis
- [ ] 2.2 The verification shortcut in §7.4 has an acknowledged but unresolved attack vector
- [ ] 2.3 The Notary Server in TLSNotary is a trust assumption that is never addressed
- [ ] 2.4 DKG ceremony has no failure recovery specified
- [ ] 2.5 Single-round execution limitation is stated but not defended
- [ ] 2.6 IPFS pinning is a liveness risk that is never addressed
- [ ] 2.7 The Relayer trust model has a subtle gap
- [ ] 2.8 Smart contract section (§8) is too thin relative to the rest
- [x] 3.1 Inconsistent struct field naming conventions
- [ ] 3.2 BLAKE2b security claim needs qualification
- [ ] 3.3 The `serde-cbor` crate (§4.4, line 548) is unmaintained
- [ ] 3.4 Several "magic numbers" lack justification
- [ ] 3.5 Minor typo / grammar issues
- [ ] 3.6 The `protocol_design.md` legacy document should be explicitly deprecated
- [ ] 4. Missing Sections (Error handling, Versioning, Observability, Testing, Multi-chain)

---


## 2. Technical Gaps & Inconsistencies

### 2.1 Leader election is under-specified for adversarial analysis

The leader election formula (§7.1, line 841):
```
leader_index = hash(block_hash ‖ request_id) % total_stake
```

The doc argues this is safe because the Leader has "zero subjective power." However:

- **Block hash manipulation:** A malicious validator on the host chain could grind block hashes to influence leader selection. The document doesn't address this.
- **Hash function not specified:** Which hash? SHA-256? BLAKE2b? Keccak? This matters for cross-chain verification.
- **What happens on leader failure?** If the elected leader is offline or malicious and doesn't produce a proposal, the document specifies no fallback / view-change mechanism. The round presumably times out, but who re-initiates?

**Recommendation:** (a) Specify the hash function. (b) Add a "Leader Failure & View-Change" subsection describing what happens on leader timeout — is a new leader elected? Does the round simply fail and the Requester must re-submit? (c) Acknowledge the block hash grinding vector and explain why it is or isn't a practical concern for Iris (likely: the Requester is paying, so grinding is economically irrational for them, and validators can't predict which requests will arrive).

### 2.2 The verification shortcut in §7.4 has an acknowledged but unresolved attack vector

Lines 860–862 describe the O(1) verification optimization where Regular Nodes only verify the proposal against their *own* local image. The parenthetical explicitly acknowledges:

> *"the Leader could theoretically propose a sub-optimal image as long as it still passes the threshold for >2n/3 nodes."*

This is a **real attack**: a colluding Leader + 1 node could submit that node's image as the "Average Scenario" even if it isn't the true medoid, as long as it's sufficiently similar to pass threshold checks. The document waves this away by noting the image must have a valid TLS proof, but that only prevents *forgery*, not *sub-optimal selection*.

**Recommendation:** Either:
1. Formally prove that sub-optimal selection within the threshold is harmless (i.e., the economic value of selecting image A vs. image B when both pass threshold is negligible), or
2. Describe a mitigation — e.g., nodes could also verify against a random sample of other manifests, or the Leader could be required to publish the full similarity matrix for spot-checking.

### 2.3 The Notary Server in TLSNotary is a trust assumption that is never addressed

Section 5 and the sequence diagram (line 777) show a "Notary Server" as a separate participant. This is a critical trust dependency:

- Who runs the Notary? Is it a peer node? A centralized service? The Iris Foundation?
- What happens if the Notary is malicious or colluding with the Prover?
- Is there a plan for decentralized notarization?

**Recommendation:** Add a "§5.2 Notary Trust Model" subsection. At minimum, state whether the notary is (a) a centralized service (MVP), (b) another committee member (future), or (c) the user can choose from a set of approved notaries.

### 2.4 DKG ceremony has no failure recovery specified

The Committee Lifecycle diagram (§3.4, line 319) shows `DKGInProgress → PendingJoin : DKG fails (retry)`, but the document never describes:
- What constitutes a DKG failure (e.g., a participant goes offline mid-ceremony)?
- How many retries are allowed?
- What happens if DKG never succeeds (does the committee remain at its old membership)?
- Is there a timeout after which the pending node is dropped?

**Recommendation:** Add a "DKG Failure Handling" paragraph after the Committee Lifecycle diagram.

### 2.5 Single-round execution limitation is stated but not defended

Line 189 states:

> *"A node may only participate in a single round at a time to mitigate potential computation and networking bottlenecks."*

This is a very strong constraint that directly affects throughput. If the average round takes 5–10 minutes (observation + transfer + normalization + voting), the network can only process 6–12 requests per hour.

**Recommendation:** Either:
1. Defend this constraint with concrete numbers (expected request volume vs. throughput), or
2. Describe the upgrade path — e.g., pipelined rounds where observation for round N+1 overlaps with voting for round N.

### 2.6 IPFS pinning is a liveness risk that is never addressed

Section 3.3 (line 259–264) and §7.3 rely on the Leader pinning to IPFS. But:
- Who pays for persistent IPFS pinning? Pinata? Filecoin deals?
- What happens if the IPFS content becomes unavailable after the round? The on-chain CID becomes a dead link.
- Is there a garbage collection policy for the local `~/.iris/cache/` directory?

**Recommendation:** Add a "§3.3.1 Storage Persistence & Pinning Strategy" section addressing long-term availability guarantees.

### 2.7 The Relayer trust model has a subtle gap

Section 1.2 (line 48) correctly states the Relayer "cannot forge consensus." But there is a **liveness attack**: a malicious Relayer could simply *refuse* to relay — either dropping requests from the chain or withholding finalized reports. The document doesn't address:
- Can multiple Relayers compete?
- Is there a timeout after which anyone can relay?
- What incentivizes the Relayer not to censor specific requests?

**Recommendation:** Expand the Relayer trust model to cover liveness, not just safety.

### 2.8 Smart contract section (§8) is too thin relative to the rest

At only ~12 lines of prose (lines 876–883), §8 is dramatically under-specified compared to the 300+ lines of networking detail. Key gaps:
- No contract interface (function signatures, events, errors)
- No description of how `updateCommittee()` works
- No gas cost estimates
- EIP-2537 is mentioned but no fallback for chains that don't support it
- The `IIrisReceiver` callback pattern lacks error handling semantics (what if the callback reverts?)

**Recommendation:** Either expand §8 significantly or create a dedicated `smart_contracts.md` spec and link to it.

---

## 3. Polish & Presentation

### ~~3.1 Inconsistent struct field naming conventions~~ ✅

Resolved — see [Completed Recommendations](#31-inconsistent-struct-field-naming-conventions-1).

### 3.2 BLAKE2b security claim needs qualification

Line 970 claims BLAKE2b provides "512-bit post-quantum security." This is an overstatement:
- BLAKE2b produces a 512-bit digest, but Grover's algorithm reduces the pre-image security to ~256 bits against a quantum adversary.
- The comparison "unlike SHA-256's 128-bit quantum resistance" is actually a point *in favor* of BLAKE2b, but the framing implies SHA-256 is weak when 128-bit quantum resistance is still considered very strong.

**Recommendation:** Rephrase to: "BLAKE2b provides a 256-bit security margin against quantum pre-image attacks (Grover's), compared to SHA-256's 128-bit quantum margin."

### 3.3 The `serde-cbor` crate (§4.4, line 548) is unmaintained

The document specifies `serde-cbor` for message serialization. This crate has been unmaintained since 2021. The maintained successor is [`ciborium`](https://crates.io/crates/ciborium).

**Recommendation:** Update the reference to `ciborium`, or specify that the exact crate choice is deferred to implementation.

### 3.4 Several "magic numbers" lack justification

| Value | Where | Issue |
|-------|-------|-------|
| 30-second observation window | §7.2, line 850 | Why 30s? What if API latency exceeds this? |
| $k = 20$ bucket size | §4.3.2, line 478 | Standard Kademlia default, fine, but worth noting |
| $D = 6$ mesh degree | §4.4, line 528 | Justified well ✓ |
| 120s message TTL | §4.4, line 533 | Why 120s? A round can last up to 3600s (GeoTIFF timeout). Stale messages from early phases would be dropped. |

**Recommendation:** Add brief rationale for the 30s window and 120s TTL, or note they are testnet-tunable defaults.

### 3.5 Minor typo / grammar issues

| Line | Issue |
|------|-------|
| 48 | "It merely transports cryptographically verifiable messages." — the antecedent of "It" is ambiguous (Relayer? intercepted data?) |
| 520 | "~20 GB of total network traffic per observation per node" — should this be "per round" instead of "per observation"? |
| 970 | "it also provides a higher security margin (more rounds) than BLAKE3" — "rounds" here refers to hash rounds, but could be confused with consensus rounds |

### 3.6 The `protocol_design.md` legacy document should be explicitly deprecated

`protocol_design.md` still contains the legacy SIFT-based consensus (§4) and an older lifecycle description that conflicts with `architecture.md`. New readers may be confused about which is canonical.

**Recommendation:** Add a deprecation notice at the top of `protocol_design.md`:
```markdown
> [!WARNING]
> This document is superseded by [architecture.md](./architecture.md). Retained for historical context only.
```

---

## 4. Missing Sections to Consider Adding

| Topic | Why it matters |
|-------|---------------|
| **Error handling & round failure modes** | What happens on API timeout? Partial manifest collection? Network partition during voting? |
| **Versioning & upgrade strategy** | How does the protocol handle breaking changes to the Manifest schema or GossipSub topic format? Is there a protocol version negotiation? |
| **Observability & monitoring** | Metrics endpoints, health checks, alerting — critical for operators |
| **Testing strategy** | How will the consensus be tested? Simulation framework? Adversarial test harness? |
| **Multi-chain deployment** | §8 mentions "Ethereum, Polygon" but doesn't address chain-specific differences (gas models, precompile availability, finality times) |

---

## Summary

| Category | Count | Highlights |
|----------|-------|------------|
| **Structural** | 5 | Add ToC, reduce redundancy between §3.1/§5/§9, add non-goals |
| **Technical** | 8 | Leader failure recovery, Notary trust, IPFS persistence, Relayer liveness, expand §8 |
| **Polish** | 6 | BLAKE2b claim, unmaintained crate, magic numbers, deprecate `protocol_design.md` |
| **New sections** | 5 | Error handling, versioning, observability, testing, multi-chain |

The document's greatest strength is its pedagogical layering — the geodesic model → state machine → network → provenance → consensus progression reads naturally and builds understanding incrementally. The primary area for improvement is closing the gap between the *descriptive* sections (which are excellent) and the *specification* sections (which need more edge-case coverage to be implementation-ready).

---

## Completed Recommendations

### 1.1 Section 5 (Data Provenance) largely re-states Section 3.1's Round lifecycle

The Observing → Aggregating → Commit flow is already described in detail in the Layer 1 state table (§3.1). Section 5 retells the same story but from the "provenance" perspective. A reader hitting §5 for the first time will experience strong déjà vu.

**Recommendation:** Refactor §5 to be a *focused deep-dive on TLSNotary mechanics only* — the MPC setup, what the `.tlsn` proof actually contains, its verification algorithm, and its trust assumptions. Remove or condense the round-lifecycle narrative that's already covered in §3.1. This would make §5 complementary instead of redundant.

### 1.2 Section 9 (Full Walkthrough) also recaps the round lifecycle a third time

The 10-step walkthrough in §9 is useful as a "tie it all together" section, but combined with §3.1 and §5, the reader encounters the same Idle → Observing → ... → Commit flow three times in the same document.

**Recommendation:** Keep §9 as-is (walkthroughs are genuinely valuable), but add a brief callout:  
> *"This walkthrough revisits the state transitions from §3.1 and the provenance chain from §5 — it is intentionally redundant as a reference summary."*  
This sets expectations and avoids the reader wondering if they missed something new.

### 1.3 No Table of Contents

At 1,004 lines, this document needs a ToC at the top. Readers landing from `implementation_plan.md` anchor links (e.g., `architecture.md#421-cryptographic-node-identity-peerid`) benefit from seeing the full document map.

**Recommendation:** Add a markdown ToC after the introductory paragraph (line 3). You can use VS Code's built-in Markdown ToC generator or manually list the 11 top-level sections.

### 1.4 The document has no "Non-Goals" or "Scope Boundaries" section

The architecture describes what the system *does* but never explicitly states what it *does not* do. For a protocol spec, this is a significant gap — it leaves room for misinterpretation about capabilities like:
- Does Iris support real-time / streaming imagery?
- Does Iris handle authentication of Data Provider API access, or is that the operator's responsibility?
- Can Iris serve historical panels on-demand, or only respond to live requests?

**Recommendation:** Add a brief "§1.3 Non-Goals & Scope Boundaries" subsection under the System Overview.

### 1.5 Missing cross-links to sibling documents

The document links to `data_normalization.md` once (line 828) but never references:
- [protocol_design.md](./protocol_design.md) — which contains the legacy SIFT-based consensus and is presumably superseded
- [threat_model.md](./threat_model.md) — which covers penalty mechanics relevant to §7 and §8
- [whitepaper.md](./whitepaper.md) — which provides higher-level motivational context

**Recommendation:** Add a "Related Documents" section or a brief header note listing the companion docs and their relationship to this spec (e.g., "supersedes `protocol_design.md` §4").

### 3.1 Inconsistent struct field naming conventions

The Rust structs mixed raw `PeerId` and `Blake2bHash` across fields with different semantic meanings, making it easy to confuse a Leader's ID with a contributor's ID, or a content hash with a proof hash.

**Resolution:** Added a **Domain Type Aliases** block (zero-cost `type` aliases) at the top of §3.1's struct definitions. All six structs (`Round`, `NodeState`, `CommitteeMember`, `Panel`, `CommitteeState`, `ValidatorEntry`) now reference domain-specific aliases:

| Alias | Underlying Type | Semantic Purpose |
|-------|----------------|------------------|
| `LeaderId` | `PeerId` | The elected leader for a specific round |
| `ContributorId` | `PeerId` | A node that contributed an observation |
| `ContentHash` | `Blake2bHash` | Hash of a raw GeoTIFF payload |
| `ProofHash` | `Blake2bHash` | Hash of a `.tlsn` proof file |
| `AggregateKey` | `BlsPublicKey` | Committee-wide BLS12-381 aggregate public key |
| `ShareSecretKey` | `BlsSecretKeyShare` | A single node's BLS private key share |
| `SharePublicKey` | `BlsPublicKeyShare` | A single node's BLS public key share |
| `ThresholdSig` | `BlsSignature` | The final aggregated t-of-n BLS signature |
