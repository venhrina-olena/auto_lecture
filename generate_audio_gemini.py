import os
import glob
import wave
from google import genai
from google.genai import types

# --- CONFIGURATION (Google AI Studio) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash-preview-tts"
VOICE_NAME = "zephyr"   # 'zephyr' - один з високоякісних синтетичних голосів

# Промпт для контролю інтонації і швидкості читання:
# ВАЖЛИВО: Промпт має бути АНГЛІЙСЬКОЮ, щоб модель не перемикалась на український акцент
PROMPT_PREFIX = """You are a professional native American English lecturer and voiceover artist. Read the following text for a university student presentation. 
Your pronunciation must be perfect standard American English with absolutely no foreign accent. Speak at a moderate, measured pace. Enunciate clearly and make logical pauses between sentences. Do not rush. Here is the text to read:

"""

def generate_audio_from_notes(notes_dir):
    if not os.path.exists(notes_dir):
        print(f"❌ Помилка: Папку '{notes_dir}' не знайдено.")
        return

    # Зберігатимемо аудіо поруч із папкою notes (в папці audio)
    base_dir = os.path.dirname(notes_dir)
    audio_dir = os.path.join(base_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Перевірка наявності API ключа
    if not GEMINI_API_KEY:
        print("❌ Помилка: Змінна оточення GEMINI_API_KEY не знайдена. Будь ласка, вкажіть її у файлі .env або системних змінних.")
        return

    # Ініціалізація клієнта
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Знаходимо всі файли з нотатками
    note_files = sorted(glob.glob(os.path.join(notes_dir, "note_*.txt")))
    
    if not note_files:
        print(f"У папці {notes_dir} не знайдено файлів з нотатками.")
        return

    print(f"Знайдено нотаток: {len(note_files)}. Починаємо генерацію Gemini TTS...")

    for note_file in note_files:
        filename = os.path.basename(note_file)
        name_part = os.path.splitext(filename)[0]
        # output filename: audio_01.wav
        output_filename = name_part.replace("note_", "audio_") + ".wav"
        output_path = os.path.join(audio_dir, output_filename)
        
        # Читаємо текст нотатки
        with open(note_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
            
        if not text:
            print(f"Пропускаємо пустий файл: {filename}")
            continue
            
        print(f"Синтезуємо {filename} -> {output_filename}...")
        
        try:
            # Збираємо остаточний текст з промптом
            full_content = PROMPT_PREFIX + text

            # Звертаємося до Gemini
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=full_content,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=VOICE_NAME
                            )
                        )
                    )
                )
            )
            
            # Витягуємо PCM аудіодані та конвертуємо в стандартий WAV
            audio_saved = False
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        # Записуємо аудіодані як WAV файл (24kHz, 16-bit Mono - стандарт Gemini)
                        with wave.open(output_path, "wb") as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(24000)
                            wf.writeframes(part.inline_data.data)
                        
                        print(f"  [Виконано] Збережено до {output_filename}")
                        audio_saved = True
                        break # Виходимо після збереження першого аудіо-шматка
            
            if not audio_saved:
                print(f"  [Увага] Відповідь отримана, але аудіодані не знайдені: {filename}")

        except Exception as e:
            print(f"  [ПОМИЛКА] під час обробки {filename}: {e}")

    print("Пакетну генерацію успішно завершено.")

if __name__ == "__main__":
    print("-" * 50)
    print("🎙️ Скрипт для озвучки нотаток через Gemini 2.5 TTS (збереже wav у папку 'audio' поруч)")
    print("-" * 50)
    
    notes_dir = input("Введіть повний шлях до папки 'notes':\n> ").strip()
    
    # Видаляємо лапки, якщо користувач вставив шлях разом з ними
    if notes_dir.startswith('"') and notes_dir.endswith('"'):
        notes_dir = notes_dir[1:-1]
    if notes_dir.startswith("'") and notes_dir.endswith("'"):
        notes_dir = notes_dir[1:-1]
        
    print("-" * 50)
    
    generate_audio_from_notes(notes_dir)
