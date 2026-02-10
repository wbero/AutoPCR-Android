# AutoPCR Android 移植文档

## 1. 移植概述

### 1.1 项目背景
AutoPCR 是一个用于 Princess Connect! Re:Dive 游戏的辅助工具，最初为桌面平台开发。本移植项目将其适配到 Android 平台，使移动设备用户能够便捷使用。

### 1.2 移植目标
- ✅ 完整保留原AutoPCR的所有核心功能
- ✅ 适配Android平台的文件系统和运行环境
- ✅ 优化移动设备的资源占用和电池消耗
- ✅ 提供简洁的用户界面和服务管理
- ✅ 支持后台运行和自动启动

### 1.3 技术栈
| 技术 | 版本/说明 |
|------|-----------|
| Java/Kotlin | Android 开发语言 |
| Python | 3.11 |
| Chaquopy | Python 嵌入框架 |
| Quart | 异步 Web 框架 |
| SQLAlchemy | ORM 数据库框架 |
| Android SDK | 33+ |

## 2. 项目结构

### 2.1 目录结构
```
android_project/
├── app/                     # Android 应用主目录
│   ├── src/main/            # 源代码目录
│   │   ├── assets/          # 静态资源
│   │   ├── java/            # Java/Kotlin 代码
│   │   ├── python/          # Python 代码
│   │   │   ├── UnityPy/     # Unity 资源处理库
│   │   │   ├── autopcr/     # 原 AutoPCR 核心代码
│   │   │   ├── android_main.py  # Android 启动入口
│   │   │   └── patch_env.py     # Android 环境补丁
│   │   └── AndroidManifest.xml  # Android 配置文件
│   ├── build.gradle         # 模块构建配置
│   └── release/             # 发布版本输出目录
├── gradle/                  # Gradle 包装器
├── .gitignore               # Git 忽略规则
├── README.md                # 项目说明文档
├── PORTING_GUIDE.md         # 本移植文档
├── build.gradle             # 项目构建配置
├── gradle.properties        # Gradle 属性配置
└── settings.gradle          # 项目设置
```

### 2.2 核心文件说明

| 文件 | 功能描述 |
|------|----------|
| `android_main.py` | Android 平台启动入口，负责初始化环境和启动服务器 |
| `patch_env.py` | Android 环境适配补丁，处理路径、日志和资源同步 |
| `build.gradle` | 配置 Chaquopy 和 Python 依赖 |
| `AndroidManifest.xml` | 配置应用权限和服务 |

## 3. 环境适配

### 3.1 文件系统适配

#### 3.1.1 路径重定向
```python
# patch_env.py
constants.ROOT_DIR = android_root
constants.CACHE_DIR = os.path.join(android_root, 'cache/')
constants.RESULT_DIR = os.path.join(android_root, 'result/')
constants.DATA_DIR = os.path.join(android_root, 'data/')
constants.CONFIG_PATH = os.path.join(constants.CACHE_DIR, 'http_server/')
```

#### 3.1.2 资源同步机制
- **目的**：将打包在 assets 中的数据文件同步到可写目录
- **实现**：递归遍历 assets 目录，复制不存在的文件
- **优化**：只复制新增或修改的文件，减少启动时间

### 3.2 日志系统适配

#### 3.2.1 重定向标准输出
```python
# patch_env.py
class LogcatWriter:
    def __init__(self, level):
        self.level = level
        from android.util import Log
        self.Log = Log
        self.tag = "AutoPCR_Py"

    def write(self, message):
        if message.strip():
            for line in message.rstrip().splitlines():
                if self.level == 'I':
                    self.Log.i(self.tag, line)
                elif self.level == 'E':
                    self.Log.e(self.tag, line)

# 应用重定向
sys.stdout = LogcatWriter('I')
sys.stderr = LogcatWriter('E')
```

### 3.3 网络适配

#### 3.3.1 本地服务器配置
- **绑定地址**：127.0.0.1
- **端口**：与原项目保持一致
- **前端资源**：动态计算前端资源路径

## 4. 启动流程

