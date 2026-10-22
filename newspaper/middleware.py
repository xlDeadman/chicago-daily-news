import os
from django.conf import settings
from django.shortcuts import render

# El aviso se guarda como un archivo dentro de la carpeta media,
# que vive en el Volume de Railway y no se borra con cada deploy.
ARCHIVO_MANTENIMIENTO = os.path.join(settings.MEDIA_ROOT, '.mantenimiento')

# Rutas que siempre funcionan, aunque la página esté en mantenimiento.
RUTAS_PERMITIDAS = ('/panel/', '/login/', '/logout/', '/admin/', '/static/', '/media/')


def esta_en_mantenimiento():
    return os.path.exists(ARCHIVO_MANTENIMIENTO)


def activar_mantenimiento(activo):
    if activo:
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        open(ARCHIVO_MANTENIMIENTO, 'w').close()
    elif os.path.exists(ARCHIVO_MANTENIMIENTO):
        os.remove(ARCHIVO_MANTENIMIENTO)


class MantenimientoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if esta_en_mantenimiento():
            es_staff = request.user.is_authenticated and request.user.is_staff
            if not es_staff and not request.path.startswith(RUTAS_PERMITIDAS):
                return render(request, 'newspaper/mantenimiento.html', status=503)
        return self.get_response(request)
