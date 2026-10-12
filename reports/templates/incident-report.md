# Incident report template — keep completed live evidence private

Case identifier: `<CASE_ID>`

Evidence source: `<SYNTHETIC_EXAMPLE_OR_PRIVATE_LAB>`

Investigation time window (UTC): `<START>` to `<END>`

## Observations

Record source/destination, ports, event times, Suricata SIDs, auth messages and
HTTP paths. Distinguish telemetry, verified facts, assumptions and missing data.

## Timeline

| UTC time | Source | Target | Observation | Evidence reference |
| --- | --- | --- | --- | --- |
| `<TIME>` | `<LAB_IP>` | `<LAB_IP>` | `<EVENT>` | `<PRIVATE_REFERENCE>` |

## Findings

Was access successful? Cite Accepted/Failed/preauth evidence; absence of a record
is not proof that success never occurred. Did expected IDS rules fire? Did clocks,
sensor coverage, buffering or log rotation affect the evidence?

## Response and lessons

Document appropriate containment within the lab, evidence preservation,
configuration corrections, recovery verification and control improvements.
Keep raw logs and captures private. Create a synthetic public summary if desired.