### 4.1 启动流程图
```
┌───────────────────┐     ┌────────────────────┐     ┌──────────────────┐
│ 应用启动         │────>│ 应用环境补丁       │────>│ 初始化事件循环   │
└───────────────────┘     └────────────────────┘     └──────────────────┘
          ^                          │                          │
          │                          v                          v
┌───────────────────┐     ┌────────────────────┐     ┌──────────────────┐
│ 服务状态监控     │<────│ 启动HTTP服务器    │<────│ 初始化数据库     │
└───────────────────┘     └────────────────────┘     └──────────────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     │
                                     v
                            ┌───────────────────┐
                            │ 后台运行服务     │
                            └───────────────────┘
```

### 4.2 启动入口详解

#### 4.2.1 初始化环境
```python
# android_main.py
async def start_server():
    logger.info("正在初始化 AutoPCR Android 服务...")
    
    try:
        # 导入并应用环境补丁
        import patch_env
        patch_env.apply_android_patches()
        
        logger.info("环境补丁已应用，正在启动服务器...")
```

#### 4.2.2 启动服务器
```python
# android_main.py
# 导入原有的服务器模块
import asyncio
from autopcr.http_server.httpserver import HttpServer
from autopcr.constants import SERVER_PORT
from autopcr.db.dbstart import db_start
from autopcr.module.crons import queue_crons

# 创建事件循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# 关键修复：计算并传递前端资源的绝对路径
import autopcr.http_server
http_server_path = os.path.dirname(os.path.abspath(autopcr.http_server.__file__))
static_dir = os.path.join(http_server_path, 'ClientApp')

# 初始化服务器
server = HttpServer(host='127.0.0.1', port=SERVER_PORT, static_dir=static_dir)

# 初始化数据库和定时任务
queue_crons()
loop.create_task(db_start())

logger.info(f"服务器正在启动，监听 127.0.0.1:{SERVER_PORT}")

# 启动服务器
server.run_forever(loop)
```

## 5. 功能适配

### 5.1 核心功能保留
- ✅ 公会战管理和伤害统计
- ✅ 任务自动完成
- ✅ 装备计算和优化
- ✅ 角色数据查询
- ✅ 商店购买和管理
- ✅ 活动任务处理

### 5.2 Android 特化功能

#### 5.2.1 后台运行
- **实现方式**：使用前台服务 + 通知
- **优势**：避免被系统杀死，确保服务持续运行
- **配置**：在 AndroidManifest.xml 中声明服务

#### 5.2.2 服务管理
- **通知控制**：通过通知栏快速启动/停止服务
- **设置界面**：提供简单的设置选项
- **状态监控**：显示服务运行状态和资源占用

#### 5.2.3 资源优化
- **内存管理**：定期清理缓存，优化内存使用
- **电池优化**：智能调度任务，避免过度耗电
- **网络优化**：减少网络请求，优化数据传输

## 6. 构建与部署

### 6.1 环境要求
- Android Studio 2022.3.1 或更高版本
- JDK 17
- Android SDK 33 或更高版本
- Python 3.11
- 有效的 Android 开发者签名

### 6.2 构建步骤
1. **克隆项目**：`git clone https://github.com/wbero/AutoPCR-Android.git`
2. **打开项目**：在 Android Studio 中打开项目
3. **同步依赖**：等待 Gradle 同步完成
4. **配置签名**：在 build.gradle 中配置签名信息
5. **构建变体**：
   - **Debug**：用于开发和测试
   - **Release**：用于发布

### 6.3 发布流程
1. **构建发布版本**：`./gradlew assembleRelease`
2. **签名 APK**：使用 keystore 签名应用
3. **验证应用**：安装并测试发布版本
4. **发布**：上传到 GitHub Releases 或其他分发渠道

### 6.4 自动构建（CI/CD）
可配置 GitHub Actions 实现自动构建和发布：
- **触发条件**：推送标签或手动触发
- **构建步骤**：安装依赖、构建、签名、发布
- **输出**：发布版本 APK

## 7. 故障排查

### 7.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 服务启动失败 | 权限不足 | 检查应用权限设置 |
| 内存占用过高 | Python 进程内存泄漏 | 重启服务，检查日志 |
| 电池消耗过快 | 后台任务过于频繁 | 调整任务调度频率 |
| 前端资源加载失败 | 路径计算错误 | 检查静态资源路径 |
| 数据库连接失败 | 权限或路径问题 | 检查数据目录权限 |

