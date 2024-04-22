from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from paciente.models import Consulta, Documento
from django.contrib.messages import constants, add_message
from datetime import datetime, timedelta

# Create your views here.
def cadastro_medico(request):

  if is_medico(request.user):
    add_message(request, constants.WARNING, "Você já possui cadastro de médico")
    return redirect('/medicos/abrir_horario')

  if request.method == "GET":
    especialidades = Especialidades.objects.all()
    return render(request, "cadastro_medico.html", {'especialidades': especialidades, 'is_medico': is_medico(request.user)})
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
    datas_abertas = DatasAbertas.objects.filter(user=request.user).order_by('data')
    return render(request, 'abrir_horario.html', {'dados_medicos': dados_medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
  
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
 consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user).order_by('data_aberta__data')
 
 return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

def consulta_area_medico(request, id_consulta):
  if not is_medico(request.user):
    add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
    return redirect('/usuarios/logout')
  
  if request.method == "GET":
    consulta = Consulta.objects.get(id=id_consulta)
    documentos = Documento.objects.filter(consulta=consulta)
    return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos,'is_medico': is_medico(request.user)})
  elif request.method == "POST":
    consulta = Consulta.objects.get(id=id_consulta)
    link = request.POST.get('link')
    if consulta.status == 'C':
      add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
      return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    elif consulta.status == "F":
      add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
      return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    consulta.link = link
    consulta.status = 'I'
    consulta.save()
    add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
def finalizar_consulta(request, id_consulta):
   if not is_medico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem finalizar consultas.')
        return redirect('/usuarios/logout')
   
   consulta=Consulta.objects.get(id=id_consulta)
   if request.user != consulta.data_aberta.user:
      add_message(request, constants.ERROR, "Você não possui autorização para finalizar essa consulta!")
      return redirect("/medicos/consultas_medico/")
   
   consulta.status = "F"
   consulta.save()
   return redirect(f"/medicos/consulta_area_medico/{id_consulta}")

def add_documento(request, id_consulta):
  if not is_medico(request.user):
    add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
    return redirect('/usuarios/logout')
  
  consulta = Consulta.objects.get(id=id_consulta)
  
  if consulta.data_aberta.user != request.user:
    add_message(request, constants.ERROR, 'Essa consulta não é sua!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
  
  titulo = request.POST.get('titulo')
  documento = request.FILES.get('documento')
  
  if not documento:
    add_message(request, constants.WARNING, 'Adicione o documento.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
  
  documento = Documento(
    consulta=consulta,
    titulo=titulo,
    documento=documento
  )
  documento.save()
  add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
  return redirect(f'/medicos/consulta_area_medico/{id_consulta}')