# 现代绘图工具

一个基于PyQt5开发的绘图软件，类似于微软的画图，提供了一系列现代UI并实现了完整的绘图功能。该项目支持在Windows上开发和测试，并可通过Buildozer打包为安卓应用程序。

## 功能特性

### 绘图工具
- 自由绘制（画笔）
- 基本形状绘制（矩形、椭圆、直线、三角形）
- 选择工具（框选缩放、框选旋转）
- 颜色选择（线条颜色、填充颜色）
- 线条宽度调整

### 编辑功能
- 撤销/重做操作
- 清除画布
- 缩放和旋转选区内的内容

### 文件操作
- 新建文件
- 打开现有图像文件
- 保存绘图作品

## 安装和开发

### 开发环境设置

1. 确保您的系统上安装了Python 3.6或更高版本

2. 安装项目依赖

```bash
pip install -r requirements.txt
```

### 在Windows上运行

在开发过程中，您可以直接在Windows上运行应用程序进行测试：

```bash
python main.py
```

## 打包为安卓应用程序

本项目使用Buildozer将PyQt5应用程序打包为安卓应用程序。由于Buildozer在Windows上的配置较为复杂，建议在Linux环境下进行打包操作。

### 准备Linux环境

1. 在Linux系统上安装Buildozer

```bash
pip install buildozer
```

2. 初始化Buildozer环境

```bash
buildozer init
```

3. 复制项目文件到Linux环境

将项目中的`main.py`、`buildozer.spec`和`requirements.txt`文件复制到Linux环境中。

### 配置Buildozer

1. 打开`buildozer.spec`文件，根据需要调整配置参数

2. 确保以下配置项正确设置：
   - `requirements = python3,kivy==2.2.1,pyqt5,sdl2_ttf`
   - `android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE`
   - `android.api = 31`
   - `android.minapi = 21`

### 构建安卓应用程序

1. 运行Buildozer构建命令

```bash
buildozer android debug
```

2. 构建完成后，APK文件将位于`bin`目录下

## 项目结构

- `main.py`：主程序文件，包含应用程序的核心功能实现
- `buildozer.spec`：Buildozer配置文件，用于打包安卓应用程序
- `requirements.txt`：项目依赖列表

## 开发说明

### 主要类结构

- `DrawingCanvas`：绘图画布类，负责处理绘图逻辑和用户交互
- `DrawingApp`：主应用程序类，负责创建UI界面和连接各个组件

### 扩展和修改

如果您想扩展或修改此应用程序，可以考虑以下几点：

1. 添加更多绘图工具（如多边形、文本工具等）
2. 改进UI设计和用户体验
3. 添加更多图像编辑功能（如滤镜、渐变等）
4. 优化在不同设备上的显示效果

## 注意事项

1. 由于PyQt5在安卓平台上的兼容性限制，某些高级功能可能在安卓设备上表现不同

2. 在打包安卓应用程序时，可能需要根据您的具体环境调整`buildozer.spec`文件中的配置参数

3. 对于复杂的绘图操作，建议在Windows上进行开发和测试，确保功能正常后再打包为安卓应用程序

## 贡献
滑稽主教（FunnyBishop）
您可以通过提交Pull Request的方式贡献代码。
如果您发现任何问题或有改进建议，请随时创建Issue。

##使用方法
使用选择工具框选公式并右键点击，选择“解方程”即可解方程。
解出的方程会以LaTeX格式显示在提示框中。
