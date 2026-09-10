-- ============================================================
-- [变更日志]
-- 修改时间：2026-09-09
-- AI模型：Muse Spark
-- 修改内容：[生产就绪全量 Schema：18 张多租户表零演示数据；TiDB Vector 备用段；旧表已彻底移除]
-- ============================================================
-- 智题库 TiKu 多租户 SaaS 生产初始化（运维直接执行）
-- 适用：MySQL 8.0 / TiDB Cloud Serverless（默认建表语句两者兼容）
-- 用法：
--   mysql -h <HOST> -u <USER> -p <DB> < tiku_init.sql
-- 首个上帝账号不在此建：服务启动后调用一次
--   POST /api/v1/super-admin/bootstrap {"phone":"13800000000","password":"..."}
-- （全库无用户时才可调用，调用后永久自锁）
-- TiDB 向量检索：默认关闭。需要时执行文件末尾【TiDB Vector 备用段】，
-- 并在后端环境变量置 TIDB_VECTOR=1（本地/SQLite 保持 0，严禁开发机连云库）。
-- ============================================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- ---------- IAM ----------
CREATE TABLE IF NOT EXISTS `sys_tenant` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `status` VARCHAR(20) DEFAULT 'active',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `sys_user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `phone` VARCHAR(20) NOT NULL COMMENT '手机号全局唯一，绝不带租户字段',
  `username` VARCHAR(50) NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `display_name` VARCHAR(50) DEFAULT '',
  `is_super_admin` TINYINT(1) DEFAULT 0,
  `status` TINYINT(1) DEFAULT 1,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_sys_user_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `sys_tenant_user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `role` VARCHAR(20) DEFAULT 'member' COMMENT 'owner/admin/member',
  `status` VARCHAR(20) DEFAULT 'active',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_tenant_user` (`tenant_id`,`user_id`),
  KEY `ix_tu_tenant` (`tenant_id`),
  KEY `ix_tu_user` (`user_id`),
  CONSTRAINT `fk_tu_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenant` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tu_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- 资源 / 任务 ----------
CREATE TABLE IF NOT EXISTS `resource_categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `target_type` VARCHAR(20) DEFAULT 'resource' COMMENT 'resource/task',
  `sort_order` INT DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_rc_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `resources` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `category_id` INT NULL,
  `type` VARCHAR(20) NOT NULL DEFAULT 'single_choice',
  `content` TEXT NOT NULL,
  `options` JSON NULL,
  `correct_answer` JSON NULL,
  `score` INT DEFAULT 10,
  `creator_id` INT NULL,
  `is_deleted` TINYINT(1) DEFAULT 0,
  `ai_rag_sources` JSON NULL COMMENT '切片级溯源',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_res_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `description` TEXT NULL,
  `cover_image` VARCHAR(500) DEFAULT '',
  `category_id` INT NULL,
  `status` VARCHAR(20) DEFAULT 'draft' COMMENT 'draft/published/archived',
  `is_timed` TINYINT(1) DEFAULT 0,
  `time_limit` INT NULL COMMENT '分钟',
  `start_time` DATETIME NULL COMMENT '保留字段，计时以 deadline+服务端开考为准',
  `deadline` DATETIME NULL,
  `verification_mode` VARCHAR(20) DEFAULT 'manual' COMMENT 'manual/ai_auto',
  `creator_id` INT NULL,
  `ai_rag_sources` JSON NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_task_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `task_resources` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `task_id` INT NOT NULL,
  `resource_id` INT NOT NULL,
  `score` INT DEFAULT 10,
  `sort_order` INT DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `ix_tr_task` (`task_id`),
  KEY `ix_tr_res` (`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `task_records` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `task_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `status` VARCHAR(30) DEFAULT 'pending' COMMENT 'pending/submitted/pending_verification/verified；行创建=服务端开考时刻',
  `score` INT NULL,
  `time_spent` INT DEFAULT 0 COMMENT '服务端结算，客户端上报仅参考',
  `answers` JSON NULL,
  `ai_result` JSON NULL,
  `ai_rag_sources` JSON NULL,
  `comments` VARCHAR(500) DEFAULT '',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '开考时刻（服务端）',
  `submit_time` DATETIME NULL COMMENT '提交时刻（服务端）',
  PRIMARY KEY (`id`),
  KEY `ix_trec_tenant` (`tenant_id`),
  KEY `ix_trec_task` (`task_id`),
  KEY `ix_trec_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `resource_favorites` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `resource_id` INT NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_fav_tenant_user_resource` (`tenant_id`,`user_id`,`resource_id`),
  KEY `ix_fav_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- 知识库 ----------
CREATE TABLE IF NOT EXISTS `kb_documents` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `scope` VARCHAR(20) DEFAULT 'private' COMMENT 'public/private',
  `creator_id` INT NOT NULL,
  `file_name` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(500) DEFAULT '',
  `status` VARCHAR(20) DEFAULT 'done',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_kb_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `kb_chunks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `document_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `embedding` TEXT NULL COMMENT '向量JSON（本地/MySQL）；TiDB 启用备用段 embedding_vec',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_kbc_tenant` (`tenant_id`),
  KEY `ix_kbc_doc` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- AI 会话 / 租户网关 ----------
CREATE TABLE IF NOT EXISTS `ai_sessions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `title` VARCHAR(100) DEFAULT '新对话',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_ais_tenant_user` (`tenant_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ai_messages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `session_id` INT NOT NULL,
  `role` VARCHAR(20) NOT NULL,
  `content` TEXT NOT NULL,
  `rag_sources` JSON NULL COMMENT '对话级溯源持久化',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_aim_session` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ai_tenant_config` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `enabled` TINYINT(1) DEFAULT 1,
  `chat_api_url` VARCHAR(500) DEFAULT '',
  `chat_api_key` VARCHAR(500) DEFAULT '',
  `chat_model` VARCHAR(100) DEFAULT '',
  `embed_model` VARCHAR(100) DEFAULT '',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_ai_cfg_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- 运营 ----------
CREATE TABLE IF NOT EXISTS `banners` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `image_url` VARCHAR(500) NOT NULL,
  `link_type` VARCHAR(20) DEFAULT 'none',
  `link_value` VARCHAR(500) DEFAULT '',
  `sort_order` INT DEFAULT 0,
  `is_enabled` TINYINT(1) DEFAULT 1,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_bn_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `banner_settings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `interval_seconds` INT DEFAULT 4,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_bs_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `content` TEXT NULL,
  `notif_type` VARCHAR(30) DEFAULT 'system',
  `link` VARCHAR(255) DEFAULT '',
  `is_read` TINYINT(1) DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_nt_tenant_user` (`tenant_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL,
  `actor_id` INT NULL,
  `actor_name` VARCHAR(50) DEFAULT '',
  `operator_type` VARCHAR(20) DEFAULT 'member',
  `action` VARCHAR(50) NOT NULL,
  `target_type` VARCHAR(50) DEFAULT '',
  `target_id` INT NULL,
  `summary` VARCHAR(255) DEFAULT '',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_al_tenant` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS=1;

-- ============================================================
-- 【TiDB Vector 备用段】（默认不执行）
-- 前提：生产库为 TiDB Cloud Serverless，且 kb_chunks 已有数据。
-- 运维执行后，后端环境变量置 TIDB_VECTOR=1（EMBED_DIM 与向量维度一致，默认 1536），
-- 服务自动切换原生 VEC_COSINE_DISTANCE 检索 embedding_vec 列；
-- TIDB_VECTOR=0（默认）时永远走本地分支，不连云库。
-- 注意：SQLite/MySQL 本地环境严禁执行本段。
-- ============================================================
-- ALTER TABLE `kb_chunks` ADD COLUMN `embedding_vec` VECTOR(1536) NULL COMMENT 'TiDB 原生向量列';
-- 回填（示例，按实际 embedding 维度调整；NULL 行检索时自动跳过）：
-- UPDATE `kb_chunks` SET `embedding_vec` = CAST(`embedding` AS VECTOR(1536)) WHERE `embedding` IS NOT NULL AND `embedding` != '' AND `embedding` != '[]';
