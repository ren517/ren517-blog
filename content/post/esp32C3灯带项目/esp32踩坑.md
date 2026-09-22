+++
author = "ren517"
title = "esp-now踩的坑"
date = "2026-09-22"
tags = [
    "嵌入式",
]
categories = [
    "教程",
]
series = ["Themes Guide"]
+++

# ESP-NOW 颜色链路 —— 踩坑复盘（2026-09-06）

> 场景：TCS34725 颜色传感器板（发送端，ESP32-C3 SuperMini）→ ESP-NOW → WLED 板（接收端，ESP32-C3 经典款）
> 约束：**两端都不配路由器，接收端跑 WLED AP 模式**，发送端按键触发单发颜色。
> 结论：在这种"无路由器、只用 AP"的场景下 ESP-NOW 天生脆弱，最终放弃改用 WiFi HTTP API。

---

## 一、架构级坑（最致命）

### 坑 1：ESP-NOW 收发双方角色 —— 发送方必须是 STA

- **现象**：一度试过两端都跑 AP 模式（想去掉 STA），结果单播/广播全 FAILED、灯不变色。
- **根因**：802.11 里**两个 AP 之间没有标准帧路径**（AP 只服务已关联的 STA）。ESP-NOW 官方标准用法就是：发送端 = STA（未连接即可），接收端 = AP。
- **正确做法**：发送端 `WiFi.mode(WIFI_STA)`（不连任何 AP），接收端 WLED 跑 AP。链路 = 发送端 STA → 接收端 AP。

### 坑 2：ESP-NOW 接收（recv_cb）默认绑定 STA 接口 —— 纯 AP 模式收不到

- **现象**：接收端切到纯 AP（mode=2）后，连 `frame from` 都不打印，但切回 APSTA（mode=3）就能收。
- **根因**：ESP-IDF 的 ESP-NOW 接收回调默认绑在 **STA 接口**上。mode=3 APSTA 时 STA 接口活着，能收；**mode=2 纯 AP 时 STA 接口被关，ESP-NOW 绑到 AP 接口，而 AP 接口会过滤未关联 STA 发来的 vendor action frame（ESP-NOW 帧类型），导致收不到**。
- **正确做法**：**必须保持 APSTA（mode=3），绝不能切纯 AP。** 即使没配路由器，STA 没目标 AP 不会持续扫描，mode=3 不存在扫描丢包问题。

### 坑 3："STA 杀死切纯 AP"是误判，反而破坏了稳定性

- **现象**：加了一段"启动 20s 后 STA 没连上就关掉 STA、锁定纯 AP"的逻辑，结果从偶尔能收到变成完全收不到。
- **根因**：误以为 APSTA 下 STA 后台扫描会把射频带离信道丢包。实际你没配路由器，STA 没目标 AP **不会持续扫描**（启动扫一下找不到就停），mode=3 不存在扫描丢包。这段逻辑反而把能收的 mode=3 切成了收不到的 mode=2。
- **教训**：**"加固"之前先验证假设，别想当然加防御代码。** 后来回退到简单基线反而稳定了。

---

## 二、WiFi 状态机坑

### 坑 4：WiFi mode 切换会让 ESP-NOW 静默失效

- **现象**：重启后/开机后一段窗口收不到任何包，"完全不能用"。
- **根因**：WLED 启动流程 `WiFi.mode(WIFI_STA)` 先扫描、之后才建 softAP，**模式每一切换（0→1→3）ESP-NOW 内部绑定就失效**。而且 WLED 重初始化 WiFi 后 ESP-NOW 也会静默失效。
- **正确做法**：监听 `WiFi.getMode()` 变化，一变就重新挂载 ESP-NOW（重新 init + 注册 recv_cb）。

### 坑 5：deinit+init 太激进会破坏内部状态

- **现象**：为了治 mode 切换失效，加了 `esp_now_deinit()` + `esp_now_init()` 强制重绑，结果"时好时坏"。
- **根因**：全量 deinit+init 会清空 ESP-NOW 内部状态/peer，反而引入不稳定。
- **教训**：**优先用"复用已有 init（ESP_ERR_ESPNOW_INTERNAL 时直接注册回调）"的轻量重挂，不要每次都 deinit。**

---

## 三、射频 / 省电坑（最隐蔽、最折磨）

### 坑 6：modem sleep 让 esp_now_send 返回 SUCCESS 但帧没真发出去

