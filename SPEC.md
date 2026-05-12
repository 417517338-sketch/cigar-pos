# Cigar Lounge — 点餐系统规格文档
**Version 1.0** | 2026-05-12

---

## 1. 概念与愿景

雪茄房高端点餐系统，为高端休闲场所提供私密、优雅的一站式消费体验。界面以深棕/金色为基调，触感流畅、视觉沉稳，让顾客在浏览产品时即感受到雪茄文化的仪式感。后台管理简洁高效，数据看板一目了然。

---

## 2. 设计语言

### 2.1 美学方向
- **主题**：Dark Luxury — 深色木质感 + 金色点缀，模拟雪茄烟气和威士忌琥珀
- **参考**：高端雪茄会所、五星级酒店Lounge Bar

### 2.2 配色
```
--color-bg:           #1a1410   /* 深棕黑背景 */
--color-surface:      #2d2318   /* 卡片表面 */
--color-surface-hover:#3d3020   /* 悬停态 */
--color-border:       #4a3a28   /* 边框 */
--color-gold:         #c9a84c   /* 金色强调 */
--color-gold-light:   #e0c87a   /* 亮金 */
--color-text:         #f5f0e8   /* 主文字 */
--color-text-muted:   #a89880   /* 次文字 */
--color-success:      #6b9b6b   /* 成功绿 */
--color-warning:      #c98a4c   /* 警告橙 */
--color-error:        #c95454   /* 错误红 */
```

### 2.3 字体
- **标题**：Noto Serif SC（中文衬线）/ Playfair Display（英文衬线）
- **正文**：Noto Sans SC / Inter
- **数字/金额**：JetBrains Mono（等宽，易读）

### 2.4 间距系统
- 基础单位：4px
- 卡片间距：16px / 24px
- 页面边距：大屏 48px / 平板 24px / 手机 16px

### 2.5 动效哲学
- **入场**：fade-in + translateY(16px) → translateY(0)，duration 400ms，ease-out
- **卡片悬停**：translateY(-4px) + box-shadow 增强，duration 200ms
- **页面切换**：opacity 淡入淡出，duration 300ms
- **支付成功**：金色光晕扩散动画，scale 1 → 1.05 → 1
- **禁止**：避免过度弹跳/闪烁，所有动效服务于优雅感

### 2.6 图标
- Lucide Icons（SVG内联，禁止Emoji）
- 尺寸：16px / 20px / 24px

---

## 3. 布局与结构

### 3.1 前台（顾客端）
- **路由**：`/` 首页（产品分类浏览）
- **分类栏**：顶部横向滚动，固定
- **产品网格**：响应式，大屏4列/平板2列/手机1列
- **购物车**：右下角悬浮按钮，显示数量角标
- **结算页**：`/checkout` 全屏结算 + 摄像头扫码支付
- **支付结果**：`/result` 成功/失败反馈

### 3.2 后台（管理端）
- **路由**：`/admin` 管理后台
- **侧边导航**：固定左侧，图标+文字
- **模块**：产品管理 / 分类管理 / 库存管理 / 销售数据 / 系统设置

### 3.3 响应式断点
```
mobile:  < 640px
tablet:  640px - 1024px
desktop: > 1024px
```

---

## 4. 功能规格

### 4.1 前台功能

#### 首页浏览
- 顶部：店铺Logo + 语言切换（下拉：中/EN/РУС）
- 分类横条：显示所有分类，点击过滤产品，支持滑动
- 产品卡片：
  - 产品图片（正方形，圆角8px）
  - 产品名称（双语）
  - 规格标签（如"12支装"）
  - 单价（金色大字）
  - 库存状态（充足/仅剩X/缺货）
  - +/- 数量按钮（缺货禁用）
- 购物车浮钮：右下角，点击展开购物车列表

#### 结算流程
- 购物车列表：可删单项，可改数量
- 折扣输入：输入折扣码或选择会员折扣
- 应付金额：原价/折扣/应付 三行显示
- 支付方式：微信 / 支付宝（图标切换）
- 摄像头扫码：点击后调用浏览器 MediaDevices API 打开摄像头
- 扫码后：显示支付二维码（模拟），倒计时
- 支付结果：成功动画 / 失败重试

#### 多语言
- 前台所有文字：中文 / English / Русский
- 产品名称/描述：双语存储，切换显示
- 语言切换：本地存储记忆

### 4.2 后台功能

#### 产品管理
- 产品列表：表格视图，支持搜索/筛选/排序
- 添加/编辑产品：
  - 名称（中/英/俄）
  - 分类（选择已有分类）
  - 规格
  - 单价
  - 成本价（隐藏，用于计算毛利）
  - 库存数量
  - 库存预警阈值（默认3）
  - 产品图片（上传至OSS）
  - 状态（上架/下架）
- 批量操作：上架/下架/删除

#### 分类管理
- 分类列表：名称（中/英/俄）/ 排序 / 状态
- 添加/编辑/删除分类
- 拖拽排序

#### 库存管理
- 库存列表：产品/当前库存/预警阈值/状态
- 入库操作：数量 + 备注
- 出库操作：数量 + 备注（订单自动出库）
- 低库存告警：仪表盘卡片，红色高亮

#### 销售数据
- **核心指标**：
  - 今日销售额 / 订单数 / 客单价
  - 本月销售额 / 订单数 / 客单价
  - **毛利润** = 销售额 - 成本 × 销量
  - **净利润** = 毛利润 - 运营成本（后台可设置分摊）
