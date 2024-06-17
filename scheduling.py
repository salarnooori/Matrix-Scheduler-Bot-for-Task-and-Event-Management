from opsdroid.skill import Skill
from opsdroid.matchers import match_regex
import re
import json
import os
from string import printable

data = []


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
        json_file.write('\n')

def load_from_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as new_file:
          new_file.write("[]")

    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

"""
detection statement of message
"""

def detect_statements(input_string):
    input_string = str(input_string)
    statements = []

    patterns = {
        "یادم باشه": r"یادم\s+باشه",
        "لغو کن": r"لغو\s+کن",
        "تغییر بده": r"تغییر\s+بده",
        "انجام شد": r"(انجام\s+شد|تمام\s+شد)",
        "نمایش بده": r'برنامه\s+(.*?)\s+(?:چیست|بگو|نشان\s+بده|نمایش\s+بده)'
    }

    for statement, pattern in patterns.items():
        if re.search(pattern, input_string):
            statements.append(statement)

    return statements

def handle_message(input_string):
  response = ''
  detected_statements = detect_statements(input_string)
  if detected_statements[0] == 'یادم باشه':
    response = add_new_item(input_string)
  elif detected_statements[0] == 'لغو کن':
    response = cancel_item(input_string)
  elif detected_statements[0] == 'تغییر بده':
    response = change_item(input_string)
  elif detected_statements[0] == 'انجام شد':
    response = done_item(input_string)
  elif detected_statements[0] == 'نمایش بده':
    response = show_items(input_string)
  else:
    response = 'پیام ورودی قابل شناسایی نیست.'
  return response

"""
add new schedule to application.
"""

def extract_schedule_info(text):
    key_phrases = ["یادم باشه", "صبح|ظهر|عصر|شب", "تاریخ", "ساعت"]
    time_pattern = r'(?:\d{1,2}:\d{1,2}|ساعت\s+\d{1,2})\s*(?:بعد\s+از\s+ظهر|بعد\s+از\s+صبح)?'
    date_pattern = r'(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:جمعه|شنبه|یک‌شنبه|دوشنبه|سه‌شنبه|چهارشنبه|پنج‌شنبه)\s+(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+ماه\s+امسال)|(?:عید\s+امسال)|(?:عید\s+بعد)|(?:امروز)|(?:صبح)|(?:ظهر)|(?:شب)|(?:عصر)|(?:دیروز)|(?:فردا)|(?:پنج\s+روز\s+بعد)|(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند))'
    each_pattern = r'هر\s+(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:هر\s+روز|هر\s+سال)'
    period_pattern = r'(\d+\s+بار)|هر\s+روز|\d+\s+(?:بار|دقیقه|ساعت|روز|هفته|ماه|سال)'
    counts_pattern = r'(?:یک|دو|سه|چهار|پنج|شش|هفت|هشت|نه|ده|یازده|دوازده|سیزده|چهارده|پانزده|شانزده|هفده|هجده|نوزده|بیست)\s+بار|1\s+بار'

    schedule_info = []

    sentences = re.split(r'[.؛]', text)

    for sentence in sentences:
        if any(phrase in sentence for phrase in key_phrases):
            times = re.findall(time_pattern, sentence)
            dates = re.findall(date_pattern, sentence)
            eaches = re.findall(each_pattern, sentence)
            counts_number = re.findall(counts_pattern, sentence)
            period_match = re.search(period_pattern, sentence)

            if period_match:
                period = period_match.group(0)
                frequency_match = re.search(r'(\d+)\s+بار', period)
                if frequency_match:
                    frequency = int(frequency_match.group(1))
                else:
                    frequency = 1
            else:
                period = "یک بار"
                frequency = 1

            task_name = re.split("|".join(key_phrases), sentence)[-1].strip()
            time_tmp = ""

            if dates:
              dd = ""
              for item in dates:
                dd += item + " "
                task_name = task_name.replace(item, "")
              time_tmp += dd


            if times:
              tt = ""
              for item in times:
                tt += item
                task_name = task_name.replace(item, "")
              time_tmp += tt

            time_tmp = time_tmp.replace('در تاریخ', '').replace('در', '').replace(' روز', '')

            if time_tmp == "":
              if eaches:
                time_tmp = eaches[0]
                task_name = task_name.replace(eaches[0], "")
              if counts_number:
                period = counts_number[0]
                task_name = task_name.replace(counts_number[0], "")


            task_info = {"name": task_name,"time": time_tmp,"period": period,"done": False,"cancel": False}
            schedule_info.append(task_info)

    return schedule_info

