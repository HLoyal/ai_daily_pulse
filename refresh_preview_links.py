#!/usr/bin/env python3
"""
自动生成 README.md 中的 HTML 预览链接
扫描仓库中的所有 HTML 文件，并生成对应的 GitHub Pages 预览链接
文件按年/月/日目录结构存放
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


def extract_date_from_filename(filename):
    """从文件名中提取日期，返回 (year, month, day) 元组或 None"""
    # 匹配格式：YYYY_MM_DD 或 YYYY-MM-DD
    patterns = [
        r'(\d{4})[\-_](\d{2})[\-_](\d{2})',
        r'(\d{4})(\d{2})(\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            year, month, day = match.groups()
            return (year, month, day)
    return None


def organize_html_file(file_path):
    """将 HTML 文件移动到正确的年/月/日目录结构中"""
    filename = file_path.name
    date_parts = extract_date_from_filename(filename)

    if not date_parts:
        print(f"  ⚠️  无法从文件名提取日期: {filename}")
        return file_path

    year, month, day = date_parts
    target_dir = Path(year) / month / day
    target_path = target_dir / filename

    # 如果文件已经在正确的位置，不需要移动
    if file_path == target_path:
        return file_path

    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)

    # 移动文件
    print(f"  📁  {filename} -> {target_path}")
    file_path.rename(target_path)

    return target_path


def find_html_files():
    """查找所有 HTML 文件，按日期排序（最新的在前）"""
    html_files = set()  # 使用集合去重
    for file_path in Path(".").rglob("*.html"):
        # 排除常见的非项目目录
        if any(part.startswith((".", "_")) for part in file_path.parts[:-1]):
            continue

        # 如果文件不在年/月/日目录结构中，尝试移动它
        file_path = organize_html_file(file_path)

        # 获取相对路径（用于生成URL）
        rel_path = file_path.relative_to(Path("."))
        html_files.add(rel_path)

    # 按文件路径排序（包含日期信息）
    return sorted(html_files, key=lambda x: str(x), reverse=True)


def extract_date_from_path(file_path):
    """从文件路径中提取日期"""
    # 首先尝试从文件名中提取日期
    filename = Path(file_path).name
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"
    
    # 尝试从目录结构中提取（年/月/日）
    parts = Path(file_path).parts
    if len(parts) >= 3:
        # 检查是否符合 年/月/日 结构
        year, month, day = parts[-4], parts[-3], parts[-2]
        if year.isdigit() and month.isdigit() and day.isdigit():
            if len(year) == 4 and len(month) == 2 and len(day) == 2:
                return f"{year}-{month}-{day}"
    
    return "-"


def get_file_url(file_path):
    """获取文件的完整URL"""
    # 使用相对路径构建URL
    path_str = str(file_path).replace("\\", "/")
    return f"{BASE_URL}{path_str}"


def generate_links_section(html_files):
    """生成链接部分的 Markdown 内容"""
    if not html_files:
        return f"{LINKS_SECTION_MARKER}\n\n> 暂无 HTML 文件\n\n{LINKS_SECTION_END_MARKER}"

    lines = [LINKS_SECTION_MARKER, ""]
    lines.append("## 📱 HTML 预览链接")
    lines.append("")
    lines.append("文件按 `年/月/日` 目录结构存放，下表按日期倒序排列。")
    lines.append("")
    lines.append("| 日期 | 文件路径 | 预览链接 |")
    lines.append("|------|--------|----------|")

    for file_path in html_files:
        date_str = extract_date_from_path(file_path)
        path_display = str(file_path).replace("\\", "/")
        full_url = get_file_url(file_path)
        lines.append(f"| {date_str} | `{path_display}` | [👉 点击预览]({full_url}) |")

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
