# DaPlex Refactoring Plan
**Branch:** `refactor/codebase-cleanup-2026-05`
**Generated:** 2026-05-28
**Scope:** DaPlex-API · daplex-dune-v2 · DaPlex-Transcoder

---

## Executive Summary

Analysis of 1,574 source files (7,880 graph nodes, 11,670 edges) across all three repos surfaced **3 security vulnerabilities**, **4 confirmed functional bugs**, and **~150 improvement opportunities**. The dominant theme is god-class proliferation: `MediaService` (3,334 lines), `VideoService` (1,579 lines), `ConfigureMediaComponent` (885 lines), and `MediaController` (1,173 lines) together account for ~7,000 lines of mixed concerns. A secondary theme is inconsistent error handling: 51+ `console.error` calls bypass the NestJS logger, and several critical async paths have no error handlers.

---

## Security Issues — Fix Immediately (Before Any Other Work)

### SEC-1 · Hardcoded JWT Secrets · `DaPlex-API/src/config.ts`
**Severity: CRITICAL**

Three env vars silently fall back to predictable defaults if not set:
```
ACCESS_TOKEN_SECRET  → 'default-access-token-secret'
REFRESH_TOKEN_SECRET → 'default-refresh-token-secret'
COOKIE_SECRET        → 'default-cookie-secret'
```
Any attacker knowing these defaults can forge valid JWTs. **Fix:** Remove all three fallback strings. Mark them `.required()` in the Joi validation schema so the app fails fast at startup.

### SEC-2 · AES IV Reuse · `DaPlex-Transcoder/src/utils/string-crypto.util.ts:5`
**Severity: CRITICAL**

`this.iv = crypto.randomBytes(16)` is generated once in the constructor and reused across all `encrypt()` calls from the same instance. IV reuse in CBC mode compromises confidentiality. **Fix:** Move IV generation inside `encrypt()` so each call produces a unique IV.

### SEC-3 · Missing RolesGuard on updatePoster · `DaPlex-API/src/resources/media/media.controller.ts:267`
**Severity: HIGH**

`updatePoster` uses `@UseGuards(AuthGuard)` only. The adjacent `deletePoster` correctly adds `RolesGuard`. Any authenticated user can replace poster images regardless of role. **Fix:** Add `RolesGuard` to the `updatePoster` guard list and audit all write endpoints.

---

## Confirmed Functional Bugs

### BUG-1 · AV1 Queue Never Cleared · `DaPlex-API/src/resources/media/media.service.ts:~3204`
`videoTranscodeVP9Queue.remove` is called twice; `videoTranscodeAV1Queue.remove` is never called. AV1 transcode jobs accumulate indefinitely. **Fix:** Change line ~3204 to `this.videoTranscodeAV1Queue.remove(jobId)`.

### BUG-2 · Double-Push on Playlist Pagination · `daplex-dune-v2/src/app/modules/media/pages/playlists/playlists.component.ts:78`
`appendPlaylistItems` spreads `newList.results` into the new object literal and then calls `.push(...newList.results)` again — doubling every appended page. **Fix:** Single immutable merge; remove the `.push()` call.

### BUG-3 · Wrong Handler on "Add Episode" Menu Item · `daplex-dune-v2/src/app/modules/admin/pages/media/media.component.ts:320`
The "Add Episode" menu item's `command` calls `this.showDeleteMediaDialog(...)` — a copy-paste error. **Fix:** Wire to the correct create-episode handler.

### BUG-4 · Dead Ternary (Both Branches Same Value) · `DaPlex-Transcoder/src/utils/mediainfo.util.ts:50`
```ts
const encodingSettings = sameRes ? this.knwonEncodingSettings : this.knwonEncodingSettings;
```
Both branches are identical. **Fix:** Use `multiResEncodingSettings` in the false branch, or remove it.

---

## Prioritized Refactoring Roadmap

> **Rule:** Write unit tests for current behavior *before* each change. Confirm tests pass *after*. Each phase = one or more PRs.

