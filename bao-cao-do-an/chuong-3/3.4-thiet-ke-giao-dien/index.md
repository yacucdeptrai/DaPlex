# 3.4. Thiết Kế Giao Diện

Mục này trình bày thiết kế giao diện của DaPlex — từ kiến trúc frontend Angular PWA, hệ thống routing và layout, đến chi tiết từng màn hình người dùng và màn hình quản trị. Phần này quan trọng vì giao diện là điểm tiếp xúc trực tiếp giữa hệ thống và người dùng, đồng thời phản ánh các quyết định kỹ thuật về state management, lazy loading, và xác thực. Nội dung được chia thành tổng quan kiến trúc frontend, bảng route toàn bộ, và hai mục chi tiết cho giao diện người dùng và giao diện admin.

---

## Tổng Quan Kiến Trúc Frontend

Frontend của DaPlex được xây dựng trên **Angular 21 PWA** — framework SPA (Single Page Application) với hỗ trợ Progressive Web App qua `ServiceWorkerModule`. Toàn bộ ứng dụng là một bundle duy nhất được serve tĩnh, giao tiếp với DaPlex-API hoàn toàn qua REST HTTP và WebSocket; không có server-side rendering. Quyết định dùng Angular thay vì React hay Vue xuất phát từ nhu cầu có một framework đủ opinionated để quản lý state phức tạp của giao diện quản trị mà không cần dựng thêm state management library bên ngoài — Angular's DI system và `@ngrx` nếu cần đều là lựa chọn tự nhiên trong ecosystem.

`AppModule` là root module, bootstrap `AppComponent`. Hai thư viện UI chính được tích hợp: **PrimeNG** (component library đầy đủ: bảng dữ liệu, dialog, menu, toast notification) và **Angular CDK** (`FullscreenOverlayContainer` để overlay hoạt động đúng trong chế độ fullscreen của trình phát). **Transloco** xử lý đa ngôn ngữ — toàn bộ chuỗi văn bản trong UI được quản lý qua file ngôn ngữ, không hardcode trực tiếp trong template. **@ngneat/cashew** là HTTP cache layer: inject `withHttpCacheInterceptor()` vào `HttpClient` chain để cache response API có TTL cấu hình qua `HTTP_CACHE_TTL`, giảm số lần gọi API cho các resource ít thay đổi (genre list, production list, settings).

Hai `HTTP_INTERCEPTORS` được đăng ký toàn cục: `BaseUrlInterceptor` tự động prefix URL tương đối với base URL của API server (lấy từ environment config), và `HttpErrorInterceptor` xử lý centralized error — đặc biệt là 401 Unauthorized sẽ trigger refresh token flow. `GlobalErrorHandler` thay thế ErrorHandler mặc định của Angular để bắt unhandled error và hiển thị toast thay vì để lỗi im lặng.

---

## Hai Layout Chính

Ứng dụng tổ chức theo hai layout riêng biệt phản ánh hai vai trò người dùng khác nhau.

**`HomeLayoutComponent`** là layout cho người dùng cuối, bao gồm navbar trên cùng, nội dung chính, và footer. Tất cả route xem nội dung đều mount vào layout này: trang chủ, tìm kiếm, danh sách, trang chi tiết, trang xem phim, và trang cá nhân. Layout này không yêu cầu đăng nhập để xem (authentication là tùy chọn cho hầu hết route).

**`AdminLayoutComponent`** là layout dành riêng cho route `/admin/`. Layout này có sidebar navigation và header khác với HomeLayout. Toàn bộ admin route đều đi qua `AuthGuard` và `WsActivatorGuard` ở cấp layout — `AuthGuard` kiểm tra user đã đăng nhập và có permission `MANAGE_MEDIA` hoặc `ADMINISTRATOR`; `WsActivatorGuard` khởi tạo kết nối WebSocket (`WsAdminGateway`) khi enter và đóng khi leave, đảm bảo WebSocket chỉ active khi admin đang ở trong khu vực quản trị.

---

## Cấu Trúc Route Toàn Bộ

