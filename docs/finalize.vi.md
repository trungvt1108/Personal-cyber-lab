# Chốt source, kiểm thử và lưu phiên bản

Hướng dẫn này dành cho lab đã hoạt động. Windows giữ source chuẩn; Kali là máy
chuyển source tới Target và Monitor. Đồng bộ source không tự triển khai lại
dịch vụ. Runtime, log và mật khẩu hiện tại nằm ngoài ZIP source.

## 1. Kiểm tra bản cuối trên Windows

Mở PowerShell tại thư mục project. Dùng venv Windows hiện có:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m yamllint .
.\.venv\Scripts\python.exe scripts/lint_markdown.py
.\.venv\Scripts\python.exe scripts/check_repository.py --manifest
.\.venv\Scripts\python.exe scripts/publication_audit.py
```

Dừng nếu có lỗi. Sáu test live được skip trên Windows; kết quả này không thay
thế validator chạy trên VM. ShellCheck và kiểm tra cấu hình Compose được mô tả
trong [testing.md](testing.md). Kết quả đã đo nằm trong
[validation-results.md](validation-results.md).

Sau khi cập nhật tài liệu và kiểm tra thành công, xuất source:

```powershell
.\.venv\Scripts\python.exe scripts/export-source.py
Get-FileHash .generated/personal-cyber-lab-source.zip -Algorithm SHA256
```

Giữ hash để đối chiếu trên ba VM. Chỉ dùng ZIP do script này tạo. ZIP không có
venv, runtime, log thật, SSH key, ảnh hoặc báo cáo private.

## 2. Đưa ZIP từ Windows vào Kali

Trong VMware, chọn Kali, vào VM Settings, Options, Shared Folders. Thêm share
`lab-source`, trỏ tới thư mục `.generated` của project Windows; bật share và
chọn Read-only. Đây là một share khác với share bằng chứng nếu đã có.

Trên Kali:

```bash
cp /mnt/hgfs/lab-source/personal-cyber-lab-source.zip /tmp/
sha256sum /tmp/personal-cyber-lab-source.zip
scp -i ~/.ssh/cyberlab_lab /tmp/personal-cyber-lab-source.zip labuser@192.168.56.20:/tmp/
scp -i ~/.ssh/cyberlab_lab /tmp/personal-cyber-lab-source.zip labuser@192.168.56.30:/tmp/
```

Nếu share chưa xuất hiện, kiểm tra lại tên share và trạng thái bật Shared Folders
trong VMware; share bằng chứng đã dùng trước đó có thể giúp đối chiếu mount HGFS.
SCP có thể hỏi passphrase của key lab. Không nhập mật khẩu Grafana vào SSH.

## 3. Cập nhật source trên từng VM

Chạy lần lượt trên Kali, Target và Monitor. Mỗi VM dùng ZIP cùng hash với Windows.
Các lệnh dưới là Bash trong VM:

```bash
cd /opt/personal-cyber-lab
sha256sum /tmp/personal-cyber-lab-source.zip
source_stage=$(mktemp -d /tmp/cyberlab-source.XXXXXX)
python3 -m zipfile -e /tmp/personal-cyber-lab-source.zip "$source_stage"
diff -u config/lab.yml "$source_stage/config/lab.yml"
```

Lệnh diff phải không in khác biệt. Nếu khác, dừng để đối chiếu NIC, IP, port và
mode; không ghi đè cấu hình đang chạy. Ba VM phải dùng cùng config đã rà soát.

Sau khi config trùng, tạo bản sao source hiện tại rồi chép source mới:

```bash
sudo install -d -m 700 local/source-backups
sudo tar -czf "local/source-backups/source-$(date -u +%Y%m%dT%H%M%SZ).tar.gz" \
  --exclude='./local' --exclude='./.git' --exclude='./.venv' \
  --exclude='./.generated' --exclude='./reports/private' .
sudo cp -R "$source_stage/." /opt/personal-cyber-lab/
python3 cyberlab.py validate-config
```

Bản sao nằm trong local, là dữ liệu private. Phép chép chỉ thêm/ghi đè file có
trong ZIP; không xóa dữ liệu khác trong deployment. Không chép venv Windows
vào Linux. Giữ staging cho tới khi kiểm tra xong.

## 4. Kiểm tra deployment hiện có

Trên Target:

```bash
sudo nginx -t
logger -p authpriv.notice -t cyberlab 'CYBERLAB synthetic pipeline marker'
```

Trên Kali:

```bash
cd /opt/personal-cyber-lab
bash scripts/validate-lab.sh --confirm-isolated
python3 cyberlab.py simulate urls --confirm-isolated
```

Trên Monitor, đợi khoảng 30 giây sau marker:

```bash
sudo -u suricata suricata -T -c /etc/suricata/cyberlab.yaml
sudo nginx -t
sudo ss -lntp 'sport = :514'
sudo python3 scripts/monitoring/validate-local.py --confirm-isolated
```

Validator Monitor phải chạy trên Monitor, trong mười phút sau marker. Ghi lại
PASS/FAIL thực tế. Nếu source có thay đổi dịch vụ chưa được áp dụng, dùng quy
trình Ansible trong [vmware.vi.md](vmware.vi.md); source copy không tự render
template hoặc khởi động container. Bản vá capture IPv4 phải có trong cả template
source và `/etc/suricata/cyberlab.yaml` đã triển khai.

## 5. Hoàn thiện tài liệu demo

Dùng [demo.vi.md](demo.vi.md) cho lượt trình diễn. Cập nhật bảng kết quả thực
hành riêng với ảnh/log/hash và ghi các giới hạn. Bản source public chỉ giữ
hướng dẫn, kết quả kiểm thử source và fixture synthetic đã được rà soát.
Không gộp log thật vào ZIP source. Snapshot là lựa chọn sao lưu thêm.

## 6. Lưu Git local trên Windows

Chạy kiểm tra source và tạo manifest lại sau thay đổi tài liệu:

```powershell
.\.venv\Scripts\python.exe scripts/check_repository.py --manifest
.\.venv\Scripts\python.exe scripts/publication_audit.py
git check-ignore reports/private/ local/ .generated/
git config --get user.name
git config --get user.email
```

Nếu chưa có danh tính commit, đặt giá trị do bạn chọn; thay hai placeholder:

```powershell
git config --local user.name "TEN_TAC_GIA"
git config --local user.email "EMAIL_COMMIT"
```

Stage đúng danh sách source đã rà soát:

```powershell
git add --pathspec-from-file=PUBLICATION_FILES.txt
git diff --cached --stat
git diff --cached --name-only
git diff --cached
.\.venv\Scripts\python.exe scripts/publication_audit.py
```

Review nội dung staged. Danh sách không được chứa reports/private, local,
.generated, key hoặc log thật. Sau khi bạn xác nhận bản staged đúng:

```powershell
git commit -m "Complete VMware SOC lab source and documentation"
git status --short
git log -1 --oneline
```

Nếu có Gitleaks, chạy scan history sau commit như hướng dẫn trong
[PUBLICATION_CHECKLIST.md](../PUBLICATION_CHECKLIST.md). Đây là commit local;
GitHub remote, push và quyết định public repo là bước riêng của chủ project.
