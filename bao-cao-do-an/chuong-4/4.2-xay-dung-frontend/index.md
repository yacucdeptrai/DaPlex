# 4.2. Xây Dựng Frontend

Phần này trình bày quá trình xây dựng frontend của hệ thống DaPlex bằng Angular 21, bao gồm kiến trúc module phân tầng, các thành phần singleton và tái sử dụng, cơ chế quản lý state, và tích hợp Progressive Web App. Frontend được thiết kế theo mô hình NgModule truyền thống với lazy-loaded feature modules nhằm tối ưu kích thước bundle và hiệu năng tải trang. Phần này gồm ba mục chi tiết: cấu trúc dự án Angular, module và routing, và trình phát video.

---

## Tổng Quan

Frontend của DaPlex được xây dựng bằng Angular 21.2.8 — phiên bản mới nhất của framework tại thời điểm phát triển — chạy trên TypeScript 5.9.3 và được đóng gói với esbuild thay cho Webpack truyền thống. Ứng dụng hoạt động như một Progressive Web App (PWA) với khả năng cache tài nguyên tĩnh qua Angular Service Worker, cho phép trải nghiệm tải nhanh hơn ở lần truy cập tiếp theo và hỗ trợ một phần chức năng offline. Toàn bộ giao tiếp với backend được thực hiện qua HTTP REST API và WebSocket, với URL gốc được cấu hình tĩnh trong `src/environments/environment.ts` và bake vào bundle tại thời điểm build.

> Một quyết định kiến trúc quan trọng là duy trì mô hình **NgModule truyền thống** (AppModule-based) thay vì chuyển sang kiến trúc Standalone Component mà Angular 17+ đề xuất. Lý do chính là tại thời điểm khởi động dự án, hệ sinh thái thư viện bên thứ ba (PrimeNG, Vidstack, Transloco) vẫn phân phối module-based API ổn định hơn so với standalone API; hơn nữa, cấu trúc lazy-loaded feature module cho phép code-splitting tự nhiên và dễ quản lý phạm vi provider giữa các tính năng độc lập. Mỗi trong năm feature module (home, auth, media, admin, users) tải riêng biệt theo route, giúp giảm kích thước bundle khởi đầu và cải thiện thời gian tải trang đầu tiên (First Contentful Paint).

Kiến trúc tổng thể của frontend DaPlex tuân theo mô hình phân tầng rõ ràng: tầng **core** chứa singleton services, interceptors, guards, strategies, và initializers chỉ được khởi tạo một lần trong vòng đời ứng dụng; tầng **shared** chứa các component, directive, pipe, và module tái sử dụng được import bởi nhiều feature module; và tầng **feature modules** chứa logic nghiệp vụ đặc thù của từng chức năng. Sự phân tách này đảm bảo không có circular dependency giữa các tầng — feature module có thể import từ shared và core, nhưng core và shared không được phép import từ feature module.

<!-- FIGURE
  id: Hình 4.2
  title: Kiến trúc module Angular của daplex-dune-v2 — phân tầng core, shared, và feature modules
  type: architecture-diagram
  description: >
    Sơ đồ kiến trúc module Angular của ứng dụng daplex-dune-v2. Trên cùng là AppModule (root) chứa AppRoutingModule, TranslocoRootModule, ServiceWorker. Tầng giữa chia làm hai nhóm song song: nhóm Core Layer gồm các singleton (AuthService, MediaService, HistoryService, QueueUploadService, các service khác) cùng với Guards (AuthGuard, WsActivatorGuard, ConfirmDeactivateGuard), Interceptors (BaseUrlInterceptor, HttpErrorInterceptor), Strategies (CustomRouteReuseStrategy, DaPlexTitleStrategy), Initializer (AppInitializer); nhóm Shared Layer gồm reusable components (VideoPlayer, MediaList, Swiper, StarRating, Skeleton, SlideMenu, ...) và WsModule (WsService + socket.io-client). Tầng dưới là 5 Feature Modules: HomeModule (lazy, /), AuthModule (lazy, /auth), MediaModule (lazy, /media), AdminModule (lazy, /admin), UsersModule (lazy, /users). Mũi tên từ AppModule xuống Core/Shared/Feature; mũi tên từ Feature imports Shared và Core.
  nodes:
    - AppModule → AppRoutingModule
    - AppModule → TranslocoRootModule (i18n en/vi)
    - AppModule → ServiceWorkerModule (PWA)
    - AppModule → CoreLayer (singleton services, guards, interceptors)
    - AppModule → SharedLayer (reusable components, WsModule)
    - AppRoutingModule → HomeModule (lazy, path /)
    - AppRoutingModule → AuthModule (lazy, path /auth)
    - AppRoutingModule → MediaModule (lazy, path /media)
    - AppRoutingModule → AdminModule (lazy, path /admin)
    - AppRoutingModule → UsersModule (lazy, path /users)
    - HomeModule → SharedLayer
    - MediaModule → SharedLayer
    - AdminModule → SharedLayer
    - CoreLayer: AuthService, MediaService, HistoryService, RatingsService, PlaylistsService, CollectionService, QueueUploadService, ItemDataService, WsService
    - SharedLayer: VideoPlayerComponent, MediaListComponent, SwiperComponent, StarRatingComponent, SkeletonComponent, SlideMenuComponent, EpisodeListComponent
  style: top-to-bottom; AppModule nền xanh đậm; CoreLayer nền xanh nhạt bên trái; SharedLayer nền xanh nhạt bên phải; Feature Modules nền xanh lá nhạt ở dưới; mũi tên lazy load dùng nét đứt
  output:
    drawio: figures/hinh-4-2-kien-truc-module-angular-daplex-dune-v2.drawio
    png: figures/hinh-4-2-kien-truc-module-angular-daplex-dune-v2.png
