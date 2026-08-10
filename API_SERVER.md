# 🚀 Moxra API Server - راهنمای اجرا و استفاده

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Uvicorn-0.20%2B-2C3E50?style=for-the-badge" alt="Uvicorn">
  <img src="https://img.shields.io/badge/REST-API-blue?style=for-the-badge" alt="REST API">
  <img src="https://img.shields.io/badge/Public-Free-brightgreen?style=for-the-badge" alt="Public Free">
</div>

---

## 📖 معرفی

Moxra API Server یک سرور REST API برای تشخیص محتوای نامناسب است. با این سرور می‌تونید از طریق HTTP درخواست بدید و محتوای تصاویر، گیف‌ها و ویدیوها رو بررسی کنید.

**ویژگی‌های کلیدی:**
- ⚡ **سرعت بالا** - تشخیص در کمتر از نیم ثانیه
- 🔓 **عمومی و رایگان** - بدون نیاز به احراز هویت
- 🌐 **API استاندارد** - RESTful با خروجی JSON
- 🎨 **رابط کاربری وب** - محیط تست تعاملی
- 📱 **سازگار با همه** - از هر زبانی قابل استفاده

---

## 📦 نصب

```bash
pip install moxra
```

برای اجرای سرور نیاز به نصب اضافی نیست، همه چیز در پکیج موجود است.

---

## 🚀 اجرای سرور

### روش ۱: ساده‌ترین روش

```bash
python -m moxra.api.app
```

### روش ۲: با Uvicorn

```bash
uvicorn moxra.api.app:create_app --host 0.0.0.0 --port 8000
```

### روش ۳: با تنظیمات سفارشی

یک فایل `run.py` بسازید:

```python
from moxra.api.app import run_server
from moxra.core.config import Config

config = Config(
    host="0.0.0.0",
    port=9000,
    debug=True,
    model_type="i3",
    device="cuda"
)

run_server(config)
```

سپس اجرا کنید:

```bash
python run.py
```

### روش ۴: با متغیرهای محیطی

```bash
# لینوکس/مک
export MOXRA_HOST="0.0.0.0"
export MOXRA_PORT="8000"
export MOXRA_DEBUG="true"
export MOXRA_MODEL_TYPE="i3"
export MOXRA_DEVICE="cuda"

python -m moxra.api.app
```

```cmd
:: ویندوز
set MOXRA_HOST=0.0.0.0
set MOXRA_PORT=8000
set MOXRA_DEBUG=true
python -m moxra.api.app
```

---

## 🌐 اندپوینت‌های API

### 📤 ۱. تشخیص تصویر

**اندپوینت:** `POST /api/v1/classify-img`

**ورودی:** multipart/form-data

| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `image` | file | ✅ | فایل تصویر (JPG, PNG, WEBP, BMP) |

**حداکثر حجم:** ۲۰ مگابایت

**مثال با curl:**
```bash
curl -X POST http://localhost:8000/api/v1/classify-img \
  -F "image=@photo.jpg"
```

**مثال با Python:**
```python
import requests

files = {"image": open("photo.jpg", "rb")}
response = requests.post("http://localhost:8000/api/v1/classify-img", files=files)
print(response.json())
```

---

### 🎞️ ۲. تشخیص گیف

**اندپوینت:** `POST /api/v1/classify-gif`

**ورودی:** multipart/form-data

| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `gif` | file | ✅ | فایل گیف (GIF) |

**حداکثر حجم:** ۲۰ مگابایت

**مثال:**
```bash
curl -X POST http://localhost:8000/api/v1/classify-gif \
  -F "gif=@animation.gif"
```

---

### 🎬 ۳. تشخیص ویدیو

**اندپوینت:** `POST /api/v1/classify-video`

**ورودی:** multipart/form-data

| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `video` | file | ✅ | فایل ویدیو (MP4, AVI, MOV, MKV) |
| `sample_rate` | float | ❌ | نرخ نمونه‌برداری (پیش‌فرض: 0.1) |
| `max_frames` | int | ❌ | حداکثر فریم (پیش‌فرض: 100) |

**حداکثر حجم:** ۱۰۰ مگابایت

**مثال:**
```bash
curl -X POST http://localhost:8000/api/v1/classify-video \
  -F "video=@video.mp4" \
  -F "sample_rate=0.05" \
  -F "max_frames=200"
```

---

### 🔗 ۴. تشخیص از طریق لینک

**اندپوینت:** `POST /api/v1/classify-url`

**ورودی:** JSON

| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `url` | string | ✅ | لینک مستقیم فایل |

**مثال:**
```bash
curl -X POST http://localhost:8000/api/v1/classify-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'
```

---

### 💚 ۵. بررسی سلامت

**اندپوینت:** `GET /api/v1/health`

**مثال:**
```bash
curl http://localhost:8000/api/v1/health
```

