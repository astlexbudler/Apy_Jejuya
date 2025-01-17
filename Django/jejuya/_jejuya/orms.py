from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.apps import apps
from django.core.serializers import serialize
import json
import copy
from . import models

APP_LABEL = "_jejuya"

def data(request):
    app_label = APP_LABEL
    if request.method == "GET":
        #주의!! app_label에는 조작할 models.py를 관장하며 settings.py에 기술된 Django app의 이름을 기재할 것.
        model = request.GET.get("model","")#모델명
        id = request.GET.get("id","")#기본검색조건
        field = request.GET.get("field","")#검색조건쌍1
        value = request.GET.get("value","")#검색조건쌍2
        obj_count = 1
        if model == '':#모델명이 지정되지 아니한 경우(모델명은 반드시 지정되어야 함)
            return JsonResponse({'success':'n', 'message':'Invalid Request: no model name'}, status=400)
        elif id != '':#id(기본검색조건)이 전달된 경우
            model_class = None
            #모델명, id가 있는 경우(무조건 하나를 검색)
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model)
                record = model_class.objects.get(**{'id': id})
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission
                for field_name in permission_info:
                    output_value = getattr(record, field_name)
                    if permission_info[field_name] == "RW":
                        #API 접근권한: READ & WRITE
                        output_value = output_value
                    elif permission_info[field_name] == "R":
                        #API 접근권한: READ ONLY
                        output_value = output_value
                    elif permission_info[field_name] == "W":
                        #API 접근권한: WRITE ONLY
                        output_value = "*"*len(str(output_value))
                    elif permission_info[field_name] == "":
                        #API 접근권한: ACCESS DENIED
                        output_value = "*"*len(str(output_value))
                    else:
                        #API 접근권한: 미지정
                        output_value = "*"*len(str(output_value))
                    setattr(record, field_name, output_value)#새로 지정
                #모델 인스턴스를 JSON 문자열로 변환
                serialized_data = serialize('json', [record])
                return JsonResponse({
                    'success' : 'y',
                    'message' : f'Successfully Found!: {obj_count} object via pk',
                    'db' : serialized_data,
                }, safe=False, status=200)
            except:
                return JsonResponse({'success':'y', 'message':'Not Found: no model or invalid pk'}, status=404)
        elif field != '':#id는 전달되지 않았으나 검색조건쌍이 전달된 경우
            model_class = None  # 모델을 찾지 못했을 경우에 대비해 미리 정의
            #모델명, 필드명, 검색할 밸류값이 모두 있는 경우(둘 이상을 검색할 수 있음)
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model)
                # 동적으로 Q 객체 생성
                q_objects = Q()
                q_objects |= Q(**{f"{field}__icontains": value})

                # 동적으로 필터링
                records = model_class.objects.filter(q_objects)
                #records = model_class.objects.filter(**{field: value})
                obj_count = len(records)
                # 모델 메타데이터 불러옴
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission

                for record in records:
                    for field_name in permission_info:
                        output_value = getattr(record, field_name)
                        if permission_info[field_name] == "RW":
                            output_value = output_value
                        elif permission_info[field_name] == "R":
                            output_value = output_value
                        elif permission_info[field_name] == "W":
                            output_value = "*"*len(str(output_value))
                        elif permission_info[field_name] == "":
                            output_value = "*"*len(str(output_value))
                        else:
                            output_value = "*"*len(str(output_value))
                        setattr(record, field_name, output_value)
                # 모델 인스턴스를 JSON 문자열로 변환
                serialized_data = serialize('json', records)
                
                # JSON 응답
                return JsonResponse({
                    'success' : 'y',
                    'message' : f'Successfully Found!: {obj_count} objects via field & value',
                    'db' : serialized_data,
                    }, safe=False)
            except model_class.DoesNotExist:
                return JsonResponse({"success": "n", 'message':'Not Found: no model or invalid field name and value'}, status=404)
        elif id == '' and field == '' and value == '':#검색조건 모두 빔: 테이블의 모든 값을 가져옴.
            model_class = None
            try:
                # 해당 모델의 모든 레코드를 가져옴
                model_class = apps.get_model(app_label=app_label, model_name=model)
                all_records = model_class.objects.all()
                records = []
                for record in all_records:
                    records.append(record)
                obj_count = len(records)
                # 모델 메타데이터 불러옴
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission

                for record in records:
                    for field_name in permission_info:
                        output_value = getattr(record, field_name)
                        if permission_info[field_name] == "RW":
                            output_value = output_value
                        elif permission_info[field_name] == "R":
                            output_value = output_value
                        elif permission_info[field_name] == "W":
                            output_value = "*"*len(str(output_value))
                        elif permission_info[field_name] == "":
                            output_value = "*"*len(str(output_value))
                        else:
                            output_value = "*"*len(str(output_value))
                        setattr(record, field_name, output_value)
                # 모든 레코드를 JSON으로 변환
                serialized_data = serialize('json', records)

                # JSON 응답
                return JsonResponse({
                    'success': 'y',
                    'message': f'Successfully Found!: all {obj_count} objects via nothing',
                    'db': serialized_data,
                }, safe=False)
            except model_class.DoesNotExist:
                return JsonResponse({"success": "n", 'message': 'Not Found: no model'}, status=404)
        else:#뭔가 이상한 경우
            return JsonResponse({'success':'n', 'message':'Invalid Request'}, status=400)

    elif request.method == "POST":
        #주의!! app_label에는 조작할 models.py를 관장하며 settings.py에 기술된 Django app의 이름을 기재할 것.
        
        model = request.POST.get("model","")#모델명
        id = request.POST.get("id","")
        field_value = request.POST.get("field_value","")#새로운 값
        #json형식의 문자열을 Python Dict 자료형으로 변환
        field_value = json.loads(field_value)
        if model == '':#모델명이 지정되지 아니한 경우
            return JsonResponse({'success':'n', 'message':'Invalid Request: no model name'}, status=400)
        elif id != '' and field_value != '':#필드명과 목표 id가 정해진 경우, 즉, Update!
            model_class = None  # 모델을 찾지 못했을 경우에 대비해 미리 정의
            record = None
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model)#모델 선택
                record = model_class.objects.get(**{'id': id}) #id로 레코드 검색
                output_record = copy.copy(record)#프론트 공개용 레코드
                #모델 메타데이터 불러오기
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission
                # 필드 정보를 출력
                fields_info = {}
                for field in model_class._meta.fields:
                    field_name = field.name
                    field_type = field.get_internal_type()
                    fields_info[field_name] = field_type

                update_message = ""#접근권한결과여부
                # 필드를 순회하며 전달된 값을 저장. 없는 경우, 기존에 저장됐던 값을 다시 저장. 또, 접근권한별로 처리.
                #단, id는 명시적으로 배제.(안전장치)
                for field in fields_info:
                    #id 값은 명시적으로 변하지 않게 처리.
                    if field == 'id':
                        continue
                    else:
                        pass
                    try:
                        #API 접근 권한에 따라 처리
                        if permission_info[field] == "RW":
                            input_value = field_value[field]#읽고쓰기권한
                            output_value = input_value
                            update_message += f"(Success) {field};\n"
                        elif permission_info[field] == "R":#읽기권한
                            input_value = getattr(record, field)
                            output_value = input_value
                            update_message += f"(Denied) {field};READ ONLY\n"
                        elif permission_info[field] == "W":#쓰기권한
                            input_value = field_value[field]
                            output_value = "*"*len(str(input_value))#censored_Value
                            update_message += f"(Success) {field};\n"
                        elif permission_info[field] == "":#API권한없음
                            input_value = getattr(record, field)
                            output_value = "*"*len(str(input_value))#censored_Value
                            update_message += f"(Denied) {field};SERVER ONLY\n"
                        else:#권한미지정
                            input_value = getattr(record, field)
                            output_value = input_value
                            update_message += f"(Error) {field};PERMISSION NOT DEFINED\n"
                        setattr(record, field, input_value)
                        setattr(output_record, field, output_value)
                    except:#에러발생시
                        input_value = getattr(record, field)
                        setattr(record, field, input_value)
                        update_message += f"(Error) {field};BY INTERNAL SERVER ERROR\n"
                update_message += "\n..System  may set previous value to (Denied) or (Error) cases instead of what you requested."
                #setattr(record, field, input_value)
                record.save()#수정, 저장.(id 자동생성)
                output_record.id = record.id
                # 모델 인스턴스를 JSON 문자열로 변환
                serialized_data = serialize('json', [output_record])
                #output_record.delete()#공개용 레코드는 리소스 절약을 위해 삭제
                # JSON 응답
                return JsonResponse({
                    'success' : 'y',
                    'message' : f'Update ORM Requested; Check The System Message Below!\n\n{update_message}',
                    'db' : serialized_data,
                    }, safe=False, status=200)
            except Exception as e:
                return JsonResponse({"success": "n", 'message':f'Not Found: no model or incorrect field name, actually the problem is that {e}'}, status=404)
        elif id == '' and field_value != '':#id가 없는 경우, 즉, Create! => 초기값생성
            model_class = None
            new_record = None
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model)# 모델 선택
                new_record = model_class()# 새로운 레코드 생성
                output_record = copy.copy(new_record)# 프론트 공개용 레코드
                # 모델 메타데이터 불러오기
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission
                # 필드 정보를 출력
                fields_info = {}
                for field in model_class._meta.fields:
                    field_name = field.name
                    field_type = field.get_internal_type()
                    fields_info[field_name] = field_type
                update_message = ""#작동결과여부
                # 필드를 순회하며 전달된 값을 저장. 없는 경우, '0'을 저장
                for field in fields_info:#실제 테이블에 기술된 필드 명을 순회하는 것임.
                    if field == "id":#id 값은 명시적으로 변하지 않게 처리
                        continue#id 값은 이후 record.save() 시 자동적으로 생성됨.
                    else:
                        pass
                    try:
                        if permission_info[field] == "RW":
                            input_value = field_value[field]
                            output_value = input_value
                            update_message += f"(Success) {field};\n"
                        elif permission_info[field] == "R":
                            input_value = '0'
                            output_value = input_value
                            update_message += f"(Denied) {field}; READ ONLY\n"
                        elif permission_info[field] == "W":
                            input_value = field_value[field]
                            output_value = "*"*len(str(input_value))
                            update_message += f"(Success) {field};\n"
                        elif permission_info[field] == "":
                            input_value = "0"#수정됨(1.12)
                            output_value = "*"*len(str(input_value))
                            update_message += f"(Denied) {field}; SERVER ONLY\n"
                        else:
                            input_value = "0"
                            output_value = input_value
                            update_message += f"(Error) {field}; PERMISSION NOT DEFINED\n"
                        
                        setattr(output_record, field, output_value)
                        setattr(new_record, field, input_value)
                    except:
                        setattr(new_record, field, '0')
                        setattr(output_record, field, '0')
                        update_message += f"(Error) {field}; BY INTERNAL SERVER ERROR\n"
                        #return JsonResponse({'success':'n', 'message':'Invalid request. Check the field_value!'}, status=400)

                update_message += "\n..System may set string 0 to (Denied) or (Error) cases instead of what you requested."
                # 생성한 레코드 저장
                new_record.save()#저장과 함께 id가 생성됨
                output_record.id = new_record.id
        
                # 모델 인스턴스를 JSON 문자열로 변환
                serialized_data = serialize('json', [output_record])
                #output_record.delete()#공개용 레코드는 리소스 절약을 위해 삭제
                # JSON 응답
                return JsonResponse({
                    'success' : 'y',
                    'message' : f'Create ORM Requested; Check The System Message Below!\n\n{update_message}',
                    'db' : serialized_data,
                    }, safe=False, status=201)
            except Exception as e:
                return JsonResponse({"success": "n", 'message':f'Not Found: no model or incorrect field name, Actually the problem is that {e}'}, status=404)
        else:#뭔가 이상한 경우
            return JsonResponse({'success':'n', 'message':'Invalid Request'}, status=400)
            
    elif request.method == "DELETE":
        #주의!! app_label에는 조작할 models.py를 관장하며 settings.py에 기술된 Django app의 이름을 기재할 것.
        
        model = request.GET.get("model","")#모델명
        id = request.GET.get("id","")#기본지정조건
        field = request.GET.get("field","")
        value = request.GET.get("value","")
        obj_count = 0
        if model == '':
            return JsonResponse({'success':'n', 'message':'Invalid Request: no model name'}, status=400)
        elif id != '':
            model_class = None
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model)
                #모델메타데이터 불러오기
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission

                for field_name in permission_info:
                    if permission_info[field_name] == "RW":
                        pass
                    elif permission_info[field_name] == "R":
                        pass
                    elif permission_info[field_name] == "W":
                        pass
                    elif permission_info[field_name] == "":
                    #필드 중 하나라도 서버권한이 필요한 경우, API로 삭제할 수 없음.
                    #즉, 서버단에서 삭제를 위한 기능을 만들거나, 사람이 삭제해야 함.
                        return JsonResponse({'success':'n', 'message':'Forbidden Request: you need higher authority to delete this record.'}, status=403)
                    else:
                        pass

                record = model_class.objects.get(**{'id': id})
                #삭제행동
                obj_count += 1
                record.delete()
                return JsonResponse({
                    'success' : 'y',
                    'message' : f'Successfully Deleted!: {obj_count} object via pk',
                }, safe=False, status=200)
            except Exception as e:
                return JsonResponse({'success':'n', 'message':f'Not Found: no model or invalid pk, Actually the problem is that {e}'}, status=404)
        elif field != '' and value != '':
            model_class = None
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model)
                #모델메타데이터 불러오기
                model_metadata = model_class.MetaData
                permission_info = model_metadata.api_permission

                for field_name in permission_info:
                    if permission_info[field_name] == "RW":
                        pass
                    elif permission_info[field_name] == "R":
                        pass
                    elif permission_info[field_name] == "W":
                        pass
                    elif permission_info[field_name] == "":
                    #필드 중 하나라도 서버권한이 필요한 경우, API로 삭제할 수 없음.
                    #즉, 서버단에서 삭제를 위한 기능을 만들거나, 사람이 삭제해야 함.
                        return JsonResponse({'success':'n', 'message':'Forbidden Request: you need higher authority to delete this record.'}, status=403)
                    else:
                        pass

                records = model_class.objects.filter(**{field: value})
                #삭제행동
                for record in records:
                    obj_count += 1
                    record.delete()
                
                return JsonResponse({
                    'success' : 'y',
                    'message' : f'Successfully Deleted!: {obj_count} objects via field & value',
                }, safe=False, status=200)
            except:
                return JsonResponse({'success':'n', 'message':'Not Found: no model or invalid field name and value'}, status=404)
        else:
            return JsonResponse({'success':'n', 'message':'Invalid Request'}, status=400)
        
    else:
        return JsonResponse({'success':'n', 'message':'Invalid Request'}, status=400)
    
