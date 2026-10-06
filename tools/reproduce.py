"""Reproduce a published score offline from the frozen outputs (no model calls).

  frozen raw outputs --(packaged byteverity provider, sealed rulebook)--> result files --(unmodified ParseBench scorer)--> score

usage: reproduce.py <frozen_outputs/<arm>> <parsebench_data_dir> <work_dir>
then:  parse-bench run <arm> --input_dir <parsebench_data_dir> --output_dir <work_dir> --skip_inference
"""
import glob, os, sys
from parse_bench.inference.providers.parse.byteverity.provider import ByteVerityProvider
from parse_bench.schemas.pipeline_io import RawInferenceResult

arm_dir, data_dir, work = sys.argv[1:4]
arm = os.path.basename(os.path.normpath(arm_dir))
p = ByteVerityProvider("byteverity", {"stage": "full"})
n = 0
for f in sorted(glob.glob(f"{arm_dir}/*/*.raw.json")):
    raw = RawInferenceResult.model_validate_json(open(f).read())
    # point the source PDF at this machine's copy of the ParseBench data
    rel = str(raw.request.source_file_path).split("/docs/")[-1]
    raw.request.source_file_path = os.path.join(data_dir, "docs", rel)
    res = p.normalize(raw)
    out = os.path.join(work, arm, f.split("/")[-2], os.path.basename(f)[: -len(".raw.json")] + ".result.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(res.model_dump_json())
    n += 1
print(f"normalized {n} documents into {work}/{arm}; now run the scorer with --skip_inference")
