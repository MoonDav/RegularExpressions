import csv
import re
from pprint import pprint

# ---------- Чтение адресной книги ----------
with open("phonebook_raw.csv", encoding="utf-8") as f:
	rows = csv.reader(f, delimiter=",")
	contacts_list = list(rows)

header = contacts_list[0]
data = contacts_list[1:]


# ---------- TODO 1.1: Фамилия, Имя, Отчество ----------
def split_name(record):
	"""Первые три поля могут содержать ФИО в любом разбиении.
	Склеиваем их через пробел и split-ом разбиваем на части."""
	fio = " ".join(record[:3]).split()
	while len(fio) < 3:          # добиваем до трёх элементов
		fio.append("")
	return fio[:3] + record[3:]  # Ф, И, О + остальные поля


data = [split_name(rec) for rec in data]


# ---------- TODO 1.2: Телефоны ----------
PHONE_RE = re.compile(
	r"""
    (?:\+7|8)?              # код страны (может отсутствовать)
    \D*                     # любые нецифровые разделители
    (\d{3})                 # код оператора
    \D*
    (\d{3})                 # первые 3 цифры
    \D*
    (\d{2})                 # следующие 2
    \D*
    (\d{2})                 # последние 2
    (?:
        \s*(?:доб\.?|д\.?|ext\.?)\s*
        (\d+)               # добавочный
    )?
    """,
	re.VERBOSE,
)


def normalize_phone(phone: str) -> str:
	if not phone.strip():
		return ""
	match = PHONE_RE.search(phone)
	if not match:
		return phone              # не распознали — оставляем как есть
	a, b, c, d, ext = match.groups()
	result = f"+7({a}){b}-{c}-{d}"
	if ext:
		result += f" доб.{ext}"
	return result


for rec in data:
	rec[5] = normalize_phone(rec[5])


# ---------- TODO 1.3: Объединение дублей ----------
# Группируем по (lastname, firstname). Пустые поля дополняем.
# Если в новой записи телефон «богаче» (есть добавочный) — он имеет приоритет.
EXT_RE = re.compile(r"доб\.\d+")


def is_richer(new_val: str, old_val: str) -> bool:
	"""Новое значение считается «богаче», если в нём есть добавочный,
	а в старом его нет."""
	if not new_val.strip():
		return False
	if not old_val.strip():
		return True
	if EXT_RE.search(new_val) and not EXT_RE.search(old_val):
		return True
	return False


merged: dict[tuple[str, str], list[str]] = {}

for rec in data:
	key = (rec[0].strip().lower(), rec[1].strip().lower())
	if key not in merged:
		merged[key] = rec[:]
	else:
		existing = merged[key]
		for i in range(len(existing)):
			if not existing[i].strip() and rec[i].strip():
				existing[i] = rec[i]                 # обычное заполнение пустого поля
			elif i == 5 and is_richer(rec[i], existing[i]):
				existing[i] = rec[i]                 # телефон с добавочным важнее

contacts_list = [header] + list(merged.values())

# pprint(contacts_list)


# ---------- TODO 2: Сохранение результата ----------
with open("phonebook.csv", "w", encoding="utf-8", newline="") as f:
	datawriter = csv.writer(f, delimiter=",")
	datawriter.writerows(contacts_list)
