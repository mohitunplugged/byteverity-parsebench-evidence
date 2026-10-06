"""Verify the hash-chained ratchet ledger: every entry_hash recomputes and every prev link holds."""
import hashlib, json, sys
path = sys.argv[1] if len(sys.argv) > 1 else "ledger/ratchet_ledger.jsonl"
L = [json.loads(l) for l in open(path)]
prev = "0" * 64
for i, e in enumerate(L):
    body = {k: v for k, v in e.items() if k != "entry_hash"}
    h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    assert h == e["entry_hash"], f"entry {i} ({e['name']}): hash does not recompute"
    assert e["prev"] == prev, f"entry {i} ({e['name']}): broken chain link"
    prev = e["entry_hash"]
verdicts = {}
for e in L: verdicts[e["verdict"]] = verdicts.get(e["verdict"], 0) + 1
print(f"LEDGER OK: {len(L)} entries, chain intact, head {prev[:16]}…  verdicts {verdicts}")
