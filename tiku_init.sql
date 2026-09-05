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
INSERT INTO `admins` VALUES (2,'admin','$2b$12$ssCpU0hIUIe3SAuPoqB3P.NRbq5AtRyI6G0GHikqs1f1dybhVpYaa','super_admin','2026-09-03 22:51:46'),(3,'admreg','$2b$12$W2MjuHoyKKk4xZZGzAByC.zjQoLk2By87mGUgc5slxne3wh.2DJfm','super_admin','2026-09-04 01:16:33');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_categories`
--

LOCK TABLES `exam_categories` WRITE;
/*!40000 ALTER TABLE `exam_categories` DISABLE KEYS */;
INSERT INTO `exam_categories` VALUES (2,'金融类','folder',2,'2026-09-04 10:08:46','question'),(3,'自考类','folder',3,'2026-09-04 10:08:52','question'),(4,'工程类','folder',1,'2026-09-04 10:08:57','question'),(5,'心理测试','folder',1,'2026-09-04 10:09:05','exam'),(6,'趣味问答','folder',1,'2026-09-04 10:09:10','exam'),(7,'专业试题','folder',1,'2026-09-04 10:09:17','exam'),(8,'消防安全','folder',0,'2026-09-04 10:09:29','question'),(9,'文学类','folder',4,'2026-09-04 12:10:25','question');
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_questions`
--

LOCK TABLES `exam_questions` WRITE;
/*!40000 ALTER TABLE `exam_questions` DISABLE KEYS */;
INSERT INTO `exam_questions` VALUES (1,1,19,5,1),(2,1,18,5,2),(3,1,17,20,3),(4,1,16,15,4);
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
  PRIMARY KEY (`id`),
  KEY `ix_exam_records_exam_id` (`exam_id`),
  KEY `ix_exam_records_user_id` (`user_id`),
  KEY `ix_exam_records_id` (`id`),
  CONSTRAINT `exam_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `exam_records_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_records`
--

LOCK TABLES `exam_records` WRITE;
/*!40000 ALTER TABLE `exam_records` DISABLE KEYS */;
INSERT INTO `exam_records` VALUES (1,8,1,'timeout',0,0,0,'2026-09-04 10:11:04','2026-09-04 12:06:20',NULL),(2,8,1,'timeout',0,0,0,'2026-09-04 10:11:24','2026-09-04 12:06:20',NULL),(3,8,1,'timeout',0,0,0,'2026-09-04 10:11:42','2026-09-04 12:06:20',NULL),(4,8,1,'timeout',0,0,0,'2026-09-04 10:15:43','2026-09-04 12:06:20',NULL),(5,8,1,'submitted',5,0,28807,'2026-09-04 10:25:38','2026-09-04 10:25:45','{\"16\": [\"B\"], \"17\": [\"A\"], \"18\": [\"B\"], \"19\": [\"A\"]}'),(6,8,1,'timeout',0,0,0,'2026-09-04 10:26:32','2026-09-04 12:06:20',NULL),(7,8,1,'timeout',0,0,0,'2026-09-04 10:26:47','2026-09-04 12:06:20',NULL),(8,8,1,'timeout',0,0,0,'2026-09-04 10:28:12','2026-09-04 12:06:20',NULL),(9,8,1,'timeout',0,0,0,'2026-09-04 12:06:20','2026-09-04 12:42:33',NULL),(10,8,1,'submitted',5,0,28811,'2026-09-04 12:06:31','2026-09-04 12:06:42','{\"16\": [], \"17\": [\"B\"], \"18\": [\"A\"], \"19\": [\"B\"]}'),(11,8,1,'timeout',0,0,0,'2026-09-04 12:12:50','2026-09-04 14:45:43',NULL),(12,8,1,'timeout',0,0,0,'2026-09-04 12:12:58','2026-09-04 14:45:43',NULL),(13,8,1,'timeout',0,0,0,'2026-09-04 12:14:40','2026-09-04 14:45:43',NULL),(14,8,1,'timeout',0,0,0,'2026-09-04 12:42:33','2026-09-04 14:45:43',NULL),(15,8,1,'timeout',0,0,0,'2026-09-04 12:42:37','2026-09-04 14:45:43',NULL),(16,8,1,'timeout',0,0,0,'2026-09-04 12:42:41','2026-09-04 14:45:43',NULL),(17,8,1,'submitted',5,0,28816,'2026-09-04 14:45:43','2026-09-04 14:46:00','{\"16\": [\"C\"], \"17\": [\"A\"], \"18\": [\"B\"], \"19\": [\"A\"]}');
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
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_exams_id` (`id`),
  CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `exam_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exams`
