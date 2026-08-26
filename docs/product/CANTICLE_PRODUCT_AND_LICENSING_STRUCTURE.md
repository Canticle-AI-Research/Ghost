# Canticle product and licensing structure

**Decision status:** operator-approved architecture; local documentation and
license candidate, not yet committed, reviewed by counsel, assigned to a legal
entity, released, or deployed.

Canticle follows an open-edge/source-available-product/proprietary-core model.
The purpose is to remove adoption friction at integration boundaries while
retaining the technology that creates the durable commercial advantage.

```text
developers and operators
        │
        ├─ Apache-2.0 clients, protocols, examples, connectors
        │       open integration edge; no MIRL/runtime/model internals
        │
        ├─ PolyForm Shield products
        │       Ghost, Canticle Core, distributed SEAM SDK/node source
        │       use/change/share allowed except to provide competing products
        │
        └─ authenticated product boundary
                │
                ├─ proprietary SEAM runtime + MIRL implementation
                ├─ proprietary SEAM-U model weights/training system
                ├─ proprietary cloud control plane and operations
                └─ paid API, hosted product, support, OEM, and enterprise terms
```

This is structurally similar to commercial AI platforms that publish client
SDKs and local agent harnesses while retaining model weights, hosted inference,
control planes, and internal production systems.

## Canonical product matrix

| Product or asset | Current evidence state | Intended public boundary | License or contract |
|---|---|---|---|
| Ghost application | implemented research prototype | source-available product | PolyForm Shield 1.0.0 |
| Ghost documentation | implemented local wiki | distributable with product | same repository grant until a separate documentation license is adopted |
| Ghost/Canticle branding and avatar art | implemented plus local WIP | official product identity only | All Rights Reserved plus trademark policy |
| thin SEAM/Canticle HTTP client | implemented separately | open integration SDK | Apache-2.0 |
| public API schema, examples, connectors | partial/planned | open adoption layer | Apache-2.0 unless a file says otherwise |
| in-process SEAM SDK | implemented separately | source-available advanced product | PolyForm Shield 1.0.0 plus commercial alternatives |
| SEAM node/self-host distribution | scaffold only | source-available or controlled enterprise product | PolyForm Shield for source; commercial EULA for controlled binaries/support |
| private SEAM runtime and MIRL internals | implemented in private repository | never included in public client artifacts | proprietary / All Rights Reserved unless separately licensed |
| Canticle Core | architecture scaffold only | source-available agent-native OS product | PolyForm Shield 1.0.0 |
| Canticle Core thin clients/protocols | planned | open integration boundary | Apache-2.0 |
| Canticle Core cloud/enterprise control plane | planned | hosted or controlled delivery | proprietary commercial terms |
| SEAM-U | named and planned; no model repository or weights located | API/product access; public model card and evals | weights/training system proprietary; service terms for access |
| research papers and public benchmark reports | separate publication decision | reproducible public evidence | publication-specific terms, normally CC BY 4.0 after provenance review |
| private datasets, credentials, customer data, unreleased experiments | private/confidential | no distribution | trade-secret controls, contracts, privacy terms |

## Why PolyForm Shield is placed on products

PolyForm Shield permits use, modification, and redistribution for any purpose
except providing a product that competes with the software or another product
the licensor or its affiliates provide using it. It is source-available, not
OSI-approved open source.

That makes it appropriate for product source that operators need to inspect,
run, adapt, or redistribute without granting a competitor an unrestricted
right to turn the same work into a substitute product. It is not appropriate
for:

- a thin client whose adoption value depends on permissive embedding;
- source that is never distributed and should remain a trade secret;
- trademarks and brand art;
- model weights or training data requiring model-specific restrictions; or
- hosted services, which are governed by service contracts rather than a
  source-code license.

## Apache-2.0 edge rule

Apache-2.0 belongs on a package only when artifact inspection proves it carries
no private runtime, MIRL implementation, SEAM-U weights, training code,
credentials, private prompts, operator records, or private control-plane logic.

The public edge should be boring and replaceable:

```text
application code
   └─ open client
         └─ authenticated, versioned HTTP protocol
               └─ private service implementation
```

