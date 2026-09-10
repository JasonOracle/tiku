# -*- coding: utf-8 -*-
"""修复被双重编码污染的租户名（经 pymysql utf8mb4 直写，绕开 docker exec TTY）。"""
import pymysql

con = pymysql.connect(host="127.0.0.1", port=3306, user="root",
                      password="rootpassword", database="tiku_db", charset="utf8mb4")
cur = con.cursor()
cur.execute("UPDATE sys_tenant SET name='星雅教育' WHERE id=1")
cur.execute("UPDATE sys_tenant SET name='皓石集团' WHERE id=2")
con.commit()
cur.execute("SELECT id,HEX(name),CHAR_LENGTH(name),name FROM sys_tenant")
ok = True
for i, h, ln, name in cur.fetchall():
    good = (ln == 4)
    ok = ok and good
    print(i, h, ln, "OK" if good else "BAD")
con.close()
print("NAMES-FIXED" if ok else "STILL-BAD")
