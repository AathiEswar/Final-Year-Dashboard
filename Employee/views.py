from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql


def dashboard_index(request):
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    query = """
    SELECT 
    (SELECT COUNT(*) FROM tbl_tasks WHERE status = 'Pending' AND assigned_to = %s) AS pending_count,
    (SELECT COUNT(*) FROM tbl_tasks WHERE status = 'In Progress' AND assigned_to = %s) AS inprogress_count,
    (SELECT COUNT(*) FROM tbl_tasks WHERE status = 'Completed' AND assigned_to = %s) AS completed_count;
    """
    cursor.execute(query, (request.session["user_id"], request.session["user_id"], request.session["user_id"]))
    Dashboard = cursor.fetchone()
    
    return render(request, 'Employee/Dashboard/index.html', {"Dashboard": Dashboard})

def profile_index(request):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_users", (request.session["user_id"], name, email, password, "Employee", request.session["department_id"]))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/employee/dashboard')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_users WHERE user_id = %s", (request.session["user_id"],))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Employee/Profile/index.html', {'User': results})

def task_index(request):
    searched = False
    if(request.method == 'POST'):
        if request.POST.get('status') is not None:
            searched = True
            status = request.POST.get('status')
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            cursor = con.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tbl_tasks t JOIN tbl_users u ON t.assigned_to = u.user_id WHERE t.department_id = %s AND t.status = %s", (request.session['department_id'], status))
            results = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()
            return render(request, 'Employee/Tasks/index.html', {'Tasks': results , 'Searched' : searched})
        else:
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            task_id = request.POST.get('task_id')
            cursor = con.cursor()
            cursor.execute("DELETE FROM tbl_tasks WHERE task_id = %s", (task_id,))
            con.commit()
            cursor.close()
            con.close()
    return render(request, 'Employee/Tasks/index.html')


def task_edit(request, id):
    if(request.method == 'POST'):
        status = request.POST.get('status1')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.execute("UPDATE tbl_tasks SET status = %s WHERE task_id = %s", (status, id))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/employee/task')
    return redirect('/login')

def dropdown(table):
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM " + table)
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return results