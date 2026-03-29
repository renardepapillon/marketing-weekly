#!/usr/bin/env python3
"""
互联网平台营销周报生成器
用法：
  python3 scripts/generate_report.py              # 生成上周周报
  python3 scripts/generate_report.py --week 2026-W13  # 生成指定周
"""

import urllib.request
import xml.etree.ElementTree as ET
import re
import os
import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────────────────────────

FEEDS = [
    {"name": "巨量引擎营销观察", "platform": "抖音/字节",
     "url": "https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3264297904.atom"},
    {"name": "快手磁力引擎商业洞察", "platform": "快手",
     "url": "https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3574491079.atom"},
    {"name": "哔哩哔哩营销科学", "platform": "B站",
     "url": "https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3964164543.atom"},
    {"name": "腾讯广告", "platform": "腾讯",
     "url": "https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_2394733811.atom"},
    {"name": "巨量引擎营销科学", "platform": "抖音/字节",
     "url": "https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_3874586334.atom"},
    {"name": "阿里妈妈数字营销", "platform": "阿里",
     "url": "https://wewe-rss-production-0970.up.railway.app/feeds/MP_WXS_2393601741.atom"},
]

NS = {'atom': 'http://www.w3.org/2005/Atom'}
CST = timezone(timedelta(hours=8))
ROOT = Path(__file__).parent.parent

# ── 工具函数 ──────────────────────────────────────────────────────────────────

def get_week_range(iso_week: str = None):
    """返回 (start, end, label)，默认上周"""
    if iso_week:
        year, w = iso_week.split('-W')
        start = datetime.strptime(f"{year}-W{w}-1", "%Y-W%W-%w").replace(tzinfo=CST)
    else:
        today = datetime.now(CST)
        start = today - timedelta(days=today.weekday() + 7)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    label = f"{start.strftime('%-m/%-d')}-{end.strftime('%-m/%-d')}"
    return start, end, label