### 7.2 日志分析
- **应用日志**：通过 Logcat 查看
  ```bash
  adb logcat | grep AutoPCR
  ```
- **Python 日志**：在应用数据目录中查看
  ```
  /data/data/com.autopcr.mobile/files/autopcr_data/log/
  ```
- **网络日志**：使用 Charles 或 Fiddler 抓包

### 7.3 调试工具
- **Android Studio Debugger**：调试 Java/Kotlin 代码
- **Frida**：动态调试 Python 代码
- **Chaquopy 调试**：使用 Chaquopy 的调试功能

## 8. 性能优化

### 8.1 内存优化
- **懒加载**：延迟加载非必要资源
- **缓存管理**：定期清理过期缓存
- **内存监控**：监控内存使用，及时释放

### 8.2 电池优化
- **任务调度**：集中执行任务，减少唤醒频率
- **网络请求**：批量处理网络请求
- **后台限制**：遵守 Android 后台限制策略

### 8.3 启动速度
- **资源预加载**：优化资源加载顺序
- **并行处理**：使用异步操作并行处理任务
- **启动时间监控**：测量并优化启动时间

## 9. 未来规划

### 9.1 功能增强
- ✅ 推送通知：任务完成、公会战提醒
- ✅ 远程控制：通过网络远程管理服务
- ✅ 数据分析：提供更详细的游戏数据分析
- ✅ 多账号支持：管理多个游戏账号

### 9.2 技术升级
- ✅ Python 版本更新：适配最新 Python 版本
- ✅ Android 版本适配：支持最新 Android 版本
- ✅ 性能优化：进一步提升性能和稳定性
- ✅ 安全加固：增强应用安全性

### 9.3 平台扩展
- ✅ iOS 移植：考虑移植到 iOS 平台
- ✅ Web 界面：提供更完善的 Web 管理界面
- ✅ 云同步：支持配置和数据的云同步

## 10. 贡献指南

### 10.1 开发流程
1. **Fork 仓库**：创建个人 fork
2. **创建分支**：`git checkout -b feature/your-feature`
3. **开发**：实现功能或修复 bug
4. **测试**：确保代码正常工作
5. **提交**：`git commit -m "Add your feature"`
6. **推送**：`git push origin feature/your-feature`
7. **PR**：创建 Pull Request

### 10.2 代码规范
- **Python**：遵循 PEP 8 规范
- **Java/Kotlin**：遵循 Android 代码规范
- **命名**：使用清晰、描述性的命名
- **注释**：关键代码添加注释
- **测试**：为新功能添加测试

### 10.3 文档规范
- **更新 README.md**：记录重要变更
- **更新 PORTING_GUIDE.md**：记录架构和流程变更
- **提交信息**：使用清晰、简洁的提交信息

## 11. 许可证

本项目基于 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证发布。

### 11.1 许可证说明
- **BY**：必须给出适当的署名
- **NC**：非商业用途
- **SA**：以相同方式共享

### 11.2 原项目信息
- **项目地址**：[https://github.com/cc004/autopcr](https://github.com/cc004/autopcr)
- **作者**：cc004
- **许可证**：CC BY-NC-SA 4.0

## 12. 联系方式

### 12.1 项目维护者
- **GitHub**：[wbero](https://github.com/wbero)
- **邮箱**：[wbero@example.com](mailto:wbero@example.com)

### 12.2 社区支持
- **GitHub Issues**：报告 bug 和提出功能请求
- **Discussions**：讨论使用问题和开发建议
- **贡献**：欢迎提交 Pull Request

## 13. 致谢

- **原作者 cc004**：创建了优秀的 AutoPCR 项目
- **Chaquopy 团队**：提供了强大的 Python 嵌入方案
- **社区贡献者**：提供了宝贵的建议和代码贡献
- **Princess Connect! Re:Dive 玩家**：使用和反馈

---

**文档版本**：v1.0.0  
**最后更新**：2026-01-30  
**维护者**：AutoPCR Android 移植团队