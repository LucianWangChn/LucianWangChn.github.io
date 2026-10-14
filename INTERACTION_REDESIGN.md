# 主页交互改造 · 2026-10-14

本版采用深松绿色首屏、浅色学术内容区、个人照片与轨道线条，保留原有项目、学习成绩、荣誉、简历及服务入口。

## 交互

- 滚动：正文逐步显现、阅读进度、章节导航高亮、章节配色、首屏轨道旋转及返回顶部。
- 鼠标：首屏光影与照片轻微位移、研究卡片光斑和倾斜；使用系统指针。
- 触屏：保留原生纵向滚动和锚点导航，不启用指针动效。
- 动效控制：右上角闪电按钮开关动效，浏览器保存偏好；系统“减少动态效果”优先。
- 无 JavaScript：完整显示内容，保留原生导航、详情折叠和简历下载。

原 `assets/style.css` 不变；新增 `assets/motion.css` 与 `assets/motion.js` 只用于首页。项目技术说明页继续沿用原样式。无运行时第三方依赖，不需要构建。

## 本地运行与验证

在仓库目录启动：

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8765/`。另一个终端执行：

```powershell
node --check assets/motion.js
python tests/verify_homepage.py
git diff --check
```

浏览器验证需要 Python Playwright 和 Chromium；网站运行不需要这些工具。已通过 50 项检查，覆盖 1440 px 桌面、320/390/600/768/1024 px 布局、鼠标交互、滚动导航、减少动态效果、动效偏好持久化、键盘跳转、无 JavaScript、项目页及 PDF/Word 下载。截图与报告保存在 Git 忽略的 `.qa/`。

## Git 管理

- 改造分支：`codex/interactive-homepage`。
- 原有域名、照片与页脚修改已单独保存为基线提交 `72a2508`。
- 视觉、动效、验证脚本与本说明单独提交，便于审阅和回退。
- 原有未跟踪的 `deploy/` 和父目录归档保持原状。
- 若要撤回改造，可对视觉改造提交执行 `git revert`，保留基线内容。

## 线上发布状态

2026-10-14 核验：正式域名首页可访问；线上样式和个人照片与本地基线的 SHA-256 一致。正式首页尚未包含此次动效。

现有服务器账号仅能访问隔离的 SFTP 目录，无法写入 `/var/www/lucianwang.com`；本次没有修改服务器内容。GitHub 分支推送不会自动更新该服务器上的正式域名。

增量包 `releases/homepage-interactive-20261014.tar.gz` 仅含 `index.html`、`assets/motion.css` 和 `assets/motion.js`。发布脚本 `scripts/publish-homepage.sh` 在服务器上检查主页基线与归档成员、备份入口文件，先安装资源，再原子替换首页。需要可写主页目录的服务器账号。执行方式：

```bash
bash publish-homepage.sh /absolute/path/homepage-interactive-20261014.tar.gz
```

脚本固定使用现有主页目录；不修改 Nginx、证书、课程服务或智能体。若线上首页已被更新，脚本停止，需先比较变化。发布后应核验首页、两个新增资源、简历下载和既有服务入口；回退命令由脚本输出。