def add_new_item(input):
  response = ''
  schedule_info = extract_schedule_info(input)

  if schedule_info:
    data = load_from_json("data.json")
    for item in schedule_info:
      data.append(item)

    save_to_json(data, "data.json")

    response += "این کار به برنامه اضافه شد." + "\n"
    response += str(schedule_info) + "\n"
  else:
    response += 'عبارت ورودی قابل شناسایی نیست.'

  return response

"""tests

input_text = "یادم باشه 14 اردیبهشت 1403 با ممد برم بیرون."
data = handle_message(input_text)

input_text = "یادم باشه فردا ساعت 9 صبح ریش سجاد رو بزنم"
data = handle_message(input_text)

input_text = "یادم باشه هر سال دو بار خون اهدا کنم."
data = handle_message(input_text)

input_text = " یادم باشه ظهر فردا آشغال ها رو دم در بزارم"
data = handle_message(input_text)

input_text = " یادم باشه فردا ساعت 5 عصر دو ساعت برم پیاده روی."
data = handle_message(input_text)

input_text = "یادم باشه امروز برم پارک.یادم باشه فردا برم سالن."
data = handle_message(input_text)

for item in data:
  print(item)

"""

def calculate_similarity(text1, text2):
    words_text1 = set(text1.split())
    words_text2 = set(text2.split())

    common_words_count = len(words_text1.intersection(words_text2))

    similarity_percentage = (common_words_count / len(words_text1)) * 100

    return similarity_percentage

def cancel_schedule_info(text):
    key_phrases = ["روز", "صبح|ظهر|عصر|شب", "تاریخ", "ساعت"]
    time_pattern = r'(?:\d{1,2}:\d{1,2}|ساعت\s+\d{1,2})\s*(?:بعد\s+از\s+ظهر|بعد\s+از\s+صبح)?'
    date_pattern = r'(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:جمعه|شنبه|یک‌شنبه|دوشنبه|سه‌شنبه|چهارشنبه|پنج‌شنبه)\s+(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+ماه\s+امسال)|(?:عید\s+امسال)|(?:عید\s+بعد)|(?:امروز)|(?:صبح)|(?:ظهر)|(?:شب)|(?:عصر)|(?:دیروز)|(?:فردا)|(?:پنج\s+روز\s+بعد)|(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند))'
    each_pattern = r'هر\s+(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:هر\s+روز|هر\s+سال)'
    period_pattern = r'(\d+\s+بار)|هر\s+روز|\d+\s+(?:بار|دقیقه|ساعت|روز|هفته|ماه|سال)'
    counts_pattern = r'(?:یک|دو|سه|چهار|پنج|شش|هفت|هشت|نه|ده|یازده|دوازده|سیزده|چهارده|پانزده|شانزده|هفتده|هجده|نوزده|بیست)\s+بار|1\s+بار'

    schedule_info = []

    sentences = re.split(r'[.؛]', text)

    for sentence in sentences:
        if any(phrase in sentence for phrase in key_phrases):
            times = re.findall(time_pattern, sentence)
            dates = re.findall(date_pattern, sentence)
            eaches = re.findall(each_pattern, sentence)
            counts_number = re.findall(counts_pattern, sentence)
            period_match = re.search(period_pattern, sentence)

            if period_match:
                period = period_match.group(0)
                frequency_match = re.search(r'(\d+)\s+بار', period)
                if frequency_match:
                    frequency = int(frequency_match.group(1))
                else:
                    frequency = 1
            else:
                period = "یک بار"
                frequency = 1

            task_name_match = re.search(r'^.*?(?=در\s+هر|در\s+تاریخ|در\s+ساعت|در\s+روز)', sentence)
            if task_name_match:
                task_name = task_name_match.group(0).strip()
            else:
                task_name = ""

            time_tmp = ""

            if dates:
                dd = ""
                for item in dates:
                    dd += item + " "
                    task_name = task_name.replace(item, "")
                time_tmp += dd

            if times:
                tt = ""
                for item in times:
                    tt += item
                    task_name = task_name.replace(item, "")
                time_tmp += tt

            time_tmp = time_tmp.replace('در تاریخ', '').replace('در', '').replace(' روز', '')

            if time_tmp == "":
                if eaches:
                    time_tmp = eaches[0]
                    task_name = task_name.replace(eaches[0], "")
                if counts_number:
                    period = counts_number[0]
                    task_name = task_name.replace(counts_number[0], "")

            task_info = {"name": task_name,"time": time_tmp,"period": period,"done": False,"cancel": False}
            schedule_info.append(task_info)

    return schedule_info