-->
![Hình 4.2: Kiến trúc module Angular của daplex-dune-v2](pending)
*Hình 4.2: Phân tầng kiến trúc module Angular — AppModule root, Core Layer singleton, Shared Layer tái sử dụng, và 5 Feature Modules lazy-loaded*

Hình 4.2 minh họa cấu trúc phân tầng của ứng dụng Angular. AppModule đóng vai trò root module, khai báo `AppRoutingModule` định nghĩa toàn bộ navigation tree, `TranslocoRootModule` cấu hình đa ngôn ngữ, và `ServiceWorkerModule` kích hoạt PWA. Năm feature modules được load theo yêu cầu (lazy load) khi người dùng điều hướng đến route tương ứng — trình duyệt chỉ tải bundle của module đó tại thời điểm cần, giúp bundle khởi đầu (`main.js`) nhỏ hơn đáng kể.

---

## Tầng Core — Các Thành Phần Singleton

Tầng core chứa toàn bộ infrastructure code không mang logic nghiệp vụ cụ thể của bất kỳ chức năng nào, mà phục vụ toàn bộ ứng dụng. **`AuthService`** là service trung tâm nhất, quản lý vòng đời phiên người dùng: sau khi đăng nhập thành công, service lưu access token trong memory (thuộc tính `_accessToken` kiểu `string | null`, không bao giờ ghi ra localStorage), đồng thời decode JWT bằng `jwtDecode` để tính thời điểm hết hạn và tự động lên lịch gọi `refreshToken()` trước một phút thông qua `window.setTimeout`. Cơ chế này đảm bảo access token luôn hợp lệ trong suốt phiên làm việc mà không cần người dùng đăng nhập lại. Refresh token được lưu trong HttpOnly cookie do server phát — Angular không thể đọc cookie này, chỉ gửi kèm tự động nhờ `withCredentials: true`, bảo vệ khỏi XSS.

**`BaseUrlInterceptor`** hoạt động như middleware cho mọi request HTTP: nếu URL không bắt đầu bằng `http`, interceptor tự động prepend `environment.apiUrl` (mặc định `http://localhost:3000/api`) vào đầu URL. Bên cạnh đó, interceptor gắn header `Authorization: Bearer <token>` từ `AuthService.accessTokenValue`, header `Accept-Language` theo ngôn ngữ hiện tại, và header `X-Socket-ID` chứa socket ID của kết nối WebSocket hiện tại — server dùng header này để tránh gửi lại WebSocket event cho chính client đã trigger action. Logic thêm header được kiểm soát bởi `HttpContext` token `CAN_INTERCEPT`: các request không cần interceptor (như tải file ngôn ngữ i18n, gọi API xác thực email) có thể opt-out bằng cách set context phù hợp.

**`AppInitializer`** là factory function chạy một lần duy nhất trong giai đoạn bootstrap Angular. Khi ứng dụng khởi động, initializer kiểm tra sự tồn tại của cookie `authenticated=true` — một cookie không HttpOnly được server ghi kèm khi phát refresh token, dùng làm tín hiệu để Angular biết người dùng đã đăng nhập từ session trước. Nếu cookie tồn tại, initializer gọi `authService.refreshToken()` để lấy access token mới trước khi Angular render bất kỳ route nào, đảm bảo trạng thái xác thực nhất quán từ đầu.

**`CustomRouteReuseStrategy`** kế thừa từ `RouteReuseStrategy` của Angular để tối ưu hiệu năng navigation. Khi người dùng điều hướng đi khỏi một route có `data.shouldReuse: true`, component tree của route đó được Angular lưu cache (detach) thay vì destroy. Khi navigate trở lại route trong danh sách `data.reuseRoutesFrom`, component được tái gắn (reattach) ngay lập tức mà không qua lifecycle `ngOnInit` lại — đặc biệt có ích cho trang danh sách media, nơi việc destroy rồi tái tạo component sẽ trigger lại API call và reset scroll position.

---

## Tầng Shared — Component và Module Tái Sử Dụng

