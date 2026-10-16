import os
import time
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("MADRASATI_EMAIL")
PASSWORD = os.environ.get("MADRASATI_PASSWORD")

def run():
    if not EMAIL or not PASSWORD:
        print(" Error: Email or Password secrets are missing!")
        return

    with sync_playwright() as p:
        # تشغيل المتصفح بوضع Headless (بدون واجهة رسومية)
        browser = p.chromium.launch(headless=True)
        # محاكاة متصفح حقيقي لتفادي الحظر
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("⚡ 1. الذهاب إلى منصة مدرستي...")
        page.goto("https://schools.madrasati.sa/")
        page.wait_for_load_state("networkidle")

        # الضغط على الكادر الطلابي / الدخول بحساب مايكروسوفت
        try:
            # البحث عن زر الدخول بحساب الطلاب
            page.click("a:has-text('الدخول بحساب الكادر الطلابي')", timeout=10000)
        except Exception:
            print("لم يتم العثور على زر 'الكادر الطلابي' المباشر، جاري محاولة الدخول العام...")

        print("🔑 2. تسجيل الدخول ببيانات Microsoft...")
        # إدخال البريد الإلكتروني
        page.fill("input[type='email']", EMAIL)
        page.click("input[type='submit']")
        page.wait_for_timeout(3000)

        # إدخال كلمة المرور
        page.fill("input[type='password']", PASSWORD)
        page.click("input[type='submit']")
        page.wait_for_timeout(3000)

        # تخطي شاشة "Stay signed in?" إن وجدت
        try:
            if page.is_visible("input[id='idSIButton9']"):
                page.click("input[id='idSIButton9']")
        except Exception:
            pass

        page.wait_for_load_state("networkidle")
        print(" تم تسجيل الدخول بنجاح!")

        print(" 3. الانتقال إلى صفحة الواجبات اليومية...")
        page.goto("https://schools.madrasati.sa/Student/Assignments")
        page.wait_for_timeout(5000)

        # البحث عن الواجبات غير المحلولة
        # يختلف الـ Selector بحسب تصميم المنصة، هنا يتم البحث عن أزرار "حل الواجب"
        assignment_buttons = page.query_selector_all("text='حل الواجب'")

        if not assignment_buttons:
            print(" لا يوجد واجبات جديدة تتطلب الحل اليوم.")
        else:
            print(f" تم العثور على {len(assignment_buttons)} واجب(ات) لم تُحل بعد.")
            
            for index, btn in enumerate(assignment_buttons):
                print(f" جاري فتح الواجب رقم {index + 1}...")
                btn.click()
                page.wait_for_timeout(4000)

                # البحث عن الأسئلة واختيار الإجابة الأولى أو إدخال نص
                # اختيار الإجابات الخيارية (Radio Buttons / Options)
                radios = page.query_selector_all("input[type='radio']")
                if radios:
                    # اختيار أول خيار في كل سؤال
                    for radio in radios:
                        if not radio.is_checked():
                            radio.check(force=True)

                # الخانات النصية (إن وجدت)
                text_areas = page.query_selector_all("textarea, input[type='text']")
                for text_area in text_areas:
                    text_area.fill("تم الحل")

                # الضغط على زر الحفظ / التسليم
                submit_btn = page.query_selector("text='إظهار النتيجة'") or page.query_selector("text='حفظ'") or page.query_selector("text='تسليم'")
                if submit_btn:
                    submit_btn.click()
                    print(f" تم حل وتسليم الواجب رقم {index + 1}!")
                    page.wait_for_timeout(3000)
                
                # العودة لصفحة الواجبات
                page.goto("https://schools.madrasati.sa/Student/Assignments")
                page.wait_for_timeout(3000)

        browser.close()
        print(" اكتملت المهمة وتم تسجيل الخروج.")

if __name__ == "__main__":
    run()
