# SOC dashboard

`cyberlab.json` is committed dashboard code, built by `scripts/build-dashboard.py`.
The provisioning directory installs a local Loki datasource with UID
`cyberlab-loki`. No dashboard upload API or Grafana Cloud integration is used.

The fourteen panels show event volume, timeline, IDS alerts, source/destination,
protocol, classification priority, authentication rejection lines, popular HTTP
paths and recent evidence. Start with a 30-minute UTC window. Use the live log
panels to expand complete events and correlate SIDs and source addresses.

SSH rejection lines can exceed the number of attempts; do not present them as
unique login failures. Signature priority is inherited from classifications and
needs investigation context. A source-IP-only top list is a ranking of observed
events, not a risk score. Empty panels are not proof that collection is healthy.

In a VM, use Grafana Explore to validate each LogQL expression. Local JSON checks
validate structure and references only; actual LogQL execution is pending until
Loki and the guests are running. Do not fake screenshots or alert totals.
