# Hướng dẫn thêm bản đồ tùy chỉnh (Custom Map) vào Apache Superset

Tài liệu này hướng dẫn cách thêm một bản đồ tùy chỉnh (ví dụ: Bản đồ Việt Nam sau sáp nhập, hoặc bản đồ cấp Quận/Huyện) vào biểu đồ **Country Map** mặc định của Superset.

## Bước 1: Chuẩn bị file bản đồ (GeoJSON)

1. Chuẩn bị file dữ liệu bản đồ định dạng `.geojson` (ví dụ: `vietnam_post.geojson` hoặc `vietnam_districts.geojson`).
2. Đảm bảo thuộc tính `ISO` hoặc `NAME_1` bên trong file GeoJSON trùng khớp với dữ liệu mã hoặc tên bạn sẽ dùng để query.
3. Copy file GeoJSON này vào thư mục chứa dữ liệu bản đồ của Superset:
   `superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries/`

## Bước 2: Khai báo bản đồ vào Source Code

Mở file `superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries.ts` và thực hiện 3 thay đổi:

**1. Import file GeoJSON mới (thêm vào phần đầu file cùng với các import khác):**
```typescript
import vietnam_post from './countries/vietnam_post.geojson';
import vietnam_districts from './countries/vietnam_districts.geojson';
```

**2. Đăng ký biến vừa import vào object `countries`:**
```typescript
export const countries = {
  // ... (danh sách các nước đang có sẵn)
  vietnam_post, 
  vietnam_districts,
};
```

**3. Đặt tên hiển thị cho Menu thả xuống (Dropdown):**
Tìm đến đoạn khai báo `export const countryOptions = ...` và thêm logic trả về tên bản đồ của bạn:
```typescript
  if (x === 'vietnam_post') {
    return [x, 'Vietnam (Sau sáp nhập)'];
  }
  if (x === 'vietnam_districts') {
    return [x, 'Vietnam (Cấp Quận/Huyện)'];
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

## Bước 4: Cách sử dụng trên giao diện Superset

Dù tên biểu đồ là "Country Map" (Bản đồ quốc gia), bạn hoàn toàn có thể dùng nó để vẽ bản đồ cấp nhỏ hơn (Quận/Huyện/Xã) miễn là đã khai báo GeoJSON thành công ở các bước trên.

1. Tạo một biểu đồ mới, chọn loại chart là **Country Map**.
2. Chọn Dataset chứa dữ liệu (Lưu ý data phải có 1 cột trùng khớp với trường `ISO` trong file GeoJSON, ví dụ: mã Quận/Huyện hoặc tên Quận/Huyện).
3. Ở ô thiết lập **Country**, bấm vào menu xổ xuống và tìm chọn tên bản đồ bạn vừa đặt (Ví dụ: `Vietnam (Cấp Quận/Huyện)` hoặc `Vietnam (Sau sáp nhập)`).
4. Kéo cột chứa mã khu vực vào ô **ISO 3166-2 Codes**.
5. Kéo cột dữ liệu muốn thể hiện màu sắc (ví dụ: Doanh thu) vào ô **Metric** (chọn `SUM`).
6. Bấm nút **Update chart** để xem kết quả.

---

## Phụ lục: Kích hoạt CSS bên trong biểu đồ Handlebars (Tùy chọn)

Mặc định, Superset khóa tính năng hiển thị `<style>` CSS bên trong **Handlebars Chart** (HTML_SANITIZATION = True) để chống tấn công XSS. 
Nếu bạn viết CSS trong ô `styleTemplate` của biểu đồ Handlebars mà không thấy tác dụng, bạn có thể thiết lập mở khóa cho thẻ này:

**Cách kích hoạt:**
1. Mở file cấu hình của Superset (Ví dụ: `docker/pythonpath_dev/superset_config.py`).
2. Thêm hoặc cập nhật dòng sau vào file:
```python
# Cho phép thẻ <style> chạy qua bộ lọc bảo mật để CSS của Handlebars hoạt động
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    "tagNames": ["style"]
}
```
3. Khởi động lại Superset.

**Lưu ý cực kỳ quan trọng:** Khi viết CSS trực tiếp vào Handlebars Chart, CSS đó sẽ ảnh hưởng đến **toàn bộ Dashboard**. Bạn BẮT BUỘC phải bọc CSS vào một `#ID` cụ thể để nó chỉ áp dụng riêng cho biểu đồ đó. Ví dụ:
```css
#bieu-do-cua-toi h1 {
    color: red;
}
```
