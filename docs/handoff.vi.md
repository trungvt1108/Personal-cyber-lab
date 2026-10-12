# Bàn giao Personal Cyber Lab

Mã nguồn, template và tài liệu đã được rà soát và chuyển sang VMware Workstation Pro.
Ba VM đã hoạt động; ảnh thực hành xác nhận URL marker, SSH rejection,
discover/HTTP và validator Monitor đạt đủ 15 PASS. Kết quả VM dựa trên bằng chứng
người dùng cung cấp; log/ảnh/hash thật được giữ private.
Xem [hướng dẫn cập nhật và test VMware](vmware.vi.md).
Trạng thái công khai: **NOT READY** cho tới khi chủ repository hoàn tất các mục
review trong [publication audit](../PUBLICATION_AUDIT.md). Bản source đầu tiên đã
được lưu bằng commit local; chưa có remote trong lần kiểm tra ngày 2026-10-13.
Dữ liệu công khai kèm source chỉ là synthetic, không phải log thực hành thật.

## 1. Chức năng đã xây dựng

- Ba VM trong LAN Segment, cấu hình chung và chế độ lightweight.
- Automation PowerShell chỉ đọc/in kế hoạch, Bash trong guest, Ansible cho Kali,
  target và monitor; SSH key, UFW và Docker hạn chế quyền.
- Demo HTTP vô hại, Suricata với 8 rule giáo dục, rsyslog tập trung,
  Alloy/Loki và Grafana dashboard 14 panel.
- CLI status/hosts/network/services/alerts/simulations/report; sáu mô phỏng có
  giới hạn, dry-run không gửi packet; HTML escape và report thật được giữ private.
- Test offline/VM opt-in, CI tĩnh, hướng dẫn investigation và publication audit.

## 2. Cây repository

Xem [cây đầy đủ](repository-tree.md) và
[danh sách chính xác file dự kiến công khai](../PUBLICATION_FILES.txt).
Các thư mục phát triển/runtime private được Git bỏ qua, không nằm trong manifest.

## 3. Kiểm tra đã chạy

Kết quả đo và phạm vi: [validation-results.md](validation-results.md).
Vòng rà soát ngày 2026-10-13: **129 passed, 6 skipped**. Ruff, format, YAML, Markdown, ShellCheck,
PowerShell syntax, Compose config, template parsing và tính tái tạo dashboard
được kiểm tra offline. Gitleaks không tìm thấy leak; scan candidate không còn
finding; pip-audit không tìm thấy advisory đã biết trong snapshot 48 package.
Kiểm tra offline và bằng chứng VM được ghi riêng; test offline không thay thế
validator guest hoặc kiểm tra topology.

## 4. Bằng chứng VM và kiểm tra còn chờ

Ảnh Kali xác nhận baseline/preflight PASS. Ảnh Monitor xác nhận Suricata -T,
Nginx -t, syslog listener và 15 mục validator PASS, gồm marker EVE/central log/Loki.
Dashboard và Explore đã có dữ liệu thực hành. Đây là quan sát trên deployment
hiện có, không phải xác nhận mọi đường xử lý hoặc mọi lần khởi động đều đúng.

Sáu test live pytest vẫn SKIP trong bộ test Windows. Chạy lại toàn bộ Ansible để
đo idempotence, log rotation/retention, reboot sau bản vá IPv4, image digest và
guest package audit chưa được đo. Hosted GitHub Actions chưa chạy. Dùng
[testing.md](testing.md) và [detection-guide.md](detection-guide.md) để kiểm tra
từng mục khi cần; giữ kết quả chưa chạy ở trạng thái chưa xác minh.

## 5. Thiết lập thủ công

1. Tạo Kali và hai Ubuntu theo [installation.md](installation.md); chọn NIC và
   RAM/CPU trong [architecture.md](architecture.md). Đổi mật khẩu image import.
2. Cấu hình LAN Segment cùng tên, kiểm tra peer capture, tắt host sharing.
   Xác minh NIC/IP tĩnh không gateway; cập nhật các bản sao `config/lab.yml`.
3. Tạo key riêng ngoài repo và xác minh SSH fingerprint từ console.
4. Trong cửa sổ NAT cài đặt, chạy Ansible từ Kali; khởi động demo trên target
   và dashboard trên monitor với mật khẩu riêng nhập kín.
5. Ngắt NAT, tắt Shared Folders/clipboard/drag-and-drop trên cả ba VM, kiểm tra
   route, chạy preflight/validator và tạo marker.
6. Review file, staged diff, commit metadata/history và checklist trước khi tự push.

## 6. Phát hiện và giới hạn bảo mật

Đã sửa quyền log Nginx, Grafana root URL từ config, SSH socket activation,
thông báo từ chối route,
cập nhật pin image và cố định action SHA. Pattern scan từng báo cụm từ trong
prompt nhập lại mật khẩu; dòng đó đã được xem trực tiếp, sửa và scan lại.
Không phát hiện credential thật. Xem [audit](../PUBLICATION_AUDIT.md).

HTTP/syslog trong lab vẫn plaintext; threshold giáo dục có thể tạo false positive;
SSH mã hóa phải đối chiếu auth log. Pin tag không thay thế image vulnerability
scan. Source và commit đầu tiên đã được review; chủ project đã chọn giữ tên/email
hiện tại trong commit metadata. Mỗi lần sửa phải review lại staged diff và scan
history sau commit; các mục chưa xác minh vẫn được ghi rõ trong audit.

## 7. Ảnh portfolio nên chụp

- Topology và cấu hình adapter đã che thông tin cá nhân.
- CLI preflight và kết quả validator thật, giữ nguyên các mục FAIL/PENDING.
- URL marker cùng EVE SID và log tập trung có timestamp tương ứng.
- Dashboard đã nhận dữ liệu, investigation timeline và report đã sanitize.

Chỉ thêm ảnh sau review nội dung/metadata theo [screenshots.md](screenshots.md).
Không tạo ảnh dashboard giả hay công khai log, PCAP hoặc report thật chưa review.

## 8. Mô tả GitHub đề xuất

> Isolated VMware Workstation Pro cybersecurity lab with Suricata, centralized logging,
> Grafana dashboards, bounded educational simulations, and a safety-focused Python CLI.

README ghi kết quả đã có bằng chứng cùng giới hạn; không dùng fixture để bổ sung
các kết quả thực hành chưa được đo.

## 9. GitHub topics đề xuất

`cybersecurity`, `homelab`, `vmware`, `suricata`, `network-security`,
`defensive-security`, `devsecops`, `ansible`, `grafana`, `loki`, `python`,
`incident-response`, `educational`.

## 10. Ba nâng cấp v2

1. TLS xác thực hai chiều cho log transport, với certificate/key luôn giữ private.
2. Windows endpoint telemetry từ VM riêng, mở rộng correlation và threat model.
3. Replay traffic tổng hợp đã review trong mạng cô lập, đo precision và detection
   latency từ dữ liệu thực nghiệm; không thêm payload gây hại.
