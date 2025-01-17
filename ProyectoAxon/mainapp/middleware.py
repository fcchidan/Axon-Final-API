from django.shortcuts import redirect

class BotCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario no ha pasado la verificación y no está accediendo a la página de verificación
        if not request.session.get('verified') and request.path != '/verificar/':
            return redirect('verify_bot')
        response = self.get_response(request)
        return response
