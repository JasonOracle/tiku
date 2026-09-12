"""
自动抓取系统快照并生成 v1.4 版本介绍文档脚本
使用系统自带 Edge/Chrome 运行，无需配置环境
"""
import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "images", "v1.4")
DOC_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "v1.4_showcase.md")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_snapshots():
    with sync_playwright() as p:
        print("[1/4] 启动浏览器...")
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # ------------------- B端抓取 -------------------
        print("[2/4] 开始抓取 B 端管理后台 (PC 视口)...")
        b_context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2
        )
        b_page = b_context.new_page()
        
        # 登录 B 端
        print("  -> 正在登录 B 端后台...")
        b_page.goto("http://localhost/admin/login")
        b_page.wait_for_timeout(1000)
        
        # 截取登录页
        b_page.screenshot(path=os.path.join(OUTPUT_DIR, "00_tob_login.png"))
        
        # 查找输入框并填入账号密码
        inputs = b_page.locator("input")
        if inputs.count() >= 2:
            inputs.nth(0).fill("13800000012")
            inputs.nth(1).fill("123456")
        else:
            b_page.fill("input[type='text'], input[placeholder*='账号'], input[placeholder*='手机']", "13800000012")
            b_page.fill("input[type='password']", "123456")
        
        # 点击登录按钮
        b_page.locator("button[type='submit'], button:has-text('登录')").click()
        b_page.wait_for_timeout(2000)
        
        # 路由清单
        b_routes = [
            ("01_tob_dashboard.png", "http://localhost/admin/dashboard", "数据看板"),
            ("02_tob_resources.png", "http://localhost/admin/resources", "题目管理"),
            ("03_tob_tasks.png", "http://localhost/admin/tasks", "试卷管理"),
            ("04_tob_ai_assistant.png", "http://localhost/admin/ai-assistant", "AI 助理"),
            ("05_tob_kb.png", "http://localhost/admin/kb", "AI 知识库"),
            ("06_tob_members.png", "http://localhost/admin/members", "成员管理"),
        ]
        
        for filename, url, label in b_routes:
            print(f"  -> 正在截图 B 端: {label} ({url})...")
            try:
                b_page.goto(url)
                b_page.wait_for_timeout(1500)
                b_page.screenshot(path=os.path.join(OUTPUT_DIR, filename))
            except Exception as e:
                print(f"  [!] 截取 {label} 失败: {e}")
        
        b_context.close()

        # ------------------- C端抓取 -------------------
        print("[3/4] 开始抓取 C 端移动端 (iPhone 视口)...")
        c_context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            device_scale_factor=2
        )
        c_page = c_context.new_page()
        
        # 访问 C 端首页或登录页
        print("  -> 正在访问 C 端登录页...")
        c_page.goto("http://localhost/login")
        c_page.wait_for_timeout(1000)
        c_page.screenshot(path=os.path.join(OUTPUT_DIR, "07_toc_login.png"))
        
        # C 端登录
        inputs = c_page.locator("input")
        if inputs.count() >= 2:
            inputs.nth(0).fill("13900000006")
            inputs.nth(1).fill("123456")
            c_page.locator("button:has-text('登录')").click()
            c_page.wait_for_timeout(1500)
        
        # C 端路由清单
        c_routes = [
            ("08_toc_home.png", "http://localhost/", "C端首页/企业空间"),
            ("09_toc_my_tasks.png", "http://localhost/my-tasks", "我的测评任务"),
            ("10_toc_profile.png", "http://localhost/profile", "个人中心"),
            ("11_toc_favorite.png", "http://localhost/favorite", "我的收藏"),
        ]
        
        for filename, url, label in c_routes:
            print(f"  -> 正在截图 C 端: {label} ({url})...")
            try:
                c_page.goto(url)
                c_page.wait_for_timeout(1500)
                c_page.screenshot(path=os.path.join(OUTPUT_DIR, filename))
            except Exception as e:
                print(f"  [!] 截取 {label} 失败: {e}")
        
        c_context.close()
        browser.close()
        
        # ------------------- 生成 Markdown 文档 -------------------
        print("[4/4] 正在生成 v1.4 项目介绍图文文档...")
        generate_markdown_doc()
        print(f"[OK] 快照与文档已生成成功: {os.path.abspath(DOC_FILE)}")


