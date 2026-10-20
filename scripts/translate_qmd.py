import os
from google import genai
import time
from google.genai import types

# --- НАЛАШТУВАННЯ ---
# 1. Отримайте API ключ тут: https://aistudio.google.com/app/apikey
# Завантажуємо ключ зі змінних оточення (або .env файлу)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Вибір моделі (замінено на доступну зі списку)
MODEL_NAME = "gemini-2.5-flash"

# Системний промпт для збереження структури
SYSTEM_INSTRUCTION = """
Ти — професійний перекладач з української на англійську. 
Твоя задача — перекласти наданий документ у форматі Quarto Markdown (.qmd).

КРИТИЧНІ ПРАВИЛА:
1. Збережи абсолютно всі теги Markdown, HTML, блоки коду (```), R/Python код та LaTeX формули без жодних змін.
2. YAML-шапку (frontmatter між ---) залишаємо з оригінальними ключами, перекладаємо лише текстові значення (наприклад, title, subtitle).
3. Не додавай від себе жодних коментарів до перекладу. Повертай ЛИШЕ перекладений текст документа у такому ж форматі.
"""

def translate_qmd_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Помилка: Файл не знайдено - {file_path}")
        return

    filename = os.path.basename(file_path)
    
    if "ua" not in filename.lower():
        print(f"❌ Помилка: Файл '{filename}' не містить 'ua' у назві.")
        return
        
    # Формуємо нове ім'я файлу: замінюємо "ua" на "eng"
    if "ua" in filename:
        output_filename = filename.replace("ua", "eng")
    elif "UA" in filename:
        output_filename = filename.replace("UA", "ENG")
    elif "Ua" in filename:
        output_filename = filename.replace("Ua", "Eng")

    output_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), output_filename)
        
    print(f"Обробка файлу: {filename} ...")
    
    # перевірка наявності API ключа
    if not GEMINI_API_KEY:
        print("❌ Помилка: Змінна оточення GEMINI_API_KEY не знайдена. Будь ласка, вкажіть її у файлі .env або системних змінних.")
        return

    # ініціалізація нового API
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Читаємо оригінальний файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        print(f"Файл {filename} порожній. Пропускаємо.")
        return
        
    try:
        # Відправляємо запит до Gemini
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        
        # Зберігаємо перекладений результат
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"✅ Успішно перекладено та збережено як '{output_filename}' в тій же папці.")
        
    except Exception as e:
        print(f"❌ Помилка під час перекладу {filename}: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("📝 Скрипт для перекладу .qmd файлів (UA -> ENG)")
    print("-" * 50)
    
    file_path = input("Введіть повний шлях до .qmd файлу для перекладу:\n> ").strip()
    
    # Видаляємо лапки, якщо користувач вставив шлях разом з ними (часто буває при копіюванні в Windows)
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
    if file_path.startswith("'") and file_path.endswith("'"):
        file_path = file_path[1:-1]
        
    print("-" * 50)
    translate_qmd_file(file_path)

