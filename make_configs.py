#!/usr/bin/env python3
"""
Generate the ChampSim JSON configs for the ELL305 page-walk-cache study.
Usage:
  python3 make_configs.py /path/to/ChampSim/champsim_config.json out_dir/
Then, for each generated file:
  ./config.sh out_dir/<name>.json && make -j4      # produces bin/<name>
"""
import copy
import json
import sys
from pathlib import Path

# PSC geometry is (sets, ways) per level; sets must be a power of two.
DEFAULT_PSC = {"pscl4": (1, 4), "pscl3": (2, 4), "pscl2": (4, 8)}
# Vavouliotis et al. ISCA'21 Table I: PML4 2-entry FA, PDP 4-entry FA, PD 32-entry 4-way.
ATP_PSC = {"pscl4": (1, 2), "pscl3": (1, 4), "pscl2": (8, 4)}

VARIANTS = {
    # name: (psc geometry, STLB (sets, ways))
    "x86_4lvl":          (DEFAULT_PSC, (128, 12)),
    "x86_4lvl_atp":      (ATP_PSC, (128, 12)),
    "x86_4lvl_pd4":      ({**ATP_PSC, "pscl2": (1, 4)}, (128, 12)),
    "x86_4lvl_pd16":     ({**ATP_PSC, "pscl2": (4, 4)}, (128, 12)),
    "x86_4lvl_pd64":     ({**ATP_PSC, "pscl2": (16, 4)}, (128, 12)),
    "x86_4lvl_pd128":    ({**ATP_PSC, "pscl2": (32, 4)}, (128, 12)),
    "x86_4lvl_stlb768":  (ATP_PSC, (64, 12)),
    "x86_4lvl_stlb3072": (ATP_PSC, (256, 12)),
}


def make_variant(base, name, psc, stlb):
    cfg = copy.deepcopy(base)
    cfg["executable_name"] = f"champsim_{name}"
    cfg["virtual_memory"]["num_levels"] = 4

    ptw = cfg["PTW"]
    for key in ("pscl5_set", "pscl5_way"):
        ptw.pop(key, None)
    for level, (sets, ways) in psc.items():
        ptw[f"{level}_set"] = sets
        ptw[f"{level}_way"] = ways

    cfg["STLB"]["sets"], cfg["STLB"]["ways"] = stlb

    for cache in ("L1I", "L1D", "L2C", "LLC"):
        cfg[cache]["prefetcher"] = "no"
    return cfg


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base = json.loads(Path(sys.argv[1]).read_text())
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, (psc, stlb) in VARIANTS.items():
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(make_variant(base, name, psc, stlb), indent=2) + "\n")
        print(path)


if __name__ == "__main__":
    main()