---

### Phase 1 — Security & Bug Fixes (1–2 days)

| ID | File | Action |
|----|------|--------|
| SEC-1 | `DaPlex-API/src/config.ts` | Remove hardcoded secret defaults, mark required |
| SEC-2 | `DaPlex-Transcoder/src/utils/string-crypto.util.ts:5` | Move IV gen inside `encrypt()` |
| SEC-3 | `DaPlex-API/src/resources/media/media.controller.ts:267` | Add `RolesGuard` to `updatePoster` |
| BUG-1 | `DaPlex-API/src/resources/media/media.service.ts:~3204` | Fix AV1 queue clear |
| BUG-2 | `daplex-dune-v2/…/playlists/playlists.component.ts:78` | Fix double-push in `appendPlaylistItems` |
| BUG-3 | `daplex-dune-v2/…/admin/pages/media/media.component.ts:320` | Fix "Add Episode" handler |
| BUG-4 | `DaPlex-Transcoder/src/utils/mediainfo.util.ts:50` | Fix dead ternary |

---

### Phase 2 — Dead Code Removal (2–3 days)

#### 2.1 Delete Dead Interfaces (Transcoder)
- `src/resources/video/interfaces/source-info.interface.ts` — never imported anywhere
- `src/resources/video/interfaces/source-audio-info.interface.ts` — never imported
- `src/resources/video/interfaces/input-audio-args.interface.ts` — never imported
- `src/resources/video/interfaces/user.interface.ts` — never imported

#### 2.2 Delete Dead NestJS Schema
- `DaPlex-Transcoder/src/schemas/external-storage.schema.ts` — NestJS `@Schema` class never registered in any module; the raw Mongoose model in `models/` is the live one.

#### 2.3 Delete Duplicate Progress Entity
- `DaPlex-Transcoder/src/resources/video/entities/progress.entity.ts` — byte-for-byte identical to `src/common/entities/progress.entity.ts`. Delete; update all imports to use the common path.

#### 2.4 Remove Dead Imports (Frontend)
- `GenresComponent` — unused `ActivatedRoute`, `Router` imports
- `ProductionsComponent` — same
- `PlaylistsComponent:39` — dead `renderer.addClass` comment + unused `Renderer2` context

#### 2.5 Remove Debug Logging from Production Code
- `DaPlex-Transcoder/src/utils/ffmpeg-helper.util.ts:7` — `console.log(data)`
- `DaPlex-Transcoder/src/utils/rclone.util.ts:434` — `console.log(cleanData)`
- `daplex-dune-v2/…/video-player.service.ts:250` — `console.log('page got message:...')`

#### 2.6 Fix Typos
- `DaPlex-Transcoder/src/utils/mediainfo.util.ts` — `knwonEncodingSettings` → `knownEncodingSettings`
- `DaPlex-Transcoder/src/resources/video/video.consumer.ts` — `VideoCosumer*` → `VideoConsumer*` (4 classes)
- `DaPlex-API/src/resources/auth/guards/auth.guard.ts:31` — `'eixst'` → `'exists'`
- `DaPlex-Transcoder/src/resources/video/video.controller.ts:17` — `resultWorker` → `resumeWorker`

#### 2.7 Remove Dead Commented-Out Code Blocks
- `DaPlex-API/src/resources/media/media.service.ts:1371,2471` — dead email notification blocks
- `daplex-dune-v2/…/create-media.component.ts:399–430` — dead `onUpdateImagesFormSubmit` block
- `DaPlex-Transcoder/src/resources/video/video.service.ts:365–373` — dead `handleSegmentError`
- `DaPlex-Transcoder/src/resources/video/video.service.ts:467–468` — dead `cancelled-encoding` queue messages
- `DaPlex-Transcoder/src/resources/video/video.service.ts:976–981` — permanently disabled FFmpeg flags

#### 2.8 Fix Missing Schema Field
- `DaPlex-Transcoder/src/models/setting.model.ts` — add `audioSpeedParams: String` to both `ISetting` interface and `settingSchema`.

