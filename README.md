# 醇境雪茄 POS 系统

Android 平板点餐系统。离线优先，支持扫码收款、蓝牙打印、数据备份。

## 技术栈

- **前端**: Vue 3 + Vite + TypeScript + Capacitor
- **后台 API**: Flask (Python)
- **数据库**: SQLite (本地) / MySQL (可选)
- **蓝牙打印**: Capacitor Bluetooth Serial

## 开发

```bash
# 前端开发
cd webapp
npm install
npm run dev

# Flask API (另一个终端)
cd api
./venv/bin/python run.py

# 构建 APK
npm run build
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
```

## APK 下载

GitHub Actions 构建产物: `android/app/build/outputs/apk/debug/app-debug.apk`
