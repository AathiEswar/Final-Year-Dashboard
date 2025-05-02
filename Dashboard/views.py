from django.shortcuts import render
from django.conf import settings
import mysql.connector as sql

def index(request):
    db = settings.DATABASES["mysql"]
    con = sql.connect(host=db["HOST"], user=db["USER"], password=db["PASSWORD"], database=db["NAME"])
    cursor = con.cursor(dictionary=True)
    query = """
    SELECT 
    (SELECT COUNT(*) FROM tbl_users) AS users_count,
    (SELECT COUNT(*) FROM tbl_projects) AS projects_count,
    (SELECT SUM(allocated_amount) FROM tbl_budget) AS budget;
    """
    cursor.execute(query)
    Dashboard = cursor.fetchone()
  
    query = """
    SELECT d.department_name, COUNT(u.user_id) AS User_Data
    FROM tbl_users u
    JOIN tbl_departments d 
    ON u.department_id = d.department_id
    GROUP BY d.department_id, d.department_name;
    """
    cursor.execute(query)
    Users = cursor.fetchall()
    User_Label = [dept['department_name'] for dept in Users]
    User_Data = [dept['User_Data'] for dept in Users]

    query = """
    SELECT 
    (SELECT COUNT(*) FROM tbl_projects WHERE status = 'Pending') AS pending_count,
    (SELECT COUNT(*) FROM tbl_projects WHERE status = 'In Progress') AS in_progress_count,
    (SELECT COUNT(*) FROM tbl_projects WHERE status = 'Completed') AS completed_count,
    ROUND((SELECT COUNT(*) FROM tbl_projects WHERE status = 'Pending') * 100 / (SELECT COUNT(*) FROM tbl_projects), 2) AS pending_percentage,
    ROUND((SELECT COUNT(*) FROM tbl_projects WHERE status = 'In Progress') * 100 / (SELECT COUNT(*) FROM tbl_projects), 2) AS in_progress_percentage,
    ROUND((SELECT COUNT(*) FROM tbl_projects WHERE status = 'Completed') * 100 / (SELECT COUNT(*) FROM tbl_projects), 2) AS completed_percentage;
    """
    cursor.execute(query)
    Project = cursor.fetchone()
    
    query = """
    SELECT 
    SUM(allocated_amount) AS allocated_amount,
    SUM(spent_amount) AS spent_amount,
    SUM(remaining_amount) AS remaining_amount,
    ROUND(SUM(allocated_amount) * 100.0 / NULLIF(SUM(allocated_amount + spent_amount + remaining_amount), 0), 2) AS allocated_persentage,
    ROUND(SUM(spent_amount) * 100.0 / NULLIF(SUM(allocated_amount + spent_amount + remaining_amount), 0), 2) AS spent_persentage,
    ROUND(SUM(remaining_amount) * 100.0 / NULLIF(SUM(allocated_amount + spent_amount + remaining_amount), 0), 2) AS remaining_persentage
    FROM tbl_budget;    
    """
    cursor.execute(query)
    Budget = cursor.fetchone()
    con.commit()
    cursor.close()
    con.close()

    Project_Labels = ["Pending " + str(Project['pending_percentage']) + "%", "In Progress " + str(Project['in_progress_percentage']) + "%", "Completed " + str(Project['completed_percentage']) + "%"]
    Project_Data = [Project['pending_count'], Project['in_progress_count'], Project['completed_count']]

    Budget_Labels = ["Allocated " + str(Budget['allocated_persentage']) + "%", "Spent " + str(Budget['spent_persentage']) + "%", "Remaining " + str(Budget['remaining_persentage']) + "%"]
    Budget_Data = [Budget['allocated_amount'], Budget['spent_amount'], Budget['remaining_amount']]
    return render(request, 'Dashboard/index.html', {"Dashboard": Dashboard, "User_Label": User_Label, "User_Data": User_Data,'Budget': Budget, 'Budget_Labels': Budget_Labels, "Budget_Data": Budget_Data,'Project': Project, 'Project_Labels': Project_Labels, "Project_Data": Project_Data})