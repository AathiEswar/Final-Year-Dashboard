from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

def index(request):
    if(request.method == 'POST'):
        if request.POST.get('role'):
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            cursor = con.cursor(dictionary=True)
            cursor.execute(f"SELECT u.user_id, u.name, u.role, u.department_id, d.department_name FROM tbl_users u JOIN tbl_departments d ON u.department_id = d.department_id WHERE role = '{request.POST.get('role')}';")
            results = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()
            return render(request, 'Users/index.html', {'Users': results})

        else:
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            user_id = request.POST.get('user_id')
            cursor = con.cursor()
            cursor.execute("DELETE FROM tbl_users WHERE user_id = %s", (user_id,))
            con.commit()
            cursor.close()
            con.close()
    return render(request, 'Users/index.html')

def add(request):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        department_id = request.POST.get('department_id')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_users", (name, email, password, role, department_id))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/user')
    return render(request, 'Users/add.html', {"Departments": departments()})

def edit(request, id):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        department_id = request.POST.get('department_id')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_users", (id, name, email, password, role, department_id))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/user')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_users WHERE user_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Users/edit.html', {'User': results, "Departments": departments()})

def departments():
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_departments")
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return results