import apps.dbconnect as db

def addfewproperties():
    
    sqlcode = """ INSERT INTO properties(
        prop_id,
        prop_desc,
        employee_id,
        prop_purch_amt,
        prop_qty,
        prop_unit,
        prop_remarks,
        rcpt_name,
        prop_total_purch_amt,
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    from datetime import datetime
    
    db.modifydatabase(sqlcode, ['12', 'aircon12', '3', '123123', '2' , 'pc', 'null', 'null', '13213' ])
    print('done!')

sql_query = """SELECT * FROM employees"""
values=[]
columns = ['id', 'ln', 'fn', 'role', 'modified', 'is_deleted']
df = db.querydatafromdatabase(sql_query, values, columns)
print(df)

sql_resetemployees = """
 TRUNCATE TABLE employees RESTART IDENTITY CASCADE
"""
db.modifydatabase(sql_resetemployees, [])
addfewemployees()
df = db.querydatafromdatabase(sql_query, values, columns)
print(df)