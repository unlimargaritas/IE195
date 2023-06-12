import apps.dbconnect as db
import pandas as pd

import hashlib

import os

df = pd.read_csv("sample.csv")

def addemployees():
    sql = """ 

        WITH temp AS (
        INSERT INTO users
                (
                user_name,
                user_password,
                user_fn,
                user_ln,
                user_faculty,
                user_admin,
                user_dep_head,
                user_delete_ind
                )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING user_id
        )
        INSERT INTO employees
            (
                employee_ln,
                employee_fn,
                employee_role,
                employee_modified_date,
                user_id,
                employee_delete_ind
            )
        SELECT %s, %s, %s, %s, user_id, %s
        FROM temp;
        """

    from datetime import datetime

    names = df['ACCOUNTABLE\nOFFICER'].dropna().unique()

    counter = 0
    for name in names:
        if ',' in name:
            first_name = name.split(", ")[1]
            last_name = name.split(", ")[0]
        else: 
            first_name = ''
            last_name = name

        encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()
        db.modifydatabase(sql, ["temp" + str(counter), encrypt_string("temp" + str(counter)), first_name, last_name, True, False, False, False, last_name, first_name, 'Faculty', datetime.now(), False])

        counter += 1

    print("employee add successful")

def getemployeesdict():
    sql_query = """SELECT employee_id, employee_ln, employee_fn FROM employees"""
    values=[]
    columns = ['id', 'ln', 'fn']
    df = db.querydatafromdatabase(sql_query, values, columns)

    employee_dict = {}
    for index in df.index:

        if df['fn'][index]:
            name = df['ln'][index] + ', ' + df['fn'][index]
        else:
            name = df['ln'][index]

        employee_dict[name] = int(df['id'][index])

    employee_dict['nan'] = ''

    return employee_dict

def addproperties(employee_dict):

    sqlcode = """ INSERT INTO properties(
                prop_qty,
                prop_unit, 
                prop_name, 
                prop_desc,
                prop_purch_date,
                prop_ret_date, 
                prop_purch_amt, 
                prop_total_purch_amt, 
                employee_id,
                prop_remarks,
                prop_delete_ind
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    for index, row in df.iterrows():
        quantity = str(row['QTY']) if not(pd.isna(row['QTY'])) else None
        unit = row['UNIT'] if not(pd.isna(row['UNIT'])) else None
        name = row['NAME'] if not(pd.isna(row['NAME'])) else None
        desc = row['DESCRIPTION'] if not(pd.isna(row['DESCRIPTION'])) else None
        purch_date = row['DATE ACQD'] if not(pd.isna(row['DATE ACQD'])) else None
        ret_date = row['MRDATE'] if not(pd.isna(row['MRDATE'])) else None
        prop_purch_amt = str(row[' UNIT\nCOST ']) if not(pd.isna(row[' UNIT\nCOST '])) else None
        prop_total_purch_amt = str(row[' TOTAL\nCOST ']) if not(pd.isna(row[' TOTAL\nCOST '])) else None
        employee = employee_dict[row['ACCOUNTABLE\nOFFICER']] if not(pd.isna(row['ACCOUNTABLE\nOFFICER'])) else None
        remarks = row['REMARKS'] if not(pd.isna(row['REMARKS'])) else None
        
        values = [quantity, unit, name, desc, purch_date, ret_date, prop_purch_amt, prop_total_purch_amt, employee, remarks, False] 
        db.modifydatabase(sqlcode, values)

    print("properties add successful")



# sql_query = """SELECT * FROM employees"""
# values=[]
# columns = ['id', 'ln', 'fn', 'role', 'modified', 'is_deleted']
# df = db.querydatafromdatabase(sql_query, values, columns)
# print(df)

# sql_resetemployees = """
#  TRUNCATE TABLE employees RESTART IDENTITY CASCADE
# """
# db.modifydatabase(sql_resetemployees, [])

addemployees()

employee_dict = getemployeesdict()

addproperties(employee_dict)
# df = db.querydatafromdatabase(sql_query, values, columns)
# print(df)