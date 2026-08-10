# 🚀 Moxra - کتابخانه تشخیص محتوای نامناسب

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/ONNX-1.12%2B-005B9F?style=for-the-badge&logo=onnx" alt="ONNX">
  <img src="https://img.shields.io/badge/Version-1.0.0-purple?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Downloads-10K+-brightgreen?style=for-the-badge" alt="Downloads">
</div>

---

## 📦 نصب

```bash
pip install moxra
```

یا برای استفاده از GPU:

```bash
pip install moxra[gpu]
```

---

## ⚡ شروع سریع

```python
from moxra import MoxraDetector

# یک خط کد - کتابخانه آماده استفاده!
detector = MoxraDetector()

# تشخیص تصویر
result = detector.classify_with_veil("image.jpg")
print(result['is_nsfw'])  # True/False
```

---

## 📖 راهنمای کامل

### ۱️⃣ ایجاد نمونه

```python
from moxra import MoxraDetector, Config

# روش ساده
detector = MoxraDetector()

# با تنظیمات سفارشی
config = Config(device="cuda", model_type="i3")
detector = MoxraDetector(config)

# از متغیرهای محیطی
config = Config.from_env()
detector = MoxraDetector(config)
```

---

### ۲️⃣ تشخیص تصویر

```python
# تشخیص با حجاب (پیشنهادی)
result = detector.classify_with_veil("photo.jpg")

# تشخیص ساده
predictions = detector.predict_image("photo.jpg")
```

**خروجی `classify_with_veil`:**

```python
{
    'predictions': {
        'neutral': 0.85,   # 85% ایمن
        'sexy': 0.08,      # 8% تحریک‌کننده
        'porn': 0.04,      # 4% مستهجن
        'hentai': 0.02,    # 2% انیمه
        'drawing': 0.01    # 1% نقاشی
    },
    'is_nsfw': False,      # آیا نامناسب است؟
    'is_safe': True,       # آیا ایمن است؟
    'is_suspicious': False, # آیا مشکوک است؟
    'nsfw_score': 0.14,    # امتیاز کلی
    'dominant_category': 'neutral',
    'veil': {
        'has_veil': False,  # آیا حجاب دارد؟
        'confidence': 0.0   # سطح اطمینان
    }
}
```

---

### ۳️⃣ تشخیص گیف

```python
result = detector.predict_gif("animation.gif")
# میانگین تمام فریم‌ها
```

---

### ۴️⃣ تشخیص ویدیو

```python
result = detector.predict_video(
    "video.mp4",
    sample_rate=0.1,    # 10% فریم‌ها
    max_frames=100      # حداکثر 100 فریم
)
```

**خروجی ویدیو:**

```python
{
    'average': {'neutral': 0.82, 'sexy': 0.07, ...},
    'frames': [
        {'time': 0.1, 'predictions': {...}},
        {'time': 0.2, 'predictions': {...}}
    ],
    'metadata': {
        'total_frames': 300,
        'processed_frames': 30,
        'fps': 30,
        'duration': 10.0
    }
}
```

---

### ۵️⃣ تشخیص از داده باینری

```python
with open("image.jpg", "rb") as f:
    image_bytes = f.read()

result = detector.predict_bytes(image_bytes)
```

---

### ۶️⃣ تشخیص همزمان (Async)

```python
import asyncio

async def main():
    detector = MoxraDetector()
    
    # اجرای همزمان چند تصویر
    tasks = [
        detector.predict_image_async("img1.jpg"),
        detector.predict_image_async("img2.jpg"),
        detector.predict_image_async("img3.jpg")
    ]
    
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

---

## ⚙️ تنظیمات پیشرفته

### کلاس Config

```python
from moxra import Config

config = Config(
    model_type="i3",        # d, m2, i3
    device="cuda",          # cpu, cuda, tensorrt
    nsfw_threshold=0.85,    # آستانه تشخیص
    safe_threshold=0.25,
    suspicious_threshold=0.60,
    cleanup_interval=100,   # پاکسازی حافظه
    intra_threads=2,        # نخ‌های ONNX
    inter_threads=1
)

detector = MoxraDetector(config)
```

### متغیرهای محیطی

```bash
# لینوکس/مک
export MOXRA_MODEL_TYPE="d"
export MOXRA_DEVICE="cpu"
export MOXRA_NSFW_THRESHOLD="0.85"

