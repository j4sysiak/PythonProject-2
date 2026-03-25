import sqlite3

p = r'C:\dev\python-projects\PycharmProjects\PythonProject-2\test_minibank.db'
con = sqlite3.connect(p)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
print('TABLES:', [r[0] for r in cur.fetchall()])
cur.close()
con.close()




p = r'C:\dev\python-projects\PycharmProjects\PythonProject-2\test_minibank.db'
con = sqlite3.connect(p)
cur = con.cursor()
try:
    cur.execute("SELECT id, owner_name, balance, currency, version FROM accounts LIMIT 5;")
    print('ACCOUNTS sample:', cur.fetchall())
except Exception as e:
    print('ACCOUNTS query error:', e)
cur.close()
con.close()
