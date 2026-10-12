# Synthetic examples only

These JSON lines were authored for unit tests and an example report. They were
not collected from a host or packet capture. All timestamps are deliberately
fixed at 2000-01-01, all addresses are lab examples, and every record is labelled
`synthetic: true`. No real credentials, personal hostnames or account data exist.

Use `cyberlab-cli alerts --sample` or `report --sample`. Do not treat these as live
evidence or feed old timestamps into Loki to prove pipeline health. Real logs
belong outside the tracked tree; the monitor configuration stores them in `/var/log`.
