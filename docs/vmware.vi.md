# Cài đặt và cập nhật lab trên VMware

Hướng dẫn dùng **VMware Workstation Pro trên Windows**, Kali và hai Ubuntu Server
24.04 LTS. Nếu đã có ba VM, giữ lại VM và thực hiện các bước cập nhật bên dưới.
Mã sửa trong thư mục Windows chưa tự đồng bộ vào `/opt/personal-cyber-lab` của VM.

## 1. Kiểm tra adapter và tên NIC

Tắt VM trước khi chỉnh adapter trong VMware Settings:

| Adapter | Kết nối | Khi chạy bài lab |
| --- | --- | --- |
| Network Adapter 1 | NAT để cài package/image | Bỏ chọn Connected và Connect at power on |
| Network Adapter 2 | LAN Segment `cyberlab-internal` trên cả ba VM | Connected |

Tạo segment bằng **VM Settings → Network Adapter → LAN Segments** rồi chọn cùng
segment cho cả ba máy. LAN Segment không có DHCP hay adapter Windows; đặt IP tĩnh
và mở Grafana trong Kali. Tắt shared folders, clipboard, drag/drop, không dùng Bridged.
Xem [thiết kế mạng và nguồn VMware](network-design.md).

Trong console mỗi VM:

```bash
systemd-detect-virt --vm
ip -br link
ip -br address
```

Lệnh đầu phải trả về `vmware`. Đối chiếu MAC với adapter VMware **tại máy của bạn**
để xác định NIC NAT/LAN. Không cần gửi MAC lên repository. `ens33`/`ens37` trên
Ubuntu và `eth0`/`eth1` trên Kali chỉ là ví dụ. Giữ tên thực tế nếu VM đã có mạng đúng.

## 2. Đồng bộ mã nguồn vào ba VM

Trước khi cập nhật, tạo snapshot riêng; giữ an toàn bản cấu hình hiện tại, SSH key,
`local/`, dữ liệu Grafana/Loki/Alloy và log. Trong PowerShell tại project Windows:

```powershell
.\.venv\Scripts\python.exe scripts/check_repository.py --manifest
.\.venv\Scripts\python.exe scripts/publication_audit.py
.\.venv\Scripts\python.exe scripts/export-source.py
```

ZIP nguồn nằm ở `.generated/personal-cyber-lab-source.zip`. Chỉ chứa file nguồn
Git candidate đã qua scan; không đóng gói runtime, VM hay log. ZIP này không phải
backup VM. Chuyển vào từng guest bằng kênh sao chép bạn đã kiểm tra, chẳng hạn ISO
chỉ đọc; tháo thiết bị chia sẻ sau khi chuyển. Giải nén vào thư mục tạm trước.

Chép source mới vào `/opt/personal-cyber-lab`; không xóa hoặc ghi đè thư mục
`local/`, log, key và dữ liệu runtime. Bản source không chứa các file đó. Với
`config/lab.yml`, đối chiếu bản hiện tại rồi cập nhật NIC đúng trên **cả ba bản sao**.
Giữ IP/port đang dùng nếu đúng phạm vi; Ansible sẽ từ chối cấu hình khác nhau.
Không copy `.venv` Windows vào Linux. Cấu hình triển khai nằm ở `config/lab.yml`;
`CYBERLAB_CONFIG` chỉ chọn input CLI, không sửa dịch vụ đã cài.

## 3. Triển khai trong cửa sổ NAT

Với VM mới, làm theo [installation.md](installation.md) để đặt IP bằng console,
cài `python3-yaml`, chuẩn bị Kali và xác minh SSH fingerprint/key trước Ansible.
Bật NAT tạm thời khi cài package và tải image. Với VM đã cấu hình, kiểm tra NIC/IP
rồi chạy lại playbook từ Kali; `--ask-become-pass` yêu cầu mật khẩu sudo của guest:

```bash
cd /opt/personal-cyber-lab/ansible
ansible-playbook playbooks/site.yml --private-key ~/.ssh/cyberlab_lab --ask-become-pass
```

Giữ console mở khi Ansible sửa SSH/UFW. Nếu key của bạn có tên khác, dùng đường dẫn
key thực tế. Khi sudo password các VM khác nhau, triển khai từng nhóm như hướng dẫn
cài đặt. Đây là lệnh chỉnh guest, không phải lệnh chạy trong PowerShell Windows.

Trên Target:

```bash
cd /opt/personal-cyber-lab
sudo docker compose -f docker/target/compose.yml up -d --build
sudo nginx -t
```

Trên Monitor ở chế độ standard:

```bash
cd /opt/personal-cyber-lab
bash scripts/monitoring/start-stack.sh --confirm-lab-guest
bash scripts/monitoring/start-stack.sh --confirm-lab-guest ps
bash scripts/monitoring/start-stack.sh --confirm-lab-guest logs
```

Launcher kiểm tra VMware/IP, quyền runtime và cú pháp Alloy trước khi khởi động.
Mật khẩu Grafana hiện có được giữ lại; chỉ hỏi khi chưa có file secret. Nếu Alloy
Exited/Restarting, đọc lỗi bằng `logs`; đừng kết luận thành công chỉ vì có Started.
Không sửa quyền log thành 777 hay cho Alloy chạy root.

## 4. Test sau khi ngắt NAT trên cả ba VM

Kiểm tra `ip -4 route show default` và `ip -6 route show default` trên từng máy:
phải không còn default route. Trên Kali:

```bash
cd /opt/personal-cyber-lab
python3 cyberlab.py preflight --confirm-isolated
bash scripts/validate-lab.sh --confirm-isolated
python3 cyberlab.py simulate urls --dry-run
python3 cyberlab.py simulate urls --confirm-isolated
```

Trên Target tạo marker log:

```bash
logger -p authpriv.notice -t cyberlab 'CYBERLAB synthetic pipeline marker'
```

Đợi khoảng 30 giây rồi trên Monitor, trong vòng 10 phút:

```bash
cd /opt/personal-cyber-lab
sudo python3 cyberlab.py alerts --eve /var/log/suricata/eve.json --limit 20
sudo python3 scripts/monitoring/validate-local.py --confirm-isolated
```

Phải thấy SID 1000004–1000006 với source Kali `.10`, destination Target `.20`,
port HTTP đúng và timestamp mới. Validator kiểm tra dịch vụ/container, EVE, auth,
HTTP và cả ba stream trong Loki. Fixture synthetic không được dùng để PASS.
Nếu Target có HTTP 200 mà Monitor không có SID, kiểm tra khả năng bắt peer traffic
theo [detection-guide.md](detection-guide.md); syslog/counter tăng chưa chứng minh
được monitor thấy gói Kali → Target.

Trong trình duyệt **Kali**, mở `http://192.168.56.30:3000`, đăng nhập `labadmin`
bằng mật khẩu riêng đã đặt, kiểm tra SOC Overview và Grafana Explore. Nếu bạn đổi
IP/port, dùng giá trị từ config. Chế độ lightweight không có dashboard và bỏ qua
kiểm tra container/Loki; vẫn phải có EVE và log tập trung.
Nếu chuyển một deployment standard đang chạy sang lightweight, dừng các container
dashboard hiện có thủ công; thay đổi mode không tự dừng hay xóa dữ liệu của chúng.

Chỉ kết luận lab hoạt động khi validator PASS và thấy đúng marker trong dashboard.
Kết quả test offline của source nằm trong [validation-results.md](validation-results.md);
chúng không thay thế kết quả đo trên VMware của bạn.
