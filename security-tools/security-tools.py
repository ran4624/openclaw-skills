#!/usr/bin/env python3
"""
Security Tools - 安全工具集
"""

import sys
import os
import hashlib
import secrets
import string
import base64
from pathlib import Path
from getpass import getpass

def generate_password(length=16, special=True):
    """生成强密码"""
    try:
        # 定义字符集
        letters = string.ascii_letters  # 大小写字母
        digits = string.digits          # 数字
        
        if special:
            # 包含特殊字符，但排除容易混淆的字符
            special_chars = "!@#$%^&*-_+=.:,"
            alphabet = letters + digits + special_chars
        else:
            alphabet = letters + digits
        
        # 确保至少包含每种类型
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            
            # 检查密码强度
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            if special:
                has_special = any(c in special_chars for c in password)
                if has_lower and has_upper and has_digit and has_special:
                    break
            else:
                if has_lower and has_upper and has_digit:
                    break
        
        # 计算熵
        import math
        entropy = len(password) * math.log2(len(alphabet))
        
        result = [
            "🔐 生成的密码",
            "",
            f"密码: {password}",
            f"长度: {len(password)} 字符",
            f"熵: 约 {entropy} bits",
        ]
        
        if entropy < 50:
            result.append("强度: ⚠️ 弱")
        elif entropy < 80:
            result.append("强度: ✅ 中等")
        else:
            result.append("强度: 🔒 强")
        
        return "\n".join(result)
    except Exception as e:
        return f"生成密码失败: {str(e)}"

def encrypt_file(input_path, output_path=None, password=None):
    """加密文件"""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    except ImportError:
        return "错误: 未安装 cryptography，请运行: pip install cryptography"
    
    try:
        input_path = Path(input_path)
        if not input_path.exists():
            return f"文件不存在: {input_path}"
        
        if output_path is None:
            output_path = str(input_path) + ".enc"
        
        # 获取密码
        if password is None:
            password = getpass("请输入加密密码: ")
            confirm = getpass("请确认密码: ")
            if password != confirm:
                return "错误: 两次输入的密码不一致"
        
        # 生成密钥
        salt = os.urandom(16)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # 加密数据
        f = Fernet(key)
        with open(input_path, 'rb') as file:
            data = file.read()
        
        encrypted = f.encrypt(data)
        
        # 保存（salt + 加密数据）
        with open(output_path, 'wb') as file:
            file.write(salt + encrypted)
        
        return f"加密完成: {output_path}"
    except Exception as e:
        return f"加密失败: {str(e)}"

def decrypt_file(input_path, output_path=None, password=None):
    """解密文件"""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    except ImportError:
        return "错误: 未安装 cryptography"
    
    try:
        input_path = Path(input_path)
        if not input_path.exists():
            return f"文件不存在: {input_path}"
        
        if output_path is None:
            # 移除 .enc 后缀
            output_path = str(input_path).replace('.enc', '.dec')
        
        # 获取密码
        if password is None:
            password = getpass("请输入解密密码: ")
        
        # 读取文件
        with open(input_path, 'rb') as file:
            data = file.read()
        
        # 分离 salt 和加密数据
        salt = data[:16]
        encrypted = data[16:]
        
        # 生成密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # 解密
        f = Fernet(key)
        decrypted = f.decrypt(encrypted)
        
        # 保存
        with open(output_path, 'wb') as file:
            file.write(decrypted)
        
        return f"解密完成: {output_path}"
    except Exception as e:
        return f"解密失败: {str(e)}"

