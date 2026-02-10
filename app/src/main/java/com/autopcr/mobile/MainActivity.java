package com.autopcr.mobile;

import android.animation.ObjectAnimator;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private View loadingContainer;
    private ImageView logoImage;
    private ProgressBar progressBar;
    private TextView statusText;
    private Button retryButton;
    private Button updateDbButton;
    
    private static final String SERVER_URL = "http://127.0.0.1:13200/daily/login";
    private static final String DB_UPDATE_URL = "http://127.0.0.1:13200/db_update";
    private Handler handler = new Handler(Looper.getMainLooper());
    private int retryCount = 0;
    private static final int MAX_RETRIES = 60;
    private boolean isServerReady = false;
    private boolean isErrorOccurred = false;
    private boolean isDbUpdateCompleted = false;
    private ObjectAnimator logoAnimator;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupWebView();
        startLogoAnimation();
        
        // 启动后台服务
        startService(new Intent(this, AutoPCRService.class));
        
        // 先加载数据库更新页面
        showLoadingState("正在启动 AutoPCR 服务器...");
        loadDbUpdatePage();
    }

    private void initViews() {
        webView = findViewById(R.id.webview);
        loadingContainer = findViewById(R.id.loadingContainer);
        logoImage = findViewById(R.id.logoImage);
        progressBar = findViewById(R.id.progressBar);
        statusText = findViewById(R.id.statusText);
        retryButton = findViewById(R.id.retryButton);
        updateDbButton = findViewById(R.id.updateDbButton);

        retryButton.setOnClickListener(v -> {
            retryCount = 0;
            showLoadingState("正在重试连接...");
            loadDbUpdatePage();
            if (!logoAnimator.isStarted()) {
                logoAnimator.start();
            }
        });

        updateDbButton.setOnClickListener(v -> {
            // 打开数据库更新页面
            webView.setVisibility(View.VISIBLE);
            loadingContainer.setVisibility(View.GONE);
            webView.loadUrl(DB_UPDATE_URL);
        });
    }

    private void startLogoAnimation() {
        logoAnimator = ObjectAnimator.ofFloat(logoImage, "alpha", 1f, 0.4f);
        logoAnimator.setDuration(1200);
        logoAnimator.setRepeatCount(ObjectAnimator.INFINITE);
        logoAnimator.setRepeatMode(ObjectAnimator.REVERSE);
        logoAnimator.start();
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);

        // 添加 JavaScript 接口用于接收数据库更新完成通知
        webView.addJavascriptInterface(new WebAppInterface(), "Android");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                isErrorOccurred = false;
                if (!isServerReady) {
                    webView.setVisibility(View.GONE);
                    loadingContainer.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                if (!isErrorOccurred) {
                    // 成功加载
                    loadingContainer.setVisibility(View.GONE);
                    webView.setVisibility(View.VISIBLE);
                    isServerReady = true;
                    retryCount = 0;
                    if (logoAnimator != null) {
                        logoAnimator.cancel();
                    }
                    
                    // 如果是数据库更新页面加载完成，显示提示
                    if (url.contains("/db_update")) {
                        Toast.makeText(MainActivity.this, "请先更新数据库，完成后将自动跳转到登录页面", Toast.LENGTH_LONG).show();
                    }
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    isErrorOccurred = true;
                    webView.setVisibility(View.GONE);
                    loadingContainer.setVisibility(View.VISIBLE);
                    
                    Log.e("WebView", "Error: " + error.getDescription());
                    
                    if (retryCount < MAX_RETRIES) {
                        retryCount++;
                        statusText.setText(String.format("服务器启动中... (%d秒)", retryCount));
                        
                        handler.postDelayed(() -> {
                            if (!isFinishing()) {
                                if (!isDbUpdateCompleted) {
                                    webView.loadUrl(DB_UPDATE_URL);
                                } else {
                                    webView.loadUrl(SERVER_URL);
                                }
                            }
                        }, 1000);
                    } else {
                        showErrorState("连接超时。\n请检查日志或尝试点击重试。");
                    }
                }
            }
        });
    }

    // JavaScript 接口类
    public class WebAppInterface {
        @JavascriptInterface
        public void onDbUpdateComplete() {
            // 数据库更新完成，跳转到登录页面
            runOnUiThread(() -> {
                isDbUpdateCompleted = true;
                Toast.makeText(MainActivity.this, "数据库更新完成，正在进入登录页面...", Toast.LENGTH_SHORT).show();
                webView.loadUrl(SERVER_URL);
            });
        }
        
        @JavascriptInterface
        public void onDbUpdateError(String error) {
            // 数据库更新出错
            runOnUiThread(() -> {
                Toast.makeText(MainActivity.this, "数据库更新失败: " + error, Toast.LENGTH_LONG).show();
            });
        }
    }

    private void loadDbUpdatePage() {
        webView.loadUrl(DB_UPDATE_URL);
    }

    private void loadPageWithRetry() {
        webView.loadUrl(SERVER_URL);
    }

    private void showLoadingState(String message) {
        loadingContainer.setVisibility(View.VISIBLE);
        progressBar.setVisibility(View.VISIBLE);
        statusText.setText(message);
        statusText.setVisibility(View.VISIBLE);
        retryButton.setVisibility(View.GONE);
        updateDbButton.setVisibility(View.GONE);
        webView.setVisibility(View.GONE); 
    }

    private void showErrorState(String message) {
        loadingContainer.setVisibility(View.VISIBLE);
        progressBar.setVisibility(View.GONE);
        statusText.setText(message);
        statusText.setVisibility(View.VISIBLE);
        retryButton.setVisibility(View.VISIBLE);
        updateDbButton.setVisibility(View.VISIBLE);
        webView.setVisibility(View.GONE);
        if (logoAnimator != null) {
            logoAnimator.cancel();
            logoImage.setAlpha(1f); // 恢复完全不透明
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
