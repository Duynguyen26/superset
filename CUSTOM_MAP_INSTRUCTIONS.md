# Hướng dẫn thêm bản đồ tùy chỉnh (Custom Map) vào Apache Superset

Tài liệu này hướng dẫn cách thêm một bản đồ tùy chỉnh (ví dụ: Bản đồ Việt Nam sau sáp nhập, hoặc bản đồ cấp Quận/Huyện) vào biểu đồ **Country Map** mặc định của Superset.

---

## 📌 Tổng quan các bản đồ đã tích hợp cho Việt Nam

Hệ thống đã tích hợp 3 loại bản đồ chất lượng cao (đầy đủ các đảo **Hoàng Sa, Trường Sa, Côn Đảo, Phú Quốc...**):
1. **Vietnam (Trước sáp nhập)** (`vietnam_pre.geojson`): Bản đồ 63 Tỉnh/Thành gốc.
2. **Vietnam (Sau sáp nhập)** (`vietnam_post.geojson`): Bản đồ 34 Tỉnh/Thành sau khi gộp theo quy tắc trong file `province_merge.csv`.
3. **Vietnam (Cấp Quận/Huyện)** (`vietnam_districts.geojson`): Bản đồ hơn 700 Quận/Huyện toàn quốc (tên Tỉnh cha trong ngoặc đơn tự động đổi theo quy tắc sáp nhập).

*Lưu ý:* Hai bản đồ cấp Tỉnh (Pre và Post) được tạo ra bằng cách gộp (dissolve) cơ sở dữ liệu địa lý chi tiết của bản đồ cấp Quận/Huyện. Điều này đảm bảo bản đồ cấp tỉnh giữ lại được đầy đủ tọa độ của tất cả các hòn đảo xa bờ (điều mà file gốc thô sơ của Superset không làm được).

---

## Bước 1: Chuẩn bị file bản đồ (GeoJSON)

1. Chuẩn bị file dữ liệu bản đồ định dạng `.geojson` (ví dụ: `vietnam_post.geojson` hoặc `vietnam_districts.geojson`).
2. Đảm bảo thuộc tính `ISO` (mã vùng dạng `VN-XXX`) hoặc `NAME_1` (tên vùng) bên trong file GeoJSON trùng khớp với dữ liệu bạn sẽ dùng để query.
3. Copy file GeoJSON này vào thư mục chứa dữ liệu bản đồ của Superset:
   `superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries/`

---

## Bước 2: Khai báo bản đồ vào Source Code

Mở file `superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries.ts` và thực hiện 3 thay đổi:

**1. Import file GeoJSON mới (thêm vào phần đầu file cùng với các import khác):**
```typescript
import vietnam_pre from './countries/vietnam_pre.geojson';
import vietnam_post from './countries/vietnam_post.geojson';
import vietnam_districts from './countries/vietnam_districts.geojson';
```

**2. Đăng ký biến vừa import vào object `countries`:**
```typescript
export const countries = {
  // ... (danh sách các nước đang có sẵn)
  vietnam_pre,
  vietnam_post, 
  vietnam_districts,
};
```

**3. Đặt tên hiển thị cho Menu thả xuống (Dropdown):**
Tìm đến đoạn khai báo `export const countryOptions = ...` và thêm logic trả về tên hiển thị của bạn:
```typescript
  if (x === 'vietnam_pre') {
    return [x, 'Vietnam (Trước sáp nhập)'];
  }
  if (x === 'vietnam_post') {
    return [x, 'Vietnam (Sau sáp nhập)'];
  }
  if (x === 'vietnam_districts') {
    return [x, 'Vietnam (Cấp Quận/Huyện)'];
  }
```

---

## Bước 3: Build lại giao diện (Frontend)

Vì file GeoJSON và danh sách Menu được nhúng trực tiếp vào mã nguồn Frontend, bạn bắt buộc phải build lại hệ thống để nhận diện bản đồ mới.

- **Đối với môi trường Development (Docker Compose):** 
  Chạy lệnh khởi động lại Node container:
  ```bash
  docker compose restart superset-node
  ```
  *Lưu ý: Bạn có thể cần xóa Cache trình duyệt (Empty Cache and Hard Reload) nếu biểu đồ vẫn hiển thị bản đồ cũ.*

- **Đối với môi trường Production (Non-Dev):** 
  Đi tới thư mục `superset-frontend` và chạy lệnh build lại:
  ```bash
  cd superset-frontend && npm run build
  ```

---

## Bước 4: Cách sử dụng trên giao diện Superset

Dù tên biểu đồ là "Country Map" (Bản đồ quốc gia), bạn hoàn toàn có thể dùng nó để vẽ bản đồ cấp nhỏ hơn (Quận/Huyện/Xã) miễn là đã khai báo GeoJSON thành công ở các bước trên.

