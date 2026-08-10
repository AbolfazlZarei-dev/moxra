# 🚀 Moxra - کتابخانه تشخیص محتوای نامناسب حرفه‌ای

<div dir="rtl" align="center">

**کتابخانه حرفه‌ای تشخیص محتوای نامناسب در تصاویر، گیف‌ها و ویدیوها**

<a href="https://www.python.org/">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blueviolet?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</a>
<a href="LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License" />
</a>
<a href="https://fastapi.tiangolo.com/">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-teal?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
</a>
<a href="https://github.com/moxra/moxra/releases">
  <img src="https://img.shields.io/github/v/release/moxra/moxra?color=orange&style=for-the-badge&logo=github&logoColor=white" alt="Release" />
</a>
<a href="https://github.com/moxra/moxra/releases">
  <img src="https://img.shields.io/github/downloads/moxra/moxra/total?color=blue&style=for-the-badge&logo=github&logoColor=white" alt="Downloads" />
</a>

</div>

---

## 🎯 درباره پروژه

<div dir="rtl">

**موکسرا** یک کتابخانه قدرتمند و سبک برای تشخیص محتوای نامناسب در تصاویر، گیف‌ها و ویدیوها است. این ابزار با استفاده از مدل‌های پیشرفته یادگیری عمیق و موتور اجرایی ONNX، با دقت بالای ۹۵٪ محتوای نامناسب را شناسایی می‌کند.

</div>

---

## ✨ ویژگی‌های برجسته

| ویژگی | توضیحات |
|:-----:|---------|
| ⚡ **سرعت بالا** | تشخیص در کمتر از نیم ثانیه |
| 🎯 **دقت ۹۵٪** | آموزش دیده روی میلیون‌ها تصویر |
| 🖼️ **فرمت‌های مختلف** | تصویر، گیف و ویدیو |
| 🔒 **حریم خصوصی** | پردازش کاملاً محلی |
| 🌐 **API عمومی** | بدون نیاز به احراز هویت |
| 🕊️ **تشخیص حجاب** | تشخیص خودکار حجاب اسلامی |
| 💰 **رایگان** | کاملاً رایگان برای همه |
| 🎨 **رابط وب** | رابط کاربری زیبا و مدرن |
| 🖥️ **خط فرمان** | ابزار کامل خط فرمان |

---

## 📥 دانلود مدل‌ها

