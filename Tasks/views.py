from django.shortcuts import render, redirect
from django.conf import settings
import mysql.connector as sql
import markdown
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import google.generativeai as genai
import json

def index(request):
    if(request.method == 'POST'):
        if request.POST.get('department') is not None:
            department = request.POST.get('department')
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            cursor = con.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tbl_tasks WHERE department_id = %s", (department,))
            results = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()
            return render(request, 'Tasks/index.html', {'departments': dropdown("tbl_departments"), 'Tasks': results})
        else:
            db = settings.DATABASES["mysql"]
            con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
            task_id = request.POST.get('task_id')
            cursor = con.cursor()
            cursor.execute("DELETE FROM tbl_tasks WHERE task_id = %s", (task_id,))
            con.commit()
            cursor.close()
            con.close()
    return render(request, 'Tasks/index.html', {'departments': dropdown("tbl_departments")})

def add(request):
    if(request.method == 'POST'):
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        assigned_to = request.POST.get('assigned_to')
        project_id = request.POST.get('project_id')
        department_id = request.POST.get('department_id')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_add_tasks", (task_title, task_description, assigned_to, project_id, department_id, status, priority, due_date))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/task')
    return render(request, 'Tasks/add.html', {'Users': dropdown("tbl_users"), 'Projects': dropdown("tbl_projects"), 'Departments': dropdown("tbl_departments")})

def edit(request, id):
    if(request.method == 'POST'):
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        assigned_to = request.POST.get('assigned_to')
        project_id = request.POST.get('project_id')
        department_id = request.POST.get('department_id')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')

        db = settings.DATABASES["mysql"]
        con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
        cursor = con.cursor()
        cursor.callproc("sp_update_tasks", (id, task_title, task_description, assigned_to, project_id, department_id, status, priority, due_date))
        con.commit()
        cursor.close()
        con.close()
        return redirect('/task')
    
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_tasks WHERE task_id = %s", (id,))
    results = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()
    results["due_date"] = results["due_date"].strftime('%Y-%m-%d')
    return render(request, 'Tasks/edit.html', {'Users': dropdown("tbl_users"), 'Projects': dropdown("tbl_projects"), 'Departments': dropdown("tbl_departments"), 'Task': results})

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
            department_id = data.get('department_id')
            status = data.get('status')
            priority = data.get('priority')
            due_date = data.get('due_date')

            # Check if all required fields are provided
            if not all([task_title, assigned_to, project_id, department_id, status, priority, due_date]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Create a prompt using the collected data
            prompt = f"""
            Generate a small, concise, professional task description in one paragraph for the following task:
            - Task Title: {task_title}
            - Assigned To: {assigned_to}
            - Project: {project_id}
            - Department: {department_id}
            - Status: {status}
            - Priority: {priority}
            - Due Date: {due_date}

            The description should focus on the task objective and provide a clear instruction in one paragraph, without any markdown formatting or extra details.
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