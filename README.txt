Инструкция для софта:
Для работы необходим Python версии 3.12+.
Перед началом откройте консоль и выполните команду:
pip install -r requirements.txt

(если возникли проблемы с pip, попробуйте прописать python -m ensurepip, если и это не поможет то попробуйте переустановить python)

После установки библиотеки следуйте этим шагам:
1. Получите API ключ и CX, следуя этому руководству на youtube: https://www.youtube.com/watch?v=D4tWHX2nCzQ
Ну, или вы можете попросить продавца сделать это за вас >:)
2. Замените API_KEY и CX в конце кода на свои.

Всё готово! Поисковиком можно пользоваться!
Далее всё просто, в интерфейсе есть всего 3 пункта:
1. Поиск
2. Настройки
3. Дорк пэйлоад

-Поиск-
Вставьте свой запрос здесь. Учтите, что это не Google, поэтому запрос обрабатывается как точное выражение без вариаций.
Например: "взлом баз данных", "стилер на python".
Но я вам рекомендую поэкспериментировать и отталкиваясь от своего опыта составлять запросы.

-Настройки-
Когда вы попадете в настройки откроется список сайтов по которым софт может искать информацию, выберите сайты на которых софт может искать информацию.
(Не рекомендуется использовать сразу много сайтов, консоль может забиться каким то одним сайтом, по моему опыту эффективные комбинации это telegra.ph + teletype.in, можно искать и на западных аналогах телеграфа, допустим medium.com)

-Дорк пэйлоад-
Нужен для поиска по Google.com (его нужно вставить в поисковик)
Используется если нужно больше результатов, но будет долгий подгруз и часто встречается капча.
Программа запросит ваш запрос и выдаст пэйлоад, использующий google dorks для более точного поиска.
Пример:
Введите запрос: "взлом баз данных"
взлом баз данных | intext:(взлом баз данных) site:telegra.ph | site:teletype.in)      

Обозначения:
Значок [+] рядом с названием указывает, что ссылка уже просматривалась ранее.
Пример:
[+] Прокси Антик Coinlist

В остальном интерфейс интуитивно понятен, за поддержкой обращайтесь на форум или телеграм @pentest_mentor, со всем помогу.
В файле dorks_guide.txt гайд по составлению запросов.



Инструкция для телеграм бота:

После того как в файле config.py есть API_KEY и CX, пришло время получить токен для бота
Пишем отцу ботов - @BotFather и создаем нового бота, даем ему любой никнейм и юзернейм.

/start
/newbot

После создания вы получити свой токен и должны будете вставить его в файл config.py, в переменную TG_API
А так же свой ID в переменную ALLOWED_USERS, я подробнее написал об этом в конфиге

После этого
Запустите файл tg_bot.py, если ошибок нет то скорее всего вы все сделали правильно
напишите /start вашему боту, если появилось меню то все готово и им можно пользоваться!
