package br.com.golup.app;
import android.Manifest;
import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.graphics.Color;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import androidx.webkit.WebViewAssetLoader;
import android.webkit.WebSettings;
import android.webkit.WebChromeClient;
public class MainActivity extends Activity {
 private WebView webView;
 private static final String SOUND="golup_goals_sound", SILENT="golup_goals_silent";
 private void channels(){
  if(Build.VERSION.SDK_INT>=26){
   NotificationManager n=getSystemService(NotificationManager.class);
   NotificationChannel s=new NotificationChannel(SOUND,"Gols com som",NotificationManager.IMPORTANCE_HIGH); s.enableVibration(true);
   NotificationChannel q=new NotificationChannel(SILENT,"Gols sem som",NotificationManager.IMPORTANCE_LOW);q.setSound(null,null);q.enableVibration(false);
   n.createNotificationChannel(s);n.createNotificationChannel(q);
  }
 }
 public class AppBridge {
  @JavascriptInterface public void testGoal(final boolean sound, final boolean vibrate){
   runOnUiThread(()->{
    if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){
     requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},10);return;
    }
    Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(MainActivity.this,sound?SOUND:SILENT):new Notification.Builder(MainActivity.this);
    b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle("⚽ GOOOL! • GolUp").setContentText("Notificação de teste.").setAutoCancel(true);
    if(Build.VERSION.SDK_INT<26){if(sound)b.setDefaults(Notification.DEFAULT_SOUND);if(vibrate)b.setVibrate(new long[]{0,150,90,150});}
    ((NotificationManager)getSystemService(NOTIFICATION_SERVICE)).notify(1001,b.build());
   });
  }
 }
 @Override public void onCreate(Bundle state){
  super.onCreate(state);getWindow().setStatusBarColor(Color.rgb(9,19,30));getWindow().setNavigationBarColor(Color.rgb(16,29,43));
  channels();webView=new WebView(this);webView.setBackgroundColor(Color.rgb(9,19,30));final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder().addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this)).build();
  webView.setWebViewClient(new WebViewClient(){@Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request){return assetLoader.shouldInterceptRequest(request.getUrl());}});webView.setWebChromeClient(new WebChromeClient());
  WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);
  webView.addJavascriptInterface(new AppBridge(),"GolUpAndroid");setContentView(webView);webView.loadUrl("https://appassets.androidplatform.net/assets/index.html");
 }
 @Override public void onBackPressed(){if(webView.canGoBack())webView.goBack();else super.onBackPressed();}
}