- **图表**：
  - 折线图：近7天/30天销售额趋势
  - 饼图：分类销售占比
- **订单列表**：订单号/时间/商品/金额/支付状态/操作
- **导出**：Excel / CSV 导出

#### 系统设置
- 店铺信息：名称/Logo/简介
- 折扣管理：添加折扣码（折扣码/折扣比例/有效期）
- 小票设置：蓝牙打印机配对
- 多语言管理：翻译词条编辑
- 操作日志：谁在什么时间改了什么

### 4.3 数据模型

#### Category（分类）
```
id          INT AUTO_INCREMENT PK
name_zh     VARCHAR(64)      -- 中文名
name_en     VARCHAR(64)      -- 英文名
name_ru     VARCHAR(64)      -- 俄文名
sort_order  INT DEFAULT 0
status      ENUM('active','inactive')
created_at  DATETIME
updated_at  DATETIME
```

#### Product（产品）
```
id              INT AUTO_INCREMENT PK
category_id     INT FK
name_zh         VARCHAR(128)
name_en         VARCHAR(128)
name_ru         VARCHAR(128)
spec            VARCHAR(64)      -- 规格
price           DECIMAL(10,2)
cost_price      DECIMAL(10,2)   -- 成本价（隐藏）
stock           INT DEFAULT 0
stock_alert     INT DEFAULT 3   -- 预警阈值
image_url       VARCHAR(512)
status          ENUM('active','inactive')
created_at      DATETIME
updated_at      DATETIME
```

#### Order（订单）
```
id              INT AUTO_INCREMENT PK
order_no        VARCHAR(32) UNIQUE
items           JSON             -- [{product_id, name, price, qty, subtotal}]
subtotal        DECIMAL(10,2)   -- 商品小计
discount_code   VARCHAR(32)
discount_amount DECIMAL(10,2)
total           DECIMAL(10,2)   -- 实付金额
cost_total      DECIMAL(10,2)   -- 成本合计（用于计算毛利）
profit          DECIMAL(10,2)   -- 毛利润
payment_method  ENUM('wechat','alipay','cash')
payment_status  ENUM('pending','paid','refunded')
ordered_at      DATETIME
paid_at         DATETIME
created_at      DATETIME
```

#### Discount（折扣）
```
id          INT AUTO_INCREMENT PK
code        VARCHAR(32) UNIQUE
type        ENUM('percentage','fixed')  -- 百分比/固定金额
value       DECIMAL(10,2)   -- 折扣值
min_amount  DECIMAL(10,2)  -- 最低消费
valid_from  DATETIME
valid_until DATETIME
status      ENUM('active','inactive')
```

#### StockLog（库存日志）
```
id          INT AUTO_INCREMENT PK
product_id  INT FK
type        ENUM('in','out','adjust')
qty         INT
balance     INT              -- 变动后余额
note        VARCHAR(256)
operator    VARCHAR(64)
created_at  DATETIME
```

#### Setting（系统设置）
```
key         VARCHAR(64) PK
value       TEXT
```

---

## 5. 技术架构

### 5.1 后端
- **框架**：Flask 3.x + SQLAlchemy
- **数据库**：MySQL 8.0（阿里云RDS）
- **ORM**：SQLAlchemy 2.0
- **迁移**：Flask-Migrate（Alembic）
- **认证**：Flask-Login（后台管理登录）
- **图片**：阿里云OSS（上传/CDN）

### 5.2 前端
- **模板**：Jinja3（服务器渲染）
- **样式**：原生 CSS（CSS变量系统）
- **交互**：原生 JavaScript（ES6+）
- **图表**：Chart.js（销售数据可视化）
- **无框架依赖**：保持轻量

### 5.3 部署
- **环境**：Ubuntu 22.04 / Python 3.11
- **WSGI**：Gunicorn
- **Web服务器**：Nginx（反向代理 + 静态文件）
- **HTTPS**：Let's Encrypt
- **域名**：用户已有域名

### 5.4 摄像头扫码
- 前端：浏览器 MediaDevices API 获取视频流
- 解析：前端扫到二维码后调用后端验证支付状态（轮询）
- 模拟模式：开发阶段使用模拟支付流程

---

## 6. 优先级与里程碑

| Phase | 内容 | 优先级 |
|-------|------|--------|
| P0 | 数据库模型 + 管理后台框架 | 开发第1天 |
| P0 | 产品管理 + 分类管理（CRUD） | 开发第1天 |
| P0 | 前台产品浏览 + 购物车 | 开发第2天 |
| P0 | 结算 + 摄像头扫码支付 | 开发第2天 |
| P1 | 销售数据看板（毛利/净利） | 开发第3天 |
| P1 | 库存管理 + 预警 | 开发第3天 |
| P1 | 折扣系统 | 开发第3天 |
| P2 | 多语言（中/英/俄） | 开发第4天 |
| P2 | 小票蓝牙打印 | 开发第4天 |
| P3 | 操作日志 | 后置 |

---

## 7. 质量标准

- 所有表单：服务端校验 + 前端校验
- 所有金额：DECIMAL(10,2)，禁止浮点运算
- 所有时间：UTC存储，本地显示
- 图片：WebP优先，最大500KB
- 响应时间：页面加载 < 2s
- 移动端：iPad/手机触控优化
