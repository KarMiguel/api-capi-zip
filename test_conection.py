#!/usr/bin/python
import psycopg2


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host='127.0.0.1',database ='main',user='admin',password='adminpass',connect_timeout = 10)
        # create a cursor
        print('antes conect')
        cur = conn.cursor()
        print('depois conet')
    # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        print('Deu certoooo')
    # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()