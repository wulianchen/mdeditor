"""
PyInstaller 打包脚本 - PyQt6版本
使用方法: python build_exe.py
"""
import PyInstaller.__main__
import os
from PIL import Image

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将 icon.png 转换为 icon_for_exe.ico（用于 exe 窗口图标）
# 优先使用优化后的 icon_optimized.png（如果存在）
png_path = os.path.join(current_dir, 'icon_optimized.png')
if not os.path.exists(png_path):
    png_path = os.path.join(current_dir, 'icon.png')

ico_path = os.path.join(current_dir, 'icon_for_exe.ico')

if os.path.exists(png_path):
    print(f"正在将 {os.path.basename(png_path)} 转换为 icon_for_exe.ico...")
    img = Image.open(png_path)
    
    # 确保是 RGBA 模式（带透明通道）
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 保存为多尺寸的 ico 文件，保持透明度
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"✓ 图标转换完成: {ico_path}")
    print(f"  - 源文件: {os.path.basename(png_path)}")
    print(f"  - 原始尺寸: {Image.open(png_path).size}")
    print(f"  - 包含尺寸: {sizes}")
    print(f"  - 透明度: 已保留")
else:
    print(f"✗ 找不到 icon.png 或 icon_optimized.png 文件")
    exit(1)

# PyInstaller 参数
args = [
    'main.py',  # 主程序文件（PyQt6版本）
    '--name=快乐马MarkDown编辑器',  # 生成的exe名称
    '--onedir',  # 打包成目录结构（而非单文件）
    '--windowed',  # 无控制台窗口（GUI应用）
    '--icon=icon_for_exe.ico',  # 使用从 PNG 转换的 ICO 图标
    '--add-data=icon.ico;.',  # 将原始icon.ico添加到根目录
    '--add-data=docs/产品简介.pdf;docs',  # 添加产品简介PDF
    '--add-data=docs/技术白皮书.pdf;docs',  # 添加技术白皮书PDF
    '--add-data=docs/版权声明.pdf;docs',  # 添加版权声明PDF
    '--add-data=全标签测试文档.md;.',  # 添加全标签测试文档（根目录）
    '--add-data=全标签测试文档-复杂标签和数学.md;.',  # 添加复杂标签测试文档（根目录）
    '--add-data=docs/运行环境要求.pdf;.',  # 添加运行环境要求PDF（根目录）
    '--add-data=editor_config.json;.',  # 添加配置文件
    '--add-data=images;images',  # 添加images目录及所有子文件
    '--add-data=导出示例;导出示例',  # 添加导出示例目录及所有内容
    '--noconfirm',  # 不询问确认
    f'--distpath={os.path.join(current_dir, "dist")}',  # 输出目录
    f'--workpath={os.path.join(current_dir, "build")}',  # 工作目录
    f'--specpath={current_dir}',  # spec文件目录
    '--hidden-import=PyQt6.sip',  # 隐藏导入
    '--hidden-import=PyQt6.QtWebEngineWidgets',  # 隐藏导入WebEngine
    '--hidden-import=markdown',  # 隐藏导入markdown
    '--collect-all=PyQt6.QtCore',  # 收集QtCore
    '--collect-all=PyQt6.QtGui',  # 收集QtGui
    '--collect-all=PyQt6.QtWidgets',  # 收集QtWidgets
    '--collect-all=PyQt6.QtWebEngineWidgets',  # 收集所有WebEngine相关文件
    '--collect-all=PyQt6.QtWebEngineCore',  # 收集WebEngineCore
]

print("开始打包 Markdown编辑器 (PyQt6版本)...")
print(f"打包参数: {' '.join(args)}")
print("-" * 50)

PyInstaller.__main__.run(args)

print("-" * 50)
print("打包完成！")
print(f"可执行文件位于: {os.path.join(current_dir, 'dist', '快乐马MarkDown编辑器', '快乐马MarkDown编辑器.exe')}")
print("")

# 复制测试文件到 exe 平级目录，便于用户测试
import shutil
dist_dir = os.path.join(current_dir, 'dist', '快乐马MarkDown编辑器')

# 创建 docs 目录
docs_dir = os.path.join(dist_dir, 'docs')
if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)
    print(f"✓ 已创建: docs/ 目录")

