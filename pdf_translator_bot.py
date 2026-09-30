import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
import PyPDF2

# التوكن الخاص بالبوت
TOKEN = "8931969050:AAHwADdFByq2VL8DYTis_RWd731rBNhpjh8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً بك! أرسل لي أي ملف PDF وسأقوم بترجمته إلى العربية.')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    # التأكد من أن الملف بصيغة PDF
    if not document.file_name.endswith('.pdf'):
        await update.message.reply_text('الرجاء إرسال ملف بصيغة PDF فقط.')
        return

    await update.message.reply_text('استلمت الملف. جاري قراءة النص والترجمة، يرجى الانتظار...')

    # تنزيل الملف
    file = await context.bot.get_file(document.file_id)
    file_path = "temp_file.pdf"
    await file.download_to_drive(file_path)

    try:
        # قراءة النص من ملف الـ PDF
        reader = PyPDF2.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"

        if not text.strip():
            await update.message.reply_text('عذراً، لم أتمكن من استخراج نص من هذا الملف (قد يكون عبارة عن صور).')
            return

        # ترجمة النص إلى العربية
        translator = GoogleTranslator(source='auto', target='ar')

        # تقسيم النص لتجنب تجاوز الحد المسموح للترجمة
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        translated_text = ""
        for chunk in chunks:
            translated_text += translator.translate(chunk) + "\n"

        # حفظ النص المترجم في ملف نصي وإرساله
        output_filename = "Translated_Document.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(translated_text)

        await update.message.reply_document(
            document=open(output_filename, "rb"),
            filename="Translated_Document.txt",
            caption="تمت الترجمة بنجاح!"
        )

    except Exception as e:
        await update.message.reply_text('حدث خطأ أثناء الترجمة. حاول مرة أخرى.')
    finally:
        # حذف الملفات المؤقتة لتنظيف السيرفر
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("Translated_Document.txt"):
            os.remove("Translated_Document.txt")

def main():
    # تشغيل البوت
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling()

if __name__ == '__main__':
    main()
