import json

with open('text.json', encoding='utf-8') as f:
    text = json.load(f)

jobs = []
softs = []

for i in text:
    if i.split('_')[0] == "job":
        jobs.append(text[i])
    elif i.split('_')[0] == "soft":
        softs.append(text[i])

jobs_checked = []
for i in jobs:
    jobs_checked.append('✅ ' + i)

softs_checked = []
for i in softs:
    softs_checked.append('✅ ' + i)


token = '2030809815:AAGTfAPXNnHygOLkttrlaD7-tziFFlhhFz8'
hlp = "*Подобрать для меня* - подбор вакансий на основе Вашего профиля\n\n" \
      "*Посмотреть все* - просмотреть все вакансии\n\n" \
      "*Мои отклики* - просмотреть вакансии, на которые Вы откликнулись\n\n" \
      "*FAQ* - полезные советы\n\n" \
      "*Обновить профиль* - обновить параметры Вашего профиля\n\n" \
      "*Помощь* - задать вопрос, дать обратную связь или подобрать вакансию, если не нашли нужную"
