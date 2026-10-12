# Firewall policy

The common Ansible role enables UFW only after allowing source-restricted SSH.
Rules are scoped to the lab interface. It does not flush unrelated existing rules;
start from clean lab snapshots and review `sudo ufw status numbered` for old rules.

Target allows Kali to SSH/HTTP. Monitor allows Kali to SSH/Grafana and target to
TCP syslog. Kali accepts no new inbound service traffic. Default incoming and
routed policies deny, while outbound is allowed for update windows. Exercise
isolation is enforced by disconnected NAT and route checks, not outbound policy.

Review `/etc/ufw/before.rules` ICMP handling: stock UFW permits echo requests for
diagnostics. ICMP demonstrations may report blocked traffic if you change it.
Published Docker ports are loopback only because Docker rules can bypass UFW.
