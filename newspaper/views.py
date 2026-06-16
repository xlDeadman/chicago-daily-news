from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Noticia, Comentario, RegistroBelico, RankingFamilia, Familia

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    noticias = list(Noticia.objects.all().order_by('-fecha', '-id'))
    principal = noticias[0] if len(noticias) > 0 else None
    columnas = noticias[1:3] if len(noticias) > 1 else []
    mixtas = noticias[3:5] if len(noticias) > 3 else []
    tendencia = Noticia.objects.filter(tendencia=True).first()
    return render(request, 'newspaper/index.html', {
        'user': request.user,
        'principal': principal,
        'columnas': columnas,
        'mixtas': mixtas,
        'tendencia': tendencia,
    })

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('usuario_habbo', '').strip()
        password = request.POST.get('contrasena', '').strip()
        modo = request.POST.get('modo_publicacion', 'personal')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['modo_publicacion'] = modo
            if user.is_staff:
                return redirect('/panel/')
            else:
                return redirect('/')
        else:
            return redirect('/?error=login')
    return redirect('/')

@csrf_exempt
def registro_view(request):
    if request.method == 'POST':
        username = request.POST.get('usuario_habbo', '').strip()
        password = request.POST.get('contrasena', '').strip()
        if not username or not password:
            return redirect('/?error=vacio')
        if User.objects.filter(username=username).exists():
            return redirect('/?error=existe')
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('/')
    return redirect('/')

@staff_required
def panel_view(request):
    total_noticias = Noticia.objects.count()
    noticias_todas = Noticia.objects.order_by('-fecha', '-id')
    paginator_noticias = Paginator(noticias_todas, 5)
    pagina_noticias = request.GET.get('p_noticias', 1)
    noticias_recientes = paginator_noticias.get_page(pagina_noticias)
    usuarios_todos = User.objects.all().order_by('-date_joined')
    paginator_usuarios = Paginator(usuarios_todos, 5)
    pagina_usuarios = request.GET.get('p_usuarios', 1)
    usuarios = paginator_usuarios.get_page(pagina_usuarios)
    comentarios_todos = Comentario.objects.all().order_by('-fecha')
    paginator_comentarios = Paginator(comentarios_todos, 5)
    pagina_comentarios = request.GET.get('p_comentarios', 1)
    comentarios = paginator_comentarios.get_page(pagina_comentarios)
    registros_todos = RegistroBelico.objects.all().order_by('-fecha')
    paginator_registros = Paginator(registros_todos, 6)
    pagina_registros = request.GET.get('p_registros', 1)
    registros = paginator_registros.get_page(pagina_registros)
    ranking = RankingFamilia.objects.all()
    return render(request, 'newspaper/panel.html', {
        'total_noticias': total_noticias,
        'noticias_recientes': noticias_recientes,
        'usuarios': usuarios,
        'comentarios': comentarios,
        'registros': registros,
        'ranking': ranking,
    })

def logout_view(request):
    logout(request)
    return redirect('/')

@staff_required
def noticias_lista(request):
    noticias = Noticia.objects.all().order_by('-fecha')
    return render(request, 'newspaper/noticias_lista.html', {'noticias': noticias})

