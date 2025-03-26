# coding=UTF-8
# 本更新脚本以
import os
import subprocess
import shutil
from datetime import datetime

# 常量
DEFAULT_REPO_URL = "https://github.com/xinnan-tech/xiaozhi-esp32-server.git"

def get_github_proxy_urls():
    """返回GitHub镜像代理地址列表"""
    return [
        "https://ghfast.top",
        "https://gh.ddlc.top",
        "https://slink.ltd",
        "https://cors.isteed.cc",
        "https://hub.gitmirror.com",
        "https://sciproxy.com",
        "https://ghproxy.net",
        "https://gitclone.com",
        "https://hub.incept.pw",
        "https://github.moeyy.xyz",
        "https://dl.ghpig.top",
        "https://gh-proxy.com",
        "https://hub.whtrys.space",
        "https://gh-proxy.ygxz.in"
    ]

def run_git_command(git_path, args):
    """执行 Git 命令并实时显示输出"""
    process = subprocess.Popen(
        [git_path] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    output_lines = []
    print(f"\n执行命令: git {' '.join(args)}")
    print("-" * 60)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            cleaned = output.strip()
            print(cleaned)
            output_lines.append(cleaned)
    print("-" * 60)
    return process.poll(), '\n'.join(output_lines)

def select_proxy_url():
    """用户选择代理地址"""
    proxies = get_github_proxy_urls()
    print("\n可用GitHub代理地址：")
    for i, url in enumerate(proxies, 1):
        print(f"{i}. {url}")
    while True:
        choice = input("\n请选择代理地址编号（留空取消代理）: ").strip()
        if not choice:
            return None
        try:
            index = int(choice) - 1
            return proxies[index]
        except (ValueError, IndexError):
            print("输入无效，请重新输入！")

def get_pull_mode():
    """选择拉取模式"""
    print("\n请选择拉取方式：")
    print("1. 普通拉取（保留本地修改）")
    print("2. 强制拉取（覆盖所有修改）")
    while True:
        choice = input("请输入选项（1/2）: ").strip()
        if choice in ('1', '2'):
            return 'normal' if choice == '1' else 'force'
        print("输入无效，请重新输入！")

def backup_config(script_dir):
    """备份配置文件"""
    data_dir = os.path.join(script_dir, "src", "main", "xiaozhi-server", "data")
    
    # 检查配置文件目录是否存在
    if not os.path.exists(data_dir):
        print(f"\n⚠️ 未找到配置文件目录：{data_dir}")
        return False
    
    if not os.path.exists(os.path.join(data_dir, ".config.yaml")):
        print("\n⚠️ 未找到配置文件，已取消备份")
        return False
    
    backup_dir = os.path.join(script_dir, "backup", f"backup_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    try:
        shutil.copytree(data_dir, backup_dir)
        print(f"\n✅ 已帮你备份好配置文件：{backup_dir}")
        return True
    except Exception as e:
        print(f"\n❌ 备份失败：{str(e)}")
        return False

def main():
    # 初始化路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    git_path = os.path.join(script_dir, "runtime", "git-2.48.1", "cmd", "git.exe")
    src_dir = os.path.join(script_dir, "src")

    # 环境检查
    if not os.path.exists(git_path):
        print(f"[ERROR] 未找到Git程序：{git_path}")
        input("按 Enter 退出...")
        return

    try:
        os.chdir(src_dir)
        print("小智AI服务端更新脚本 Ver 1.0")
        print(f"当前工作目录：{src_dir}")
    except Exception as e:
        print(f"[ERROR] 目录切换失败：{str(e)}")
        input("按 Enter 退出...")
        return

    # 代理设置流程
    use_proxy = input("\n是否设置GitHub代理？（留空或输入非y为不设置）(y/n): ").lower() == 'y'

    try:
        if use_proxy:
            proxy_url = select_proxy_url()
            if proxy_url:
                # 拼接代理地址
                new_url = f"{proxy_url.rstrip('/')}/{DEFAULT_REPO_URL}"
                print(f"\n设置代理地址：{new_url}")
                run_git_command(git_path, ["remote", "set-url", "origin", new_url])
            else:
                reset = input("是否重置为默认地址？(y/n): ").lower() == 'y'
                if reset:
                    print(f"\n重置为默认地址：{DEFAULT_REPO_URL}")
                    run_git_command(git_path, ["remote", "set-url", "origin", DEFAULT_REPO_URL])
                else:
                    print("未输入内容，已取消重置操作")

        # 拉取操作
        pull_mode = get_pull_mode()
        
        if pull_mode == 'normal':
            code, output = run_git_command(git_path, ["pull"])
            if code == 0:
                print("\n✅ 拉取成功，建议同步完成后运行该目录下的一键更新依赖批处理进行依赖更新。" if "Already up" not in output else "\n🎉 恭喜，你本地的代码已经是最新版本！")
            else:
                print("\n❌ 拉取失败，请检查日志")
        else:
            print("\n警告⚠️： 强制拉取将覆盖所有本地修改！")
            if input("你确认要强制拉取吗？请输入“确认强制拉取”确认操作：") == "确认强制拉取":
                # 尝试备份并执行强制拉取
                backup_success = backup_config(script_dir)
                if not backup_success:
                    print("\n⚠️ 注意：配置文件未备份，继续执行强制拉取！")
                
                print("\n正在强制同步...")
                run_git_command(git_path, ["fetch", "--all"])
                run_git_command(git_path, ["reset", "--hard", "origin/main"])
                print("\n🎉 强制同步完成！建议同步完成后运行该目录下的一键更新依赖批处理进行依赖更新。")
            else:
                print("\n⛔ 输入无效，已取消强制拉取操作")

    finally:
        # 显示最终远程地址
        print("\n当前远程地址：")
        run_git_command(git_path, ["remote", "-v"])

    input("\n操作完成，按 Enter 退出...")

if __name__ == "__main__":
    main()