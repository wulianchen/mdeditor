"""
系统兼容性检测脚本
用于检查当前系统是否满足 Markdown 编辑器的运行要求
"""
import sys
import os
import platform
import subprocess


def check_python_version():
    """检查 Python 版本"""
    print("=" * 60)
    print("1. Python 版本检查")
    print("=" * 60)
    
    version = sys.version_info
    print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python 版本符合要求 (≥ 3.8)")
        return True
    else:
        print("❌ Python 版本过低，需要 ≥ 3.8")
        return False


def check_os_compatibility():
    """检查操作系统兼容性"""
    print("\n" + "=" * 60)
    print("2. 操作系统检查")
    print("=" * 60)
    
    os_name = platform.system()
    os_version = platform.version()
    arch = platform.architecture()[0]
    
    print(f"操作系统: {os_name}")
    print(f"版本: {os_version}")
    print(f"架构: {arch}")
    
    if os_name == "Windows":
        win_version = platform.win32_ver()[0]
        print(f"Windows 版本: {win_version}")
        
        # 检查是否为 64 位
        if arch == "64bit":
            print("✅ 64位 Windows 系统")
            
            # 检查 Windows 版本
            if win_version in ["7", "8", "8.1", "10", "11"]:
                print(f"✅ Windows {win_version} 受支持")
                return True
            else:
                print(f"⚠️  Windows {win_version} 未经验证，可能存在问题")
                return False
        else:
            print("❌ 不支持 32 位系统")
            return False
    else:
        print(f"❌ 不支持 {os_name} 系统，目前仅支持 Windows")
        return False


def check_dependencies():
    """检查依赖库"""
    print("\n" + "=" * 60)
    print("3. 依赖库检查")
    print("=" * 60)
    
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("PyQt6-WebEngine", "PyQt6.QtWebEngineWidgets"),
        ("markdown", "markdown"),
        ("PyMuPDF", "fitz"),
        ("Pillow", "PIL"),
    ]
    
    all_ok = True
    
    for name, module_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {name:20s} - 已安装")
        except ImportError as e:
            print(f"❌ {name:20s} - 未安装 ({e})")
            all_ok = False
    
    return all_ok


def check_vc_redist():
    """检查 Visual C++ Redistributable"""
    print("\n" + "=" * 60)
    print("4. Visual C++ 运行时检查")
    print("=" * 60)
    
    # 检查常见的 VC++ DLL
    vc_dlls = [
        "vcruntime140.dll",
        "msvcp140.dll",
    ]
    
    import ctypes
    
    all_found = True
    for dll in vc_dlls:
        try:
            ctypes.CDLL(dll)
            print(f"✅ {dll:20s} - 已找到")
        except OSError:
            print(f"⚠️  {dll:20s} - 未找到（可能需要安装 VC++ Redistributable）")
            all_found = False
    
    if not all_found:
        print("\n建议下载安装:")
        print("https://aka.ms/vs/17/release/vc_redist.x64.exe")
    
    return all_found


def check_gpu_opengl():
    """检查显卡和 OpenGL 支持"""
    print("\n" + "=" * 60)
    print("5. 显卡和 OpenGL 检查")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QOpenGLContext
        
        app = QApplication(sys.argv)
        
        # 检查 OpenGL 支持
        context = QOpenGLContext()
        if context.create():
            print("✅ OpenGL 上下文创建成功")
            
            # 获取 OpenGL 版本信息
            surface = context.surface()
            if surface:
                print("✅ 表面创建成功")
            else:
                print("⚠️  无法创建表面，可能影响渲染")
        else:
            print("❌ OpenGL 上下文创建失败")
            print("   这可能导致 QtWebEngine 无法正常工作")
            return False
        
        del app
        return True
        
    except Exception as e:
        print(f"⚠️  无法检查 OpenGL: {e}")
        print("   请确保显卡驱动已更新")
        return False


