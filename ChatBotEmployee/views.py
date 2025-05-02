# chatbot/views.py
import json
import google.generativeai as genai
from django.http import JsonResponse
from django.conf import settings
import mysql.connector as sql
from .models import ChatMessage
from django.contrib.auth.models import User

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
def get_database_context(user):
    """Fetch all data from key tables to provide full context to the AI"""
    db = settings.DATABASES["mysql"]
    con = sql.connect(
        host=db["HOST"],
        user=db["USER"],
        password=db["PASSWORD"],
        database=db["NAME"]
    )
    cursor = con.cursor(dictionary=True)

    try:
        context = {}

        # Helper to fetch all rows and count from a table
        def fetch_table_data(name, query, params=None):
            cursor.execute(query, params if params else [])
            rows = cursor.fetchall()
            return {
                "count": len(rows),
                "data": rows
            }

        # Fetch user data for the logged-in employee
        context["user"] = fetch_table_data("users", "SELECT * FROM tbl_users WHERE user_id = %s", (user['user_id'],))
        # Fetch department data related to that user
        context["department"] = fetch_table_data("departments", "SELECT * FROM tbl_departments WHERE department_id = %s", (user['department_id'],))
        # Fetch tasks related to the user or department (if they only access their tasks)
        context["tasks"] = fetch_table_data("tasks", "SELECT * FROM tbl_tasks WHERE assigned_to = %s", (user['user_id'],))
        
        context["projects"] = fetch_table_data("projects","SELECT * FROM tbl_projects WHERE department_id = %s",(user['department_id'],))
        
        context["department_tasks"] = fetch_table_data(
            "tasks",
            """
            SELECT t.*
            FROM tbl_tasks t
            JOIN tbl_projects p ON t.project_id = p.project_id
            WHERE p.department_id = %s
            """,
            (user['department_id'],)
        )
        
        context["department_users"] = fetch_table_data(
            "department_users",
            "SELECT * FROM tbl_users WHERE department_id = %s",
            (user['department_id'],)
        )
        
        return context  # convert to JSON outside if needed

    finally:
        con.close()

def chat_api(request):
    """API endpoint to handle chat interactions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_query = data.get('message', '')
            
            # print("Session contents:")
            # for key, value in request.session.items():
            #     print(f"{key}: {value}")
                
            # print("Role : " , request.session["Employee"])

            
            # Get database context
            user = request.session
            
            db_context = get_database_context(user)
            # db_context = get_database_context()
            
            # Create a prompt that includes the database context
            prompt = f"""
            You are a helpful database assistant for a project management system for only the user that I pass below.
            The following JSON contains User data from the database of the user that will interact with you :
            {db_context}
            
            Based on this data, please answer the following question:
            {user_query}
            
            Respond in a concise and helpful way using only the provided data , always use names instead of ID..
            DO NOT RESPOND IF THE QUERY DEMANDS AN SENSITIVE INFORMATION OR VIOLATES SECURITY ISSUES LIKE PASSWORD
            If the query is about explaining something give it as multiple paragraphs.
            If the query is about listing data give in ordered or unordered list.
            """
            
            # Generate response using Gemini API
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            # Save the conversation
            # ChatMessage.objects.create(
            #     user_message=user_query,
            #     bot_response=response.text
            # )
            
            return JsonResponse({
                'response': response.text
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)