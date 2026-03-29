# 互联网平台营销周报

自动抓取各大平台营销公众号 RSS Feed，每周一生成结构化周报，发布到 GitHub Pages。

## 覆盖平台

| 公众号 | 平台 |
|--------|------|
| 巨量引擎营销观察 | 抖音/字节 |
| 快手磁力引擎商业洞察 | 快手 |
| 哔哩哔哩营销科学 | B站 |
| 腾讯广告 | 腾讯 |
| 巨量引擎营销科学 | 抖音/字节 |
| 阿里妈妈数字营销 | 阿里 |

## 使用

```bash
# 生成上周周报
python3 scripts/generate_report.py

# 生成指定周
python3 scripts/generate_report.py --week 2026-W13

# 指定日期范围
python3 scripts/generate_report.py --start-date 2026-03-23 --end-date 2026-03-30
```

## 自动化

GitHub Actions 每周一北京时间 09:00 自动运行，生成周报并推送到仓库，GitHub Pages 自动部署。

## GitHub Pages

Settings → Pages → Source: Deploy from branch → Branch: main → Folder: /docs → Save