**خروجی:**
```json
{
  "Moxra": {
    "model": "Moxra-1",
    "ok": true,
    "status": "healthy",
    "model_loaded": true,
    "inference_count": 1234,
    "device": "cpu",
    "image_dim": 224,
    "uptime_seconds": 3600.5
  }
}
```

---

### 🧹 ۶. پاکسازی حافظه کش

**اندپوینت:** `POST /api/v1/cleanup`

**مثال:**
```bash
curl -X POST http://localhost:8000/api/v1/cleanup
```

---

## 📊 ساختار پاسخ

همه پاسخ‌ها به این صورت هستند:

```json
{
  "Moxra": {
    "model": "Moxra-1",
    "ok": true,
    "channel": "moxra.ir",
    "writer": " @Moxra ",
    "result": {
      "filename": "image.jpg",
      "type": "image",
      "predictions": {
        "neutral": 0.8500,
        "sexy": 0.0800,
        "porn": 0.0400,
        "hentai": 0.0200,
        "drawing": 0.0100
      },
      "dominant_category": "neutral",
      "raw_nsfw_score": 0.1400,
      "adjusted_nsfw_score": 0.1400,
      "is_nsfw": false,
      "is_safe": true,
      "is_suspicious": false,
      "veil": {
        "has_veil": false,
        "confidence": 0.0,
        "method": "none"
      },
      "thresholds": {
        "nsfw": 0.85,
        "safe": 0.25,
        "suspicious": 0.60
      }
    }
  }
}
```

---

## 🎨 رابط کاربری وب

سرور شامل یک رابط کاربری وب زیبا است:

```
http://localhost:8000
```

**ویژگی‌ها:**
- ✨ طراحی مدرن و جذاب
- 📤 کشیدن و رها کردن فایل
- ⚡ نتایج لحظه‌ای
- 🌓 حالت تاریک/روشن
- 📱 کاملاً واکنش‌گرا
- 🔄 تغییر زبان (فارسی/انگلیسی)

---

## 💻 کدهای وضعیت HTTP

| کد | توضیح |
|-----|-------|
| ✅ **۲۰۰** | موفقیت آمیز |
| ❌ **۴۰۰** | درخواست نامعتبر |
| ❌ **۴۱۳** | حجم فایل بیش از حد (۲۰/۱۰۰ مگابایت) |
| ❌ **۴۱۵** | نوع فایل پشتیبانی نمی‌شود |
| ❌ **۵۰۰** | خطای داخلی سرور |

---

## 🌍 مثال‌های استفاده از زبان‌های مختلف

### Python

```python
import requests

# تشخیص تصویر
files = {"image": open("photo.jpg", "rb")}
response = requests.post("http://localhost:8000/api/v1/classify-img", files=files)
data = response.json()

if data['Moxra']['result']['is_nsfw']:
    print("⚠️ محتوای نامناسب!")
else:
    print("✅ محتوای ایمن")
```

### JavaScript (Node.js / Fetch)

```javascript
// تشخیص تصویر
const formData = new FormData();
formData.append('image', file);

const response = await fetch('http://localhost:8000/api/v1/classify-img', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log(data.Moxra.result.is_nsfw ? 'NSFW' : 'SAFE');
```

### PHP

```php
<?php
// تشخیص تصویر
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'http://localhost:8000/api/v1/classify-img');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, [
    'image' => new CURLFile('photo.jpg')
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);
echo $data['Moxra']['result']['is_nsfw'] ? 'NSFW' : 'SAFE';
?>
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func main() {
    file, _ := os.Open("photo.jpg")
    defer file.Close()

    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)
    part, _ := writer.CreateFormFile("image", "photo.jpg")
    io.Copy(part, file)
    writer.Close()

    req, _ := http.NewRequest("POST", "http://localhost:8000/api/v1/classify-img", body)
    req.Header.Set("Content-Type", writer.FormDataContentType())

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Println(result)
}
```

### C# (.NET)

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        using var client = new HttpClient();
        using var content = new MultipartFormDataContent();
        
        var fileContent = new ByteArrayContent(File.ReadAllBytes("photo.jpg"));
        fileContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg");
        content.Add(fileContent, "image", "photo.jpg");

        var response = await client.PostAsync("http://localhost:8000/api/v1/classify-img", content);
        var result = await response.Content.ReadAsStringAsync();
        Console.WriteLine(result);
    }
}
```

### Java (OkHttp)

```java
import okhttp3.*;
import java.io.File;

public class Main {
    public static void main(String[] args) throws Exception {
        OkHttpClient client = new OkHttpClient();
        
        RequestBody requestBody = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("image", "photo.jpg",
                RequestBody.create(new File("photo.jpg"), MediaType.parse("image/jpeg")))
            .build();
        
        Request request = new Request.Builder()
            .url("http://localhost:8000/api/v1/classify-img")
            .post(requestBody)
            .build();
        
        Response response = client.newCall(request).execute();
        System.out.println(response.body().string());
    }
}
```

### Ruby

```ruby
require 'net/http'
require 'uri'
require 'json'