def generate_markdown_doc():
    doc_content = """# 智题库 (TiKu) v1.4 系统功能快照与产品架构指南

> **版本定位**：企业级多租户智能题库与在线考核闭环系统  
> **核心特性**：多租户数据隔离、AI 智能出题与交互卡片、智能组卷、B端全功能看板、C端移动轻量答题。

---

## 🏗️ 系统全景架构

```
┌─────────────────────────────────────────────────────────────┐
│                    智题库 TiKu 平台架构                     │
├──────────────────────────────┬──────────────────────────────┤
│    B 端管理后台 (PC 端)       │      C 端答题端 (移动端)      │
│  - 机构大屏与运营看板         │  - 企业专属空间与任务大厅   │
│  - 题库资源与多题型管理       │  - 在线测评与答题卡交互     │
│  - 智能组卷与防作弊规则配置   │  - 成绩分析报告与错题集     │
│  - AI 智能助理 (批量出题/答疑)│  - 个人中心与资源收藏       │
├──────────────────────────────┴──────────────────────────────┤
│             FastAPI SaaS 核心中枢 + MySQL 8.0               │
│        (多租户权限校验 / 租户数据逻辑隔离 / 审计日志)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 一、B 端管理后台 (PC 端)

### 1. 登录与身份鉴权
支持机构管理员（Admin）、企业管理员及平台超级管理员（Super Admin）登录，具备细粒度权限控制与租户隔离机制。

![B端登录界面](./images/v1.4/00_tob_login.png)

---

### 2. 数据看板 (Dashboard)
实时统计机构资产：题库总数、试卷总数、参与人次、考生成绩分布大盘，帮助管理者全局把握教学与考核态势。

![数据看板](./images/v1.4/01_tob_dashboard.png)

---

### 3. 题目管理中心 (Questions)
支持单选题、多选题、判断题、填空题、问答题等多题型录入与维护，支持批量导入导出、解析维护与知识点标签化关联。

![题目管理](./images/v1.4/02_tob_resources.png)

---

### 4. 试卷与考核中心 (Exams)
灵活配置考试时长、及格线、限考次数、防切屏作弊监控等，一键发布考核任务并自动同步至考生端。

![试卷管理](./images/v1.4/03_tob_tasks.png)

---

### 5. AI 智能助手 (AI Assistant)
具备 LLM 深度赋能：
- **自然语言出题**：对话输入出题需求，直接输出批量题型预览卡片；
- **智能组卷调用**：自动检索题库并组装试卷草稿；
- **安全合规守卫**：防越权删除、防敏感泄题，操作卡片历史持久化。

![AI 智能助理](./images/v1.4/04_tob_ai_assistant.png)

---

### 6. AI 知识库管理 (Knowledge Base)
支持上传教学讲义、教材切片，作为 AI RAG 知识检索源，实现基于机构专属文档的精准出题与智能答疑。

![AI 知识库](./images/v1.4/05_tob_kb.png)

---

### 7. 团队与成员管理 (Members)
多层级人员管理，支持按部门/班级批量管理学员、分配角色权限，考核名单精准下发。

![成员管理](./images/v1.4/06_tob_members.png)

---

## 二、C 端考生端 (移动端)

针对移动设备（H5 / 小程序）优化，提供极致流畅的刷题与考试体验。

### 1. 登录与企业空间
考生输入账号密码一键进入所属企业/机构空间，查看个人任务待办。

| 考生登录界面 | 企业空间首页 |
| :---: | :---: |
| ![C端登录](./images/v1.4/07_toc_login.png) | ![企业空间首页](./images/v1.4/08_toc_home.png) |

---

### 2. 我的考核任务与个人中心
按时序罗列进行中、未开始与已完成的测评，个人中心支持查看错题收藏与成长轨迹。

| 我的测评列表 | 个人中心与错题收藏 |
| :---: | :---: |
| ![我的任务](./images/v1.4/09_toc_my_tasks.png) | ![个人中心](./images/v1.4/10_toc_profile.png) |

---

## 三、版本里程碑与后续演进 (v1.5)

- [x] **v1.4 现状**：B端 AI 助手交互闭环已固化，多租户架构稳定，PC 与移动端实现全链路业务流通。
- [ ] **v1.5 规划**：全面重构 C 端考生端（Uni-app + Wot Design Uni + 极客蓝极简风格），带来更强大的作答动画、本地暂存防丢失与深色模式支持。
"""
    with open(DOC_FILE, "w", encoding="utf-8") as f:
        f.write(doc_content)


if __name__ == "__main__":
    run_snapshots()
