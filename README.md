# ByteVerity Parse × ParseBench: public evidence bundle

**Claim.** `byteverity_parse` and `byteverity_parse_hybrid` score **81.46** and **82.11** on ParseBench (public set,
2,078 pages, unmodified scorer at commit `afb36bd`). Both scores reproduce exactly from the frozen model outputs here.
No ground-truth file is read while outputs are produced. Every rule-based decision comes from one of 17 sealed
decision oracles, shipped as **complete decision tables** with the provider.

Everything below runs offline, with no model or API key and no ByteVerity binaries.

| # | Establishes | Check | Expected |
|---|---|---|---|
| 1 | Bundle authenticity (every file hashed and signed, Ed25519) | `python tools/verify_manifest.py manifest.signed.json` (dependency-free) | `signature: VALID … files: N/N match` |
| 2 | Exact score reproduction | from a ParseBench checkout with the PR's `byteverity` provider: `python tools/reproduce.py frozen_outputs/<arm> <ParseBench>/data work/` then `parse-bench run <arm> --input_dir <ParseBench>/data --output_dir work --skip_inference` | `reproduction*.txt`: 82.11 / 81.46, every dimension matching `claimed_scores.json` |
| 3 | Decisions are sealed and complete | `decision_tables/*.table.json`: each table's SHA-256 is pinned in `PINS.json`; every cell of the declared input domain has exactly one decision (the provider refuses to start otherwise; `tests/.../test_byteverity.py`) | 17 tables, 14,083 cells, all present |
| 4 | No ground truth at inference | `tools/gt_blind_audit.py` (Python audit hook) and `tools/gt_blind_strace.sh` (OS-level `openat`, including native MuPDF) | `GROUND-TRUTH FILES OPENED: NONE` at both levels (`gt_blind_*.txt`) |
| 5 | The oracles were proven before sealing | `oracle_proofs/SUMMARY.txt` plus each oracle's signed validity evidence envelope (`.validity/evidence.json`, trusted signer `08da8d8a…`) | 18 × VERIFIED · COMPLETE · PRODUCTION READY · VALID |
| 6 | How the system got here | `python tools/verify_ledger.py` (every admitted *and rejected* change, with measured scores) | `LEDGER OK: 59 entries, chain intact` |

## What this bundle cannot prove
Nothing cryptographic shows that the frozen outputs came from GPT-6 Luna or Sol, because API responses carry no
provider signature. That is settled the standard way: **an independent run by the ParseBench maintainers with their
own `OPENAI_API_KEY`**, using the PR's provider. It logs tokens and cost for every call. The model samples its
output, so an independent run will differ slightly. The deterministic layer (checks 2–3) is fixed.

## Contents
- `frozen_outputs/<arm>/<group>/*.raw.json`: every page's model output plus the residual evidence the provider
  records (layout detections, emphasis claims, table-zoom answers). These replay with no other inputs.
- `decision_tables/`: the 17 sealed oracles' complete decision tables and their pins (identical to the PR's).
- `oracle_proofs/`: per-oracle verification summaries and signed validity evidence envelopes. The oracle sources and
  the synthesa-decide engine are proprietary and not included.
- `ledger/`, `claimed_scores.json`, `reproduction.txt` (hybrid), `reproduction_luna.txt` (Luna-only), `gt_blind_*.txt`,
  `files_opened_os_level.txt`, `tools/`, `manifest.signed.json`.

## Download
The full bundle (frozen outputs, proofs, ledger, audits) is the release asset `byteverity-parsebench-evidence-v1.tar.gz`; its SHA-256 is in `SHA256SUMS`. Extract it and run the checks above from its root.
