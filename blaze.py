# -*- coding: utf-8 -*-
"""
BLAZE RUST — Wiki сайт сервера (Flask, один файл)

Локальный запуск:
    pip install flask
    python blaze.py

На хостинге (RelaxDev / Render и т.п.):
    gunicorn -b 0.0.0.0:$PORT blaze:app

Сборка статики (для GitHub Pages, необязательно):
    python blaze.py --build --base "/blazerust"
"""

import sys
import os
import shutil

from flask import Flask, render_template_string, abort

app = Flask(__name__)

# Принудительно отдаём ответ как HTML-страницу,
# иначе некоторые хостинги шлют text/plain и браузер показывает теги как текст
@app.after_request
def force_html(response):
    if response.content_type.startswith("text/"):
        response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

ONLINE = 6
SERVER_IP = "46.174.48.219:28015"
DISCORD = "https://discord.gg/blazerust"
TELEGRAM_CHANNEL = "https://t.me/blazerust_tg"
TELEGRAM_CHAT = "https://t.me/BlazeRust_Chat"

# ---------------------------------------------------------------------------
# Структура навигации
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Правила", [
        ("rules-intro", "Вводные правила"),
        ("rules-main", "Основные правила"),
        ("donate", "Соглашение на донат"),
    ]),
    ("Для новичков", [
        ("info-start", "Как начать"),
        ("info-privileges", "Привилегии и VIP"),
        ("info-commands", "Команды чата"),
        ("info-clans", "Как создать клан"),
    ]),
    ("Поддержка", [
        ("support-complaint", "Как подать жалобу"),
        ("support-punishments", "Наказания"),
    ]),
    ("Инструкции", [
        ("info-steamid", "Как узнать SteamID"),
        ("info-connect", "Подключение connect"),
    ]),
]

FLAT = [slug for _, items in SECTIONS for slug, _ in items]


def find_cat(slug):
    for cat, items in SECTIONS:
        for s, _ in items:
            if s == slug:
                return cat
    return ""


# ---------------------------------------------------------------------------
# Помощники разметки
# ---------------------------------------------------------------------------
def related(items):
    cards = "".join(
        '<a class="related-card reveal" href="/page/%s"><small>Читать далее</small>%s</a>'
        % (slug, title)
        for slug, title in items
    )
    return '<div class="related"><h3>Похожие статьи</h3><div class="related-grid">%s</div></div>' % cards


def callout(kind, title, text):
    return '<div class="callout %s reveal"><div><b>%s</b><p>%s</p></div></div>' % (kind, title, text)


def pager(slug):
    idx = FLAT.index(slug)
    prev_s = FLAT[idx - 1] if idx > 0 else None
    next_s = FLAT[idx + 1] if idx < len(FLAT) - 1 else None
    out = '<div class="pager">'
    if prev_s:
        out += '<a class="pager-btn prev reveal" href="/page/%s"><span>← Назад</span><strong>%s</strong></a>' % (
            prev_s, PAGES[prev_s]["title"])
    if next_s:
        out += '<a class="pager-btn next reveal" href="/page/%s"><span>Далее →</span><strong>%s</strong></a>' % (
            next_s, PAGES[next_s]["title"])
    out += "</div>"
    return out


# ---------------------------------------------------------------------------
# Контент страниц
# ---------------------------------------------------------------------------
PAGES = {}

PAGES["rules-intro"] = {
    "title": "Вводные правила",
    "html": '''
<p class="lead">Базовые положения проекта BLAZE RUST. Прочитай их до первого захода — это поможет избежать недопониманий и спорных ситуаций.</p>

<h2>Общие положения</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">01</span><div><strong>Незнание правил не освобождает от ответственности</strong><p>Заходя на сервер BLAZE RUST, вы автоматически соглашаетесь с правилами проекта в полном объёме. Ознакомьтесь с ними заранее.</p></div></div>
  <div class="li reveal"><span class="li-num">02</span><div><strong>Решение администрации окончательно</strong><p>В спорных ситуациях окончательное решение остаётся за администрацией проекта. Спорные моменты, не описанные в правилах, трактуются на усмотрение администрации.</p></div></div>
  <div class="li reveal"><span class="li-num">03</span><div><strong>Правила могут изменяться</strong><p>Администрация вправе дополнять и изменять правила без отдельного оповещения. Актуальная версия всегда опубликована здесь, в BLAZE.wiki.</p></div></div>
  <div class="li reveal"><span class="li-num">04</span><div><strong>Все обращения — через Discord</strong><p>Жалобы, споры и вопросы решаются через создание тикета в нашем Discord. Доказательства (видео/скриншоты) повышают шанс на положительное решение.</p></div></div>
</div>
''' + callout("tip", "Совет", "После вводных правил обязательно прочитайте основные правила — именно за их нарушение выдаются блокировки.")
    + related([("rules-main", "Основные правила"), ("support-punishments", "Наказания"), ("donate", "Соглашение на донат")]),
}

PAGES["rules-main"] = {
    "title": "Основные правила",
    "html": '''
<p class="lead">Свод правил поведения на сервере BLAZE RUST. За их нарушение администрация вправе выдать предупреждение, мут или блокировку без возврата средств.</p>

<h2>Поведение и честная игра</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">01</span><div><strong>Читы и стороннее ПО запрещены</strong><p>Использование читов, макросов, скриптов и любого ПО, дающего преимущество, — перманентный бан без возможности обжалования и возврата доната.</p></div></div>
  <div class="li reveal"><span class="li-num">02</span><div><strong>Эксплойты и баги</strong><p>Использование игровых багов и эксплойтов (дюп, проход сквозь текстуры и т.п.) запрещено. О найденных багах сообщайте администрации через Discord.</p></div></div>
  <div class="li reveal"><span class="li-num">03</span><div><strong>Обман администрации</strong><p>Попытка ввести администрацию в заблуждение, поддельные доказательства и обман при разборе жалоб караются блокировкой.</p></div></div>
</div>

<h2>Общение и чат</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">04</span><div><strong>Уважение к игрокам</strong><p>Оскорбления, разжигание межнациональной розни, угрозы и травля в чате и голосовых каналах запрещены.</p></div></div>
  <div class="li reveal"><span class="li-num">05</span><div><strong>Спам и реклама</strong><p>Флуд, спам, капс и реклама сторонних проектов и услуг в чате запрещены.</p></div></div>
  <div class="li reveal"><span class="li-num">06</span><div><strong>Никнейм</strong><p>Запрещены оскорбительные, провокационные и вводящие в заблуждение никнеймы (в т.ч. имитация администрации).</p></div></div>
</div>
''' + callout("danger", "Важно", "Игровые действия (рейды, обманы внутри игры, союзы и предательства) — это часть Rust и не являются нарушением. Правила выше касаются поведения вне игровой механики.")
    + related([("rules-intro", "Вводные правила"), ("support-punishments", "Наказания"), ("support-complaint", "Как подать жалобу")]),
}