#### 2.9 Replace AppService Hello World (Transcoder)
- `AppService.getHello()` → repurpose `GET /` as a health check returning `{ status: 'ok' }`.

---

### Phase 3 — Extract Constants (1 day)

| Constant | Value | Affected Files |
|----------|-------|----------------|
| `FFMPEG_RECONNECT_ARGS` | `['-reconnect','1','-reconnect_on_http_error','400,401,...']` | 8 files |
| `HDR_TONEMAP_FILTER` | zscale tonemap string | `video.service.ts`, `thumbnail.util.ts` |
| `THUMBNAIL_FOLDER` | `'thumbnails'` | 5 locations in `video.service.ts` |
| `EXPECTED_AUDIO_STREAMS` | `3` | `video.service.ts:454` |
| `OPUS_STEREO_BITRATE` | `128` | `video.service.ts:891` |
| `MAX_AUDIO_CHANNELS` | `8` | `video.service.ts:920` |
| `SURROUND_CHANNEL_COUNTS` | `[5,6,7,8]` | `video.service.ts:457` |
| `AUTH_COOKIE_MARKER` | `'authenticated=true'` | `http-error.interceptor.ts` |

All go into `config.ts` (Transcoder) or `core/constants.ts` (Frontend).

---

### Phase 4 — Inconsistent Error Handling (1–2 days)

#### 4.1 Replace `console.error` with NestJS Logger (API — 51+ occurrences)
Files: `onedrive.service.ts` (11×), `filer.service.ts` (9×), `s3.service.ts` (7×), `tmdb-scanner.service.ts` (9×), `tvdb-scanner.service.ts` (7×), `cloudflare-r2.service.ts` (2×), `http-email.service.ts` (3×), `imgur.service.ts` (3×).

```ts
private readonly logger = new Logger(ServiceName.name);
// before: console.error(msg)
// after:  this.logger.error(msg, trace)
```

#### 4.2 Add Missing Error Handlers (Frontend)
- `ConfigureMediaComponent.loadMedia()` — loading flag never reset on HTTP error; same for `loadEpisodes`, `loadVideos`, `loadSubtitleFormData`
- `HomeComponent` — add `catchError(() => of(null))` per inner observable so one failing request doesn't silence all six
- `history.service.ts.updateToServer()` — failed watch-time writes silently discarded; add retry or at minimum an error log
- `media.component.ts.removeMedia()` — no user feedback on deletion failure

#### 4.3 Type-Narrow `catch (e)` Unsafe Access (Transcoder)
`video.service.ts:683,693,762–769` and `thumbnail.util.ts:152–157` access `e.code` on untyped `catch (e)`. Apply:
```ts
if (typeof e === 'object' && e !== null && 'code' in e)
```
Or introduce a typed `FfmpegError` class.

---

### Phase 5 — Type Safety (1–2 days)

| File | Issue | Fix |
|------|-------|-----|
| `DaPlex-API/…/media.service.ts` | 8× `let fileInfo: any` | Define `StorageFileInfo` interface |
| `DaPlex-API/…/media-result.consumer.ts` | `Promise<any>` return | Define `ProcessResult` union |
| `DaPlex-Transcoder/…/video.service.ts` | `Queue<…, any, …>` | Replace `any` with `Record<string, never>` |
| `DaPlex-Transcoder/…/string-crypto.util.ts` | `resolve(null)` on `Promise<string>` | Change to `Promise<string \| null>` |
| `DaPlex-Transcoder/…/storage.interface.ts` | `class IStorage` | Change to `interface IStorage` |
| `DaPlex-Transcoder/…/video.service.ts:86` | `codec: number = 1` | `codec: VideoCodec = VideoCodec.H264` |
| `daplex-dune-v2/core/utils/ng-track-by.ts` | All `any` types | Generic `<T extends { id: unknown }>` |
| `daplex-dune-v2/core/services/auth.service.ts:85` | `jwtDecode<any>` | Define `JwtPayload` interface |
| `daplex-dune-v2/core/services/media.service.ts` + 5 siblings | `{ [key: string]: any }` | `Record<string, string \| number \| boolean>` |
| `daplex-dune-v2/…/configure-media.component.ts` | `editImage(data: any)` (4 copies) | Define `ImageEditorData` interface |
| `daplex-dune-v2/core/guards/auth.guard.ts:22` | Unchecked cast on `route.data` | Add array type guard |
| `DaPlex-API/…/auth.service.ts` | `+configService.get<string>()` to number | `parseInt(..., 10)` with NaN guard |

