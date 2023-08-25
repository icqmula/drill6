from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from .forms import VehiculoForm, RegistroUsuarioForm

from django.http import HttpResponse, HttpResponseRedirect
from tokenize import PseudoExtras
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import VehiculoModel
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/vehiculo/login/')
def indexView(request):
    return render(request, 'index.html',{})


@permission_required('vehiculo.add_vehiculomodel', raise_exception=True)
def addVehiculo(request):
    form = VehiculoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = VehiculoForm()
        messages.success(request, '¡Los datos se han procesado exitosamente!')

    return render(request, "addform.html", {'form': form})


def registro_view(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            content_type = ContentType.objects.get_for_model(VehiculoModel)
            visualizar_catalogo = Permission.objects.get(codename='visualizar_catalogo', content_type=content_type)

            user = form.save()

            user.user_permissions.add(visualizar_catalogo)

            login(request, user)
            messages.success(request, "Usuario registrado exitosamente.")
            return HttpResponseRedirect('/')
        messages.error(request, "Registro inválido. Algunos datos incorrectos. Verifique")

    form = RegistroUsuarioForm()
    context = {"register_form": form }
    return render(request, "registro.html", context)

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Iniciaste sesión como {username}.")
                return HttpResponseRedirect('/')
            else:
                messages.error(request, "Username o password inválido!")
        else:
            messages.error(request, "Username o password inválido!")

    form = AuthenticationForm()
    context = {"login_form": form}
    return render(request, "login.html", context)

@permission_required('vehiculo.visualizar_catalogo', raise_exception=True)
def listar_vehiculo(request):
    vehiculos = VehiculoModel.objects.all()
    context = {'lista_vehiculos': vehiculos}
    return render(request, 'lista.html', context)