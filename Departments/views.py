from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

def index(request):
    
    if(request.method == 'POST'):
        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        department_id = request.POST.get('department_id')
        cursor = con.cursor()
        cursor.execute("DELETE FROM tbl_departments WHERE department_id = %s", (department_id,))
        con.commit()
        cursor.close()
        con.close()

    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_departments")
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Departments/index.html', {'Departments': results})

def add(request):
    if(request.method == 'POST'):
        department_name = request.POST.get('department_name')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_departments", (department_name,))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department')
    return render(request, 'Departments/add.html')

def edit(request, id):
    if(request.method == 'POST'):
        department_name = request.POST.get('department_name')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_departments", (id, department_name))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_departments WHERE department_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Departments/edit.html', {'Department': results})