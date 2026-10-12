# Bàn giao Personal Cyber Lab

Mã nguồn, template và tài liệu đã được rà soát và chuyển sang VMware Workstation Pro.
Khả năng bắt gói và pipeline trên các VM của bạn vẫn cần kiểm chứng bằng marker mới.
Xem [hướng dẫn cập nhật và test VMware](vmware.vi.md).
Trạng thái công khai: **NOT READY** cho tới khi chủ repository hoàn tất các mục
review trong [publication audit](../PUBLICATION_AUDIT.md). Chưa stage, commit hay
push. Dữ liệu đính kèm chỉ là synthetic, không phải bằng chứng detection thực tế.

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
Vòng rà soát VMware ngày 2026-10-10: **129 passed, 6 skipped**. Ruff, format, YAML, Markdown, ShellCheck,
PowerShell syntax, Compose config, template parsing và tính tái tạo dashboard
được kiểm tra offline. Gitleaks không tìm thấy leak; scan candidate không còn
finding; pip-audit không tìm thấy advisory đã biết trong snapshot 48 package.
Các kiểm tra này không chứng minh topology hay pipeline VM đang hoạt động.

## 4. Kiểm tra cần VM

**SKIPPED - requires running cyber lab.**

Kiểm tra reachability/services, thực thi/idempotence Ansible, các lệnh kiểm tra
cấu hình service, Suricata packet/rule, auth/HTTP log forwarding, container
readiness và marker → EVE → Loki → dashboard. Dùng
[testing.md](testing.md) và [detection-guide.md](detection-guide.md).
Hosted GitHub Actions chưa chạy; image digest và guest package audit còn chờ.

## 5. Thiết lập thủ công

1. Tạo Kali và hai Ubuntu theo [installation.md](installation.md); chọn NIC và
   RAM/CPU trong [architecture.md](architecture.md). Đổi mật khẩu image import.
2. Cấu hình LAN Segment cùng tên, kiểm tra peer capture, tắt host sharing.
   Xác minh NIC/IP tĩnh không gateway; cập nhật các bản sao `config/lab.yml`.
3. Tạo key riêng ngoài repo và xác minh SSH fingerprint từ console.
4. Trong cửa sổ NAT cài đặt, chạy Ansible từ Kali; khởi động demo trên target
   và dashboard trên monitor với mật khẩu riêng nhập kín.
5. Ngắt NAT trên cả ba VM, kiểm tra route, chạy preflight/validator và tạo marker.
6. Review file, staged diff, commit metadata/history và checklist trước khi tự push.

## 6. Phát hiện và giới hạn bảo mật

Đã sửa quyền log Nginx, Grafana root URL từ config, SSH socket activation,
thông báo từ chối route,
cập nhật pin image và cố định action SHA. Pattern scan từng báo cụm từ trong
prompt nhập lại mật khẩu; dòng đó đã được xem trực tiếp, sửa và scan lại.
Không phát hiện credential thật. Xem [audit](../PUBLICATION_AUDIT.md).

HTTP/syslog trong lab vẫn plaintext; threshold giáo dục có thể tạo false positive;
SSH mã hóa phải đối chiếu auth log. Pin tag không thay thế image vulnerability
scan. Chưa review staged snapshot/commit vì chưa stage/commit; các mục chưa xác
minh được ghi **REQUIRES MANUAL REVIEW**, không được tự coi là an toàn.

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

Trước khi có bằng chứng live, giữ tuyên bố triển khai/validation pending trong README.

## 9. GitHub topics đề xuất

`cybersecurity`, `homelab`, `vmware`, `suricata`, `network-security`,
`defensive-security`, `devsecops`, `ansible`, `grafana`, `loki`, `python`,
`incident-response`, `educational`.

## 10. Ba nâng cấp v2

1. TLS xác thực hai chiều cho log transport, với certificate/key luôn giữ private.
2. Windows endpoint telemetry từ VM riêng, mở rộng correlation và threat model.
3. Replay traffic tổng hợp đã review trong mạng cô lập, đo precision và detection
   latency từ dữ liệu thực nghiệm; không thêm payload gây hại.