Tầng shared tập trung các component UI không liên kết với domain cụ thể nào, được import bởi nhiều feature module. Thư mục `shared/components` chứa 21 component, trong đó các component chính bao gồm:

| Component | Mô tả |
|---|---|
| `video-player` | Trình phát tích hợp Vidstack |
| `media-list` | Grid/list hiển thị catalog |
| `swiper` | Carousel sử dụng Swiper.js |
| `episode-list` | Danh sách tập phim |
| `star-rating` | Đánh giá sao tương tác |
| `skeleton` | Loading placeholder |
| `slide-menu` | Menu trượt mobile |
| `file-upload` | Upload với progress |
| `circular-progress` | Vòng tròn tiến trình |
| `stepper` | Wizard form |
| `home-header` | Thanh tiêu đề trang chủ |
| `home-footer` | Footer trang chủ |

Việc tập trung tại shared tránh trường hợp hai feature module tự định nghĩa component tương tự nhau với hành vi khác nhau.

**`WsModule`** trong `shared/modules/ws` đóng gói toàn bộ logic WebSocket thành một Angular module nhỏ. `WsService` sử dụng `socket.io-client` với transport `websocket` (bỏ qua polling để giảm latency), wrap các event của Socket.IO thành `Observable` thông qua `fromEvent()` của RxJS để tương thích với async pipe và lifecycle của Angular. Service hỗ trợ room-based messaging qua `joinRoom()` và `leaveRoom()` — khi encode video hoàn thành, server emit event vào room tương ứng ID của job, và chỉ client đang theo dõi job đó nhận được thông báo. Module nhận hai token tùy chọn qua DI: `WS_NAMESPACE` để kết nối đến một Socket.IO namespace cụ thể và `WS_AUTH` để bật gửi access token khi handshake.

**`TranslocoRootModule`** cấu hình hệ thống đa ngôn ngữ với hai ngôn ngữ được hỗ trợ: tiếng Anh (`en`) và tiếng Việt (`vi`). File ngôn ngữ được tải lazy từ `/assets/i18n/{lang}.json` qua HTTP, không đóng gói vào bundle chính. `DaPlexTitleStrategy` tích hợp router với Transloco: khi Angular router resolve một route mới, strategy tra cứu key `pageTitles.{routeTitle}` trong translation dictionary, sau đó cập nhật `<title>` của trang theo định dạng `{tên đã dịch} - DaPlex`. Cơ chế này đảm bảo tiêu đề trang hiển thị đúng ngôn ngữ mà người dùng đang chọn, quan trọng cho cả UX lẫn SEO.

---

## Quản Lý State và Dữ Liệu

DaPlex frontend sử dụng **`@ngrx/signals`** 20.1.0 để quản lý state phản ứng theo kiến trúc signal-based thay vì Redux-style store truyền thống. `@ngrx/signals` cung cấp `signalStore()` cho phép định nghĩa các atom state nhỏ, composed được trong phạm vi feature module — không cần global store, không cần action/reducer boilerplate. State của màn hình lọc media (bộ lọc thể loại, sắp xếp, phân trang) được lưu trong signal store local của MediaModule; khi component unmount theo lazy loading, store đó bị GC cùng với component.

Các service như `MediaService`, `HistoryService`, `PlaylistsService`, `CollectionService` đảm nhiệm việc gọi API tương ứng và trả về `Observable<T>` — component subscribe để nhận dữ liệu và dùng `async pipe` trong template để tự động unsubscribe khi destroy. `QueueUploadService` quản lý hàng đợi upload file: khi admin chọn nhiều file cùng lúc, service xếp hàng và upload tuần tự, emit progress event qua Subject để component hiển thị thanh tiến trình real-time. `ItemDataService` phục vụ mục đích đặc biệt: truyền dữ liệu item (media metadata, episode) giữa hai route liền kề mà không cần API round-trip — khi người dùng click vào một media card, component nguồn ghi data vào service, component đích đọc lại ngay thay vì tải lại từ server.

---

## Cấu Trúc Chi Tiết Các Phần

Phần 4.2 được tổ chức thành ba mục chi tiết tương ứng với ba khía cạnh kỹ thuật chính của frontend:

- **[4.2.1. Cấu trúc dự án Angular](4.2.1-cau-truc-du-an-angular.md)** — Phân tích chi tiết cấu trúc thư mục, tổ chức file, cách phân chia core/shared/modules, và các quy ước đặt tên trong dự án Angular.
- **[4.2.2. Module và routing](4.2.2-module-va-routing.md)** — Mô tả AppRoutingModule, HomeLayoutComponent shell, cấu hình lazy loading cho từng feature module, guard bảo vệ route, và cơ chế route reuse.
- **[4.2.3. Trình phát video](4.2.3-trinh-phat-video.md)** — Phân tích VideoPlayerComponent tích hợp Vidstack và DASH.js, cấu hình ABR, xử lý subtitle và audio track, và giao tiếp với backend streaming endpoint.
