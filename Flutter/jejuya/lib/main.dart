import 'dart:io';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:splash_view/splash_view.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'firebase_options.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:convert';
import 'dart:developer' as dev;

import 'package:t29ndrbx/globals.dart';
import 'package:t29ndrbx/apis.dart';

void main() async {
  // 앱 초기화
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
      name: firebaseProjectId, options: DefaultFirebaseOptions.currentPlatform);

  // 앱 실향 즁 퓨사 얼람 슈산 솔종(안드로이드만 작동)
  FirebaseMessaging.onMessage.listen((RemoteMessage message) async {
    FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
        FlutterLocalNotificationsPlugin();
    var android =
        const AndroidInitializationSettings('@drawable/ic_notification');
    var ios = const DarwinInitializationSettings();
    var settings = InitializationSettings(android: android, iOS: ios);
    flutterLocalNotificationsPlugin.initialize(settings);
    var androidPlatformChannelSpacifics = const AndroidNotificationDetails(
      "AppToasterChannelId",
      "AppToasterChannelName",
      importance: Importance.max,
      priority: Priority.high,
    );
    var iOSPlatformChannelSpecifics = const DarwinNotificationDetails();
    var platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpacifics,
      iOS: iOSPlatformChannelSpecifics,
    );
    await flutterLocalNotificationsPlugin.show(
      0,
      message.notification!.title,
      message.notification!.body,
      platformChannelSpecifics,
      payload: 'Default_Sound',
    );
  });

  // 푸시 알림을 통해서 앱을 실행할 경우
  FirebaseMessaging.instance.getInitialMessage().then((RemoteMessage? message) {
    String? url = message?.data['url']; // 메세지에 url이 있는 경우
    if (url != null) {
      webviewStartPage = url; // 시작 페이지를 url로 설정
    }
  });

  runApp(
    const SplashScreen(),
  );
}

// 스플레시 화면
// 필요한 경우 스플레시 화면 설정(기본값: 흰색 배경, 로딩 인디케이터)
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: appName,
      theme:
          ThemeData(fontFamily: 'my_font'), // pubspect.yaml에서 시스템 폰트 설정 변경 가능
      home: SplashView(
        showStatusBar: true,
        backgroundColor: const Color.fromRGBO(255, 255, 255, 1),
        loadingIndicator: const Padding(
          padding: EdgeInsets.only(bottom: 60.0),
          child: CircularProgressIndicator(
              color: Color.fromARGB(255, 225, 225, 225)),
        ),
        duration: const Duration(seconds: 1), // 스플레시 화면 지속 시간
        bottomLoading: true,
        done: Done(
          const ScaffoldMessenger(
            child: App(),
          ),
          animationDuration: const Duration(
            milliseconds: 10,
          ),
        ),
      ),
    );
  }
}

class App extends StatefulWidget {
  const App({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  final GlobalKey inAppWebViewKey = GlobalKey();
  late InAppWebViewController inAppWebViewController;
  late InAppWebViewController subInAppWebViewController;
  static const channel = MethodChannel('fcm_default_channel');
  FirebaseFirestore firestore = FirebaseFirestore.instance;

  @override
  void initState() {
    super.initState();

    userAgent = Platform.isAndroid
        ? "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/294.0.0.39.118;]"
        : "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1";
    currentBackPressTime = DateTime.now();

    // 푸시 알림을 총해 앱이 다시 활성화된 경우(백그라운드에서 포그라운드로 전환된 경우)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      String? url = message.data['url']; // 메세지에 url이 있는 경우
      if (url != null) {
        // url로 이동
        inAppWebViewController.loadUrl(
          urlRequest: URLRequest(url: WebUri(url)),
        );
      }
    });
  }

  // 앱 최초 실행 시, 사용자 정보 생성 및 권한 요청 화면으로 이동
  Future<void> initializeUser() async {
    if (requiredPermissions.contains('push')) {
      // FirebaseMessaging 권한 요청(푸시 알림 수신 허용)
      await FirebaseMessaging.instance.requestPermission().then((value) {
        if (value.authorizationStatus == AuthorizationStatus.authorized) {
          isPushAllow = true;
        } else {
          isPushAllow = false;
        }
      });
    } else {
      isPushAllow = false;
    }
    // userDeviceToken 확인, 확인할 수 없다면, 빈 문자열로 설정
    userDeviceToken = (await FirebaseMessaging.instance.getToken()) ?? '';
    // Firestore에 저장된 사용자 정보 가져오기
    await getFireData();

    if (userLoginId == null) {
      // 처음 앱을 실행한 경우
      isCommertialPushAllow = false;
      userLoginId = '';
      // Firestore에 초기 데이터 저장
      await setFireData();
      setState(() => nowScreen = "permission_ask_screen"); // 권한 요청 화면으로 이동
    } else {
      // TEST
      setState(() => nowScreen = "permission_ask_screen"); // 권한 요청 화면으로 이동
    }
  }

