# Company IP readiness

This is the operational checklist for moving the current founder-owned work
into a company. It intentionally separates formation, ownership, licensing,
distribution, and product contracts.

## Before formation

- Choose the legal entity type, jurisdiction, exact legal name, registered
  agent, ownership/capitalization, and tax treatment with qualified advisors.
- Inventory every repository, domain, package name, social account, design,
  logo, model artifact, dataset, paper, invention, vendor account, and contract.
- Record the current owner and every contributor for each asset.
- Preserve Git history and dated design records as authorship evidence.
- Identify third-party code, models, fonts, datasets, generated assets, and
  provider terms; do not assume paid access transfers ownership.
- Stop accepting contributions without an explicit inbound contribution policy.
- Keep the interim root `CONTRIBUTING.md` pause in force until the receiving
  entity and counsel-reviewed contributor agreement exist.
- Keep the founder's legal name as licensor until an entity actually exists and
  an assignment is executed.

## At formation

Have counsel prepare and execute, as applicable:

- founder stock/equity purchase and vesting documents;
- proprietary information and invention assignment agreement;
- founder-to-company IP assignment covering all scheduled pre-formation assets;
- board/member approval accepting the assignment;
- contractor and employee invention-assignment templates;
- confidentiality and security agreements;
- contributor license agreement with commercial relicensing rights;
- trademark ownership/filing plan; and
- domain, package registry, cloud, and repository-account transfer records.

The IP schedule should name assets precisely rather than saying only “all code.”
Include Ghost, SEAM, MIRL, the SEAM SDK/client/node/runtime, Canticle Core,
SEAM-U, Canticle.cc, branding, documentation, research artifacts, model assets,
datasets the founder owns, domains, package names, and associated goodwill.

## Immediately after assignment

- Update copyright notices to the exact legal entity name prospectively.
- Keep the signed assignment and approvals in the corporate record book, not a
  public repository.
- Update GitHub organization ownership, registries, domains, cloud billing,
  banking, and vendor accounts to company-controlled identities.
- Require hardware-backed MFA, recovery codes under company control, scoped
  service accounts, and a documented access-removal process.
- Create `legal@`, `privacy@`, `security@`, and `licensing@canticle.cc` routing.
- Record which person can sign commercial licenses and security/privacy terms.

## Repository controls

For every active repository, maintain:

- one authoritative `LICENSE`;
- required `NOTICE` and trademark/excluded-asset language;
- correct package metadata;
- a public/private/source-available classification;
- an owner and release authority;
- a dependency and artifact provenance report;
- secret scanning and branch protection;
- a release checklist; and
- an append-only decision/history record.

Mixed-license monorepos need file-level boundaries and automated package-member
tests. A top-level license alone is not enough when private, open, brand, and
third-party assets coexist.

## SEAM-U model readiness

Before training or distributing SEAM-U, establish:

- provenance and permitted use for every training/evaluation dataset;
- provider/model terms for synthetic data and distillation;
- consent, privacy, deletion, retention, and security rules;
- ownership and assignments for training code, weights, adapters, tokenizer,
  prompts, annotations, and evaluation results;
- export-control, sanctions, safety, and high-risk-use review;
- model card, limitations, evaluation protocol, and incident process;
- input/output and customer-data terms; and
- a separate decision for API-only, controlled weights, or public weights.

Do not apply a software repository license to model weights by implication.

## Trademark and brand readiness

- Search for conflicting marks before investing further in names.
- Decide which word marks and logos should be filed and in which product/service
  classes.
- Use marks consistently and preserve specimens of actual commerce.
- Publish a trademark policy permitting truthful reference while prohibiting
  false endorsement and rebranding of forks.
- Replace or ratify the interim root `TRADEMARKS.md` policy after the mark owner
  and filing strategy are confirmed.
- Keep source-code licensing separate from trademark permission.

## Evidence packet for counsel

Prepare one bounded packet containing:

1. the product/licensing matrix;
2. repository and contributor inventory;
3. current licenses/notices and proposed changes;
4. founder IP schedule;
5. third-party dependency/model/data inventory;
6. planned revenue channels and customer types;
7. hosted versus self-hosted architecture;
8. privacy/data flows; and
9. the questions requiring jurisdiction-specific advice.

This repository records the engineering boundary. Counsel should validate the
entity, assignment, trademark, employment, privacy, tax, export, warranty,
indemnity, and enforcement language before commercial launch.
