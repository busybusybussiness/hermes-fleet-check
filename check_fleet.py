#!/usr/bin/env python3
"""check_fleet.py - lint an agent-fleet config (roles -> model tier, fallback chain, cadence).

Stdlib only. Usage:  python check_fleet.py fleet.json
Exit 0 = no findings, 1 = findings printed, 2 = unreadable input.

Checks (each one is a failure mode we hit in practice):
  - every role has a valid tier
  - every LLM role has a primary model AND at least one fallback (no single point of failure)
  - no model appears twice in one role's chain
  - no role's chain contains a model listed in disabled_models (dead providers / exhausted quotas)
  - no-LLM roles name no model
  - cadence is set and not faster than the floor (default 60 minutes)
"""
import json
import sys

TIERS = {"oversight", "operator", "volume", "free", "no-llm"}
DEFAULT_CADENCE_FLOOR_MIN = 60


def check(cfg):
    """Return a list of human-readable findings. Empty list = pass."""
    findings = []
    if not isinstance(cfg, dict):
        return ["top level must be a JSON object"]
    roles = cfg.get("roles")
    if not isinstance(roles, list) or not roles:
        return ["config has no 'roles' list"]
    floor = cfg.get("cadence_floor_minutes", DEFAULT_CADENCE_FLOOR_MIN)
    disabled = set(cfg.get("disabled_models", []))

    seen = set()
    for r in roles:
        name = r.get("name") or "<unnamed>"
        if name in seen:
            findings.append(f"{name}: duplicate role name")
        seen.add(name)

        tier = r.get("tier")
        if tier not in TIERS:
            findings.append(f"{name}: unknown tier {tier!r}")

        if tier == "no-llm":
            if r.get("model") or r.get("fallbacks"):
                findings.append(f"{name}: no-llm role must not name a model")
        else:
            model = r.get("model")
            fallbacks = r.get("fallbacks") or []
            if not model:
                findings.append(f"{name}: no primary model")
            if not fallbacks:
                findings.append(f"{name}: no fallback model (single point of failure)")
            chain = ([model] if model else []) + list(fallbacks)
            if len(set(chain)) != len(chain):
                findings.append(f"{name}: same model appears twice in its chain")
            for m in chain:
                if m in disabled:
                    findings.append(f"{name}: chain uses disabled model {m!r}")

        cad = r.get("cadence_minutes")
        if cad is None:
            findings.append(f"{name}: no cadence_minutes")
        elif not isinstance(cad, (int, float)) or cad < floor:
            findings.append(f"{name}: cadence {cad} min is below the {floor} min floor")
    return findings


def main(argv):
    if len(argv) != 2:
        print("usage: python check_fleet.py fleet.json")
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read {argv[1]}: {e}")
        return 2
    findings = check(cfg)
    if not findings:
        print(f"PASS: {len(cfg['roles'])} roles, no findings")
        return 0
    for line in findings:
        print("FAIL: " + line)
    print(f"{len(findings)} finding(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