def orm_doctor(request):
    app_label = APP_LABEL
    #주의!! app_label에는 조작할 models.py를 관장하며 settings.py에 기술된 Django app의 이름을 기재할 것.
    all_models = apps.get_models()  # 애플리케이션의 모든 모델 클래스 가져오기
    model_names = []
    message = "ORM Doctor Diagnosis..\n"
    message += "Names of Models ──────────\n"
    for model_class in all_models:
        model_name = model_class.__name__
        message += f"{model_name} "
    message += "\n"
    message += "Details ──────────────────\n"
    model_index = 0
    for model_class in all_models:
        message += f"[{model_index}] Model Name: {model_class.__name__}\n"
        model_index += 1
        #try:
        field_names = []
        for field in model_class._meta.fields:
            field_name = field.name
            field_names.append(field_name)
        # 모델 레벨 메타데이터에 접근
        try:
            model_class = apps.get_model(app_label=app_label, model_name=model_class.__name__)
        except:
            continue
        model_metadata = model_class.MetaData
        # 각 필드의 api_permission 내역 출력(커스텀 메타데이터)
        permission_info = model_metadata.api_permission
        type_info = {}
        for field in model_class._meta.fields:
            field_name = field.name
            field_type = field.get_internal_type()
            type_info[field_name] = field_type
        # 각 필드의 type 내역 출력
        max_length_info = {}
        for field in model_class._meta.fields:
            field_name = field.name
            field_max_length = getattr(field, 'max_length', None)
            max_length_info[field_name] = field_max_length
        # 각 필드의 길이제한 내역 출력
        help_text_info = {}
        for field in model_class._meta.fields:
            field_name = field.name
            field_help_text = getattr(field, 'help_text', None)
            help_text_info[field_name] = field_help_text
        # 각 필드의 주석 내역 출력
        # 조회한 내용을 정리
        for field_name in field_names:
            try:
                message += f"\tField: ({field_name})\n"
                message += f"\t\t├ API Permission: {permission_info[field_name]}\n"
                message += f"\t\t├ Type: {type_info[field_name]}, Max Length: {max_length_info[field_name]}\n"
                message += f"\t\t└ Description: {help_text_info[field_name]}\n\n"
            except:
                continue
        message += "────────────────────\n"
    message += "Diagnosis Ends ──────────\n"
    return HttpResponse(message)

def upload_file(request): # 파일 업로드
    try:
        upload = models.UPLOAD(
            file = request.FILES["file"]
        )
        upload.save()
        path = "/media/" + str(upload.file)
    except:
        path = "/static/_admoney/avatar/default.png"
    return JsonResponse({
        "path": path
    })