PAGES["donate"] = {
    "title": "Соглашение на донат",
    "html": '''
<p class="lead">Условия пополнения донат-счёта и возврата средств в магазине BLAZE RUST. Принимаются автоматически при пополнении баланса.</p>
''' + callout("note", "Автоматическое соглашение", "Пополняя свой баланс в магазине, вы автоматически принимаете условия этого раздела в полном объёме.")
    + '''
<h2>Содержание</h2>
<div class="grid grid-2">
  <div class="card tilt reveal"><div class="card-ico">01</div><h3>Пополнение счёта</h3><p>Правила пополнения донат-счёта и выдачи покупок.</p></div>
  <div class="card tilt reveal"><div class="card-ico">02</div><h3>Возврат средств</h3><p>Условия возврата и требования к видео-фиксации.</p></div>
</div>

<h2>Глава 1 · Пополнение счёта</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">01</span><div><strong>Полное согласие</strong><p>Пополняя донат-счёт в нашем магазине, вы принимаете все правила проекта и соглашаетесь с ними в полном объёме.</p></div></div>
  <div class="li reveal"><span class="li-num">02</span><div><strong>Проблемы с товаром</strong><p>В случае возникновения проблем с купленными предметами мы обязаны решить все ваши проблемы. Компенсация выдаётся по усмотрению администратора.</p></div></div>
  <div class="li reveal"><span class="li-num">03</span><div><strong>Утеря данных</strong><p>При утере данных от аккаунта гарантия восстановления средств не предоставляется.</p></div></div>
  <div class="li reveal"><span class="li-num">04</span><div><strong>Обман администрации</strong><p>При попытке обмануть администрацию ваш счёт будет заморожен и аннулирован.</p></div></div>
  <div class="li reveal"><span class="li-num">05</span><div><strong>Нарушение правил</strong><p>За нарушение правил проекта администрация вправе лишить вас купленного доната.</p></div></div>
  <div class="li reveal"><span class="li-num">06</span><div><strong>Ошибочная покупка</strong><p>Если вы купили что-то по ошибке, но ещё не забрали из корзины (/store) — мы поможем восстановить баланс и заберём товар. Для этого достаточно создать тикет в Discord.</p></div></div>
</div>

<h2>Глава 2 · Возврат средств</h2>
<p>Средства возвращаются на банковский счёт по усмотрению администратора. В основном же их можно вернуть на донат-счёт и воспользоваться повторно для покупки товаров.</p>
<p><strong>Что считается браком:</strong> брак — это дефект, из-за которого продукция не может быть использована по своему назначению. Вы можете потребовать возврат, если у товара имеется брак.</p>
<p>Если у купленного товара возникает брак с новой функцией, добавленной на сервера в течение недели, — возврат не оформляется, а мы занимаемся исправлением. Если по истечении времени проблема осталась, возврат возможен.</p>

<h2>Чтобы получить возврат на счёт, нужна видео-фиксация:</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Момент пополнения счёта</h3><p>Запись должна начинаться с момента пополнения баланса.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Момент покупки товара</h3><p>Далее фиксируется сама покупка в магазине.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Момент взятия товара из корзины</h3><p>Показываем выдачу товара через /store.</p></div></div>
  <div class="step reveal"><div class="step-num">4</div><div><h3>Сам «брак» товара</h3><p>И демонстрация дефекта. Видео должно быть цельным и не отредактированным.</p></div></div>
</div>
<p>Если видео-фиксация есть — создайте тикет в Discord, обратитесь к администратору и договоритесь, куда отправить запись для восстановления денежных средств.</p>
''' + callout("warn", "Возникла проблема?", "Все вопросы по донату и возврату решаются через тикет в Discord.")
    + related([("info-privileges", "Привилегии и VIP"), ("rules-main", "Основные правила"), ("info-commands", "Команды чата")]),
}

PAGES["support-complaint"] = {
    "title": "Как подать жалобу",
    "html": '''
<p class="lead">Жалобы на читеров и нарушителей рассматриваются через тикет в Discord. Чем полнее доказательства — тем быстрее решение.</p>

<h2>Как подать</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Создайте тикет в Discord</h3><p>Зайдите в наш Discord и откройте тикет в канале жалоб.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Укажите данные</h3><p>Сообщите ник и SteamID нарушителя, сервер и время нарушения.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Приложите доказательства</h3><p>Прикрепите видео или скриншоты, где чётко видно нарушение. Дождитесь ответа администрации.</p></div></div>
</div>

<h2>Что приложить к жалобе</h2>
<div class="grid grid-3">
  <div class="card tilt reveal"><div class="card-ico">👤</div><h3>Ник и SteamID нарушителя</h3><p>Точные данные игрока, на которого подаёте жалобу.</p></div>
  <div class="card tilt reveal"><div class="card-ico">🎥</div><h3>Видео-доказательство</h3><p>Цельная, не отредактированная запись, где видно сам факт нарушения (чит, эксплойт, оскорбление).</p></div>
  <div class="card tilt reveal"><div class="card-ico">📅</div><h3>Дата, время и сервер</h3><p>Когда и на каком из серверов произошло нарушение.</p></div>
</div>
''' + callout("warn", "Без доказательств жалоба не рассматривается", "Голословные обвинения без видео или скриншотов администрация не принимает. Требования к видео-фиксации совпадают с разделом «Соглашение на донат».")
    + related([("support-punishments", "Наказания"), ("rules-main", "Основные правила"), ("info-commands", "Команды чата")]),
}

PAGES["support-punishments"] = {
    "title": "Наказания",
    "html": '''
<p class="lead">Ориентировочная таблица наказаний за нарушение правил. Окончательная мера определяется администрацией с учётом тяжести и повторности.</p>

<h2>Таблица наказаний</h2>
<div class="table-wrap"><table>
<thead><tr><th>Нарушение</th><th>Первое</th><th>Повторное</th></tr></thead>
<tbody>
<tr><td>Использование читов</td><td><span class="tag bad">Бан навсегда</span></td><td><span class="tag bad">Бан навсегда</span></td></tr>
<tr><td>Использование багов / эксплойтов</td><td><span class="tag mid">Бан 7 дней</span></td><td><span class="tag bad">Бан навсегда</span></td></tr>
<tr><td>Оскорбления в чате</td><td><span class="tag ok">Мут 1 час</span></td><td><span class="tag mid">Мут 24 часа</span></td></tr>
<tr><td>Спам / реклама</td><td><span class="tag ok">Предупреждение</span></td><td><span class="tag mid">Мут 12 часов</span></td></tr>
<tr><td>Обман администрации</td><td><span class="tag mid">Бан 3 дня</span></td><td><span class="tag bad">Бан навсегда</span></td></tr>
</tbody></table></div>
''' + callout("note", "Сроки ориентировочны", "Конкретная мера остаётся на усмотрение администрации и может быть строже при отягчающих обстоятельствах. Бан за читы обжалованию и возврату доната не подлежит.")
    + related([("rules-intro", "Вводные правила"), ("rules-main", "Основные правила"), ("support-complaint", "Как подать жалобу")]),
}