# ویندوز (CMD)
set MOXRA_MODEL_TYPE=d
set MOXRA_DEVICE=cpu
```

---

## 📊 آمار و مدیریت

```python
# دریافت آمار
stats = detector.get_stats()
print(f"تعداد تشخیص‌ها: {stats['inference_count']}")
print(f"دستگاه: {stats['device']}")
print(f"زمان اجرا: {stats['uptime_seconds']} ثانیه")

# پاکسازی حافظه
detector.cleanup()
```

---

## 🎯 دسته‌بندی‌ها

| نام | توضیح | رنگ |
|-----|-------|-----|
| **neutral** | محتوای ایمن و عادی | 🟢 |
| **sexy** | محتوای تحریک‌کننده | 🟡 |
| **porn** | محتوای مستهجن | 🔴 |
| **hentai** | انیمه مستهجن | 🟣 |
| **drawing** | نقاشی و هنر | 🔵 |

---

## 💡 مثال‌های کاربردی

### مثال ۱: بررسی دسته‌ای چند تصویر

```python
from moxra import MoxraDetector
import os

detector = MoxraDetector()
images = ["img1.jpg", "img2.jpg", "img3.jpg"]

for img in images:
    if os.path.exists(img):
        result = detector.classify_with_veil(img)
        status = "🚫 NSFW" if result['is_nsfw'] else "✅ SAFE"
        print(f"{img}: {status} ({result['dominant_category']})")
```

### مثال ۲: فیلتر خودکار تصاویر

```python
from moxra import MoxraDetector
import shutil

detector = MoxraDetector()

def filter_images(images, safe_folder="safe", nsfw_folder="nsfw"):
    for img in images:
        result = detector.classify_with_veil(img)
        dest = nsfw_folder if result['is_nsfw'] else safe_folder
        shutil.move(img, f"{dest}/{img}")

filter_images(["photo1.jpg", "photo2.jpg", "photo3.jpg"])
```

### مثال ۳: نمایش گرافیکی نتیجه

```python
from moxra import MoxraDetector

detector = MoxraDetector()
result = detector.classify_with_veil("image.jpg")

print("=" * 40)
print("📊 نتیجه تشخیص")
print("=" * 40)

for cat, prob in result['predictions'].items():
    bar = "█" * int(prob * 40)
    print(f"{cat:10} {prob*100:5.1f}% {bar}")

print("=" * 40)
print(f"امتیاز NSFW: {result['nsfw_score']*100:.1f}%")
print(f"وضعیت: {'🚫 نامناسب' if result['is_nsfw'] else '✅ ایمن'}")
print("=" * 40)
```

### مثال ۴: تشخیص با پیشرفت

```python
from moxra import MoxraDetector
import time

detector = MoxraDetector()

def classify_with_progress(image_path):
    print(f"⏳ در حال پردازش: {image_path}")
    start = time.time()
    
    result = detector.classify_with_veil(image_path)
    
    elapsed = time.time() - start
    print(f"✅ کامل شد در {elapsed:.2f} ثانیه")
    return result

result = classify_with_progress("large_image.jpg")
```

---

## 🚨 خطاها

| خطا | راه حل |
|-----|--------|
| `FileNotFoundError` | مسیر فایل را بررسی کنید |
| `ValueError` | فرمت فایل پشتیبانی نمی‌شود |
| `RuntimeError` | خطا در پردازش، دوباره امتحان کنید |

---

## 📄 مجوز

MIT License - استفاده آزاد برای پروژه‌های شخصی و تجاری

---

## 👨‍💻 توسعه‌دهنده

**ابوالفضل زارعی | Abolfazl Zarei**

<div align="center">
  <a href="https://github.com/AbolfazlZarei-dev">
    <img src="https://img.shields.io/badge/GitHub-دنبال_کنید-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <a href="https://t.me/SBCS_IR">
    <img src="https://img.shields.io/badge/تلگرام-دنبال_کنید-2CA5E0?style=for-the-badge&logo=telegram" alt="Telegram">
  </a>
  <a href="https://rubika.ir/NinjaCode">
    <img src="https://img.shields.io/badge/روبیکا-دنبال_کنید-FF6B6B?style=for-the-badge" alt="Rubika">
  </a>
  <a href="https://abolfazlzarei.sbs">
    <img src="https://img.shields.io/badge/وب‌سایت-مشاهده-4285F4?style=for-the-badge" alt="Website">
  </a>
</div>

---

## ⭐ حمایت

اگر این کتابخانه برای شما مفید بود:
- ⭐ به مخزن ستاره دهید
- 📢 با دیگران به اشتراک بگذارید
- 🐛 مشکلات را گزارش کنید

---

<div align="center">

**ساخته شده با ❤️ برای جامعه متن‌باز**

</div>
