import os
import mimetypes
from pathlib import Path

class Sandbox:
    def __init__(self):
        # Путь для загрузки и временного хранения файлов
        self.upload_dir = Path("O:/Diplom/IDS/sandbox/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)  # Создание директории, если её нет

        # Параметры безопасности
        self.max_file_size = 5 * 1024 * 1024  # 5 МБ

        # MIME-типы и расширения файлов, которые разрешены для загрузки
        self.allowed_mime_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",  # Разрешаем текстовые файлы
            "image/png",   # Разрешаем PNG
            "image/jpeg",  # Разрешаем JPEG
            "application/msword",  # Разрешаем .doc файлы
        ]
        
        self.allowed_extensions = [".pdf", ".docx", ".txt", ".png", ".jpeg", ".jpg", ".doc"]

    def save_temp_file(self, uploaded_file):
        """Сохраняет загружаемый файл во временной папке для проверки."""
        temp_path = self.upload_dir / uploaded_file.name
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print(f"[LOG] Файл {uploaded_file.name} успешно записан в {temp_path}")
            return temp_path
        except Exception as e:
            print(f"[ERROR] Ошибка записи файла {uploaded_file.name}: {e}")
            return None

    def is_safe_file(self, file_path):
        """Проверка типа и размера файла."""
        try:
            # Проверка размера
            if file_path.stat().st_size > self.max_file_size:
                print("[LOG] Файл превышает допустимый размер.")
                return False

            # Определение MIME-типа и расширения
            mime_type, _ = mimetypes.guess_type(file_path)
            file_extension = file_path.suffix.lower()  # Получаем расширение файла
            
            print(f"[LOG] MIME-тип файла: {mime_type}")
            print(f"[LOG] Расширение файла: {file_extension}")

            # Проверка MIME-типа и расширения
            if mime_type not in self.allowed_mime_types or file_extension not in self.allowed_extensions:
                print(f"[LOG] Недопустимый MIME-тип или расширение: {mime_type}, {file_extension}")
                return False

            return True
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке файла {file_path}: {e}")
            return False

    def analyze_file(self, file_path):
        """Анализирует содержимое файла на предмет вредоносного содержимого."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                if b"<script>" in content or b"eval(" in content:
                    print("[LOG] Обнаружен потенциально вредоносный контент.")
                    return False
            print("[LOG] Файл успешно прошёл анализ содержимого.")
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка анализа файла: {e}")
            return False

    def process_file(self, temp_path):
        """Процесс проверки файла, принимает путь к уже сохранённому файлу."""
        try:
            # Проверка безопасности
            if not self.is_safe_file(temp_path):
                os.remove(temp_path)  # Удаляем файл, если он не прошёл проверку
                return "Файл не прошел проверку безопасности."

            # Анализ содержимого
            if not self.analyze_file(temp_path):
                os.remove(temp_path)  # Удаляем файл, если он содержит подозрительное содержимое
                return "Файл содержит подозрительное содержимое."

            print("[LOG] Файл успешно прошел все проверки.")
            return "Файл успешно прошел проверку."
        except Exception as e:
            os.remove(temp_path)  # Удаляем файл при возникновении ошибки
            return f"Ошибка анализа файла: {e}"
