from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

def index(request):
    
    if(request.method == 'POST'):
        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        project_id = request.POST.get('project_id')
        cursor = con.cursor()
        cursor.execute("DELETE FROM tbl_projects WHERE project_id = %s", (project_id,))
        con.commit()
        cursor.close()
        con.close()

    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT p.project_id, p.project_name, p.status, d.department_name FROM tbl_projects p JOIN tbl_departments d ON p.department_id = d.department_id;")
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Projects/index.html', {'Projects': results})

def add(request):
    if(request.method == 'POST'):
        project_name = request.POST.get('project_name')
        department_id = request.POST.get('department_id')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_projects", (project_name, department_id, status, start_date, end_date, budget))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/project')
    return render(request, 'Projects/add.html', {"Departments": departments()})

def edit(request, id):
    if(request.method == 'POST'):
        project_name = request.POST.get('project_name')
        department_id = request.POST.get('department_id')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_projects", (id, project_name, department_id, status, start_date, end_date, budget))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/project')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_projects WHERE project_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()    
    cursor.close()
    con.close()
    results['start_date'] = results['start_date'].strftime('%Y-%m-%d')
    results['end_date'] = results['end_date'].strftime('%Y-%m-%d')
    return render(request, 'Projects/edit.html', {'Project': results, "Departments": departments()})

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