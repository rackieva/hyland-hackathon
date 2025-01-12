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
                create table if not exists loginTable (
                    login1 text,
                    url1 text,
                    userName1 text,
                    password1 text);
                
                prepare clearTable1 (text) as
                    delete from loginTable 
                    where login1 =$1 
                      and url1 is not null 
                      and userName1 is not null 
                      and password1 is not null;

                execute clearTable1(%s);

                insert into loginTable(login1, url1, userName1, password1)
                        values
                            ('spiderman', 'https://google.com', 'Peter_Parker', 'supersecretpassword'),
                            ('spiderman', 'https://amazon.com', 'Peter_Parker2', 'supersecretpassword2'),
                            ('spiderman', 'https://apple.com', 'Peter_Parker3', 'supersecretpassword3'),
                            ('spiderman', 'https://card.com', 'Peter_Parker4', 'supersecretpassword4'),
                            ('winniethePooh', 'https://google.com', 'Winnie_the_Pooh', 'supersecretpassword'),
                            ('winniethePooh', 'https://amazon.com', 'Winnie_the_Pooh2', 'super1secretpassword2'),
                            ('winniethePooh', 'https://apple.com', 'Winnie_the_Pooh3', 'super1secretpassword3'),
                            ('winniethePooh', 'https://card.com', 'Winnie_the_Pooh4', 'super1secretpassword4');   
                        
                prepare newTable1 (text) as
                    select url1 as "URL", userName1 as "Username", password1 as "Password" from loginTable
                        where login1 = $1;

                execute newTable1(%s);
                 """, (login, login))
                
            if isClicked:
                    cur.execute("""
                        INSERT INTO loginTable(login1, url1, userName1, password1)
                        VALUES (%s, %s, %s, %s)
                    """, (login, url, usrname, password2))

            # connect to html some how
            results = cur.fetchall()
            object_array = [
                dict(zip([col[0] for col in cur.description], row))
                    for row in results
                ]

    except psycopg2.Error as e:
        print("Error connecting to database:", e)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    connect_to_neon()