---

### Phase 6 — Deduplication (3–4 days)

| Item | What to Extract | Where |
|------|-----------------|-------|
| 6.1 | Abstract BullMQ consumer base class | API `media.consumer.ts` + Transcoder `video.consumer.ts` |
| 6.2 | `StorageResolverService` + `IStorageService` interface | API — replaces 12× storage if-else dispatch |
| 6.3 | `resolveIoEmitter()` private helper | API `media.service.ts` — replaces ~30 inline socket resolutions |
| 6.4 | Generic `findOrCreateEntities<T>()` | API `media.service.ts` — collapses 3 near-identical helpers |
| 6.5 | `toHttpParams(dto)` utility | Frontend — shared across 6 service files |
| 6.6 | `TablePaginationHelper.buildParams()` | Frontend — shared across 3 admin list pages |
| 6.7 | `MediaMetaService` | Frontend — shared between `DetailsComponent` and `WatchComponent` |
| 6.8 | `ConfirmActionService` wrapper | Frontend — replaces 12× copy-pasted `confirmationService.confirm()` |
| 6.9 | `createCancelChecker()` util | Transcoder — shared across `VideoService` and `videoSourceHelper` |
| 6.10 | `spawnManagedProcess()` util / `ProcessSpawnerService` | Transcoder — replaces 4× identical spawn skeletons |
| 6.11 | Collapse `createTwoPassesVideoEncodingArgs` pass=1/pass=2 | Transcoder — ~50 duplicated lines |

---

### Phase 7 — God Class Decomposition (8–14 days)

Each extraction is a separate PR. Write tests for the extracted service first.

#### 7.1 `MediaService` → 8 Focused Services (API) — 8–10 days

| New Service | Responsibility |
|-------------|----------------|
| `MediaCrudService` | CRUD, pagination, search |
| `MediaImageService` | Poster/backdrop upload & delete |
| `MediaVideoService` | Source upload, transcode dispatch, queue management |
| `MediaSubtitleService` | Subtitle CRUD |
| `MediaChapterService` | Chapter management |
| `MediaEpisodeService` | TV episode CRUD |
| `MediaStreamService` | HLS/DASH manifest management |
| `MediaSchedulerService` | The 4 `@Cron`-decorated jobs (start here — fewest deps) |

#### 7.2 `MediaController` → 5 Controllers (API) — 2–3 days

| Controller | Endpoints |
|------------|-----------|
| `MovieController` | Basic media CRUD, poster |
| `TVEpisodeController` | Episode management |
| `MediaVideoController` | Source upload, transcode control |
| `MediaSubtitleController` | Subtitle CRUD |
| `MediaChapterController` | Chapter CRUD |

#### 7.3 `ConfigureMediaComponent` → 6 Tab Sub-Components (Frontend) — 4–5 days

| New Component | Responsibility |
|---------------|----------------|
| `ConfigureMediaFormComponent` | Update-media form |
| `ConfigureMediaImagesComponent` | Poster/backdrop editing |
| `ConfigureMediaVideosComponent` | Trailer management |
| `ConfigureMediaSourceComponent` | Movie source upload |
| `ConfigureMediaSubtitlesComponent` | Subtitle list |
| `ConfigureMediaEpisodesComponent` | TV episode list |

Parent becomes a thin `media$` signal container.

