[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$checks = @()
$vmwareFound = [bool](Get-Command vmware.exe -ErrorAction SilentlyContinue)
foreach ($programRoot in @($env:ProgramFiles, ${env:ProgramFiles(x86)})) {
    if ($programRoot) {
        $vmwarePath = Join-Path $programRoot 'VMware\VMware Workstation\vmware.exe'
        if (Test-Path -LiteralPath $vmwarePath) { $vmwareFound = $true }
    }
}
$checks += [pscustomobject]@{ Tool = 'VMware Workstation Pro'; Available = $vmwareFound }
foreach ($tool in @('git', 'code', 'python')) {
    $checks += [pscustomobject]@{ Tool = $tool; Available = [bool](Get-Command $tool -ErrorAction SilentlyContinue) }
}
$checks | Format-Table -AutoSize
try {
    $memoryGiB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
    Write-Output "Installed memory: $memoryGiB GiB; standard mode uses about 7 GiB for guests."
} catch {
    Write-Output 'Memory check unavailable; inspect Windows Settings manually.'
}
Write-Output 'Read-only checks completed. No network, VM or firewall settings changed.'
Write-Output 'Manually create the three VMs and verify LAN Segment attachment in docs/installation.md.'
if ($checks.Available -contains $false) { exit 1 }
