# 雪茄房 POS 系统 · 项目宪法

> 最后更新：2026-05-13

---

## 一、项目定位

**产品名称：** 醇境雪茄 POS
**形态：** Android 平板 APK（离线优先）+ 手机浏览器后台管理
**核心功能：** 点餐 / 收款 / 库存 / 报表 / 退单 / 数据备份

---

## 二、技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────┐
│           Android 平板（离线可用）             │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐  │
│  │  前台 POS   │    │   SQLite 数据库  │  │
│  │  (APK/Web)  │◄──►│   本地持久化    │  │
│  └─────────────┘    └──────────────────┘  │
│         │                                     │
│    [摄像头扫码]  [蓝牙打印机]  [语音提示]       │
│                                             │
│  可选：结算后 push 到 GitHub                 │
└─────────────────────────────────────────────┘
              │ WiFi 同一局域网
              ▼
┌─────────────────────────────────────────────┐
│         手机浏览器（后台管理）                  │
│         访问平板 IP:5000 或 本机 Flask        │
└─────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| 前台 UI | HTML5 + CSS3 + Vanilla JS | 现有 front/ 目录，保持不变 |
| APK 打包 | Capacitor + Vite | Web 项目打包成 Android APK |
| 本地数据库 | SQLite | 平板本地存储，通过 `cordova-plugin-sqlite-2` 或 Capacitor SQL plugin |
| 语音提示 | Web Speech API (TTS) | 扫码成功/失败自动语音播报 |
| 摄像头扫码 | `@zxing/library` | Browser 版扫码，支持微信/支付宝 |
| 蓝牙打印机 | `cordova-plugin-bluetooth-serial` | ESC/POS 协议，蓝牙 SPP |
| 后台管理 | 平板上运行 Flask（局域网访问）| 手机浏览器打开平板 IP |
| Git 同步 | simple-git / GitHub API | 结算数据 JSON push 到私有仓库 |
| 备份恢复 | JSON 文件（SD 卡）| 导出/导入，无需网络 |

### 2.3 数据模型（SQLite Schema）

```sql
-- 产品分类
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_zh TEXT NOT NULL,
    name_en TEXT,
    name_ru TEXT,
    sort_order INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at DATETIME,
    updated_at DATETIME
);

-- 产品
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    name_zh TEXT NOT NULL,
    name_en TEXT,
    name_ru TEXT,
    spec TEXT,
    price REAL NOT NULL,
    cost_price REAL DEFAULT 0,
    stock INTEGER DEFAULT 0,
    stock_alert INTEGER DEFAULT 3,
    status TEXT DEFAULT 'active',
    image_url TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- 订单
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no TEXT UNIQUE NOT NULL,
    subtotal REAL NOT NULL,
    discount_amount REAL DEFAULT 0,
    discount_rate REAL DEFAULT 0,
    total REAL NOT NULL,
    cost_total REAL DEFAULT 0,
    profit REAL DEFAULT 0,
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    paid_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);

-- 订单明细
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    product_name TEXT,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    cost_price REAL DEFAULT 0,
    created_at DATETIME
);

-- 折扣码
CREATE TABLE discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    type TEXT DEFAULT 'percent',
    value REAL NOT NULL,
    min_amount REAL DEFAULT 0,
    max_uses INTEGER,
    used_count INTEGER DEFAULT 0,
    valid_from DATETIME,
    valid_until DATETIME,
    status TEXT DEFAULT 'active',
    created_at DATETIME
);

-- 系统设置（KEY-VALUE）
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- 数据变更日志（用于结算同步）
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    data_type TEXT,
    data_id INTEGER,
    payload TEXT,
    synced INTEGER DEFAULT 0,
    created_at DATETIME
);
```

### 2.4 API 设计（Flask → 未来平板本地服务）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 分类列表 |
| GET | `/api/products` | 产品列表 |
| GET | `/api/products/<id>` | 产品详情 |
| POST | `/api/orders` | 创建订单 |
| PUT | `/api/orders/<id>` | 更新订单状态（支付/退款）|
| GET | `/api/orders` | 订单列表（支持日期筛选）|
| GET | `/api/stats/daily?date=` | 日报表 |
| GET | `/api/stats/monthly?year=&month=` | 月报表 |
| POST | `/api/sync/push` | Git 同步 push |
| GET | `/api/backup/export` | 导出全量数据 JSON |
| POST | `/api/backup/import` | 导入数据 JSON |

---

## 三、功能规格

### 3.1 前台 POS（平板 APK）