PAGES["info-start"] = {
    "title": "Как начать",
    "html": '''
<p class="lead">Пошаговый гайд для новичков: как скачать пиратку Rust, подключиться к BLAZE RUST и сделать первые шаги.</p>

<h2>Шаг 1. Скачай пиратку Rust</h2>
<p>Сервер BLAZE RUST полностью пиратский — лицензия не нужна. Скачай пиратскую версию Rust с проверенного источника, установи и запусти лаунчер.</p>

<h2>Шаг 2. Подключись к серверу</h2>
<p>Скопируй адрес сервера и вставь его в игровую консоль (клавиша F1):</p>
<div class="codeblock">connect %s</div>

<h2>Шаг 3. Начни выживать</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Собери базу</h3><p>Скорость добычи x50 — фундамент и стены появятся за считанные минуты.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Забери киты</h3><p>Введи /kit в чате и получи стартовый набор.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Объединяйся</h3><p>Создай клан через /clan create Название и зови друзей.</p></div></div>
</div>
''' % SERVER_IP + callout("tip", "Совет", "Перед первым заходом прочитай вводные и основные правила — это сэкономит нервы и сохранит донат.")
    + related([("info-connect", "Подключение connect"), ("info-commands", "Команды чата"), ("rules-intro", "Вводные правила")]),
}

PAGES["info-privileges"] = {
    "title": "Привилегии и VIP",
    "html": '''
<p class="lead">Привилегии дают доступ к уникальным возможностям: киты, телепорты, свои зоны и многое другое. Все покупки — через /store.</p>

<div class="grid grid-3">
  <div class="price-card tilt reveal">
    <h3>VIP</h3>
    <div class="price">149 ₽</div>
    <ul>
      <li>Кит VIP каждые 24 часа</li>
      <li>/sethome ×3</li>
      <li>Приоритет в очереди</li>
      <li>Цветной ник в чате</li>
    </ul>
    <a class="btn btn-ghost btn-sm" href="/page/donate">Купить</a>
  </div>
  <div class="price-card hot tilt reveal">
    <h3>PREMIUM</h3>
    <div class="price">349 ₽</div>
    <ul>
      <li>Всё из VIP</li>
      <li>Кит PREMIUM каждые 12 часов</li>
      <li>/sethome ×6, /tpa без кулдауна</li>
      <li>Своя зона на базе (2×2)</li>
    </ul>
    <a class="btn btn-primary btn-sm" href="/page/donate">Купить</a>
  </div>
  <div class="price-card tilt reveal">
    <h3>LEGENDARY</h3>
    <div class="price">699 ₽</div>
    <ul>
      <li>Всё из PREMIUM</li>
      <li>Кит LEGENDARY каждые 6 часов</li>
      <li>/sethome ×10, приватные ТП</li>
      <li>Особый скин и эффекты</li>
    </ul>
    <a class="btn btn-ghost btn-sm" href="/page/donate">Купить</a>
  </div>
</div>
''' + callout("note", "Выдача", "Все привилегии выдаются мгновенно через /store. При возникновении проблем создайте тикет в Discord.")
    + related([("donate", "Соглашение на донат"), ("info-commands", "Команды чата"), ("info-start", "Как начать")]),
}

PAGES["info-commands"] = {
    "title": "Команды чата",
    "html": '''
<p class="lead">Основные команды чата на BLAZE RUST. Пиши их в игровом чате (Enter) или в консоли (F1).</p>

<h2>Основные команды</h2>
<div class="table-wrap"><table>
<thead><tr><th>Команда</th><th>Описание</th></tr></thead>
<tbody>
<tr><td><span class="cmd-mini">/store</span></td><td>Открыть магазин и забрать покупки</td></tr>
<tr><td><span class="cmd-mini">/kit</span></td><td>Забрать доступные киты</td></tr>
<tr><td><span class="cmd-mini">/sethome</span></td><td>Установить точку дома</td></tr>
<tr><td><span class="cmd-mini">/home</span></td><td>Телепортироваться домой</td></tr>
<tr><td><span class="cmd-mini">/tpa &lt;ник&gt;</span></td><td>Запросить телепорт к игроку</td></tr>
<tr><td><span class="cmd-mini">/clan</span></td><td>Управление кланом</td></tr>
<tr><td><span class="cmd-mini">/w &lt;ник&gt; &lt;текст&gt;</span></td><td>Личное сообщение</td></tr>
<tr><td><span class="cmd-mini">/report &lt;ник&gt;</span></td><td>Пожаловаться на игрока</td></tr>
<tr><td><span class="cmd-mini">/top</span></td><td>Топ игроков</td></tr>
<tr><td><span class="cmd-mini">/stats</span></td><td>Твоя статистика</td></tr>
</tbody></table></div>
''' + callout("tip", "Подсказка", "Полный список команд смотри в игре через /help. По вопросам команд — тикет в Discord.")
    + related([("info-clans", "Как создать клан"), ("info-start", "Как начать"), ("info-privileges", "Привилегии и VIP")]),
}

PAGES["info-clans"] = {
    "title": "Как создать клан",
    "html": '''
<p class="lead">Клановая система на BLAZE RUST позволяет объединяться в группы, иметь общий дом и захватывать карту вместе.</p>

<h2>Как создать клан</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Создай клан</h3><p>Введи команду:</p><div class="cmd"><code>/clan create Название</code></div></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Пригласи друзей</h3><p>Отправь приглашение игроку:</p><div class="cmd"><code>/clan invite Ник</code></div></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Прими заявку</h3><p>Игрок принимает приглашение:</p><div class="cmd"><code>/clan accept</code></div></div></div>
</div>

<h2>Основные команды клана</h2>
<div class="table-wrap"><table>
<thead><tr><th>Команда</th><th>Описание</th></tr></thead>
<tbody>
<tr><td><span class="cmd-mini">/clan create &lt;название&gt;</span></td><td>Создать клан</td></tr>
<tr><td><span class="cmd-mini">/clan invite &lt;ник&gt;</span></td><td>Пригласить игрока</td></tr>
<tr><td><span class="cmd-mini">/clan kick &lt;ник&gt;</span></td><td>Исключить игрока</td></tr>
<tr><td><span class="cmd-mini">/clan leave</span></td><td>Покинуть клан</td></tr>
<tr><td><span class="cmd-mini">/clan info</span></td><td>Информация о клане</td></tr>
<tr><td><span class="cmd-mini">/clan base</span></td><td>Телепорт на базу клана</td></tr>
</tbody></table></div>
''' + callout("note", "Лимиты", "Максимальный размер клана и правила нейтралитета уточняй на сервере или в Discord.")
    + related([("info-commands", "Команды чата"), ("info-start", "Как начать"), ("rules-main", "Основные правила")]),
}

PAGES["info-steamid"] = {
    "title": "Как узнать SteamID",
    "html": '''
<p class="lead">SteamID нужен для жалоб, покупок и обращения в поддержку. Узнать его можно прямо в игре за 10 секунд.</p>

<h2>Способ 1. Игровая консоль</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Открой консоль</h3><p>Нажми клавишу F1 в игре.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Введи команду</h3><p>Напиши в консоли:</p><div class="cmd"><code>status</code></div></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Скопируй SteamID</h3><p>В списке игроков найди себя и скопируй ID вида <code>STEAM_0:1:12345678</code>.</p></div></div>
</div>

<h2>Способ 2. Сторонние сервисы</h2>
<p>Зайди на сайт <strong>steamidfinder.com</strong>, вставь ссылку на профиль Steam и получи свой SteamID64 / SteamID.</p>
''' + callout("tip", "Совет", "Храни SteamID под рукой — он понадобится в тикете Discord при жалобах и возврате доната.")
    + related([("support-complaint", "Как подать жалобу"), ("info-connect", "Подключение connect"), ("donate", "Соглашение на донат")]),
}

