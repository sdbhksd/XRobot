# XRobot 自动代码生成工具集 / XRobot Auto Code Generation Toolkit

<h1 align="center">
<img src="https://github.com/Jiu-xiao/LibXR_CppCodeGenerator/raw/main/imgs/XRobot.jpeg" width="300">
</h1><br>

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![GitHub Repo](https://img.shields.io/github/stars/xrobot-org/XRobot?style=social)](https://github.com/Jiu-xiao/libxr)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen)](https://xrobot-org.github.io/)
[![GitHub Issues](https://img.shields.io/github/issues/xrobot-org/XRobot)](https://github.com/xrobot-org/XRobot/issues)
[![CI/CD - Python Package](https://github.com/xrobot-org/XRobot/actions/workflows/python-publish.yml/badge.svg)](https://github.com/xrobot-org/XRobot/actions/workflows/python-publish.yml)

XRobot 是一套为嵌入式系统（如 STM32）设计的自动化代码生成工具，配合模块化硬件抽象层 LibXR 使用，支持模块仓库管理、构造参数配置、C++ 主函数生成等任务。  
XRobot is a suite of automated code generation tools for embedded systems (e.g., STM32), designed to work with the modular hardware abstraction layer LibXR. It supports tasks such as module repository management, constructor configuration, and C++ main function generation.

---

## 🔧 安装 / Installation

```bash
pip install xrobot
```

或从源码安装：

Or install from source:

```bash
git clone https://github.com/xrobot-org/XRobot.git
cd XRobot
pip install .
```

---

## 🧩 功能总览 / Features Overview

- 模块仓库拉取与同步  
Clone and update module repositories
- 模块构造参数提取与配置  
Extract and configure constructor arguments
- 自动生成 `XRobotMain()` 主入口函数  
Auto-generate `XRobotMain()` main entry
- 模块头文件中的 manifest 解析器  
Manifest parser from header files
- 模块快速生成器（含 CMake 和 README）  
Module skeleton generator (with CMake & README)
- 支持本地或远程 YAML 配置  
Support local or remote YAML config

---

## 🚀 命令行工具 / CLI Tools

以下命令在安装后可直接调用：

The following commands can be run after installation:

| 命令 Command        | 说明                         | Description                         |
| ------------------- | ---------------------------- | ----------------------------------- |
| `xrobot_add_mod`    | 添加模块仓库或模块实例       | Add repo or append module config    |
| `xrobot_init_mod`   | 拉取并同步所有模块仓库       | Clone and sync all module repos     |
| `xrobot_gen_main`   | 生成 C++ 主函数              | Generate main C++ entry source file |
| `xrobot_create_mod` | 创建模块模板                 | Create a new module folder & header |
| `xrobot_mod_parser` | 解析模块并打印 manifest 信息 | Parse and show module manifest      |
| `xrobot_setup`      | 一键配置模块 + 生成主函数    | One-click setup & generate main     |

---

### `xrobot_add_mod`

该工具根据输入目标（Git 仓库 URL 或模块名）自动判断操作类型，分别将模块信息写入：

- `Modules/modules.yaml`（模块仓库配置）
- `User/xrobot.yaml`（模块实例配置）

This tool automatically detects the operation type (repo or local module) and writes to:

- `Modules/modules.yaml` for module repositories
- `User/xrobot.yaml` for module instance configurations

#### 🚀 使用方法 / Usage

```bash
# 添加模块仓库
# Add module repo  
# (default to Modules/modules.yaml)
python xrobot_add_mod.py https://github.com/yourorg/BlinkLED.git --version main

# 追加模块实例
# Append module instance
# (default to User/xrobot.yaml)
python xrobot_add_mod.py BlinkLED
```

#### 🎛️ 命令行参数 / Command-Line Arguments

- `target`  
  位置参数，Git 仓库地址或模块名。  
  Positional argument: Git repo URL or local module name.

- `--version`, `-v`  
  可选，指定仓库的分支或标签，仅在 `target` 为 URL 时有效。  
  Optional version (branch or tag), valid only when target is a repo URL.

- `--config`, `-c`  
  可选，指定 YAML 配置文件路径。模块仓库默认写入 `Modules/modules.yaml`，模块实例默认写入 `User/xrobot.yaml`。  
  Optional config file path. Defaults to `Modules/modules.yaml` for repos or `User/xrobot.yaml` for instances.

#### 📤 输出结果 / Output

- 添加模块仓库  
  会将如下内容添加到 `Modules/modules.yaml`：  

  ```yaml
  modules:
    - name: BlinkLED
      repo: https://github.com/yourorg/BlinkLED.git
      version: main
  ```

- 追加模块实例  
  自动读取模块头文件中的构造参数，并将如下内容追加到 `User/xrobot.yaml`：  

  ```yaml
  modules:
    - name: BlinkLED
      constructor_args:
        your_arg_name_here: <default or empty>
  ```

#### 示例 / Example

MODULES/module_name/module_name.hpp

```cpp
/* === MODULE MANIFEST ===
module_name: BMI088
module_description: 博世 BMI088 6 轴惯性测量单元（IMU）的驱动模块 / Driver module for Bosch BMI088 6-axis Inertial Measurement Unit (IMU)
constructor_args:
  - rotation:
      w: 1.0
      x: 0.0
      y: 0.0
      z: 0.0
  - pid_param:
      k: 1.0
      p: 0.0
      i: 0.0
      d: 0.0
      i_limit: 0.0
      out_limit: 0.0
      cycle: false
  - gyro_topic_name: "bmi088_gyro"
  - accl_topic_name: "bmi088_accl"
  - target_temperature: 45
  - task_stack_depth: 512
required_hardware: spi_bmi088/spi1/SPI1 bmi088_accl_cs bmi088_gyro_cs bmi088_accl_int bmi088_gyro_int pwm_bmi088_heat ramfs database
repository: https://github.com/xrobot-org/BMI088
=== END MANIFEST === */
```

modules.yaml

```yaml
modules:
- name: BlinkLED
  repo: https://github.com/xrobot-org/BlinkLED
- name: BMI088
  repo: https://github.com/xrobot-org/BMI088
- name: MadgwickAHRS
  repo: https://github.com/xrobot-org/MadgwickAHRS
```

User/xrobot.yaml

```yaml
global_settings:
  monitor_sleep_ms: 1000
modules:
- name: BlinkLED
  constructor_args:
    blink_cycle: 250
- name: BMI088
  constructor_args:
    rotation:
      w: 1.0
      x: 0.0
      y: 0.0
      z: 0.0
    pid_param:
      k: 0.15
      p: 1.0
      i: 0.1
      d: 0.0
      i_limit: 0.3
      out_limit: 1.0
      cycle: false
    gyro_topic_name: bmi088_gyro
    accl_topic_name: bmi088_accl
    target_temperature: 45
    task_stack_depth: 512
- name: MadgwickAHRS
  constructor_args:
    beta: 0.033
    gyro_topic_name: bmi088_gyro
    accl_topic_name: bmi088_accl
    quaternion_topic_name: ahrs_quaternion
    euler_topic_name: ahrs_euler
    task_stack_depth: 512
```

---

### `xrobot_init_mod`

该工具用于根据模块配置文件（本地或远程 YAML）自动克隆或更新模块仓库，默认拉取至 `Modules/` 目录。  
This tool clones or updates module repositories based on a YAML config file (local or remote), and stores them under the `Modules/` directory.

#### 🚀 使用方法 / Usage

```bash
# 使用默认配置文件 modules.yaml 并拉取到 Modules/
# Pull modules from modules.yaml to Modules/
xrobot_init_mod

# 指定配置文件和目录
# Specify config file and directory
xrobot_init_mod --config my_config.yaml --directory MyModules
```

#### 🎛️ 命令行参数 / Command-Line Arguments

- `--config`, `-c`  
  指定模块配置文件路径或 URL。默认为 `modules.yaml`。  
  Path or URL to the module configuration file. Default is `modules.yaml`.

- `--directory`, `-d`  
  指定模块仓库下载目录，默认为 `Modules/`。  
  Output directory for module repositories. Default is `Modules/`.

#### 📤 输出结果 / Output

- 如果配置文件不存在，将自动生成模板
  If the configuration file does not exist, a template will be generated.
- 若模块目录不存在，执行 `git clone --recurse-submodules`  
  If the module directory does not exist, `git clone --recurse-submodules` is executed.
- 若模块已存在，进入目录后执行 `git pull`，并根据配置切换分支（如果提供 `version` 字段）  
  If the module exists, enter the directory and execute `git pull`, and switch branches if a `version` field is provided.
- 每个模块最终存储在 `<output_directory>/<module_name>` 路径中  
  Each module is stored at `<output_directory>/<module_name>`.

输出示例 / Output Example：

```bash
[INFO] Cloning new module: BlinkLED
[EXEC] git clone --recurse-submodules --branch main https://github.com/xrobot-org/BlinkLED Modules/BlinkLED

[SUCCESS] All modules processed
```

### `xrobot_gen_main`

该工具用于根据模块清单和构造参数配置文件，自动生成 C++ 入口函数 `XRobotMain()`，支持嵌套参数、重复实例、多模块构造。  
This tool generates a C++ entry function `XRobotMain()` based on the module list and configuration file, supporting nested args, multiple instances, and module composition.

#### 🚀 使用方法 / Usage

```bash
# 自动发现所有模块并生成主函数
# Auto-discover modules and generate main entry
xrobot_gen_main --output User/xrobot_main.hpp

# 指定模块和构造参数配置
# Specify modules and config manually
xrobot_gen_main -o main.cpp -m BlinkLED Motor IMU --config User/xrobot.yaml
```

#### 🎛️ 命令行参数 / Command-Line Arguments

- `--output`, `-o`  
  **必填**，生成的 C++ 文件路径。  
  **Required**. Output path of generated C++ file.

- `--modules`, `-m`  
  可选，指定模块名列表；若未指定，则自动扫描 `Modules/` 目录下的模块。  
  Optional. List of module names to include. If omitted, auto-discovered from `Modules/`.

- `--hw`  
  可选，指定硬件容器变量名，默认为 `hw`。  
  Optional. Hardware container variable name. Default: `hw`.

- `--config`, `-c`  
  可选，指定构造参数 YAML 文件；若文件不存在，则自动生成。  
  Optional. Path to constructor configuration file. Will be created if not found.

#### 📤 输出结果 / Output

- 若未指定 `--config`，将扫描模块头文件中的 `/* === MODULE MANIFEST === */` 区块并生成默认 YAML  
  If `--config` is not specified, will scan for `/* === MODULE MANIFEST === */` block and generate default YAML.
- 生成一个包含 `XRobotMain()` 函数的 `.hpp` 或 `.cpp` 文件  
  Generates a `.hpp` or `.cpp` file containing the `XRobotMain()` function.
- 每个模块按 `static ModuleName<HardwareContainer> name(hw, appmgr, ...);` 格式实例化  
  Each module is instantiated as `static ModuleName<HardwareContainer> name(hw, appmgr, ...);`
- 支持自动添加头文件  
  Support for automatically adding header files
- 主循环使用 `appmgr.MonitorAll()` 与 `Thread::Sleep()`  
  Main loop uses `appmgr.MonitorAll()` and `Thread::Sleep()`

输出代码示例 / Output Code Example：

```cpp
#include "app_framework.hpp"
#include "libxr.hpp"

// Module headers
#include "BlinkLED.hpp"
#include "BMI088.hpp"
#include "MadgwickAHRS.hpp"

template <typename HardwareContainer>
static void XRobotMain(HardwareContainer &hw) {
  using namespace LibXR;
  ApplicationManager appmgr;

  // Auto-generated module instantiations
  static BlinkLED<HardwareContainer> blinkled(hw, appmgr, 250);
  static BMI088<HardwareContainer> bmi088(hw, appmgr, {1.0, 0.0, 0.0, 0.0}, {0.15, 1.0, 0.1, 0.0, 0.3, 1.0, false}, "bmi088_gyro", "bmi088_accl", 45, 512);
  static MadgwickAHRS<HardwareContainer> madgwickahrs(hw, appmgr, 0.033, "bmi088_gyro", "bmi088_accl", "ahrs_quaternion", "ahrs_euler", 512);

  while (true) {
    appmgr.MonitorAll();
    Thread::Sleep(1000);
  }
}
```

### `xrobot_create_mod`

该工具用于快速创建一个符合 XRobot 模块规范的目录结构，包含头文件、README、CMake 配置等，便于模块开发初始化。  
This tool quickly scaffolds a new XRobot module with standard files including header, README, and CMake setup, to accelerate module development.

#### 🚀 使用方法 / Usage

```bash
# 创建一个名为 MyModule 的模块
# Create a module named MyModule
xrobot_create_mod MyModule --desc "LED blinker" --hw led button --repo https://github.com/yourorg/MyModule
```

#### 🎛️ 命令行参数 / Command-Line Arguments

- `module_name`  
  **必填**，模块名称，必须与目录名一致。  
  **Required**. Module name, must match folder name.

- `--desc`  
  模块说明文字。默认值："No description provided"  
  Description text for the module. Default: "No description provided".

- `--hw`  
  所需硬件逻辑接口名列表。默认空。  
  List of required logical hardware interfaces. Default: empty.

- `--repo`  
  GitHub 仓库地址（可选）。  
  GitHub repository URL (optional).

- `--out`  
  输出路径，默认为 `Modules/`。  
  Output folder. Default: `Modules/`.

#### 📂 生成结构 / Generated Structure

假设模块名为 `BlinkLED`，会生成以下文件结构：  
If the module name is `BlinkLED`, the following structure will be generated:

```text
Modules/
└── BlinkLED/
    ├── BlinkLED.hpp        # 带 manifest 的头文件 / Header file with manifest
    ├── README.md           # 模块文档 / Module documentation
    └── CMakeLists.txt      # 构建配置 / Build configuration
```

### `xrobot_mod_parser`

该工具用于解析 XRobot 模块头文件中的 `MODULE MANIFEST`，提取模块的描述、构造参数、所需硬件等信息，并格式化输出。  
This tool parses the `MODULE MANIFEST` block in XRobot module header files, extracting the module description, constructor arguments, required hardware, and formatting the output.

#### 🚀 使用方法 / Usage

```bash
# 解析指定路径下的模块目录或模块集合
# Parse module directory or module collection at the specified path
xrobot_mod_parser --path Modules/BlinkLED
```

```bash
# 解析指定路径下的模块目录或模块集合
# Parse module directory or module collection at the specified path
xrobot_mod_parser --path ./Modules
```

#### 🎛️ 命令行参数 / Command-Line Arguments

- `--path`, `-p`  
  **必填**，模块目录路径或模块集合路径。  
  **Required**. Path to the module directory or module collection.

#### 📤 输出结果 / Output

- 输出模块描述、构造参数和所需硬件信息。  
  Prints the module description, constructor arguments, and required hardware.
  
- 如果模块头文件中的 `constructor_args` 是字典或列表形式，它会被正确解析并格式化为易读格式。  
  If `constructor_args` in the module header is in dictionary or list format, it is parsed and formatted into a readable structure.

输出示例 / Output Example：

```bash
=== Module: BlinkLED ===
Description       : 控制 LED 闪烁的简单模块 / A simple module to control LED blinking
Repository        : https://github.com/xrobot-org/BlinkLED

Constructor Args  :
  - blink_cycle        = 250

Required Hardware : led/LED/led1/LED1
```

### `xrobot_setup`

该工具用于自动配置 XRobot 环境，生成模块仓库配置、CMake 配置以及主函数代码。它通过调用 `xrobot_init_mod` 初始化模块，生成 CMake 配置，并根据构造参数自动生成主函数代码。  
This tool automates the XRobot setup, generating module repository configuration, CMake configuration, and main function code. It initializes modules via `xrobot_init_mod`, generates CMake configuration, and automatically generates the main function code based on constructor parameters.

#### 🚀 使用方法 / Usage

```bash
# 自动配置并生成主函数代码
# Auto-configure and generate main function code
xrobot_setup
```

#### 🎛️ 命令行参数 / Command-Line Arguments

- `--config`, `-c`  
  可选，指定构造参数配置文件路径，可以是本地文件或远程 URL。  
  Optional. Path to constructor configuration file, can be a local file or a URL.

#### 📤 输出结果 / Output

- **默认配置文件**：  
  如果 `Modules/modules.yaml` 不存在，脚本会生成一个默认配置文件。  
  If `Modules/modules.yaml` doesn't exist, a default configuration file will be created.
  
- **模块初始化**：  
  调用 `xrobot_init_mod` 命令初始化模块仓库，拉取模块代码。  
  Calls `xrobot_init_mod` to initialize the module repository and clone modules.

- **CMake 配置**：  
  生成 `Modules/CMakeLists.txt`，用于自动包含所有模块的构建配置。  
  Generates `Modules/CMakeLists.txt` for auto-including build configurations of all modules.

- **主函数生成**：  
  生成 `User/xrobot_main.hpp`，包含自动生成的 `XRobotMain()` 函数代码。  
  Generates `User/xrobot_main.hpp` with the auto-generated `XRobotMain()` function code.

输出示例 / Output Example：

```bash
Starting XRobot auto-configuration

[INFO] Default config created: ./Modules/modules.yaml
Please edit the file and rerun.

[EXEC] xrobot_init_mod --config ./Modules/modules.yaml --dir ./Modules
[INFO] Generated default Modules/CMakeLists.txt at: Modules/CMakeLists.txt

[EXEC] xrobot_gen_main --output ./User/xrobot_main.hpp --config ./User/xrobot.yaml
[INFO] Constructor config generated: ./User/xrobot.yaml
Modify the configuration and rerun to apply changes

[EXEC] xrobot_gen_main --output ./User/xrobot_main.hpp --config ./User/xrobot.yaml
All done! Main function generated at: ./User/xrobot_main.hpp
```

## 🧪 快速上手 / Quickstart

```bash
# 1. 初始化模块仓库模板
# 1. Initialize the module repository template
$ xrobot_init_mod --config Modules/modules.yaml
[WARN] Configuration file not found, creating template: Modules\modules.yaml
[INFO] Please edit the configuration file and rerun this script.

# 2. 拉取模块仓库
# 2. Pull module repositories
$ xrobot_init_mod --config Modules/modules.yaml
[INFO] Cloning new module: BlinkLED
Cloning into 'Modules\BlinkLED'...
remote: Enumerating objects: 19, done.
remote: Counting objects: 100% (19/19), done.
remote: Compressing objects: 100% (13/13), done.
remote: Total 19 (delta 6), reused 19 (delta 6), pack-reused 0 (from 0)
Receiving objects: 100% (19/19), done.
Resolving deltas: 100% (6/6), done.
[SUCCESS] All modules processed

$ mkdir User

# 3. 生成主函数
# 3. Generate main function
$ xrobot_gen_main --output User/xrobot_main.hpp
Discovered modules: BlinkLED
[SUCCESS] Generated entry file: User/xrobot_main.hpp

# 4. 创建模块
# 4. Create a module
$ xrobot_create_mod MySensor --desc "IMU interface module" --hw imu scl sda
[OK] Module MySensor generated at Modules\MySensor

# 5. 查看模块信息
# 5. View module information
$ xrobot_mod_parser --path .\Modules\MySensor\

=== Module: MySensor ===
Description       : IMU interface module

Constructor Args  :
  - name               = your_arg_name_here

Required Hardware : imu scl sda

# 6. 添加模块实例
# 6. Add a module instance
$ xrobot_add_mod MySensor
[SUCCESS] Appended module instance 'MySensor' to User\xrobot.yaml

# 7. 查看模块实例
# 7. View module instances
$ cat .\User\xrobot.yaml
global_settings:
  monitor_sleep_ms: 1000
modules:
- name: BlinkLED
  constructor_args:
    blink_cycle: 250
- name: MySensor
  constructor_args:
    name: your_arg_name_here

# 8. 重新生成主函数
# 8. Regenerate main function
$ xrobot_gen_main --output User/xrobot_main.hpp
Discovered modules: BlinkLED, MySensor
[SUCCESS] Generated entry file: User/xrobot_main.hpp

# 9. 查看主函数
# 9. View main function
$ cat .\User\xrobot_main.hpp
#include "app_framework.hpp"
#include "libxr.hpp"

// Module headers
#include "BlinkLED.hpp"
#include "MySensor.hpp"

template <typename HardwareContainer>
static void XRobotMain(HardwareContainer &hw) {
  using namespace LibXR;
  ApplicationManager appmgr;

  // Auto-generated module instantiations
  static BlinkLED<HardwareContainer> blinkled(hw, appmgr, 250);
  static MySensor<HardwareContainer> mysensor(hw, appmgr, "your_arg_name_here");

  while (true) {
    appmgr.MonitorAll();
    Thread::Sleep(1000);
  }
}
```

---

## 📂 项目结构 / Project Structure

```text
C:\Users\xiao\test
├── Modules/                # 上层功能模块 / High-level functional modules
│   ├── BlinkLED/           # 示例模块：LED 闪烁 / Example module: LED blinking
│   │   ├── BlinkLED.hpp    # 模块定义及 manifest / Module header with manifest
│   │   ├── CMakeLists.txt  # 构建脚本 / Build configuration
│   │   └── README.md       # 模块说明文档 / Module documentation
│   └── modules.yaml        # 模块注册列表 / Module registration list
│
├── User/                   # 用户生成文件 / User-generated files
│   ├── xrobot.yaml         # XRobot 配置文件 / XRobot configuration
│   └── xrobot_main.hpp     # 自动生成主函数 / Auto-generated main entry
```

---

## LibXR / LibXR_CppCodeGenerator / XRobot Relationship

LibXR、LibXR_CppCodeGenerator 与 XRobot 三者形成了一套完整的嵌入式与机器人软件开发体系，分工明确，协同紧密。  
LibXR, LibXR_CppCodeGenerator and XRobot together form a complete software ecosystem for embedded and robotics development, with clear separation of concerns and tight integration.

---

### 🧠 LibXR

**LibXR 是跨平台的驱动抽象与工具库**，支持 STM32、Linux 等平台，包含：  
LibXR is a cross-platform driver abstraction and utility library supporting STM32, Linux, and more. It provides:

- 通用外设接口封装  
  Unified peripheral interface abstraction  
- 嵌入式组件（如 Terminal、PowerManager、Database 等）  
  Embedded modules like Terminal, PowerManager, Database, etc.  
- FreeRTOS / bare-metal 支持  
  FreeRTOS and bare-metal support  
- 机器人运动学与导航  
  Kinematics and navigation libraries for robotics  
- 自动代码生成支持  
  Code generation support

#### 🔗 Links

- **Repository**: [libxr](https://github.com/Jiu-xiao/libxr)  
- **API Documentation**: [API](https://jiu-xiao.github.io/libxr/)  
- **Issues**: [Issue Tracker](https://github.com/Jiu-xiao/libxr/issues)

---

### 🔧 LibXR_CppCodeGenerator

**LibXR_CppCodeGenerator 是用于 LibXR 的代码生成工具链**，当前支持 STM32 + CubeMX，未来将扩展至 Zephyr、ESP-IDF 等平台。  
LibXR_CppCodeGenerator is a code generation toolchain for LibXR. It currently supports STM32 with CubeMX, and is planned to support Zephyr, ESP-IDF, and more.

- 从不同平台的工程文件生成 `.yaml` 配置  
  Parse project files from different platforms to generate `.yaml` configurations
- 基于 `.yaml` 自动生成 `app_main.cpp`、中断、CMake 等  
  Generate `app_main.cpp`, interrupt handlers, and CMake integration  
- 支持 `XRobot` glue 层集成  
  Supports optional integration with XRobot framework  
- 支持用户代码保留与多文件结构  
  Preserves user code blocks and supports modular output

#### 🔗 Links

- **Repository**: [LibXR_CppCodeGenerator](https://github.com/Jiu-xiao/LibXR_CppCodeGenerator)  
- **Documentation and Releases**: [PyPI](https://pypi.org/project/libxr/)  
- **Issues**: [Issue Tracker](https://github.com/Jiu-xiao/LibXR_CppCodeGenerator/issues)

---

### 🤖 XRobot

XRobot 是一个轻量级的模块化应用管理框架，专为嵌入式设备而设计。它本身不包含任何驱动或业务代码，专注于模块的注册、调度、生命周期管理、事件处理与参数配置。  
**XRobot is a lightweight modular application management framework designed for embedded systems.**  
It does not include any drivers or business logic by itself. Instead, it focuses on module registration, scheduling, lifecycle management, event handling, and parameter configuration.

- 模块注册与生命周期管理  
  Module registration and lifecycle management  
- 参数管理 / 配置系统 / 事件系统  
  Parameter management, configuration system, and event system  
- ApplicationRunner / ThreadManager 等应用调度器  
  ApplicationRunner and ThreadManager for runtime coordination  
- 不直接访问硬件，依赖 LibXR 的 PeripheralManager  
  Does not access hardware directly, relies on LibXR's PeripheralManager

---

#### ✅ Recommended For 推荐使用场景

- 拥有多个子模块（如传感器、通信、控制器）且希望统一管理初始化、调度与资源依赖  
  For projects with multiple submodules (e.g., sensors, communication, controllers) needing unified lifecycle and dependency management.

- 希望构建平台无关的应用层逻辑，与底层驱动解耦  
  For building platform-independent application logic decoupled from hardware drivers.

- 与 **LibXR** 结合使用，实现自动注册硬件对象（通过 `HardwareContainer`）  
  When used with **LibXR**, supports automatic hardware registration via `HardwareContainer`.

- 支持生成模块入口代码、配置逻辑名与硬件名的映射，便于快速适配不同硬件配置  
  Supports generating module entry code and logical-to-physical hardware name mapping for quick adaptation to different platforms.

#### 🔗 Links

- **Repository**: [XRobot](https://github.com/xrobot-org/XRobot)  
- **Documentation**: [GitHub Pages](https://xrobot-org.github.io)  
- **Releases**: [PyPI](https://pypi.org/project/xrobot)  
- **Issues**: [Issue Tracker](https://github.com/xrobot-org/XRobot/issues)

---

## 📄 License

Apache 2.0 License. © xrobot-org authors.