# 【关键】从 _internal/docs 复制 PDF 文件到根目录的 docs 文件夹
internal_docs_dir = os.path.join(dist_dir, '_internal', 'docs')
pdf_files = ['产品简介.pdf', '技术白皮书.pdf', '版权声明.pdf']

for pdf_file in pdf_files:
    src_pdf = os.path.join(internal_docs_dir, pdf_file)
    dst_pdf = os.path.join(docs_dir, pdf_file)
    if os.path.exists(src_pdf):
        shutil.copy2(src_pdf, dst_pdf)
        print(f"✓ 已复制: {pdf_file} -> docs/")
    else:
        print(f"✗ 源文件不存在: {src_pdf}")

# 复制全标签测试文档.md
src_md = os.path.join(current_dir, '全标签测试文档.md')
dst_md = os.path.join(dist_dir, '全标签测试文档.md')
if os.path.exists(src_md):
    shutil.copy2(src_md, dst_md)
    print(f"✓ 已复制: 全标签测试文档.md -> {dist_dir}")
else:
    print(f"✗ 源文件不存在: {src_md}")

# 复制全标签测试文档-复杂标签和数学.md
src_md2 = os.path.join(current_dir, '全标签测试文档-复杂标签和数学.md')
dst_md2 = os.path.join(dist_dir, '全标签测试文档-复杂标签和数学.md')
if os.path.exists(src_md2):
    shutil.copy2(src_md2, dst_md2)
    print(f"✓ 已复制: 全标签测试文档-复杂标签和数学.md -> {dist_dir}")
else:
    print(f"✗ 源文件不存在: {src_md2}")

# 【关键】从 _internal 复制 images 目录到根目录
internal_images = os.path.join(dist_dir, '_internal', 'images')
dst_images = os.path.join(dist_dir, 'images')
if os.path.exists(internal_images):
    if os.path.exists(dst_images):
        shutil.rmtree(dst_images)
    shutil.copytree(internal_images, dst_images)
    print(f"✓ 已复制: images/ -> {dist_dir}/images/ (从 _internal)")
else:
    print(f"✗ 源目录不存在: {internal_images}")

# 【关键】从 _internal 复制 导出示例 目录到根目录
internal_export_examples = os.path.join(dist_dir, '_internal', '导出示例')
dst_export_examples = os.path.join(dist_dir, '导出示例')
if os.path.exists(internal_export_examples):
    if os.path.exists(dst_export_examples):
        shutil.rmtree(dst_export_examples)
    shutil.copytree(internal_export_examples, dst_export_examples)
    print(f"✓ 已复制: 导出示例/ -> {dist_dir}/导出示例/ (从 _internal)")
else:
    print(f"✗ 源目录不存在: {internal_export_examples}")

# 复制 editor_config.json
src_config = os.path.join(current_dir, 'editor_config.json')
dst_config = os.path.join(dist_dir, 'editor_config.json')
if os.path.exists(src_config):
    shutil.copy2(src_config, dst_config)
    print(f"✓ 已复制: editor_config.json -> {dist_dir}")
else:
    print(f"✗ 源文件不存在: {src_config}")

# 复制运行环境要求.pdf到根目录（PyInstaller onedir模式会将 --add-data 文件放入 _internal 目录）
src_pdf_internal = os.path.join(dist_dir, '_internal', '运行环境要求.pdf')
src_pdf_docs = os.path.join(current_dir, 'docs', '运行环境要求.pdf')
dst_pdf = os.path.join(dist_dir, '运行环境要求.pdf')

if os.path.exists(src_pdf_internal):
    # 从 _internal 目录复制到根目录
    shutil.copy2(src_pdf_internal, dst_pdf)
    print(f"✓ 已复制: 运行环境要求.pdf -> {dist_dir} (从 _internal)")
elif os.path.exists(src_pdf_docs):
    # 直接从源 docs 目录复制
    shutil.copy2(src_pdf_docs, dst_pdf)
    print(f"✓ 已复制: 运行环境要求.pdf -> {dist_dir} (从源 docs)")
else:
    print(f"⚠ 运行环境要求.pdf 未找到")

print("")
print("注意：要使Markdown文件默认用此程序打开，请右键.md文件 -> 属性 -> 更改打开方式 -> 选择上面的exe文件")
