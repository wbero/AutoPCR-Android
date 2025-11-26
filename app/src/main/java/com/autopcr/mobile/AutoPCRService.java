package com.autopcr.mobile;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class AutoPCRService extends Service {
    private static final String TAG = "AutoPCRService";
    private static final String CHANNEL_ID = "AutoPCRServerChannel";
    private static final int NOTIFICATION_ID = 1;

    private ExecutorService executorService;
    private boolean isRunning = false;

    @Override
    public void onCreate() {
        super.onCreate();
        executorService = Executors.newSingleThreadExecutor();
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && "STOP".equals(intent.getAction())) {
            stopSelf();
            return START_NOT_STICKY;
        }

        if (!isRunning) {
            startForeground(NOTIFICATION_ID, createNotification("服务器正在启动..."));
            startPythonServer();
        }

        return START_STICKY;
    }

    private void startPythonServer() {
        isRunning = true;
        executorService.submit(() -> {
            try {
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(getApplicationContext()));
                }

                Python py = Python.getInstance();
                Log.i(TAG, "Python环境已初始化");

                // 更新通知状态
                updateNotification("服务器运行中 (端口: 13200)");
                showToast("AutoPCR 服务器已启动");

                // 调用 Python 入口函数
                // 注意：这个调用是阻塞的，直到服务器停止
                py.getModule("android_main").callAttr("start_server");

            } catch (Exception e) {
                Log.e(TAG, "Python 服务器运行错误", e);
                updateNotification("服务器错误: " + e.getMessage());
                showToast("服务器启动失败");
                isRunning = false;
                stopSelf();
            }
        });
    }

    private Notification createNotification(String contentText) {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE);

        return new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("AutoPCR 服务")
                .setContentText(contentText)
                .setSmallIcon(android.R.drawable.ic_menu_info_details) // 需要替换为实际图标
                .setContentIntent(pendingIntent)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
    }

    private void updateNotification(String contentText) {
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) {
            manager.notify(NOTIFICATION_ID, createNotification(contentText));
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel serviceChannel = new NotificationChannel(
                    CHANNEL_ID,
                    "AutoPCR Server Channel",
                    NotificationManager.IMPORTANCE_LOW
            );
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(serviceChannel);
            }
        }
    }
    
    private void showToast(String msg) {
        new Handler(Looper.getMainLooper()).post(() -> 
            Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_SHORT).show()
        );
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        isRunning = false;
        if (executorService != null) {
            executorService.shutdownNow();
        }
        Log.i(TAG, "服务已销毁");
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