PAGES["info-connect"] = {
    "title": "Подключение connect",
    "html": '''
<p class="lead">Подключение к BLAZE RUST занимает меньше минуты. Используй игровую консоль или добавь сервер в избранное.</p>

<h2>Адрес сервера</h2>
<div class="codeblock">connect %s</div>

<h2>Как подключиться</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Запусти Rust</h3><p>Открой пиратскую версию Rust и нажми F1, чтобы открыть консоль.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Вставь команду</h3><p>Вставь <code>connect %s</code> и нажми Enter.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Начинай выживать</h3><p>Дождись загрузки и отправляйся на пустошь!</p></div></div>
</div>
''' % (SERVER_IP, SERVER_IP) + callout("warn", "Ошибка Timed Out (EAC)?", "Отключи EAC/античит в лаунчере или перезапусти игру. Подробнее — в технических гайдах.")
    + related([("info-start", "Как начать"), ("info-steamid", "Как узнать SteamID"), ("info-commands", "Команды чата")]),
}

# ---------------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------------
HOME_HTML = '''
<section class="hero">
  <div class="hero-badge"><span class="pulse-dot"></span>Пиратский сервер Rust · Без лицензии</div>
  <h1 class="hero-title">BLAZE <span>RUST</span></h1>
  <div class="hero-tags">
    <span>X50</span><span>NOLIMIT</span><span>CLANS</span><span>LOOT+</span>
  </div>
  <p class="hero-sub">BLAZE RUST X50 — создан для интенсивной, динамичной игры. Сделан с упором в комфорт для игроков, с максимальной производительностью и использованием передового железа. Выживай, строй, рейдь — и забирай своё место под солнцем пустоши!</p>
  <div class="hero-cta">
    <a class="btn btn-primary" href="/page/info-start">🚀 Начать играть</a>
    <a class="btn btn-ghost" href="/page/rules-intro">📜 Правила</a>
    <a class="btn btn-ghost" href="/page/donate">🛒 Магазин</a>
  </div>
  <div class="hero-stats">
    <div class="stat"><b class="count" data-count="6">0</b><small>онлайн</small></div>
    <div class="stat"><b class="count" data-count="250">0</b><small>макс. игроков</small></div>
    <div class="stat"><b class="count" data-count="24">0</b><small>поддержка 24/7</small></div>
    <div class="stat"><b class="count" data-count="50">0</b><small>рейты сервера</small></div>
  </div>
</section>

<section class="section telegram-block">
  <div class="tg-card">
    <div class="tg-emoji">📢</div>
    <div class="tg-body">
      <h2 class="section-title">BLAZE RUST в Telegram!</h2>
      <p class="tg-text">🔥 Не упусти шанс получить эксклюзивные промокоды в нашем Telegram-канале!</p>
      <a class="tg-link" href="https://t.me/blazerust_tg" target="_blank" rel="noopener">https://t.me/blazerust_tg</a>
      <p class="tg-text">💬 Также вы можете общаться в нашем Telegram-чате: <a href="https://t.me/BlazeRust_Chat" target="_blank" rel="noopener">@BlazeRust_Chat</a></p>
      <p class="tg-text">Присоединяйтесь к нам, чтобы быть в курсе всех новостей и бонусов! 🎉</p>
    </div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Проект</h2>
  <p class="section-sub reveal">BlazeRust — для комфортной игры. Это не просто сервер. Здесь прислушиваются к мнению игроков. И только вы решаете, что будет на сервере.</p>
  <div class="grid grid-2">
    <div class="card tilt reveal"><div class="card-ico">⚡</div><h3>BlazeRust — Reborn</h3><p>Сервер перезапущен и развивается каждый день. Работа над ним идёт постоянно — контент добавляется с каждым обновлением.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🖥️</div><h3>Как зайти?</h3><p>Скопируй адрес и вставь в игровую консоль (F1):</p><div class="codeblock" style="margin-top:10px">connect %s</div></div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Основные плагины</h2>
  <div class="grid grid-4">
    <div class="card tilt reveal"><div class="card-ico">📋</div><h3>Меню сервера</h3><p>Информация о сервере, система китов и вайпблок. В настройках — отображение убийств и автозакрытие дверей.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🛒</div><h3>Магазин предметов</h3><p>Полноценный внутриигровой магазин с удобной выдачей.</p></div>
    <div class="card tilt reveal"><div class="card-ico">💬</div><h3>Чат-система</h3><p>Удобный чат с поддержкой личных сообщений и команд.</p></div>
    <div class="card tilt reveal"><div class="card-ico">⚔️</div><h3>Клановая система</h3><p>Создавай клан, зови друзей и захватывай карту.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🎉</div><h3>Ивент-системы</h3><p>Различные ивенты и повышенный дроп с танка.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🔧</div><h3>Крафт без верстака</h3><p>Всё изучено, вещи не ломаются, авто-сортировка в ящиках.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🚁</div><h3>Коптер по кнопке</h3><p>Вызов коптера одной кнопкой. Бесконечный день.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🔁</div><h3>ТП, трейд, upgrade</h3><p>Метаболизм, трейд, телепорт и upgrade-системы.</p></div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Оптимизация</h2>
  <div class="grid grid-3">
    <div class="card tilt reveal"><div class="card-ico">⚡</div><h3>FPS+</h3><p>Все плагины делались с упором на оптимизацию. Вырезаны все лишние объекты с карты.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🔥</div><h3>Огонь вырезан</h3><p>Дополнительно огонь и трупы полностью вырезаны с сервера — ещё больше FPS.</p></div>
    <div class="card tilt reveal"><div class="card-ico">📈</div><h3>Комфортный геймплей</h3><p>Как для кланов, так и для небольших команд. Это не конечный результат — работа идёт каждый день.</p></div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Частые вопросы</h2>
  <div class="faq">
    <details class="reveal"><summary>Это пиратский сервер? Нужна лицензия?</summary><p>Да, сервер полностью пиратский. Лицензия не нужна — достаточно скачать пиратскую версию Rust и подключиться по адресу сервера.</p></details>
    <details class="reveal"><summary>Какие вайпы и когда?</summary><p>Вайпы проходят по расписанию, которое публикуется в нашем Telegram и Discord. Следи за обновлениями.</p></details>
    <details class="reveal"><summary>Как создать клан?</summary><p>Используй команду /clan create Название. Полная инструкция — в разделе «Как создать клан».</p></details>
    <details class="reveal"><summary>Где купить привилегию?</summary><p>В магазине через /store на сервере или на сайте. Выдача происходит мгновенно после оплаты.</p></details>
    <details class="reveal"><summary>Что делать, если заметил читера?</summary><p>Оставь жалобу в Discord через тикет с видео-доказательствами. Инструкция — в разделе «Как подать жалобу».</p></details>
  </div>
</section>
''' % SERVER_IP

