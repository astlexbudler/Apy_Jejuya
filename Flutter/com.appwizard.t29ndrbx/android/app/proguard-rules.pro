## Flutter wrapper
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }
-dontwarn io.flutter.embedding.**
# Google Play Core SplitCompat
-keep public class com.google.android.play.core.splitcompat.** { *; }
-keep public class com.google.android.play.core.splitinstall.** { *; }
-keepclassmembers class * extends com.google.android.play.core.splitcompat.SplitCompatApplication { *; }