| Route | Component | Layout | Ghi Chú |
|---|---|---|---|
| `/` | `HomeComponent` | Home | Trang chủ — featured, trending, recent |
| `/search` | `SearchComponent` | Home | Tìm kiếm real-time |
| `/list/:path` | `ListComponent` | Home | Danh sách theo filter |
| `/list/:path/:sub_path` | `ListComponent` | Home | Danh sách lồng nhau |
| `/details/:id` | `DetailsComponent` | Home | Trang chi tiết nội dung |
| `/playlists/:id` | `PlaylistsComponent` | Home | Xem playlist |
| `/watch/:id` | `WatchComponent` | Home | Trình phát video |
| `/sign-in` | `SignInComponent` | Home | Đăng nhập |
| `/sign-up` | `SignUpComponent` | Home | Đăng ký |
| `/confirm-email` | `ConfirmEmailComponent` | Home | Xác thực email |
| `/forgot-password` | `ForgotPasswordComponent` | Home | Quên mật khẩu |
| `/reset-password` | `ResetPasswordComponent` | Home | Đặt lại mật khẩu |
| `/users/:id` | `ProfileComponent` | Home | Trang cá nhân |
| `/users/:id/history` | `HistoryComponent` | Home | Lịch sử xem |
| `/users/:id/playlists` | `PlaylistsComponent` | Home | Playlist của user |
| `/users/:id/rated` | `RatedComponent` | Home | Danh sách đã đánh giá |
| `/users/settings` | `AccountSettingsComponent` | Settings | Cài đặt tài khoản |
| `/users/settings/profile` | `ProfileSettingsComponent` | Settings | Cài đặt hồ sơ |
| `/users/settings/privacy` | `PrivacySettingsComponent` | Settings | Cài đặt quyền riêng tư |
| `/users/settings/media` | `MediaSettingsComponent` | Settings | Cài đặt chất lượng phát |
| `/users/settings/subtitle` | `SubtitleSettingsComponent` | Settings | Cài đặt phụ đề |
| `/admin/media` | `MediaComponent` (Admin) | Admin | Quản lý nội dung video |
| `/admin/genres` | `GenresComponent` | Admin | Quản lý thể loại |
| `/admin/productions` | `ProductionsComponent` | Admin | Quản lý hãng sản xuất |
| `/admin/audit-log` | `AuditLogComponent` | Admin | Lịch sử hành động (ADMINISTRATOR only) |

*Bảng 3.6: Toàn bộ route của daplex-dune-v2 và component tương ứng*

---

## Các Quyết Định Kỹ Thuật Frontend

**Lazy loading và `CustomRouteReuseStrategy`.** Tất cả feature module đều được lazy-load (`loadChildren: () => import(...)`), nghĩa là bundle JavaScript của `AdminModule` chỉ được tải khi user điều hướng vào `/admin/` lần đầu. `CustomRouteReuseStrategy` cấu hình route reuse: khi user navigate từ `details/:id` về `search` hay `list/:path`, Angular không destroy và re-create `SearchComponent` mà giữ lại component instance đã render — scroll position và filter state được bảo tồn, tránh phải gọi lại API để load lại danh sách.

**PWA Service Worker.** `ServiceWorkerModule` được register với strategy `registerWhenStable:30000` (chờ 30 giây sau khi app ổn định trước khi register) để không ảnh hưởng đến thời gian load ban đầu. Service worker cache static asset (JS, CSS, images) cho phép ứng dụng hoạt động offline hoặc với mạng yếu sau lần tải đầu tiên.

**`APP_INITIALIZER`: Khôi Phục Auth Session.** `AppInitializer` factory được gọi trước khi Angular render bất kỳ component nào. Nó gọi `AuthService.loadUser()` để kiểm tra refresh token trong cookie và khôi phục session đăng nhập — đảm bảo user không bị đăng xuất khi F5 trang, và các route được bảo vệ bởi `AuthGuard` nhận được thông tin user chính xác ngay từ navigation đầu tiên.

---

## Cấu Trúc Các Mục Tiếp Theo

Hai mục tiếp theo đi vào chi tiết từng màn hình:

- [**3.4.1 — Giao Diện Người Dùng**](3.4.1-giao-dien-nguoi-dung.md): Mô tả và wireframe các màn hình phục vụ người xem — trang chủ, tìm kiếm, danh sách, trang chi tiết nội dung, trình phát video, trang cá nhân, và cài đặt.
- [**3.4.2 — Giao Diện Admin**](3.4.2-giao-dien-admin.md): Mô tả và wireframe màn hình quản trị — quản lý media (upload, encode, publish), quản lý taxonomy (genre, production), và audit log.