Permissive edge code is a distribution mechanism. It is not where Canticle
stores its durable advantage.

## Permanent proprietary rule

Private repositories do not need a source-available license merely because
they exist. Undistributed SEAM/MIRL internals, SEAM-U assets, hosted control
planes, private training/evaluation data, deployment credentials, and customer
records remain All Rights Reserved and confidential. Access is granted only by
employment, contractor, customer, research, or commercial agreement.

Publishing a repository is a distribution decision. Moving source from a
private repository into a PolyForm Shield product requires an explicit boundary
review, provenance scan, artifact scan, and history record.

## Ghost migration boundary

Ghost's current candidate uses an independently authored opaque HTTP adapter.
It contains no private SEAM import or Git dependency and preserves the full
reasoning/action lifecycle through additive service routes.

```text
CURRENT PUBLIC PATH
Ghost ──HTTP adapter──► authenticated SEAM API ──► private SDK/runtime

TARGET ENTERPRISE PATH
Ghost ──open client──► licensed local SEAM node ──► private runtime package
```

The code/API path is implemented but is not yet a published package or hosted
deployment. Those claims require protected merge, immutable artifact
qualification, an available compatible service, and the deployment gates below.

## Canticle Core boundary

Canticle Core is planned as an agent-native operating environment on Linux,
not a replacement kernel. Its source-available operator product may include the
virtual namespace, FUSE adapter, typed operation protocol, permission UX, and
Ghost integration under PolyForm Shield.

The canonical SEAM database implementation, MIRL compiler, hosted identity and
entitlement systems, enterprise fleet control, and SEAM-U inference remain
behind proprietary boundaries. Thin remote clients and protocol bindings may
be Apache-2.0.

Because filesystem metadata operations cannot tolerate ordinary WAN latency,
the design needs a local service boundary for `stat`, `list`, and read paths.
That local service can be a licensed SEAM node or a bounded cache backed by the
hosted service. A design that sends every FUSE syscall to a remote API does not
satisfy Canticle Core's stated latency contract.

## SEAM-U boundary

SEAM-U is the planned first SEAM-native language model. No model repository,
weights, tokenizer, training corpus, or qualified checkpoint was located during
the 2026-08-25 reconciliation. The name is approved; implementation and model
claims remain planned.

The default commercial boundary is:

- model cards, safety/evaluation summaries, and API examples may be public;
- client access uses the same Apache-2.0 integration edge;
- weights, optimizer state, training code, data mixture, data licenses,
  alignment artifacts, and production inference remain proprietary;
- customer inputs/outputs are governed by product and privacy terms; and
- any future open-weight release requires its own model-license decision and
  cannot inherit a software license by accident.

## Revenue surfaces

The license architecture supports multiple revenue lanes without charging for
every clone:

- hosted Ghost subscriptions;
- SEAM memory/API usage;
- SEAM-U inference usage;
- managed Canticle Core workspaces;
- enterprise self-host and air-gapped licenses;
- OEM/embedded/competing-use licenses outside PolyForm Shield;
- support, deployment, migration, compliance, and recovery services; and
- custom evaluation, research, and integration agreements.

Pricing, entitlements, service levels, and refund terms belong in commercial
documents, not in the source license.

## Ownership before and after incorporation

At this local candidate boundary, the identified copyright holder is Nicholas
Thomas. A future company cannot own pre-incorporation intellectual property
merely because its brand name appears in a repository.

After the company exists, execute a written founder IP assignment covering the
repos, designs, documentation, domains, trademarks, model artifacts, datasets,
inventions, and related contract rights. Then update notices to the company's
exact legal name prospectively. Do not backdate or silently rewrite historical
copyright records.

See [company IP readiness](../legal/COMPANY_IP_READINESS.md) for the operational
checklist and [licensing structure](../legal/LICENSING_STRUCTURE.md) for
repository placement rules.

The root [contribution policy](../../CONTRIBUTING.md) pauses external pull
requests until the receiving entity and contributor agreement exist. The root
[trademark policy](../../TRADEMARKS.md) keeps brand permission separate from
the software grant.
