#!/bin/bash
# Streamlit 应用重启脚本

echo "=================================================="
echo "Streamlit 应用重启脚本"
echo "=================================================="
echo ""

# 检查是否有 Streamlit 在运行
echo "1. 检查运行中的 Streamlit 进程..."
STREAMLIT_PID=$(pgrep -f "streamlit run")

if [ ! -z "$STREAMLIT_PID" ]; then
    echo "   发现运行中的 Streamlit (PID: $STREAMLIT_PID)"
    echo "   正在停止..."
    kill $STREAMLIT_PID
    sleep 2
    echo "   ✅ 已停止"
else
    echo "   没有运行中的 Streamlit 进程"
fi

echo ""
echo "2. 清除 Streamlit 缓存..."
streamlit cache clear
echo "   ✅ 缓存已清除"

echo ""
echo "3. 验证模块更新..."
python3 -c "
import image_processor
print('   检查 generate_map_reference:', '✅' if hasattr(image_processor, 'generate_map_reference') else '❌')
print('   检查 buyer_id 参数:', '✅' if 'buyer_id' in image_processor.process_pdf.__code__.co_varnames else '❌')
print('   检查 add_spatial_tracking:', '✅' if hasattr(image_processor, 'add_spatial_tracking') else '❌')
"

echo ""
echo "4. 启动 Streamlit 应用..."
echo ""
echo "=================================================="
echo "应用正在启动，请在浏览器中访问显示的 URL"
echo "=================================================="
echo ""

streamlit run app.py
