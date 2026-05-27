# 2.3. Yêu Cầu Chức Năng

Yêu cầu chức năng (functional requirements) của hệ thống DaPlex được tổ chức theo tác nhân chính, phản ánh trực tiếp tập quyền (permission set) mà mỗi nhóm người dùng sở hữu trong hệ thống RBAC. Cách tổ chức này đảm bảo mỗi yêu cầu chức năng đều có thể truy ngược về một hoặc nhiều endpoint cụ thể trong `DaPlex-API`, một hoặc nhiều Use Case trong tầng ứng dụng Angular, và một tập hành động được phép theo cấu trúc `UserPermission` enum trong codebase.

Toàn bộ chức năng của hệ thống phân thành hai nhóm chính: nhóm chức năng dành cho người dùng thông thường (User) phục vụ nhu cầu tiêu thụ nội dung hàng ngày, và nhóm chức năng dành cho quản trị viên (Administrator) phục vụ nhu cầu vận hành và quản lý hệ thống.

---

## Mục lục

- [2.3.1. Yêu cầu chức năng — Người dùng thông thường](2.3.1-nguoi-dung.md)
- [2.3.2. Yêu cầu chức năng — Quản trị viên](2.3.2-quan-tri-vien.md)
