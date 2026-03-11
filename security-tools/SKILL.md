# Security Tools

系统安全工具集，包含密码生成、文件加密、SSH 管理等功能。

## 功能

- **密码生成** — 生成强密码、随机字符串
- **文件加密/解密** — 使用 AES 加密文件
- **哈希计算** — MD5、SHA256、SHA512
- **SSH 管理** — 查看密钥、生成密钥对
- **安全检查** — 扫描常见安全问题

## 使用

```bash
# 密码生成
security-tools passwd            # 生成 16 位强密码
security-tools passwd -l 24      # 生成 24 位密码
security-tools passwd -s         # 包含特殊字符

# 文件加密
security-tools encrypt file.txt        # 加密文件
security-tools decrypt file.txt.enc    # 解密文件

# 哈希计算
security-tools hash file.txt           # 计算各种哈希
security-tools hash -a sha256 file.txt # 指定算法

# SSH 管理
security-tools ssh-list          # 列出 SSH 密钥
security-tools ssh-gen mykey     # 生成新密钥对
```
