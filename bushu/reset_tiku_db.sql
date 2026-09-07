-- =========================================================================
-- 智题库 (TiKu) 云端数据库一键自愈与重置脚本 (reset_tiku_db.sql)
-- 使用场景: 当本地表结构大幅变更，导致线上数据库报 500 列缺失错误时使用。
-- 操作方式: 登录 TiDB Cloud 网页控制台 -> 点击左侧 SQL Editor -> 粘贴下方代码全选执行
-- =========================================================================

-- 1. 删除旧库 (清除所有旧表和历史脏数据)
DROP DATABASE IF EXISTS tiku;

-- 2. 重新创建全新 UTF8MB4 数据库
CREATE DATABASE tiku CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. 切换到当前库
USE tiku;

-- 提示:
-- 执行完毕后，在 Render 控制台点击 [Manual Deploy] -> [Clear build cache & deploy]
-- 后端启动时会自动在空库中根据最新的 Python 代码把所有表全部新建好！
-- 然后在本地终端运行 python seed_rbac_users.py 即可秒级注入超级管理员账号。
