import psycopg

c = psycopg.connect("postgresql://postgres:postgres@localhost:5432/timetable_db")
cur = c.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = [r[0] for r in cur.fetchall()]
print(f"{len(tables)} tables:")
for t in tables:
    print(" -", t)
c.close()
