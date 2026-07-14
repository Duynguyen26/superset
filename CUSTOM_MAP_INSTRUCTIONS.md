# Hướng dẫn thêm bản đồ tùy chỉnh (Custom Map) vào Apache Superset

Tài liệu này hướng dẫn cách thêm một bản đồ tùy chỉnh (ví dụ: Bản đồ Việt Nam sau sáp nhập) vào biểu đồ **Country Map** mặc định của Superset.

## Bước 1: Chuẩn bị file bản đồ (GeoJSON)

1. Chuẩn bị file dữ liệu bản đồ định dạng `.geojson` (ví dụ: `vietnam_post.geojson`).
2. Đảm bảo thuộc tính `ISO` hoặc `NAME_1` bên trong file GeoJSON trùng khớp với dữ liệu bạn sẽ query.
3. Copy file GeoJSON này vào thư mục chứa dữ liệu bản đồ của Superset:
   `superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries/`

## Bước 2: Khai báo bản đồ vào Source Code

Mở file `superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries.ts` và thực hiện 3 thay đổi:

**1. Import file GeoJSON mới (thêm vào phần đầu file cùng với các import khác):**
```typescript
import vietnam_post from './countries/vietnam_post.geojson';
```

**2. Đăng ký biến vừa import vào object `countries`:**
```typescript
export const countries = {
  // ... (danh sách các nước đang có sẵn)
  vietnam_post, 
};
```

**3. Đặt tên hiển thị cho Menu thả xuống (Dropdown):**
Tìm đến đoạn khai báo `export const countryOptions = ...` và thêm logic trả về tên bản đồ của bạn:
```typescript
  if (x === 'vietnam_post') {
    return [x, 'Vietnam (Sau sáp nhập)'];
  }
```

## Bước 3: Build lại giao diện (Frontend)

Vì file GeoJSON và danh sách Menu được nhúng trực tiếp vào mã nguồn Frontend, bạn bắt buộc phải build lại hệ thống để nhận diện bản đồ mới.

- **Đối với môi trường Development (Docker Compose):** 
  Chạy lệnh khởi động lại Node container:
  ```bash
  docker compose restart superset-node
  ```
  *Lưu ý: Bạn có thể cần xóa Cache trình duyệt (Empty Cache and Hard Reload) nếu biểu đồ vẫn hiển thị bản đồ cũ.*

- **Đối với môi trường Production:** 
  Đi tới thư mục `superset-frontend` và chạy lệnh build:
  ```bash
  npm run build
  ```

Sau khi hoàn tất, bạn có thể tạo một biểu đồ **Country Map** mới và chọn bản đồ tùy chỉnh của mình từ danh sách thả xuống.
