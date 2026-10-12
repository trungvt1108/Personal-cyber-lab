# cyberlab-cli

Install editable from the repo with `python -m pip install -e .`, or use
`python3 cyberlab.py` with Python/PyYAML already installed. The installed entry
point and convenience file are equivalent. `--config` must precede the command;
it can point to an ignored local configuration. `CYBERLAB_CONFIG` selects the
same file without sending it anywhere. The tool never reads host identity or
uploads telemetry. Offline commands work on Windows; live checks run on Kali.

Deployment scripts and Ansible use `config/lab.yml` on all three source copies.
Custom `--config`/`CYBERLAB_CONFIG` files select CLI input only; they do not rewrite
guest services, inventory or firewall rules. Keep the deployed canonical file
consistent and unset `CYBERLAB_CONFIG` before using the stack launcher.

`verify-guest --source-role monitor --confirm-lab-guest` checks Linux/VMware and
the configured IP/prefix without sending packets. NAT is allowed during this
installation check. `preflight --confirm-isolated` additionally rejects IPv4/IPv6
default routes. It cannot attest VMware adapter settings; review them manually.

```bash
python3 cyberlab.py validate-config
python3 cyberlab.py hosts
python3 cyberlab.py status
python3 cyberlab.py preflight --confirm-isolated
python3 cyberlab.py check-network --confirm-isolated
python3 cyberlab.py check-services --confirm-isolated
python3 cyberlab.py simulate ping --dry-run
python3 cyberlab.py simulate http --confirm-isolated --count 8
python3 cyberlab.py alerts --sample
python3 cyberlab.py report --sample
```

Read EVE and generate real reports **on the monitor** with appropriate local read
permissions, e.g. `sudo python3 cyberlab.py report`. Default log files are the
installed monitor paths. Live reports go only to ignored `reports/private/`;
synthetic reports go to `reports/examples/`. Output path escapes and symlinks
are refused. Report HTML escapes untrusted log text, uses no JavaScript or
external assets, and marks unmeasured system/service status as UNVERIFIED.

`status --live` or `report --live --confirm-isolated` opt in to source-bound
service checks from Kali. For an offline report from copied lab evidence, use
`--eve`, `--auth` and `--http` paths under an ignored private directory. Keep those
files private; never stage the completed report. Missing files are clearly shown,
not replaced with synthetic data automatically.

Exit codes: 0 completed, 1 an observed diagnostic failed, 2 invalid/unsafe input
or runtime error, 3 a live/evidence check was skipped. Dry-run reports zero network
operations. TCP discovery reports both connections and failures; a blocked port
is an expected observation, not proof that no service exists behind the firewall.

Logs are bounded to 32 MiB per file, 64 KiB per line and the latest 5000 valid
records by default. Parser errors, out-of-scope addresses and omitted records
are counted. Metrics describe that retained sample; reports do not silently claim
complete historical coverage. SSH metrics count log lines, not distinct attempts.
