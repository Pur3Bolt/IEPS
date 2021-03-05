import psycopg2

username = 'ieps'
password = 'ieps123ieps!'
host = '167.86.79.68'
port = '5432'
dbname = 'ieps'
schema = 'crawldb'


def get_connection():
    return psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (dbname, username, host, password))


def get_cursor(conn):
    return conn.cursor()


def commit(cur):
    cur.execute("COMMIT;")


def insert_into_site(cur, values, commit=True):
    if cur.closed:
        cur = get_cursor(cur.connection)
    cur.execute("INSERT INTO %s.site(domain, robots_content, sitemap_content) VALUES %s;"
                % (schema, str(tuple(values))))
    if commit:
        cur.execute("COMMIT;")


def read_from_site(cur, f_all=True):
    if cur.closed:
        cur = get_cursor(cur.connection)
    cur.execute("SELECT * FROM %s.site;" % schema)
    if f_all:
        return cur.fetchall()
    else:
        return cur.fetchone()[0]


# 1. get connection
connection = get_connection()

# 2. get cursor
kursor = get_cursor(connection)

# 3. naredi neki z kurzorjem
insert_into_site(kursor, ['aljaz', 'je', 'legenda'])

# 4. spet pejdi po kurzor
kursor = get_cursor(connection)

# 5. preberi iz baze
data = read_from_site(kursor)
print("data: ", data)
