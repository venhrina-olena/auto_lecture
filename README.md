# Набір скриптів автоматизації підготовки лекцій

Дана директорія містить скрипти для реалізації напівавтоматизованого пайплайну (Human-in-the-Loop) створення самовідтворюваних англомовних лекцій.

## Структура компонентів

| Файл | Призначення | Технології |
|---|---|---|
| [`translate_qmd.py`](file:///scripts/translate_qmd.py) | Переклад Quarto Markdown (`.qmd`) зі збереженням розмітки, формул і коду | Python, `google-genai` (`gemini-2.5-flash`) |
| [`extract_notes_from_pptx.py`](file:///scripts/extract_notes_from_pptx.py) | Експорт нотаток доповідача зі слайдів PPTX у текстові файли `notes/note_*.txt` | Python, `python-pptx` |
| [`generate_audio_gemini.py`](file:///scripts/generate_audio_gemini.py) | Пакетний синтез англомовного аудіо мовлення з нотаток | Python, `google-genai` (`gemini-2.5-flash-preview-tts`), `wave` |
| [`macros.vba`](file:///scripts/macros.vba) | Макрос для PowerPoint: імпорт аудіодоріжок, приховання та автосинхронізація таймінгу | VBA (Visual Basic for Applications) |

## Встановлення та налаштування

1. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```

2. Налаштуйте API-ключ:
   - Скопіюйте файл `.env.example` у файл `.env`:
     ```bash
     cp .env.example .env
     ```
   - Відкрийте `.env` та вкажіть ваш дійсний ключ Google AI Studio:
     ```env
     GEMINI_API_KEY=AIzaSy...
     ```

## Порядок виконання

1. **Переклад:**
   ```bash
   python translate_qmd.py
   ```
2. **Створення презентації та нотаток:**
   - Згенеруйте PPTX у NotebookLM / Gemini Notebook.
   - За допомогою Gem-бота узгодьте текст виступу для кожного слайда та вставте його у нотатки слайдів PPTX.
3. **Експорт нотаток:**
   ```bash
   python extract_notes_from_pptx.py
   ```
4. **Синтез мовлення:**
   ```bash
   python generate_audio_gemini.py
   ```
5. **Вбудовування в PowerPoint:**
   - Відкрийте презентацію в PowerPoint.
   - Натисніть `Alt + F11`, вставте модуль із кодом [`macros.vba`](file:///scripts/macros.vba).
   - Запустіть макрос `InsertAudio_With_Prefix`. Слайди автоматично отримають аудіодоріжки та налаштований час показу.