> ⚠️ **نکته مهم**: فایل‌های مدل به دلیل حجم بالا در **[GitHub Releases](https://github.com/moxra/moxra/releases)** قرار گرفته‌اند.

### 📋 لیست مدل‌ها

| ردیف | نام مدل | توضیحات | حجم | لینک دانلود |
|:----:|---------|---------|:---:|:-----------:|
| ۱ | `moxra_model.onnx` | مدل پیش‌فرض MobileNet V2 | ۱۴ مگابایت | [📥 دانلود](https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0//moxra_model.onnx) |
| ۲ | `moxra_m2model.onnx` | مدل بهینه‌شده MobileNet V2 | ۱۴ مگابایت | [📥 دانلود](https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0//moxra_m2model.onnx) |
| ۳ | `moxra_i3model.onnx` | مدل Inception V3 (دقت بالا) | ۹۲ مگابایت | [📥 دانلود](https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0//moxra_i3model.onnx) |

---

## 🚀 نصب و راه‌اندازی

### ۱. نصب از PyPI

```bash
pip install moxra
```

### ۲. نصب از روی کد منبع

```bash
git clone https://github.com/moxra/moxra.git
cd moxra
pip install -e .
```

### ۳. دانلود مدل‌ها (اختیاری - به صورت خودکار دانلود می‌شود)

**روش اول - دانلود با PowerShell (ویندوز):**
```powershell
# ایجاد پوشه مدل
New-Item -ItemType Directory -Force -Path "moxra_model"

# دانلود مدل پیش‌فرض
Invoke-WebRequest -Uri "https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0/moxra_model.onnx" -OutFile "moxra_model/moxra_model.onnx"

# دانلود مدل بهینه‌شده
Invoke-WebRequest -Uri "https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0/moxra_m2model.onnx" -OutFile "moxra_model/moxra_m2model.onnx"

# دانلود مدل Inception V3
Invoke-WebRequest -Uri "https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0/moxra_i3model.onnx" -OutFile "moxra_model/moxra_i3model.onnx"
```

**روش دوم - دانلود با curl:**
```bash
# ایجاد پوشه مدل
mkdir -p moxra_model

# دانلود مدل‌ها
curl -L https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0//moxra_model.onnx -o moxra_model/moxra_model.onnx
curl -L https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0//moxra_m2model.onnx -o moxra_model/moxra_m2model.onnx
curl -L https://github.com/AbolfazlZarei-dev/moxra/releases/download/v1.0.0//moxra_i3model.onnx -o moxra_model/moxra_i3model.onnx
```

---

## 💻 شروع سریع با کتابخانه

```python
from moxra import MoxraDetector

# راه‌اندازی تشخیص‌دهنده
detector = MoxraDetector()

# تشخیص تصویر با قابلیت تشخیص حجاب
result = detector.classify_with_veil("image.jpg")

# نمایش نتیجه
print(f"آیا محتوا نامناسب است؟ {result['is_nsfw']}")
print(f"امتیاز NSFW: {result['adjusted_nsfw_score']:.2%}")
print(f"دسته غالب: {result['dominant_category']}")
print(f"پیش‌بینی‌ها: {result['predictions']}")
```

### خروجی نمونه:

```
🟢 محتوای ایمن
امتیاز NSFW: ۱۴٪
دسته غالب: neutral
پیش‌بینی‌ها: {'neutral': 0.85, 'sexy': 0.08, 'porn': 0.04, 'hentai': 0.02, 'drawing': 0.01}
```

---

## 📖 استفاده پیشرفته از کتابخانه

### تشخیص تصویر

```python
from moxra import MoxraDetector

detector = MoxraDetector()

# تشخیص ساده
predictions = detector.predict_image("photo.jpg")
print(predictions)

# تشخیص با حجاب (پیشنهادی)
result = detector.classify_with_veil("photo.jpg")
print(result['is_nsfw'])
print(result['veil']['has_veil'])
```

### تشخیص گیف

```python
result = detector.predict_gif("animation.gif")
# میانگین تمام فریم‌ها
print(result)
```

### تشخیص ویدیو

```python
result = detector.predict_video(
    "video.mp4",
    sample_rate=0.1,    # ۱۰٪ فریم‌ها
    max_frames=100      # حداکثر ۱۰۰ فریم
)

print(f"تعداد فریم‌ها: {result['metadata']['processed_frames']}")
print(f"میانگین: {result['average']}")
```

### تشخیص از داده باینری

```python
with open("image.jpg", "rb") as f:
    image_bytes = f.read()

result = detector.predict_bytes(image_bytes)
print(result)
```

### تنظیمات سفارشی

```python
from moxra import MoxraDetector, Config

config = Config(
    model_type="i3",        # d, m2, i3
    device="cuda",          # cpu, cuda, tensorrt
    nsfw_threshold=0.85,
    safe_threshold=0.25
)

detector = MoxraDetector(config)
result = detector.classify_with_veil("image.jpg")
```

### تشخیص همزمان (Async)

```python
import asyncio
from moxra import MoxraDetector

async def main():
    detector = MoxraDetector()
    
    tasks = [
        detector.predict_image_async("img1.jpg"),
        detector.predict_image_async("img2.jpg"),
        detector.predict_image_async("img3.jpg")
    ]
    
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

### دریافت آمار

```python
stats = detector.get_stats()
print(f"تعداد تشخیص‌ها: {stats['inference_count']}")
print(f"دستگاه: {stats['device']}")
print(f"زمان اجرا: {stats['uptime_seconds']} ثانیه")
```

### پاکسازی حافظه

```python
detector.cleanup()
```

---

## 🌐 راه‌اندازی سرور API

### اجرای سرور

```bash
# روش اول - با run.py
python run.py

# روش دوم - با uvicorn
uvicorn moxra.api.app:create_app --host 0.0.0.0 --port 8000 --reload

# روش سوم - با متغیرهای محیطی
export MOXRA_HOST="0.0.0.0"
export MOXRA_PORT="8000"
python -m moxra.api.app
```

### دسترسی به رابط کاربری

پس از اجرا، به آدرس زیر بروید:
```
http://localhost:8000
```

### اندپوینت‌های API

| متد | مسیر | توضیحات |
|:---:|------|---------|
| `POST` | `/api/v1/classify-img` | تشخیص تصویر |
| `POST` | `/api/v1/classify-gif` | تشخیص گیف |
| `POST` | `/api/v1/classify-video` | تشخیص ویدیو |
| `POST` | `/api/v1/classify-url` | تشخیص از لینک |
| `GET` | `/api/v1/health` | بررسی سلامت |
| `POST` | `/api/v1/cleanup` | پاکسازی حافظه |

### تست با curl

```bash
# تشخیص تصویر
curl -X POST http://localhost:8000/api/v1/classify-img -F "image=@image.jpg"

# تشخیص گیف
curl -X POST http://localhost:8000/api/v1/classify-gif -F "gif=@animation.gif"

# تشخیص ویدیو
curl -X POST http://localhost:8000/api/v1/classify-video -F "video=@video.mp4" -F "sample_rate=0.05"

# تشخیص از لینک
curl -X POST http://localhost:8000/api/v1/classify-url -H "Content-Type: application/json" -d '{"url": "https://example.com/image.jpg"}'

# بررسی سلامت
curl http://localhost:8000/api/v1/health

# پاکسازی حافظه
curl -X POST http://localhost:8000/api/v1/cleanup
```

---

## 🖥️ ابزار خط فرمان

```bash
# تشخیص تصویر
moxra -i image.jpg

# تشخیص تصویر با خروجی زیبا
moxra -i image.jpg --format pretty

# تشخیص با خروجی JSON
moxra -i image.jpg --format json

# تشخیص ویدیو
moxra -i video.mp4 -s 0.05 -f 200

# ذخیره خروجی
moxra -i image.jpg -o result.json

# نمایش جزئیات کامل
moxra -i image.jpg -v

# استفاده از مدل خاص
moxra -i image.jpg -t i3 -d cuda
```

### گزینه‌های خط فرمان

| گزینه | توضیحات |
|-------|---------|
| `-i, --input` | مسیر فایل ورودی (اجباری) |
| `-t, --type` | نوع مدل: d, m2, i3 |
| `-d, --device` | دستگاه: cpu, cuda, tensorrt |
| `-s, --sample-rate` | نرخ نمونه‌برداری ویدیو |
| `-f, --max-frames` | حداکثر فریم ویدیو |
| `--format` | فرمت خروجی: json, pretty, simple |
| `-o, --output` | ذخیره خروجی در فایل |
| `-v, --verbose` | نمایش خروجی مفصل |
| `--no-color` | غیرفعال کردن رنگ‌ها |

---

## 📁 ساختار پروژه

```
moxra/
│
├── moxra/                     # 📦 کد اصلی
│   ├── api/                   # 🌐 API و اندپوینت‌ها
│   │   ├── app.py            # برنامه FastAPI
│   │   ├── routes.py         # مسیرهای API
│   │   └── models.py         # مدل‌های داده
│   │
│   ├── core/                  # ⚙️ هسته تشخیص
│   │   ├── detector.py       # موتور اصلی
│   │   ├── config.py         # تنظیمات
│   │   └── models.py         # مدیریت مدل
│   │
│   ├── processors/            # 🖼️ پردازشگرها
│   │   ├── image.py          # پردازش تصویر
│   │   ├── gif.py            # پردازش گیف
│   │   └── video.py          # پردازش ویدیو
│   │
│   └── cli/                   # 💻 ابزار خط فرمان
│       └── main.py
│
├── moxra_model/               # 📁 مدل‌ها (اینجا قرار دهید)
│   ├── moxra_model.onnx
│   ├── moxra_m2model.onnx
│   └── moxra_i3model.onnx
│
├── static/                    # 🎨 فایل‌های استاتیک
├── templates/                 # 📄 قالب‌های HTML
├── run.py                     # 🚀 اجرای سرور
├── requirements.txt           # 📋 وابستگی‌ها
├── setup.py                   # 📦 نصب پکیج
└── README.md                  # 📖 این فایل
```

---

## 🔧 وابستگی‌ها

```txt
Python >= 3.8
FastAPI >= 0.100.0
ONNX Runtime >= 1.12.0
OpenCV >= 4.5.0
Pillow >= 9.0.0
NumPy >= 1.21.0
Uvicorn >= 0.20.0
Requests >= 2.28.0
Pydantic >= 2.0.0
```

---

## 📊 دسته‌بندی‌ها

| دسته | توضیحات | رنگ |
|------|---------|:----:|
| 🟢 **neutral** | محتوای ایمن و معمولی | سبز |
| 🟡 **sexy** | محتوای تحریک‌کننده | زرد |
| 🔴 **porn** | محتوای صریح بزرگسالان | قرمز |
| 🟣 **hentai** | محتوای صریح انیمه | بنفش |
| 🔵 **drawing** | نقاشی‌ها و تصاویر هنری | آبی |

---

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.  
برای اطلاعات بیشتر به فایل [LICENSE](LICENSE) مراجعه کنید.

---

## 👨‍💻 توسعه‌دهنده

<div dir="rtl" align="center">

**ابوالفضل زارعی**

</div>

| پلتفرم | لینک |
|---------|------|
| 🐙 **گیت‌هاب** | [@AbolfazlZarei-dev](https://github.com/AbolfazlZarei-dev) |
| 📱 **تلگرام** | [@Abolfazl_PGR](https://t.me/Abolfazl_PGR) |
| 🌐 **روبیکا** | [@NinjaCode](https://rubika.ir/NinjaCode) |
| 🌐 **وب‌سایت** | [abolfazlzarei.sbs](https://abolfazlzarei.sbs) |
| 📧 **ایمیل** | [ninjacode.ir@gmail.com](mailto:ninjacode.ir@gmail.com) |

---

## ⭐ حمایت

اگر این پروژه برای شما مفید بود:

- ⭐ به پروژه **ستاره** دهید
- 📢 آن را با دیگران **به اشتراک** بگذارید
- 🐛 **مشکلات** را گزارش دهید
- 🔧 در توسعه **مشارکت** کنید

---

<div align="center">

**ساخته شده با ❤️ توسط ابوالفضل زارعی**

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?logo=github)](https://github.com/AbolfazlZarei-dev)
[![Telegram](https://img.shields.io/badge/Telegram-Follow-2CA5E0?logo=telegram)](https://t.me/Abolfazl_PGR)
[![Rubika](https://img.shields.io/badge/Rubika-Follow-FF6B6B)](https://rubika.ir/NinjaCode)
[![Website](https://img.shields.io/badge/Website-Visit-4285F4)](https://abolfazlzarei.sbs)

</div>