- **现象**：**发送端刚重启时成功率高，过一会（几十秒后）就几乎 0% 成功**。广播显示 SUCCESS，接收端却收不到。
- **根因**：STA 未连接时，ESP-IDF 一段时间后会启用 **modem sleep**，射频周期性睡眠。`esp_now_send` 返回 SUCCESS **只代表"帧交给驱动"**，不代表射频真发射了——射频睡着时驱动接受帧但不实际发射。
- **正确做法**：`esp_wifi_set_ps(WIFI_PS_NONE)` 关闭省电。**而且只在初始化时设一次会被 ESP-IDF 异步覆盖，必须每秒（或在每次发送前）强制重设。**

### 坑 7：loop 里每秒 set_ps 仍覆盖不到发送前那一刻

- **现象**：加了 loop 每秒 set_ps，还是间歇失败。
- **根因**：loop 执行频率有抖动，发送前那一刻射频可能又睡了。
- **正确做法**：**在 sendPacket 开头发送前**再强制 `set_ps(NONE) + scan_stop() + ensureChannel() + delay(20)` 让射频稳定再发。

### 坑 8：ESP-NOW 唯一稳定的组合是开 promiscuous —— 但也说明设计错了

- **现象**：所有组合里，**只有 mode=3 + 开启 promiscuous（混杂模式抓帧）时收过一次**。
- **根因**：promiscuous 强制射频持续接收不睡 + 驱动层不过滤未关联 vendor action frame，正好抵消了坑 2、坑 6。但靠 promiscuous 当常规机制本身就是 workaround。
- **教训**：**当一个协议需要靠混杂模式才能稳定跑通时，说明选型错了。** 这正是放弃 ESP-NOW 改用 HTTP 的导火索。

---

## 四、返回码误读坑（最误导判断）

### 坑 9：单播 FAILED ≠ 没收到

- **现象**：发送端日志 `Send -> 对端MAC: FAILED` 满天飞，以为对端没收到。
- **根因**：STA→AP 未关联时，发单播**拿不到 MAC 层 ACK**，所以 `esp_now_send` 返回 FAILED。但**接收端 ESP-NOW 回调照样能收到帧**（接收不依赖 MAC ACK）。
- **正确做法**：单播 FAILED 只是"没拿到硬件回执"，不代表送达失败。主送达应靠**广播 + 应用层 ACK（接收端回一个广播 ACK）**。

### 坑 10：广播 SUCCESS ≠ 对端收到

- **现象**：广播每轮都 SUCCESS，但接收端没反应。
- **根因**：广播无 ACK，SUCCESS 只代表发出去了。物理层（射频睡眠/信道不对/对端没在收）任一环节出问题都对端收不到。

### 坑 11：错误码 12393 = ESP_ERR_ESPNOW_NOT_FOUND

- **根因**：广播发送前**没有 add_peer(FF:FF:FF:FF:FF:FF)**。ESP-NOW 任何发送（含广播）都必须先注册 peer。
- **正确做法**：初始化时务必 `esp_now_add_peer` 注册广播 peer。

---

## 五、MAC 地址坑

### 坑 12：C3 双接口 MAC 写死 = 换板即废

- **现象**：换了一块 C3 经典款后，写死的旧板 MAC 单播全 FAILED。
- **根因**：ESP32-C3 有 STA 和 softAP 两个接口 MAC，关系为 **AP MAC = STA MAC + 1**（如 STA=...27:28 / AP=...27:29）。旧代码写死了旧板的 DD/DC。
- **正确做法**：**发送端从接收端心跳的源地址自动学习对端 MAC**，换板不用改代码、不用重烧发送端。每次心跳比对（接收端 APSTA→AP 切换时源 MAC 会从 STA 接口 MAC 变到 AP 接口 MAC，要跟着更新 peer）。

---

## 六、调试 / 工具坑

### 坑 13：`esp_core_dump_flash: No core dump partition found!` 不是崩溃

- **现象**：板子反复打印这条，以为崩溃循环。
- **根因**：只是固件没划 core dump 分区，无害提示。程序一直在跑（灯亮就是证据）。

### 坑 14：SuperMini vs 经典款串口差异（看不到日志）

- **现象**：换经典款后串口只剩 core dump 那一条，看不到任何 WLED 应用日志。
- **根因**：SuperMini 是原生 USB CDC，`Serial` 走 USB；**经典款 USB 口接的是 CH340→UART0**。WLED 的 esp32c3dev 编译配置默认 `ARDUINO_USB_CDC_ON_BOOT=1`，`Serial` 走 USB CDC 引脚，而经典款 USB 口接的是 CH340→UART0，日志全输出到没人接的 USB CDC 引脚。
- **正确做法**：`platformio.ini` esp32c3dev env 里 `CDC_ON_BOOT=1` 改成 `0`，让 `Serial` 走 UART0，经典款 CH340 才能看日志。