**页面布局：**
- 左侧边栏：分类按钮列表（支持滚动，点击筛选）
- 右侧主区：产品卡片网格（3列，触屏优化）
- 底部固定购物车栏：品项数量 + 总价 + 结算按钮

**购物流程：**
1. 点击分类 → 显示该分类产品
2. 点击产品卡片 → 加入购物车（弹出数量选择，最小1）
3. 底部购物车实时更新
4. 点击结算 → 进入结算页

**结算页：**
- 显示订单明细、折扣码输入、总价
- 扫码区域（摄像头打开微信/支付宝收款码）
- 扫码成功后：
  - 语音提示："收款到账，XX元"
  - 自动打印小票（蓝牙打印机）
  - 订单写入本地 SQLite，status='paid'
  - 库存扣减

**扫码收款细节：**
- 使用 `@zxing/library` Browser Edition
- 支持相机实时预览扫描 QR Code
- 扫码结果由人工确认金额后点击"确认收款"
- 收款方式：微信/支付宝/现金（扫码失败可选手动现金）

**语音提示（Web Speech API）：**
- 收款成功："收款到账，128元"
- 扫码失败："请重新扫码"
- 库存不足："库存不足"
- 退单成功："退单已完成"

**蓝牙打印（ESC/POS）：**
- 小票格式：
  ```
  ==============================
        醇境雪茄
  ==============================
  订单号：CL-20260513-001
  时间：2026-05-13 14:30
  --------------------------------
  蒙特克里斯托二号  x1  ¥580
  威士忌古典        x2  ¥320
  --------------------------------
  小计：¥900
  折扣：¥0
  合计：¥900
  支付方式：微信
  ==============================
         感谢惠顾
  ==============================
  ```

### 3.2 后台管理（手机浏览器）

**访问方式：** 手机浏览器打开 `http://<平板IP>:5000/admin/`

**功能模块：**

| 模块 | 功能 |
|------|------|
| 仪表盘 | 今日营收、本日订单数、低库存告警、本月利润 |
| 产品管理 | CRUD 产品（含图片上传）、库存修改 |
| 分类管理 | CRUD 分类 |
| 库存管理 | 库存出入库记录、手动调整库存 |
| 销售统计 | 日报表/月报表，含毛利润/净利润 |
| 折扣码 | 创建折扣码（百分比/固定金额） |
| 系统设置 | 店铺名、货币符号、订单前缀、默认语言 |

**报表字段：**
- 销售总额 = SUM(orders.total WHERE status='paid')
- 成本总额 = SUM(orders.cost_total WHERE status='paid')
- **毛利润** = 销售总额 - 成本总额
- **净利润** = 毛利润（运营成本已简化为产品成本，不另计）
- 客单价 = 销售总额 / 订单数

### 3.3 退单流程

**入口：** 前台结算页 → "退单" 按钮

**方式 A：扫码退单**
1. 点击"退单" → 打开摄像头
2. 扫描原始小票上的订单二维码（包含 order_no）
3. 系统查询该订单，确认状态为 paid
4. 显示退款明细，人工确认
5. 点击"确认退单"：
   - 语音提示："退单已完成"
   - 自动打印退单小票
   - 库存恢复（+）
   - 订单 status → 'refunded'
   - 利润数据相应调整（负数）

**方式 B：线下退钱**
- 扫描失败时，手动输入订单号查询
- 选择"线下退钱"（现金退款，无需扫码）
- 同上流程，备注"线下退钱"

**权限：** 退单需要 admin 账号确认（防止店员随意退单）

### 3.4 数据备份与同步

**本地备份（每次结算后自动）：**
- 结算完成 → 生成 `/sdcard/CigarPOS/backups/YYYY-MM-DD.json`
- 包含：categories, products, orders, order_items, settings
- 覆盖写入当天文件（同名不累加）

**手动导出：**
- 后台 → 系统设置 → "导出数据" 按钮
- 生成全量 JSON，保存到 SD 卡

**Git 同步（可选）：**
- 后台 → 系统设置 → "同步到 Git" 按钮
- 使用 simple-git 或 GitHub API
- 将当月备份 JSON push 到私有 GitHub 仓库
- 需要配置：GitHub Token + 仓库地址（存入 settings）

**数据导入（新安装）：**
- 首次启动检测 SD 卡 `/CigarPOS/backups/` 目录
- 如有备份文件 → 引导用户选择导入
- 或后台手动上传 JSON 文件导入
- 导入前清空本地数据（警告提示）

---

## 四、UI 设计规范

