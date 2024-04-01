### Данный репозиторий содержит исходный код умного ассистента для саммаризации и анализа аудиофайлов и видеозаписей.


<br>


### Что умеет данный ассистент?
- Взаимодействовать с пользователем в телеграмме
- Сохранять и производить анализ аудиофайлов и видеозаписей
- Обсуживать с пользователем загруженные аудиофайлы и видеозаписи


<br>


### Настройка для локальной разработки

#### Настройка Venv
```bash
git clone https://github.com/allseeteam/ai-secretary.git
cd ai-secretary
python3 -m venv venv
source venv/bin/activate 
```

#### Установка Telegram Bot API (пример для Ubuntu, [инструкция для других систем](https://github.com/allseeteam/telegram-bot-api))
```bash
apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    git \
    cmake \
    gperf \
    g++

git clone --recursive https://github.com/tdlib/telegram-bot-api.git && \
    cd telegram-bot-api && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --target install
```

#### Запуск сервера бота
Необходимо задать в ENV следующие переменные или передать напрямую при запуске:
- TELEGRAM_API_HASH — [Hash приложения Telegram](https://tlgrm.ru/docs/api/obtaining_api_id)
- TELEGRAM_BOT_TOKEN — [Токен бота Telegram](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
Команда для запуска сервера бота:
```bash
cd telegram-bot-api/build
 ./telegram-bot-api --api-id=${TELEGRAM_API_ID} --api-hash=${TELEGRAM_API_HASH} --local
```

#### Запуск бота
Необходимо задать в /env или в ENV следующие переменные:
- TELEGRAM_BOT_TOKEN — [Токен бота Telegram](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
- TELEGRAM_BOT_API_BASE_URL — Базовый адрес сервера вашего бота (для локального сервера: http://localhost:8081/bot)
- OPENAI_API_KEY — [Токен OpenAI](https://platform.openai.com/docs/quickstart?context=python#:~:text=Set%20up%20your%20API%20key%20for%20a%20single%20project)
- SQLITE_DB_PATH — Путь по которому мы хотим хранить нашу SQLite базу данных 
(стандартный адрес: bot/database/ai-secretary.db)
- TRANSCRIPTION_API_BASE_URL — Базовый адрес сервера для транскрибации (развернуть сервер можно по инструкциям из [репозитория](https://github.com/allseeteam/whisperx-fastapi), для локального сервера адрес (для данного кейса обязательно при запуске образа указываем --network host): http://127.0.0.1:8000)

```bash
python3 bot/bot.py
```


<br>


### Настройка Docker
#### Предварительная настрока сети (опционально, если не проходят запросы на прокси):
```bash
sudo iptables -P INPUT ACCEPT
```

#### Сборка контейнера
При вызове docker build необходимо указать следующие переменные:
- HTTP_PROXY — Адрес прокси-сервера для обхода географических ограничений (пример настройки прокси-сервера на Ubuntu: PROXY_SETUP.md)
- HTTPS_PROXY — См. HTTP_PROXY
- NO_PROXY — Адреса, запросы на которые мы будем обрабатывать без прокси
```bash
docker build --build-arg HTTP_PROXY=${HTTP_PROXY} --build-arg HTTPS_PROXY=${HTTPS_PROXY} --build-arg NO_PROXY=${NO_PROXY} -t ai-secretary .
```

#### Запуск контейнера
Для корректной работы требуется передавать в docker run следующие переменные окружения:
- TELEGRAM_API_ID — [ID приложения Telegram](https://tlgrm.ru/docs/api/obtaining_api_id)
- TELEGRAM_API_HASH — [Hash приложения Telegram](https://tlgrm.ru/docs/api/obtaining_api_id)
- TELEGRAM_BOT_TOKEN — [Токен бота Telegram](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
- TELEGRAM_BOT_API_BASE_URL — Базовый адрес сервера вашего бота (для локального сервера: http://localhost:8081/bot)
- OPENAI_API_KEY — [Токен OpenAI](https://platform.openai.com/docs/quickstart?context=python#:~:text=Set%20up%20your%20API%20key%20for%20a%20single%20project)
- SQLITE_DB_PATH — Путь по которому мы хотим хранить нашу SQLite базу данных 
(стандартный адрес: bot/database/ai-secretary.db)
- TRANSCRIPTION_API_BASE_URL — Базовый адрес сервера для транскрибации (развернуть сервер можно по инструкциям из [репозитория](https://github.com/allseeteam/whisperx-fastapi), для локального сервера адрес (для данного кейса обязательно при запуске образа указываем --network host): http://127.0.0.1:8000)                                                                                                                                                   
```bash
docker run -d --network host --env-file env/.env --name ai-secretary-container ai-secretary
```