def cancel_item(input):
  response = ''
  schedule_info = cancel_schedule_info(input)

  if schedule_info:
    cancel = False
    for i in range(len(data)):
      if calculate_similarity(data[i]['name'], schedule_info[0]['name']) > 60 and calculate_similarity(data[i]['time'], schedule_info[0]['time']) > 60:
        cancel = True
        data[i]['cancel'] = "True"
        save_to_json(data, "data.json")
        response += 'این کار لغو شد.' + '\n'
        response += str(data[i]) + '\n'
        break

    if cancel == False:
      response += "هیج کار برای لغو کردن با این مشخصات در برنامه پیدا نشد" + '\n'
      response += str(schedule_info)

  else:
    response += 'عبارت ورودی قابل شناسایی نیست.'

  return response

"""tests

input_message = 'بیرون رفتن با ممد در تاریخ 14 اردیبهشت 1403 را لغو کن.'
data = handle_message(input_message)

input_message = 'اهدا کردن خون هر سال را لغو کن.'
data = handle_message(input_message)

input_message = 'اهدا کردن خون در تاریخ هر سال را لغو کن.'
data = handle_message(input_message)

input_message = 'خرید نان در تاریخ 22 بهمن 1402  5 بار را لغو کن.'
data = handle_message(input_message)

"""

def change_schedule_info(text):
    start_pattern = r'(?:زمان|تاریخ)\b'
    name_pattern = r'\b(?:زمان|تاریخ)\s+(.*?)\s+در\b'
    time_pattern = r'در\b\s*(.*?)\s+را به\b'
    new_time_pattern = r'را به\b\s+(.*?)\s+تغییر\b'

    schedule_info = []

    sentences = re.split(r'[.؛]', text)

    for sentence in sentences:
      if sentence.strip() != '':
        name = None
        time = None
        new_time = None

        start_match = re.search(start_pattern, text)
        name_match = re.search(name_pattern, text)
        time_match = re.search(time_pattern, text)
        new_time_match = re.search(new_time_pattern, text)

        if all(match is not None for match in [start_match, name_match, time_match, new_time_match]):
            name = name_match.group(1).strip()
            time = time_match.group(1).strip()
            new_time = new_time_match.group(1).strip()

        if name != None or time != None or new_time != None:
          task_info = {"name": name, "time": time, "new_time": new_time}
          schedule_info.append(task_info)

    return schedule_info