#### 7.4 `MediaFormHelperService` (Frontend) — 2 days
`ConfigureMediaComponent` and `CreateMediaComponent` duplicate ~40% of their code. Extract shared form-building, patching, suggestion-loading, `editImage`, dialog-open methods into an injectable service.

#### 7.5 `VideoService` → 5 Focused Services (Transcoder) — 4–5 days

| New Service | Responsibility |
|-------------|----------------|
| `FfmpegArgBuilder` | All FFmpeg argument builders |
| `RcloneService` | All rclone spawn wrappers |
| `ProcessSpawnerService` | Managed `child_process.spawn` helper |
| `QualityService` | Quality calculation, validation, availability |
| `CodecPresetRegistry` | SVT-AV1 / libaom codec preset dispatch |

#### 7.6 Migrate Transcoder to Persistent Mongoose Connection — 1–2 days
Replace all inline `mongoose.connect/disconnect` per job with `MongooseModule.forRootAsync` in `AppModule`. Inject models via `@InjectModel()`. Affects `VideoService:89,152` and `findAvailableQuality:1467`.

---

### Phase 8 — Auth Guard Consolidation (API) — 1 day

- Remove `OwnerGuard` — its only check is already in `RolesGuard`
- Rename `throwError: false` option to `optional: boolean`
- Remove local `ExtraUserProperties` class; use `AuthUserDto` directly
- Export `FindUserOptions` from `auth.service.ts`

---

### Phase 9 — Barrel Exports & Module Cleanup — 1 day

- Add `index.ts` barrels to: `DaPlex-API/src/resources/{media,auth,users,playlists,genres,collections,productions}/`
- `media.module.ts` — remove duplicate `HistoryModule` import
- Extract `TRANSCODE_JOB_OPTIONS` constant from 4 identical `BullModule.registerQueue` calls
- Remove dead `email`/`password` fields from `RefreshTokenPayload`

---

## Priority Matrix

| Priority | Repo | Item | Type |
|----------|------|------|------|
| 🔴 CRITICAL | API | Hardcoded JWT secrets | Security |
| 🔴 CRITICAL | Transcoder | AES IV reuse | Security |
| 🔴 HIGH | API | Missing RolesGuard on updatePoster | Security |
| 🔴 HIGH | API | AV1 queue never cleared | Bug |
| 🔴 HIGH | Frontend | Double-push pagination bug | Bug |
| 🔴 HIGH | Frontend | Wrong "Add Episode" handler | Bug |
| 🟠 HIGH | API | 3,334-line MediaService god class | Maintainability |
| 🟠 HIGH | API | 4 copy-paste BullMQ consumers | Maintainability |
| 🟠 HIGH | Transcoder | 1,579-line VideoService god class | Maintainability |
| 🟠 HIGH | Transcoder | Per-job mongoose connect/disconnect | Performance |
| 🟠 HIGH | Frontend | 885-line ConfigureMedia god component | Maintainability |
| 🟡 MED | API | 51+ console.error calls | Observability |
| 🟡 MED | All | 8× FFMPEG_RECONNECT_ARGS duplication | Code health |
| 🟡 MED | Frontend | `any` params in 6 service files | Type safety |
| 🟢 LOW | All | Dead interfaces, typos, barrel exports | Hygiene |

---

## Estimated Total Effort

| Phase | Days |
|-------|------|
| 1 — Security & Bugs | 1–2 |
| 2 — Dead Code | 2–3 |
| 3 — Constants | 1 |
| 4 — Error Handling | 1–2 |
| 5 — Type Safety | 1–2 |
| 6 — Deduplication | 3–4 |
| 7 — God Classes | 8–14 |
| 8 — Auth Guards | 1 |
| 9 — Barrel/Module | 1 |
| **Total** | **~19–30 dev-days** |

---

## Graphify Outputs

- Interactive graph: `graphify-out/graph.html`
- Full audit report: `graphify-out/GRAPH_REPORT.md`
- Raw graph data: `graphify-out/graph.json`
