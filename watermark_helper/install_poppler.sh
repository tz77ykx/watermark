#!/bin/bash
# Poppler 自动安装脚本（macOS）

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Poppler 自动安装脚本"
echo "=========================================="
echo ""

# 检查是否为 macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此脚本仅适用于 macOS"
    exit 1
fi

# 检查是否已安装 poppler
if command -v pdftoppm &> /dev/null; then
    echo "✅ poppler 已经安装"
    echo "   位置: $(which pdftoppm)"
    echo "   版本: $(pdftoppm -v 2>&1 | head -1)"
    echo ""
    echo "无需重复安装，可以直接使用应用。"
    exit 0
fi

echo "检测到 poppler 未安装，开始安装..."
echo ""

# 检查是否安装了 Homebrew
if ! command -v brew &> /dev/null; then
    echo "=========================================="
    echo "步骤 1: 安装 Homebrew"
    echo "=========================================="
    echo ""
    echo "Homebrew 是 macOS 的包管理器，用于安装各种工具。"
    echo "这是首次安装，可能需要 5-15 分钟。"
    echo ""
    read -p "是否继续安装 Homebrew？(y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消安装。"
        exit 1
    fi

    echo ""
    echo "正在安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # 添加到 PATH
    if [ -d "/opt/homebrew" ]; then
        echo ""
        echo "添加 Homebrew 到 PATH (Apple Silicon)..."
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo ""
        echo "添加 Homebrew 到 PATH (Intel)..."
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    echo "✅ Homebrew 安装完成"
    echo ""
else
    echo "✅ Homebrew 已安装: $(brew --version | head -1)"
    echo ""
fi

# 安装 poppler
echo "=========================================="
echo "步骤 2: 安装 poppler"
echo "=========================================="
echo ""
echo "正在安装 poppler（PDF 处理工具）..."
echo "这可能需要 2-5 分钟..."
echo ""

brew install poppler

echo ""
echo "✅ poppler 安装完成"
echo ""

# 验证安装
echo "=========================================="
echo "步骤 3: 验证安装"
echo "=========================================="
echo ""

if command -v pdftoppm &> /dev/null; then
    echo "✅ pdftoppm 命令可用"
    echo "   位置: $(which pdftoppm)"
fi

if command -v pdfinfo &> /dev/null; then
    echo "✅ pdfinfo 命令可用"
    echo "   位置: $(which pdfinfo)"
fi

if command -v pdftocairo &> /dev/null; then
    echo "✅ pdftocairo 命令可用"
    echo "   位置: $(which pdftocairo)"
fi

echo ""

# 测试 pdf2image
echo "测试 pdf2image 库..."
python3 -c "
try:
    from pdf2image import convert_from_bytes
    print('✅ pdf2image 可以使用了')
except ImportError:
    print('⚠️  pdf2image 库未安装')
    print('   请运行: pip3 install pdf2image')
except Exception as e:
    print('❌ 发生错误:', str(e))
" 2>&1

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "现在可以运行应用了："
echo ""
echo "  streamlit run app.py"
echo ""
echo "如果仍然报错，请重新打开终端窗口，以确保 PATH 生效。"
echo ""
