library my_app.globals;

// Firebase 연결 프로젝트 아이디
const String firebaseProjectId = "cixt7hh3u";

// 앱 아이디
const String appId = "t29ndrbx";

// 앱 이름
const String appName = "제주야";

// 앱 빌드 버전
const String appVersion = "24";

// 시스템 언어(KO, EN)
const String lang = "KO";

// 웹뷰 시작 페이지
String webviewStartPage = "https://jejuya.applifyapplications.com";

// 앱 메뉴 타입(navbar, floatingButton, none)
const String menuType = 'none';

// 외부 앱 연결 예외 경로
const externalApplicationException = [
  "about:blank",
  "https:www.facebook.com/v2.3/plugins",

  "https://jejuya.applifyapplications.com", // 웹뷰 페이지
];

// Javascript
const String generalJavascript = '''
 // 앱 정보 가져오기(packageName, version, firebaseProjectId)
  getAppInfo = async () => {
    return await window.flutter_inappwebview.callHandler('getAppInfo');
  }

  // 사용자 정보 가져오기(userDeviceToken, isPushAllow, isCommertialPushAllow)
  getUserInfo = async () => {
    return await window.flutter_inappwebview.callHandler('getUserInfo');
  }

  // eyoom 서비스 로그인 시 아이디와 토큰 연결
  const ffk3s01vr = document.getElementsByName("mb_id");
  if (ffk3s01vr.length > 0) {
    ffk3s01vr[0].addEventListener("change", function() {
      const mmo9soqz612c = ffk3s01vr[0].value;
      window.flutter_inappwebview.callHandler('eyoomRegisterId', mmo9soqz612c);
    });
  }
''';

// 필요 권한 리스트
const requiredPermissions = [
  'push',
  //'location',
  //'file',
];

// 글로벌 변수들
late String userDeviceToken;
late DateTime currentBackPressTime;
late String userAgent;
late String webviewErrorMessage;
late bool isPushAllow;
late bool isCommertialPushAllow;
String? userLoginId;
bool isLoading = false;
// main_screen, permission_ask_screen, setting_screen
String nowScreen = 'main_screen';
bool isInit = false;
