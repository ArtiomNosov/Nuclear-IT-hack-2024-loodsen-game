from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import User, Topic, JobStatus, Job, MatchType, Match, ReviewType, Review, Message
from .forms import JobForm, UserForm, MyUserCreationForm
import re

def get_user_context(user):
    if not user.is_authenticated:
        return {}
    transactions = user.transaction_set.all()
    balance = sum([x.amount if x.addition == 1 else -x.amount for x in transactions])
    context = {
        'balance': int(balance)
    }
    return context

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'Пользователь не существует')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неправильный логин или пароль')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def get_customer(job):
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')[0]
    return User.objects.get(id=customer_id['user'])

def get_job_to_customer(jobs):
    job_to_customer = {}  # Создаем пустой словарь

    for job in jobs:
        customer = get_customer(job)
        if customer:
            job_to_customer[job] = customer
    
    return job_to_customer

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    jobs = Job.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    job_count = jobs.count()
    job_messages = Message.objects.filter(
        Q(job__topic__name__icontains=q))[0:3]

    job_to_customer = get_job_to_customer(jobs)  

    context = {'jobs': jobs, 
               'job_to_customer': job_to_customer, 
               'topics': topics,
               'job_count': job_count, 
               'job_messages': job_messages}
    
    context.update(get_user_context(request.user))
    return render(request, 'base/home.html', context)


def job(request, pk):
    job = Job.objects.get(id=pk)
    job_messages = job.message_set.all()
    participants_id = Match.objects.filter(job=job).values('user')
    participants = User.objects.filter(id__in=[user_id['user'] for user_id in participants_id])
    print()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            job=job,
            body=request.POST.get('body')
        )
        message.save()
        if Match.objects.filter(user=request.user).count() == 0:
            match = Match.objects.create(
                job = job,
                user = request.user,
                type = MatchType.objects.get_or_create(name='Participant')[0]
            )
            match.save()
        return redirect('job', pk=job.id)
    
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')
    job_customer = User.objects.filter(id=customer_id[0]['user'])[0]
    context = {'job': job, 'job_messages': job_messages,
               'participants': participants,
               'job_customer': job_customer}
    context.update(get_user_context(request.user))
    return render(request, 'base/job.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    jobs = Job.objects.filter(id__in=[x['job'] for x in 
        Match.objects.filter(user=user, type=MatchType.objects.get_or_create(name='Customer')[0].id).values('job')
    ])
    job_messages = user.message_set.all()
    topics = Topic.objects.all()
    job_to_customer = get_job_to_customer(jobs)
    context = {'user': user, 'job_to_customer': job_to_customer,
               'job_messages': job_messages, 'topics': topics}
    context.update(get_user_context(request.user))
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def userBalance(request, pk):
    user = User.objects.get(id=pk)
    transactions = user.transaction_set.all()
    context = {
        'user': user,
        'transactions': transactions,
    }
    context.update(get_user_context(request.user))
    return render(request, f'base/balance.html', context)


def get_cost(str_cost):
    arr = re.findall(r'\d+', str_cost)
    if len(arr) > 1 and int(arr[1]) < 100:
        return float(arr[0]) + float(arr[1]) * 0.01
    elif len(arr) > 0:
        return arr[0]
    return 0


@login_required(login_url='login')
def createJob(request):
    form = JobForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        job = Job.objects.create(
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            status = JobStatus.objects.get_or_create(name='Find performer')[0],
            cost=get_cost(request.POST.get('cost')),
        )
        
        job.save()
        match = Match.objects.create(
            job = job,
            user = request.user,
            type = MatchType.objects.get_or_create(name='Customer')[0],
        )
        match.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    context.update(get_user_context(request.user))
    return render(request, 'base/job_form.html', context)


@login_required(login_url='login')
def updateJob(request, pk):
    job = Job.objects.get(id=pk)
    form = JobForm(instance=job)
    topics = Topic.objects.all()
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')
    job_customer = User.objects.filter(id=customer_id[0]['user'])[0]
    if request.user != job_customer:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        job.name = request.POST.get('name')
        job.topic = topic
        job.description = request.POST.get('description')
        job.cost = get_cost(request.POST.get('cost'))
        job.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'job': job}
    context.update(get_user_context(request.user))
    return render(request, 'base/job_form.html', context)

def get_customer(job):
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')
    job_customer = User.objects.filter(id=customer_id[0]['user'])[0]
    return job_customer

@login_required(login_url='login')
def deleteJob(request, pk):
    job = Job.objects.get(id=pk)
    job_customer = get_customer(job)

    if request.user != job_customer:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        job.delete()
        return redirect('home')
    context = {'obj': job}
    context.update(get_user_context(request.user))
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    context = {'obj': message}
    context.update(get_user_context(request.user))
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    context.update(get_user_context(request.user))
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    context.update(get_user_context(request.user))
    return render(request, 'base/topics.html', context)


def activityPage(request):
    job_messages = Message.objects.all()
    context = {'job_messages': job_messages}
    context.update(get_user_context(request.user))
    return render(request, 'base/activity.html', context)

# jira super loader

