# most of this code from this file is from https://neon.tech/docs/guides/python 
# all code debugged by chatgpt o1 
# should work on python version 3.7 and later

#code from neon{

import os
import ssl
import psycopg2
from urllib.parse import urlparse, parse_qs

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
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_NONE
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode=sslmode,          # psycopg2 will handle SSL if sslmode=require
            sslcontext=ssl_context    # only needed if you're customizing SSL behavior
        )
        print("Connected to Neon database")
        
#code from neon }
        
        # Example query
        with conn.cursor() as cur:
            cur.execute("SELECT NOW(), version()")
            record = cur.fetchone()
            print("Current time:", record[0])
            print("PostgreSQL version:", record[1])
            
#code from neon {
    
    except psycopg2.Error as e:
        print("Error connecting to database:", e)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    connect_to_neon()
   
#code from neon }
