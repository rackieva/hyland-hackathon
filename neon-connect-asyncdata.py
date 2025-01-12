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
                CREATE TABLE IF NOT EXISTS loginTable (
                    login1 TEXT,
                    url1 TEXT,
                    userName1 TEXT,
                    password1 TEXT
                );
            """)

            await conn.execute("""
                DELETE FROM loginTable
                WHERE login1 = $1
                  AND url1 IS NOT NULL
                  AND userName1 IS NOT NULL
                  AND password1 IS NOT NULL
            """, login)

            await conn.execute("""
                INSERT INTO loginTable(login1, url1, userName1, password1)
                VALUES
                    ('spiderman',     'https://google.com', 'Peter_Parker',     'supersecretpassword'),
                    ('spiderman',     'https://amazon.com', 'Peter_Parker2',    'supersecretpassword2'),
                    ('spiderman',     'https://apple.com',  'Peter_Parker3',    'supersecretpassword3'),
                    ('spiderman',     'https://card.com',   'Peter_Parker4',    'supersecretpassword4'),
                    ('winniethePooh', 'https://google.com', 'Winnie_the_Pooh',  'supersecretpassword'),
                    ('winniethePooh', 'https://amazon.com', 'Winnie_the_Pooh2', 'super1secretpassword2'),
                    ('winniethePooh', 'https://apple.com',  'Winnie_the_Pooh3', 'super1secretpassword3'),
                    ('winniethePooh', 'https://card.com',   'Winnie_the_Pooh4', 'super1secretpassword4');
            """)

            if isClicked:
                await conn.execute("""
                    INSERT INTO loginTable(login1, url1, userName1, password1)
                    VALUES ($1, $2, $3, $4)
                """, login, url, usrname, password2)

            # 5) Fetch relevant rows for the login
            rows = await conn.fetch("""
                SELECT 
                    url1 AS "URL",
                    userName1 AS "Username",
                    password1 AS "Password"
                FROM loginTable
                WHERE login1 = $1
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