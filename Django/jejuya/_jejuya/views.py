import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from . import models as mo
from . import utilities as ut
from . import daos as do

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash



##########
# views.py
# def index(request): # 메인 페이지(기준점 검색(선택) 페이지)
# def point_around(request): # 기준점 검색 결과 페이지
# def around_detail(request): # 관광지 상세 페이지
# def schedule(request): # 내 일정 페이지
# def schedule_map(request): # 일정 지도 페이지
# def around_list(request): # 관광지 리스트 페이지
# def point_list(request): # 기준점 리스트 페이지
# def contact(request): # 얍 관리자 연락처 페이지
# def terms(request): # 얍 이용약관 페이지
# supervisor
# def supervisor(request): #관리자 페이지
# def supervisor_accounts(request): # 사용자 관리 페이지
# def supervisor_arounds(request): # 관광지 관리 페이지
# def supervisor_around_write(request): # 관광지 등록 페이지
# def supervisor_around(request): # 관광지 상세 페이지
# def supervisor_points(request): # 기준점 관리 페이지
# def supervisor_point_write(request): # 기준점 등록 페이지
# def supervisor_point(request): # 기준점 상세 페이지
# def supervisor_push(request): # 푸시 발송 페이지
# def supervisor_login(request):  # 관리자 로그인 페이지



#########
# views.py
def get_account(request): # 현재 로그인된 사용자 정보 가져오기
    if request.user.is_authenticated: # 로그인되어있다면, 계정 정보 가져오기
        account_id = request.user.username.replace('jejuya_', '')
        account = do.get_account(account_id)
    else: # 로그인되어있지 않다면, 새로운 사용자 생성 후 계정 정보 가져오기
        account = create_account(request)
    return account

def create_account(request): # 새로운 사용자 생성 및 로그인
    id = ut.get_rand_id(16) # 16자리 랜덤 아이디 생성
    password = 'jejuya_' + id # 비밀번호는 아이디와 동일

    # ACCOUNT 테이블에 저장
    account = mo.ACCOUNT(
        id=id,
        password=password,
        account_type='user'
    )
    account.save()

    # 사용자 계정 생성
    try:
        user = User.objects.create_user(
            username=f'jejuya_{id}',
            password=password
        )
    except:
        user = User.objects.get(
            username=f'jejuya_{id}'
        )
        user.set_password(password)
    user.save()

    # 로그인
    user = authenticate(username=f'jejuya_{id}', password=password)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    return do.get_account(id)



##########
# pages
def index(request): # 메인 페이지(기준점 검색(선택) 페이지)
    account = get_account(request)
    schedules = do.get_user_schedules(account['id'])

    # GET
    keyword_or_address = request.GET.get('search', '')

    # CONTEXTS
    points = do.search_points(keyword_or_address)
    contexts = {
        'account': account,
        'schedules': schedules,

        'points': points
    }

    return render(request, '_jejuya/index.html', contexts)

def point_around(request): # 기준점 검색 결과 페이지
    account = get_account(request)
    schedules = do.get_user_schedules(account['id'])
    print(schedules)

    # GET
    point_id = request.GET.get('point_id', '')
    distance = request.GET.get('distance', '15')
    point_type = request.GET.get('point_type', '')
    point_category = request.GET.get('category', '')

    # CONTEXTS
    point = do.get_point(point_id)
    arounds = do.point_arounds(point_id, distance, point_type, point_category)
    all_types = do.get_all_types()
    all_categories = do.get_all_categories()
    contexts = {
        'account': account,
        'schedules': schedules,

        'point': point,
        'arounds': arounds,
        'all_categories': all_categories,
        'all_types': all_types,
        'distance': distance,
    }

    return render(request, '_jejuya/point_around.html', contexts)

def around_detail(request): # 관광지 상세 페이지
    account = get_account(request)

    # GET
    around_id = request.GET.get('around_id', '')

    # CONTEXTS
    around = do.get_around(around_id)
    contexts = {
        'account': account,

        'around': around
    }

    return render(request, '_jejuya/around_detail.html', contexts)

