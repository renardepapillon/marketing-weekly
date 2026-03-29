# 任务：营销周报系统

## 目标
构建一个完整的营销周报自动化系统，抓取多个平台微信公众号 RSS Feed，生成结构化周报并发布到 GitHub Pages。

## RSS Feed 列表
```
巨量引擎营销观察（抖音/字节）: https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3264297904.atom
快手磁力引擎商业洞察: https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3574491079.atom
哔哩哔哩营销科学: https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3964164543.atom
腾讯广告: https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_2394733811.atom
巨量引擎营销科学: https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3874586334.atom
阿里妈妈数字营销: https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_2393601741.atom
```

## 项目结构
```
marketing-weekly/
├── scripts/
│   └── generate_report.py    # 主脚本：抓取 RSS + 生成周报
├── docs/                     # GitHub Pages 根目录
│   ├── index.html            # 周报首页（列出所有周报）
│   └── reports/              # 各周周报存放目录
│       └── YYYY-WNN.html     # 单期周报
├── .github/
│   └── workflows/
│       └── weekly-report.yml # GitHub Actions：每周一早上 9:00 自动运行
└── README.md
```

## 周报字段（每篇文章）
对每篇文章提取/生成以下字段：
- **发布日期**：从 RSS <updated> 字段提取
- **发布平台**：根据 Feed 来源标记（如：巨量引擎、快手、B站、腾讯广告、阿里妈妈）
- **周期范围**：本期周报覆盖的日期范围（上周一到上周日）
- **内容概览**：文章摘要（2-3句话，从文章正文提取关键句）
- **解决方案**：文章中提到的产品/工具/方案（如有）
- **行业/企业痛点**：文章针对的问题或场景
- **新的合作方式**：文章中提到的合作模式、联合营销等（如有）
- **新的玩法**：创新营销手段、新格式、新功能（如有）
- **视觉**：文章封面图 URL（从 RSS 内容中提取 og:image 或第一张图）
- **链接**：原文链接

## 周度小结
每期周报末尾生成一个「本周平台动向小结」：
- 各平台本周发文数量
- 本周出现频率最高的关键词/话题（如 AI、全域、ROI 等）
- 跨平台共同趋势（2-3条洞察）

## GitHub Pages 设计
- 简洁现代风格，中文界面
- 首页：显示所有历史周报列表（按周倒序）
- 单期周报页：
  - 顶部：周期范围 + 平台图标导航
  - 中部：按平台分组显示文章卡片（含封面图、字段信息）
  - 底部：本周小结区块
- 响应式，手机可读
- 纯静态 HTML（无需后端，部署到 GitHub Pages）

## GitHub Actions 配置
- 触发时间：每周一 01:00 UTC（北京时间周一早上 9:00）
- 运行环境：ubuntu-latest，Python 3.11
- 步骤：
  1. checkout 仓库
  2. 安装依赖（requests, feedparser, jinja2）
  3. 运行 generate_report.py（抓取上周 RSS 文章，生成本期 HTML）
  4. git commit & push 新生成的 HTML 文件
  5. GitHub Pages 自动部署（从 docs/ 目录）
- 需要的 Secret：无（RSS 是公开的，GitHub Pages 部署用默认 GITHUB_TOKEN）

## 脚本要求（generate_report.py）
- 使用 feedparser 解析 Atom Feed
- 筛选本期时间范围内的文章（默认：上周一到上周日）
- 支持命令行参数 --start-date --end-date 手动指定范围
- 使用 Jinja2 模板生成 HTML
- 自动更新 docs/index.html（在列表中插入新周报链接）
- 封面图：从文章 content 字段中用正则提取第一个 <img> src
- 对无内容字段填入"暂无"占位

## 交付物
请创建完整可运行的项目，包含所有文件。
脚本需要可以直接运行：`python3 scripts/generate_report.py`
GitHub Actions workflow 需要可以直接复制到 `.github/workflows/` 使用。