### 4.1 视觉风格

- **主题：** 深色奢华（Dark Luxury）
- **背景色：** #0F0D0B（深棕黑）
- **侧边栏：** #1A1612（略浅）
- **卡片背景：** #1E1A16
- **主色调：** #C9A84C（古铜金）
- **文字主色：** #E8DCC8（米白）
- **文字次色：** #8B7355（暗金）
- **危险色：** #C94A4A（暗红）
- **成功色：** #4A9C6D（暗绿）

### 4.2 图标

- **仅使用 Lucide SVG 图标**（禁止 Emoji）
- 大小：24px（标准）、32px（大卡片）、16px（紧凑）

### 4.3 字体

- 主字体：系统默认无衬线（iOS: SF Pro, Android: Roboto）
- 数字/金额：等宽字体

### 4.4 动效

- 页面切换：淡入淡出 200ms ease
- 卡片点击：scale(0.98) → scale(1) 100ms
- 购物车添加：产品图片飞入动画
- 结算成功：金色光晕扩散动画
- 触屏反馈：涟漪效果（Ripple）

### 4.5 布局

**平板竖屏（主）：**
```
┌──────────────────────────┐
│  顶部栏（店铺名+语言）      │
├────────┬─────────────────┤
│        │                 │
│  分类  │    产品网格      │
│  侧栏  │   (3列滚动)     │
│        │                 │
│        │                 │
├────────┴─────────────────┤
│  购物车栏（固定底部）        │
└──────────────────────────┘
```

**平板横屏：**
- 左侧分类栏收窄，右侧产品网格 4-5 列

---

## 五、非功能需求

### 5.1 性能

- 页面首次加载 < 1.5s（平板本地）
- 扫码响应 < 500ms
- 订单创建 < 200ms

### 5.2 离线能力

- 核心功能（点餐、收款、退单）完全离线可用
- Git 同步需要网络（可选）
- 后台管理需要平板在线（同一局域网）

### 5.3 安全

- admin 密码：首次强制修改默认密码
- 退单需要二次确认
- SQLite 数据库不加密（平板丢失风险由用户自负）

### 5.4 兼容性

- Android 8.0+（API 26+）
- 平板横竖屏自适应
- 主流平板分辨率：1920x1200, 2048x1536, 2560x1600

---

## 六、交付物

1. `cigar-pos.apk` — Android 安装包
2. `cigar-lounge-web/` — Web 前台源码（Vite 项目）
3. `cigar-lounge-api/` — Flask 后端 API 源码
4. `SPEC.md` — 本宪法文档
5. `capacitor.config.ts` — Capacitor 配置
6. 数据库 schema 变更记录

---

## 七、Capacitor 项目结构

```
cigar-lounge/
├── src/                      # Vite 前端源码
│   ├── pages/
│   │   ├── pos/              # 前台 POS 页面
│   │   ├── checkout/         # 结算页
│   │   ├── refund/           # 退单页
│   │   └── settings/         # 设置页
│   ├── components/
│   │   ├── ProductCard.vue
│   │   ├── CartBar.vue
│   │   ├── CategorySidebar.vue
│   │   └── ReceiptPrinter.vue
│   ├── services/
│   │   ├── db.ts             # SQLite 操作
│   │   ├── scanner.ts        # 扫码服务
│   │   ├── bluetooth.ts      # 蓝牙打印
│   │   ├── tts.ts            # 语音服务
│   │   └── sync.ts           # Git 同步
│   └── App.vue
├── api/                      # Flask 后端（平板上运行）
│   ├── app.py
│   ├── models/
│   └── routes/
├── android/                  # Capacitor Android 项目
├── capacitor.config.ts
└── vite.config.ts
```

---

## 八、开发阶段

| 阶段 | 内容 | 交付 |
|------|------|------|
| Phase 0 | 调研、宪法、项目结构 | 本文档 |
| Phase 1 | Vite 项目初始化，POS 页面移植 | 可运行的平板 UI |
| Phase 2 | SQLite 数据库集成，数据读写 | 离线订单流程 |
| Phase 3 | 扫码收款 + 语音提示 | 扫码到账 |
| Phase 4 | 蓝牙打印小票 | 自动打印 |
| Phase 5 | 退单流程 | 扫码/手动退单 |
| Phase 6 | 后台管理（Flask API） | 手机浏览器管理 |
| Phase 7 | Git 同步 + 数据备份/恢复 | 数据安全 |
| Phase 8 | APK 打包、签名、发布 | cigar-pos.apk |
