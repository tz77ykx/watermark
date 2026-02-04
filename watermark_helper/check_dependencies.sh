#!/bin/bash
# 依赖检查脚本

echo "=========================================="
echo "PDF 水印工具 - 依赖检查"
echo "=========================================="
echo ""

# 检查 Python
echo "1. 检查 Python"
echo "----------------------------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 未安装"
fi
echo ""

# 检查 pip
echo "2. 检查 pip"
echo "----------------------------------------"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo "✅ pip $PIP_VERSION"
else
    echo "❌ pip3 未安装"
fi
echo ""

# 检查 Python 包
echo "3. 检查 Python 包"
echo "----------------------------------------"
python3 -c "
import sys

packages = [
    'streamlit',
    'pdf2image',
    'PIL',
    'numpy',
    'cv2',
    'pandas',
    'openpyxl'
]

for pkg in packages:
    try:
        if pkg == 'PIL':
            __import__('PIL')
            import PIL
            print(f'✅ Pillow {PIL.__version__}')
        elif pkg == 'cv2':
            __import__('cv2')
            import cv2
            print(f'✅ opencv-python {cv2.__version__}')
        else:
            mod = __import__(pkg)
            version = getattr(mod, '__version__', '未知版本')
            print(f'✅ {pkg} {version}')
    except ImportError:
        print(f'❌ {pkg} 未安装')
" 2>&1
echo ""

# 检查 Homebrew
echo "4. 检查 Homebrew"
echo "----------------------------------------"
if command -v brew &> /dev/null; then
    BREW_VERSION=$(brew --version | head -1)
    echo "✅ $BREW_VERSION"
else
    echo "❌ Homebrew 未安装"
    echo "   安装命令: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
fi
echo ""

# 检查 poppler
echo "5. 检查 poppler（PDF 处理工具）"
echo "----------------------------------------"
if command -v pdftoppm &> /dev/null; then
    POPPLER_LOC=$(which pdftoppm)
    POPPLER_VER=$(pdftoppm -v 2>&1 | head -1)
    echo "✅ poppler 已安装"
    echo "   位置: $POPPLER_LOC"
    echo "   版本: $POPPLER_VER"
else
    echo "❌ poppler 未安装"
    echo "   这是导致 'Unable to get page count' 错误的原因"
    echo ""
    echo "   安装方法："
    echo "   1. 运行自动安装脚本: ./install_poppler.sh"
    echo "   2. 或手动安装: brew install poppler"
fi
echo ""

# 检查 poppler 的其他命令
if command -v pdftoppm &> /dev/null; then
    echo "   poppler 工具："
    for cmd in pdftoppm pdfinfo pdftocairo pdftotext; do
        if command -v $cmd &> /dev/null; then
            echo "   ✅ $cmd"
        else
            echo "   ⚠️  $cmd (可选)"
        fi
    done
    echo ""
fi

# 测试 pdf2image
echo "6. 测试 pdf2image 功能"
echo "----------------------------------------"
python3 -c "
try:
    from pdf2image import convert_from_bytes
    print('✅ pdf2image 可以正常使用')
    print('   可以处理 PDF 文件')
except Exception as e:
    print('❌ pdf2image 无法使用')
    print(f'   错误: {str(e)}')
    if 'poppler' in str(e).lower():
        print('   原因: 缺少 poppler 工具')
        print('   解决: 运行 ./install_poppler.sh')
" 2>&1
echo ""

# 总结
echo "=========================================="
echo "依赖检查总结"
echo "=========================================="
echo ""

# 统计
python3 -c "
import sys
import subprocess

missing = []

# 检查关键依赖
checks = [
    ('Python 3', 'python3 --version'),
    ('Homebrew', 'brew --version'),
    ('poppler', 'pdftoppm -v'),
]

for name, cmd in checks:
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    if result.returncode != 0:
        missing.append(name)

# 检查 Python 包
packages = ['streamlit', 'pdf2image', 'PIL', 'numpy', 'cv2', 'pandas']
for pkg in packages:
    try:
        __import__(pkg if pkg != 'PIL' else 'PIL')
    except ImportError:
        missing.append(f'Python 包: {pkg}')

if not missing:
    print('✅ 所有依赖都已安装，可以正常使用！')
    print('')
    print('运行应用：')
    print('  streamlit run app.py')
else:
    print('⚠️  缺少以下依赖：')
    for item in missing:
        print(f'  - {item}')
    print('')
    print('请按照上面的提示安装缺少的依赖。')
    print('')
    if 'poppler' in missing or any('poppler' in str(m).lower() for m in missing):
        print('关键问题：poppler 未安装')
        print('快速解决：运行 ./install_poppler.sh')
" 2>&1

echo ""
