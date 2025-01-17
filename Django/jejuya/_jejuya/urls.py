from django.urls import path
from . import views as v
from . import apis as a
from . import orms as o



urlpatterns = [

    # v.py
    # 메인 페이지(기준점 검색(선택) 페이지)
    # 내 위치, 주소 검색, 호텔 또는 관광지 선택, 지도 위 위치 선택 등을 통해 기준점을 검색하는 페이지. 새로운 사용자 세션 확인 후 필요 시 새로운 사용자 세션 생성.
    path('', v.index, name='index'),
    # 기준점 검색 결과 페이지
    # 기준점 주변 관광지 검색, 카테고리 필터, 거리 필터(km). 관광지 핀 선택 시, 하단에 관광지 요약 카드 표시. 카드 클릭 시 관광지 상세 페이지 window.open으로 띄움.
    path('point_around', v.point_around, name='point_around'),
    # 내 일정 페이지
    # 펼치는 탭으로 일정 별 선택한 관광지를 보여주는 페이지. 관광지 클릭 시 관광지 상세 페이지 window.open으로 띄움. 관광지 삭제 기능. 일정에 지도 표시 기능. 날짜 변경 시, 일정 변경 확인 modal 띄움.
    path('schedule', v.schedule, name='schedule'),
    # 일정 지도 페이지
    # 일정에 추가한 관광지를 지도에 표시하는 페이지. 지도 위에 관광지 이름 표시. 관광지 클릭 시, 관광지 상세 페이지 window.open으로 띄움.
    path('schedule_map', v.schedule_map, name='schedule_map'),
    # 기준점 리스트 페이지
    # 기준점 리스트를 보여주는 페이지. 기준점 이름, 주소, 설명을 보여줌. 기준점 클릭 시, 기준점 검색 페이지로 이동.
    path('point_list', v.point_list, name='point_list'),
    # 관광지 리스트 페이지
    # 앱에 등록된 모든 관광지를 리스트로 보여주는 페이지. 관광지 이름, 주소, 설명을 보여줌. 관광지 클릭 시, 관광지 상세 페이지 window.open으로 띄움.
    path('around_list', v.around_list, name='around_list'),

    # 기타 페이지
    path('contact', v.contact, name='contact'), # Contact
    path('terms', v.terms, name='terms'), # Terms of Service

    # supervisor
    # 관리자 페이지
    # 사용자 관리 메뉴, 관광지 관리 메뉴, 푸시 발송 메뉴
    path('supervisor', v.supervisor, name='supervisor'), # supervisor main
    # 사용자 관리 페이지
    # 사용자 목록, 사용자 삭제 기능. 관리자 아이디 비밀번호 변경 기능. 관리자 등록 기능
    path('supervisor_accounts', v.supervisor_accounts, name='supervisor_accounts'), # supervisor account list
    # 관광지 관리 페이지
    # 관광지 목록, 관광지 등록 버튼, 관광지 삭제 기능
    path('supervisor_arounds', v.supervisor_arounds, name='supervisor_arounds'), # supervisor around list
    # 관광지 등록 페이지
    # 관광지 이름, 주소, 설명, 사진 등록, 티켓 구매 링크
    path('supervisor_around_write', v.supervisor_around_write, name='supervisor_around_write'), # supervisor around write
    # 기준점 관리 페이지
    # 기준점 목록, 기준점 등록 버튼, 기준점 삭제 기능
    path('supervisor_points', v.supervisor_points, name='supervisor_points'), # supervisor point list
    # 기준점 등록 페이지
    # 기준점 이름, 주소, 설명, 사진 등록
    path('supervisor_point_write', v.supervisor_point_write, name='supervisor_point_write'), # supervisor point write
    # 푸시 발송 페이지
    # 푸시 발송 기능. 제목, 내용 입력 후 발송 버튼 클릭 시, 모든 사용자에게 푸시 발송
    path('supervisor_push', v.supervisor_push, name='supervisor_push'), # supervisor push
    # 관리자 로그인 페이지
    path('supervisor_login', v.supervisor_login, name='supervisor_login'), # supervisor login

    # apis.py
    path('api/csv_points', a.csv_points, name='csv_points'), # csv_points API
    path('api/csv_arounds', a.csv_arounds, name='csv_arounds'), # csv_arounds API
    # 관리자 로그인 API
    # id, password를 받아 로그인 시도. 로그인 성공 시, 세션 생성. ip로 반복 시도 확인 후 로그인 제한
    path('api/login_supervisor', a.login_supervisor, name='login_supervisor'), # try supervisor login API
    # 관리자 로그아웃 API
    # session.flush() 및 request.logout()으로 로그아웃 및 모든 세션 삭제
    path('api/logout_account', a.logout_account, name='logout_account'), # logout API
    # 관리자 계정 생성 API
    # 현재 관리자로 로그인된 상태에서만 사용 가능. id, password를 받아 관리자 계정 생성. 만약 관리자 계정이 없을 경우, 최초 관리자 계정 생성
    path('api/write_supervisor', a.write_supervisor, name='write_supervisor'), # write supervisor API
    # 계정 삭제 API
    # 현재 관리자로 로그인된 상태에서만 사용 가능. id를 받아 해당 계정 삭제. 본인 계정은 삭제 불가.
    path('api/delete_account', a.delete_account, name='delete_account'), # delete account API
    # 관리자 비밀번호 변경 API
    # 현재 관리자로 로그인된 상태에서만 사용 가능. id, password를 받아 해당 계정의 비밀번호 덮어쓰기
    path('api/rewrite_password', a.rewrite_password, name='rewrite_password'), # rewrite password API
    # 아이디 중복 확인
    # id를 받아 해당 id가 이미 존재하는지 확인
    path('api/check_id', a.check_id, name='check_id'), # check id API
    # points 전부 삭제
    # 모든 points 삭제
    path('api/delete_all_points', a.delete_all_points, name='delete_all_points'), # delete all points API
    # arounds 전부 삭제
    # 모든 arounds 삭제
    path('api/delete_all_arounds', a.delete_all_arounds, name='delete_all_arounds'), # delete all arounds API



    # messaging
    # 푸시 발송 API
    # 제목과 내용을 받아 모든 사용자에게 푸시 발송(device token이 있는 모든 사용자에게 발송)
    path('api/send_apppush', a.send_apppush, name='send_apppush'), # send app push API

    # map
    # 주소->좌표 변환 API
    # 주소를 받아 좌표로 변환 후 반환
    path('api/address_to_coords', a.address_to_coords, name='address_to_coords'), # address to coords
    # 좌표->주소 변환 API
    # 좌표를 받아 주소로 변환 후 반환
    path('api/coords_to_address', a.coords_to_address, name='coords_to_address'), # coords to address
    # 거리 계산 API
    # 두 좌표를 받아 거리 계산 후 반환
    path('api/calc_distance', a.calc_distance, name='calc_distance'), # calc distance
    # 좌표 중앙값 계산 API
    # 여러 좌표를 받아 해당 좌표들의 중앙값 계산 후 반환
    path('api/calc_center', a.calc_center, name='calc_center'), # calc center

    # o.py
    path('orm/data', o.data, name='data'), # get/set/delete data RESTFUL API
    path('orm/upload_file', o.upload_file, name='upload_file'), # upload file and return file path API

]