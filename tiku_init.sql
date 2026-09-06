-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: tiku_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '管理员账号',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `role` varchar(20) DEFAULT NULL COMMENT '角色 (super_admin, admin)',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `status` tinyint(1) DEFAULT '1',
  `ai_quota_limit` int DEFAULT '0',
  `daily_ai_quota` int DEFAULT '0',
  `quota_reset_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_admins_username` (`username`),
  KEY `ix_admins_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (2,'admin','$2b$12$ssCpU0hIUIe3SAuPoqB3P.NRbq5AtRyI6G0GHikqs1f1dybhVpYaa','super_admin','2026-09-03 22:51:46',1,0,6,'2026-09-06'),(3,'admreg','$2b$12$W2MjuHoyKKk4xZZGzAByC.zjQoLk2By87mGUgc5slxne3wh.2DJfm','super_admin','2026-09-04 01:16:33',1,0,0,NULL);
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ai_usage_logs`
--

DROP TABLE IF EXISTS `ai_usage_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ai_usage_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int DEFAULT NULL COMMENT '发起老师ID (null=系统业务兜底调用)',
  `action` varchar(30) NOT NULL COMMENT '动作 (question_gen, exam_gen, chat, grading)',
  `quota_delta` int DEFAULT NULL COMMENT '个人额度变动 (负数=扣减, 0=系统调用)',
  `detail` json DEFAULT NULL COMMENT '调用明细 (模型/耗时/题目数等)',
  `created_at` datetime DEFAULT NULL COMMENT '调用时间',
  PRIMARY KEY (`id`),
  KEY `ix_ai_usage_logs_admin_id` (`admin_id`),
  KEY `ix_ai_usage_logs_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ai_usage_logs`
--

LOCK TABLES `ai_usage_logs` WRITE;
/*!40000 ALTER TABLE `ai_usage_logs` DISABLE KEYS */;
INSERT INTO `ai_usage_logs` VALUES (2,NULL,'grading',0,'{\"exam_id\": 2, \"record_id\": 18, \"short_count\": 1}','2026-09-06 18:06:58'),(3,2,'question_gen',-1,'{\"count\": 2, \"q_type\": \"single\"}','2026-09-06 11:09:12'),(4,2,'exam_gen',-1,'{\"specs\": [{\"count\": 2, \"score\": null, \"q_type\": \"single\"}, {\"count\": 1, \"score\": null, \"q_type\": \"judge\"}, {\"count\": 1, \"score\": null, \"q_type\": \"short\"}], \"title\": \"AI组卷·Python基础0906190846\"}','2026-09-06 11:09:20'),(5,2,'question_gen',-1,'{\"count\": 2, \"q_type\": \"single\"}','2026-09-06 11:13:09'),(6,2,'exam_gen',-1,'{\"specs\": [{\"count\": 2, \"score\": null, \"q_type\": \"single\"}, {\"count\": 1, \"score\": null, \"q_type\": \"judge\"}, {\"count\": 1, \"score\": null, \"q_type\": \"short\"}], \"title\": \"AI组卷·Python基础0906191243\"}','2026-09-06 11:13:29'),(7,2,'question_gen',-1,'{\"count\": 2, \"q_type\": \"single\"}','2026-09-06 11:16:33'),(8,2,'exam_gen',-1,'{\"specs\": [{\"count\": 2, \"score\": null, \"q_type\": \"single\"}, {\"count\": 1, \"score\": null, \"q_type\": \"judge\"}, {\"count\": 1, \"score\": null, \"q_type\": \"short\"}], \"title\": \"AI组卷·Python基础0906191607\"}','2026-09-06 11:16:42'),(9,NULL,'grading',0,'{\"exam_id\": 11, \"record_id\": 22, \"short_count\": 1}','2026-09-06 11:17:09'),(10,NULL,'grading',0,'{\"exam_id\": 10, \"record_id\": 21, \"short_count\": 1}','2026-09-06 11:17:10'),(11,NULL,'grading',0,'{\"exam_id\": 11, \"record_id\": 23, \"short_count\": 1}','2026-09-06 11:17:14'),(12,2,'question_gen',-1,'{\"count\": 2, \"q_type\": \"single\"}','2026-09-06 11:22:26'),(13,2,'exam_gen',-1,'{\"specs\": [{\"count\": 2, \"score\": null, \"q_type\": \"single\"}, {\"count\": 1, \"score\": null, \"q_type\": \"judge\"}, {\"count\": 1, \"score\": null, \"q_type\": \"short\"}], \"title\": \"AI组卷·Python基础0906192200\"}','2026-09-06 11:22:39'),(14,NULL,'grading',0,'{\"exam_id\": 14, \"record_id\": 28, \"short_count\": 1}','2026-09-06 11:22:58'),(15,NULL,'grading',0,'{\"exam_id\": 13, \"record_id\": 27, \"short_count\": 1}','2026-09-06 11:23:01'),(16,NULL,'grading',0,'{\"exam_id\": 14, \"record_id\": 29, \"short_count\": 1}','2026-09-06 11:23:04');
/*!40000 ALTER TABLE `ai_usage_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int DEFAULT NULL COMMENT '操作人ID (AI 操作时可为空)',
  `operator_type` varchar(20) DEFAULT NULL COMMENT '操作者类型 (admin 人类, ai AI员工, system 系统)',
  `operator_name` varchar(50) DEFAULT NULL COMMENT '操作者名称快照',
  `action_type` varchar(50) NOT NULL COMMENT '动作类型 (create/update/delete/publish/archive/grade/generate...)',
  `target_type` varchar(50) DEFAULT NULL COMMENT '目标对象类型 (question/exam/record/admin/quota)',
  `target_id` int DEFAULT NULL COMMENT '目标对象ID',
  `summary` varchar(255) DEFAULT NULL COMMENT '动作摘要 (便于列表直读)',
  `before_data` json DEFAULT NULL COMMENT '操作前数据快照',
  `after_data` json DEFAULT NULL COMMENT '操作后数据',
  `created_at` datetime DEFAULT NULL COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `ix_audit_logs_id` (`id`),
  KEY `ix_audit_logs_admin_id` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,2,'admin','admin','refill_quota','admin',2,'为 admin 补充今日 AI 额度 +5','null','{\"daily_ai_quota\": 5}','2026-09-06 18:06:24'),(2,2,'admin','admin','create','question',21,'新增题目 #21 [single]','null','{\"type\": \"single\", \"title\": \"HTTP 默认端口是?\", \"source\": \"manual\"}','2026-09-06 18:06:37'),(3,2,'admin','admin','create','question',22,'新增题目 #22 [fill]','null','{\"type\": \"fill\", \"title\": \"HTTPS 的默认端口是___。\", \"source\": \"manual\"}','2026-09-06 18:06:37'),(4,2,'admin','admin','create','question',23,'新增题目 #23 [short]','null','{\"type\": \"short\", \"title\": \"简述 HTTPS 相比 HTTP 的安全改进。\", \"source\": \"manual\"}','2026-09-06 18:06:37'),(5,2,'admin','admin','create','exam',2,'创建试卷《v1.2 冒烟卷》','null','{\"title\": \"v1.2 冒烟卷\", \"status\": \"published\", \"question_count\": 3}','2026-09-06 18:06:37'),(6,NULL,'ai','AI员工','grade','record',18,'AI 全托管批阅并发布成绩: 记录#18 得分80','null','{\"operator\": \"ai\", \"short_scores\": {\"23\": 20}}','2026-09-06 18:06:58'),(7,2,'admin','admin','refill_quota','admin',2,'为 admin 补充今日 AI 额度 +10','null','{\"daily_ai_quota\": 14}','2026-09-06 11:09:12'),(8,2,'admin','admin','create','question',24,'新增题目 #24 [single]','null','{\"type\": \"single\", \"title\": \"HTTP 默认端口是?\", \"source\": \"manual\"}','2026-09-06 11:09:12'),(9,2,'admin','admin','create','question',25,'新增题目 #25 [multiple]','null','{\"type\": \"multiple\", \"title\": \"以下哪些是 HTTP 方法?\", \"source\": \"manual\"}','2026-09-06 11:09:12'),(10,2,'admin','admin','create','question',26,'新增题目 #26 [judge]','null','{\"type\": \"judge\", \"title\": \"HTTPS 的默认端口是 443。\", \"source\": \"manual\"}','2026-09-06 11:09:12'),(11,2,'admin','admin','create','question',27,'新增题目 #27 [fill]','null','{\"type\": \"fill\", \"title\": \"中国的首都是___，简称___。\", \"source\": \"manual\"}','2026-09-06 11:09:12'),(12,2,'admin','admin','create','question',28,'新增题目 #28 [short]','null','{\"type\": \"short\", \"title\": \"简述 HTTPS 相比 HTTP 的安全改进。\", \"source\": \"manual\"}','2026-09-06 11:09:12'),(13,2,'admin','admin','create','question',NULL,'批量入库 2 道题目 (来源: AI生成)','null','{\"question_ids\": [29, 30]}','2026-09-06 11:09:20'),(14,2,'admin','admin','create','exam',3,'创建试卷《自测·客观卷0906190846》','null','{\"title\": \"自测·客观卷0906190846\", \"status\": \"published\", \"question_count\": 3}','2026-09-06 11:09:20'),(15,2,'admin','admin','create','exam',4,'创建试卷《自测·主观卷0906190846》','null','{\"title\": \"自测·主观卷0906190846\", \"status\": \"published\", \"question_count\": 2}','2026-09-06 11:09:20'),(16,2,'ai','admin','generate','exam',5,'AI 智能组卷《AI组卷·Python基础0906190846》(草稿, 复用2题/新生成1题)','null','{\"status\": \"draft\", \"question_ids\": [29, 30, 31]}','2026-09-06 11:09:37'),(17,2,'admin','admin','create','question',32,'新增题目 #32 [single]','null','{\"type\": \"single\", \"title\": \"HTTP 默认端口是?\", \"source\": \"manual\"}','2026-09-06 11:13:09'),(18,2,'admin','admin','create','question',33,'新增题目 #33 [multiple]','null','{\"type\": \"multiple\", \"title\": \"以下哪些是 HTTP 方法?\", \"source\": \"manual\"}','2026-09-06 11:13:09'),(19,2,'admin','admin','create','question',34,'新增题目 #34 [judge]','null','{\"type\": \"judge\", \"title\": \"HTTPS 的默认端口是 443。\", \"source\": \"manual\"}','2026-09-06 11:13:09'),(20,2,'admin','admin','create','question',35,'新增题目 #35 [fill]','null','{\"type\": \"fill\", \"title\": \"中国的首都是___，简称___。\", \"source\": \"manual\"}','2026-09-06 11:13:09'),(21,2,'admin','admin','create','question',36,'新增题目 #36 [short]','null','{\"type\": \"short\", \"title\": \"简述 HTTPS 相比 HTTP 的安全改进。\", \"source\": \"manual\"}','2026-09-06 11:13:09'),(22,2,'admin','admin','create','question',NULL,'批量入库 2 道题目 (来源: AI生成)','null','{\"question_ids\": [37, 38]}','2026-09-06 11:13:29'),(23,2,'admin','admin','create','exam',6,'创建试卷《自测·客观卷0906191243》','null','{\"title\": \"自测·客观卷0906191243\", \"status\": \"published\", \"question_count\": 3}','2026-09-06 11:13:29'),(24,2,'admin','admin','create','exam',7,'创建试卷《自测·主观卷0906191243》','null','{\"title\": \"自测·主观卷0906191243\", \"status\": \"published\", \"question_count\": 2}','2026-09-06 11:13:29'),(25,2,'ai','admin','generate','exam',8,'AI 智能组卷《AI组卷·Python基础0906191243》(草稿, 复用3题/新生成0题)','null','{\"status\": \"draft\", \"question_ids\": [29, 30, 31]}','2026-09-06 11:13:55'),(26,2,'admin','admin','create','question',39,'新增题目 #39 [single]','null','{\"type\": \"single\", \"title\": \"HTTP 默认端口是?\", \"source\": \"manual\"}','2026-09-06 11:16:33'),(27,2,'admin','admin','create','question',40,'新增题目 #40 [multiple]','null','{\"type\": \"multiple\", \"title\": \"以下哪些是 HTTP 方法?\", \"source\": \"manual\"}','2026-09-06 11:16:33'),(28,2,'admin','admin','create','question',41,'新增题目 #41 [judge]','null','{\"type\": \"judge\", \"title\": \"HTTPS 的默认端口是 443。\", \"source\": \"manual\"}','2026-09-06 11:16:33'),(29,2,'admin','admin','create','question',42,'新增题目 #42 [fill]','null','{\"type\": \"fill\", \"title\": \"中国的首都是___，简称___。\", \"source\": \"manual\"}','2026-09-06 11:16:33'),(30,2,'admin','admin','create','question',43,'新增题目 #43 [short]','null','{\"type\": \"short\", \"title\": \"简述 HTTPS 相比 HTTP 的安全改进。\", \"source\": \"manual\"}','2026-09-06 11:16:33'),(31,2,'admin','admin','create','question',NULL,'批量入库 2 道题目 (来源: AI生成)','null','{\"question_ids\": [44, 45]}','2026-09-06 11:16:42'),(32,2,'admin','admin','create','exam',9,'创建试卷《自测·客观卷0906191607》','null','{\"title\": \"自测·客观卷0906191607\", \"status\": \"published\", \"question_count\": 3}','2026-09-06 11:16:42'),(33,2,'admin','admin','create','exam',10,'创建试卷《自测·主观卷0906191607》','null','{\"title\": \"自测·主观卷0906191607\", \"status\": \"published\", \"question_count\": 2}','2026-09-06 11:16:42'),(34,2,'ai','admin','generate','exam',11,'AI 智能组卷《AI组卷·Python基础0906191607》(草稿, 复用2题/新生成1题)','null','{\"status\": \"draft\", \"question_ids\": [29, 30, 46]}','2026-09-06 11:17:01'),(35,2,'admin','admin','update_status','exam',11,'试卷《AI组卷·Python基础0906191607》状态 draft → published','{\"status\": \"draft\"}','{\"status\": \"published\"}','2026-09-06 11:17:01'),(36,2,'admin','admin','update','exam',11,'编辑试卷《AI组卷·Python基础0906191607》','{\"title\": \"AI组卷·Python基础0906191607\", \"status\": \"published\", \"is_ai_auto_grade\": true}','{\"title\": \"AI组卷·Python基础0906191607\", \"status\": \"published\"}','2026-09-06 11:17:01'),(37,2,'admin','admin','grade','record',21,'批阅发布: 《自测·主观卷0906191607》答卷#21 最终得分 35','null','{\"accept_ai\": false, \"short_scores\": {\"43\": 15}}','2026-09-06 11:17:04'),(38,NULL,'ai','AI员工','grade','record',22,'AI 全托管批阅并发布成绩: 记录#22 得分0','null','{\"operator\": \"ai\", \"short_scores\": {\"46\": 0}}','2026-09-06 11:17:09'),(39,NULL,'ai','AI员工','grade','record',23,'AI 全托管批阅并发布成绩: 记录#23 得分0','null','{\"operator\": \"ai\", \"short_scores\": {\"46\": 0}}','2026-09-06 11:17:14'),(40,2,'admin','admin','create','question',47,'新增题目 #47 [single]','null','{\"type\": \"single\", \"title\": \"HTTP 默认端口是?\", \"source\": \"manual\"}','2026-09-06 11:22:26'),(41,2,'admin','admin','create','question',48,'新增题目 #48 [multiple]','null','{\"type\": \"multiple\", \"title\": \"以下哪些是 HTTP 方法?\", \"source\": \"manual\"}','2026-09-06 11:22:26'),(42,2,'admin','admin','create','question',49,'新增题目 #49 [judge]','null','{\"type\": \"judge\", \"title\": \"HTTPS 的默认端口是 443。\", \"source\": \"manual\"}','2026-09-06 11:22:26'),(43,2,'admin','admin','create','question',50,'新增题目 #50 [fill]','null','{\"type\": \"fill\", \"title\": \"中国的首都是___，简称___。\", \"source\": \"manual\"}','2026-09-06 11:22:26'),(44,2,'admin','admin','create','question',51,'新增题目 #51 [short]','null','{\"type\": \"short\", \"title\": \"简述 HTTPS 相比 HTTP 的安全改进。\", \"source\": \"manual\"}','2026-09-06 11:22:26'),(45,2,'admin','admin','create','question',NULL,'批量入库 2 道题目 (来源: AI生成)','null','{\"question_ids\": [52, 53]}','2026-09-06 11:22:39'),(46,2,'admin','admin','create','exam',12,'创建试卷《自测·客观卷0906192200》','null','{\"title\": \"自测·客观卷0906192200\", \"status\": \"published\", \"question_count\": 3}','2026-09-06 11:22:39'),(47,2,'admin','admin','create','exam',13,'创建试卷《自测·主观卷0906192200》','null','{\"title\": \"自测·主观卷0906192200\", \"status\": \"published\", \"question_count\": 2}','2026-09-06 11:22:39'),(48,2,'ai','admin','generate','exam',14,'AI 智能组卷《AI组卷·Python基础0906192200》(草稿, 复用4题/新生成0题)','null','{\"status\": \"draft\", \"question_ids\": [29, 30, 46, 18]}','2026-09-06 11:22:49'),(49,2,'admin','admin','update_status','exam',14,'试卷《AI组卷·Python基础0906192200》状态 draft → published','{\"status\": \"draft\"}','{\"status\": \"published\"}','2026-09-06 11:22:49'),(50,2,'admin','admin','update','exam',14,'编辑试卷《AI组卷·Python基础0906192200》','{\"title\": \"AI组卷·Python基础0906192200\", \"status\": \"published\", \"is_ai_auto_grade\": true}','{\"title\": \"AI组卷·Python基础0906192200\", \"status\": \"published\"}','2026-09-06 11:22:49'),(51,2,'admin','admin','grade','record',27,'批阅发布: 《自测·主观卷0906192200》答卷#27 最终得分 35','null','{\"accept_ai\": false, \"short_scores\": {\"51\": 15}}','2026-09-06 11:22:52'),(52,NULL,'ai','AI员工','grade','record',28,'AI 全托管批阅并发布成绩: 记录#28 得分0','null','{\"operator\": \"ai\", \"short_scores\": {\"46\": 0}}','2026-09-06 11:22:58'),(53,NULL,'ai','AI员工','grade','record',29,'AI 全托管批阅并发布成绩: 记录#29 得分0','null','{\"operator\": \"ai\", \"short_scores\": {\"46\": 0}}','2026-09-06 11:23:04');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banner_settings`
--

DROP TABLE IF EXISTS `banner_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banner_settings` (
  `id` int NOT NULL,
  `interval_seconds` int DEFAULT NULL COMMENT '轮播间隔秒（2-10）',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banner_settings`
