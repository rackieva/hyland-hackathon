# most code from this file is from https://neon.tech/docs/guides/python and debugged by chatgpt o1 
# should work on python version 3.7 and later
import os
import ssl
import psycopg2
from urllib.parse import urlparse
from urllib.parse import parse_qs

def connect_to_neon():
    # Hardcoded credentials (not recommended for production)
    DATABASE_URL = "postgresql://username:password@neon-hostname/database-name?sslmode=require"
    
    # Parse the connection URL
    result = urlparse(DATABASE_URL)
    query_params = parse_qs(result.query)

    # Extract components from the parsed URL
    user = result.username
    password = result.password
    host = result.hostname
    port = result.port
    dbname = result.path.lstrip('/')  # remove the leading "/"
    sslmode = query_params.get('sslmode', ['require'])[0]

    # (Optional) Create a custom SSL context if desired
    ssl_context = ssl.create_default_context()
    # Adjust as needed. If you truly do not want SSL cert validation:
    #ssl_context.check_hostname = False
    #ssl_context.verify_mode = ssl.CERT_NONE
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode=sslmode,          # psycopg2 will handle SSL if sslmode=require
            ##sslcontext=ssl_context    # only needed if you're customizing SSL behavior
        )
        print("Connected to Neon database")
        
        
        with conn.cursor() as cur:
        # Execute a query
            cur.execute("""
                 create table if not exists passwordTable(
                    login1 text,
                    password1 text);

                prepare clearTable2 (text) as
                    delete from passwordTable 
                    where login1 =$1 
                      and password1 is not null;

                execute clearTable2(%s);

                insert into passwordTable (login1, password1) values 
                    ('spiderman','peterparkerPassword')
                    ('winniethePooh','winnieIStheBest');

                case
                    when
                        -- user inputs 2 values 
                            then
                                insert into passwordTable (login1, password1)
                                values (%s,%s)
                                 
                else
                    end;
                
                prepare newTable2 (text) as
                    select * from passwordTable
                        where login1 = $1
                        and password1 is not null;
                execute newTable2(%s);
                 """, (login, login, password2, login))

            # connect to html some how
            results = cur.fetchall()
            for row in results:
                print(row)

    except psycopg2.Error as e:
        print("Error connecting to database:", e)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    connect_to_neon()