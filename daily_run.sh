#!/usr/bin/env zsh

# =============================================================================
# 自动刷新 HTML 预览链接并推送到远程仓库
# 使用方式: ./refresh_and_push.zsh
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查当前目录是否是 git 仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "当前目录不是一个 git 仓库"
    exit 1
fi

print_info "检查新的未追踪 HTML 文件..."

# 获取未追踪的 HTML 文件列表
untracked_files=$(git ls-files --others --exclude-standard -- "*.html")

if [[ -z "$untracked_files" ]]; then
    print_warning "没有发现新的未追踪 HTML 文件"
    exit 0
fi

print_success "发现新的 HTML 文件:"
echo "$untracked_files" | while read file; do
    echo "  - $file"
done

# 运行脚本生成预览链接
print_info "运行链接生成脚本..."

if [[ -f "refresh_preview_links.py" ]]; then
    python3 refresh_preview_links.py
else
    print_error "未找到链接生成脚本（refresh_preview_links.py）"
    exit 1
fi

# 检查 README.md 是否有更新
if git diff --quiet README.md 2>/dev/null; then
    print_warning "README.md 没有发生变化"
else
    print_success "README.md 已更新"
fi

# 获取当前日期用于 commit message
current_date=$(date +"%Y/%m/%d")
commit_message="feat: add daily AI pulse for ${current_date}"

# 添加所有变更到 git
print_info "添加文件到 git..."
git add -A

# 提交变更
print_info "提交变更..."
echo "Commit message: ${commit_message}"
git commit -m "${commit_message}"

print_success "已提交到本地仓库"

# 推送到远程仓库
print_info "推送到远程仓库..."
git push origin $(git branch --show-current)

print_success "成功推送到远程仓库！"
echo ""
echo -e "${GREEN}✅ 完成！${NC}"
echo "   - 新的 HTML 文件已添加到 git"
echo "   - README.md 已更新，包含新的预览链接"
echo "   - 所有变更已提交并推送到远程"