def check_disk_space():
    """检查磁盘空间"""
    print("\n" + "=" * 60)
    print("6. 磁盘空间检查")
    print("=" * 60)
    
    try:
        # 获取程序所在磁盘的可用空间
        drive = os.path.splitdrive(os.path.abspath(__file__))[0] + "\\"
        
        if os.name == 'nt':  # Windows
            import shutil
            total, used, free = shutil.disk_usage(drive)
            
            free_gb = free / (1024 ** 3)
            print(f"驱动器: {drive}")
            print(f"可用空间: {free_gb:.2f} GB")
            
            if free_gb > 1:
                print("✅ 磁盘空间充足")
                return True
            else:
                print("⚠️  磁盘空间不足，建议清理至少 1GB 空间")
                return False
        else:
            print("⚠️  无法检查磁盘空间（非 Windows 系统）")
            return True
            
    except Exception as e:
        print(f"⚠️  无法检查磁盘空间: {e}")
        return True


def check_firewall_antivirus():
    """检查防火墙和杀毒软件（提示性检查）"""
    print("\n" + "=" * 60)
    print("7. 安全软件提示")
    print("=" * 60)
    
    print("⚠️  以下安全软件可能影响程序运行:")
    print("   - Windows Defender")
    print("   - 第三方杀毒软件（360、腾讯电脑管家等）")
    print("   - 企业防火墙")
    print("\n建议:")
    print("   1. 将程序目录添加到杀毒软件白名单")
    print("   2. 允许 QtWebEngineProcess.exe 通过防火墙")
    print("   3. 如遇问题，临时关闭杀毒软件测试")


def generate_report(results):
    """生成检测报告"""
    print("\n" + "=" * 60)
    print("📊 检测报告总结")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"总检查项: {total}")
    print(f"通过: {passed}")
    print(f"未通过: {total - passed}")
    print()
    
    if passed == total:
        print("✅ 所有检查项通过！您的系统可以运行 Markdown 编辑器")
        print("\n建议:")
        print("   - 首次启动可能需要几秒加载时间")
        print("   - 如遇问题，请查看 error.log 文件")
    elif passed >= total * 0.7:
        print("⚠️  大部分检查项通过，但存在潜在风险")
        print("\n建议:")
        print("   - 尝试运行程序，观察是否有问题")
        print("   - 如出现闪退，请检查未通过的项")
    else:
        print("❌ 多项检查未通过，不建议运行")
        print("\n建议:")
        print("   - 先解决未通过的问题")
        print("   - 考虑升级系统或硬件")
    
    print("\n详细日志已保存到: compatibility_check.log")
    
    # 保存报告到文件
    with open("compatibility_check.log", "w", encoding="utf-8") as f:
        f.write("Markdown 编辑器 - 系统兼容性检测报告\n")
        f.write(f"检测时间: {platform.uname()}\n")
        f.write(f"Python 版本: {sys.version}\n")
        f.write("=" * 60 + "\n\n")
        
        for check_name, result in results.items():
            status = "✅ 通过" if result else "❌ 未通过"
            f.write(f"{check_name}: {status}\n")
        
        f.write(f"\n总计: {passed}/{total} 通过\n")


def main():
    """主函数"""
    print("🔍 Markdown 编辑器 - 系统兼容性检测工具")
    print("=" * 60)
    print()
    
    results = {}
    
    # 执行各项检查
    results["Python 版本"] = check_python_version()
    results["操作系统"] = check_os_compatibility()
    results["依赖库"] = check_dependencies()
    results["VC++ 运行时"] = check_vc_redist()
    results["OpenGL 支持"] = check_gpu_opengl()
    results["磁盘空间"] = check_disk_space()
    
    # 提示性检查（不影响结果）
    check_firewall_antivirus()
    
    # 生成报告
    generate_report(results)
    
    print("\n按任意键退出...")
    input()


if __name__ == "__main__":
    main()
