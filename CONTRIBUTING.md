# Contributing

Keep changes educational, local and defensive. Preserve default-deny validation
for every network entry point. Include regression tests for changes to safety
controls, parsing and report escaping. Do not attach real logs, keys, screenshots
or packet captures to issues or pull requests.

Run the checks in [docs/testing.md](docs/testing.md). Live VM checks are opt-in
and are never run by CI. Document skipped checks accurately. Review the
publication checklist before staging explicit filenames; never stage blindly.

Use clear commit messages and explain observable behavior and validation in pull
requests. Dependencies must have an upstream source and a documented purpose.
