from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants, add_message
from django.contrib import auth

# Create your views here.
def cadastro(request):
  if request.method == "GET":
    return render(request, "cadastro.html")
  elif request.method == "POST":
    username = request.POST.get('username')
    email = request.POST.get("email")
    senha = request.POST.get("senha")
    confirmar_senha = request.POST.get('confirmar_senha')

    users = User.objects.filter(username=username,)
    mails = User.objects.filter(email=email,)

    if users.exists():
      add_message(request, constants.ERROR, "Username ja existe")
      return redirect('/usuarios/cadastro')
    
    if mails.exists():
      add_message(request, constants.ERROR, "Email ja cadastrado")
      return redirect('/usuarios/cadastro')
    
    if senha != confirmar_senha:
      add_message(request, constants.ERROR, "A senha e o confirmar senha devem ser iguais")
      return redirect('/usuarios/cadastro')
    
    if len(senha) < 6:
      add_message(request, constants.ERROR, 'A senha deve possuir pelo menos 6 caracteres')
      return redirect('/usuarios/cadastro')
    
    try:
      User.objects.create_user(
      username=username,
      email=email,
      password=senha,
      )
      return redirect('/usuarios/login')
    
    except:
      add_message(request, constants.ERROR, 'Erro ao cadastrar usuário')
      return redirect('/usuarios/cadastro')
    
def login_view(request):
  if request.method == "GET":
    return render(request, "login.html")
  elif request.method == "POST":
    username = request.POST.get("username")
    senha = request.POST.get("senha")

    user = auth.authenticate(request, username=username, password=senha)

    if user:
      auth.login(request, user)
      return redirect("/pacientes/home")
    
    add_message(request, constants.ERROR, "Usuário ou senha inválidos")
    return redirect('/usuarios/login')

def logout(request):
  auth.logout(request)
  return redirect("/usuarios/login")