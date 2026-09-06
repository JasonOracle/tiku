# C端注册资料完善 + 全套自测方案

## 一、数据模型（backend/app/models/user.py + main.py auto_patch + tiku_init.sql）

User 表新增 5 列（全部幂等补列，老数据无损）：

| 字段 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| nickname | VARCHAR(50) | 可空（老用户展示回退 username） | 昵称，**注册必填** |
| gender | VARCHAR(10) | 可空，值 `male`/`female` | 性别，**注册必选** |
| position | VARCHAR(50) | 可空 | 职务，选填 |
| phone | VARCHAR(20) | 可空 + **唯一索引**（老数据全 NULL 不冲突） | 手机号，**必填**，正则 `^1[3-9]\d{9}$` |
| email | VARCHAR(100) | 可空 | 邮箱，选填 |

登录方式不变（用户名+密码），手机号仅作资料与唯一性约束（同号注册返回 400「该手机号已被注册」）。

## 二、后端 API

1. **`POST /api/v1/auth/register`**（api/v1/auth.py + schemas/auth.py）：
   - RegisterRequest 扩展；**必填/格式校验全部走手动业务校验返回 400 中文 detail**（"请填写昵称"/"请选择性别"/"手机号格式不正确"/"该手机号已被注册"/"该用户名已被占用"），不依赖 Pydantic 422 —— 因为 C 端拦截器目前不解析 422，英文报错体验差。
   - login 返回的 `UserResponse` 增加 nickname/gender/position/email 字段。
2. **新增 `GET /api/v1/users/me`**：返回完整个人资料（个人中心展示与昵称刷新用）。
3. **B 端昵称数据**：答题明细（admin/users/records）、阅卷大厅列表与详情、考情看板 user_records 三处响应统一增加 `nickname` 字段，展示口径"昵称优先、无则用户名"由前端处理。
4. **pytest**（新增 tests/test_registration_profile.py）：全字段注册 201、缺昵称/缺性别/手机号格式错/手机号重复/用户名重复 → 400 中文、登录返回资料、GET /users/me。

## 三、C 端前端（toc）

1. **LoginView**：注册模式扩展为完整表单（毛玻璃风格一致）：昵称(必填)、性别(男/女单选必选)、手机号(必填)、职务(选填)、邮箱(选填) + 用户名/密码；注册成功弹提示并切回登录、自动预填用户名。
2. **store/user.ts**：增加 nickname 持久化；登录时写入。
3. **ProfileView**：欢迎区改为 昵称大字 + @用户名 小字 + 性别/职务标签；数据源接 `GET /users/me`（失败回退 store）；资料缺失字段显示"—"。

## 四、B 端前端（tob）

1. **UsersView**：「注册C端用户」tab 增加 昵称/性别/手机号 列；顺手补上缺失的分页控件（当前只显示前 10 条）；「答题明细」tab 答题用户列显示 `nickname(username)`。
2. **GradingView**：考生列、批阅弹窗标题改显示昵称。
3. **ExamsView 考情看板弹窗**：作答用户列改显示昵称。

## 五、批量账号 + 全套自测（脚本 `scripts/e2e_selftest.py` 存入仓库，可复跑）

对着**线上服务 + 真实 SenseNova** 全链路自测：

1. **B 端造数**：admin 登录 → 新建题目分类 + 试卷分类 → 手工新建 5 种题型题目各 1（单选/多选/判断/填空/简答）→ ✨AI 出题（真调大模型）→ ✨AI 组卷（真调，含简答题）→ 两份卷均上架
2. **批量注册 6 个 C 端账号**：全字段填写（男女各半、职务有/无、唯一手机号 139000000xx）；同时验证负路径：重复手机号 400、缺昵称 400
3. **模拟考试**：
   - 手工卷：3 个账号分别以"客观全对""多选漏选（半对）""含简答"策略作答 → 验证即时出分/半对得分/简答转 pending_grading → 阅卷大厅定分发布
   - AI 卷：2 个账号作答 → 真实 AI 全托管阅卷 → 验证得分、评语落库、消息通知
4. **展示与聚合校验**：B 端用户列表/阅卷大厅/考情看板昵称字段；C 端 /users/me 资料；我的测试三桶聚合与"再考一次"
5. 输出**自测报告**（每项通过/失败 + 账号清单），同步记录到 progress.md

## 六、收尾

pytest 全绿 + tob/toc build → 实库 auto_patch 迁移 + 容器重建 + nginx reload → 文档同步（progress/api-contract/README）→ git commit。

批量账号将保留作为演示数据（如需清理可随时删除）。