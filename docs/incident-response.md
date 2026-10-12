# Incident exercise: rejected SSH followed by HTTP markers

Objective: correlate network and host evidence, identify the lab source and target,
decide whether authentication succeeded, and explain appropriate containment.
This is a planned educational activity, not a real compromise.

## Prepare and generate the controlled sequence

Review isolation and UTC time. From Kali, after host key enrollment:

```bash
python3 cyberlab.py simulate ssh --dry-run --count 3
python3 cyberlab.py simulate ssh --confirm-isolated --count 3
python3 cyberlab.py simulate urls --confirm-isolated
```

Observe target auth and HTTP logs, monitor EVE and the Grafana investigation
panels. The repository's fixed-year-2000 fixtures are a separate synthetic
training example; they are not evidence that these commands ran successfully.

## Investigate

1. Establish the earliest event time and clock reliability. State which timestamp
   is event time versus collection time.
2. Identify source `.10`, target `.20`, SSH/HTTP ports from the shared config,
   and verify those roles from observed records rather than assumption alone.
3. Find invalid-user/preauth rejection messages. Compare them with any Accepted
   records in the window. A connection/SYN or HTTP status 200 is not SSH success.
4. Identify the URL marker SIDs and any repeated-connection/frequency signatures.
   Explain threshold behavior and possible false positives.
5. Correlate Nginx path/status/source records and Suricata HTTP/flow IDs. Account
   for encrypted SSH content, missing records, duplicate rejection lines, packet
   drops, queue loss or stale timestamps.
6. Decide what evidence supports access success, rejection or uncertainty. The
   demo application has no real accounts; its HTTP 200 only proves a response.

## Contain, preserve and recover

Stop the planned simulation if traffic is unexpected. Restrict the lab source
using the guest firewall or disconnect its private adapter manually, while
preserving VM console access. Keep original logs/snapshots privately and record
hashes/timeline in a private case folder. Do not alter evidence to match an
expected result. Fix route, firewall, SSH, sensor or ingestion configuration as
appropriate, then rerun one bounded verification exercise.

Use [the report template](../reports/templates/incident-report.md). Include facts,
limitations, containment reasoning, recovery observations and improvements.
For a public portfolio, rewrite the narrative with synthetic identifiers and
reviewed screenshots rather than uploading raw evidence.

## Questions for a portfolio discussion

- Why is a Suricata SSH connection alert insufficient to infer authentication failure?
- How can a switched VMware Workstation Pro network hide traffic from the monitor?
- What distinguishes a blocked port, a closed port and a service responding?
- Why does HTTP 200 on a marker path not imply exploitation?
- Which missing observations would change the incident conclusion?