  Future<void> goForward() async {
    // 화면이 아직 로딩 중인 경우, 앞으로가기 방지
    if (isLoading) {
      return;
    }

    if (await inAppWebViewController.canGoForward()) {
      // 앞으로갈 수 있는 경우, 웹뷰 앞으로가기
      inAppWebViewController.goForward();
    } else {
      // 앞으로갈 수 없는 경우, 메시지 출력
      // 언어에 따라 다른 메시지 출력
      if (lang == "KO") {
        // 한국어
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('앞으로 갈 수 있는 페이지가 없습니다.'),
            duration: Duration(seconds: 1),
          ),
        );
      } else if (lang == "EN") {
        // 영어
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('There is no page to go forward.'),
            duration: Duration(seconds: 1),
          ),
        );
      }
    }
    return;
  }

  // 뒤로가기 이벤트 처리
  Future<void> goBack() async {
    // 화면이 아직 로딩 중인 경우, 뒤로가기 방지
    if (isLoading) {
      return;
    }

    // 스크린 제어
    if (nowScreen == 'setting_screen' || nowScreen == 'permission_ask_screen') {
      // 설정 화면 또는 권한 요청 화면에서 뒤로가기 버튼을 누른 경우, 메인 화면으로 이동
      setState(() => nowScreen = 'main_screen');
      return;
    }

    if (await inAppWebViewController.canGoBack()) {
      // 뒤로갈 수 있는 경우, 웹뷰 뒤로가기
      await inAppWebViewController.goBack();
    } else {
      if (DateTime.now().difference(currentBackPressTime) <
          const Duration(seconds: 3)) {
        // 뒤로갈 수 있는 페이지가 없고, 뒤로가기를 누른지 3초 이내인 경우 앱 종료
        if (Platform.isAndroid) {
          SystemNavigator.pop();
        } else {
          exit(0);
        }
      } else {
        // 뒤로갈 수 있는 페이지가 없고, 뒤로가기를 누른지 3초 이상인 경우, 앱 종료 메세지 표시
        currentBackPressTime = DateTime.now();

        // 언어에 따라 다른 메시지 출력
        if (lang == "KO") {
          // 한국어
          // ignore: use_build_context_synchronously
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('뒤로가기 버튼을 한번 더 누르시면 종료됩니다.'),
              duration: Duration(seconds: 1),
            ),
          );
        } else if (lang == "EN") {
          // 영어
          // ignore: use_build_context_synchronously
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Press the back button again to exit.'),
              duration: Duration(seconds: 1),
            ),
          );
        }
      }
    }
    return;
  }

  Future<Position> _getUserLocation() async {
    return await Geolocator.getCurrentPosition();
  }

  @override
  Widget build(BuildContext context) {
    if (!isInit) {
      // 앱 실행 후 1번만 실행
      isInit = true;
      initializeUser();
    }

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        goBack();
      },
      child: Scaffold(
        appBar: AppBar(
          // 상단바: 없음
          toolbarHeight: 0,
          backgroundColor: Colors.black,
          bottom: const PreferredSize(
            preferredSize: Size.fromHeight(0),
            child: SafeArea(
              bottom: false,
              child: SizedBox(),
            ),
          ),
        ),
        body: LayoutBuilder(
          // 화면 레이아웃
          builder: (BuildContext buildContext, BoxConstraints boxConstraints) {
            final bodyWidth = boxConstraints.maxWidth;
            final bodyHeight = boxConstraints.maxHeight;
            return Stack(
              children: [
                InAppWebView(
                  // 웹뷰화면
                  key: inAppWebViewKey,
                  initialUrlRequest: URLRequest(
                    // 시작 페이지
                    url: WebUri(webviewStartPage),
                  ),
                  initialSettings: InAppWebViewSettings(
                    userAgent: userAgent,
                    useShouldOverrideUrlLoading: true,
                    useShouldInterceptRequest: true,
                    javaScriptEnabled: true,
                    javaScriptCanOpenWindowsAutomatically: true,
                    supportMultipleWindows: true,
                    useOnDownloadStart: true,
                    useHybridComposition: true,
                    allowsInlineMediaPlayback: true,
                  ),
                  onWebViewCreated: (controller) {
                    inAppWebViewController = controller;

                    // Javascript Handlers
                    /*
                    아래 핸들러를 JavaScript로 호출하여, 앱 정보 및 사용자 정보를 가져올 수 있습니다.
                    [예시]
                    1. 플러터 앱이 준비되었는지 확인
                    var isAppReady = false;
                    window.addEventListener("flutterInAppWebViewPlatformReady", function (event) {
                        isAppReady = true;
                    });
                    2. 이밴트 핸들러 호출
                    window.flutter_inappwebview.callHandler(
                      handlerName, args
                    ).then((result) => {
                      console.log(result);
                    });
                     */
                    // getAppInfo: 앱 정보 가져오기(packageName, version, firebaseProjectId)
                    inAppWebViewController.addJavaScriptHandler(
                      handlerName: 'getAppInfo',
                      callback: (args) async {
                        return {
                          'packageName': 'com.appwizard.$appId',
                          'version': appVersion,
                          'firebaseProjectId': firebaseProjectId,
                        };
                      },
                    );
                    // getUserInfo: 사용자 정보 가져오기(userDeviceToken, isPushAllow, isCommertialPushAllow)
                    inAppWebViewController.addJavaScriptHandler(
                      handlerName: 'getAppInfo',
                      callback: (args) async {
                        return {
                          'userDeviceToken': userDeviceToken,
                          'isPushAllow': isPushAllow,
                          'isCommertialPushAllow': isCommertialPushAllow,
                        };
                      },
                    );
                    // eyoomRegisterId: eyoom 서비스 로그인 시 아이디와 토큰 연결
                    inAppWebViewController.addJavaScriptHandler(
                      handlerName: 'eyoomRegisterId',
                      callback: (args) async {
                        userLoginId = args[0];
                        await setFireData();
                        return;
                      },
                    );
                    // setLoginId: 로그인 시 아이디 저장
                    inAppWebViewController.addJavaScriptHandler(
                      handlerName: 'setLoginId',
                      callback: (args) async {
                        userLoginId = args[0];
                        await setFireData();
                        return;
                      },
                    );
                    /*
                    inAppWebViewController.addJavaScriptHandler(
                      handlerName: 'getLocation',
                      callback: (args) async {
                        // 위치 정보 요청
                        Position position = await _getUserLocation();
                        dev.log(
                            'Location: ${position.latitude}, ${position.longitude}');
                        return jsonEncode({
                          'latitude': position.latitude,
                          'longitude': position.longitude,
                        });
                      },
                    );*/
                  },
                  onCreateWindow: (controller, createWindowAction) async {
                    // Multiple Window 처리(팝업 처리) 최대 1개까지만 가능
                    showDialog(
                      context: context,
                      builder: (context) {
                        return AlertDialog(
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(0)),
                          contentPadding: EdgeInsets.zero,
                          content: SizedBox(
                            width: MediaQuery.of(context).size.width,
                            height: MediaQuery.of(context).size.height,
                            child: InAppWebView(
                              windowId: createWindowAction.windowId,
                              onWebViewCreated:
                                  (InAppWebViewController controller) =>
                                      subInAppWebViewController = controller,
                            ),
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.of(context).pop(),
                              child: const Text(
                                // 닫기 버튼. 언어에 따라 다른 메시지 출력
                                lang == "KO"
                                    ? "닫기"
                                    : lang == "EN"
                                        ? "Close"
                                        : "",
                                style: TextStyle(color: Colors.grey),
                              ),
                            ),
                          ],
                        );
                      },
                    );
                    return true;
                  },
                  shouldOverrideUrlLoading:
                      (controller, navigationAction) async {
                    // URL Override 처리
                    var url = navigationAction.request.url;

                    // 제주야 요청사항(travelbox.vpass.co.kr)은 외부 브라우저로 열기
                    if (url
                        .toString()
                        .startsWith('https://travelbox.vpass.co.kr/')) {
                      // 외부 브라우저로 열기
                      launchUrlString(
                        url.toString(),
                        mode: LaunchMode.externalApplication,
                      );
                      return NavigationActionPolicy.CANCEL;
                    }

                    // 외부 앱 연결 예외 경로 처리
                    for (var e in externalApplicationException) {
                      if (url.toString().startsWith(e)) {
                        // 욉부 앱 연결 예외 경로인 경우, 웹뷰 내 로딩 허용
                        return NavigationActionPolicy.ALLOW;
                      }
                    }

                    // 앱 스키마 처리
                    if (!url.toString().startsWith('http')) {
                      if (Platform.isIOS) {
                        // iOS 앱 스키마 처리
                        if (await canLaunchUrlString(url.toString())) {
                          await launchUrlString(url.toString());
                        } else {
                          // 앱이 설치되어 있지 않은 경우,
                          // ignore: use_build_context_synchronously
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(lang == "KO"
                                  ? "필요한 앱이 설치되어 있지 않습니다."
                                  : lang == "EN"
                                      ? "The required app is not installed."
                                      : ""),
                              duration: Duration(seconds: 1),
                            ),
                          );
                        }
                      } else {
                        // Android 앱 스키마 처리
                        await channel
                            .invokeMethod('getAppUrl', <String, Object>{
                          'url': url.toString(),
                        }).then((value) async {
                          if (await canLaunchUrlString(value)) {
                            // 앱이 설치되어 있는 경우
                            await launchUrlString(value);
                          } else {
                            // 앱이 설치되어 있지 않은 경우, 플레이스토어로 이동
                            String appId = url.toString().substring(
                                  url.toString().indexOf("package=") + 8,
                                  url.toString().length,
                                );
                            appId = appId.substring(0, appId.indexOf(";"));
                            launchUrlString("market://details?id=$appId");
                          }
                        });
                      }
                    }

                    // 앱 스키마 주소가 아니면서, 외부 앱 실행 주소가 아닌 경우, 웹뷰 내 로딩 허용
                    return NavigationActionPolicy.ALLOW;
                  },
                  onLoadStart: (controller, url) {
                    setState(() => isLoading = true);
                  },
                  onLoadStop: (controller, url) {
                    setState(() => isLoading = false);

                    // 앱 자바스크립트 설정
                    inAppWebViewController.evaluateJavascript(
                        source: generalJavascript);
                  },
                  onReceivedError: (controller, request, message) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(message.toString()),
                        duration: const Duration(seconds: 3),
                      ),
                    );
                    // 리다이렉션 중단 및 뒤로가기
                    inAppWebViewController.goBack();
                  },
                ),
                // 스크린들
                nowScreen == "permission_ask_screen" // 권한 요청 화면(최초 실행 시)
                    ? SizedBox(
                        width: bodyWidth,
                        height: bodyHeight,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Container(
                              // 상단바
                              height: 60,
                              color: const Color.fromARGB(255, 100, 100, 100),
                              padding:
                                  const EdgeInsets.symmetric(vertical: 5.0),
                              child: Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Padding(
                                    padding: EdgeInsets.only(left: 20.0),
                                    child: Text(
                                      // 상단 제목. 언어에 따라 다른 메시지 출력
                                      lang == "KO"
                                          ? "권한"
                                          : lang == "EN"
                                              ? "Permission"
                                              : "",
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 20.0,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  IconButton(
                                    // 닫기 버튼
                                    icon: const Icon(
                                      Icons.close,
                                      color: Colors.white,
                                    ),
                                    onPressed: () => goBack(),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              // 본문
                              height: bodyHeight - 60,
                              color: const Color.fromARGB(255, 245, 245, 245),
                              child: SingleChildScrollView(
                                // 스크롤 가능한 본문
                                scrollDirection: Axis.vertical,
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const SizedBox(height: 10),
                                    const SizedBox(
                                      // 본문 제목
                                      height: 40,
                                      child: Padding(
                                        padding: EdgeInsets.all(10.0),
                                        child: Text(
                                          // 언어에 따라 다른 메시지 출력
                                          lang == "KO"
                                              ? "앱 이용을 위해 다음 접근권한이 필요합니다."
                                              : lang == "EN"
                                                  ? "The following permissions are required to use the app."
                                                  : "",
                                          style: TextStyle(
                                            fontSize: 12.0,
                                            color: Color.fromARGB(
                                                255, 100, 100, 100),
                                          ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(
                                      height: 40,
                                      child: Padding(
                                        padding: EdgeInsets.all(10.0),
                                        child: Text(
                                          // 언어에 따라 다른 메시지 출력
                                          lang == "KO"
                                              ? "필수"
                                              : lang == "EN"
                                                  ? "Required"
                                                  : "",
                                          style: TextStyle(
                                            fontSize: 14.0,
                                            color: Color.fromARGB(
                                                255, 100, 100, 100),
                                          ),
                                        ),
                                      ),
                                    ),
                                    Container(
                                      width: double.infinity,
                                      decoration: const BoxDecoration(
                                        border: Border(
                                          top: BorderSide(
                                            color: Color.fromARGB(
                                                255, 200, 200, 200),
                                            width: 1.0,
                                            style: BorderStyle.solid,
                                          ),
                                          bottom: BorderSide(
                                            color: Color.fromARGB(
                                                255, 200, 200, 200),
                                            width: 1.0,
                                            style: BorderStyle.solid,
                                          ),
                                        ),
                                        color: Colors.white,
                                      ),
                                      child: const Row(
                                        children: [
                                          Padding(
                                            padding: EdgeInsets.fromLTRB(
                                                18, 18, 0, 18),
                                            child: Icon(Icons.badge),
                                          ),
                                          Padding(
                                            padding: EdgeInsets.all(18.0),
                                            child: Text(
                                              // 언어에 따라 다른 메시지 출력
                                              lang == "KO"
                                                  ? "기기ID"
                                                  : lang == "EN"
                                                      ? "Device ID"
                                                      : "",
                                              style: TextStyle(
                                                fontSize: 14.0,
                                                color: Colors.black,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    const SizedBox(height: 10),
                                    const SizedBox(
                                      height: 40,
                                      child: Padding(
                                        padding: EdgeInsets.all(10.0),
                                        child: Text(
                                          // 언어에 따라 다른 메시지 출력
                                          lang == "KO"
                                              ? "선택"
                                              : lang == "EN"
                                                  ? "Optional"
                                                  : "",
                                          style: TextStyle(
                                            fontSize: 14.0,
                                            color: Color.fromARGB(
                                                255, 100, 100, 100),
                                          ),
                                        ),
                                      ),
                                    ),
                                    Container(
                                      width: double.infinity,
                                      decoration: const BoxDecoration(
                                        border: Border(
                                          top: BorderSide(
                                            color: Color.fromARGB(
                                                255, 200, 200, 200),
                                            width: 1.0,
                                            style: BorderStyle.solid,
                                          ),
                                          bottom: BorderSide(
                                            color: Color.fromARGB(
                                                255, 200, 200, 200),
                                            width: 1.0,
                                            style: BorderStyle.solid,
                                          ),
                                        ),
                                        color: Colors.white,
                                      ),
                                      child: Column(
                                        children: [
                                          requiredPermissions
                                                  .contains('location')
                                              ? Container(
                                                  width: double.infinity,
                                                  decoration:
                                                      const BoxDecoration(
                                                    border: Border(
                                                      bottom: BorderSide(
                                                        color: Color.fromARGB(
                                                            255, 200, 200, 200),
                                                        width: 1.0,
                                                        style:
                                                            BorderStyle.solid,
                                                      ),
                                                    ),
                                                    color: Colors.white,
                                                  ),
                                                  child: const Column(
                                                    children: [
                                                      Row(
                                                        children: [
                                                          Padding(
                                                            padding: EdgeInsets
                                                                .fromLTRB(18,
                                                                    18, 0, 0),
                                                            child: Icon(Icons
                                                                .location_on),
                                                          ),
                                                          Padding(
                                                            padding: EdgeInsets
                                                                .fromLTRB(18,
                                                                    18, 18, 0),
                                                            child: Text(
                                                              // 언어에 따라 다른 메시지 출력
                                                              lang == "KO"
                                                                  ? "위치"
                                                                  : lang == "EN"
                                                                      ? "Location"
                                                                      : "",
                                                              style: TextStyle(
                                                                fontSize: 14.0,
                                                                color: Colors
                                                                    .black,
                                                              ),
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                      Row(
                                                        children: [
                                                          Padding(
                                                            padding:
                                                                EdgeInsets.all(
                                                                    16.0),
                                                            child: Text(
                                                              // 언어에 따라 다른 메시지 출력
                                                              lang == "KO"
                                                                  ? "현재 위치 정보를 확인하기 위한 위치 접근"
                                                                  : lang == "EN"
                                                                      ? "Access to location to check current location information"
                                                                      : "",
                                                              style: TextStyle(
                                                                color: Color
                                                                    .fromARGB(
                                                                        255,
                                                                        130,
                                                                        130,
                                                                        130),
                                                                fontSize: 14.0,
                                                              ),
                                                            ),
                                                          ),
                                                        ],
                                                      )
                                                    ],
                                                  ),
                                                )
                                              : const SizedBox(),
                                          requiredPermissions.contains('file')
                                              ? Container(
                                                  width: double.infinity,
                                                  decoration:
                                                      const BoxDecoration(
                                                    border: Border(
                                                      bottom: BorderSide(
                                                        color: Color.fromARGB(
                                                            255, 200, 200, 200),
                                                        width: 1.0,
                                                        style:
                                                            BorderStyle.solid,
                                                      ),
                                                    ),
                                                    color: Colors.white,
                                                  ),
                                                  child: const Column(
                                                    children: [
                                                      Row(
                                                        children: [
                                                          Padding(
                                                            padding: EdgeInsets
                                                                .fromLTRB(18,
                                                                    18, 0, 0),
                                                            child: Icon(
                                                                Icons.storage),
                                                          ),
                                                          Padding(
                                                            padding: EdgeInsets
                                                                .fromLTRB(18,
                                                                    18, 18, 0),
                                                            child: Text(
                                                              // 언어에 따라 다른 메시지 출력
                                                              lang == "KO"
                                                                  ? "저장소"
                                                                  : lang == "EN"
                                                                      ? "Storage"
                                                                      : "",
                                                              style: TextStyle(
                                                                fontSize: 14.0,
                                                                color: Colors
                                                                    .black,
                                                              ),
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                      Row(
                                                        children: [
                                                          Padding(
                                                            padding:
                                                                EdgeInsets.all(
                                                                    16.0),
                                                            child: Text(
                                                              // 언어에 따라 다른 메시지 출력
                                                              lang == "KO"
                                                                  ? "파일 업로드를 위한 저장소 접근"
                                                                  : lang == "EN"
                                                                      ? "Access to storage for file upload"
                                                                      : "",
                                                              style: TextStyle(
                                                                color: Color
                                                                    .fromARGB(
                                                                        255,
                                                                        130,
                                                                        130,
                                                                        130),
                                                                fontSize: 14.0,
                                                              ),
                                                            ),
                                                          ),
                                                        ],
                                                      )
                                                    ],
                                                  ),
                                                )
                                              : const SizedBox(),
                                          requiredPermissions.contains('file')
                                              ? Container(
                                                  width: double.infinity,
                                                  decoration:
                                                      const BoxDecoration(
                                                    border: Border(
                                                      bottom: BorderSide(
                                                        color: Color.fromARGB(
                                                            255, 200, 200, 200),
                                                        width: 1.0,
                                                        style:
                                                            BorderStyle.solid,
                                                      ),
                                                    ),
                                                    color: Colors.white,
                                                  ),
                                                  child: const Column(
                                                    children: [
                                                      Row(
                                                        children: [
                                                          Padding(
                                                            padding: EdgeInsets
                                                                .fromLTRB(18,
                                                                    18, 0, 0),
                                                            child: Icon(
                                                                Icons.camera),
                                                          ),
                                                          Padding(
                                                            padding: EdgeInsets
                                                                .fromLTRB(18,
                                                                    18, 18, 0),
                                                            child: Text(
                                                              // 언어에 따라 다른 메시지 출력
                                                              lang == "KO"
                                                                  ? "카메라"
                                                                  : lang == "EN"
                                                                      ? "Camera"
                                                                      : "",
                                                              style: TextStyle(
                                                                fontSize: 14.0,
                                                                color: Colors
                                                                    .black,
                                                              ),
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                      Row(
                                                        children: [
                                                          Padding(
                                                            padding:
                                                                EdgeInsets.all(
                                                                    16.0),
                                                            child: Text(
                                                              // 언어에 따라 다른 메시지 출력
                                                              lang == "KO"
                                                                  ? "사진 촬영을 위한 카메라 접근"
                                                                  : lang == "EN"
                                                                      ? "Access to camera for taking pictures"
                                                                      : "",
                                                              style: TextStyle(
                                                                color: Color
                                                                    .fromARGB(
                                                                        255,
                                                                        130,
                                                                        130,
                                                                        130),
                                                                fontSize: 14.0,
                                                              ),
                                                            ),
                                                          ),
                                                        ],
                                                      )
                                                    ],
                                                  ),
                                                )
                                              : const SizedBox(),
                                          requiredPermissions.contains('push')
                                              ? const Row(
                                                  children: [
                                                    Padding(
                                                      padding:
                                                          EdgeInsets.fromLTRB(
                                                              18, 18, 0, 0),
                                                      child:
                                                          Icon(Icons.campaign),
                                                    ),
                                                    Padding(
                                                      padding:
                                                          EdgeInsets.fromLTRB(
                                                              18, 18, 18, 0),
                                                      child: Text(
                                                        // 언어에 따라 다른 메시지 출력
                                                        lang == "KO"
                                                            ? "광고성 푸시알림 수신"
                                                            : lang == "EN"
                                                                ? "Receive commercial push notifications"
                                                                : "",
                                                        style: TextStyle(
                                                          fontSize: 14.0,
                                                          color: Colors.black,
                                                        ),
                                                      ),
                                                    ),
                                                  ],
                                                )
                                              : const SizedBox(),
                                          requiredPermissions.contains('push')
                                              ? CheckboxListTile(
                                                  title: const Text(
                                                    // 언어에 따라 다른 메시지 출력
                                                    lang == "KO"
                                                        ? '이벤트, 홍보성 소식을 푸시 알림으로 받아보세요.'
                                                        : 'Receive event and promotional news as push notifications.',
                                                    style: TextStyle(
                                                      color: Color.fromARGB(
                                                          255, 130, 130, 130),
                                                      fontSize: 14.0,
                                                    ),
                                                  ),
                                                  value: isCommertialPushAllow,
                                                  onChanged: (value) async {
                                                    // 광고성 푸시알림 수신 체크박스
                                                    setState(() =>
                                                        isCommertialPushAllow =
                                                            value!);
                                                    await setFireData();
                                                  },
                                                )
                                              : const SizedBox(),
                                        ],
                                      ),
                                    ),
                                    const Row(
                                      children: [
                                        Padding(
                                          padding: EdgeInsets.all(18.0),
                                          child: Text(
                                            // 언어에 따라 다른 메시지 출력
                                            lang == "KO"
                                                ? "* 선택 권한 이용 시 별도의 허용이 필요하며,\n  거부 시 서비스 이용이 제한될 수 있습니다."
                                                : lang == "EN"
                                                    ? "* Separate permission is required for optional permissions,\n  and service usage may be restricted if denied."
                                                    : "",
                                            style: TextStyle(
                                              fontSize: 12.0,
                                              color: Color.fromARGB(
                                                  255, 100, 100, 100),
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                    const Row(
                                      children: [
                                        Padding(
                                          padding:
                                              EdgeInsets.fromLTRB(8, 0, 18, 18),
                                          child: Text(
                                            // 언어에 따라 다른 메시지 출력
                                            lang == "KO"
                                                ? "* 권한 설정은 '설정 > 앱'에서 변경하실 수 있습니다."
                                                : lang == "EN"
                                                    ? "* Permissions can be changed in 'Settings > Apps'."
                                                    : "",
                                            style: TextStyle(
                                              fontSize: 12.0,
                                              color: Color.fromARGB(
                                                  255, 100, 100, 100),
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.end,
                                      children: [
                                        Padding(
                                          padding: const EdgeInsets.all(18.0),
                                          child: ElevatedButton(
                                            onPressed: () => goBack(),
                                            style: ElevatedButton.styleFrom(
                                                backgroundColor: Colors.grey),
                                            child: const Text(
                                              // 확인 버튼. 언어에 따라 다른 메시지 출력
                                              lang == "KO"
                                                  ? "확인"
                                                  : lang == "EN"
                                                      ? "Confirm"
                                                      : "",
                                              style: TextStyle(
                                                fontSize: 14.0,
                                                color: Colors.white,
                                              ),
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      )
                    : const SizedBox(),
                nowScreen == "setting_screen" // 설정 화면
                    ? SizedBox(
                        width: bodyWidth,
                        height: bodyHeight,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Container(
                              // 상단바
                              height: 60,
                              color: const Color.fromARGB(255, 100, 100, 100),
                              padding:
                                  const EdgeInsets.symmetric(vertical: 5.0),
                              child: Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Padding(
                                    // 상단 제목
                                    padding: EdgeInsets.only(left: 20.0),
                                    child: Text(
                                      // 상단 제목. 언어에 따라 다른 메시지 출력
                                      lang == "KO"
                                          ? '설정'
                                          : lang == "EN"
                                              ? 'Setting'
                                              : '',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 20.0,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  IconButton(
                                    // 뒤로가기 버튼
                                    icon: const Icon(
                                      Icons.close,
                                      color: Colors.white,
                                    ),
                                    onPressed: () => goBack(),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              height: bodyHeight - 60,
                              color: const Color.fromARGB(255, 245, 245, 245),
                              child: SingleChildScrollView(
                                scrollDirection: Axis.vertical,
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    GestureDetector(
                                      // 브라우저로 열기
                                      onTap: () async {
                                        var url = await inAppWebViewController
                                            .getUrl();
                                        Uri? currentUrl = url;
                                        launchUrlString(
                                          currentUrl.toString(),
                                          mode: LaunchMode.externalApplication,
                                        );
                                      },
                                      child: Container(
                                        width: double.infinity,
                                        decoration: const BoxDecoration(
                                          border: Border(
                                            top: BorderSide(
                                              color: Color.fromARGB(
                                                  255, 200, 200, 200),
                                              width: 1.0,
                                              style: BorderStyle.solid,
                                            ),
                                            bottom: BorderSide(
                                              color: Color.fromARGB(
                                                  255, 200, 200, 200),
                                              width: 1.0,
                                              style: BorderStyle.solid,
                                            ),
                                          ),
                                          color: Colors.white,
                                        ),
                                        child: const Padding(
                                          padding: EdgeInsets.all(18.0),
                                          child: Text(
                                            // 언어에 따라 다른 메시지 출력
                                            lang == "KO"
                                                ? "브라우저로 열기"
                                                : lang == "EN"
                                                    ? "Open in browser"
                                                    : "",
                                            style: TextStyle(
                                              fontSize: 14.0,
                                              color: Colors.black,
                                            ),
                                          ),
                                        ),
                                      ),
                                    ),
                                    requiredPermissions
                                            .contains('push') // 푸시 알림 수신 설명 메뉴
                                        ? const SizedBox(
                                            height: 40,
                                            child: Padding(
                                              padding: EdgeInsets.all(10.0),
                                              child: Text(
                                                // 언어에 따라 다른 메시지 출력
                                                lang == "KO"
                                                    ? "푸시 알림 허용"
                                                    : lang == "EN"
                                                        ? "Push Notification Allow"
                                                        : "",
                                                style: TextStyle(
                                                  fontSize: 14.0,
                                                  color: Color.fromARGB(
                                                      255, 100, 100, 100),
                                                ),
                                              ),
                                            ),
                                          )
                                        : const SizedBox(),
                                    requiredPermissions
                                            .contains('push') // 푸시 알림 수신 설명 메뉴
                                        ? Container(
                                            width: double.infinity,
                                            decoration: const BoxDecoration(
                                              border: Border(
                                                top: BorderSide(
                                                  color: Color.fromARGB(
                                                      255, 200, 200, 200),
                                                  width: 1.0,
                                                  style: BorderStyle.solid,
                                                ),
                                              ),
                                              color: Colors.white,
                                            ),
                                            child: const Row(
                                              children: [
                                                Padding(
                                                  padding: EdgeInsets.fromLTRB(
                                                      18, 18, 0, 0),
                                                  child:
                                                      Icon(Icons.notifications),
                                                ),
                                                Padding(
                                                  padding: EdgeInsets.fromLTRB(
                                                      18, 18, 18, 0),
                                                  child: Text(
                                                    // 언어에 따라 다른 메시지 출력
                                                    lang == "KO"
                                                        ? "푸시 알림 수신"
                                                        : "Receive Push Notifications",
                                                    style: TextStyle(
                                                      fontSize: 14.0,
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          )
                                        : const SizedBox(),
                                    requiredPermissions
                                            .contains('push') // 푸시 알림 수신 설명 메뉴
                                        ? Container(
                                            // 일반 푸시 알림 수신 체크박스
                                            decoration: const BoxDecoration(
                                              color: Colors.white,
                                              border: Border(
                                                bottom: BorderSide(
                                                  color: Color.fromARGB(
                                                      255, 200, 200, 200),
                                                ),
                                              ),
                                            ),
                                            child: CheckboxListTile(
                                              title: const Text(
                                                // 언어에 따라 다른 메시지 출력
                                                lang == "KO"
                                                    ? "일반 푸시 알림 수신"
                                                    : "Receive General Push Notifications",
                                                style: TextStyle(
                                                  fontSize: 14.0,
                                                ),
                                              ),
                                              value: isPushAllow,
                                              onChanged: (value) async {
                                                if (!value!) {
                                                  isCommertialPushAllow = false;
                                                }
                                                setState(
                                                    () => isPushAllow = value);
                                                await setFireData();
                                                if (isPushAllow) {
                                                  await FirebaseMessaging
                                                      .instance
                                                      .requestPermission()
                                                      .then(
                                                    (value) {
                                                      if (value
                                                              .authorizationStatus
                                                              .toString() !=
                                                          "AuthorizationStatus.authorized") {
                                                        openAppSettings();
                                                      }
                                                    },
                                                  );
                                                }
                                              },
                                            ),
                                          )
                                        : const SizedBox(),
                                    requiredPermissions
                                            .contains('push') // 푸시 알림 수신 설명 메뉴
                                        ? Container(
                                            decoration: const BoxDecoration(
                                                color: Colors.white),
                                            child: const Row(
                                              children: [
                                                Padding(
                                                  padding: EdgeInsets.fromLTRB(
                                                      18, 18, 0, 0),
                                                  child: Icon(Icons.campaign),
                                                ),
                                                Padding(
                                                  padding: EdgeInsets.fromLTRB(
                                                      18, 18, 18, 0),
                                                  child: Text(
                                                    // 언어에 따라 다른 메시지 출력
                                                    lang == "KO"
                                                        ? "광고성 푸시 알림 수신"
                                                        : lang == "EN"
                                                            ? "Receive Commercial Push Notifications"
                                                            : "",
                                                    style: TextStyle(
                                                      fontSize: 14.0,
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          )
                                        : const SizedBox(),
                                    requiredPermissions
                                            .contains('push') // 푸시 알림 수신 설명 메뉴
                                        ? Container(
                                            // 광고성 푸시 알림 수신 체크박스
                                            decoration: const BoxDecoration(
                                              border: Border(
                                                bottom: BorderSide(
                                                  color: Color.fromRGBO(
                                                      200, 200, 200, 1),
                                                ),
                                              ),
                                              color: Colors.white,
                                            ),
                                            child: CheckboxListTile(
                                              title: const Text(
                                                // 언어에 따라 다른 메시지 출력
                                                lang == "KO"
                                                    ? '이벤트, 홍보성 소식을 푸시 알림으로 받아보세요.'
                                                    : lang == "EN"
                                                        ? 'Receive event and promotional news as push notifications.'
                                                        : '',
                                                style: TextStyle(
                                                  color: Color.fromARGB(
                                                      255, 130, 130, 130),
                                                  fontSize: 14.0,
                                                ),
                                              ),
                                              value: isCommertialPushAllow,
                                              onChanged: (value) async {
                                                setState(() =>
                                                    isCommertialPushAllow =
                                                        value!);
                                                await setFireData();
                                              },
                                            ),
                                          )
                                        : const SizedBox(),
                                    const Padding(
                                      padding:
                                          EdgeInsets.fromLTRB(10, 10, 0, 0),
                                      child: Text(
                                        // 언어에 따라 다른 메시지 출력
                                        lang == "KO"
                                            ? "권한 차단 후, 다시 허용하려면 설정에서 권한 허용이 필요합니다."
                                            : lang == "EN"
                                                ? "After blocking the permission, required in the settings to allow it again."
                                                : "",
                                        style: TextStyle(
                                          fontSize: 14.0,
                                          color: Color.fromARGB(
                                              255, 100, 100, 100),
                                        ),
                                      ),
                                    ),
                                    GestureDetector(
                                      onTap: () => openAppSettings(),
                                      child: const Padding(
                                        padding: EdgeInsets.only(left: 10.0),
                                        child: Text(
                                          // 언어에 따라 다른 메시지 출력
                                          lang == "KO"
                                              ? "앱 설정 바로가기"
                                              : lang == "EN"
                                                  ? "App Settings"
                                                  : "",
                                          style: TextStyle(
                                            fontSize: 14.0,
                                            color: Colors.blue,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      )
                    : const SizedBox(),
              ],
            );
          },
        ),
        bottomNavigationBar: menuType == "navbar" // 메뉴 타입이 bottom인 경우
            ? Container(
                // 하단바
                height: 55, // 높이
                padding: const EdgeInsets.all(0.0),
                margin: const EdgeInsets.all(0.0),
                decoration: const BoxDecoration(color: Colors.black), // 배경색
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    GestureDetector(
                      // 홈 버튼
                      onTap: () => inAppWebViewController.loadUrl(
                        urlRequest: URLRequest(
                          url: WebUri(webviewStartPage),
                        ),
                      ),
                      child: const Padding(
                        padding: EdgeInsets.fromLTRB(24, 5, 0, 0),
                        child: Icon(
                          Icons.home,
                          color: Colors.white,
                          size: 26,
                        ),
                      ),
                    ),
                    GestureDetector(
                      // 뒤로가기 버튼
                      onTap: () => goBack(),
                      child: const Padding(
                        padding: EdgeInsets.fromLTRB(0, 0, 2, 0),
                        child: Icon(
                          Icons.chevron_left,
                          color: Colors.white,
                          size: 32,
                        ),
                      ),
                    ),
                    GestureDetector(
                      // 앞으로가기 버튼
                      onTap: () => goForward(),
                      child: const Padding(
                        padding: EdgeInsets.fromLTRB(0, 0, 2, 0),
                        child: Icon(
                          Icons.chevron_right,
                          color: Colors.white,
                          size: 32,
                        ),
                      ),
                    ),
                    GestureDetector(
                      // 새로고침 버튼
                      onTap: () => inAppWebViewController.reload(),
                      child: const Padding(
                        padding: EdgeInsets.fromLTRB(0, 3, 6, 0),
                        child: Icon(
                          Icons.refresh,
                          color: Colors.white,
                          size: 26,
                        ),
                      ),
                    ),
                    GestureDetector(
                      // 설정 버튼
                      onTap: () {
                        setState(() => nowScreen = "setting_screen");
                      },
                      child: const Padding(
                        padding: EdgeInsets.fromLTRB(2, 4, 26, 0),
                        child: Icon(
                          Icons.settings,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            : const SizedBox(),
        floatingActionButton:
            menuType == "floatingButton" // 메뉴 타입이 floating인 경우
                ? FloatingActionButton(
                    // 메뉴 호출 버튼
                    onPressed: () {
                      setState(() => nowScreen = "setting_screen");
                    },
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    shape: const CircleBorder(),
                    mini: true,
                    child: const Icon(
                      Icons.settings,
                      size: 20,
                    ),
                  )
                : const SizedBox(),
      ),
    );
  }
}