### 坑 15：USB CDC 串口在无主机时阻塞

- **现象**：用电脑数据线供电很快，用充电器供电按键后灯要 2~3 秒才亮。
- **根因**：没有电脑主机取数据时，每次 `Serial.print` 都阻塞到超时（几十~几百 ms），按键一次打十几行日志累积成卡顿。
- **正确做法**：加 `DEBUG_SERIAL` 这类编译期开关，脱离电脑供电时设 0 = 零打印零阻塞。

---

## 七、WLED 应用层坑（改色）

### 坑 16：直接改 seg 颜色会被 colorUpdated 覆盖（"闪一下变回手机色"）

- **根因**：WLED 的 `colorUpdated()` 内部先调 `applyValuesToSelectedSegs()`，把全局 UI 状态（colPri/effectCurrent 等）强制写回所有选中段，覆盖掉 usermod 直接写入段的颜色。
- **正确做法**：先写全局 `colPri[]` + `effectCurrent` + `effectPalette`，再写主段，最后 `applyFinalBri()` + `colorUpdated(CALL_MODE_DIRECT_CHANGE)`。

### 坑 17：只改 bri 不改 briT 会被过渡引擎拉回

- **正确做法**：`applyFinalBri()` 同步 bri/briT 两者。

### 坑 18：usermod 回调在 WiFi 任务上下文，不能直接操作 strip

- **根因**：ESP-NOW 接收回调跑在 WiFi 任务上下文，直接操作 `strip`/`bri` 会踩内存。
- **正确做法**：回调里只用 `portMUX` 临界区拷贝数据 + 置标志，真正上色放到 usermod 的 `loop()`（主循环）里做。

---

## 八、最终结论

| 维度           | ESP-NOW                              | WiFi HTTP                    | **BLE（NimBLE，最终落地）**                               |
| -------------- | ------------------------------------ | ---------------------------- | --------------------------------------------------------- |
| 传输可靠性     | UDP 类，无 ACK，靠应用层补           | TCP，原生可靠                | 链路层 ACK + 重传，原生可靠                               |
| 接收端         | 需自写 usermod + 心跳 + ACK + 重挂载 | WLED 原生 `/win` API，零代码 | 接收端需一个 GATT Server（自定义 service/characteristic） |
| 省电/射频      | modem sleep 反复踩坑                 | STA 常驻射频，较费电         | 连接态 μA 级，最省电                                      |
| 换板           | 需自动学 MAC（仍不稳）               | 只改 IP，稳                  | **按 service UUID 扫描发现，MAC 无关，换板零改动**        |
| 重启后         | 偶发失联，需按键前 refresh           | TCP 自动重连                 | `onDisconnect` 回调 + 发送前自动重连                      |
| 是否需要路由器 | 不需要                               | 需要 WLED AP（或路由器）     | **不需要**                                                |
| 固件体积       | 小                                   | 大（TCP/IP 协议栈）          | 小（NimBLE 轻量）                                         |

**一句话教训（更正）**：ESP-NOW 适合"不依赖 IP、极低功耗、近距离一对多广播"的场景；在"无路由器、只用 AP、要求稳定点对点"的场景下，它的 WiFi 模式绑定 + 省电 + 接口绑定三大坑会反复发作。**但正解不是唯一的**——本项目的实际落地是 **BLE（NimBLE）**：它同样不需要路由器、点对点、比 WiFi 更省电，且连接管理/重传/重连由 BLE 协议栈原生搞定，正好绕开了 ESP-NOW 那三大坑。WiFi HTTP 也是可选方案（需路由器或 WLED AP），但 BLE 在这个"无路由器 + 低功耗 + 即时点对点"场景下是最契合的选择。

**为什么 BLE 天然避开了 ESP-NOW 的所有坑：**

1. **没有 STA/AP 接口绑定问题**（坑 2/3）→ BLE 是连接式，没有 ESP-NOW 那种"recv 绑 STA 接口、纯 AP 收不到"的怪事。
2. **没有 modem sleep 假成功**（坑 6）→ NimBLE 管射频功耗，`writeValue()` 返回 true 即代表链路层已发出并确认，不会出现"返回 SUCCESS 帧却没发出去"。
3. **返回码语义清晰**（坑 9/10）→ BLE 写有链路层确认，不像 ESP-NOW 单播 FAILED≠没收到、广播 SUCCESS≠对端收到。
4. **换板零改动**（坑 12）→ 按 service UUID 扫描发现对端，根本不依赖 MAC。
5. **重启后自动恢复**（17:26 的坑）→ `onDisconnect` 回调重置状态 + `sendColorBLE()` 发送前自动重连，协议栈层面解决。
