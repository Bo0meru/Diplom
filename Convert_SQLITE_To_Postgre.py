# Конвертация data.json из UTF-16 LE в UTF-8
input_file = "users.json"
output_file = "users_utf8.json"

with open(input_file, "r", encoding="utf-16") as infile:
    content = infile.read()

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write(content)

print(f"Файл {output_file} успешно создан в UTF-8!")
