# ADR 0004: Open edge, shielded product, proprietary core

- Status: accepted locally; publication and counsel review pending
- Date: 2026-08-25
- Decision owner: Nicholas Thomas

## Context

Ghost needs broad usability without transferring Canticle's general-purpose
memory, runtime, model, and hosted-service advantage to competitors. BUSL's
mandatory future license conversion does not provide permanent restrictions.
A fully proprietary client creates installation and integration friction.

## Decision

Use three lanes:

1. Apache-2.0 for thin clients and integration protocols with no protected
   implementation.
2. PolyForm Shield 1.0.0 for user-runnable source-available product software,
   including Ghost, Canticle Core, and source-distributed SDK/node surfaces.
3. Permanent proprietary controls for private SEAM/MIRL internals, SEAM-U
   weights/training, cloud control planes, private data, and confidential work.

Branding and trademarks remain outside software grants. Commercial agreements
may grant additional rights to PolyForm Shield work.

## Consequences

- PolyForm components must be called source-available, not open source.
- Ghost's current private in-process dependency remains an internal topology;
  public distribution requires a complete API/client path or licensed local
  node.
- External contributions need inbound terms sufficient for commercial
  relicensing.
- Current founder-owned IP must be assigned in writing after the company is
  formed.
- Every package must have artifact tests that enforce its intended boundary.

## Non-decision

This ADR does not form a company, assign IP, register trademarks, publish a
package, create SEAM-U, or substitute for legal advice.