--

LOCK TABLES `banner_settings` WRITE;
/*!40000 ALTER TABLE `banner_settings` DISABLE KEYS */;
INSERT INTO `banner_settings` VALUES (1,5);
/*!40000 ALTER TABLE `banner_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banners`
--

DROP TABLE IF EXISTS `banners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banners` (
  `id` int NOT NULL AUTO_INCREMENT,
  `image_url` varchar(255) NOT NULL COMMENT '图片路径',
  `link_type` varchar(20) NOT NULL COMMENT '链接类型: none, external, internal',
  `link_value` varchar(500) DEFAULT NULL COMMENT '外链URL或站内路径',
  `sort_order` int DEFAULT NULL COMMENT '排序（越小越靠前）',
  `is_enabled` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_banners_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banners`
--

LOCK TABLES `banners` WRITE;
/*!40000 ALTER TABLE `banners` DISABLE KEYS */;
INSERT INTO `banners` VALUES (4,'/uploads/abfcbda2edf04862b7e65b754691ec8b.jpg','none','',1,1,'2026-09-04 07:54:08'),(5,'/uploads/3becb6afe6064e9293d86ef6db5af7f5.png','none','',2,1,'2026-09-04 07:54:20'),(6,'/uploads/52ccadb713074f3eb9bcd3d3cb53bca6.png','none','',3,1,'2026-09-04 12:10:38');
/*!40000 ALTER TABLE `banners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_categories`
--

DROP TABLE IF EXISTS `exam_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '分类名称',
  `icon` varchar(50) DEFAULT NULL COMMENT '分类图标 key',
  `sort_order` int DEFAULT NULL COMMENT '排序规则 (数字越小越靠前)',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `target_type` varchar(20) NOT NULL DEFAULT 'exam' COMMENT 'åˆ†ç±»ç”¨é€”: question, exam',
  PRIMARY KEY (`id`),
  KEY `ix_exam_categories_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_categories`
--

LOCK TABLES `exam_categories` WRITE;
/*!40000 ALTER TABLE `exam_categories` DISABLE KEYS */;
INSERT INTO `exam_categories` VALUES (2,'金融类','folder',2,'2026-09-04 10:08:46','question'),(3,'自考类','folder',3,'2026-09-04 10:08:52','question'),(4,'工程类','folder',1,'2026-09-04 10:08:57','question'),(5,'心理测试','folder',1,'2026-09-04 10:09:05','exam'),(6,'趣味问答','folder',1,'2026-09-04 10:09:10','exam'),(7,'专业试题','folder',1,'2026-09-04 10:09:17','exam'),(8,'消防安全','folder',0,'2026-09-04 10:09:29','question'),(9,'文学类','folder',4,'2026-09-04 12:10:25','question'),(10,'自测题库分类0906190846','folder',1,'2026-09-06 11:09:12','question'),(11,'自测试卷分类0906190846','folder',1,'2026-09-06 11:09:12','exam'),(12,'自测题库分类0906191243','folder',1,'2026-09-06 11:13:09','question'),(13,'自测试卷分类0906191243','folder',1,'2026-09-06 11:13:09','exam'),(14,'自测题库分类0906191607','folder',1,'2026-09-06 11:16:33','question'),(15,'自测试卷分类0906191607','folder',1,'2026-09-06 11:16:33','exam'),(16,'自测题库分类0906192200','folder',1,'2026-09-06 11:22:26','question'),(17,'自测试卷分类0906192200','folder',1,'2026-09-06 11:22:26','exam');
/*!40000 ALTER TABLE `exam_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_questions`
--

DROP TABLE IF EXISTS `exam_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `question_id` int NOT NULL,
  `score` int DEFAULT NULL COMMENT '该题在此试卷中的分值',
  `sort_order` int DEFAULT NULL COMMENT '题目在试卷中的顺序',
  PRIMARY KEY (`id`),
  KEY `ix_exam_questions_exam_id` (`exam_id`),
  KEY `ix_exam_questions_question_id` (`question_id`),
  KEY `ix_exam_questions_id` (`id`),
  CONSTRAINT `exam_questions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE,
  CONSTRAINT `exam_questions_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_questions`
--

LOCK TABLES `exam_questions` WRITE;
/*!40000 ALTER TABLE `exam_questions` DISABLE KEYS */;
INSERT INTO `exam_questions` VALUES (1,1,19,5,1),(2,1,18,5,2),(3,1,17,20,3),(4,1,16,15,4),(8,3,24,10,1),(9,3,25,10,2),(10,3,26,10,3),(11,4,27,20,1),(12,4,28,30,2),(13,5,29,10,1),(14,5,30,10,2),(16,6,32,10,1),(17,6,33,10,2),(18,6,34,10,3),(19,7,35,20,1),(20,7,36,30,2),(21,8,29,10,1),(22,8,30,10,2),(24,9,39,10,1),(25,9,40,10,2),(26,9,41,10,3),(27,10,42,20,1),(28,10,43,30,2),(29,11,29,10,1),(30,11,30,10,2),(31,11,46,10,3),(32,12,47,10,1),(33,12,48,10,2),(34,12,49,10,3),(35,13,50,20,1),(36,13,51,30,2),(37,14,29,10,1),(38,14,30,10,2),(39,14,46,10,3),(40,14,18,5,4);
/*!40000 ALTER TABLE `exam_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_records`
--

DROP TABLE IF EXISTS `exam_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `status` varchar(20) DEFAULT NULL COMMENT '状态 (in_progress, submitted, timeout)',
  `score` int DEFAULT NULL COMMENT '得分',
  `passed` tinyint(1) DEFAULT NULL COMMENT '是否及格',
  `time_spent` int DEFAULT NULL COMMENT '用时时长 (秒)',
  `start_time` datetime DEFAULT NULL COMMENT '开始做题时间',
  `submit_time` datetime DEFAULT NULL COMMENT '提交/结算时间',
  `user_answers` json DEFAULT NULL COMMENT '用户作答答案 JSON {question_id: [''A'']}',
  `ai_grading_result` json DEFAULT NULL,
  `short_scores` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_exam_records_exam_id` (`exam_id`),
  KEY `ix_exam_records_user_id` (`user_id`),
  KEY `ix_exam_records_id` (`id`),
  CONSTRAINT `exam_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `exam_records_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_records`
--

LOCK TABLES `exam_records` WRITE;
/*!40000 ALTER TABLE `exam_records` DISABLE KEYS */;
INSERT INTO `exam_records` VALUES (1,8,1,'timeout',0,0,0,'2026-09-04 10:11:04','2026-09-04 12:06:20',NULL,NULL,NULL),(2,8,1,'timeout',0,0,0,'2026-09-04 10:11:24','2026-09-04 12:06:20',NULL,NULL,NULL),(3,8,1,'timeout',0,0,0,'2026-09-04 10:11:42','2026-09-04 12:06:20',NULL,NULL,NULL),(4,8,1,'timeout',0,0,0,'2026-09-04 10:15:43','2026-09-04 12:06:20',NULL,NULL,NULL),(5,8,1,'submitted',5,0,28807,'2026-09-04 10:25:38','2026-09-04 10:25:45','{\"16\": [\"B\"], \"17\": [\"A\"], \"18\": [\"B\"], \"19\": [\"A\"]}',NULL,NULL),(6,8,1,'timeout',0,0,0,'2026-09-04 10:26:32','2026-09-04 12:06:20',NULL,NULL,NULL),(7,8,1,'timeout',0,0,0,'2026-09-04 10:26:47','2026-09-04 12:06:20',NULL,NULL,NULL),(8,8,1,'timeout',0,0,0,'2026-09-04 10:28:12','2026-09-04 12:06:20',NULL,NULL,NULL),(9,8,1,'timeout',0,0,0,'2026-09-04 12:06:20','2026-09-04 12:42:33',NULL,NULL,NULL),(10,8,1,'submitted',5,0,28811,'2026-09-04 12:06:31','2026-09-04 12:06:42','{\"16\": [], \"17\": [\"B\"], \"18\": [\"A\"], \"19\": [\"B\"]}',NULL,NULL),(11,8,1,'timeout',0,0,0,'2026-09-04 12:12:50','2026-09-04 14:45:43',NULL,NULL,NULL),(12,8,1,'timeout',0,0,0,'2026-09-04 12:12:58','2026-09-04 14:45:43',NULL,NULL,NULL),(13,8,1,'timeout',0,0,0,'2026-09-04 12:14:40','2026-09-04 14:45:43',NULL,NULL,NULL),(14,8,1,'timeout',0,0,0,'2026-09-04 12:42:33','2026-09-04 14:45:43',NULL,NULL,NULL),(15,8,1,'timeout',0,0,0,'2026-09-04 12:42:37','2026-09-04 14:45:43',NULL,NULL,NULL),(16,8,1,'timeout',0,0,0,'2026-09-04 12:42:41','2026-09-04 14:45:43',NULL,NULL,NULL),(17,8,1,'submitted',5,0,28816,'2026-09-04 14:45:43','2026-09-04 14:46:00','{\"16\": [\"C\"], \"17\": [\"A\"], \"18\": [\"B\"], \"19\": [\"A\"]}',NULL,NULL),(19,15,9,'submitted',30,1,300,'2026-09-06 11:17:04','2026-09-06 11:17:04','{\"39\": [\"A\"], \"40\": [\"A\", \"B\", \"D\"], \"41\": [\"A\"]}',NULL,NULL),(20,16,9,'submitted',25,1,200,'2026-09-06 11:17:04','2026-09-06 11:17:04','{\"39\": [\"A\"], \"40\": [\"A\"], \"41\": [\"A\"]}',NULL,NULL),(21,17,10,'submitted',35,1,600,'2026-09-06 11:17:04','2026-09-06 11:17:04','{\"42\": [\"北京市\", \" 京 \"], \"43\": [\"HTTPS 用 TLS 加密，端口 443，但没提证书\"]}','{\"error\": null, \"graded_at\": \"2026-09-06 11:17:10\", \"suggestions\": [{\"comment\": \"提到了TLS加密，踩中第1个踩分点；但未提及证书验证身份，也未提及防窃听防篡改，后两个踩分点均未得分。\", \"question_id\": 43, \"suggested_score\": 10}]}','{\"43\": 15}'),(22,18,11,'submitted',0,1,400,'2026-09-06 11:17:04','2026-09-06 11:17:09','{\"29\": [\"A\"], \"30\": [\"A\"], \"46\": [\"HTTPS 通过 TLS 加密传输并用证书验证身份，可以防窃听防篡改\"]}','{\"error\": null, \"graded_at\": \"2026-09-06 11:17:08\", \"suggestions\": [{\"comment\": \"学生作答内容与题目完全无关，答的是HTTPS与TLS加密，未涉及Python for循环和while循环的任何要点，全部踩分点均未命中。\", \"question_id\": 46, \"suggested_score\": 0}]}','{\"46\": 0}'),(23,19,11,'submitted',0,1,400,'2026-09-06 11:17:10','2026-09-06 11:17:14','{\"29\": [\"A\"], \"30\": [\"A\"], \"46\": [\"不知道，随便写的答案\"]}','{\"error\": null, \"graded_at\": \"2026-09-06 11:17:14\", \"suggestions\": [{\"comment\": \"学生明确表示不知道，未涉及for循环遍历可迭代对象、while循环基于条件判断及各自适用场景等任何踩分点，完全未作答。\", \"question_id\": 46, \"suggested_score\": 0}]}','{\"46\": 0}'),(24,16,9,'in_progress',0,0,0,'2026-09-06 11:17:16',NULL,NULL,NULL,NULL),(25,21,12,'submitted',30,1,300,'2026-09-06 11:22:51','2026-09-06 11:22:51','{\"47\": [\"A\"], \"48\": [\"A\", \"B\", \"D\"], \"49\": [\"A\"]}',NULL,NULL),(26,22,12,'submitted',25,1,200,'2026-09-06 11:22:51','2026-09-06 11:22:51','{\"47\": [\"A\"], \"48\": [\"A\"], \"49\": [\"A\"]}',NULL,NULL),(27,23,13,'submitted',35,1,600,'2026-09-06 11:22:51','2026-09-06 11:22:51','{\"50\": [\"北京市\", \" 京 \"], \"51\": [\"HTTPS 用 TLS 加密，端口 443，但没提证书\"]}','{\"error\": null, \"graded_at\": \"2026-09-06 11:23:00\", \"suggestions\": [{\"comment\": \"提到了TLS加密，踩中第1个踩分点；未提及证书验证身份，也未明确说明防窃听防篡改，仅得1/3分。\", \"question_id\": 51, \"suggested_score\": 10}]}','{\"51\": 15}'),(28,24,14,'submitted',0,0,400,'2026-09-06 11:22:52','2026-09-06 11:22:58','{\"18\": [\"A\"], \"29\": [\"A\"], \"30\": [\"A\"], \"46\": [\"我认为这道题考察的是：简述 Python 中 for 循环和 while 循环的区别及各自适用的场景。。要点如下：第一，需要理解其基本定义；第二，要结合实际应用场景说明其作用与优势；第三，注意与相邻概念的区别。以上是我的完整作答。\"]}','{\"error\": null, \"graded_at\": \"2026-09-06 11:22:58\", \"suggestions\": [{\"comment\": \"学生未实际回答题目内容，仅复述了题干并给出泛泛的答题思路，未涉及for循环遍历可迭代对象、while循环基于条件判断、以及两者各自适用场景等任何踩分点，得0分。\", \"question_id\": 46, \"suggested_score\": 0}]}','{\"46\": 0}'),(29,25,14,'submitted',0,0,400,'2026-09-06 11:23:01','2026-09-06 11:23:04','{\"18\": [\"A\"], \"29\": [\"A\"], \"30\": [\"A\"], \"46\": [\"不知道，随便写的答案\"]}','{\"error\": null, \"graded_at\": \"2026-09-06 11:23:03\", \"suggestions\": [{\"comment\": \"学生未作答，未涉及任何踩分点，得0分。\", \"question_id\": 46, \"suggested_score\": 0}]}','{\"46\": 0}'),(30,22,12,'in_progress',0,0,0,'2026-09-06 11:23:07',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `exam_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exams`
--

DROP TABLE IF EXISTS `exams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL COMMENT '试卷标题',
  `category_id` int DEFAULT NULL COMMENT '分类ID',
  `cover_url` varchar(255) DEFAULT NULL COMMENT '试卷封面图片路径',
  `is_timed` tinyint(1) DEFAULT NULL COMMENT '是否限制作答时长',
  `time_limit` int DEFAULT NULL COMMENT '限时时长 (分钟)',
  `total_score` int DEFAULT NULL COMMENT '试卷总分',
  `pass_score` int DEFAULT NULL COMMENT '及格分数',
  `is_recommended` tinyint(1) DEFAULT NULL COMMENT '是否在首页推荐推荐',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `pass_percent` int DEFAULT '60' COMMENT 'åŠæ ¼ç™¾åˆ†æ¯”',
  `status` varchar(20) NOT NULL DEFAULT 'draft' COMMENT 'çŠ¶æ€: draft, published, archived',
  `category_name` varchar(100) DEFAULT '',
  `is_random` tinyint(1) DEFAULT '0',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `is_ai_auto_grade` tinyint(1) DEFAULT '0',
  `creator_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_exams_id` (`id`),
  CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `exam_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exams`
--

LOCK TABLES `exams` WRITE;
/*!40000 ALTER TABLE `exams` DISABLE KEYS */;
INSERT INTO `exams` VALUES (1,'心理健康测评',5,'preset:1',1,30,45,27,0,'2026-09-04 10:10:51',60,'published','心理测试',0,NULL,NULL,0,NULL),(3,'自测·客观卷0906190846',11,'',1,30,30,18,0,'2026-09-06 11:09:20',60,'published','自测试卷分类0906190846',0,NULL,NULL,0,2),(4,'自测·主观卷0906190846',11,'',1,30,50,25,0,'2026-09-06 11:09:20',50,'published','自测试卷分类0906190846',0,NULL,NULL,0,2),(5,'AI组卷·Python基础0906190846',11,'',1,30,0,0,0,'2026-09-06 11:09:37',50,'draft','',0,NULL,NULL,1,2),(6,'自测·客观卷0906191243',13,'',1,30,30,18,0,'2026-09-06 11:13:29',60,'published','自测试卷分类0906191243',0,NULL,NULL,0,2),(7,'自测·主观卷0906191243',13,'',1,30,50,25,0,'2026-09-06 11:13:29',50,'published','自测试卷分类0906191243',0,NULL,NULL,0,2),(8,'AI组卷·Python基础0906191243',13,'',1,30,0,0,0,'2026-09-06 11:13:55',50,'draft','',0,NULL,NULL,1,2),(9,'自测·客观卷0906191607',15,'',1,30,30,18,0,'2026-09-06 11:16:42',60,'published','自测试卷分类0906191607',0,NULL,NULL,0,2),(10,'自测·主观卷0906191607',15,'',1,30,50,25,0,'2026-09-06 11:16:42',50,'published','自测试卷分类0906191607',0,NULL,NULL,0,2),(11,'AI组卷·Python基础0906191607',15,'',1,30,0,0,0,'2026-09-06 11:17:01',50,'published','自测试卷分类0906191607',0,NULL,NULL,1,2),(12,'自测·客观卷0906192200',17,'',1,30,30,18,0,'2026-09-06 11:22:39',60,'published','自测试卷分类0906192200',0,NULL,NULL,0,2),(13,'自测·主观卷0906192200',17,'',1,30,50,25,0,'2026-09-06 11:22:39',50,'published','自测试卷分类0906192200',0,NULL,NULL,0,2),(14,'AI组卷·Python基础0906192200',17,'',1,30,35,18,0,'2026-09-06 11:22:49',50,'published','自测试卷分类0906192200',0,NULL,NULL,1,2);
/*!40000 ALTER TABLE `exams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL COMMENT '接收老师ID',
  `title` varchar(200) NOT NULL COMMENT '通知标题',
  `content` text COMMENT '通知正文',
  `notif_type` varchar(30) DEFAULT NULL COMMENT '通知类型 (grading, exam_draft, ai_error, system)',
  `link` varchar(255) DEFAULT NULL COMMENT 'B端跳转路径 (仅 /admin/ 开头)',
  `is_read` tinyint(1) DEFAULT NULL COMMENT '是否已读',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_notifications_admin_id` (`admin_id`),
  KEY `ix_notifications_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,2,'AI 全托管批阅完成','《v1.2 冒烟卷》答卷 #18 已由 AI 批阅完毕并自动发布成绩（80 分）。','grading','/admin/grading',0,'2026-09-06 18:06:58'),(2,2,'AI 组卷草稿已生成','《AI组卷·Python基础0906190846》已生成草稿（共 3 题, 其中 AI 新生成 1 题），请检查后手动上架。','exam_draft','/admin/exams',0,'2026-09-06 11:09:37'),(3,2,'AI 组卷草稿已生成','《AI组卷·Python基础0906191243》已生成草稿（共 3 题, 其中 AI 新生成 0 题），请检查后手动上架。','exam_draft','/admin/exams',0,'2026-09-06 11:13:55'),(4,2,'AI 组卷草稿已生成','《AI组卷·Python基础0906191607》已生成草稿（共 3 题, 其中 AI 新生成 1 题），请检查后手动上架。','exam_draft','/admin/exams',0,'2026-09-06 11:17:01'),(5,2,'AI 全托管批阅完成','《AI组卷·Python基础0906191607》答卷 #22 已由 AI 批阅完毕并自动发布成绩（0 分）。','grading','/admin/grading',0,'2026-09-06 11:17:09'),(6,2,'AI 全托管批阅完成','《AI组卷·Python基础0906191607》答卷 #23 已由 AI 批阅完毕并自动发布成绩（0 分）。','grading','/admin/grading',0,'2026-09-06 11:17:14'),(7,2,'AI 组卷草稿已生成','《AI组卷·Python基础0906192200》已生成草稿（共 4 题, 其中 AI 新生成 0 题），请检查后手动上架。','exam_draft','/admin/exams',0,'2026-09-06 11:22:49'),(8,2,'AI 全托管批阅完成','《AI组卷·Python基础0906192200》答卷 #28 已由 AI 批阅完毕并自动发布成绩（0 分）。','grading','/admin/grading',0,'2026-09-06 11:22:58'),(9,2,'AI 全托管批阅完成','《AI组卷·Python基础0906192200》答卷 #29 已由 AI 批阅完毕并自动发布成绩（0 分）。','grading','/admin/grading',0,'2026-09-06 11:23:04');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(20) NOT NULL COMMENT '题型 (single, multiple, judge, fill)',
  `title` text NOT NULL COMMENT '题目标题/题干',
  `options` json DEFAULT NULL COMMENT '选项列表 JSON [{''key'':''A'', ''text'':''xxx''}]',
  `answer` json NOT NULL COMMENT '正确答案 JSON [''A''] 或 [''A'', ''B'']',
  `explanation` text COMMENT '文字解析',
  `difficulty` varchar(20) DEFAULT NULL COMMENT '难度 (easy, medium, hard)',
  `category_id` int DEFAULT NULL COMMENT '所属分类ID',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `score` int DEFAULT '10' COMMENT 'é¢˜ç›®é»˜è®¤åˆ†å€¼',
  `is_deleted` tinyint(1) DEFAULT '0',
  `source` varchar(20) DEFAULT 'manual',
  `grading_points` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_questions_id` (`id`),
  CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `exam_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (11,'single','以下哪种灭火器适合扑灭电气火灾？','[{\"key\": \"A\", \"text\": \"泡沫灭火器\"}, {\"key\": \"B\", \"text\": \"水基型灭火器\"}, {\"key\": \"C\", \"text\": \"二氧化碳灭火器\"}, {\"key\": \"D\", \"text\": \"干粉灭火器\"}]','[\"C\"]','电气火灾不能用水或泡沫，应使用二氧化碳或干粉灭火器','easy',4,'2026-09-04 10:09:29',10,0,'manual',NULL),(12,'single','下列哪项不属于消防四个能力建设内容？','[{\"key\": \"A\", \"text\": \"检查消除火灾隐患的能力\"}, {\"key\": \"B\", \"text\": \"扑救初期火灾的能力\"}, {\"key\": \"C\", \"text\": \"组织引导人员疏散逃生的能力\"}, {\"key\": \"D\", \"text\": \"独立扑救大型火灾的能力\"}]','[\"D\"]','四个能力不含独立扑救大型火灾','medium',4,'2026-09-04 10:09:29',10,0,'manual',NULL),(13,'single','发现火灾时，第一步应该做什么？','[{\"key\": \"A\", \"text\": \"立即自行扑火\"}, {\"key\": \"B\", \"text\": \"大声呼救\"}, {\"key\": \"C\", \"text\": \"拨打119报警\"}, {\"key\": \"D\", \"text\": \"先转移财物\"}]','[\"C\"]','发现火灾应第一时间拨打119报警','easy',3,'2026-09-04 10:09:29',10,0,'manual',NULL),(14,'single','安全出口标志灯的颜色是？','[{\"key\": \"A\", \"text\": \"红色\"}, {\"key\": \"B\", \"text\": \"黄色\"}, {\"key\": \"C\", \"text\": \"绿色\"}, {\"key\": \"D\", \"text\": \"蓝色\"}]','[\"C\"]','安全出口标志灯为绿色，便于在浓烟中识别','easy',4,'2026-09-04 10:09:29',10,0,'manual',NULL),(15,'multiple','以下哪些属于常见的火灾逃生自救方法（多选）？','[{\"key\": \"A\", \"text\": \"低姿态匍匐前进\"}, {\"key\": \"B\", \"text\": \"用湿毛巾捂住口鼻\"}, {\"key\": \"C\", \"text\": \"乘坐电梯逃跑\"}, {\"key\": \"D\", \"text\": \"向有光亮处爬行\"}]','[\"A\", \"B\", \"D\"]','乘坐电梯逃跑是错误的，火灾时电梯可能断电或成为烟道','medium',3,'2026-09-04 10:09:29',15,0,'manual',NULL),(16,'multiple','以下哪些行为可能引发火灾（多选）？','[{\"key\": \"A\", \"text\": \"在床上吸烟\"}, {\"key\": \"B\", \"text\": \"电线私拉乱接\"}, {\"key\": \"C\", \"text\": \"规范使用燃气\"}, {\"key\": \"D\", \"text\": \"长期不清理油烟机\"}]','[\"A\", \"B\", \"D\"]','在床上吸烟、私拉电线、不清理油烟机均是常见火灾隐患','easy',3,'2026-09-04 10:09:29',15,0,'manual',NULL),(17,'multiple','灭火的基本原理包括哪几种（多选）？','[{\"key\": \"A\", \"text\": \"冷却法降低燃烧温度\"}, {\"key\": \"B\", \"text\": \"窒息法隔绝氧气\"}, {\"key\": \"C\", \"text\": \"隔离法移除可燃物\"}, {\"key\": \"D\", \"text\": \"转移法转移财产\"}]','[\"A\", \"B\", \"C\"]','灭火三要素为冷却、窒息、隔离，转移财产不属于灭火原理','hard',2,'2026-09-04 10:09:29',20,0,'manual',NULL),(18,'judge','家用电器着火时，应立即用水扑灭。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"B\"]','家用电器着火应先断电，再用干粉或二氧化碳灭火器扑救，不能直接用水','easy',3,'2026-09-04 10:09:29',5,0,'manual',NULL),(19,'judge','在高层建筑发生火灾时，人员应向上疏散到楼顶等待救援。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"B\"]','高层火灾应向下疏散至安全出口，若下方被堵才可至楼顶等待救援','medium',3,'2026-09-04 10:09:29',5,0,'manual',NULL),(20,'judge','干粉灭火器在有效期内可用于扑灭固体液体气体及电气火灾。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"A\"]','干粉灭火器适用范围广，可扑灭A类B类C类及电气火灾','medium',8,'2026-09-04 10:09:29',4,0,'manual',NULL),(24,'single','HTTP 默认端口是?','[{\"key\": \"A\", \"text\": \"80\"}, {\"key\": \"B\", \"text\": \"443\"}, {\"key\": \"C\", \"text\": \"22\"}, {\"key\": \"D\", \"text\": \"3389\"}]','[\"A\"]','HTTP 80 / HTTPS 443','medium',10,'2026-09-06 11:09:12',10,0,'manual','[]'),(25,'multiple','以下哪些是 HTTP 方法?','[{\"key\": \"A\", \"text\": \"GET\"}, {\"key\": \"B\", \"text\": \"POST\"}, {\"key\": \"C\", \"text\": \"SEND\"}, {\"key\": \"D\", \"text\": \"DELETE\"}]','[\"A\", \"B\", \"D\"]','SEND 不是 HTTP 方法','medium',10,'2026-09-06 11:09:12',10,0,'manual','[]'),(26,'judge','HTTPS 的默认端口是 443。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"A\"]','HTTPS 默认 443','medium',10,'2026-09-06 11:09:12',10,0,'manual','[]'),(27,'fill','中国的首都是___，简称___。','[]','[[\"北京\", \"北京市\"], [\"京\"]]','一空多答示例','medium',10,'2026-09-06 11:09:12',20,0,'manual','[]'),(28,'short','简述 HTTPS 相比 HTTP 的安全改进。','[]','[\"HTTPS 使用 TLS/SSL 加密传输，并通过证书验证服务器身份，防止窃听与篡改\"]','按踩分点给分','medium',10,'2026-09-06 11:09:12',30,0,'manual','[\"TLS/SSL 加密\", \"证书验证身份\", \"防窃听防篡改\"]'),(29,'single','以下哪个是合法的 Python 变量名？','[{\"key\": \"A\", \"text\": \"2name\"}, {\"key\": \"B\", \"text\": \"my-var\"}, {\"key\": \"C\", \"text\": \"_count\"}, {\"key\": \"D\", \"text\": \"class\"}]','[\"C\"]','Python 变量名必须以字母或下划线开头，不能以数字开头（排除A）；变量名中不能包含减号等运算符（排除B）；变量名不能是 Python 关键字（class 是关键字，排除D）；_count 以下划线开头，符合命名规则，是合法变量名。','easy',10,'2026-09-06 11:09:20',10,0,'ai','[]'),(30,'single','关于 Python 中列表（list）和元组（tuple）的区别，以下说法正确的是？','[{\"key\": \"A\", \"text\": \"列表和元组都可以随意修改其中的元素\"}, {\"key\": \"B\", \"text\": \"列表用圆括号 () 定义，元组用方括号 [] 定义\"}, {\"key\": \"C\", \"text\": \"列表是可变序列，元组是不可变序列\"}, {\"key\": \"D\", \"text\": \"列表和元组在功能上完全相同，没有任何区别\"}]','[\"C\"]','列表（list）用方括号 [] 定义，是可变序列，可以增删改元素；元组（tuple）用圆括号 () 定义，是不可变序列，创建后不能修改其元素。选项A错误，元组不可修改；选项B错误，括号用法说反了；选项D错误，两者有本质区别。','easy',10,'2026-09-06 11:09:20',10,0,'ai','[]'),(32,'single','HTTP 默认端口是?','[{\"key\": \"A\", \"text\": \"80\"}, {\"key\": \"B\", \"text\": \"443\"}, {\"key\": \"C\", \"text\": \"22\"}, {\"key\": \"D\", \"text\": \"3389\"}]','[\"A\"]','HTTP 80 / HTTPS 443','medium',12,'2026-09-06 11:13:09',10,0,'manual','[]'),(33,'multiple','以下哪些是 HTTP 方法?','[{\"key\": \"A\", \"text\": \"GET\"}, {\"key\": \"B\", \"text\": \"POST\"}, {\"key\": \"C\", \"text\": \"SEND\"}, {\"key\": \"D\", \"text\": \"DELETE\"}]','[\"A\", \"B\", \"D\"]','SEND 不是 HTTP 方法','medium',12,'2026-09-06 11:13:09',10,0,'manual','[]'),(34,'judge','HTTPS 的默认端口是 443。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"A\"]','HTTPS 默认 443','medium',12,'2026-09-06 11:13:09',10,0,'manual','[]'),(35,'fill','中国的首都是___，简称___。','[]','[[\"北京\", \"北京市\"], [\"京\"]]','一空多答示例','medium',12,'2026-09-06 11:13:09',20,0,'manual','[]'),(36,'short','简述 HTTPS 相比 HTTP 的安全改进。','[]','[\"HTTPS 使用 TLS/SSL 加密传输，并通过证书验证服务器身份，防止窃听与篡改\"]','按踩分点给分','medium',12,'2026-09-06 11:13:09',30,0,'manual','[\"TLS/SSL 加密\", \"证书验证身份\", \"防窃听防篡改\"]'),(37,'single','以下哪个是 Python 中合法的变量名？','[{\"key\": \"A\", \"text\": \"2name\"}, {\"key\": \"B\", \"text\": \"my-var\"}, {\"key\": \"C\", \"text\": \"_count\"}, {\"key\": \"D\", \"text\": \"class\"}]','[\"C\"]','Python 变量命名规则：1) 不能以数字开头，排除 A；2) 不能包含连字符（-），排除 B；3) 不能使用关键字（如 class），排除 D；4) 可以以下划线开头，C 合法。','easy',12,'2026-09-06 11:13:29',10,0,'ai','[]'),(38,'single','关于 Python 中列表（list）与元组（tuple）的区别，下列说法正确的是？','[{\"key\": \"A\", \"text\": \"列表不可变，元组可变\"}, {\"key\": \"B\", \"text\": \"列表用圆括号 () 定义，元组用方括号 [] 定义\"}, {\"key\": \"C\", \"text\": \"列表可变，元组不可变\"}, {\"key\": \"D\", \"text\": \"列表和元组在功能上完全相同，没有区别\"}]','[\"C\"]','列表（list）用方括号 [] 定义，元素可变（可增删改）；元组（tuple）用圆括号 () 定义，元素不可变（创建后不能修改）。因此 C 正确，A 说反了，B 括号写反了，D 明显错误。','easy',12,'2026-09-06 11:13:29',10,0,'ai','[]'),(39,'single','HTTP 默认端口是?','[{\"key\": \"A\", \"text\": \"80\"}, {\"key\": \"B\", \"text\": \"443\"}, {\"key\": \"C\", \"text\": \"22\"}, {\"key\": \"D\", \"text\": \"3389\"}]','[\"A\"]','HTTP 80 / HTTPS 443','medium',14,'2026-09-06 11:16:33',10,0,'manual','[]'),(40,'multiple','以下哪些是 HTTP 方法?','[{\"key\": \"A\", \"text\": \"GET\"}, {\"key\": \"B\", \"text\": \"POST\"}, {\"key\": \"C\", \"text\": \"SEND\"}, {\"key\": \"D\", \"text\": \"DELETE\"}]','[\"A\", \"B\", \"D\"]','SEND 不是 HTTP 方法','medium',14,'2026-09-06 11:16:33',10,0,'manual','[]'),(41,'judge','HTTPS 的默认端口是 443。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"A\"]','HTTPS 默认 443','medium',14,'2026-09-06 11:16:33',10,0,'manual','[]'),(42,'fill','中国的首都是___，简称___。','[]','[[\"北京\", \"北京市\"], [\"京\"]]','一空多答示例','medium',14,'2026-09-06 11:16:33',20,0,'manual','[]'),(43,'short','简述 HTTPS 相比 HTTP 的安全改进。','[]','[\"HTTPS 使用 TLS/SSL 加密传输，并通过证书验证服务器身份，防止窃听与篡改\"]','按踩分点给分','medium',14,'2026-09-06 11:16:33',30,0,'manual','[\"TLS/SSL 加密\", \"证书验证身份\", \"防窃听防篡改\"]'),(44,'single','以下哪个是 Python 中合法的变量名？','[{\"key\": \"A\", \"text\": \"2name\"}, {\"key\": \"B\", \"text\": \"my-var\"}, {\"key\": \"C\", \"text\": \"_count\"}, {\"key\": \"D\", \"text\": \"class\"}]','[\"C\"]','Python 变量命名规则：1. 必须以字母或下划线开头，不能以数字开头，排除A；2. 只能包含字母、数字和下划线，不能包含连字符，排除B；3. 不能使用 Python 关键字（如 class、if、for 等），排除D。C选项 _count 以下划线开头，符合命名规则，是合法变量名。','easy',14,'2026-09-06 11:16:42',10,0,'ai','[]'),(45,'single','关于 Python 中列表（list）与元组（tuple）的区别，以下说法正确的是？','[{\"key\": \"A\", \"text\": \"列表是不可变的，元组是可变的\"}, {\"key\": \"B\", \"text\": \"列表用圆括号()定义，元组用方括号[]定义\"}, {\"key\": \"C\", \"text\": \"列表是可变的，元组是不可变的\"}, {\"key\": \"D\", \"text\": \"列表和元组在功能上完全相同，没有任何区别\"}]','[\"C\"]','列表（list）用方括号[]定义，是可变的（mutable），支持增删改元素；元组（tuple）用圆括号()定义，是不可变的（immutable），创建后不能修改其内容。A选项说反了；B选项括号用反了；D选项明显错误。因此正确答案是C。','easy',14,'2026-09-06 11:16:42',10,0,'ai','[]'),(46,'short','简述 Python 中 for 循环和 while 循环的区别及各自适用的场景。','[]','[\"for 循环用于遍历可迭代对象（如列表、字符串、range 等），适用于已知迭代次数或遍历集合的场景；while 循环在条件为真时重复执行，适用于不确定迭代次数、需要满足特定条件才停止的场景。\"]','for 循环适合遍历已知序列，代码简洁；while 循环适合条件驱动的场景，如等待用户输入、处理不确定次数的任务等。','easy',8,'2026-09-06 11:17:01',10,0,'ai','[\"说明 for 循环遍历可迭代对象\", \"说明 while 循环基于条件判断\", \"说明 for 循环适用场景\", \"说明 while 循环适用场景\"]'),(47,'single','HTTP 默认端口是?','[{\"key\": \"A\", \"text\": \"80\"}, {\"key\": \"B\", \"text\": \"443\"}, {\"key\": \"C\", \"text\": \"22\"}, {\"key\": \"D\", \"text\": \"3389\"}]','[\"A\"]','HTTP 80 / HTTPS 443','medium',16,'2026-09-06 11:22:26',10,0,'manual','[]'),(48,'multiple','以下哪些是 HTTP 方法?','[{\"key\": \"A\", \"text\": \"GET\"}, {\"key\": \"B\", \"text\": \"POST\"}, {\"key\": \"C\", \"text\": \"SEND\"}, {\"key\": \"D\", \"text\": \"DELETE\"}]','[\"A\", \"B\", \"D\"]','SEND 不是 HTTP 方法','medium',16,'2026-09-06 11:22:26',10,0,'manual','[]'),(49,'judge','HTTPS 的默认端口是 443。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"A\"]','HTTPS 默认 443','medium',16,'2026-09-06 11:22:26',10,0,'manual','[]'),(50,'fill','中国的首都是___，简称___。','[]','[[\"北京\", \"北京市\"], [\"京\"]]','一空多答示例','medium',16,'2026-09-06 11:22:26',20,0,'manual','[]'),(51,'short','简述 HTTPS 相比 HTTP 的安全改进。','[]','[\"HTTPS 使用 TLS/SSL 加密传输，并通过证书验证服务器身份，防止窃听与篡改\"]','按踩分点给分','medium',16,'2026-09-06 11:22:26',30,0,'manual','[\"TLS/SSL 加密\", \"证书验证身份\", \"防窃听防篡改\"]'),(52,'single','以下哪个是合法的 Python 变量名？','[{\"key\": \"A\", \"text\": \"2var\"}, {\"key\": \"B\", \"text\": \"my-var\"}, {\"key\": \"C\", \"text\": \"_myVar\"}, {\"key\": \"D\", \"text\": \"class\"}]','[\"C\"]','Python 变量命名规则：①只能以字母或下划线开头，不能以数字开头（排除A）；②只能包含字母、数字和下划线，不能包含连字符（排除B）；③不能是 Python 关键字（排除D，class 是关键字）。因此 _myVar 是合法变量名。','easy',16,'2026-09-06 11:22:39',10,0,'ai','[]'),(53,'single','关于 Python 中列表（list）与元组（tuple）的区别，以下说法正确的是？','[{\"key\": \"A\", \"text\": \"列表是不可变的，元组是可变的\"}, {\"key\": \"B\", \"text\": \"列表用圆括号()表示，元组用方括号[]表示\"}, {\"key\": \"C\", \"text\": \"列表是可变的，元组是不可变的\"}, {\"key\": \"D\", \"text\": \"列表和元组在功能上完全相同，没有任何区别\"}]','[\"C\"]','列表（list）是可变的序列，用方括号[]表示，支持增删改操作；元组（tuple）是不可变的序列，用圆括号()表示，创建后不能修改其元素。因此选项A说反了，选项B括号用反了，选项D错误，正确答案是C。','easy',16,'2026-09-06 11:22:39',10,0,'ai','[]');
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_favorites`
--

DROP TABLE IF EXISTS `user_favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_favorites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `question_id` int NOT NULL,
  `created_at` datetime DEFAULT NULL COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_user_question_favorite` (`user_id`,`question_id`),
  KEY `ix_user_favorites_id` (`id`),
  KEY `ix_user_favorites_question_id` (`question_id`),
  KEY `ix_user_favorites_user_id` (`user_id`),
  CONSTRAINT `user_favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_favorites_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_favorites`
--

LOCK TABLES `user_favorites` WRITE;
/*!40000 ALTER TABLE `user_favorites` DISABLE KEYS */;
INSERT INTO `user_favorites` VALUES (2,8,19,'2026-09-04 10:28:17'),(3,8,16,'2026-09-04 12:06:37');
/*!40000 ALTER TABLE `user_favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL',
  `status` tinyint(1) DEFAULT NULL COMMENT '账号状态 (True=正常, False=禁用)',
  `created_at` datetime DEFAULT NULL COMMENT '注册时间',
  `nickname` varchar(50) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `position` varchar(50) DEFAULT '',
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `uix_users_phone` (`phone`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'student_e2e','$2b$12$YEch3Lls93TG0GYphZREQ.bYuigjm0yy.DBiDpHQz2XdSN28hoXPi','',1,'2026-09-03 20:32:28',NULL,NULL,'',NULL,''),(2,'student_e2estudent_e2e','$2b$12$L.8enQwIa2fRo1NoILo4RuOcHL7HwUHXYS8gqbJewpH5Do4uQmMLi','',1,'2026-09-03 20:36:43',NULL,NULL,'',NULL,''),(3,'e2e_student_v2','$2b$12$8lLzsPgDCR8sBhBG13KSx.hjvJ6LsK/9.kI1qVhsq/0zzmKeYX2nW','',1,'2026-09-03 20:47:37',NULL,NULL,'',NULL,''),(4,'student_e2estudent_e2estudent_test_888','$2b$12$Yo7FDRT5O/0fd9KjvcH00.6mjuTOld7pNCpvpeZnxtRMaDWGTohKe','',1,'2026-09-03 20:50:45',NULL,NULL,'',NULL,''),(5,'user123','$2b$12$uNSFwqpuJStA9jcscbq9UO/t4OcUNGa.H8378okGSawb8v7drEDvm','',1,'2026-09-03 20:56:06',NULL,NULL,'',NULL,''),(6,'student_h5','$2b$12$e2kHCHaCIRBY5d.0/yIpmO4f6B2r6gTMG4UwORID3I4B0shGzWNhy','',1,'2026-09-03 20:59:47',NULL,NULL,'',NULL,''),(7,'student_e2estudent_h5','$2b$12$v62AzAZUyb23BwMXt88Pheqd/bPD6PUERxiu.Zp8jKxQgqR3czIs6','',1,'2026-09-03 21:06:07',NULL,NULL,'',NULL,''),(8,'root','$2b$12$rQo.6fcYD8nMY177dccFJuvQetlfDKorD/cNUNUzojS7m8ySDKM8a','',1,'2026-09-03 22:38:01',NULL,NULL,'',NULL,''),(9,'u455800','$2b$12$01EvKfxP2ltDJtZM2sS0qODFogm0YVjIgmUKGjwkGW/PCkRQ8q.Ui','',1,'2026-09-04 01:16:41',NULL,NULL,'',NULL,''),(10,'u455806','$2b$12$izLGE946hvYgJ7DH4O0WBujJRJQ8ou8SAqV4g2SzmL8fqgXAdeq/W','',1,'2026-09-04 01:16:47',NULL,NULL,'',NULL,''),(11,'u455872','$2b$12$41xH65ja.RQ2tHs44s6d6ehbQ0z9vhXkseEK8mr7Q6gZ4hOvrxYwi','',1,'2026-09-04 01:17:53',NULL,NULL,'',NULL,''),(12,'g458501','$2b$12$27QuvgWK0RPleEn54Qf4tuYnp7DmPeMSZ4Cm2bmUZ9EMnhqaVFjM2','',1,'2026-09-04 02:01:42',NULL,NULL,'',NULL,''),(13,'b503419','$2b$12$15iQZ9o8ikKQqHy/z8IHEe4YIRHM6lfsH2CoTSeELsIYGiLdQLfhm','',1,'2026-09-04 14:30:20',NULL,NULL,'',NULL,''),(15,'e2e0906191607_1','$2b$12$l9lv65b9GPKy.jkLJZQNvudUdC7mdTBnRO7AefGYMFoT13nRt.HcC','',1,'2026-09-06 11:17:02','测试员小张','male','消防讲师','13961916070','e2e0906191607_1@test.com'),(16,'e2e0906191607_2','$2b$12$YgXMspT0st9rVtiW4o8LTOiv7ShD1/XjR2/5dWTW4Rs.F4ruiTq7W','',1,'2026-09-06 11:17:02','测试员小王','female','企业安监员','13961916071','e2e0906191607_2@test.com'),(17,'e2e0906191607_3','$2b$12$AfYdre5Y6LhkZzQYYMGLgeL37cueVdTnZIDbq9hfhIIHVWYMIGINW','',1,'2026-09-06 11:17:02','测试员小李','male','','13961916072','e2e0906191607_3@test.com'),(18,'e2e0906191607_4','$2b$12$tqxeBPb1WzWP4TriruNgIO0tF3vqM56AXjCQVd0Aiy0fxWZVnwNS2','',1,'2026-09-06 11:17:03','测试员小赵','female','在校学生','13961916073','e2e0906191607_4@test.com'),(19,'e2e0906191607_5','$2b$12$LIU.89XWoLr1gnySFo/Ft.BSrP9Jog5yaQK0Ir2bUsecJA7d9yKBq','',1,'2026-09-06 11:17:03','测试员小陈','male','IT工程师','13961916074','e2e0906191607_5@test.com'),(20,'e2e0906191607_6','$2b$12$0EfwoEPUnAhUyzh1D3UPTujzNfwsxEN6tKnfw7gQ5NM9v2RXVCVdS','',1,'2026-09-06 11:17:04','测试员小刘','female','','13961916075',''),(21,'e2e0906192200_1','$2b$12$UQLZ08U1jLYUnHWCX3R0xO.7EIvPcnlfhQsbLGEbeir6MFsURPd.i','',1,'2026-09-06 11:22:49','测试员小张','male','消防讲师','13961922000','e2e0906192200_1@test.com'),(22,'e2e0906192200_2','$2b$12$3lpmjK9xMyIZwazdX4Ze.OJIOiLfMgeENlHAQeuSoctojKw5ZWQHW','',1,'2026-09-06 11:22:49','测试员小王','female','企业安监员','13961922001','e2e0906192200_2@test.com'),(23,'e2e0906192200_3','$2b$12$Uz6i3YpJvlpyb8wV3QRe/.VbJi4FIBnR9svBN8lsU3Eqf8F/9YlvO','',1,'2026-09-06 11:22:50','测试员小李','male','','13961922002','e2e0906192200_3@test.com'),(24,'e2e0906192200_4','$2b$12$kmdufNqZJOM1nmJI3OQhUuLc1K70USFoTpEPafnYjG8cz1Kuuner6','',1,'2026-09-06 11:22:50','测试员小赵','female','在校学生','13961922003','e2e0906192200_4@test.com'),(25,'e2e0906192200_5','$2b$12$kVNMCZHX84ZOx2ogKzrtm.5h.wwX5FUQwCoXqreC.tZI7GfAXvWDa','',1,'2026-09-06 11:22:51','测试员小陈','male','IT工程师','13961922004','e2e0906192200_5@test.com'),(26,'e2e0906192200_6','$2b$12$ivYCNTr/9hyxuWsHeAU5EehPyyI6PdqgGoUGwuD4jKsXNTaFrMuKS','',1,'2026-09-06 11:22:51','测试员小刘','female','','13961922005','');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-06 19:23:50
