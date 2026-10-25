# hermes-fleet-check

A small, standard-library-only linter for a multi-agent fleet config (roles, model tiers, fallback chains, cron cadence).
It exits 1 on any finding, so you can run it in CI or before you change a schedule.

## What it checks
- every role has a valid tier (`oversight`, `operator`, `volume`, `free`, `no-llm`)
- every LLM role has a primary model and at least one fallback
- no model appears twice in one role's chain
- no chain contains a model listed in `disabled_models` (dead providers, exhausted quotas)
- no-LLM roles name no model
- cadence is set and not faster than a floor (default 60 minutes)

## Use
```
python check_fleet.py examples/good_fleet.json   # PASS, exit 0
python check_fleet.py examples/bad_fleet.json    # 7 findings, exit 1
python test_check_fleet.py                       # 4 tests
```
Config shape: see `examples/good_fleet.json`. Model names in the examples are placeholders, not recommendations.

## Limits
It checks structure only. It does not check that a model exists, is reachable, or is priced as you expect.
It is not affiliated with or endorsed by the Hermes Agent project.

## Related (paid, optional)
The same author sells a written reference built from one operator's own fleet (tiers, fallback pattern, cadence rules, kill switch, role charter template):
[Hermes Fleet Cost & Ops Kit, $19](https://busybusiness.gumroad.com/l/jiznum). The linter here is free and stands alone.

Disclosure: AI-assisted drafting; the operator reviewed and ran the code.

MIT licensed.