def hash_file(file_path, algorithm=None):
    """计算文件哈希"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return f"文件不存在: {file_path}"
        
        algorithms = {
            'md5': hashlib.md5(),
            'sha1': hashlib.sha1(),
            'sha256': hashlib.sha256(),
            'sha512': hashlib.sha512(),
        }
        
        if algorithm:
            alg = algorithms.get(algorithm.lower())
            if not alg:
                return f"不支持的算法: {algorithm}"
            hashers = [alg]
        else:
            hashers = [hashlib.md5(), hashlib.sha256(), hashlib.sha512()]
        
        # 读取文件并计算哈希
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                for h in hashers:
                    h.update(chunk)
        
        # 输出结果
        result = [f"📊 文件哈希: {file_path}", ""]
        for h in hashers:
            result.append(f"{h.name.upper()}: {h.hexdigest()}")
        
        return "\n".join(result)
    except Exception as e:
        return f"计算哈希失败: {str(e)}"

def hash_string(text, algorithm='sha256'):
    """计算字符串哈希"""
    try:
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512,
        }
        
        h = algorithms.get(algorithm.lower(), hashlib.sha256)()
        h.update(text.encode('utf-8'))
        
        return f"{algorithm.upper()}: {h.hexdigest()}"
    except Exception as e:
        return f"计算哈希失败: {str(e)}"

def list_ssh_keys():
    """列出 SSH 密钥"""
    try:
        ssh_dir = Path.home() / '.ssh'
        
        if not ssh_dir.exists():
            return "未找到 ~/.ssh 目录"
        
        result = ["🔑 SSH 密钥", ""]
        
        # 查找密钥文件
        key_files = list(ssh_dir.glob('id_*'))
        key_files = [f for f in key_files if not f.name.endswith('.pub')]
        
        if not key_files:
            result.append("未找到私钥文件")
        else:
            for key_file in key_files:
                pub_file = key_file.with_suffix(key_file.suffix + '.pub')
                if pub_file.exists():
                    # 读取公钥获取信息
                    with open(pub_file, 'r') as f:
                        pub_content = f.read().strip()
                    parts = pub_content.split()
                    if len(parts) >= 2:
                        key_type = parts[0]
                        comment = parts[2] if len(parts) > 2 else '无备注'
                        result.append(f"{key_file.name}")
                        result.append(f"  类型: {key_type}")
                        result.append(f"  备注: {comment}")
                        result.append("")
                else:
                    result.append(f"{key_file.name} (无对应公钥)")
                    result.append("")
        
        # 检查 SSH 代理
        result.append("📝 SSH 代理状态:")
        try:
            import subprocess
            output = subprocess.run(['ssh-add', '-l'], capture_output=True, text=True, timeout=5)
            if output.returncode == 0:
                result.append(output.stdout)
            else:
                result.append("没有加载的密钥")
        except:
            result.append("无法获取 SSH 代理状态")
        
        return "\n".join(result)
    except Exception as e:
        return f"列出 SSH 密钥失败: {str(e)}"

def generate_ssh_key(name, key_type='ed25519', comment=None):
    """生成 SSH 密钥对"""
    try:
        import subprocess
        
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        key_path = ssh_dir / name
        
        if comment is None:
            comment = f"{os.getenv('USER')}@{os.uname().nodename}"
        
        # 生成密钥
        cmd = [
            'ssh-keygen',
            '-t', key_type,
            '-f', str(key_path),
            '-C', comment,
            '-N', ''  # 空密码
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return f"SSH 密钥已生成:\n  私钥: {key_path}\n  公钥: {key_path}.pub"
        else:
            return f"生成失败: {result.stderr}"
    except FileNotFoundError:
        return "错误: 未找到 ssh-keygen 命令"
    except Exception as e:
        return f"生成 SSH 密钥失败: {str(e)}"

def security_check():
    """安全检查"""
    try:
        result = ["🔒 安全检查报告", ""]
        issues = []
        
        # 检查 SSH 目录权限
        ssh_dir = Path.home() / '.ssh'
        if ssh_dir.exists():
            stat = ssh_dir.stat()
            if oct(stat.st_mode)[-3:] != '700':
                issues.append(f"SSH 目录权限不正确: {oct(stat.st_mode)[-3:]}")
        
        # 检查是否有空密码密钥
        if ssh_dir.exists():
            for key_file in ssh_dir.glob('id_*'):
                if not key_file.name.endswith('.pub'):
                    # 检查是否是空密码
                    import subprocess
                    check = subprocess.run(
                        ['ssh-keygen', '-y', '-f', str(key_file)],
                        capture_output=True,
                        input='\n',
                        text=True,
                        timeout=5
                    )
                    if check.returncode == 0:
                        issues.append(f"密钥 {key_file.name} 未设置密码")
        
        # 检查敏感文件
        sensitive_files = ['.env', '.aws/credentials', '.netrc']
        for file in sensitive_files:
            path = Path.home() / file
            if path.exists():
                stat = path.stat()
                if stat.st_mode & 0o077:
                    issues.append(f"敏感文件权限过宽: {file}")
        
        if issues:
            result.append("⚠️ 发现以下问题:")
            for issue in issues:
                result.append(f"  - {issue}")
        else:
            result.append("✅ 未发现明显安全问题")
        
        return "\n".join(result)
    except Exception as e:
        return f"安全检查失败: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Security Tools - 安全工具集")
        print("\n用法:")
        print("  passwd [选项]           - 生成密码")
        print("    -l <长度>              密码长度 (默认16)")
        print("    -s                     包含特殊字符")
        print("")
        print("  encrypt <文件> [输出]   - 加密文件")
        print("  decrypt <文件> [输出]   - 解密文件")
        print("")
        print("  hash <文件> [选项]      - 计算文件哈希")
        print("    -a <算法>              指定算法 (md5/sha1/sha256/sha512)")
        print("  hash-str <字符串>       - 计算字符串哈希")
        print("")
        print("  ssh-list                - 列出 SSH 密钥")
        print("  ssh-gen <名称>          - 生成 SSH 密钥对")
        print("")
        print("  check                   - 运行安全检查")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "passwd":
        length = 16
        special = False
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '-l' and i + 1 < len(sys.argv):
                length = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '-s':
                special = True
                i += 1
            else:
                i += 1
        
        print(generate_password(length, special))
    
    elif cmd == "encrypt":
        if len(sys.argv) < 3:
            print("用法: encrypt <文件> [输出文件]")
        else:
            output = sys.argv[3] if len(sys.argv) > 3 else None
            print(encrypt_file(sys.argv[2], output))
    
    elif cmd == "decrypt":
        if len(sys.argv) < 3:
            print("用法: decrypt <文件> [输出文件]")
        else:
            output = sys.argv[3] if len(sys.argv) > 3 else None
            print(decrypt_file(sys.argv[2], output))
    
    elif cmd == "hash":
        if len(sys.argv) < 3:
            print("用法: hash <文件> [-a 算法]")
        else:
            algorithm = None
            if '-a' in sys.argv and sys.argv.index('-a') + 1 < len(sys.argv):
                algorithm = sys.argv[sys.argv.index('-a') + 1]
            print(hash_file(sys.argv[2], algorithm))
    
    elif cmd == "hash-str":
        if len(sys.argv) < 3:
            print("用法: hash-str <字符串>")
        else:
            print(hash_string(sys.argv[2]))
    
    elif cmd == "ssh-list":
        print(list_ssh_keys())
    
    elif cmd == "ssh-gen":
        if len(sys.argv) < 3:
            print("用法: ssh-gen <密钥名称>")
        else:
            print(generate_ssh_key(sys.argv[2]))
    
    elif cmd == "check":
        print(security_check())
    
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
