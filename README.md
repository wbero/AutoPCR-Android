# AutoPCR Android 移植版

这是 [AutoPCR](https://github.com/cc004/autopcr) 项目的 Android 平台移植版本，基于 CC BY-NC-SA 4.0 许可证。

## 项目简介

AutoPCR 是一个用于 Princess Connect! Re:Dive 游戏的辅助工具，提供多种功能如角色数据查询、装备计算、公会战管理等。本项目将其移植到 Android 平台，方便移动端用户使用。

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

- ✅ 完整移植原 AutoPCR 功能
- ✅ 本地 HTTP 服务器，无需网络连接
- ✅ 适配 Android 环境的路径处理
- ✅ 自动同步资源文件
- ✅ 支持后台运行

## 编译与构建

### 环境要求

- Android Studio 2022.3.1 或更高版本
- JDK 17
- Android SDK 33 或更高版本
- Python 3.11

### 编译步骤

1. 克隆项目到本地
2. 使用 Android Studio 打开项目
3. 等待 Gradle 同步完成
4. 连接 Android 设备或启动模拟器
5. 点击 "Run" 按钮编译并安装应用

### 生成发布版本

```bash
# 在项目根目录执行
./gradlew assembleRelease
```

生成的 APK 文件将位于 `app/release/autopcr.apk`

## 使用说明

1. 安装 APK 文件到 Android 设备
2. 打开应用，等待服务启动
3. 在浏览器中访问 `http://127.0.0.1:8000`
4. 开始使用 AutoPCR 功能

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

## 贡献

欢迎提交 Issue 和 Pull Request！

## 注意事项

1. 本项目仅用于学习和研究目的
2. 请遵守游戏的用户协议
3. 请勿用于商业用途
4. 作者不对使用本项目产生的任何后果负责