def fetch_feed(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': 'marketing-weekly-bot/1.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def extract_cover(content_html: str) -> str:
    """从文章 HTML 中提取第一张图片 URL"""
    m = re.search(r'src="(https://mmbiz\.qpic\.cn/[^"]+)"', content_html)
    if m:
        return m.group(1)
    m = re.search(r'cover_image[^(]*\(([^)]+)\)', content_html)
    if m:
        return m.group(1)
    return ""

def extract_text(content_html: str, max_chars=300) -> str:
    """从 HTML 中提取纯文本摘要"""
    text = re.sub(r'<[^>]+>', '', content_html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars] + "…" if len(text) > max_chars else text

def parse_entries(feed_xml: bytes, start: datetime, end: datetime, feed_meta: dict) -> list:
    root = ET.fromstring(feed_xml)
    entries = []
    for entry in root.findall('atom:entry', NS):
        updated_str = entry.findtext('atom:updated', '', NS)
        try:
            dt = datetime.fromisoformat(updated_str.replace('Z', '+00:00')).astimezone(CST)
        except Exception:
            continue
        if not (start <= dt < end):
            continue
        link_el = entry.find('atom:link', NS)
        link = link_el.get('href', '') if link_el is not None else ''
        title = entry.findtext('atom:title', '', NS)
        content = entry.findtext('atom:content', '', NS) or ''
        cover = extract_cover(content)
        entries.append({
            "date": dt.strftime('%-m/%-d'),
            "dt": dt,
            "platform_name": feed_meta["name"],
            "platform": feed_meta["platform"],
            "title": title,
            "link": link,
            "cover": cover,
            "summary": extract_text(content, 200),
        })
    return entries

# ── HTML 生成 ─────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
         max-width: 1400px; margin: 0 auto; padding: 20px; background: #f5f5f5; color: #333; }}
  h1 {{ color: #1a1a1a; border-bottom: 3px solid #e63946; padding-bottom: 10px; }}
  .meta {{ color: #888; font-size: 14px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  th {{ background: #1a1a2e; color: #fff; padding: 12px 10px; text-align: left;
        font-size: 13px; white-space: nowrap; }}
  td {{ padding: 10px; border-bottom: 1px solid #f0f0f0; font-size: 13px;
        vertical-align: top; line-height: 1.6; }}
  tr:hover td {{ background: #fafafa; }}
  .platform {{ display: inline-block; padding: 2px 8px; border-radius: 12px;
               font-size: 12px; font-weight: 600; white-space: nowrap; }}
  .p-douyin {{ background: #ffe0e0; color: #c0392b; }}
  .p-kuaishou {{ background: #fff0cc; color: #b8860b; }}
  .p-bili {{ background: #e0eaff; color: #2563eb; }}
  .p-tencent {{ background: #e0f0e0; color: #15803d; }}
  .p-ali {{ background: #ffe8cc; color: #c05621; }}
  .cover img {{ width: 80px; height: 60px; object-fit: cover; border-radius: 4px; }}
  a {{ color: #2563eb; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .summary {{ max-width: 300px; color: #555; }}
  .week-tag {{ background: #e8f4fd; color: #1565c0; padding: 2px 8px;
               border-radius: 4px; font-size: 12px; }}
  .section-summary {{ background: #fff; border-radius: 8px; padding: 20px;
                      margin-top: 32px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  .section-summary h2 {{ margin-top: 0; color: #1a1a2e; }}
  .stat-grid {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }}
  .stat-card {{ background: #f8f9fa; border-radius: 8px; padding: 16px 20px;
                flex: 1; min-width: 140px; }}
  .stat-num {{ font-size: 28px; font-weight: 700; color: #e63946; }}
  .stat-label {{ font-size: 12px; color: #888; }}
  .keywords {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }}
  .kw {{ background: #e8f4fd; color: #1565c0; padding: 4px 10px;
         border-radius: 12px; font-size: 13px; }}
  .trend-list li {{ margin-bottom: 8px; line-height: 1.6; }}
</style>
</head>
<body>
<h1>📊 互联网平台营销周报</h1>
<div class="meta">周期范围：<strong>{week_label}</strong> &nbsp;|&nbsp; 共收录 <strong>{total}</strong> 篇 &nbsp;|&nbsp; 生成时间：{gen_time}</div>

<table>
<thead>
<tr>
  <th>周期范围</th>
  <th>发布日期</th>
  <th>发布平台</th>
  <th>内容概览</th>
  <th>解决方案</th>
  <th>行业/企业痛点</th>
  <th>新的合作方式</th>
  <th>新的玩法</th>
  <th>视觉</th>
  <th>链接</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>

{summary_section}

</body>
</html>"""

ROW_TEMPLATE = """<tr>
  <td><span class="week-tag">{week_label}</span></td>
  <td style="white-space:nowrap">{date}</td>
  <td><span class="platform {platform_class}">{platform_name}</span></td>
  <td class="summary">{summary}</td>
  <td>—</td>
  <td>—</td>
  <td>—</td>
  <td>—</td>
  <td class="cover">{cover_html}</td>
  <td><a href="{link}" target="_blank">原文 →</a></td>
</tr>"""

PLATFORM_CLASS = {
    "抖音/字节": "p-douyin",
    "快手": "p-kuaishou",
    "B站": "p-bili",
    "腾讯": "p-tencent",
    "阿里": "p-ali",
}

def build_html(entries: list, week_label: str) -> str:
    rows = []
    for e in sorted(entries, key=lambda x: x['dt']):
        cover_html = f'<img src="{e["cover"]}" alt="">' if e["cover"] else "—"
        rows.append(ROW_TEMPLATE.format(
            week_label=week_label,
            date=e["date"],
            platform_name=e["platform_name"],
            platform_class=PLATFORM_CLASS.get(e["platform"], ""),
            summary=e["summary"],
            cover_html=cover_html,
            link=e["link"],
        ))

    platform_counts = {}
    for e in entries:
        platform_counts[e["platform_name"]] = platform_counts.get(e["platform_name"], 0) + 1

    stat_cards = "".join(
        f'<div class="stat-card"><div class="stat-num">{v}</div><div class="stat-label">{k}</div></div>'
        for k, v in sorted(platform_counts.items(), key=lambda x: -x[1])
    )
    stat_cards = f'<div class="stat-card"><div class="stat-num">{len(entries)}</div><div class="stat-label">本周总文章数</div></div>' + stat_cards

    summary_section = f"""
<div class="section-summary">
  <h2>📈 本周平台动向小结</h2>
  <div class="stat-grid">{stat_cards}</div>
  <p><strong>各平台发文统计</strong>已如上图。如需补充 AI 趋势洞察，请运行带 --ai 参数的版本。</p>
</div>"""

    return HTML_TEMPLATE.format(
        title=f"营销周报 {week_label}",
        week_label=week_label,
        total=len(entries),
        gen_time=datetime.now(CST).strftime('%Y-%m-%d %H:%M CST'),
        rows="\n".join(rows),
        summary_section=summary_section,
    )

# ── 首页更新 ──────────────────────────────────────────────────────────────────

def update_index(report_filename: str, week_label: str, total: int):
    index_path = ROOT / "docs" / "index.html"
    new_item = f'<li><a href="reports/{report_filename}">📅 {week_label}（{total}篇）</a></li>'
    if index_path.exists():
        content = index_path.read_text()
        if report_filename in content:
            return  # 已存在
        content = content.replace("<!-- REPORTS -->", f"{new_item}\n    <!-- REPORTS -->")
        index_path.write_text(content)
    else:
        index_path.write_text(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>互联网平台营销周报</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:800px;margin:40px auto;padding:20px}}
h1{{color:#1a1a2e}}ul{{list-style:none;padding:0}}li{{margin:12px 0}}
a{{color:#2563eb;text-decoration:none;font-size:16px}}a:hover{{text-decoration:underline}}</style>
</head>
<body>
<h1>📊 互联网平台营销周报</h1>
<p>覆盖：巨量引擎 / 快手 / B站 / 腾讯广告 / 阿里妈妈</p>
<ul>
    {new_item}
    <!-- REPORTS -->
</ul>
</body></html>""")

# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', help='指定周，格式 2026-W13')
    parser.add_argument('--start-date', help='自定义开始日期 YYYY-MM-DD')
    parser.add_argument('--end-date', help='自定义结束日期 YYYY-MM-DD')
    args = parser.parse_args()

    if args.start_date and args.end_date:
        start = datetime.fromisoformat(args.start_date).replace(tzinfo=CST)
        end = datetime.fromisoformat(args.end_date).replace(tzinfo=CST)
        week_label = f"{start.strftime('%-m/%-d')}-{end.strftime('%-m/%-d')}"
        iso_week = start.strftime('%Y-W%W')
    else:
        start, end, week_label = get_week_range(args.week)
        iso_week = start.strftime('%Y-W%W')

    print(f"📅 生成周报：{week_label}（{start.date()} ~ {end.date()}）")

    all_entries = []
    for feed in FEEDS:
        print(f"  抓取 {feed['name']}...", end=" ")
        try:
            xml = fetch_feed(feed['url'])
            entries = parse_entries(xml, start, end, feed)
            print(f"{len(entries)} 篇")
            all_entries.extend(entries)
        except Exception as e:
            print(f"❌ 失败: {e}")

    print(f"\n✅ 共收录 {len(all_entries)} 篇文章")

    if not all_entries:
        print("⚠️  本周无文章，跳过生成")
        return

    html = build_html(all_entries, week_label)
    report_dir = ROOT / "docs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    week_slug = iso_week.replace(':', '-')
    filename = f"{week_slug}.html"
    (report_dir / filename).write_text(html)
    print(f"📄 周报已生成：docs/reports/{filename}")

    update_index(filename, week_label, len(all_entries))
    print("🏠 首页已更新")

if __name__ == "__main__":
    main()
