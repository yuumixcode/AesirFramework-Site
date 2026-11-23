#!/usr/bin/env python3
"""从旧站最后一次成功构建产物 site/ 生成全路径跳转版 redirect/。

文档站 2026-11-23 并入主仓（https://yuumixcode.github.io/AesirFramework/）。
GitHub Pages 无服务端 301 能力，用 meta refresh + canonical 保存量深链与搜索权重。
用法（旧仓根运行）：python3 tools/make-redirects.py [siteDir] [outDir]
"""

import html
import re
import sys
from pathlib import Path

NEW_BASE = "https://yuumixcode.github.io/AesirFramework/"
SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "redirect")

TEMPLATE = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
<title>{title}</title>
</head>
<body>
<p>本页已迁移：<a href="{url}">{url}</a></p>
<p>AesirFramework 文档站已于 2026-11-23 并入框架主仓，旧地址仅作跳转保留。</p>
</body>
</html>
"""


def new_url(rel: str) -> str:
    # 目录型 URL：去掉尾段 index.html，与_new_站 use_directory_urls 结构对齐
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return NEW_BASE + rel


def main() -> None:
    if not SITE.is_dir():
        sys.exit(f"构建产物目录不存在: {SITE}（先在旧仓跑 zensical build）")
    count = 0
    for src in sorted(SITE.rglob("*.html")):
        rel = src.relative_to(SITE).as_posix()
        url = new_url(rel)
        m = re.search(r"<title>(.*?)</title>", src.read_text(encoding="utf-8"), re.S)
        title = html.escape(m.group(1).strip()) if m else "AesirFramework"
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(TEMPLATE.format(url=url, title=title), encoding="utf-8")
        count += 1
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    print(f"generated {count} redirect pages -> {OUT}/")


if __name__ == "__main__":
    main()