import os
import requests
import sys
# https://docs.google.com/spreadsheets/d/1KfqpJ0u4K9htCjQTiZC4V6tzLwZQCCoa9XLBIQCMk7c/edit?usp=sharing
def getGoogleSeet(spreadsheet_id, outDir, outFile):
  
  url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv'
  response = requests.get(url)
  if response.status_code == 200:
    filepath = os.path.join(outDir, outFile)
    with open(filepath, 'wb') as f:
      f.write(response.content)
      print('CSV file saved to: {}'.format(filepath))    
  else:
    print(f'Error downloading Google Sheet: {response.status_code}')
    sys.exit(1)


##############################################
import pandas as pd
import re
import numpy as np

import requests
import base64
import uuid

sber_id = "08b96aae-68dc-4180-9cfe-86e7e3a36bd0"

sber_secret = "2df7ab68-b4ba-42a8-91e8-f8cf86057f49"

auth_key = "MDhiOTZhYWUtNjhkYy00MTgwLTljZmUtODZlN2UzYTM2YmQwOjJkZjdhYjY4LWI0YmEtNDJhOC05MWU4LWY4Y2Y4NjA1N2Y0OQ=="


url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

def token(auth,scope ='GIGACHAT_API_PERS'):

    rq_uid = str(uuid.uuid4())

    payload={
    'scope': scope
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': rq_uid,
    'Authorization': f"Basic {auth}"
    }
    response = requests.request("POST", url, headers=headers, data=payload,verify=False)
    return response
import gigachat
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models.gigachat import GigaChat

giga_token = token(auth_key)
chat = GigaChat(credentials=auth_key, scope ="GIGACHAT_API_PERS", verify_ssl_certs=False,model="GigaChat")

def paraphrase(human_message):
    messages = [SystemMessage(content = '''
Ты - писатель фэнтези.
Твоя главная цель - придумать название для задачи пользователя и переписать текст этой задачи в стиле фэнтези, и озаглавить описание задачи названием.
Требования к ответу:
-Все слова в сгенерированном ответе близки к жанру фэнтези.
-Сгенерированное описание задачи составляет не более 100 символов.
-В сгенерированном описании присутсвуют все ключевые слова из запроса, а так же все имена из запроса без изменений формы.
-В начале описания ты обращаешься к пользователю словами "Путник" или "Герой" или "Принцесса" или "Рыцарь" или другими персонажами из фэнтези.
-Все глаголы в сгенерированном описании второго лица
-Общий стиль сгенерированного описания близок к фэнтези.
-Ты используешь повелительное наклонение.
-Ты сгенерировал название.
-Ты ответил в формате "Название задачи. Описание задачи".
Убедись, что в твоем ответе присутствет название, которое ты сгенерировал для задания.
Не забудь отправить ответ в формате "Название задачи. Описание задачи". Убедись, что ты озаглавил описание задачи сгенерированным названием на основе запроса пользователя

'''
                              )]
    messages.append(HumanMessage(human_message))
    res = chat.invoke(messages)
    messages.append(res)
    print(res.content)
    return res.content

import time

@login_required(login_url='login')
def updateJira(request):
    outDir = 'tmp/'

    os.makedirs(outDir, exist_ok = True)
    filepath = getGoogleSeet('1KfqpJ0u4K9htCjQTiZC4V6tzLwZQCCoa9XLBIQCMk7c', outDir, "jira.csv")

    jira_df = pd.read_csv('tmp/jira.csv')
    jira_df
    print(jira_df)

    task_df = jira_df[jira_df['Тип задачи'] != 'Эпик']
    task_df

    epic_df = jira_df[jira_df['Тип задачи'] == 'Эпик'][['Ключ', 'Резюме']]
    epic_df.columns = ['Ключ эпика', 'Резюме эпика']
    epic_df

    # task_df = task_df.merge(epic_df, left_on='parent', right_on='Ключ эпика')
    # task_df

    base_job = pd.DataFrame()
    base_job['id'] = task_df['Ключ'].transform(lambda x: re.findall(r'\d+', x)[0])
    base_job['id']

    base_job['name'] = task_df['Резюме']
    base_job['name']
    print(1)
    for i in range(base_job['name'].size):
        res = paraphrase(base_job['name'][i])

        base_job['name'][i] = res
    print(2) 
    print(task_df)

    base_job['description'] = task_df['Описание']
    base_job['description']

    base_job['cost'] = task_df['Story point estimate'].transform(lambda x: 0 if np.isnan(x) else x*1000)
    base_job['cost']

    base_job['created'] = pd.to_datetime(task_df['Создано'], format='%d.%m.%Y %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S.000000')
    base_job['created']

    for i in range(task_df.shape[0]):
        print('job!')
        job = Job.objects.create(
                # id=base_job['id'][i], 
                topic=Topic.objects.get_or_create(name='test')[0], # task_df['Резюме эпика'][i])[0],
                name=base_job['name'][i],
                description=base_job['description'][i],
                status = JobStatus.objects.get_or_create(name='Find performer')[0],
                cost=base_job['cost'][i],
            )
        match = Match.objects.create(
            job = job,
            user = request.user,
            type = MatchType.objects.get_or_create(name='Customer')[0],
        )
        match.save()
        job.save()
    return redirect('home')