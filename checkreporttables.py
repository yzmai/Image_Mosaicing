import threading
import time
import os
import math
import pandas as pd
import sys
import logging
import platform
from imp import reload
import ibm_db

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# create table T_SINGLE_CHECKINFO(SGLCHECKID VARCHAR(18),NAME VARCHAR(10),SEX INTEGER,AGE              INTEGER ,MOBILEPHONE VARCHAR(11),IDCARD VARCHAR(18),REGISTDATE DATE);
# create table T_SINGLE_CHECKRESULT(DIAGNOSEID INTEGER, SGLCHECKID VARCHAR(18) ,REGISTDATE DATE, CHECKUNITNAME VARCHAR(20),DIAGRESULT VARCHAR(500));
# insert into T_SINGLE_CHECKINFO (SGLCHECKID, NAME, SEX, AGE, MOBILEPHONE, IDCARD, REGISTDATE ) values ('000101017021303691', '冯XX', 1,53, '1391042XXXX', '23060219640315XXXX', '11-22-2017 23:58:03')

personDf=pd.read_csv(r'D:\Ciji\R\Analysis\Enterprice/Person_20181204_sample.csv', dtype = {'SGLCHECKID' : str, 'MOBILEPHONE' : str, 'IDCARD' : str})
resultDf=pd.read_csv(r'D:\Ciji\R\Analysis\Enterprice/Diagnose_20181204_sample.csv', dtype = {'DIAGNOSEID' : str, 'SGLCHECKID' : str})




for rowId in range(len(personDf)):
    personDf['REGISTDATE'].iloc[rowId] = personDf['REGISTDATE'].iloc[rowId].replace("/", '-')
    eachline = "insert into T_SINGLE_CHECKINFO (SGLCHECKID, NAME, SEX, AGE, MOBILEPHONE, IDCARD, REGISTDATE ) values ('" + personDf['SGLCHECKID'].iloc[rowId] + "', '" + personDf['NAME'].iloc[rowId] + "', " \
               + str(personDf['SEX'].iloc[rowId]) + "," + str(personDf['AGE'].iloc[rowId])  + ", '" + personDf['MOBILEPHONE'].iloc[rowId] + "', '" + personDf['IDCARD'].iloc[rowId] \
                 + "', '" + personDf['REGISTDATE'].iloc[rowId] + "')"

for rowId in range(len(resultDf)):
    eachline = "insert into T_SINGLE_CHECKRESULT (DIAGNOSEID, SGLCHECKID, REGISTDATE, CHECKUNITNAME, DIAGRESULT ) values (" + resultDf['DIAGNOSEID'].iloc[rowId] + ", '" + resultDf['SGLCHECKID'].iloc[rowId] + "', '" + personDf['REGISTDATE'].iloc[rowId] + "', '" \
               + resultDf['CHECKUNITNAME'].iloc[rowId] + "', '" + resultDf['DIAGRESULT'].iloc[rowId] + "')"

import ibm_db
#For connecting to local database named pydev for user db2inst1 and password secret, use below example
#ibm_db_conn = ibm_db.connect('pydev', 'db2inst1', 'secret')
#For connecting to remote database named pydev for uid db2inst and pwd secret on host host.test.com, use below example
# Connect using ibm_db
# conn_str='database=pydev;hostname=host.test.com;port=portno;protocol=tcpip;uid=db2inst1;pwd=secret'
# conn_str='database=BLUDB;hostname=worker04.bone.lan.ynby.com;port=30068;protocol=tcpip;uid=user1006;pwd=bp#G#B7?7atQ7Y9*'
conn_str='database=BLUDB;hostname=192.168.168.6;port=30068;protocol=tcpip;uid=user1006;pwd=bp#G#B7?7atQ7Y9*'
ibm_db_conn = ibm_db.connect(conn_str,'','')

# Connect using ibm_db_dbi
import ibm_db_dbi
conn = ibm_db_dbi.Connection(ibm_db_conn)
# Execute tables API
conn.tables('DB2ADMIN', '%')
[{'TABLE_CAT': None, 'TABLE_SCHEM': 'DB2ADMIN', 'TABLE_NAME': 'MYTABLE', 'TABLE_TYPE': 'TABLE', 'REMARKS': None}]
# create table using ibm_db
create="create table mytable(id int, name varchar(50))"
ibm_db.exec_immediate(ibm_db_conn, create)
# Insert 3 rows into the table
insert = "insert into mytable values(?,?)"
params=((1,'Sanders'),(2,'Pernal'),(3,'OBrien'))
stmt_insert = ibm_db.prepare(ibm_db_conn, insert)
ibm_db.execute_many(stmt_insert,params)
# Fetch data using ibm_db_dbi
select="select id, name from mytable"
cur = conn.cursor()
cur.execute(select)
row=cur.fetchall()
print("{} \t {} \t {}".format(row[0],row[1],row[2]),end="\n")
row=cur.fetchall()
print(row)
# Fetch data using ibm_db
stmt_select = ibm_db.exec_immediate(ibm_db_conn, select)
cols = ibm_db.fetch_tuple( stmt_select )
print("%s, %s" % (cols[0], cols[1]))
cols = ibm_db.fetch_tuple( stmt_select )
print("%s, %s" % (cols[0], cols[1]))
cols = ibm_db.fetch_tuple( stmt_select )
print("%s, %s" % (cols[0], cols[1]))
cols = ibm_db.fetch_tuple( stmt_select )
print(cols)
# Close connections
cur.close()
ibm_db.close(ibm_db_conn)
