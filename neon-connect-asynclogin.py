# code is from https://neon.tech/docs/guides/python and debugged by chatgpt o1 
# should work on python version 3.7 and later
#postgreSQL implementation by me (eva rackaityte)
import asyncio
import asyncpg
import ssl
from urllib.parse import urlparse, parse_qs

async def connect_to_neon(login, url, usrname, password2, isClicked):

    # Hardcoded credentials (not recommended for production)
    # Example: postgresql://username:password@neon-hostname/database-name?sslmode=require
    DATABASE_URL = "postgresql://username:password@neon-hostname/database-name?sslmode=require"

    # (Optional) Parse components from your DATABASE_URL, if you want to inspect:
    result = urlparse(DATABASE_URL)
    query_params = parse_qs(result.query)

    # Usually not strictly necessary, but you can do:
    user = result.username
    password = result.password
    host = result.hostname
    port = result.port
    dbname = result.path.lstrip('/')
    sslmode = query_params.get('sslmode', ['require'])[0]

    # (Optional) Create a custom SSL context if you want to control SSL behavior
    # ssl_context = ssl.create_default_context()
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_NONE

    pool = await asyncpg.create_pool(
        DATABASE_URL,
        # ssl=ssl_context,  # uncomment if you want to pass a custom SSL context
    )

    object_array = []
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                create table if not exists passwordTable(
                    login1 text,
                    password1 text);
            """)

            await conn.execute("""
                delete from passwordTable 
                    where login1 =$1 
                      and password1 is not null;
            """, login)

            await conn.execute("""
                insert into passwordTable (login1, password1) values 
                    ('spiderman','peterparkerPassword')
                    ('winniethePooh','winnieIStheBest');
            """)

            if isClicked:
                await conn.execute("""
                    insert into passwordTable(login1, password1)
                    values ($1, $2)
                """, login, password2)

            # 5) Fetch relevant rows for the login
            rows = await conn.fetch("""
                SELECT 
                    login1,
                    password1
                FROM passwordTable
                WHERE login1 = $1
                  and password1 is not null;
            """, login)

            # 6) Convert rows into a list of dictionaries
            object_array = [dict(r) for r in rows]

    except Exception as e:
        print("Error connecting or executing queries:", e)
    finally:
        # Always close your pool
        await pool.close()

    # Return the data
    return object_array