
import cx_Oracle


cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_21_10")

conn=None
connStr= 'test_code/Oracle123@10.0.223.163:1521/bcadb'
try:
    conn=cx_Oracle.connect(connStr)
    cur= conn.cursor()
    sqlTxt='insert into test_transform (\
            select name, address, website, phone_number, trunc(avg(reviews_count)), round(avg(reviews_average),1)\
            from test_insert\
            group by name, address, website, phone_number)'
    cur.execute(sqlTxt)
    conn.commit()
    print('finished transform')
except Exception as err:
    print('Error while inserting rows')
    print(err)
finally:
    if(conn):
    #close the cursor object to avoid memory leaks
        cur.close()
        #close the connection as well
        conn.close()