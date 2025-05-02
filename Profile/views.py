from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

def index(request):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        department_id = request.POST.get('department_id')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_users", (request.session["user_id"], name, email, password, role, department_id))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_users WHERE user_id = %s", (request.session["user_id"],))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Profile/index.html', {'User': results, "Departments": departments()})

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