--

LOCK TABLES `exams` WRITE;
/*!40000 ALTER TABLE `exams` DISABLE KEYS */;
INSERT INTO `exams` VALUES (1,'心理健康测评',5,'preset:1',1,30,45,27,0,'2026-09-04 10:10:51',60,'published','心理测试',0);
/*!40000 ALTER TABLE `exams` ENABLE KEYS */;
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
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_questions_id` (`id`),
  CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `exam_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (11,'single','以下哪种灭火器适合扑灭电气火灾？','[{\"key\": \"A\", \"text\": \"泡沫灭火器\"}, {\"key\": \"B\", \"text\": \"水基型灭火器\"}, {\"key\": \"C\", \"text\": \"二氧化碳灭火器\"}, {\"key\": \"D\", \"text\": \"干粉灭火器\"}]','[\"C\"]','电气火灾不能用水或泡沫，应使用二氧化碳或干粉灭火器','easy',4,'2026-09-04 10:09:29',10),(12,'single','下列哪项不属于消防四个能力建设内容？','[{\"key\": \"A\", \"text\": \"检查消除火灾隐患的能力\"}, {\"key\": \"B\", \"text\": \"扑救初期火灾的能力\"}, {\"key\": \"C\", \"text\": \"组织引导人员疏散逃生的能力\"}, {\"key\": \"D\", \"text\": \"独立扑救大型火灾的能力\"}]','[\"D\"]','四个能力不含独立扑救大型火灾','medium',4,'2026-09-04 10:09:29',10),(13,'single','发现火灾时，第一步应该做什么？','[{\"key\": \"A\", \"text\": \"立即自行扑火\"}, {\"key\": \"B\", \"text\": \"大声呼救\"}, {\"key\": \"C\", \"text\": \"拨打119报警\"}, {\"key\": \"D\", \"text\": \"先转移财物\"}]','[\"C\"]','发现火灾应第一时间拨打119报警','easy',3,'2026-09-04 10:09:29',10),(14,'single','安全出口标志灯的颜色是？','[{\"key\": \"A\", \"text\": \"红色\"}, {\"key\": \"B\", \"text\": \"黄色\"}, {\"key\": \"C\", \"text\": \"绿色\"}, {\"key\": \"D\", \"text\": \"蓝色\"}]','[\"C\"]','安全出口标志灯为绿色，便于在浓烟中识别','easy',4,'2026-09-04 10:09:29',10),(15,'multiple','以下哪些属于常见的火灾逃生自救方法（多选）？','[{\"key\": \"A\", \"text\": \"低姿态匍匐前进\"}, {\"key\": \"B\", \"text\": \"用湿毛巾捂住口鼻\"}, {\"key\": \"C\", \"text\": \"乘坐电梯逃跑\"}, {\"key\": \"D\", \"text\": \"向有光亮处爬行\"}]','[\"A\", \"B\", \"D\"]','乘坐电梯逃跑是错误的，火灾时电梯可能断电或成为烟道','medium',3,'2026-09-04 10:09:29',15),(16,'multiple','以下哪些行为可能引发火灾（多选）？','[{\"key\": \"A\", \"text\": \"在床上吸烟\"}, {\"key\": \"B\", \"text\": \"电线私拉乱接\"}, {\"key\": \"C\", \"text\": \"规范使用燃气\"}, {\"key\": \"D\", \"text\": \"长期不清理油烟机\"}]','[\"A\", \"B\", \"D\"]','在床上吸烟、私拉电线、不清理油烟机均是常见火灾隐患','easy',3,'2026-09-04 10:09:29',15),(17,'multiple','灭火的基本原理包括哪几种（多选）？','[{\"key\": \"A\", \"text\": \"冷却法降低燃烧温度\"}, {\"key\": \"B\", \"text\": \"窒息法隔绝氧气\"}, {\"key\": \"C\", \"text\": \"隔离法移除可燃物\"}, {\"key\": \"D\", \"text\": \"转移法转移财产\"}]','[\"A\", \"B\", \"C\"]','灭火三要素为冷却、窒息、隔离，转移财产不属于灭火原理','hard',2,'2026-09-04 10:09:29',20),(18,'judge','家用电器着火时，应立即用水扑灭。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"B\"]','家用电器着火应先断电，再用干粉或二氧化碳灭火器扑救，不能直接用水','easy',3,'2026-09-04 10:09:29',5),(19,'judge','在高层建筑发生火灾时，人员应向上疏散到楼顶等待救援。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"B\"]','高层火灾应向下疏散至安全出口，若下方被堵才可至楼顶等待救援','medium',3,'2026-09-04 10:09:29',5),(20,'judge','干粉灭火器在有效期内可用于扑灭固体液体气体及电气火灾。','[{\"key\": \"A\", \"text\": \"正确\"}, {\"key\": \"B\", \"text\": \"错误\"}]','[\"A\"]','干粉灭火器适用范围广，可扑灭A类B类C类及电气火灾','medium',8,'2026-09-04 10:09:29',4);
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'student_e2e','$2b$12$YEch3Lls93TG0GYphZREQ.bYuigjm0yy.DBiDpHQz2XdSN28hoXPi','',1,'2026-09-03 20:32:28'),(2,'student_e2estudent_e2e','$2b$12$L.8enQwIa2fRo1NoILo4RuOcHL7HwUHXYS8gqbJewpH5Do4uQmMLi','',1,'2026-09-03 20:36:43'),(3,'e2e_student_v2','$2b$12$8lLzsPgDCR8sBhBG13KSx.hjvJ6LsK/9.kI1qVhsq/0zzmKeYX2nW','',1,'2026-09-03 20:47:37'),(4,'student_e2estudent_e2estudent_test_888','$2b$12$Yo7FDRT5O/0fd9KjvcH00.6mjuTOld7pNCpvpeZnxtRMaDWGTohKe','',1,'2026-09-03 20:50:45'),(5,'user123','$2b$12$uNSFwqpuJStA9jcscbq9UO/t4OcUNGa.H8378okGSawb8v7drEDvm','',1,'2026-09-03 20:56:06'),(6,'student_h5','$2b$12$e2kHCHaCIRBY5d.0/yIpmO4f6B2r6gTMG4UwORID3I4B0shGzWNhy','',1,'2026-09-03 20:59:47'),(7,'student_e2estudent_h5','$2b$12$v62AzAZUyb23BwMXt88Pheqd/bPD6PUERxiu.Zp8jKxQgqR3czIs6','',1,'2026-09-03 21:06:07'),(8,'root','$2b$12$rQo.6fcYD8nMY177dccFJuvQetlfDKorD/cNUNUzojS7m8ySDKM8a','',1,'2026-09-03 22:38:01'),(9,'u455800','$2b$12$01EvKfxP2ltDJtZM2sS0qODFogm0YVjIgmUKGjwkGW/PCkRQ8q.Ui','',1,'2026-09-04 01:16:41'),(10,'u455806','$2b$12$izLGE946hvYgJ7DH4O0WBujJRJQ8ou8SAqV4g2SzmL8fqgXAdeq/W','',1,'2026-09-04 01:16:47'),(11,'u455872','$2b$12$41xH65ja.RQ2tHs44s6d6ehbQ0z9vhXkseEK8mr7Q6gZ4hOvrxYwi','',1,'2026-09-04 01:17:53'),(12,'g458501','$2b$12$27QuvgWK0RPleEn54Qf4tuYnp7DmPeMSZ4Cm2bmUZ9EMnhqaVFjM2','',1,'2026-09-04 02:01:42'),(13,'b503419','$2b$12$15iQZ9o8ikKQqHy/z8IHEe4YIRHM6lfsH2CoTSeELsIYGiLdQLfhm','',1,'2026-09-04 14:30:20');
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

-- Dump completed on 2026-09-05 15:42:27