def change_item(input):
  response = ''
  schedule_info = change_schedule_info(input)
  if schedule_info:
    change = False
    for i in range(len(data)):
      if calculate_similarity(data[i]['name'], schedule_info[0]['name']) > 60:
        if (str(data[i]['time'])).find(str(schedule_info[0]['time'])) == -1:
          change = True
          data[i]['time'] = str(schedule_info[0]['new_time'])
          save_to_json(data, "data.json")
          response += 'برنامه زمانی این کار تغییر کرد.' + '\n'
          response += str(data[i])
          break
        elif calculate_similarity(data[i]['time'], schedule_info[0]['time']) < 90:
          change = True
          data[i]['time'] = str(schedule_info[0]['time']) + " " + str(schedule_info[0]['new_time'])
          save_to_json(data, "data.json")
          response += 'برنامه زمانی این کار تغییر کرد.' + '\n'
          response += str(data[i])
          break
        else:
          change = True
          data[i]['time'] = str(schedule_info[0]['new_time'])
          save_to_json(data, "data.json")
          response += 'برنامه زمانی این کار تغییر کرد.' + '\n'
          response += str(data[i])
          break

    if change == False:
      response += "هیج کار برای لغو کردن با این مشخصات در برنامه پیدا نشد" + '\n'
      response += str(schedule_info)

  else:
    response += 'عبارت ورودی قابل شناسایی نیست.'

  return response

"""tests

input_message = "زمان تماس با دوستم در 12 فروردین را به 9:30 شب تغییر بده."
data = handle_message(input_message)

input_message = "یادم باشه در تاریخ 12 فروردین ساعت 5 صبح با دوستم تماس بگیرم."
data = handle_message(input_message)

input_message = "زمان تماس با دوستم در 12 فروردین را به 9:30 شب تغییر بده."
data = handle_message(input_message)

input_message = "تاریخ اهدا خون کردن در هر سال را به هر ماه تغییر بده."
data = handle_message(input_message)

"""

def done_schedule_info(text):
    key_phrases = ["روز", "صبح|ظهر|عصر|شب", "تاریخ", "ساعت", "انجام شد", "تمام شد"]
    time_pattern = r'(?:\d{1,2}:\d{1,2}|ساعت\s+\d{1,2})\s*(?:بعد\s+از\s+ظهر|بعد\s+از\s+صبح)?'
    date_pattern = r'(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:جمعه|شنبه|یک‌شنبه|دوشنبه|سه‌شنبه|چهارشنبه|پنج‌شنبه)\s+(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+ماه\s+امسال)|(?:عید\s+امسال)|(?:عید\s+بعد)|(?:امروز)|(?:صبح)|(?:ظهر)|(?:شب)|(?:عصر)|(?:دیروز)|(?:فردا)|(?:پنج\s+روز\s+بعد)|(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند))'

    schedule_info = []

    sentences = re.split(r'[.؛]', text)

    for sentence in sentences:
        if any(phrase in sentence for phrase in key_phrases):
            times = re.findall(time_pattern, sentence)
            dates = re.findall(date_pattern, sentence)

            task_name_match = re.search(r'^.*?(?=تمام\s+شد|انجام\s+شد)', sentence)
            if task_name_match:
                task_name = task_name_match.group(0).strip()
            else:
                task_name = ""

            time_tmp = ""

            if dates:
                dd = ""
                for item in dates:
                    dd += item + " "
                    task_name = task_name.replace(item, "")
                time_tmp += dd

            if times:
                tt = ""
                for item in times:
                    tt += item
                    task_name = task_name.replace(item, "")
                time_tmp += tt

            time_tmp = time_tmp.replace('در تاریخ', '').replace('در', '').replace(' روز', '')
            task_name = task_name.replace('کار', '').replace(time_tmp, '').replace('در تاریخ', '').replace('در روز', '')

            task_info = {"name": task_name,"time": time_tmp,"period": None,"done": True,"cancel": False}
            schedule_info.append(task_info)

    return schedule_info

