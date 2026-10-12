# Kali configuration

Use `config/lab.yml` for the lab IP and interface names. The Kali role in Ansible
sets the generic hostname, disables packet forwarding and configures a restrictive
UFW policy. Package bootstrap is separate so installation can use a temporary NAT
window. Live CLI commands bind to Kali's configured lab IP and verify isolation.

Kali uses NetworkManager by default. Configure the static connection from the VM
console as documented; do not install an Ubuntu Netplan configuration on Kali.
