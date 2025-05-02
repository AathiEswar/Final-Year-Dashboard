# chatbot/views.py
import json
import google.generativeai as genai
from django.http import JsonResponse
from django.conf import settings
import mysql.connector as sql
from .models import ChatMessage

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
        
        def fetch_table_data_user(name, query, params=None):
            cursor.execute(query, params if params else [])
            rows = cursor.fetchall()
            return {
                "count": len(rows),
                "data": rows
            }

        # Helper to fetch all rows and count from a table
        def fetch_table_data(name, query):
            cursor.execute(query)
            rows = cursor.fetchall()
            return {
                "count": len(rows),
                "data": rows
            }
        context["user"] = fetch_table_data_user("users", "SELECT * FROM tbl_users WHERE user_id = %s", (user['user_id'],))
        # Fetch full data from key tables
        context["users"] = fetch_table_data("users", "SELECT * FROM tbl_users")
        context["projects"] = fetch_table_data("projects", "SELECT * FROM tbl_projects")
        context["departments"] = fetch_table_data("departments", "SELECT * FROM tbl_departments")
        context["budget"] = fetch_table_data("budget", "SELECT * FROM tbl_budget")
        context["tasks"] = fetch_table_data("tasks", "SELECT * FROM tbl_tasks")

        return context  # convert to JSON outside if needed

    finally:
        con.close()
        
def chat_api(request):
    """API endpoint to handle chat interactions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_query = data.get('message', '')
            
            user = request.session
            # Get database context
            db_context = get_database_context(user)
            
            # Create a prompt that includes the database context
            prompt = f"""
            You are a helpful database assistant for a project management system.
            The following JSON contains data from the database:
            {db_context}
            
            Based on this data, please answer the following question:
            {user_query}
            
            Respond in a concise and helpful way using only the provided data , always use names instead of ID.
            DO NOT RESPOND IF THE QUERY DEMANDS AN SENSITIVE INFORMATION OR VIOLATES SECURITY ISSUES LIKE PASSWORD, ID.
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