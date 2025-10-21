import yaml
from pathlib import Path

test_codes = [
    "T023",
    "T029",
    "T031",
    "T033",
    "T034",
    "T037",
    "T039",
    "T040",
    "T041",
    "T046",
    "T047",
    "T048",
    "T058",
    "T059",
    "T060",
    "T061",
    "T067",
    "T074",
    "T109",
    "T116",
    "T121",
    "T123",
    "T126",
    "T130",
    "T131",
    "T168",
    "T170",
    "T184",
    "T191",
    "T195",
    "T196",
    "T197",
    "T200",
    "T201",
]

if __name__ == "__main__":

    config_path = Path("/workspace/src/nre_pipeline/processor/quickumls_processor/config/semantic_types.yml")
    with config_path.open("r", encoding="utf-8") as f:
        semantic_types = yaml.safe_load(f) or {}

    for x in sorted([(t, semantic_types[t] if t in semantic_types else "-------") for t in test_codes], key=lambda x: x[1]):
        print(x)