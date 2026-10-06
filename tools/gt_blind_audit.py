"""GT-blind audit: replay every frozen output through the packaged provider under a Python audit hook that records
every file opened. Fails if any ground-truth file (ParseBench *.jsonl rules, *.test.json sidecars) is ever opened.

usage: gt_blind_audit.py <frozen_outputs/<arm>>"""
import glob, json, os, sys
OPENED = set()


def hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        OPENED.add(os.fspath(args[0]) if not isinstance(args[0], bytes) else args[0].decode(errors="replace"))


sys.addaudithook(hook)
from parse_bench.inference.providers.parse.byteverity.provider import ByteVerityProvider  # noqa: E402
from parse_bench.schemas.pipeline_io import RawInferenceResult  # noqa: E402

arm = sys.argv[1]
files = sorted(glob.glob(f"{arm}/*/*.raw.json"))
before = set(OPENED)
p = ByteVerityProvider("byteverity", {"stage": "full"})
for f in files:
    p.normalize(RawInferenceResult.model_validate_json(open(f).read()))
opened = OPENED - before
gt = sorted(x for x in opened if x.endswith(".jsonl") or x.endswith(".test.json") or "expected_markdown" in x)
kinds = {}
for x in opened:
    k = os.path.splitext(x)[1] or "(none)"
    kinds[k] = kinds.get(k, 0) + 1
print(f"replayed {len(files)} documents; distinct files opened {len(opened)} by type {dict(sorted(kinds.items()))}")
print("GROUND-TRUTH FILES OPENED:", gt if gt else "NONE")
sys.exit(1 if gt else 0)