# تشخیص تصویر
uri = URI('http://localhost:8000/api/v1/classify-img')
request = Net::HTTP::Post.new(uri)
request.set_form(
  { 'image' => File.open('photo.jpg') },
  'multipart/form-data'
)

response = Net::HTTP.start(uri.hostname, uri.port) do |http|
  http.request(request)
end

data = JSON.parse(response.body)
puts data['Moxra']['result']['is_nsfw'] ? 'NSFW' : 'SAFE'
```

---

## ⚙️ تنظیمات سرور

### متغیرهای محیطی

| متغیر | توضیح | پیش‌فرض |
|-------|-------|---------|
| `MOXRA_HOST` | آدرس میزبان | `0.0.0.0` |
| `MOXRA_PORT` | پورت سرور | `8000` |
| `MOXRA_DEBUG` | حالت اشکال‌زدایی | `false` |
| `MOXRA_MODEL_TYPE` | نوع مدل (d/m2/i3) | `d` |
| `MOXRA_DEVICE` | دستگاه (cpu/cuda) | `cpu` |
| `MOXRA_NSFW_THRESHOLD` | آستانه NSFW | `0.85` |
| `MOXRA_SAFE_THRESHOLD` | آستانه ایمن | `0.25` |
| `MOXRA_MAX_FILE_SIZE` | حداکثر حجم فایل (MB) | `20` |

### تنظیمات در کد

```python
from moxra.api.app import run_server
from moxra.core.config import Config

config = Config(
    host="0.0.0.0",
    port=9000,
    debug=True,
    model_type="i3",
    device="cuda",
    nsfw_threshold=0.90,
    safe_threshold=0.30
)

run_server(config)
```

---

## 📊 آمار سرور

با اندپوینت `/health` می‌تونید آمار سرور رو ببینید:

```json
{
  "Moxra": {
    "model": "Moxra-1",
    "ok": true,
    "status": "healthy",
    "model_loaded": true,
    "inference_count": 1234,
    "error_count": 5,
    "device": "cpu",
    "image_dim": 224,
    "uptime_seconds": 3600.5,
    "providers": ["CPUExecutionProvider"],
    "thresholds": {
      "nsfw": 0.85,
      "safe": 0.25,
      "suspicious": 0.60
    }
  }
}
```

---

## 📁 ساختار فایل‌های سرور

```
moxra/
└── api/
    ├── app.py          # برنامه اصلی FastAPI
    ├── routes.py       # اندپوینت‌های API
    └── models.py       # مدل‌های Pydantic
```

---

## 🚨 عیب‌یابی

### خطا: پورت ۸۰۰۰ در حال استفاده است

```bash
# پورت دیگری استفاده کنید
python -m moxra.api.app --port 9000
```

### خطا: مدل پیدا نشد

مدل به صورت خودکار دانلود می‌شود، اگر اینترنت ندارید:

```bash
# مسیر مدل را مشخص کنید
export MOXRA_MODEL="/path/to/model.onnx"
```

### خطا: حافظه کم

```bash
# پاکسازی حافظه
curl -X POST http://localhost:8000/api/v1/cleanup
```

---

## 🔒 امنیت

- ✅ سرور به صورت عمومی اجرا می‌شود
- ✅ فایل‌ها پس از پردازش حذف می‌شوند
- ✅ بدون ذخیره‌سازی اطلاعات کاربران
- ✅ CORS برای همه دامنه‌ها فعال است

---

## 📄 مجوز

MIT License - استفاده آزاد برای پروژه‌های شخصی و تجاری

---

## 👨‍💻 توسعه‌دهنده

**ابوالفضل زارعی | Abolfazl Zarei**

<div align="center">
  <a href="https://github.com/AbolfazlZarei-dev">
    <img src="https://img.shields.io/badge/GitHub-دنبال_کنید-181717?style=for-the-badge&logo=github">
  </a>
  <a href="https://t.me/Abolfazl_PGR">
    <img src="https://img.shields.io/badge/تلگرام-دنبال_کنید-2CA5E0?style=for-the-badge&logo=telegram">
  </a>
  <a href="https://rubika.ir/NinjaCode">
    <img src="https://img.shields.io/badge/روبیکا-دنبال_کنید-FF6B6B?style=for-the-badge">
  </a>
  <a href="https://abolfazlzarei.sbs">
    <img src="https://img.shields.io/badge/وب‌سایت-مشاهده-4285F4?style=for-the-badge">
  </a>
</div>

---

<div align="center">

**ساخته شده با ❤️ برای جامعه متن‌باز**

</div>