@staff_required
def noticia_nueva(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        modo = request.session.get('modo_publicacion', 'personal')
        autor = 'Chicago Daily News' if modo == 'oficial' else request.user.username
        imagen = request.FILES.get('imagen')
        Noticia.objects.create(titulo=titulo, contenido=contenido, autor=autor, imagen=imagen)
        return redirect('/panel/')
    return render(request, 'newspaper/noticia_form.html')

@staff_required
def noticia_editar(request, id):
    noticia = Noticia.objects.get(id=id)
    if request.method == 'POST':
        noticia.titulo = request.POST.get('titulo')
        noticia.contenido = request.POST.get('contenido')
        if request.FILES.get('imagen'):
            noticia.imagen = request.FILES.get('imagen')
        noticia.save()
        return redirect('/panel/')
    return render(request, 'newspaper/noticia_form.html', {'noticia': noticia})

@staff_required
def noticia_eliminar(request, id):
    noticia = Noticia.objects.get(id=id)
    noticia.delete()
    return redirect('/panel/')

def noticia_detalle(request, id):
    noticia = Noticia.objects.get(id=id)
    comentarios = noticia.comentarios.all().order_by('-fecha')
    if request.method == 'POST':
        if request.user.is_authenticated:
            contenido = request.POST.get('contenido', '').strip()
            if contenido:
                Comentario.objects.create(noticia=noticia, autor=request.user, contenido=contenido)
        return redirect(f'/noticia/{id}/')
    return render(request, 'newspaper/noticia_detalle.html', {
        'user': request.user,
        'noticia': noticia,
        'comentarios': comentarios,
    })

@staff_required
def usuarios_lista(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'newspaper/usuarios.html', {'usuarios': usuarios})

@staff_required
def usuario_eliminar(request, id):
    usuario = User.objects.get(id=id)
    usuario.delete()
    return redirect('/panel/')

@staff_required
def usuario_deshabilitar(request, id):
    usuario = User.objects.get(id=id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return redirect('/panel/')

@staff_required
def usuario_permisos(request, id):
    usuario = User.objects.get(id=id)
    usuario.is_staff = not usuario.is_staff
    usuario.save()
    return redirect('/panel/')

@staff_required
def noticia_tendencia(request, id):
    Noticia.objects.all().update(tendencia=False)
    noticia = Noticia.objects.get(id=id)
    noticia.tendencia = True
    noticia.save()
    return redirect('/panel/')

def todas_noticias(request):
    noticias_todas = Noticia.objects.all().order_by('-fecha', '-id')
    paginator = Paginator(noticias_todas, 6)
    pagina = request.GET.get('pagina', 1)
    noticias = paginator.get_page(pagina)
    return render(request, 'newspaper/todas_noticias.html', {
        'user': request.user,
        'noticias': noticias,
    })

@csrf_exempt
def set_modo(request):
    if request.method == 'POST':
        modo = request.POST.get('modo_publicacion', 'personal')
        request.session['modo_publicacion'] = modo
    return redirect('/panel/')

@staff_required
def comentarios_lista(request):
    comentarios = Comentario.objects.all().order_by('-fecha')
    return render(request, 'newspaper/comentarios.html', {'comentarios': comentarios})

@staff_required
def comentario_eliminar(request, id):
    comentario = Comentario.objects.get(id=id)
    comentario.delete()
    return redirect('/panel/comentarios/')

def registros_belicos(request):
    registros_todos = RegistroBelico.objects.all().order_by('-fecha')
    paginator = Paginator(registros_todos, 6)
    pagina = request.GET.get('pagina', 1)
    registros = paginator.get_page(pagina)
    ranking = RankingFamilia.objects.all()
    return render(request, 'newspaper/registros_belicos.html', {
        'user': request.user,
        'registros': registros,
        'ranking': ranking,
    })

@staff_required
def registro_nuevo(request):
    if request.method == 'POST':
        familia1 = request.POST.get('familia1')
        familia2 = request.POST.get('familia2')
        ganador = request.POST.get('ganador')
        fecha = request.POST.get('fecha')
        RegistroBelico.objects.create(
    familia1=familia1,
    familia2=familia2,
    ganador=ganador,
    fecha=fecha if fecha else None
)
        return redirect('/panel/')
    return render(request, 'newspaper/registro_form.html')

@staff_required
def registro_eliminar(request, id):
    registro = RegistroBelico.objects.get(id=id)
    registro.delete()
    return redirect('/panel/')

@staff_required
def ranking_nuevo(request):
    if request.method == 'POST':
        familia = request.POST.get('familia')
        pettadas = request.POST.get('pettadas')
        RankingFamilia.objects.create(familia=familia, pettadas=pettadas)
        return redirect('/panel/')
    return render(request, 'newspaper/ranking_form.html')

@staff_required
def ranking_eliminar(request, id):
    ranking = RankingFamilia.objects.get(id=id)
    ranking.delete()
    return redirect('/panel/')

def familias_activas(request):
    familias = Familia.objects.all().order_by('nombre')
    return render(request, 'newspaper/familias_activas.html', {
        'user': request.user,
        'familias': familias,
    })

@staff_required
def familia_nueva(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        don = request.POST.get('don')
        estado = request.POST.get('estado') == 'on'
        Familia.objects.create(nombre=nombre, don=don, estado=estado)
        return redirect('/panel/')
    return render(request, 'newspaper/familia_form.html')

@staff_required
def familia_eliminar(request, id):
    familia = Familia.objects.get(id=id)
    familia.delete()
    return redirect('/panel/')