from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from paciente.models import Consulta
from django.contrib.messages import constants, add_message
from datetime import datetime, timedelta

# Create your views here.
def cadastro_medico(request):

  if is_medico(request.user):
    add_message(request, constants.WARNING, "Você já possui cadastro de médico")
    return redirect('/medicos/abrir_horario')

  if request.method == "GET":
    especialidades = Especialidades.objects.all()
    return render(request, "cadastro_medico.html", {'especialidades': especialidades})
  elif request.method == "POST":
    crm = request.POST.get('crm')
    nome = request.POST.get('nome')
    cep = request.POST.get('cep')
    rua = request.POST.get('rua')
    bairro = request.POST.get('bairro')
    numero = request.POST.get('numero')
    cim = request.FILES.get('cim')
    rg = request.FILES.get('rg')
    foto = request.FILES.get('foto')
    especialidade = request.POST.get('especialidade')
    descricao = request.POST.get('descricao')
    valor_consulta = request.POST.get('valor_consulta')
    #Validar entradas
    dados_medico = DadosMedico(
      crm=crm,
      nome=nome,
      cep=cep,
      rua=rua,
      bairro=bairro,
      numero=numero,
      rg=rg,
      cedula_identidade_medica=cim,
      foto=foto,
      user=request.user,
      descricao=descricao,
      especialidade_id=especialidade,
      valor_consulta=valor_consulta
    )
    dados_medico.save()
    add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')
    return redirect('/medicos/abrir_horario')
  

def abrir_horario(request):
  if not is_medico(request.user):
    add_message(request, constants.WARNING, "Realize seu cadastro médico para acessar a página de horarios")
    return redirect("/medicos/cadastro_medico")
  
  if request.method == "GET":
    dados_medico = DadosMedico.objects.get(user=request.user)
    datas_abertas = DatasAbertas.objects.filter(user=request.user)
    return render(request, 'abrir_horario.html', {'dados_medicos': dados_medico, 'datas_abertas': datas_abertas})
  
  elif request.method == "POST":
    data = request.POST.get('data')

    data_format = datetime.strptime(data, "%Y-%m-%dT%H:%M")

    if data_format <= datetime.now():
      add_message(request, constants.WARNING, "Data inválida")
      return redirect('/medicos/abrir_horario')
    
    horario_abrir = DatasAbertas(data=data, user=request.user)
    horario_abrir.save()

    add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso.')
    return redirect('/medicos/abrir_horario')

def consultas_medico(request):
 if not is_medico(request.user):
  add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
  return redirect('/usuarios/logout')

 hoje = datetime.now().date()
 consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1)).order_by('data_aberta__data')
 consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).order_by('data_aberta__data')
 
 return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