def done_item(input):
  response = ''
  schedule_info = done_schedule_info(input)
  if schedule_info:
    done = False
    for i in range(len(data)):
      if calculate_similarity(data[i]['name'], schedule_info[0]['name']) > 60:
        if schedule_info[0]['time'] != '':
          if calculate_similarity(data[i]['time'], schedule_info[0]['time']) > 80:
            done = True
            data[i]['done'] = "True"
            save_to_json(data, "data.json")
            response += 'این کار انجام شد.' + '\n'
            response += str(data[i])
            break
        else:
          done = True
          data[i]['done'] = "True"
          save_to_json(data, "data.json")
          response += 'این کارانجام شد.' + '\n'
          response += str(data[i])
          break

    if done == False:
      response += "هیج کار برای تمام شدن با این مشخصات در برنامه پیدا نشد"
      response += str(schedule_info)

  else:
    response += 'عبارت ورودی قابل شناسایی نیست.'

  return response

"""tests

input_message = 'کار اهدا کردن خون انجام شد.'
data = handle_message(input_message)

input_message = 'کار اهدا کردن خون در تاریخ 15 تیر انجام شد.'
data = handle_message(input_message)

"""

def show_schedule_info(text):
    key_phrases = ["برنامه", "نشان بده", "نمایش بده", "بگو"]
    time_pattern = r'(?:\d{1,2}:\d{1,2}|ساعت\s+\d{1,2})\s*(?:بعد\s+از\s+ظهر|بعد\s+از\s+صبح)?'
    date_pattern = r'(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:جمعه|شنبه|یک‌شنبه|دوشنبه|سه‌شنبه|چهارشنبه|پنج‌شنبه)\s+(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+\d{2,4})|(?:\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+ماه\s+امسال)|(?:عید\s+امسال)|(?:عید\s+بعد)|(?:امروز)|(?:صبح)|(?:ظهر)|(?:شب)|(?:عصر)|(?:دیروز)|(?:فردا)|(?:پنج\s+روز\s+بعد)|(?:در\s+تاریخ\s+\d{1,2}\s+(?:فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند))'
    period_pattern = r'(?:روزانه|ماهانه|سالانه|هفتگی)'


    period_mapping = {
        "سالانه": "هر سال",
        "روزانه": "هر روز",
        "هفتگی": "هر هفته",
        "ماهانه": "هر ماه"
    }

    schedule_info = []

    sentences = re.split(r'[.؟؛]', text)

    for sentence in sentences:
        if any(phrase in sentence for phrase in key_phrases):
            times = re.findall(time_pattern, sentence)
            dates = re.findall(date_pattern, sentence)
            period = re.findall(period_pattern, sentence)

            time_tmp = ""
            if dates:
                dd = ""
                for item in dates:
                    dd += item + " "
                time_tmp += dd

            if times:
                tt = ""
                for item in times:
                    tt += item
                time_tmp += tt

            time_tmp = time_tmp.replace('در تاریخ', '').replace('در', '').replace(' روز', '')

            task_info = {"time": time_tmp,"period": period_mapping[period[0]] if period else None}
            schedule_info.append(task_info)

    return schedule_info

def show_items(input):
  response = ''
  schedule_info = show_schedule_info(input)

  show_list = []

  if schedule_info:
    for i in range(len(data)):
      if ( (str(data[i]['time']).strip().find(schedule_info[0]['time'].strip()) != -1) if schedule_info[0]['time'] != '' else False) or ( (calculate_similarity(data[i]['time'], schedule_info[0]['period']) > 90) if schedule_info[0]['period'] != None else False ):
        show_list.append(data[i])

    if show_list:
      response += ('برنامه های مطابق با این زمان') + '\n'
      response += str(schedule_info) + '\n'
      response += ('---------------------------------------') + '\n'
      for item in show_list:
        response += str(item) + '\n'
    else:
      response += ('هیج برنامه این مطابق این زمان پیدا نشد.') + '\n'
      response += str(schedule_info)

  else:
    response += ('عبارت ورودی قابل شناسایی نیست.')

  return response

"""tests

input_message = 'برنامه ام در تاریخ 12 فروردین چیست ?'
data = handle_message(input_message)

input_message = 'برنامه ماهانه ام را بگو'
data = handle_message(input_message)


"""

class ScheduleSkill(Skill):
    @match_regex(r'.*')
    async def hello(self, message):
        response = handle_message(message.text)
        await message.respond(response)
        