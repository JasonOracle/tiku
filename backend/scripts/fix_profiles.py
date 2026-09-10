# -*- coding: utf-8 -*-
"""
一次性脚本：修正星雅教育与皓石集团全部成员的画像数据。
执行方式：python backend/scripts/fix_profiles.py
"""
import pymysql

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "rootpassword",
    "database": "tiku_db",
    "charset": "utf8mb4",
}

# 格式: (user_id, display_name, gender, age, occupation, nickname, bio)
PROFILES = [
    # ── 星雅教育 (Tenant 1) ──
    (2,  "陈星雅", "male",   38, "教务主任",     "陈星雅", "星雅教育创始人兼教务主任，拥有15年K12教育管理经验，主导课程体系研发与教学质量监控"),
    (4,  "赵艳",   "female", 36, "高中语文教师", "赵艳",   "从事高中语文教学12年，市级优秀教师，擅长古诗词鉴赏与高考作文指导"),
    (6,  "孙杰",   "female", 29, "初中数学教师", "孙杰",   "数学教育学硕士，专注初中数学竞赛辅导，曾带学生获省级竞赛一等奖"),
    (8,  "刘艳",   "female", 42, "高中英语教师", "刘艳",   "英语专业八级，18年教龄，负责高三英语备课组，擅长听力与阅读理解专项突破"),
    (10, "李艳",   "female", 31, "初中物理教师", "李艳",   "物理学硕士，6年教龄，擅长实验教学与趣味科普，深受学生喜爱"),
    (13, "赵芳",   "female", 27, "小学数学教师", "赵芳",   "师范大学应届优秀毕业生，教学风格活泼生动，负责三四年级数学教学与课后辅导"),
    # ── 皓石集团 (Tenant 2) ──
    (3,  "林敏",   "female", 35, "人力资源总监",   "林敏",   "皓石集团HR负责人，统筹全集团员工培训体系、考核评价与合规教育，8年人力资源管理经验"),
    (5,  "陈伟",   "male",   28, "软件研发工程师", "陈伟",   "后端开发方向，3年Java微服务架构经验，目前参与集团数字化转型核心项目"),
    (7,  "李敏",   "male",   45, "财务经理",       "李敏",   "注册会计师（CPA），20年企业财务管理经验，负责集团财务审计与合规风控"),
    (9,  "王磊",   "male",   33, "市场营销经理",   "王磊",   "负责集团品牌推广与市场策略制定，擅长数字营销与渠道管理，曾主导多个百万级营销项目"),
    (11, "吴涛",   "male",   26, "产品运营专员",   "吴涛",   "互联网产品运营方向，负责集团内部培训平台的日常运营、数据分析与用户增长"),
    (12, "周芳",   "female", 30, "行政管理专员",   "周芳",   "负责集团行政事务与员工活动组织，持有人力资源管理师证书，细致高效"),
]


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for uid, name, gender, age, occupation, nickname, bio in PROFILES:
        # 更新 sys_user.display_name
        cursor.execute(
            "UPDATE sys_user SET display_name=%s WHERE id=%s",
            (name, uid)
        )
        # 更新 sys_user_profile 画像
        cursor.execute(
            "UPDATE sys_user_profile SET gender=%s, age=%s, occupation=%s, nickname=%s, bio=%s WHERE user_id=%s",
            (gender, age, occupation, nickname, bio, uid)
        )
        affected = cursor.rowcount
        # 如果 profile 行不存在则插入
        if affected == 0:
            cursor.execute(
                "INSERT INTO sys_user_profile (user_id, gender, age, occupation, nickname, bio) VALUES (%s,%s,%s,%s,%s,%s)",
                (uid, gender, age, occupation, nickname, bio)
            )
        print(f"  ✅ [{uid}] {name} ({occupation}, {gender}, {age}岁)")

    conn.commit()
    print(f"\n🎉 共更新 {len(PROFILES)} 条成员画像")

    # 验证：回查全表
    print("\n── 验证回查 ──")
    cursor.execute(
        "SELECT u.id, u.display_name, tu.tenant_id, t.name, tu.role, "
        "p.gender, p.age, p.occupation, p.bio "
        "FROM sys_user u "
        "JOIN sys_tenant_user tu ON u.id=tu.user_id "
        "JOIN sys_tenant t ON t.id=tu.tenant_id "
        "LEFT JOIN sys_user_profile p ON p.user_id=u.id "
        "WHERE tu.tenant_id IN (1,2) ORDER BY tu.tenant_id, u.id"
    )
    for row in cursor.fetchall():
        uid, dname, tid, tname, role, g, a, o, bio = row
        print(f"  [{tid}:{tname}] {dname}({role}) | {g}/{a}岁/{o} | {bio[:30]}...")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
