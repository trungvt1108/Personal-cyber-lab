# Installation: Windows host and VMware Workstation Pro guests

No VMs are created automatically. Start with official installers/images:
[VMware Workstation Pro](https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion),
[Kali](https://www.kali.org/get-kali/) and
[Ubuntu Server 24.04 LTS](https://releases.ubuntu.com/24.04/).
Verify the publisher's image checksums. Install Git, VS Code and Python 3.12+ on
Windows if you want offline CLI checks. This guide uses VMware Workstation Pro on Windows; ESXi port-group settings are different.

## 1. Check the host without changing it

In PowerShell at the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/windows/check-prerequisites.ps1
powershell -File scripts/windows/show-network-plan.ps1
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe cyberlab.py validate-config
```

`ExecutionPolicy Bypass` applies to this process; it does not change the Windows
policy permanently. The scripts only check prerequisites and print a network
plan. Missing tools are reported; they are not installed silently.

## 2. Create the machines manually

Create `LAB-KALI`, `LAB-TARGET` and `LAB-MONITOR` using the RAM/CPU/disk table in
[architecture.md](architecture.md). Use an ordinary generic guest account such
as `labuser` with sudo rights on Ubuntu. Set a unique password locally during
installation; no password belongs in the repo. Import a Kali VM or install it.
Never reuse personal credentials. Verify the SSH server is installed on Ubuntu.
Change any default account password supplied by an imported Kali image locally.

While the VMs are powered off, confirm for each:

1. Network Adapter 1: **NAT**, no port forwarding; Connected only during setup.
2. Add Network Adapter 2: **LAN Segment**, name `cyberlab-internal` on all VMs.
   Create it using VM Settings → Network Adapter → LAN Segments. No DHCP is provided.
3. For isolation, uncheck NAT **Connected** and **Connect at power on** on all VMs.
   Suricata requests guest promiscuous capture; verify peer traffic using the detection guide.
4. Shared folders, clipboard and drag/drop are disabled. No bridged adapter exists.
5. IPv4 forwarding between the guest adapters is not configured.

Take a clean snapshot after the OS installation. Copy only project source into
the guests using a temporary read-only ISO or another method you review. Do not
include `.venv`, `.env`, personal files or credentials. Avoid leaving host shares
attached. The repository should be present on Kali and both Ubuntu guests at
`/opt/personal-cyber-lab` before running Ansible; make the source readable.

## 3. Assign static private addresses from VM consoles

Run `ip -br link` in each guest; compare adapter MACs in VMware Workstation Pro locally to
identify the private NIC, without copying MACs into the repo. Edit the example
interface names in `config/lab.yml` if necessary. The Ubuntu examples use
`ens33` for NAT and `ens37` for LAN Segment; your VM may use different names. Keep configurations consistent
across the source copies. A lab address has no gateway and no DNS.

Ubuntu: `python3-yaml` is needed for the network renderer. During the update
window, install it with `sudo apt-get install python3-yaml`. From the project root:

```bash
python3 cyberlab.py render-network target
# On monitor use: python3 cyberlab.py render-network monitor
sudo install -m 600 .generated/50-cyberlab-target.yaml /etc/netplan/50-cyberlab.yaml
sudo netplan try
```

Review existing Netplan files first; avoid defining the same interface twice.
`netplan try` provides a timed rollback when connectivity breaks. Confirm from
the console, then check `ip -br address`. The renderer leaves NAT DHCP available
for update windows; cable disconnection is a separate manual action.

Kali: use NetworkManager rather than Netplan. After checking `eth1` is your lab
NIC, run these commands manually from the console, substituting values from your
config if changed:

```bash
sudo nmcli connection add type ethernet ifname eth1 con-name cyberlab-private \
  ipv4.method manual ipv4.addresses 192.168.56.10/24 ipv4.never-default yes \
  ipv6.method disabled
sudo nmcli connection up cyberlab-private
bash scripts/linux/bootstrap-kali.sh --confirm-lab-guest
```

Do not run the `connection add` repeatedly: if it exists, use `nmcli connection
modify cyberlab-private ...`. Check that an old auto-DHCP connection is not
active on the same NIC. These commands change only the Kali guest's network.

## 4. Enroll keys and host fingerprints

Create a unique lab SSH key **outside the repo** on Kali with a passphrase:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/cyberlab_lab
```

At each Ubuntu console, print its host fingerprint with
`sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`. Compare that fingerprint
when first connecting from Kali. Never disable host key checks or use a blind
`ssh-keyscan` as verification. Install `<SSH_PUBLIC_KEY>` in the lab account's
`~/.ssh/authorized_keys` using the console or verified `ssh-copy-id` during
bootstrap, then verify key login. Set `.ssh` to 700 and `authorized_keys` to 600.
No public/private key or known_hosts file is committed.

```bash
ssh-copy-id -i ~/.ssh/cyberlab_lab.pub labuser@192.168.56.20
ssh-copy-id -i ~/.ssh/cyberlab_lab.pub labuser@192.168.56.30
ssh -i ~/.ssh/cyberlab_lab labuser@192.168.56.20
```

If your lab account differs, change only the ignored local inventory override;
never copy a identifying real username into public templates. Add the key to a
local SSH agent or pass its location using Ansible's `--private-key` argument.

## 5. Prepare and deploy the Ubuntu services

Run Ansible from Kali. NAT may be enabled here because package/image installation
needs an update window. Connections still use the validated lab addresses.

```bash
cd /opt/personal-cyber-lab/ansible
ansible-playbook playbooks/site.yml --private-key ~/.ssh/cyberlab_lab --ask-become-pass
```

The first play validates shared config locally before any guest connection. The
same checks run before facts/roles on each guest play, including with `--limit`.
An inventory address override or a mismatched guest config aborts deployment.
The common role verifies that the learner has an authorized key before disabling
password SSH. It keeps guest source files unchanged, installs required packages,
sets generic hostnames and applies restricted rules. Review existing firewall
rules on non-fresh guests. The automation never creates SSH keys or passwords.

Ubuntu 24.04 uses [SSH socket activation](https://discourse.ubuntu.com/t/sshd-now-uses-socket-based-activation-ubuntu-22-10-and-later/30189/1).
The common role validates SSH, disables that socket and removes its migration
overrides, then enables the ordinary SSH service. This makes the configured
private `ListenAddress`/port apply to the listener. Keep guest console access
available during activation changes; verify `sudo ss -lntp` and key login after
deployment. This transition has not been executed here.

If guest sudo passwords differ, deploy one role at a time with separate prompts:
add `--limit localhost,kali`, then `--limit localhost,target`, then
`--limit localhost,monitor` to the playbook command. Including localhost preserves
the configuration check. Never store become passwords in public inventory.

On target, start the demo service after deployment:

```bash
cd /opt/personal-cyber-lab
sudo docker compose -f docker/target/compose.yml up -d --build
sudo nginx -t
```

On monitor in standard mode, create a Grafana secret using a hidden interactive
prompt; the script stores it only in ignored `local/` with mode 600:

```bash
cd /opt/personal-cyber-lab
bash scripts/monitoring/start-stack.sh --confirm-lab-guest
bash scripts/monitoring/start-stack.sh --confirm-lab-guest ps
```

The launcher validates Alloy before startup. Use `logs` for recent diagnostics
or `validate` to rerun Alloy syntax validation. These commands supply both required
Compose variables; a bare Compose command does not inherit them.

The source copies must have the same IP/interface/port configuration. In
lightweight mode omit the dashboard stack and use central log files plus reports.

## 6. Disconnect Internet and validate from Kali

Power off each VM, disconnect adapter 1's NAT cable, and start all three. Confirm
Kali has no IPv4/IPv6 default routes. Disable an active stale NAT connection in
NetworkManager or reboot if needed. Inspect VMware Workstation Pro settings again.

```bash
python3 cyberlab.py preflight --confirm-isolated
bash scripts/validate-lab.sh --confirm-isolated
python3 cyberlab.py simulate urls --dry-run
python3 cyberlab.py simulate urls --confirm-isolated
```

Open `http://192.168.56.30:3000` **in the Kali browser**, using `labadmin` and your
unique local password. No Windows browser access exists in LAN Segment mode.
Follow [detection-guide.md](detection-guide.md) to prove the log-to-dashboard path.
Take a clean configured snapshot before exercises. Record results honestly.
