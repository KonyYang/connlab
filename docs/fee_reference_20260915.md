# Fee reference version 2026-09-15

The active Fee Evaluation default rules are compiled from `FDQF-E-176 Testing Fee Evaluation_Rev_F_20260915.xlsx`, sheet `Unit Price Reference`, source rows 4–52 and discount policy row 54. The reviewed workbook SHA-256 is `c230445ad8620ee4d6ad178717d45f0a7d75b249342db3e98b752aa5db56d27f`. Generation reads the checked-in JSON seed, not the workbook. The earlier seed files remain available for historical Fee provenance.

To review a future source revision, create a new versioned snapshot and mapping, validate every source row and ambiguous rule, compile a new seed, and only then switch `active_fee_rule_seed.json`. `scripts/build_fee_reference_20260915.py` documents the one-time compilation of this exact workbook and rejects other file hashes. Do not run it as part of normal Fee generation.

Fee draft defaults read the confirmed Matrix authority, including each Group's sample quantity and confirmed LLCR/CR point authority. They do not consume an in-progress Matrix edit. IR/DWV readings require a confirmed point count (or explicit operator entry); until the planned Matrix Test points support exists, unknown count and specimen-preparation base fee stay in manual review. Other conditional source prices, such as temperature/humidity mode and single-Group report page tier, also require review where the confirmed inputs do not decide the tier. An explicit UI action can copy price and unit type to matching tests in other Groups; each copied row remains editable and must pass the usual Fee confirmation.

The price reference changes only the default for a newly built draft. A previously confirmed Fee is not silently rewritten. Verify source/version provenance when comparing old and new outputs. Current scope does not change Fee Form file-saving or historical import behavior.

Matrix-derived step Base Fee defaults depend on the total number of Groups in the confirmed Matrix,
not the visible Fee group filter. With more than one Group, all step Base Fees default to zero and
Testing Fee is recalculated from that value. With one Group, the existing fixed-amount and duration
rules apply; unresolved inputs retain their existing review requirements. Hovering over a step's
Base Fee input shows its matched Unit Price Reference condition text, such as `<16hours  200`.
These are editable defaults: saved manual pricing edits and confirmed Fee values keep their existing
hydration/rebase behavior. Sample preparation and report preparation retain their separate rules.

Regression boundaries: validate the source hash and exact row coverage, maintain old-seed loadability, assert confirmed-Matrix-only quantities, test manual review for missing counts and tiers, preserve user-edited pricing draft conflict/rebase behavior, and test cross-Group copy exclusions for different conditions. Browser checks must avoid confirming or exporting an existing business project's Fee unless using a disposable fixture.
