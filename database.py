import psycopg2
import psycopg2.extras
import credentials
import json

# Connect to default/local postgres, no credentials required
conn = psycopg2.connect('dbname=postgres', cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()

cur.execute(""" 
            CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY,
            username VARCHAR UNIQUE,
            password VARCHAR UNIQUE,
            info JSON NOT NULL ) 
            """)
conn.commit()          



def find_by_username(username):
    query = 'SELECT * FROM users WHERE username = (%s)'
    cur.execute(query, [ username ])
    return cur.fetchone()

def create_new_user(userData):
    username = userData['username']
    password = credentials.generatePassword(userData['password'])
    info = userData['info']

    query = """ INSERT INTO users
            (username, password, info)
            VALUES (%s, %s, %s) 
            ON CONFLICT DO NOTHING """
    data = (username, password, json.dumps(info))
   
    existingUser = find_by_username(username)

    if existingUser:
        return None
    else:
        cur.execute(query, data)
        conn.commit()
        newUser = find_by_username(username)

        return newUser

def update_user(username, userData):
    # as specified in description, only updating json data for user
    infoData = json.dumps(userData)
    query = """ UPDATE users
            SET info = (%s)
            WHERE username = (%s)
            """
    data = (infoData, username)
    
    cur.execute(query, data)
    conn.commit()
    newUser = find_by_username(username)

    return newUser

def delete_user(username):
    query = """ DELETE FROM users
            WHERE username = (%s)
            """
    data = (username, )

    cur.execute(query, data) 
    conn.commit()
    return

