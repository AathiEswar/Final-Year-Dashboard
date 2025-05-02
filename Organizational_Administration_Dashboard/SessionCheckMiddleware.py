from django.shortcuts import redirect

class SessionCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        allowed_paths = ['/login']
        
        # for key, value in request.session.items():
        #     print(key, value)

        is_admin = request.session.get('Admin')
        is_department_head = request.session.get('Department Head')
        is_employee = request.session.get('Employee')

        if path in allowed_paths:
            pass

        elif is_admin:
            if path.startswith('/department-head') or path.startswith('/employee'):
                return redirect('/login')

        elif is_department_head:
            if path.startswith('/department-head') == False:
                return redirect('/login')

        elif is_employee:
            if path.startswith('/employee') == False:
                return redirect('/login')

        else:
            return redirect('/login')


        
        response = self.get_response(request)
        return response
