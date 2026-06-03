#!/usr/bin/env python3
"""
自动生成 README.md 中的 HTML 预览链接
扫描仓库中的所有 HTML 文件，并生成对应的 GitHub Pages 预览链接
"""

import os
import re
from pathlib import Path
from datetime import datetime

# 配置
BASE_URL = "https://HLoyal.github.io/ai_daily_pulse/"
README_PATH = Path("README.md")
LINKS_SECTION_MARKER = "<!-- HTML_LINKS_START -->"
LINKS_SECTION_END_MARKER = "<!-- HTML_LINKS_END -->"


def find_html_files():
    """查找所有 HTML 文件，按文件名排序"""
    html_files = []
    for file_path in Path(".").rglob("*.html"):
        # 排除常见的非项目目录
        if any(part.startswith((".", "_")) for part in file_path.parts[:-1]):
            continue
        html_files.append(file_path)
    return sorted(html_files, key=lambda x: x.name, reverse=True)


def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    # 尝试匹配 ai_daily_tech_pulse_2026_06_03.html 格式
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"
    return None


def generate_links_section(html_files):
    """生成链接部分的 Markdown 内容"""
    if not html_files:
        return f"{LINKS_SECTION_MARKER}\n\n> 暂无 HTML 文件\n\n{LINKS_SECTION_END_MARKER}"

    lines = [LINKS_SECTION_MARKER, ""]
    lines.append("## 📱 HTML 预览链接")
    lines.append("")
    lines.append("| 日期 | 文件名 | 预览链接 |")
    lines.append("|------|--------|----------|")

    for file_path in html_files:
        filename = file_path.name
        date_str = extract_date_from_filename(filename) or "-"
        full_url = f"{BASE_URL}{filename}"
        lines.append(f"| {date_str} | `{filename}` | [👉 点击预览]({full_url}) |")

    lines.append("")
    lines.append(f"*最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append(LINKS_SECTION_END_MARKER)

    return "\n".join(lines)


def update_readme(links_section):
    """更新 README.md 文件"""
    if not README_PATH.exists():
        # 创建新的 README.md
        content = f"# AI Daily Pulse\n\n{links_section}\n"
    else:
        content = README_PATH.read_text(encoding="utf-8")

        # 检查是否已存在链接部分
        if LINKS_SECTION_MARKER in content and LINKS_SECTION_END_MARKER in content:
            # 替换现有部分
            pattern = f"{re.escape(LINKS_SECTION_MARKER)}.*?{re.escape(LINKS_SECTION_END_MARKER)}"
            content = re.sub(pattern, links_section, content, flags=re.DOTALL)
        else:
            # 在文件末尾添加
            content = content.rstrip() + "\n\n" + links_section + "\n"

    README_PATH.write_text(content, encoding="utf-8")
    print(f"✅ README.md 已更新")


def main():
    print("🔍 扫描 HTML 文件...")
    html_files = find_html_files()
    print(f"📄 找到 {len(html_files)} 个 HTML 文件")

    print("🔗 生成链接...")
    links_section = generate_links_section(html_files)

    print("📝 更新 README.md...")
    update_readme(links_section)

    print("\n✨ 完成！预览链接已添加到 README.md")
    print(f"🌐 基础 URL: {BASE_URL}")


if __name__ == "__main__":
    main()
