# # import psycopg2
# # from psycopg2.extras import RealDictCursor

# # # Use the EXTERNAL Render PostgreSQL URL
# # DATABASE_URL = "postgresql://skyzone_cms_user:kQs88iKfmKtprgnocTkokbmiLWms0SSN@dpg-d4ines0dl3ps73dbrpjg-a.oregon-postgres.render.com:5432/purple_desk_db"

# # try:
# #     conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
# #     cursor = conn.cursor()
# #     print("✅ Connected to the database successfully!")
# # except Exception as e:
# #     print("❌ Failed to connect to database:")
# #     print(e)
# #     exit()

# # try:
# #     cursor.execute("SELECT * FROM myapp_user;")  # Replace if table name differs
# #     rows = cursor.fetchall()
    
# #     if rows:
# #         print(f"\nTotal rows: {len(rows)}\n")
# #         for row in rows:
# #             print(row)
# #     else:
# #         print("No data found in the table.")

# # except Exception as e:
# #     print("❌ Failed to query table:")
# #     print(e)

# # finally:
# #     cursor.close()
# #     conn.close()
# #     print("\nConnection closed.")





# import psycopg2

# # External Render PostgreSQL URL
# DATABASE_URL = "postgresql://skyzone_cms_user:kQs88iKfmKtprgnocTkokbmiLWms0SSN@dpg-d4ines0dl3ps73dbrpjg-a.oregon-postgres.render.com:5432/skyzone_cms"

# try:
#     # Connect to the default 'postgres' database to list all databases
#     conn = psycopg2.connect(
#         host="dpg-d4ines0dl3ps73dbrpjg-a.oregon-postgres.render.com",
#         dbname="postgres",  # Connect to default DB
#         user="skyzone_cms_user",
#         password="kQs88iKfmKtprgnocTkokbmiLWms0SSN",
#         port=5432
#     )
#     cursor = conn.cursor()
#     print("✅ Connected successfully!")

#     # Query to list all databases
#     cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
#     databases = cursor.fetchall()

#     print("\nDatabases on server:")
#     for db in databases:
#         print(f"- {db[0]}")

# except Exception as e:
#     print("❌ Failed to connect or query:")
#     print(e)

# finally:
#     if cursor: cursor.close()
#     if conn: conn.close()
#     print("\nConnection closed.")



import psycopg2

# Connection details for your Render PostgreSQL
HOST = "dpg-d4ines0dl3ps73dbrpjg-a.oregon-postgres.render.com"
PORT = 5432
DBNAME = "postgres"
USER = "skyzone_cms_user"
PASSWORD = "kQs88iKfmKtprgnocTkokbmiLWms0SSN"

try:
    # Connect to the 'skyzone_cms' database
    conn = psycopg2.connect(
        host=HOST,
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    cursor = conn.cursor()
    print("✅ Connected successfully!\n")

    # Query to list all tables in the 'public' schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE';
    """)
    tables = cursor.fetchall()

    if tables:
        print("Tables in database 'skyzone_cms':")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("No tables found in 'skyzone_cms'.")

except Exception as e:
    print("❌ Failed to connect or query:")
    print(e)

finally:
    if cursor: cursor.close()
    if conn: conn.close()
    print("\nConnection closed.")
