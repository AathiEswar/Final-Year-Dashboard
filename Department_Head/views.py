from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import google.generativeai as genai
import json

def dashboard_index(request):
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    query = """
    SELECT 
    (SELECT COUNT(*) FROM tbl_users WHERE department_id = %s) AS users_count,
    (SELECT COUNT(*) FROM tbl_projects WHERE department_id = %s) AS projects_count;
    """
    cursor.execute(query, (request.session["department_id"], request.session["department_id"]))
    Dashboard = cursor.fetchone()
  
    department_id = request.session["department_id"]
    query = f"""
    SELECT 
    (SELECT COUNT(*) FROM tbl_projects WHERE status = 'Pending' AND department_id = {department_id}) AS pending_count,
    (SELECT COUNT(*) FROM tbl_projects WHERE status = 'In Progress' AND department_id = {department_id}) AS in_progress_count,
    (SELECT COUNT(*) FROM tbl_projects WHERE status = 'Completed' AND department_id = {department_id}) AS completed_count,
    ROUND((SELECT COUNT(*) FROM tbl_projects WHERE status = 'Pending' AND department_id = {department_id}) * 100 / (SELECT COUNT(*) FROM tbl_projects WHERE department_id = {department_id}), 2) AS pending_percentage,
    ROUND((SELECT COUNT(*) FROM tbl_projects WHERE status = 'In Progress' AND department_id = {department_id}) * 100 / (SELECT COUNT(*) FROM tbl_projects WHERE department_id = {department_id}), 2) AS in_progress_percentage,
    ROUND((SELECT COUNT(*) FROM tbl_projects WHERE status = 'Completed' AND department_id = {department_id}) * 100 / (SELECT COUNT(*) FROM tbl_projects WHERE department_id = {department_id}), 2) AS completed_percentage;
    """
    cursor.execute(query)
    Project = cursor.fetchone()
    
    Project_Labels = ["Pending " + str(Project['pending_percentage']) + "%", "In Progress " + str(Project['in_progress_percentage']) + "%", "Completed " + str(Project['completed_percentage']) + "%"]
    Project_Data = [Project['pending_count'], Project['in_progress_count'], Project['completed_count']]
    
    return render(request, 'Department_Head/Dashboard/index.html', {"Dashboard": Dashboard, 'Project': Project, 'Project_Labels': Project_Labels, "Project_Data": Project_Data})

def profile_index(request):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_users", (request.session["user_id"], name, email, password, "Department Head", request.session["department_id"]))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department_head/dashboard')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_users WHERE user_id = %s", (request.session["user_id"],))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Department_Head/Profile/index.html', {'User': results})

def project_index(request):
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_projects p JOIN tbl_departments d ON p.department_id = d.department_id WHERE p.department_id = %s;", (request.session["department_id"],))
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Department_Head/Projects/index.html', {'Projects': results})

def user_index(request):
    if(request.method == 'POST'):
        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        user_id = request.POST.get('user_id')
        cursor = con.cursor()
        cursor.execute("DELETE FROM tbl_users WHERE user_id = %s", (user_id,))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department-head/user')
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_users u JOIN tbl_departments d ON u.department_id = d.department_id WHERE u.role = 'Employee' AND u.department_id = %s", (request.session["department_id"],))
    results = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Department_Head/Users/index.html', {'Users': results})

def user_add(request):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_users", (name, email, password, "Employee", request.session["department_id"]))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department-head/user')
    return render(request, 'Department_Head/Users/add.html')

def user_edit(request, id):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_users", (id, name, email, password, "Employee", request.session["department_id"]))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department-head/user')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_users WHERE user_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Department_Head/Users/edit.html', {'User': results})

def task_index(request):
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
            return render(request, 'Department_Head/Tasks/index.html', {'Tasks': results , "Searched" : searched})
        else:
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            task_id = request.POST.get('task_id')
            cursor = con.cursor()
            cursor.execute("DELETE FROM tbl_tasks WHERE task_id = %s", (task_id,))
            con.commit()
            cursor.close()
            con.close()
    return render(request, 'Department_Head/Tasks/index.html')

def task_index_user(request, id):
    if(request.method == 'POST'):
        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        task_id = request.POST.get('task_id')
        cursor = con.cursor()
        cursor.execute("DELETE FROM tbl_tasks WHERE task_id = %s", (task_id,))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department-head/user')
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_tasks WHERE assigned_to = %s AND Department_id = %s", (id, request.session["department_id"]))
    results = cursor.fetchall()
    cursor.execute("SELECT name FROM tbl_users WHERE user_id = %s", (id,))
    results1 = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    return render(request, 'Department_Head/Tasks/index_user.html', {'Tasks': results, 'Name': results1['name']})

def task_add(request):
    if(request.method == 'POST'):
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        assigned_to = request.POST.get('assigned_to')
        project_id = request.POST.get('project_id')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_tasks", (task_title, task_description, assigned_to, project_id, request.session["department_id"], status, priority, due_date))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department-head/task')
    department_id = request.session["department_id"]
    return render(request, 'Department_Head/Tasks/add.html', {'Users': dropdown("tbl_users WHERE role = 'Employee' AND department_id = %s" % department_id), 'Projects': dropdown("tbl_projects WHERE department_id = %s" % department_id)})

def task_edit(request, id):
    if(request.method == 'POST'):
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        assigned_to = request.POST.get('assigned_to')
        project_id = request.POST.get('project_id')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_tasks", (id, task_title, task_description, assigned_to, project_id, request.session["department_id"], status, priority, due_date))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/department-head/task')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_tasks WHERE task_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    results["due_date"] = results["due_date"].strftime('%Y-%m-%d')
    department_id = request.session["department_id"]
    return render(request, 'Department_Head/Tasks/edit.html', {'Users': dropdown("tbl_users WHERE role = 'Employee' AND department_id = %s" % department_id), 'Projects': dropdown("tbl_projects WHERE department_id = %s" % department_id), 'Task': results})

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



def generate_description(request):
    if request.method == 'POST':
        try:
            # Parse the incoming request
            data = json.loads(request.body)
            task_title = data.get('task_title')
            assigned_to = data.get('assigned_to')
            project_id = data.get('project_id')
            status = data.get('status')
            priority = data.get('priority')
            due_date = data.get('due_date')

            # Check if all required fields are provided
            if not all([task_title, assigned_to, project_id, status, priority, due_date]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Create a prompt using the collected data
            prompt = f"""
            Generate a small, concise, professional task description in one paragraph for the following task:
            - Task Title: {task_title}
            - Assigned To: {assigned_to}
            - Project: {project_id}
            - Status: {status}
            - Priority: {priority}
            - Due Date: {due_date}

            The description should focus on the task objective and provide a clear instruction in one paragraph,
            without any markdown formatting or extra details.
            """


            # Call the Gemini API to generate content
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)

            # Check if the response contains text (description)
            if response.text:
                html_description = response.text.strip()

                return JsonResponse({'description': html_description})
            else:
                return JsonResponse({'error': 'Failed to generate description'}, status=500)

        except Exception as e:
            # Catch any error that occurred and return it to the client
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)