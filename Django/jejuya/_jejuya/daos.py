from . import models as mo
from django.db.models import Q


# DB GET
def get_all_accounts():
    accounts = mo.ACCOUNT.objects.all().order_by('account_type', '-dt')
    accounts_data = [
        {
            'id': account.id,
            'account_type': account.account_type,
            'device_token': account.device_token,
            'dt': account.dt
        } for account in accounts
    ]
    return accounts_data

def get_account(account_id):
    account = mo.ACCOUNT.objects.get(id=account_id)
    account_data = {
        'id': account.id,
        'account_type': account.account_type,
        'device_token': account.device_token,
        'dt': account.dt
    }
    return account_data

def get_user_schedules(user_id):
    schedules = mo.SCHEDULE.objects.filter(user_id=user_id).order_by('-date')
    schedules_data = []
    for schedule in schedules:
        schedule_data = {
            'id': schedule.id,
            'date': schedule.date,
            'items': get_schedule_items(schedule.id)
        }
        if schedule_data['items'] is None:
            schedule.delete()
        else:
            schedules_data.append(schedule_data)
    return schedules_data

def get_schedule(schedule_id):
    schedule = mo.SCHEDULE.objects.get(id=schedule_id)
    schedule_data = {
        'id': schedule.id,
        'date': schedule.date,
        'items': get_schedule_items(schedule.id)
    }
    return schedule_data

def get_schedule_items(schedule_id):
    schedule_items = mo.SCHEDULE_ITEM.objects.filter(schedule_id=schedule_id)
    if not schedule_items:
        return None
    schedule_items_datas = []
    for schedule_item in schedule_items:
        schedule_items_data = {
            'id': schedule_item.id,
            'around': get_around(schedule_item.around_id)
        }
        if schedule_items_data['around'] is None:
            schedule_items_data['around'] = get_point(schedule_item.around_id)
        schedule_items_datas.append(schedule_items_data)
    return schedule_items_datas

def get_schedule_item(schedule_item_id):
    schedule_item = mo.SCHEDULE_ITEM.objects.get(id=schedule_item_id)
    schedule_item_data = {
        'id': schedule_item.id,
        'schedule': get_schedule(schedule_item.schedule_id),
        'around': get_around(schedule_item.around_id)
    }
    return schedule_item_data

def get_all_points():
    points = mo.POINT.objects.all()
    points_data = [
        {
            'id': point.id,
            'name': point.name,
            'address': point.address,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'rooms_cnt': point.rooms_cnt,
            'tel': point.tel,
            'note': point.note,
            'medias': str(point.medias).split(',')
        } for point in points
    ]
    return points_data

def get_point(point_id):
    point = mo.POINT.objects.get(id=point_id)
    point_data = {
        'id': point.id,
        'name': point.name,
        'address': point.address,
        'latitude': point.latitude,
        'longitude': point.longitude,
        'rooms_cnt': point.rooms_cnt,
        'tel': point.tel,
        'note': point.note,
        'medias': str(point.medias).split(',')
    }
    return point_data

def get_all_arounds():
    arounds = mo.AROUND.objects.all()
    arounds_data = [
        {
            'id': around.id,
            'name': around.name,
            'address': around.address,
            'latitude': around.latitude,
            'longitude': around.longitude,
            'tel': around.tel,
            'around_type': around.around_type,
            'categories': str(around.categories).split(','),
            'open_time': around.open_time,
            'holiday': around.holiday,
            'reserve_link': around.reserve_link,
            'note': around.note,
            'medias': str(around.medias).split(',')
        } for around in arounds
    ]
    return arounds_data

def get_around(around_id):
    around = mo.AROUND.objects.filter(id=around_id).first()
    if around is None:
        return None
    around_data = {
        'id': around.id,
        'name': around.name,
        'address': around.address,
        'latitude': around.latitude,
        'longitude': around.longitude,
        'tel': around.tel,
        'around_type': around.around_type,
        'categories': str(around.categories).split(','),
        'open_time': around.open_time,
        'holiday': around.holiday,
        'reserve_link': around.reserve_link,
        'note': around.note,
        'medias': str(around.medias).split(',')
    }
    return around_data

# others
def search_points(keyword_or_address):
    points = mo.POINT.objects.filter(Q(name__contains=keyword_or_address) | Q(address__contains=keyword_or_address))
    points_data = [
        {
            'id': point.id,
            'name': point.name,
            'address': point.address,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'rooms_cnt': point.rooms_cnt,
            'tel': point.tel,
            'note': point.note,
            'medias': str(point.medias).split(',')
        } for point in points
    ]
    return points_data

def point_arounds(point_id, distance, around_type, around_category):
    point = mo.POINT.objects.get(id=point_id)
    distance = int(distance) # km
    # 0.1 lat/lng = 11.1km
    distance = distance / 111

    arounds = mo.AROUND.objects.filter(
        latitude__gte=float(point.latitude) - distance,
        latitude__lte=float(point.latitude) + distance,
        longitude__gte=float(point.longitude) - distance,
        longitude__lte=float(point.longitude) + distance,
        around_type__contains=around_type,
        categories__contains=around_category
    )
    arounds_data = [
        {
            'id': around.id,
            'name': around.name,
            'address': around.address,
            'latitude': around.latitude,
            'longitude': around.longitude,
            'tel': around.tel,
            'around_type': around.around_type,
            'categories': str(around.categories).split(','),
            'open_time': around.open_time,
            'holiday': around.holiday,
            'reserve_link': around.reserve_link,
            'note': around.note,
            'medias': str(around.medias).split(',')
        } for around in arounds
    ]
    return arounds_data

def get_all_categories():
    arounds = mo.AROUND.objects.all()
    categories = []
    for around in arounds:
        for category in str(around.categories).split(','):
            if category not in categories:
                categories.append(category)
    return categories

def get_all_types():
    arounds = mo.AROUND.objects.all()
    types = []
    for around in arounds:
        if around.around_type not in types:
            types.append(around.around_type)
    return types