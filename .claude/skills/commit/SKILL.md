---
name: commit
description: Tạo commit theo chuẩn Conventional Commits cho dự án iProxy
argument-hint: "[loại commit hoặc mô tả thay đổi]"
---

## Quy tắc commit

Tạo commit theo chuẩn **Conventional Commits** với format:

```
<type>(<scope>): <description>
```

### Type (bắt buộc)

| Type       | Mô tả                                       |
|------------|---------------------------------------------|
| `feat`     | Thêm tính năng mới                          |
| `fix`      | Sửa bug                                     |
| `docs`     | Thay đổi documentation                      |
| `style`    | Format code, không thay đổi logic           |
| `refactor` | Refactor code, không thêm feature hay fix bug|
| `perf`     | Cải thiện performance                        |
| `test`     | Thêm hoặc sửa test                          |
| `build`    | Thay đổi build system hoặc dependencies     |
| `ci`       | Thay đổi CI/CD config                       |
| `chore`    | Các thay đổi khác (không ảnh hưởng src/test)|

### Scope (tuỳ chọn)

Scope theo module của iProxy:
- **Backend**: `auth`, `accounts`, `proxy`, `models`, `db`, `api`, `security`, `config`, `redis`, `migration`, `routing`, `mcp`
- **Frontend**: `ui`, `dashboard`, `monitor`, `stats`, `keys`, `settings`
- **Infra**: `docker`, `ci`, `deps`

### Quy tắc

1. Description viết bằng tiếng Anh, lowercase, không dấu chấm cuối
2. Tối đa 72 ký tự cho dòng đầu
3. Nếu có breaking change, thêm `!` sau type/scope: `feat(api)!: change response format`
4. Body (tuỳ chọn) giải thích chi tiết bằng tiếng Việt hoặc Anh

## Quy trình

### Bước 1: Kiểm tra staged changes

- Chạy `git diff --staged --name-status` để xem đã có gì staged chưa
- Nếu ĐÃ có staged → đi tiếp bước 2
- Nếu CHƯA có staged → hỏi user muốn stage gì

### Bước 2: Chạy lint/format theo loại file staged

Kiểm tra file staged thuộc backend hay frontend (hoặc cả hai):

**Nếu có file Python (`backend/`):**
- Chạy `cd backend && source venv/bin/activate`
- Nếu activate thất bại → báo cho user và KHÔNG commit
- Chạy `ruff check .` để kiểm tra lint
- Chạy `ruff format .` để format code
- Nếu có lỗi lint → báo cho user và KHÔNG commit cho đến khi fix xong
- Re-stage các file đã được format: `git add <các file .py đã staged>`

**Nếu có file TypeScript/JavaScript (`admin/`):**
- Chạy `cd admin && npm run lint` để kiểm tra
- Nếu có lỗi → báo cho user và KHÔNG commit cho đến khi fix xong

### Bước 3: Phân tích thay đổi

- Phân loại files trong staged theo type: code (.py, .ts, .tsx), docs (.md), config, migration, etc.
- Nếu có NHIỀU loại file khác nhau → gộp thành 1 commit với type phổ quát nhất
  - Ưu tiên: `feat` > `fix` > `refactor` > `chore` > `docs`
- Nếu chỉ có 1 loại → dùng type phù hợp

### Bước 4: Tạo commit message

- Xác định type dựa trên nội dung thay đổi
- Xác định scope dựa trên thư mục/module bị ảnh hưởng
- Nếu user truyền `$ARGUMENTS`, dùng làm gợi ý cho description
- Tạo message theo Conventional Commits format

### Bước 5: Commit

- Hiển thị commit message cho user xác nhận
- Chạy `git commit -m "<message>"`
