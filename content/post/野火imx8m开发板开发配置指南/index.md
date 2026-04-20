+++
author = "嵌入式老师"
title = "野火imx8m开发板开发配置指南"
date = "2026-04-20"
description = "嵌入式实验课"
tags = [
    "嵌入式",
]
categories = [
    "教程",
]
series = ["Themes Guide"]
+++

# 野火 i.MX8M 开发板环境配置与开发工作流完整指南

## 目录

1. [认识野火 i.MX8M 开发板](#一认识野火-imx8m-开发板)
2. [MobaXterm 下载、安装及串口连接配置](#二mobaxterm-下载安装及串口连接配置)
3. [开发板网络配置（USB0 共享 + ETH0 调试）](#三开发板网络配置usb0-共享--eth0-调试)
4. [VMware + Ubuntu NFS 共享配置及 VSCode 开发工作流](#四vmware--ubuntu-nfs-共享配置及-vscode-开发工作流)

---

## 一、认识野火 i.MX8M 开发板

本章节帮助您快速了解野火 i.MX8M Mini 开发板的硬件接口，重点关注 USB 和网络接口。

### 1.1 硬件概览

请通过以下官方文档详细了解开发板的硬件规格和接口布局：

📖 **参考文档**：[野火 i.MX8MM 硬件介绍](https://doc.embedfire.com/linux/imx8mm/linux_base/zh/latest/linux_basis/ebf6ull_hardware/ebf6ull_hardware.html)

**重点关注的接口：**

- **USB 接口**：用于 USB Gadget 网络共享（usb0）
- **以太网接口（ETH0）**：用于稳定的 SSH 远程调试和文件传输
- **串口（UART）**：用于初始系统访问和调试

> 💡 **提示**：无需记忆所有细节，只需通过上述链接了解 USB 和网络接口的位置和基本功能即可。后续配置时会具体说明如何使用这些接口。

---

## 二、MobaXterm 下载、安装及串口连接配置

### 2.1 MobaXterm 下载与安装

**获取安装包：**

- 教师将提供 MobaXterm 安装包（推荐 Professional Edition）
- 或从官网下载：https://mobaxterm.mobatek.net/download.html

**安装步骤：**

1. 运行安装程序，按照向导完成安装
2. 首次启动时，可选择便携版（Portable）或安装版（Installer edition）
3. 建议创建桌面快捷方式以便快速访问

### 2.2 通过串口连接开发板

#### 硬件连线

请参考官方文档完成串口线的物理连接：

📖 **参考文档**：[开发板启动与串口连接](https://doc.embedfire.com/linux/imx8mm/linux_base/zh/latest/linux_basis/board_startup/board_startup.html)

**基本连线步骤：**

1. 使用 USB 转串口线（Type-C）
2. 一端连接开发板的 USB OTG 接口
3. 另一端连接 Windows 主机的 USB 端口

#### MobaXterm 串口配置

**配置步骤：**

1. 启动 MobaXterm
2. 点击左上角 **"Session"** → 选择 **"Serial"**
3. **查找 COM 端口号**（重要！）：

   **方法一：通过设备管理器查看**
   - 在 Windows 中，右键点击 **"此电脑"** 或 **"我的电脑"** → 选择 **"管理"**
   - 或者按 `Win + X` 键，选择 **"设备管理器"**
   - 或者按 `Win + R`，输入 `devmgmt.msc` 后回车

   在设备管理器窗口中：
   - 展开 **"端口 (COM 和 LPT)"** 或 **"Ports (COM & LPT)"** 类别
   - 查找包含 **"USB-SERIAL"**、**"CH340"**、**"CP210x"**、**"FTDI"** 或类似字样的设备
   - 括号中的数字即为 COM 端口号，例如：**USB-SERIAL CH340 (COM3)**
   - 记下这个 COM 编号（如 COM3、COM4 等）

   > 💡 **提示**：如果找不到串口设备，请检查：
   >
   > - USB 转串口线是否已正确连接
   > - 是否需要安装驱动程序（常见芯片：CH340、CP2102、FT232）
   > - 尝试拔插 USB 线后刷新设备管理器（按 F5）

   **方法二：通过 MobaXterm 自动检测**
   - 在 Serial session 配置界面，点击 **"Serial port"** 下拉菜单
   - MobaXterm 会自动列出可用的 COM 端口
   - 通常只有一个选项时，直接选择即可

4. 配置串口参数：
   - **Serial port**：选择刚才找到的 COM 端口（如 COM3）
   - **Speed (baud)**：`115200`
   - **Data bits**：`8`
   - **Stop bits**：`1`
   - **Parity**：`None`
   - **Flow control**：`None`
5. 点击 **"OK"** 建立连接
6. 给开发板上电，应能看到启动日志

> ⚠️ **注意**：如果看不到输出，请检查：
>
> - COM 端口号是否正确
> - 波特率是否为 115200
> - 串口线是否连接牢固
> - 开发板是否正常供电

**登录系统：**

- 默认用户名：`root` 或 `debian`（根据镜像版本）
- 默认密码：temppwd

---

## 三、开发板网络配置（USB0 共享 + ETH0 调试）

本章节基于 LubanCat 开发板双网卡配置经验，适配野火 i.MX8M 开发板的双网络接口场景。

### 3.1 网络拓扑与 IP 规划

| 接口     | 用途     | 开发板 IP       | 子网掩码          | 网关          | DNS                          |
| :------- | :------- | :-------------- | :---------------- | :------------ | :--------------------------- |
| **usb0** | **上网** | `192.168.7.2`   | `255.255.255.252` | `192.168.7.1` | `8.8.8.8`, `114.114.114.114` |
| **eth0** | **调试** | `192.168.137.2` | `255.255.255.0`   | **无**        | -                            |

> **重要说明**：
>
> - **usb0**：通过 USB Gadget 技术共享 Windows 主机网络，作为开发板的默认互联网出口
> - **eth0**：连接到路由器或开发主机，用于稳定的 SSH 远程调试，不参与互联网访问
> - Windows 主机侧需正确配置对应虚拟网卡 IP（usb0 对应 `192.168.7.1`，eth0 对应 `192.168.137.1`）

### 3.1.1 Windows 主机 USB 网络共享配置

在配置开发板网络之前，**必须先在 Windows 主机上启用 USB 网络共享功能**。请按照以下步骤操作：

#### 步骤 1：连接开发板到 Windows 主机

1. 使用 USB Type-C 数据线连接开发板的 **USB OTG 接口**到 Windows 主机的 USB 端口
2. 给开发板上电并等待系统启动完成
3. 通过串口确认开发板已正常启动

#### 步骤 2：打开网络连接设置

1. 按 `Win + R` 键，输入 `ncpa.cpl` 后回车
2. 或者：右键点击任务栏网络图标 → **"网络和 Internet 设置"** → **"更改适配器选项"**
3. 这将打开"网络连接"窗口，显示所有网络适配器

#### 步骤 3：启用 Internet 连接共享（ICS）

1. 找到您当前正在使用的**上网网卡**（通常是 WiFi 或以太网适配器）
   - 状态应显示为"已启用"或"Connected"
   - 右键点击该网卡 → 选择 **"属性"**

2. 切换到 **"共享"** 选项卡

3. 勾选 **"允许其他网络用户通过此计算机的 Internet 连接来连接"**

4. 在 **"家庭网络连接"** 下拉菜单中，选择开发板对应的 USB 网络设备
   - 通常显示为：**"以太网 X"** 或 **"USB Ethernet/RNDIS Gadget"**
   - 如果不确定是哪个，可以拔掉开发板 USB 线观察哪个适配器消失来判断

5. 点击 **"确定"** 保存设置

> ⚠️ **重要提示**：
>
> - 启用共享后，Windows 会自动将该 USB 网卡的 IP 设置为 `192.168.7.1`
> - 如果提示需要重启或其他警告，请点击"是"继续
> - 某些情况下可能需要重新插拔 USB 线才能使共享生效

#### 步骤 4：验证 USB 网卡配置

1. 在网络连接窗口中，找到刚才选择的 USB 网卡
2. 右键点击 → **"状态"** → **"详细信息"**
3. 确认 IPv4 地址为 `192.168.7.1`
4. 子网掩码应为 `255.255.255.252`

如果 IP 不是 `192.168.7.1`，可以手动设置：

1. 右键 USB 网卡 → **"属性"**
2. 双击 **"Internet 协议版本 4 (TCP/IPv4)"**
3. 选择 **"使用下面的 IP 地址"**：
   - IP 地址：`192.168.7.1`
   - 子网掩码：`255.255.255.252`
   - 默认网关：留空
4. 点击 **"确定"** 保存

#### 步骤 5：测试连通性

在 Windows 命令提示符中测试：

```cmd
ping 192.168.7.2
```

如果能 ping 通，说明 USB 网络共享配置成功！

> 📖 **参考文档**：更多详细信息请参考 [野火论坛 - USB 网络共享配置教程](https://www.firebbs.cn/forum.php?mod=viewthread&tid=34475&highlight=usb%E5%85%B1%E4%BA%AB)

### 3.2 前置准备：清理冲突服务

野火 i.MX8M Debian 系统可能安装了多个网络管理器（如 ConnMan、NetworkManager），它们会相互冲突。**在修改配置前，请务必执行以下步骤以锁定唯一的网络管理器。**

通过 MobaXterm 串口连接登录后，依次执行：

```bash
# 1. 停止所有潜在冲突的网络服务
sudo systemctl stop connman NetworkManager systemd-networkd

# 2. 禁用开机自启
sudo systemctl disable connman NetworkManager systemd-networkd

# 3. 彻底屏蔽（Mask），防止被其他依赖意外唤醒
sudo systemctl mask connman NetworkManager systemd-networkd

# 4. 启用传统的 networking 服务
sudo systemctl enable networking
```

### 3.3 核心配置步骤

#### 3.3.1 编辑网络配置文件

使用编辑器打开 `/etc/network/interfaces`：

```bash
sudo nano /etc/network/interfaces
```

#### 3.3.2 写入标准配置

请确保文件内容与下方完全一致（您可以删除原有的其他配置）：

```text
# 环路接口(必须保留)
auto lo
iface lo inet loopback

# eth0: 开发调试网口(静态IP, 不设网关)
auto eth0
iface eth0 inet static
    address 192.168.137.2
    netmask 255.255.255.0
    # 重要：此处千万不要写 gateway，否则会与 usb0 冲突

# usb0: USB共享上网口(静态IP, 设为默认网关)
auto usb0
iface usb0 inet static
    address 192.168.7.2
    netmask 255.255.255.252
    gateway 192.168.7.1
    dns-nameservers 8.8.8.8 114.114.114.114
```

**操作提示：**

- 在 `nano` 中，按 `Ctrl + O` 然后回车保存
- 按 `Ctrl + X` 退出编辑器

#### 3.3.3 应用配置

有两种方式使配置生效：

**方式 A（推荐）：重启开发板**

```bash
sudo reboot
```

**方式 B：重启网络服务**

```bash
sudo systemctl restart networking
```

### 3.4 验证与测试

重启或重启服务后，请重新通过串口登录开发板，执行以下检查：

#### 3.4.1 检查路由表

```bash
route -n
```

**预期结果：**

- 第一行应为：`0.0.0.0  192.168.7.1  ...  UG  ...  usb0`（默认网关指向 usb0）
- 应包含：`192.168.137.0  ...  eth0`（局域网路由）
- 应包含：`192.168.7.0  ...  usb0`（USB 网段路由）

#### 3.4.2 检查 IP 地址

```bash
ip addr show
```

**预期结果：**

- `eth0` 显示 `inet 192.168.137.2/24`
- `usb0` 显示 `inet 192.168.7.2/30`

#### 3.4.3 连通性测试

```bash
# 测试外网(百度)
ping -c 4 www.baidu.com

# 测试内网 (Windows 主机 eth0 侧)
ping -c 4 192.168.137.1
```

### 3.5 常见问题排查

#### Q1: ping 不通百度，提示 "Network is unreachable"

- **原因**：默认路由缺失或错误
- **解决**：
  1. 检查 `route -n` 是否有 `UG` 标志的行指向 `usb0`
  2. 如果没有，检查 `/etc/network/interfaces` 中 `usb0` 是否写了 `gateway 192.168.7.1`
  3. 手动修复：`sudo ip route add default via 192.168.7.1 dev usb0`

#### Q2: ping 不通百度，提示 "Temporary failure in name resolution"

- **原因**：DNS 配置未生效
- **解决**：
  1. 查看 `cat /etc/resolv.conf`
  2. 如果为空或错误，手动添加：
     ```bash
     echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
     ```
  3. 长期解决：确保 `/etc/network/interfaces` 中 `usb0` 下有 `dns-nameservers` 字段，并安装 `resolvconf` (`sudo apt install resolvconf`)

#### Q3: SSH 连接 eth0 经常断开

- **原因**：Windows 主机防火墙拦截或 IP 冲突
- **解决**：
  1. 确保 Windows 端 `192.168.137.1` 网卡开启了"文件和打印机共享"
  2. 尝试在 Windows 命令行 `ping 192.168.137.2` 看是否通畅

#### Q4: 重启后配置失效，又变回 ConnMan 管理

- **原因**：屏蔽（Mask）操作未成功或被撤销
- **解决**：重新执行第 3.2 节中的 `sudo systemctl mask connman ...` 命令，并确认返回结果为 `Created symlink ... -> /dev/null`

---

## 四、VMware + Ubuntu NFS 共享配置及 VSCode 开发工作流

本章节详细介绍如何配置 VMware Ubuntu 虚拟机与开发板之间的 NFS 共享，以及完整的 VSCode 交叉编译开发和部署流程。

### 4.1 VMware 网络适配器配置

#### 4.1.1 添加第二块网络适配器

1. 关闭 Ubuntu 虚拟机
2. 右键虚拟机 → **设置** → **添加** → **网络适配器**
3. 选择新添加的网络适配器，设置为：
   - **网络连接**: 桥接模式
   - **复制物理网络连接状态**: ✓ 勾选

#### 4.1.2 配置 VMware 虚拟网络编辑器

1. 打开 VMware → **编辑** → **虚拟网络编辑器**
2. 点击 **更改设置**（需要管理员权限）
3. 找到 **VMnet0**（桥接模式）：
   - 类型: **桥接模式**
   - 桥接到: 选择宿主机的物理网卡（确保该网卡在 192.168.137.x 网段）
4. 点击 **确定** 保存

---

### 4.2 Ubuntu 主机配置

#### 4.2.1 确认网络接口名称

```bash
ip addr show
```

记录新增的网卡名称（如 `ens38`）

#### 4.2.2 配置静态 IP 地址

编辑 Netplan 配置文件：

```bash
sudo nano /etc/netplan/01-network-manager-all.yaml
```

添加以下内容（根据实际情况修改网卡名称）：

```yaml
# Let NetworkManager manage all devices on this system
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens38:
      dhcp4: no
      addresses:
        - 192.168.137.100/24
      routes:
        - to: default
          via: 192.168.137.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 114.114.114.114
```

应用配置：

```bash
sudo chmod 600 /etc/netplan/01-network-manager-all.yaml
sudo netplan apply
```

验证 IP 配置：

```bash
ip addr show ens38
```

应看到类似输出：

```
inet 192.168.137.100/24 brd 192.168.137.255 scope global ens38
```

#### 4.2.3 安装 NFS 服务器

```bash
sudo apt update
sudo apt install -y nfs-kernel-server
```

#### 4.2.4 创建共享目录

```bash
sudo mkdir -p /home/frank/nfs_share
sudo chmod 777 /home/frank/nfs_share
```

#### 4.2.5 配置 NFS 导出

编辑 exports 文件：

```bash
sudo nano /etc/exports
```

添加以下行（允许整个 192.168.137.0/24 网段访问）：

```
/home/frank/nfs_share 192.168.137.0/24(rw,sync,no_subtree_check,no_root_squash)
```

> **参数说明：**
>
> - `rw`: 读写权限
> - `sync`: 同步写入
> - `no_subtree_check`: 禁用子目录检查（提高性能）
> - `no_root_squash`: 允许 root 用户保持 root 权限

#### 4.2.6 启动并启用 NFS 服务

```bash
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server
```

#### 4.2.7 验证 NFS 共享

```bash
showmount -e localhost
```

应看到：

```
Export list for localhost:
/home/frank/nfs_share 192.168.137.0/24
```

#### 4.2.8 配置防火墙（如有启用）

```bash
# 检查防火墙状态
sudo ufw status

# 如果启用了 UFW，允许 NFS 相关端口
sudo ufw allow from 192.168.137.0/24 to any port nfs
sudo ufw allow from 192.168.137.0/24 to any port mountd
sudo ufw allow from 192.168.137.0/24 to any port rpc-bind
sudo ufw reload
```

---

### 4.3 开发板配置

#### 4.3.1 安装 NFS 客户端

在开发板上执行（通过 MobaXterm SSH 连接，见 4.5 节）：

```bash
sudo apt update
sudo apt install -y nfs-common
```

> 如果遇到 "bad option" 错误，就是因为缺少 `nfs-common` 包。

#### 4.3.2 创建挂载点

```bash
sudo mkdir -p /mnt/nfs
```

#### 4.3.3 手动挂载 NFS 共享

```bash
sudo mount -t nfs 192.168.137.100:/home/frank/nfs_share /mnt/nfs
```

#### 4.3.4 验证挂载

```bash
df -h | grep nfs
ls -la /mnt/nfs
```

应能看到 Ubuntu 主机共享的文件。

#### 4.3.5 测试读写权限

```bash
# 在开发板上创建测试文件
touch /mnt/nfs/test_from_board.txt
echo "Hello from development board" > /mnt/nfs/test_from_board.txt

# 在 Ubuntu 主机上验证
ls -la /home/frank/nfs_share/
cat /home/frank/nfs_share/test_from_board.txt
```

#### 4.3.6 配置开机自动挂载（可选）

编辑 fstab 文件：

```bash
sudo nano /etc/fstab
```

添加以下行：

```
192.168.137.100:/home/frank/nfs_share /mnt/nfs nfs defaults,_netdev 0 0
```

> `_netdev` 选项确保在网络就绪后再挂载。

测试 fstab 配置：

```bash
sudo umount /mnt/nfs
sudo mount -a
```

---

### 4.4 常见问题排查

#### 问题 1: 开发板无法 ping 通 Ubuntu

```bash
# 在开发板上测试
ping 192.168.137.100
```

**解决方法：**

1. 检查 Ubuntu 的 IP 配置：`ip addr show ens38`
2. 检查 VMware 网络适配器是否设置为桥接模式
3. 检查 Windows 防火墙是否阻止了 ICMP 请求
4. 确保 Ubuntu 和开发板在同一网段

#### 问题 2: NFS 挂载失败

**常见错误及解决：**

```bash
# 错误: "mount.nfs: access denied by server"
# 解决: 检查 /etc/exports 配置，确保 IP 范围正确
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server

# 错误: "mount.nfs: Connection timed out"
# 解决: 检查网络连接和防火墙
ping 192.168.137.100
sudo ufw status

# 错误: "mount.nfs: Protocol not supported"
# 解决: 指定 NFS 版本
sudo mount -t nfs -o vers=3 192.168.137.100:/home/frank/nfs_share /mnt/nfs
```

#### 问题 3: 权限问题

```bash
# 如果在开发板上无法写入 NFS 共享
# 检查 Ubuntu 上的目录权限
ls -la /home/frank/nfs_share

# 确保权限为 777 或适当的所有者
sudo chmod 777 /home/frank/nfs_share
```

---

### 4.5 MobaXterm SSH 连接及 VSCode 开发工作流

本节介绍如何通过 MobaXterm SSH 连接开发板，并将 VSCode 中编译好的程序传送到开发板上运行的完整流程。

#### 4.5.1 配置 MobaXterm SSH 会话

**前提条件：**

- 开发板 eth0 已配置为 `192.168.137.2`
- Windows 主机对应网卡已配置为 `192.168.137.1`
- 两者可以互相 ping 通

**SSH 连接步骤：**

1. 启动 MobaXterm
2. 点击左上角 **"Session"** → 选择 **"SSH"**
3. 配置 SSH 参数：
   - **Remote host**: `192.168.137.2`（开发板 eth0 IP）
   - **Specify username**: 勾选，输入用户名（如 `debian` 或 `root`）
   - **Port**: `22`（默认 SSH 端口）
4. 点击 **"Advanced SSH settings"**（可选）：
   - 如需密钥认证，在此配置私钥文件
5. 点击 **"OK"** 建立连接
6. 首次连接时会提示接受主机密钥，点击 **"Yes"**
7. 输入密码完成登录

> 💡 **提示**：可以将此会话保存，方便下次快速连接：
>
> - 连接成功后，左侧 Sessions 栏会自动保存
> - 右键会话 → **Edit session** 可修改配置
> - 双击保存的会话即可快速重连

#### 4.5.2 VSCode 交叉编译程序

**在 Ubuntu VM 中编译：**

1. 在 VSCode 中打开项目文件夹（位于 NFS 共享目录或其子目录）
2. 配置交叉编译工具链（示例 `.vscode/tasks.json`）：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build for i.MX8M",
      "type": "shell",
      "command": "aarch64-linux-gnu-gcc",
      "args": [
        "-o",
        "${workspaceFolder}/output/myapp",
        "${workspaceFolder}/src/main.c",
        "-Wall",
        "-O2"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": ["$gcc"]
    }
  ]
}
```

3. 按 `Ctrl+Shift+B` 触发构建任务
4. 编译完成后，可执行文件生成在 `${workspaceFolder}/output/myapp`

> 📌 **注意**：由于使用了 NFS 共享，编译输出的文件会自动出现在开发板的 `/mnt/nfs` 目录下！

#### 4.5.3 方法一：通过 NFS 直接运行（推荐）

这是最便捷的方式，利用已配置的 NFS 共享：

**在开发板上（通过 MobaXterm SSH）：**

```bash
# 1. 进入 NFS 挂载目录
cd /mnt/nfs

# 2. 查看编译好的程序
ls -la output/

# 3. 赋予执行权限（如果需要）
chmod +x output/myapp

# 4. 直接运行程序
./output/myapp

# 或者带参数运行
./output/myapp arg1 arg2
```

**优点：**

- ✅ 无需额外传输步骤
- ✅ 修改代码后重新编译即可立即运行
- ✅ 适合频繁调试的开发阶段

**缺点：**

- ⚠️ 依赖 NFS 网络连接稳定性
- ⚠️ 性能略低于本地存储（对于大型程序）

#### 4.5.4 方法二：通过 MobaXterm SFTP 传输

如果不想使用 NFS，或需要将程序复制到开发板本地存储：

**使用 MobaXterm 内置 SFTP：**

1. 建立 SSH 连接后，MobaXterm 左侧会自动显示 SFTP 浏览器
2. 右侧窗口显示开发板文件系统
3. 左侧窗口显示 Windows 本地文件系统

**传输步骤：**

1. 在 Ubuntu VM 中，将编译好的程序复制到 Windows 可访问的位置：

   ```bash
   # 在 Ubuntu 终端
   cp /home/frank/nfs_share/output/myapp /mnt/hgfs/Shared/myapp
   ```

   （假设已配置 VMware 共享文件夹）

2. 在 MobaXterm SFTP 浏览器中：
   - 导航到 Windows 端的程序位置
   - 拖拽文件到开发板的目标目录（如 `/home/debian/`）

3. 在 SSH 终端中运行：
   ```bash
   cd /home/debian
   chmod +x myapp
   ./myapp
   ```

#### 4.5.5 方法三：使用 SCP 命令传输

**从 Ubuntu VM 发送到开发板：**

```bash
# 在 Ubuntu 终端执行
scp /home/frank/nfs_share/output/myapp debian@192.168.137.2:/home/debian/
```

**从开发板拉取文件到 Ubuntu：**

```bash
# 在 Ubuntu 终端执行
scp debian@192.168.137.2:/home/debian/logfile.txt /home/frank/nfs_share/
```

#### 4.5.6 方法四：使用 rsync 同步（高级）

适合大量文件或需要同步整个目录的场景：

```bash
# 从 Ubuntu 同步到开发板
rsync -avz /home/frank/nfs_share/output/ debian@192.168.137.2:/home/debian/output/

# 从开发板同步到 Ubuntu
rsync -avz debian@192.168.137.2:/home/debian/logs/ /home/frank/nfs_share/logs/
```

---

### 4.6 完整开发工作流示例

以下是从零开始到程序在开发板上运行的完整流程：

#### 步骤 1：准备工作

```bash
# 【Ubuntu VM】确保 NFS 服务正常运行
sudo systemctl status nfs-kernel-server

# 【开发板】确保 NFS 客户端已挂载
df -h | grep nfs
# 应看到: 192.168.137.100:/home/frank/nfs_share on /mnt/nfs
```

#### 步骤 2：编写代码

在 VSCode 中编辑源代码（文件位于 NFS 共享目录）：

```c
// /home/frank/nfs_share/projects/hello/main.c
#include <stdio.h>

int main() {
    printf("Hello from i.MX8M!\n");
    return 0;
}
```

#### 步骤 3：交叉编译

在 VSCode 中按 `Ctrl+Shift+B`，或在终端执行：

```bash
cd /home/frank/nfs_share/projects/hello
aarch64-linux-gnu-gcc -o hello main.c -Wall -O2
```

#### 步骤 4：在开发板上运行

通过 MobaXterm SSH 连接开发板后：

```bash
# 进入 NFS 挂载点
cd /mnt/nfs/projects/hello

# 查看文件（应该能看到刚编译的 hello 程序）
ls -la hello

# 赋予执行权限
chmod +x hello

# 运行程序
./hello
```

**预期输出：**

```
Hello from i.MX8M!
```

#### 步骤 5：调试与迭代

1. 修改源代码（在 VSCode 中）
2. 重新编译（`Ctrl+Shift+B`）
3. 直接在开发板 SSH 终端中再次运行 `./hello`
4. 重复直到满意

---

### 4.6.1 测试：NFS共享与跨平台运行对比测试

本案例将通过实际的 `malloc_frag.c` 程序，演示完整的 NFS 共享、交叉编译、文件传输以及在 Ubuntu x86_64 和开发板 ARM64 平台上运行对比的全过程。

#### 案例目标

- ✅ 掌握将源代码复制到 NFS 共享目录的方法
- ✅ 学习使用 gcc（本地）和交叉编译器（aarch64）分别编译
- ✅ 通过 NFS 和 MobaXterm SSH 两种方式传输可执行文件
- ✅ 对比同一程序在不同架构平台上的运行结果
- ✅ 理解内存管理在嵌入式系统中的重要性

#### 步骤 1：准备源代码

**方法 A：从 docs 目录复制到 NFS 共享目录**

在 Ubuntu VM 终端中执行：

```bash
# 创建项目目录
mkdir -p /home/frank/nfs_share/projects/malloc_test

# 复制源代码
cp /home/frank/embedded/docs/notebooks/malloc_frag.c /home/frank/nfs_share/projects/malloc_test/

# 验证文件已复制
ls -la /home/frank/nfs_share/projects/malloc_test/
```

**方法 B：直接在 VSCode 中打开并另存为**

1. 在 VSCode 中打开 `/home/frank/embedded/docs/notebooks/malloc_frag.c`
2. 点击 **文件** → **另存为**
3. 保存到 `/home/frank/nfs_share/projects/malloc_test/malloc_frag.c`

> 💡 **提示**：由于使用了 NFS 共享，此时在开发板上已经可以看到这个文件了！

#### 步骤 2：在 Ubuntu x86_64 上编译并运行

**编译为本机可执行文件：**

```bash
cd /home/frank/nfs_share/projects/malloc_test

# 使用本机 gcc 编译（生成 x86_64 架构的可执行文件）
gcc -o malloc_frag_x86 malloc_frag.c -Wall -O2

# 查看生成的文件信息
file malloc_frag_x86
```

**预期输出：**

```
malloc_frag_x86: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, ...
```

**在本机运行：**

```bash
./malloc_frag_x86
```

**预期输出：**

```
[Step 1] Heap Init (10 Blocks).
[Status] Alloc A,B,C,D,E: X X X X X X X X X X

[Step 3] Free B and D to create holes...
[Status] Free B, D       : X X _ _ X X _ _ X X

[Step 4] Try Alloc Block F (Size=3)...
Error: Allocation Failed! (Fragmentation detected)
Reason: Total Free blocks = 4 (Size>3), but Max Contiguous Space = 2.
Conclusion: 这就是为什么嵌入式系统慎用 malloc 的原因。
```

#### 步骤 3：交叉编译为 ARM64 架构

**使用交叉编译工具链：**

```bash
cd /home/frank/nfs_share/projects/malloc_test

# 使用 aarch64 交叉编译器编译（生成 ARM64 架构的可执行文件）
aarch64-linux-gnu-gcc -o malloc_frag_arm64 malloc_frag.c -Wall -O2

# 查看生成的文件信息
file malloc_frag_arm64
```

**预期输出：**

```
malloc_frag_arm64: ELF 64-bit LSB pie executable, ARM aarch64, version 1 (SYSV), dynamically linked, ...
```

> ⚠️ **重要说明**：
>
> - `malloc_frag_x86` 只能在 x86_64 架构（Ubuntu VM）上运行
> - `malloc_frag_arm64` 只能在 ARM64 架构（开发板）上运行
> - 如果尝试在错误的平台上运行，会报错：`Exec format error`

#### 步骤 4：方法一 - 通过 NFS 直接在开发板上运行

由于我们已经配置了 NFS 共享，编译好的 ARM64 程序已经自动出现在开发板的 `/mnt/nfs` 目录下了！

**在开发板上（通过 MobaXterm SSH 连接）：**

```bash
# 进入 NFS 挂载的项目目录
cd /mnt/nfs/projects/malloc_test

# 查看文件列表（应该能看到两个可执行文件）
ls -la

# 赋予执行权限
chmod +x malloc_frag_arm64

# 运行 ARM64 版本
./malloc_frag_arm64
```

**预期输出：**（与 Ubuntu 上相同）

```
[Step 1] Heap Init (10 Blocks).
[Status] Alloc A,B,C,D,E: X X X X X X X X X X

[Step 3] Free B and D to create holes...
[Status] Free B, D       : X X _ _ X X _ _ X X

[Step 4] Try Alloc Block F (Size=3)...
Error: Allocation Failed! (Fragmentation detected)
Reason: Total Free blocks = 4 (Size>3), but Max Contiguous Space = 2.
Conclusion: 这就是为什么嵌入式系统慎用 malloc 的原因。
```

#### 步骤 5：方法二 - 通过 VSCode 下载 + MobaXterm SFTP 上传

这是**最推荐的离线传输方式**，适合需要将程序保存到开发板本地存储的场景。

##### 第一阶段：在 VSCode 中下载编译好的文件到 Windows

**操作步骤：**

1. **确保 NFS 共享已挂载**

   在 Ubuntu VM 终端中确认：

   ```bash
   df -h | grep nfs_share
   # 应看到类似输出：
   # 192.168.137.100:/home/frank/nfs_share on /home/frank/nfs_share type nfs4
   ```

2. **在 VSCode 中定位文件**
   - 打开 VSCode 的文件资源管理器（左侧边栏）
   - 导航到：`/home/frank/nfs_share/projects/malloc_test/`
   - 找到编译好的文件：`malloc_frag_arm64`

3. **下载到 Windows 本地**

   **方法 A：右键菜单下载**
   - 在 VSCode 文件树中，右键点击 `malloc_frag_arm64`
   - 选择 **"Download..."** 或 **"另存为"**
   - 选择 Windows 本地的保存位置（如 `C:\Users\YourName\Downloads\`）

   **方法 B：拖拽下载**
   - 直接从 VSCode 文件树拖拽 `malloc_frag_arm64` 到 Windows 桌面或文件夹

   **方法 C：命令行复制（如果配置了 VMware 共享文件夹）**

   ```bash
   # 在 Ubuntu VM 终端执行
   cp /home/frank/nfs_share/projects/malloc_test/malloc_frag_arm64 /mnt/hgfs/Shared/
   # 然后在 Windows 的 C:\Shared\ 目录中找到该文件
   ```

4. **验证文件已下载**

   在 Windows 文件资源管理器中确认文件存在：
   - 文件大小应与 Ubuntu 上的一致
   - 文件名保持为 `malloc_frag_arm64`（无扩展名）

> 💡 **提示**：VSCode 的下载功能依赖于 Remote-SSH 或本地文件系统访问。如果使用 NFS 挂载，可以直接在 Windows 资源管理器中访问 `\\ubuntu-ip\nfs_share`（需要配置 Samba 共享）。

##### 第二阶段：通过 MobaXterm SFTP 上传到开发板

**操作步骤：**

1. **启动 MobaXterm 并连接 SSH**
   - 打开 MobaXterm
   - 双击之前保存的 SSH 会话（或新建 SSH 连接到 `192.168.137.2`）
   - 输入用户名和密码完成登录

2. **使用内置 SFTP 浏览器**

   连接成功后，MobaXterm 左侧会自动显示 **SFTP 面板**：
   - **上半部分**：显示开发板的文件系统（远程）
   - **下半部分**：显示 Windows 本地文件系统

3. **导航到文件位置**

   **在 Windows 侧（下半部分）：**
   - 浏览到你刚才下载文件的目录
   - 例如：`C:\Users\YourName\Downloads\`
   - 找到 `malloc_frag_arm64` 文件

   **在开发板侧（上半部分）：**
   - 导航到目标目录，例如：`/home/debian/`
   - 或者创建专门的项目目录：
     ```bash
     # 在 MobaXterm SSH 终端中执行
     mkdir -p /home/debian/projects/malloc_test
     cd /home/debian/projects/malloc_test
     ```

4. **拖拽上传文件**
   - 从 Windows 侧（下半部分）选中 `malloc_frag_arm64`
   - 拖拽到开发板侧（上半部分）的目标目录
   - 等待传输完成（底部会显示进度条）

5. **验证文件已上传**

   在 MobaXterm SSH 终端中执行：

   ```bash
   cd /home/debian/projects/malloc_test
   ls -la malloc_frag_arm64
   ```

   **预期输出：**

   ```
   -rw-r--r-- 1 debian debian 16384 Apr  9 10:30 malloc_frag_arm64
   ```

6. **赋予执行权限并运行**

   ```bash
   # 赋予执行权限
   chmod +x malloc_frag_arm64

   # 运行程序
   ./malloc_frag_arm64
   ```

   **预期输出：**

   ```
   [Step 1] Heap Init (10 Blocks).
   [Status] Alloc A,B,C,D,E: X X X X X X X X X X

   [Step 3] Free B and D to create holes...
   [Status] Free B, D       : X X _ _ X X _ _ X X

   [Step 4] Try Alloc Block F (Size=3)...
   Error: Allocation Failed! (Fragmentation detected)
   Reason: Total Free blocks = 4 (Size>3), but Max Contiguous Space = 2.
   Conclusion: 这就是为什么嵌入式系统慎用 malloc 的原因。
   ```

##### 优势与适用场景

**✅ 优势：**

- **离线可用**：文件保存在 Windows 本地，无需持续网络连接
- **版本管理**：可以在 Windows 上保留多个版本的备份
- **灵活性强**：可以随时重新上传，不受 NFS 挂载状态影响
- **可视化操作**：MobaXterm SFTP 界面直观，支持拖拽

**⚠️ 注意：**

- 需要额外的下载和上传步骤
- 修改代码后需要重新编译、下载、上传
- 适合最终部署或存档，不适合频繁调试

---

#### 步骤 6：方法三 - 使用 SCP 命令直接从 Ubuntu 发送

这是**最快速的命令行传输方式**，适合熟悉 Linux 命令的用户。

**在 Ubuntu VM 终端中执行：**

```bash
# 确保交叉编译已完成
cd /home/frank/nfs_share/projects/malloc_test
ls -la malloc_frag_arm64

# 使用 SCP 直接发送到开发板
scp malloc_frag_arm64 debian@192.168.137.2:/home/debian/projects/malloc_test/

# 输入开发板密码（默认为 temppwd）
```

**SCP 命令详解：**

```bash
scp [选项] 源文件 用户名@目标IP:目标路径
```

- `malloc_frag_arm64`：要传输的文件
- `debian`：开发板上的用户名
- `192.168.137.2`：开发板的 IP 地址
- `/home/debian/projects/malloc_test/`：目标目录

**常用 SCP 选项：**

```bash
# 递归传输整个目录
scp -r /home/frank/nfs_share/projects/malloc_test/ debian@192.168.137.2:/home/debian/projects/

# 显示传输进度
scp -v malloc_frag_arm64 debian@192.168.137.2:/home/debian/

# 压缩传输（适合大文件）
scp -C malloc_frag_arm64 debian@192.168.137.2:/home/debian/
```

**然后在开发板 SSH 终端中运行：**

```bash
# 连接到开发板（如果还未连接）
ssh debian@192.168.137.2

# 进入目标目录
cd /home/debian/projects/malloc_test

# 赋予执行权限
chmod +x malloc_frag_arm64

# 运行程序
./malloc_frag_arm64
```

##### 反向传输：从开发板拉取文件到 Ubuntu

如果需要将开发板上生成的日志或数据文件传回 Ubuntu：

```bash
# 在 Ubuntu VM 终端执行
scp debian@192.168.137.2:/home/debian/projects/malloc_test/output.log /home/frank/nfs_share/projects/malloc_test/
```

##### 优势与适用场景

**✅ 优势：**

- **速度快**：一条命令完成传输
- **可脚本化**：可以轻松集成到自动化脚本中
- **双向传输**：支持上传和下载
- **无需图形界面**：纯命令行操作，适合远程服务器

**⚠️ 注意：**

- 需要记住命令语法
- 每次传输都需要输入密码（除非配置 SSH 密钥）
- 适合熟悉 Linux 的用户

#### 步骤 7：对比分析运行结果

**对比项 1：输出内容一致性**

| 平台      | 架构   | 输出内容       | 是否一致 |
| --------- | ------ | -------------- | -------- |
| Ubuntu VM | x86_64 | 内存碎片化演示 | ✅       |
| 开发板    | ARM64  | 内存碎片化演示 | ✅       |

**结论**：程序的逻辑输出完全一致，因为这是纯计算型程序，不涉及平台特定的硬件操作。

**对比项 2：可执行文件格式**

```bash
# 在 Ubuntu 上检查
file malloc_frag_x86
# 输出: ELF 64-bit LSB pie executable, x86-64, ...

file malloc_frag_arm64
# 输出: ELF 64-bit LSB pie executable, ARM aarch64, ...
```

**对比项 3：文件大小差异**

```bash
ls -lh malloc_frag_*
```

可能会观察到：

- 两个文件大小略有不同（由于不同的指令集编码）
- ARM64 版本可能稍大或稍小，取决于编译器优化

**对比项 4：性能差异（可选测试）**

可以使用 `time` 命令测量执行时间：

```bash
# 在 Ubuntu 上
time ./malloc_frag_x86

# 在开发板上
time ./malloc_frag_arm64
```

> 📊 **注意**：由于这是一个非常小的程序，执行时间差异可能不明显。对于复杂程序，ARM 处理器（尤其是嵌入式级别）通常会比桌面级 x86_64 慢。

#### 步骤 8：深入理解 - 为什么需要交叉编译？

**尝试在开发板上运行 x86_64 版本（会失败）：**

```bash
# 先将 x86_64 版本传到开发板
scp /home/frank/nfs_share/projects/malloc_test/malloc_frag_x86 debian@192.168.137.2:/home/debian/

# 在开发板上尝试运行
cd /home/debian
chmod +x malloc_frag_x86
./malloc_frag_x86
```

**预期错误：**

```
-bash: ./malloc_frag_x86: cannot execute binary file: Exec format error
```

**原因解释：**

- CPU 只能理解其原生指令集
- x86_64 指令 ≠ ARM64 指令
- 就像让只会中文的人读英文书一样，CPU "看不懂" 错误的指令格式

**反过来也一样：**

```bash
# 在 Ubuntu 上尝试运行 ARM64 版本
./malloc_frag_arm64
```

**同样会报错：**

```
cannot execute binary file: Exec format error
```

#### 步骤 9：实验总结

通过这个实践案例，我们学习了：

1. ✅ **NFS 共享的优势**：编译后立即可见，无需手动传输
2. ✅ **交叉编译的必要性**：不同架构需要不同的编译器
3. ✅ **多种文件传输方式**：NFS、SFTP、SCP 各有适用场景
4. ✅ **平台差异性**：同一源码在不同架构上产生不同的可执行文件
5. ✅ **嵌入式内存管理**：通过 `malloc_frag.c` 理解了内存碎片化问题

**关键收获：**

> 🔑 **NFS 是最便捷的开发方式**：修改代码 → 重新编译 → 直接在开发板运行，整个流程无缝衔接！
>
> 🔑 **交叉编译是嵌入式开发的基石**：必须为目标平台选择合适的编译工具链。
>
> 🔑 **理解底层原理很重要**：知道为什么不能混用不同架构的可执行文件，有助于排查问题。

---

### 4.7 高级技巧（实用小技巧，非必需掌握内容，根据自己的情况选择学习）

#### 4.7.1 自动化部署脚本

在项目根目录创建 `deploy.sh`：

```bash
#!/bin/bash
# deploy.sh - 自动编译并部署到开发板

PROJECT_NAME="myapp"
BUILD_DIR="/home/frank/nfs_share/projects/${PROJECT_NAME}"
BOARD_IP="192.168.137.2"
BOARD_USER="debian"

echo "=== Building ${PROJECT_NAME} ==="
cd ${BUILD_DIR}
make clean && make

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful"
echo "💡 Program is available at: /mnt/nfs/projects/${PROJECT_NAME}/${PROJECT_NAME}"
echo "💡 Run on board: ssh ${BOARD_USER}@${BOARD_IP}"
echo "   Then execute: cd /mnt/nfs/projects/${PROJECT_NAME} && ./${PROJECT_NAME}"
```

#### 4.7.2 VSCode Remote SSH 扩展（替代方案）

如果希望直接在 VSCode 中编辑开发板上的文件：

1. 在 VSCode 中安装 **Remote - SSH** 扩展
2. 按 `F1` → 输入 "Remote-SSH: Connect to Host"
3. 输入：`debian@192.168.137.2`
4. 输入密码
5. 现在可以直接在 VSCode 中编辑开发板上的文件，并使用集成终端运行命令

> ⚠️ **注意**：这种方式不经过 NFS，适合小项目或不需要交叉编译的场景。

#### 4.7.3 性能优化建议

- **NFS 挂载选项优化**：

  ```bash
  # 在开发板 /etc/fstab 中使用更优化的选项
  192.168.137.100:/home/frank/nfs_share /mnt/nfs nfs rw,sync,hard,intr,rsize=8192,wsize=8192,_netdev 0 0
  ```

- **减少编译时间**：
  - 使用 `ccache` 缓存编译结果
  - 并行编译：`make -j4`

- **网络稳定性**：
  - 优先使用有线以太网而非 WiFi
  - 避免在大文件传输时进行其他网络密集型操作

---

## 附录：常用命令速查

### 网络诊断

```bash
# 检查 IP 配置
ip addr show

# 检查路由表
route -n

# Ping 测试
ping -c 4 192.168.137.100

# 检查 DNS
nslookup www.baidu.com
```

### NFS 相关

```bash
# 查看 NFS 共享
showmount -e 192.168.137.100

# 挂载 NFS
sudo mount -t nfs 192.168.137.100:/home/frank/nfs_share /mnt/nfs

# 卸载 NFS
sudo umount /mnt/nfs

# 检查挂载状态
df -h | grep nfs
```

### 系统服务

```bash
# 查看服务状态
sudo systemctl status nfs-kernel-server
sudo systemctl status networking

# 重启服务
sudo systemctl restart nfs-kernel-server
sudo systemctl restart networking
```

---

## 总结

本文档涵盖了从认识开发板、串口连接、网络配置到 NFS 共享和完整开发工作流的全部内容。关键要点：

1. **串口连接**是初始访问开发板的唯一方式，务必掌握 MobaXterm 串口配置
2. **双网卡配置**中，usb0 负责上网，eth0 负责调试，两者分工明确
3. **NFS 共享**极大简化了文件传输流程，实现"编译即部署"
4. **MobaXterm SSH** 提供了便捷的远程终端和文件传输功能
5. **VSCode + NFS** 组合实现了高效的交叉编译开发体验

祝您开发顺利！🎉

---

**文档版本**: v1.0  
**最后更新**: 2026年4月9日  
**适用平台**: 野火 i.MX8M Mini 开发板 + VMware Ubuntu + Windows 主机
