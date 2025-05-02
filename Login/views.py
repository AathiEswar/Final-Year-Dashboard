from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_users WHERE email = %s AND password = %s", (email, password))
        results = cursor.fetchone()
        con.commit()
        cursor.close()
        con.close()
        if results is None:
            return render(request, 'Login/index.html', {"Error": "Please enter correct email & password!"})
        if results["role"] == "Admin":
            request.session['Admin'] = 'Admin'
            request.session['user_id'] = results['user_id']
            return redirect('/')
        elif results["role"] == "Department Head":
            request.session['Department Head'] = 'Department Head'
            request.session['department_id'] = results['department_id']
            request.session['user_id'] = results['user_id']
            return redirect('/department-head/dashboard')
        elif results["role"] == "Employee":
            request.session['Employee'] = 'Employee'
            request.session['department_id'] = results['department_id']
            request.session['user_id'] = results['user_id']
            return redirect('/employee/dashboard')
    return render(request, 'Login/index.html')

def logout(request):
    request.session.flush()
    return redirect('/login')