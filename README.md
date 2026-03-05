# 图书馆借书查询系统

自动查询图书馆书籍可借状态，定时监控不可借书籍，可借时提醒用户。

## 功能特性

- 📚 **书籍管理** - 添加、删除、查看待查询书籍
- 🔍 **状态查询** - 查询书籍是否可借及馆藏位置
- ⏰ **定时监控** - 定时检查不可借书籍状态
- 🔔 **智能提醒** - 书籍可借时自动通知（控制台/邮件）
- ⚙️ **可配置** - 支持配置不同图书馆网站
- 🧪 **单元测试** - 完善的单元测试覆盖

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

复制配置文件示例并修改：

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml` 文件，配置图书馆信息和提醒方式。

### 3. 使用

#### 添加书籍
```bash
python main.py add --title "Python编程" --author "Guido" --monitor
```

#### 查看书单
```bash
python main.py list
```

#### 立即检查
```bash
python main.py check
```

#### 启动监控
```bash
python main.py monitor
```

## 命令说明

| 命令 | 说明 | 示例 |
|------|------|------|
| `add` | 添加书籍到书单 | `python main.py add --title "书名" --monitor` |
| `list` | 列出所有书籍 | `python main.py list` |
| `remove <book_id>` | 移除指定书籍 | `python main.py remove abc123` |
| `toggle <book_id>` | 切换书籍监控状态 | `python main.py toggle abc123` |
| `check` | 立即检查所有书籍 | `python main.py check` |
| `monitor` | 启动定时监控 | `python main.py monitor` |

### add 命令参数

| 参数 | 简写 | 说明 | 必需 |
|------|------|------|------|
| `--title` | `-t` | 书名 | 否（至少提供一个） |
| `--isbn` | `-i` | ISBN | 否（至少提供一个） |
| `--author` | `-a` | 作者 | 否（至少提供一个） |
| `--monitor` | `-m` | 开启监控 | 否（默认关闭） |

## 配置说明

### 图书馆配置

```yaml
library:
  name: "深圳图书馆"
  base_url: "https://www.szlib.org.cn/"
  search_url: "https://www.szlib.org.cn/opac/"
  timeout: 30
```

### 定时任务配置

```yaml
scheduler:
  enabled: true
  interval_minutes: 30  # 每30分钟检查一次
  retry_on_failure: true
  max_retries: 3
```

### 提醒配置

```yaml
notification:
  enabled: true
  methods:
    - console
    - email
  email:
    smtp_server: smtp.qq.com
    smtp_port: 587
    sender: your_email@qq.com
    password: your_smtp_password
    recipients:
      - recipient1@example.com
```

## 技术设计

### 系统架构

```
lib-borrow-notify/
├── main.py              # 主程序入口，命令行接口
├── config.py            # 配置管理模块
├── book_manager.py      # 书籍数据管理模块
├── library_scraper.py   # 图书馆爬虫模块
├── notifier.py          # 消息通知模块
├── scheduler.py         # 定时任务调度模块
├── config.yaml          # 配置文件
├── requirements.txt     # Python依赖
└── tests/              # 单元测试
    └── test_book_manager.py
```

### 核心模块设计

#### 1. Config（配置管理）

- **职责**：加载和管理应用配置
- **核心类**：`Config`
- **功能**：
  - 从 YAML 文件加载配置
  - 提供配置项访问接口
  - 支持嵌套配置访问（如 `config.library.name`）

#### 2. BookManager（书籍管理）

- **职责**：管理书单数据的持久化和操作
- **核心类**：`Book`, `BookManager`
- **功能**：
  - 书籍 CRUD 操作
  - JSON 文件持久化
  - 监控状态管理

#### 3. LibraryScraper（图书馆爬虫）

- **职责**：与图书馆网站交互，查询书籍信息
- **核心类**：`LibraryScraper`（基类）, `ShenzhenLibraryScraper`（实现）
- **功能**：
  - 搜索书籍
  - 获取馆藏信息
  - 解析可借状态
- **扩展方式**：继承基类实现 `search_book` 方法

#### 4. Notifier（消息通知）

- **职责**：发送书籍可借提醒
- **核心类**：`Notifier`（基类）, `ConsoleNotifier`, `EmailNotifier`, `NotificationManager`
- **功能**：
  - 多渠道通知（控制台、邮件）
  - 可扩展的通知接口
  - 消息格式化

#### 5. Scheduler（定时调度）

- **职责**：定时检查书籍状态并触发通知
- **核心类**：`BookMonitor`
- **功能**：
  - 定时任务调度
  - 状态变化检测
  - 集成通知模块

### 数据流程

```
用户命令
    ↓
Main.py (命令解析)
    ↓
BookManager (数据操作)
    ↓
LibraryScraper (查询图书馆)
    ↓
状态更新
    ↓
状态变化? → 是 → Notifier (发送提醒)
    ↓
BookManager (保存数据)
```

### 深圳图书馆爬虫实现

#### API 接口

深圳图书馆使用以下 API：

1. **搜索 API**：`/api/opacservice/getQueryResult`
   - 参数：`v_index`（搜索类型）, `v_value`（关键词）
   - 返回：书籍列表，包含 `recordid` 和 `tablename`

2. **馆藏 API**：`/api/opacservice/getpreholding`
   - 参数：`metaTable`, `metaId`
   - 返回：馆藏信息，包含 `CanLoanBook` 数组

#### 请求流程

```
1. 访问 /opac/ 建立 session
2. 调用 getQueryResult 搜索书籍
3. 从结果中提取 recordid 和 tablename
4. 调用 getpreholding 获取馆藏信息
5. 解析 CanLoanBook 获取可借位置
```

## 扩展开发

### 添加新的图书馆支持

继承 `LibraryScraper` 类并实现 `search_book` 方法：

```python
class MyLibraryScraper(LibraryScraper):
    def search_book(self, book: Book) -> Tuple[bool, List[str], str]:
        # 实现你的图书馆搜索逻辑
        # 返回: (是否可借, 馆藏位置列表, 检查时间)
        pass
```

### 添加新的提醒方式

继承 `Notifier` 类并实现 `send` 方法：

```python
class MyNotifier(Notifier):
    def send(self, message: str):
        # 实现你的提醒逻辑
        pass
```

然后在 `NotificationManager._init_notifiers()` 中注册。

## 运行测试

```bash
# 运行所有测试
python -m unittest discover tests

# 运行特定测试文件
python -m unittest tests.test_book_manager

# 运行特定测试类
python -m unittest tests.test_book_manager.TestBookManager

# 运行特定测试方法
python -m unittest tests.test_book_manager.TestBookManager.test_book_creation
```

## 注意事项

- 深圳图书馆爬虫已完整实现，可以真实查询书籍可借状态和馆藏位置
- 请合理设置检查间隔，避免对图书馆网站造成压力
- 使用邮件提醒需配置 SMTP 服务器信息
- 当前支持深圳图书馆，其他图书馆需自行实现爬虫
- 数据文件（book_list.json）已在 .gitignore 中，不会被提交

## 开发计划

- [ ] 支持更多图书馆（广州图书馆、上海图书馆等）
- [ ] 添加 Web 界面
- [ ] 支持更多通知方式（微信、Telegram 等）
- [ ] 添加书籍推荐功能
- [ ] 支持批量导入书单

## 许可证

MIT License
