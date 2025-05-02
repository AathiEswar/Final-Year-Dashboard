from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

def index(request):
    
    if(request.method == 'POST'):
        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        budget_id = request.POST.get('budget_id')
        cursor = con.cursor()
        cursor.execute("DELETE FROM tbl_budget WHERE budget_id = %s", (budget_id,))
        con.commit()
        cursor.close()
        con.close()

    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT b.*, d.department_name FROM tbl_budget b JOIN tbl_departments d ON b.department_id = d.department_id;")
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Budgets/index.html', {'Budgets': results})

def add(request):
    if(request.method == 'POST'):
        department_id = request.POST.get('department_id')
        allocated_amount = request.POST.get('allocated_amount')
        spent_amount = request.POST.get('spent_amount')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_budget", (department_id, allocated_amount, spent_amount))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/budget')
    return render(request, 'Budgets/add.html', {"Departments": departments()})

def edit(request, id):
    if(request.method == 'POST'):
        department_id = request.POST.get('department_id')
        allocated_amount = request.POST.get('allocated_amount')
        spent_amount = request.POST.get('spent_amount')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_budget", (id, department_id, allocated_amount, spent_amount))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/budget')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_budget WHERE budget_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()    
    cursor.close()
    con.close()
    return render(request, 'Budgets/edit.html', {'Budget': results, "Departments": departments()})

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