# ---------------------------------------------------------------------------
# Шаблон сайта — ЧЁРНО-БИРЮЗОВЫЙ дизайн, анимации везде
# ---------------------------------------------------------------------------
BASE = '''
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="BLAZE RUST [ X50 | NOLIMIT | CLANS | LOOT+ ] — пиратский сервер Rust. Правила, донат, наказания, инструкции.">
<title>{{ page_title }} — BLAZE RUST</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;800&family=Manrope:wght@400;500;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg0:#000103;--bg1:#010a12;--bg2:#02131e;
  --card:rgba(3,14,22,.82);--card2:rgba(4,22,32,.7);
  --line:rgba(103,232,249,.13);--line2:rgba(103,232,249,.28);
  --cyan:#22d3ee;--aqua:#7ff0f5;--teal:#2dd4bf;--sky:#38bdf8;
  --text:#d2f2fa;--muted:#8fb6c4;
  --grad:linear-gradient(120deg,#06b6d4,#14b8a6 50%,#0284c7);
  --grad-hot:linear-gradient(120deg,#67e8f9,#22d3ee 30%,#2dd4bf 65%,#38bdf8);
  --shadow:0 24px 60px rgba(0,0,0,.75);
  --radius:18px;
}
html{scroll-behavior:smooth}
body{font-family:'Manrope',sans-serif;background:var(--bg0);color:var(--text);min-height:100vh;overflow-x:hidden;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--cyan)}
code{font-family:'JetBrains Mono',monospace;color:var(--aqua);background:rgba(34,211,238,.09);padding:2px 7px;border-radius:7px;border:1px solid var(--line2);font-size:.92em}

.bg-fx{position:fixed;inset:0;z-index:-4;background:
  radial-gradient(1100px 600px at 78% -8%,rgba(6,182,212,.16),transparent 60%),
  radial-gradient(900px 520px at 2% 28%,rgba(20,184,166,.1),transparent 55%),
  radial-gradient(1000px 650px at 100% 88%,rgba(2,132,199,.12),transparent 55%),
  linear-gradient(180deg,#000103,#010a12 45%,#000103)}
.bg-fx::before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(103,232,249,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(103,232,249,.04) 1px,transparent 1px);background-size:46px 46px;-webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000 0%,transparent 78%);mask-image:radial-gradient(ellipse at 50% 0%,#000 0%,transparent 78%)}
.orb{position:fixed;border-radius:50%;filter:blur(100px);opacity:.42;z-index:-3;animation:float 16s ease-in-out infinite}
.o1{width:440px;height:440px;background:rgba(6,182,212,.45);top:-130px;right:-90px}
.o2{width:360px;height:360px;background:rgba(20,184,166,.36);bottom:-110px;left:-100px;animation-delay:-6s}
.o3{width:280px;height:280px;background:rgba(2,132,199,.34);top:42%;left:58%;animation-delay:-11s}
@keyframes float{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(34px,-44px) scale(1.09)}66%{transform:translate(-28px,26px) scale(.93)}}
.stars{position:fixed;inset:0;z-index:-2;pointer-events:none}
.stars i{position:absolute;border-radius:50%;background:#8ff0ff;box-shadow:0 0 6px rgba(127,240,245,.9);opacity:0;animation:twinkle 3s ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.6)}50%{opacity:1;transform:scale(1.15)}}
.vignette{position:fixed;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.6))}

.topbar{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:14px;padding:13px 22px;background:rgba(1,7,12,.8);backdrop-filter:blur(18px);border-bottom:1px solid var(--line)}
.burger{display:grid;place-items:center;width:40px;height:40px;border-radius:12px;border:1px solid var(--line2);background:rgba(6,26,36,.5);color:var(--aqua);font-size:18px;cursor:pointer;transition:.25s}
.burger:hover{background:rgba(34,211,238,.13);border-color:var(--cyan);transform:rotate(90deg)}
@media(min-width:1024px){.burger{display:none}}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);font-family:'Unbounded',sans-serif}
.logo-mark{width:40px;height:40px;display:grid;place-items:center;border-radius:13px;background:var(--grad-hot);color:#02121a;font-weight:800;font-size:21px;box-shadow:0 0 24px rgba(34,211,238,.5);animation:pulseGlow 2.6s ease-in-out infinite}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 14px rgba(34,211,238,.35)}50%{box-shadow:0 0 34px rgba(34,211,238,.7)}}
.logo-text{font-size:17px;letter-spacing:1px}
.logo-text span{color:var(--cyan);margin-left:4px}
.top-actions{margin-left:auto;display:flex;align-items:center;gap:12px}
.online-badge{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;border:1px solid var(--line2);background:rgba(6,26,36,.55);font-size:13px;font-weight:700;color:var(--aqua);white-space:nowrap}
.online-badge i{width:8px;height:8px;border-radius:50%;background:#34d399;box-shadow:0 0 0 0 rgba(52,211,153,.7);animation:ping 1.6s infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(52,211,153,.7)}70%{box-shadow:0 0 0 9px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}

.sidebar{position:fixed;top:0;left:0;bottom:0;width:274px;padding:86px 16px 24px;background:rgba(1,7,12,.94);backdrop-filter:blur(20px);border-right:1px solid var(--line);transform:translateX(-100%);transition:transform .38s cubic-bezier(.22,1,.36,1);z-index:60;overflow-y:auto}
body.nav-open .sidebar{transform:translateX(0)}
@media(min-width:1024px){.sidebar{transform:none}}
.overlay{position:fixed;inset:0;background:rgba(0,4,6,.72);backdrop-filter:blur(3px);opacity:0;pointer-events:none;transition:opacity .3s;z-index:55}
body.nav-open .overlay{opacity:1;pointer-events:auto}
@media(min-width:1024px){.overlay{display:none}}
.sidebar-head{font-family:'Unbounded',sans-serif;font-size:12px;letter-spacing:3px;color:var(--cyan);padding:6px 12px 10px;text-transform:uppercase}
.nav-cat{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin:18px 12px 6px;opacity:.75}
.nav-item{position:relative;display:flex;align-items:center;gap:10px;padding:10px 12px;margin:2px 0;border-radius:12px;color:var(--muted);text-decoration:none;font-size:14px;font-weight:600;border:1px solid transparent;transition:.25s;overflow:hidden}
.nav-item::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--cyan);opacity:0;transform:scale(0);transition:.25s}
.nav-item::after{content:"";position:absolute;left:0;bottom:0;height:2px;width:0;background:var(--grad-hot);transition:width .3s}
.nav-item:hover{color:var(--text);background:rgba(34,211,238,.07);border-color:var(--line);transform:translateX(4px)}
.nav-item:hover::before{opacity:1;transform:scale(1)}
.nav-item:hover::after{width:100%}
.nav-item.active{color:#02121a;background:var(--grad-hot);border-color:transparent;box-shadow:0 8px 26px rgba(34,211,238,.35)}
.nav-item.active::before{opacity:0}

.content{margin-left:0;padding:34px 20px 60px;max-width:1120px;width:100%}
@media(min-width:1024px){.content{margin-left:274px;padding:46px 54px 84px}}

.btn{position:relative;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:13px 26px;border-radius:14px;font-weight:800;font-size:14px;letter-spacing:.3px;text-decoration:none;cursor:pointer;border:none;transition:transform .25s,box-shadow .25s;font-family:inherit}
.btn-primary{background:var(--grad-hot);color:#02121a;box-shadow:0 10px 32px rgba(34,211,238,.35)}
.btn-primary:hover{transform:translateY(-3px) scale(1.02);box-shadow:0 18px 44px rgba(34,211,238,.55)}
.btn-ghost{background:rgba(6,26,36,.55);color:var(--aqua);border:1px solid var(--line2)}
.btn-ghost:hover{transform:translateY(-3px);background:rgba(34,211,238,.12);border-color:var(--cyan);box-shadow:0 0 26px rgba(34,211,238,.25)}
.btn::after{content:"";position:absolute;top:0;left:-80%;width:50%;height:100%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.4),transparent);transform:skewX(-20deg);transition:left .55s}
.btn:hover::after{left:130%}
.btn-sm{padding:9px 16px;font-size:13px;border-radius:11px}
.ripple{position:absolute;border-radius:50%;background:rgba(255,255,255,.4);transform:scale(0);animation:rip .65s ease-out forwards;pointer-events:none}
@keyframes rip{to{transform:scale(1);opacity:0}}

.hero{position:relative;text-align:center;padding:60px 10px 30px;animation:fadeUp .8s ease both}
.hero-badge{display:inline-flex;align-items:center;gap:9px;padding:8px 18px;border-radius:999px;border:1px solid var(--line2);background:rgba(6,26,36,.55);font-size:13px;font-weight:700;color:var(--aqua);margin-bottom:24px;backdrop-filter:blur(8px)}
.pulse-dot{width:8px;height:8px;border-radius:50%;background:#34d399;box-shadow:0 0 0 0 rgba(52,211,153,.7);animation:ping 1.6s infinite}
.hero-title{font-family:'Unbounded',sans-serif;font-size:clamp(42px,8vw,92px);font-weight:800;line-height:1.04;background:linear-gradient(120deg,#a5f3fc,#22d3ee 30%,#2dd4bf 60%,#7dd3fc);-webkit-background-clip:text;background-clip:text;color:transparent;background-size:220% auto;animation:gradShift 5s linear infinite;filter:drop-shadow(0 12px 36px rgba(6,182,212,.4))}
.hero-title span{color:var(--cyan)}
@keyframes gradShift{to{background-position:220% center}}
.hero-tags{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:24px 0 16px}
.hero-tags span{padding:7px 16px;border-radius:999px;border:1px solid var(--line2);background:rgba(34,211,238,.07);color:var(--aqua);font-size:13px;font-weight:800;letter-spacing:1px;transition:.25s}
.hero-tags span:hover{background:rgba(34,211,238,.2);box-shadow:0 0 18px rgba(34,211,238,.35);transform:translateY(-2px)}
.hero-sub{max-width:660px;margin:0 auto 32px;color:var(--muted);font-size:17px}
.hero-cta{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin-bottom:48px}
.hero-stats{display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.stat{min-width:150px;padding:22px 26px;border-radius:var(--radius);border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));backdrop-filter:blur(10px);transition:.3s}
.stat:hover{transform:translateY(-6px);border-color:var(--line2);box-shadow:0 0 30px rgba(34,211,238,.18)}
.stat b{display:block;font-family:'Unbounded',sans-serif;font-size:32px;color:var(--aqua);text-shadow:0 0 18px rgba(127,240,245,.45)}
.stat small{color:var(--muted);font-size:12px;letter-spacing:1px;text-transform:uppercase}

.telegram-block{max-width:780px;margin:0 auto}
.tg-card{display:flex;gap:18px;align-items:flex-start;padding:30px;border-radius:24px;border:1px solid rgba(34,197,94,.3);background:linear-gradient(135deg,rgba(4,18,14,.9),rgba(6,30,22,.75));backdrop-filter:blur(14px);animation:fadeUp .7s ease both;transition:.3s}
.tg-card:hover{border-color:rgba(34,197,94,.55);box-shadow:0 0 44px rgba(34,197,94,.18);transform:translateY(-3px)}
.tg-emoji{font-size:44px;line-height:1;animation:bob 2.6s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
.tg-body{flex:1}
.tg-card .section-title{margin-bottom:10px;font-size:clamp(20px,3vw,28px)}
.tg-text{color:var(--muted);font-size:15px;margin-bottom:8px}
.tg-link{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:14px;color:#4ade80;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.32);padding:8px 14px;border-radius:12px;text-decoration:none;margin:6px 0 12px;transition:.25s}
.tg-link:hover{background:rgba(34,197,94,.2);box-shadow:0 0 20px rgba(34,197,94,.3)}

.section{padding:36px 0}
.section-title{font-family:'Unbounded',sans-serif;font-size:clamp(22px,3.4vw,34px);margin-bottom:8px;background:linear-gradient(120deg,#cff8fe,#7ff0f5);-webkit-background-clip:text;background-clip:text;color:transparent;background-size:200% auto;animation:gradShift 8s linear infinite}
.section-sub{color:var(--muted);margin-bottom:28px}
.grid{display:grid;gap:18px}
.grid-2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.card{position:relative;padding:26px;border-radius:var(--radius);border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));backdrop-filter:blur(12px);transition:transform .35s,box-shadow .35s,border-color .35s;overflow:hidden}
.card::before{content:"";position:absolute;inset:0;background:radial-gradient(420px 220px at 50% -20%,rgba(34,211,238,.14),transparent 70%);opacity:0;transition:opacity .35s}
.card::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;background:linear-gradient(135deg,rgba(34,211,238,.65),transparent 45%);-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:0;transition:opacity .35s;pointer-events:none}
.card:hover{transform:translateY(-9px);border-color:transparent;box-shadow:0 26px 56px rgba(0,0,0,.7),0 0 26px rgba(34,211,238,.15)}
.card:hover::before{opacity:1}
.card:hover::after{opacity:1}
.card-ico{width:54px;height:54px;border-radius:15px;display:grid;place-items:center;font-size:25px;background:rgba(34,211,238,.1);border:1px solid var(--line2);margin-bottom:16px;transition:.35s}
.card:hover .card-ico{transform:scale(1.12) rotate(-8deg);background:var(--grad-hot);box-shadow:0 8px 26px rgba(34,211,238,.45)}
.card h3{font-size:18px;margin-bottom:8px}
.card p{color:var(--muted);font-size:14px}

.steps{display:grid;gap:16px}
.step{display:flex;gap:18px;padding:22px;border-radius:var(--radius);border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));backdrop-filter:blur(10px);transition:.3s}
.step:hover{border-color:var(--line2);transform:translateX(8px);box-shadow:0 14px 36px rgba(0,0,0,.55)}
.step-num{flex:0 0 auto;width:48px;height:48px;border-radius:15px;display:grid;place-items:center;font-family:'Unbounded',sans-serif;font-weight:800;font-size:18px;background:var(--grad-hot);color:#02121a;box-shadow:0 6px 20px rgba(34,211,238,.4)}
.step h3{font-size:17px;margin-bottom:4px}
.step p{color:var(--muted);font-size:14px}

.callout{padding:18px 22px;border-radius:14px;border:1px solid;margin:24px 0;display:flex;gap:14px;align-items:flex-start;animation:fadeUp .6s ease both;background:rgba(3,14,22,.7)}
.callout b{display:block;margin-bottom:2px}
.callout p{font-size:14px;opacity:.92;margin:0}
.callout.tip{border-color:rgba(45,212,191,.35)}
.callout.tip b{color:#5eead4}
.callout.note{border-color:rgba(56,189,248,.35)}
.callout.note b{color:#7dd3fc}
.callout.warn{border-color:rgba(251,191,36,.35)}
.callout.warn b{color:#fcd34d}
.callout.danger{border-color:rgba(248,113,113,.4)}
.callout.danger b{color:#fca5a5}

.article{animation:fadeUp .7s ease both}
.crumbs{display:flex;flex-wrap:wrap;gap:8px;font-size:13px;color:var(--muted);margin-bottom:14px}
.crumbs a{color:var(--cyan);text-decoration:none;transition:.2s}
.crumbs a:hover{text-shadow:0 0 14px rgba(34,211,238,.9)}
.page-title{font-family:'Unbounded',sans-serif;font-size:clamp(26px,4.6vw,44px);margin-bottom:10px;background:linear-gradient(120deg,#cff8fe,#7ff0f5);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 6px 22px rgba(34,211,238,.25))}
.lead{color:var(--muted);font-size:16px;max-width:760px;margin-bottom:26px}
.article h2{font-family:'Unbounded',sans-serif;font-size:clamp(19px,2.6vw,26px);margin:36px 0 16px;display:flex;align-items:center;gap:12px}
.article h2::before{content:"";width:8px;height:28px;border-radius:99px;background:var(--grad-hot);box-shadow:0 0 18px rgba(34,211,238,.6)}
.article h3{font-size:18px;margin:22px 0 10px;color:var(--aqua)}
.article p{color:#bde4ee;margin-bottom:12px}

.list{display:grid;gap:14px;margin:18px 0}
.li{display:flex;gap:16px;padding:18px 20px;border-radius:14px;border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.8),rgba(2,9,14,.88));transition:.3s}
.li:hover{border-color:var(--line2);transform:translateX(7px);box-shadow:0 10px 28px rgba(0,0,0,.5)}
.li-num{flex:0 0 auto;font-family:'Unbounded',sans-serif;color:var(--cyan);font-size:14px;padding-top:3px}
.li strong{display:block;margin-bottom:2px}
.li p{color:var(--muted);font-size:14px;margin:0}

.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:16px;background:linear-gradient(160deg,rgba(5,18,26,.8),rgba(2,9,14,.88));backdrop-filter:blur(10px);margin:20px 0}
table{width:100%;border-collapse:collapse;min-width:520px}
th{font-family:'Unbounded',sans-serif;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;text-align:left;padding:16px 20px;color:var(--aqua);background:rgba(34,211,238,.07);border-bottom:1px solid var(--line2)}
td{padding:15px 20px;font-size:14px;border-bottom:1px solid var(--line);color:#bde4ee}
tbody tr{transition:.2s}
tbody tr:hover{background:rgba(34,211,238,.07)}
tbody tr:last-child td{border-bottom:none}
.tag{display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:800}
.tag.bad{background:rgba(248,113,113,.13);color:#fca5a5;border:1px solid rgba(248,113,113,.35)}
.tag.mid{background:rgba(251,191,36,.1);color:#fcd34d;border:1px solid rgba(251,191,36,.3)}
.tag.ok{background:rgba(45,212,191,.1);color:#5eead4;border:1px solid rgba(45,212,191,.3)}
.cmd-mini{display:inline-block;padding:3px 10px;border-radius:8px;background:rgba(34,211,238,.08);border:1px solid var(--line2);font-family:'JetBrains Mono',monospace;font-size:12.5px;color:var(--aqua)}

.cmd{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 18px;border-radius:12px;border:1px solid var(--line);background:rgba(1,8,13,.85);font-family:'JetBrains Mono',monospace;font-size:14px;color:#67e8f9;margin:10px 0;transition:.25s}
.cmd:hover{border-color:var(--cyan);box-shadow:0 0 18px rgba(34,211,238,.22);transform:translateX(4px)}
.codeblock{cursor:pointer;user-select:all;background:rgba(1,8,13,.92);border:1px solid var(--line2);border-radius:14px;padding:16px 18px;font-family:'JetBrains Mono',monospace;font-size:14px;color:#67e8f9;margin:14px 0;overflow-x:auto;transition:.25s;position:relative}
.codeblock:hover{border-color:var(--cyan);box-shadow:0 0 20px rgba(34,211,238,.25)}
.codeblock::after{content:"📋 клик — скопировать";position:absolute;right:12px;top:10px;font-family:'Manrope',sans-serif;font-size:11px;color:var(--muted);opacity:.8}

.price-card{position:relative;padding:28px 24px;border-radius:20px;border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));backdrop-filter:blur(12px);text-align:center;transition:.35s;overflow:hidden}
.price-card:hover{transform:translateY(-11px);border-color:var(--line2);box-shadow:0 26px 64px rgba(0,0,0,.75)}
.price-card.hot{border-color:rgba(34,211,238,.5);box-shadow:0 0 44px rgba(34,211,238,.18)}
.price-card .price{font-family:'Unbounded',sans-serif;font-size:32px;color:var(--aqua);margin:14px 0;text-shadow:0 0 18px rgba(127,240,245,.4)}
.price-card ul{list-style:none;text-align:left;margin:14px 0 20px;display:grid;gap:8px}
.price-card li{font-size:13.5px;color:var(--muted);display:flex;gap:8px;align-items:flex-start}
.price-card li::before{content:"✔";color:var(--teal);font-weight:800}

.pager{display:flex;justify-content:space-between;gap:14px;margin-top:44px;flex-wrap:wrap}
.pager-btn{flex:1;min-width:220px;padding:18px 22px;border-radius:16px;border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));text-decoration:none;color:var(--muted);transition:.3s;display:block}
.pager-btn:hover{border-color:var(--cyan);transform:translateY(-5px);box-shadow:0 16px 38px rgba(0,0,0,.6);color:var(--text)}
.pager-btn span{font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:.8;display:block;margin-bottom:4px}
.pager-btn strong{color:var(--aqua);font-size:15px}
.pager-btn.next{text-align:right}

.related{margin-top:44px;padding-top:26px;border-top:1px solid var(--line)}
.related h3{font-family:'Unbounded',sans-serif;font-size:16px;color:var(--aqua);margin-bottom:14px;letter-spacing:1px}
.related-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.related-card{display:block;padding:18px;border-radius:14px;border:1px solid var(--line);background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));text-decoration:none;color:var(--text);transition:.3s}
.related-card:hover{border-color:var(--cyan);transform:translateY(-6px);box-shadow:0 16px 34px rgba(0,0,0,.6)}
.related-card small{display:block;color:var(--cyan);font-size:12px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}

.faq details{background:linear-gradient(160deg,rgba(5,18,26,.85),rgba(2,9,14,.9));border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin-bottom:12px;transition:.3s}
.faq details[open]{border-color:var(--cyan);box-shadow:0 12px 34px rgba(0,0,0,.55)}
.faq summary{cursor:pointer;font-weight:800;font-size:15.5px;display:flex;justify-content:space-between;align-items:center;gap:12px;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:22px;color:var(--cyan);transition:transform .3s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq p{color:var(--muted);font-size:14px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}

.footer{margin-left:0;padding:30px 24px 40px;text-align:center;color:var(--muted);font-size:13px;border-top:1px solid var(--line);background:rgba(0,5,9,.8)}
@media(min-width:1024px){.footer{margin-left:274px}}
.reveal{opacity:0;transform:translateY(28px);transition:opacity .7s ease,transform .7s ease}
.reveal.visible{opacity:1;transform:none}
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
::-webkit-scrollbar{width:10px}
::-webkit-scrollbar-track{background:#010a12}
::-webkit-scrollbar-thumb{background:linear-gradient(#06b6d4,#14b8a6);border-radius:99px}
::selection{background:rgba(34,211,238,.35)}
</style>
</head>
<body>
<div class="bg-fx"></div>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="orb o3"></div>
<div class="vignette"></div>

<header class="topbar">
  <button class="burger" onclick="toggleSidebar()" aria-label="Меню">☰</button>
  <a class="logo" href="/"><span class="logo-mark">B</span><span class="logo-text">BLAZE<span>RUST</span></span></a>
  <div class="top-actions">
    <span class="online-badge"><i></i>{{ online }} online</span>
    <a class="btn btn-primary btn-sm" href="/page/donate">🛒 Магазин</a>
  </div>
</header>

<aside id="sidebar" class="sidebar">
  <div class="sidebar-head">Разделы Wiki</div>
  <nav>
    <a class="nav-item {{ 'active' if active == 'home' else '' }}" href="/">🏠 Главная</a>
    {% for cat, items in sections %}
      <div class="nav-cat">{{ cat }}</div>
      {% for slug, label in items %}
        <a class="nav-item {{ 'active' if active == slug else '' }}" href="/page/{{ slug }}">{{ label }}</a>
      {% endfor %}
    {% endfor %}
  </nav>
</aside>
<div class="overlay" onclick="toggleSidebar()"></div>

<main class="content">
  {{ content }}
</main>

<footer class="footer">© 2026 BLAZE RUST. Все права защищены. · Пиратский сервер Rust · <a href="/page/rules-intro">Правила</a> · <a href="/page/donate">Магазин</a></footer>

<script>
(function(){
  var wrap=document.createElement('div');wrap.className='stars';
  for(var i=0;i<80;i++){
    var s=document.createElement('i');
    s.style.left=(Math.random()*100)+'%';
    s.style.top=(Math.random()*100)+'%';
    s.style.animationDelay=(Math.random()*4)+'s';
    s.style.animationDuration=(2+Math.random()*3)+'s';
    s.style.width=s.style.height=(Math.random()*2+1)+'px';
    wrap.appendChild(s);
  }
  document.body.appendChild(wrap);
})();
var revs=document.querySelectorAll('.reveal');
if('IntersectionObserver' in window){
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('visible'); io.unobserve(e.target);} });
  },{threshold:.12});
  revs.forEach(function(r){ io.observe(r); });
}else{ revs.forEach(function(r){ r.classList.add('visible'); }); }
var counts=document.querySelectorAll('.count');
var cio=new IntersectionObserver(function(es){
  es.forEach(function(e){
    if(!e.isIntersecting) return;
    var el=e.target,target=+el.dataset.count,cur=0,step=Math.max(1,Math.round(target/50));
    var t=setInterval(function(){ cur+=step; if(cur>=target){cur=target;clearInterval(t);} el.textContent=cur; },28);
    cio.unobserve(el);
  });
},{threshold:.5});
counts.forEach(function(c){ cio.observe(c); });
document.querySelectorAll('.tilt').forEach(function(card){
  card.addEventListener('mousemove',function(e){
    var r=card.getBoundingClientRect();
    var x=(e.clientX-r.left)/r.width-.5;
    var y=(e.clientY-r.top)/r.height-.5;
    card.style.transform='perspective(850px) rotateY('+(x*8)+'deg) rotateX('+(-y*8)+'deg) translateY(-7px)';
  });
  card.addEventListener('mouseleave',function(){ card.style.transform=''; });
});
document.addEventListener('click',function(e){
  var b=e.target.closest('.btn');
  if(!b) return;
  var r=b.getBoundingClientRect(),s=document.createElement('span');
  s.className='ripple';var size=Math.max(r.width,r.height);
  s.style.width=s.style.height=size+'px';
  s.style.left=(e.clientX-r.left-size/2)+'px';
  s.style.top=(e.clientY-r.top-size/2)+'px';
  b.appendChild(s);
  setTimeout(function(){ s.remove(); },650);
});
document.querySelectorAll('.codeblock').forEach(function(b){
  b.addEventListener('click',function(){
    var txt=b.innerText.replace('📋 клик — скопировать','').trim();
    function done(){ var old=b.innerHTML; b.innerHTML='✅ Скопировано!'; setTimeout(function(){ b.innerHTML=old; },1300); }
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(done); }
    else{ var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);done(); }
  });
});
function toggleSidebar(){ document.body.classList.toggle('nav-open'); }
</script>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Сборка статического сайта (необязательно, для GitHub Pages)
# ---------------------------------------------------------------------------
def build_static(output_dir="_site", base="/"):
    """Собирает статический сайт для GitHub Pages."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    routes = [("/", "index.html")]
    for slug in PAGES:
        routes.append(("/page/%s" % slug, os.path.join("page", slug, "index.html")))

    with app.test_client() as client:
        for url, rel_path in routes:
            html = client.get(url).get_data(as_text=True)
            if base and base != "/":
                html = html.replace('href="/', 'href="%s/' % base)
                html = html.replace('src="/', 'src="%s/' % base)
            full_path = os.path.join(output_dir, rel_path)
            d = os.path.dirname(full_path)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html)
            print("OK: %s (%d байт)" % (rel_path, len(html)))
    print("Статический сайт собран в папке %s (base=%s)" % (output_dir, base))


# ---------------------------------------------------------------------------
# Маршруты
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template_string(
        BASE,
        page_title="Главная",
        active="home",
        content=HOME_HTML,
        online=ONLINE,
        sections=SECTIONS,
    )


@app.route("/page/<slug>")
def wiki(slug):
    if slug not in PAGES:
        abort(404)
    info = PAGES[slug]
    cat = find_cat(slug)
    crumbs = '<nav class="crumbs"><a href="/">Главная</a><span>/</span><span>%s</span><span>/</span><span>%s</span></nav>' % (cat, info["title"])
    header = '<h1 class="page-title">%s</h1>' % info["title"]
    body = '<div class="article">%s%s%s%s</div>' % (crumbs, header, info["html"], pager(slug))
    return render_template_string(
        BASE,
        page_title=info["title"],
        active=slug,
        content=body,
        online=ONLINE,
        sections=SECTIONS,
    )


if __name__ == "__main__":
    if "--build" in sys.argv:
        base = "/"
        if "--base" in sys.argv:
            base = sys.argv[sys.argv.index("--base") + 1]
        build_static(base=base)
    else:
        port = int(os.environ.get("PORT", 5000))
        print("BLAZE RUST Wiki запущен: http://0.0.0.0:%d" % port)
        app.run(host="0.0.0.0", port=port, debug=False)
