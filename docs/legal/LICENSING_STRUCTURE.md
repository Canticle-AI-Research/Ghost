# Licensing structure

**Current licensor:** Nicholas Thomas.

**Future licensor:** the exact legal entity formed for Canticle, only after a
written assignment makes that entity the relevant owner or authorized licensor.

## Three software lanes

### Lane A — Apache-2.0 open integration edge

Use for thin clients, schemas, protocol bindings, examples, and connectors that
contain no protected implementation. These components may be embedded in
commercial and competing applications. That permissiveness is intentional: it
makes the service easier to adopt.

Required repository evidence:

- full Apache-2.0 `LICENSE`;
- `NOTICE` with copyright and attribution where appropriate;
- package metadata containing `Apache-2.0`;
- artifact scan proving no private modules or assets ship;
- dependency-license inventory; and
- public API compatibility tests.

### Lane B — PolyForm Shield source-available products

Use for software distributed in source form that customers and operators need
to run or modify, but that should not become a competing product.

Required repository evidence:

- the unmodified PolyForm Shield 1.0.0 text;
- a `Required Notice:` line identifying copyright and license;
- a specific `Licensor Line of Business:` line;
- metadata using an appropriate `LicenseRef` when the package format requires
  an SPDX expression not present in the SPDX License List;
- explicit trademark and excluded-asset notice;
- a commercial-license contact; and
- public language calling the work **source-available**, never open source.

PolyForm Shield does not mean “noncommercial.” A company may use the software
commercially when its use does not provide a competing product. If Canticle
wants to prohibit all commercial use, Shield is not the correct license.

### Lane C — permanent proprietary core

Use for source and artifacts Canticle does not distribute generally: SEAM and
MIRL internals, SEAM-U weights/training systems, cloud control planes, private
datasets, secrets, customer records, and unreleased research.

Controls are operational as well as textual:

- private repositories and least-privilege access;
- All Rights Reserved/confidential notices;
- employee and contractor invention-assignment agreements;
- customer/partner nondisclosure and commercial agreements;
- artifact allowlists and release scans;
- secret management and audit logs; and
- prompt removal of access when a role or contract ends.

## Placement table

| Repository/product | Lane | Reason |
|---|---|---|
| Ghost | B | user-runnable source product; protect against competing products |
| Canticle Core | B | user-runnable source product/OS environment |
| source-distributed SEAM SDK | B | exposes valuable in-process capabilities but must be usable by Ghost/operators |
| source-distributed SEAM Node | B | self-host product; competing service restriction matters |
| thin SEAM/Canticle client | A | adoption and embedding layer only |
| API schema and examples | A | integration contract, not implementation advantage |
| private SEAM runtime/MIRL | C | canonical proprietary implementation |
| SEAM-U model/training | C | planned proprietary model and data assets |
| cloud/identity/billing/fleet control | C | undistributed hosted implementation |
| logos, names, mascots, trade dress | separate | trademark/copyright assets are not software grants |

## Dual and commercial licensing

The copyright owner can offer the same PolyForm Shield work under a separate
commercial agreement. That agreement can grant competing use, OEM embedding,
private forks, redistribution, warranties, indemnity, support, or enterprise
self-hosting. The public Shield grant remains unchanged for everyone else.

To preserve this ability after outside contributions begin, Canticle needs a
contributor agreement that grants the company sufficient rights to relicense
contributions. A Developer Certificate of Origin alone confirms provenance but
does not necessarily grant broad relicensing authority.

Until that agreement and the receiving entity exist, Ghost does not accept
external pull requests. The root `CONTRIBUTING.md` records this temporary
inbound-IP boundary. The root `TRADEMARKS.md` separately governs brand use.

## Prohibited documentation language

Do not describe PolyForm Shield components as:

- open source;
- Apache licensed;
- free for every commercial use;
- restricted solely to Ghost; or
- equivalent to a private trade-secret repository.

Do not describe planned SEAM-U or Canticle Core components as shipped,
released, qualified, hosted, or available until their own evidence supports it.
