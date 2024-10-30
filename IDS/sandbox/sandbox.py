import os
import mimetypes
from pathlib import Path

class Sandbox:
    def __init__(self, ids, user="system"):
        # Путь для загрузки и временного хранения файлов
        self.upload_dir = Path("O:/Diplom/IDS/sandbox/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)  # Создание директории, если её нет

        # Параметры безопасности
        self.max_file_size = 5 * 1024 * 1024  # 5 МБ
        self.allowed_mime_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "image/png",
            "image/jpeg",
            "application/msword",
        ]
        self.allowed_extensions = [".pdf", ".docx", ".txt", ".png", ".jpeg", ".jpg", ".doc"]

        # Инициализация IDS для логирования событий
        self.ids = ids
        self.user = user

    def save_temp_file(self, uploaded_file):
        """Сохраняет загружаемый файл во временной папке для проверки и логирует это действие."""
        temp_path = self.upload_dir / uploaded_file.name
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            log_msg = f"Файл {uploaded_file.name} успешно записан во временную папку {temp_path}"
            print(f"[LOG] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return temp_path
        except Exception as e:
            log_msg = f"Ошибка записи файла {uploaded_file.name}: {e}"
            print(f"[ERROR] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return None

    def is_safe_file(self, file_path):
        """Проверка типа и размера файла с логированием результата."""
        try:
            if file_path.stat().st_size > self.max_file_size:
                log_msg = "Файл превышает допустимый размер."
                print(f"[LOG] {log_msg}")
                self.ids.log_event(self.user, log_msg)
                return False

            mime_type, _ = mimetypes.guess_type(file_path)
            file_extension = file_path.suffix.lower()
            
            print(f"[LOG] MIME-тип файла: {mime_type}")
            print(f"[LOG] Расширение файла: {file_extension}")

            if mime_type not in self.allowed_mime_types or file_extension not in self.allowed_extensions:
                log_msg = f"Недопустимый MIME-тип или расширение: {mime_type}, {file_extension}"
                print(f"[LOG] {log_msg}")
                self.ids.log_event(self.user, log_msg)
                return False

            return True
        except Exception as e:
            log_msg = f"Ошибка при проверке файла {file_path}: {e}"
            print(f"[ERROR] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return False

    def analyze_file(self, file_path):
        """Анализирует содержимое файла на предмет вредоносного содержимого с логированием результата."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                if b"<script>" in content or b"eval(" in content:
                    log_msg = "Обнаружен потенциально вредоносный контент."
                    print(f"[LOG] {log_msg}")
                    self.ids.log_event(self.user, log_msg)
                    return False
            log_msg = "Файл успешно прошел анализ содержимого."
            print(f"[LOG] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return True
        except Exception as e:
            log_msg = f"Ошибка анализа файла: {e}"
            print(f"[ERROR] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return False

    def process_file(self, temp_path):
        """Процесс проверки файла, принимает путь к уже сохранённому файлу и логирует результат."""
        try:
            if not self.is_safe_file(temp_path):
                os.remove(temp_path)
                log_msg = "Файл не прошел проверку безопасности."
                print(f"[LOG] {log_msg}")
                self.ids.log_event(self.user, log_msg)
                return log_msg

            if not self.analyze_file(temp_path):
                os.remove(temp_path)
                log_msg = "Файл содержит подозрительное содержимое."
                print(f"[LOG] {log_msg}")
                self.ids.log_event(self.user, log_msg)
                return log_msg

            log_msg = "Файл успешно прошел все проверки."
            print(f"[LOG] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return log_msg
        except Exception as e:
            os.remove(temp_path)
            log_msg = f"Ошибка анализа файла: {e}"
            print(f"[ERROR] {log_msg}")
            self.ids.log_event(self.user, log_msg)
            return log_msg