def schedule(request): # 내 일정 페이지
    account = get_account(request)

    # CONTEXTS
    schedules = do.get_user_schedules(account['id'])
    contexts = {
        'account': account,

        'schedules': schedules
    }

    return render(request, '_jejuya/schedule.html', contexts)

def schedule_map(request): # 일정 지도 페이지
    account = get_account(request)

    # GET
    schedule_id = request.GET.get('id', '')

    # CONTEXTS
    schedules = do.get_user_schedules(account['id'])
    schedule = do.get_schedule(schedule_id)
    contexts = {
        'account': account,
        'schedules': schedules,

        'schedule': schedule
    }

    return render(request, '_jejuya/schedule_map.html', contexts)

def around_list(request): # 관광지 리스트 페이지
    account = get_account(request)

    # CONTEXTS
    arounds = do.get_all_arounds()
    contexts = {
        'account': account,

        'arounds': arounds
    }

    return render(request, '_jejuya/around_list.html', contexts)

def point_list(request): # 기준점 리스트 페이지
    account = get_account(request)

    # CONTEXTS
    points = do.get_all_points()
    contexts = {
        'account': account,

        'points': points
    }

    return render(request, '_jejuya/point_list.html', contexts)

def contact(request): # 얍 관리자 연락처 페이지
    return render(request, '_jejuya/contact.html')

def terms(request): # 얍 이용약관 페이지
    return render(request, '_jejuya/terms.html')



##########
# supervisor
def supervisor(request): #관리자 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    contexts = {
        'account': account
    }

    return render(request, '_jejuya/supervisor.html', contexts)

def supervisor_accounts(request): # 사용자 관리 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    accounts = do.get_all_accounts()
    contexts = {
        'account': account,

        'accounts': accounts
    }

    return render(request, '_jejuya/supervisor_accounts.html', contexts)

def supervisor_arounds(request): # 관광지 관리 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    arounds = do.get_all_arounds()
    contexts = {
        'account': account,

        'arounds': arounds
    }

    return render(request, '_jejuya/supervisor_arounds.html', contexts)

def supervisor_around_write(request): # 관광지 등록 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    around_types = []
    categories = []
    for around in mo.AROUND.objects.all():
        around_types.append(around.around_type)
        for category in around.categories.split(','):
            categories.append(category)
    around_types = list(set(around_types))
    categories = list(set(categories))
    contexts = {
        'account': account,

        'around_types': around_types,
        'categories': categories
    }

    return render(request, '_jejuya/supervisor_around_write.html', contexts)

def supervisor_around(request): # 관광지 상세 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # GET
    around_id = request.GET.get('around_id', '')

    # CONTEXTS
    around = do.get_around(around_id)
    contexts = {
        'account': account,

        'around': around
    }

    return render(request, '_jejuya/supervisor_around.html', contexts)

def supervisor_points(request): # 기준점 관리 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    points = do.get_all_points()
    contexts = {
        'account': account,

        'points': points
    }

    return render(request, '_jejuya/supervisor_points.html', contexts)

def supervisor_point_write(request): # 기준점 등록 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    points = do.get_all_points()
    contexts = {
        'account': account,

        'points': points
    }

    return render(request, '_jejuya/supervisor_point_write.html', contexts)

def supervisor_point(request): # 기준점 상세 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # GET
    point_id = request.GET.get('point_id', '')

    # CONTEXTS
    point = do.get_point(point_id)
    contexts = {
        'account': account,

        'point': point
    }

    return render(request, '_jejuya/supervisor_point.html', contexts)

def supervisor_push(request): # 푸시 발송 페이지
    account = get_account(request)
    if account['account_type'] != 'supervisor': # 관리자가 아니라면, 관리자 로그인 페이지로 이동
        return redirect('supervisor_login')

    # CONTEXTS
    contexts = {
        'account': account
    }

    return render(request, '_jejuya/supervisor_push.html', contexts)

def supervisor_login(request):  # 관리자 로그인 페이지
    logout(request)
    request.session.flush()

    # CONTEXTS
    contexts = {
        'ip': ut.get_ip(request)
    }

    return render(request, '_jejuya/supervisor_login.html', contexts)