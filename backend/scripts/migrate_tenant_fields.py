"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[为 sys_tenant 表新增 6 个展示字段（短名/行业/规模/联系人/电话/备注），幂等可重跑]
"""
import pymysql

HOST = "127.0.0.1"
PORT = 3306
USER = "root"
PASSWORD = "rootpassword"
DB = "tiku_db"

COLUMNS = [
    ("short_name", "VARCHAR(50)"),
    ("industry", "VARCHAR(50)"),
    ("scale", "VARCHAR(20)"),
    ("contact_name", "VARCHAR(50)"),
    ("contact_phone", "VARCHAR(20)"),
    ("remark", "VARCHAR(255)"),
]


def column_exists(cur, table: str, col: str) -> bool:
    cur.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",
        (DB, table, col),
    )
    return cur.fetchone() is not None


def main():
    conn = pymysql.connect(host=HOST, port=PORT, user=USER,
                           password=PASSWORD, database=DB, charset="utf8mb4")
    cur = conn.cursor()
    added = 0
    for col, typ in COLUMNS:
        if not column_exists(cur, "sys_tenant", col):
            cur.execute(f"ALTER TABLE sys_tenant ADD COLUMN `{col}` {typ} NULL COMMENT '{col}'")
            added += 1
            print(f"  + added column {col} ({typ})")
        else:
            print(f"  ~ column {col} already exists")
    conn.commit()
    cur.execute("SELECT id, name, short_name, industry, scale, contact_name FROM sys_tenant LIMIT 10")
    rows = cur.fetchall()
    print(f"\nsys_tenant 前 {len(rows)} 行预览：")
    for r in rows:
        print(f"  id={r[0]} name={r[1]} short_name={r[2]} industry={r[3]} scale={r[4]} contact={r[5]}")
    print(f"\n迁移完成，新增 {added} 列")
    conn.close()


if __name__ == "__main__":
    main()