1. Tạo một biểu đồ mới, chọn loại chart là **Country Map**.
2. Chọn Dataset chứa dữ liệu (Lưu ý data phải có 1 cột trùng khớp với trường `ISO` trong file GeoJSON, ví dụ: mã Quận/Huyện hoặc tên Quận/Huyện).
3. Ở ô thiết lập **Country**, bấm vào menu xổ xuống và tìm chọn tên bản đồ bạn vừa đặt (Ví dụ: `Vietnam (Cấp Quận/Huyện)` hoặc `Vietnam (Sau sáp nhập)`).
4. Kéo cột chứa mã khu vực vào ô **ISO 3166-2 Codes**.
5. Kéo cột dữ liệu muốn thể hiện màu sắc (ví dụ: Doanh thu) vào ô **Metric** (chọn `SUM`).
6. Bấm nút **Update chart** để xem kết quả.

---

## 🛠️ Quy trình cập nhật lại bản đồ khi thay đổi quy tắc sáp nhập

Nếu sau này bạn thay đổi quy tắc sáp nhập tỉnh trong file `province_merge.csv`, bạn cần chạy lại script Python để tự động vẽ lại biên giới bản đồ cấp Tỉnh và cập nhật tên Quận/Huyện tương ứng:

1. Chỉnh sửa file `province_merge.csv` theo quy tắc mới.
2. Đảm bảo file gốc cấp Huyện đầy đủ đảo vẫn nằm tại `/tmp/vn_districts.geojson`.
3. Chạy script sau trong môi trường ảo của bạn:

```bash
source venv/bin/activate
python3 -c "
import geopandas as gpd
import pandas as pd
import json

# 1. Đọc dữ liệu gốc
gdf_dist = gpd.read_file('/tmp/vn_districts.geojson')
df_merge = pd.read_csv('province_merge.csv')

df_merge['province_old'] = df_merge['province_old'].str.strip()
df_merge['province_new_prefix'] = df_merge['province_new_prefix'].str.strip()
df_merge['province_code_new'] = df_merge['province_code_new'].str.strip()
df_merge['province_old_prefix'] = df_merge['province_old_prefix'].str.strip()
df_merge['province_code_old'] = df_merge['province_code_old'].str.strip()

merge_map = dict(zip(df_merge['province_old'], zip(df_merge['province_new_prefix'], df_merge['province_code_new'])))
old_name_map = dict(zip(df_merge['province_old'], zip(df_merge['province_old_prefix'], df_merge['province_code_old'])))

# 2. Cập nhật bản đồ Quận/Huyện theo tỉnh cha mới
mock_data = []
with open('/tmp/vn_districts.geojson') as f:
    dist_data = json.load(f)

for feature in dist_data['features']:
    props = feature['properties']
    dist_code = 'VN-D' + str(props.get('Ma', ''))
    old_prov = props.get('Tinh_Thanh', '').strip()
    new_prov = merge_map.get(old_prov, (old_prov.replace('Tỉnh ', '').replace('Thành phố ', ''), ''))[0]
    name = f\"{props.get('Ten', '')} ({new_prov})\"
    feature['properties'] = {'ISO': dist_code, 'NAME_1': name}
    mock_data.append({'ISO': dist_code, 'District': name, 'Sales': 100})

with open('superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries/vietnam_districts.geojson', 'w') as f:
    json.dump(dist_data, f, ensure_ascii=False)
pd.DataFrame(mock_data).to_csv('mock_data_districts.csv', index=False)

# 3. Tạo bản đồ 63 tỉnh gốc (Pre)
gdf_dist['name_pre'] = gdf_dist['Tinh_Thanh'].map(lambda x: old_name_map.get(x.strip(), (x, ''))[0])
gdf_dist['code_pre'] = gdf_dist['Tinh_Thanh'].map(lambda x: 'VN-' + old_name_map.get(x.strip(), ('', x))[1])
gdf_pre = gdf_dist.dissolve(by='name_pre', as_index=False)
gdf_pre['ISO'] = gdf_pre['code_pre']
gdf_pre['NAME_1'] = gdf_pre['name_pre']
gdf_pre[['ISO', 'NAME_1', 'geometry']].to_file('superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries/vietnam_pre.geojson', driver='GeoJSON')

# 4. Tạo bản đồ sáp nhập (Post)
gdf_dist['name_post'] = gdf_dist['Tinh_Thanh'].map(lambda x: merge_map.get(x.strip(), (x, ''))[0])
gdf_dist['code_post'] = gdf_dist['Tinh_Thanh'].map(lambda x: 'VN-' + merge_map.get(x.strip(), ('', x))[1])
gdf_post = gdf_dist.dissolve(by='name_post', as_index=False)
gdf_post['ISO'] = gdf_post['code_post']
gdf_post['NAME_1'] = gdf_post['name_post']
gdf_post[['ISO', 'NAME_1', 'geometry']].to_file('superset-frontend/plugins/legacy-plugin-chart-country-map/src/countries/vietnam_post.geojson', driver='GeoJSON')

print('Regeneration complete!')
"
```

4. Chạy build/restart lại Container theo **Bước 3** để áp dụng thay đổi.

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
