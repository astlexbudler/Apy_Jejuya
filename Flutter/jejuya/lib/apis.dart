import 'package:t29ndrbx/globals.dart'; // firebaseProjectId, appId, deviceToken, appVersion 변수는 globals.dart에 저장되어 있음
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:developer' as dev;

/*
apis.dart

setFireData(Map<String, dynamic> data)
  - firestore에 데이터 저장
  - firebaseProjectId > appId > deviceToken 경로에 데이터 저장
  - 경로가 없다면 생성 후 저장, 경로가 있다면 업데이트
  - 성공 여부는 반환하지 않음

getFireData()
  - firestore에서 데이터 가져오기
  - firebaseProjectId > appId > deviceToken 경로에서 데이터 가져오기
  - 데이터가 없다면 null 반환

compareStoreVersion(String platform)
  - 현재 앱 버전과 스토어 버전 비교
  - platform: android, ios
  - 같다면 true, 다르다면 false 반환. 에러 발생 시 null 반환

 */

// firestore에 데이터 저장
Future<void> setFireData() async {
  Map<String, dynamic> data = {
    'loginId': {'stringValue': userLoginId},
    'deviceToken': {'stringValue': userDeviceToken},
    'isPushAllow': {'booleanValue': isPushAllow},
    'isCommertialPushAllow': {'booleanValue': isCommertialPushAllow},
  };
  dev.log('setFireData: $data');
  await http.patch(
    Uri.parse(
        'https://firestore.googleapis.com/v1/projects/$firebaseProjectId/databases/(default)/documents/$appId/$userDeviceToken'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode({"fields": data}),
  );
}

// firestore에서 데이터 가져오기
Future<void> getFireData() async {
  try {
    final response = await http.get(
      Uri.parse(
          'https://firestore.googleapis.com/v1/projects/$firebaseProjectId/databases/(default)/documents/$appId/$userDeviceToken'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      dev.log('getFireData: $data');
      isCommertialPushAllow =
          data['fields']['isCommertialPushAllow']['booleanValue'];
      isPushAllow = data['fields']['isPushAllow']['booleanValue'];
      userLoginId = data['fields']['loginId']['stringValue'];
    }
  } catch (e) {
    dev.log('getFireData error: $e');
  }
}

// 현재 앱 버전과 스토어 버전 비교
Future<bool?> compareStoreVersion(String platform) async {
  try {
    if (platform == 'android') {
      final response = await http.get(
        Uri.parse(
          'https://play.google.com/store/apps/details?id=com.t29ndrbx.t29ndrbx',
        ),
      );
      if (response.statusCode == 200) {
        final html = response.body;
        final regex = RegExp(r'Current Version.+?>([\d.]+)<');
        final match = regex.firstMatch(html);
        if (match != null) {
          final playStoreVersion = match.group(1);
          return appVersion == playStoreVersion;
        }
      }
    } else if (platform == 'ios') {
      final response = await http.get(
        Uri.parse(
          'https://itunes.apple.com/lookup?bundleId=com.t29ndrbx.t29ndrbx',
        ),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['resultCount'] > 0) {
          final appStoreVersion = data['results'][0]['version'];
          return appVersion == appStoreVersion;
        }
      }
    }
  } catch (e) {
    return null;
  }
  return null;
}
