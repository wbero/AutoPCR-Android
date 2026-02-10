# AutoPCR Android 移植版

这是 [AutoPCR](https://github.com/cc004/autopcr) 项目的 Android 平台移植版本，基于 CC BY-NC-SA 4.0 许可证。

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/wbero/AutoPCR-Android)](https://github.com/wbero/AutoPCR-Android/releases)
[![GitHub](https://img.shields.io/github/license/wbero/AutoPCR-Android)](https://github.com/wbero/AutoPCR-Android/blob/master/LICENSE)

## 项目简介

AutoPCR 是一个用于 Princess Connect! Re:Dive 游戏的辅助工具，提供多种功能如角色数据查询、装备计算、公会战管理等。本项目将其移植到 Android 平台，方便移动端用户使用。

**最新版本**: v1.0.1 (2026-02-10) - [下载 APK](https://github.com/wbero/AutoPCR-Android/releases)

## 技术栈

- **Android 开发**：Java/Kotlin
- **Python 版本**：3.11
- **Python 嵌入方案**：[Chaquopy](https://chaquo.com/chaquopy/)
- **Web 框架**：Quart (异步 Web 框架)
- **数据库**：SQLAlchemy
- **其他主要依赖**：
  - aiohttp
  - pycryptodome
  - UnityPy
  - Pillow
  - PuLP

## 项目结构

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
├── build.gradle             # 项目构建配置
├── settings.gradle          # 项目设置
└── README.md                # 项目说明文档
```

## 功能特性

### 🎯 核心功能
- ✅ **完整的 AutoPCR 功能移植** - 所有原版功能均完美适配 Android
- ✅ **本地 HTTP 服务器** - 无需网络连接，通过浏览器访问管理界面
- ✅ **后台服务运行** - 应用最小化后仍可继续工作
- ✅ **多架构支持** - 兼容 ARM64-v8a 和 armeabi-v7a 设备

### 🚀 新增功能 (v1.0.1)
- 🌊 **深渊探索模块** - 新增 abyss.py 功能模块
- 🔮 **幻境系统** - 新增 mirage.py 功能模块  
- 📊 **数据库优化** - 改进数据管理性能和稳定性
- 🌐 **Web 界面增强** - 新增数据库更新和启动页面
- 🛠️ **错误处理改进** - 更友好的错误提示和恢复机制

### 📱 用户体验
- 🎨 **优化的 UI 布局** - 更符合移动端使用习惯
- ⚡ **快速启动** - 优化启动流程，减少等待时间
- 📝 **详细日志** - 完整的运行日志便于问题排查

## 🛠️ 开发与编译

### 📋 环境要求

- **IDE**: Android Studio 2022.3.1 或更高版本
- **JDK**: 17 或更高版本
- **Android SDK**: 33 或更高版本
- **Python**: 3.11
- **构建工具**: Gradle 8.2+

### 🔧 编译步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/wbero/AutoPCR-Android.git
   cd AutoPCR-Android
   ```

2. **导入项目**
   - 使用 Android Studio 打开项目目录
   - 等待 Gradle 同步完成

3. **连接设备**
   - 连接 Android 设备或启动模拟器
   - 确保设备已开启 USB 调试

4. **编译运行**
   - 点击 Android Studio 的 "Run" 按钮
   - 或使用命令行编译：

   ```bash
   # 编译调试版本
   ./gradlew assembleDebug
   
   # 编译发布版本
   ./gradlew assembleRelease
   ```

### 📦 生成发布版本

```bash
# 清理并构建
./gradlew clean assembleRelease

# 生成的 APK 位置
ls app/build/outputs/apk/release/
```

### 🎯 项目结构说明

```
android_project/
├── app/                     
│   ├── src/main/            
│   │   ├── assets/          # 静态资源文件
│   │   ├── java/            # Android Java 代码
│   │   │   └── com/autopcr/mobile/
│   │   │       ├── MainActivity.java    # 主活动
│   │   │       └── AutoPCRService.java  # 后台服务
│   │   ├── python/          # Python 核心代码
│   │   │   ├── UnityPy/     # Unity 资源处理
│   │   │   ├── autopcr/     # AutoPCR 核心功能
│   │   │   ├── android_main.py  # Android 启动入口
│   │   │   └── patch_env.py     # 环境适配补丁
│   │   └── res/             # Android 资源文件
│   ├── build.gradle         # 模块构建配置
│   └── version.properties   # 版本配置文件
├── releases/                # 发布文件目录
│   ├── AutoPCR-v1.0.1.apk   # 发布版 APK
│   └── RELEASE_NOTES_v1.0.1.md  # 发布说明
└── build.gradle             # 项目构建配置
```

## 📲 安装与使用

### 📥 下载安装
1. 前往 [GitHub Releases](https://github.com/wbero/AutoPCR-Android/releases) 页面
2. 下载最新版本的 `AutoPCR-v1.0.1.apk`
3. 在 Android 设备上启用"未知来源"安装：
   - 设置 → 安全 → 未知来源
4. 点击 APK 文件进行安装

### 🚀 快速开始
1. 打开 AutoPCR 应用
2. 等待服务启动完成（首次运行需要初始化）
3. 访问 `http://localhost:8080` 使用 Web 管理界面
4. 应用支持后台运行，可在通知栏管理服务状态

### 📋 系统要求
- **Android 版本**: 5.0 (API 21) 或更高
- **处理器架构**: ARM64-v8a 或 armeabi-v7a
- **内存**: 建议 2GB 以上
- **存储空间**: 至少 100MB 可用空间

## 核心代码说明

### android_main.py
Android 平台的启动入口脚本，负责：
- 应用环境补丁
- 初始化事件循环
- 启动 HTTP 服务器
- 初始化数据库和定时任务

### patch_env.py
Android 环境适配补丁，主要功能：
- 重定向标准输出到 Android Logcat
- 同步 assets 中的数据文件到可写目录
- 修改路径配置以适配 Android 环境

## 许可证

本项目基于 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证发布。

## 原项目信息

- 原项目地址：[https://github.com/cc004/autopcr](https://github.com/cc004/autopcr)
- 原作者：cc004
- 原许可证：CC BY-NC-SA 4.0

## 🤝 贡献与支持

### 🐛 问题反馈
如遇到问题或有功能建议，请：
1. 查看 [已知问题](#注意事项) 部分
2. 在 [GitHub Issues](https://github.com/wbero/AutoPCR-Android/issues) 提交问题
3. 提供详细的设备信息和错误日志

### 💡 贡献指南
欢迎提交 Pull Request！
- Fork 项目并创建功能分支
- 确保代码符合项目规范
- 添加必要的测试和文档
- 提交 Pull Request 并描述变更内容

### 📧 联系方式
- **GitHub**: [wbero/AutoPCR-Android](https://github.com/wbero/AutoPCR-Android)
- **原项目**: [cc004/autopcr](https://github.com/cc004/autopcr)

## 📝 版本历史

### v1.0.1 (2026-02-10)
- 🌊 新增深渊探索功能模块
- 🔮 新增幻境系统功能模块
- 📊 优化数据库性能和稳定性
- 🌐 增强 Web 管理界面
- 🎨 改进用户界面布局
- 🛠️ 增强错误处理机制

### v1.0.0 (2025-11-26)
- 🚀 初始版本发布
- ✅ 完成 AutoPCR 核心功能移植
- ✅ 实现本地 HTTP 服务器
- ✅ 支持后台服务运行

## ⚠️ 注意事项

### 🎮 使用须知
1. **学习研究用途** - 本项目仅用于学习和研究目的
2. **遵守游戏协议** - 请遵守 Princess Connect! Re:Dive 的用户协议
3. **非商业用途** - 禁止用于商业盈利活动
4. **风险自担** - 作者不对使用后果承担任何责任

### 📱 兼容性说明
- 某些 Android 设备可能存在兼容性问题
- 部分功能需要稳定的网络连接
- 首次运行可能需要较长时间初始化
- 建议在充电状态下使用以避免电池消耗过快

### 🔒 安全提醒
- 请从官方 GitHub 仓库下载 APK
- 注意保护个人游戏账号安全
- 定期更新到最新版本以获得安全修复
