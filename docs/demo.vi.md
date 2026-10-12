# Kịch bản demo Personal Cyber Lab

## Chuẩn bị

- Ba VM cùng LAN Segment; NAT ngắt trước thực hành.
- Shared Folders, clipboard và drag-and-drop tắt trên cả ba VM. Chuyển tài liệu
  vào VM trước lượt demo; mở lại share sau khi kết thúc nếu cần lấy bằng chứng.
- Kali truy cập Target và Monitor bằng IP trong config.
- Mở terminal từng VM và Grafana trên Kali.
- Đối chiếu giờ UTC bằng `date -u` trên ba VM trước khi chọn cửa sổ điều tra.
- Sensor hiện giám sát IPv4, loại IPv4 multicast; chưa giám sát IPv6/multicast.

## Trình diễn khoảng 10 phút

| Phần | Thao tác | Bằng chứng cần thấy |
| --- | --- | --- |
| Kiến trúc | Giải thích Kali, Target, Monitor và log pipeline | Sơ đồ trong docs/architecture.md |
| Trạng thái | Kali chạy validate-lab.sh | Mạng, SSH, HTTP, Grafana PASS |
| Marker | Target logger; Kali simulate urls | HTTP 200, SIDs 1000004–6, auth marker |
| Giám sát | Monitor chạy validate-local.py | Toàn bộ kiểm tra PASS trong cửa sổ mới |
| Điều tra | Grafana Explore theo SID hoặc marker | Nguồn, đích, UTC, nội dung sự kiện |
| Báo cáo | Mở báo cáo private tại máy trình diễn | Timeline, hash, kết luận và giới hạn |

Lệnh marker/validator nằm trong [detection-guide.md](detection-guide.md). Các
thông tin đăng nhập Grafana lấy từ cấu hình local; không đưa mật khẩu lên slide.

## Hai bài bổ sung

Chạy trên Kali sau preflight:

```bash
python3 cyberlab.py simulate discover --dry-run
python3 cyberlab.py simulate discover --confirm-isolated
python3 cyberlab.py simulate http --dry-run --count 8
python3 cyberlab.py simulate http --confirm-isolated --count 8
```

Trên Grafana Explore, chọn cùng cửa sổ thời gian với lượt chạy:

```logql
{job="suricata",event_type="alert"} | json | alert_signature_id="1000002"
{job="suricata",event_type="alert"} | json | alert_signature_id="1000007"
```

Giải thích SID 1000002 đếm SYN theo nguồn, không đếm cổng khác nhau; kết nối HTTP
lặp có thể kích hoạt rule này. SID 1000007 đếm GET theo nguồn, vượt năm lần khớp
trong mười giây thì cảnh báo. Số cảnh báo cần đo thực tế vì lưu lượng trước đó
trong cửa sổ có thể ảnh hưởng bộ đếm.

## Kết luận trình bày

Nêu bài nào đã có bằng chứng, giới hạn nào chưa kiểm chứng và cách xử lý lỗi đã
gặp. HTTP 200 chỉ xác nhận phản hồi ứng dụng. Cảnh báo SSH mạng không chứng minh
kết quả xác thực; dùng auth log. Signature severity không tự quyết định mức độ
incident. Capture filter giới hạn phạm vi quan sát; counters không chứng minh
đã nhận đủ mọi log. Giữ ảnh/log thật trong hồ sơ private.
