# MusicBot\_disnake
![GitHub License](https://img.shields.io/github/license/caribbean444/MusicBot_disnake)
![GitHub Release](https://img.shields.io/github/v/release/caribbean444/MusicBot_disnake)
![Stars](https://img.shields.io/github/stars/caribbean444/MusicBot_disnake?style=social)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Discord API](https://img.shields.io/badge/Discord-API-green)
![Docker Ready](https://img.shields.io/badge/Docker-ready-blue)
![Maintained](https://img.shields.io/maintenance/yes/2024)
---
MusicBot\_disnake - музыкальный бот для Discord, поддерживающий использование OpenVPN.

## Содержание
1. [Описание](#MusicBot_disnake)
2. [Пример использования](#Пример-использования)
3. [Требования к железу](#Требования-к-железу)
4. [Описание команд](#Описание-команд)
5. [Установка](#Установка)
6. [Лицензия](#License)
7. [Дисклеймер](#Disclaimer)


## Пример использования
### Интерфейс бота в чате Discord    
![alt text](/images/example.png)

**`▶️`** - Включение плеера, если он был поставлен на паузу.    
**`⏸️`** - Пауза плеера.    
**`⏹️`** - Остановка плеера с очисткой очереди треков.    
**`⏩`** - Пропуск текущего трека.    
**`📶`** - Отображение очереди треков в виде списка с возможностью выбора трека. При выборе трека из списка все треки до выбранного пропускаются и удаляются из очереди.
 

## Требования к железу

Для корректной работы музыкального бота MusicBot_disnake требуются минимальные аппаратные характеристики сервера:

- **Процессор:** 2 ядра с тактовой частотой 2.0 ГГц или выше.
- **Оперативная память:** минимум 0.5 ГБ. (Рекомендуется 1 ГБ.)
- **Место на диске:** минимум 5 ГБ свободного пространства для кэша и временных файлов.
- **Сетевое соединение:** стабильный доступ в интернет с минимальной задержкой и пропускной способностью 5 Мбит/с.

Рекомендуется запускать бота на сервере под управлением Linux для оптимальной производительности.

## Описание команд

Бот поддерживает следующие команды:

- **`.play <URL>`**  
  Добавляет трек в очередь для воспроизведения. Поддерживаются ссылки на YouTube и YouTube Music.

- **`.ignore <#Текстовый канал>`**  
  Добавляет текстовый канал в список каналов, игнорируемых ботом.

- **`.noignore <#Текстовый канал>`**  
  Удаляет текстовый канал из списка каналов, игнорируемых ботом.

- **`.time <seconds>`**  
  Изменение времени бездействия бота. По умолчанию 5 минут.

- **`.clear`**  
  Очищает очередь треков.

- **`.queue`**  
  Показывает список треков в очереди.

- **`.leave`**  
  Отключает бота от голосового канала и очищает очередь треков.

- **`.queue_size`**  
  Показывает размер очереди.

- **`.skip`**  
  Пропускает текущий трек.

- **`.shutdown`**    
  Перезагружает бота. Доступен только для владельцев бота, указанных в файле .env

---

## Установка

Развёртывание бота осуществляется с использованием Docker и Docker Compose. Если у вас уже установлен Docker и Docker Compose, пропустите первый шаг.

### 1. Установка Docker

Для обеспечения функциональности бота требуется установка Docker. Следуйте указанным инструкциям для вашей операционной системы.

#### **Windows**:

1. Загрузите **Docker Desktop** с официального сайта:  
   [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Установите Docker Desktop, следуя рекомендациям установщика.
3. Перезагрузите систему после завершения установки.
4. Проверьте корректность установки, выполнив команду в PowerShell или командной строке:
   ```bash
   docker --version
   ```

#### **macOS**:

1. Загрузите **Docker Desktop** с официального сайта:  
   [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Выполните установку, следуя инструкциям инсталлятора.
3. Перезагрузите систему.
4. Убедитесь в успешной установке с помощью команды:
   ```bash
   docker --version
   ```

#### **Linux** (Ubuntu/Debian):
1. Выполните обновление списка пакетов:
   ```bash
   sudo apt update
   sudo apt install -y ca-certificates curl gnupg
   ```
2. Импортируйте ключи репозитория Docker:
   ```bash
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   ```
3. Добавьте репозиторий Docker в список источников:
   ```bash
   echo \
   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```
4. Установите Docker и плагин Docker Compose:
   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```
5. Проверьте успешность установки:
   ```bash
   docker --version
   ```

#### **Linux** (CentOS/RHEL):

1. Установите дополнительные утилиты:
   ```bash
   sudo yum install -y yum-utils
   ```
2. Подключите репозиторий Docker:
   ```bash
   sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
   ```
3. Выполните установку Docker:
   ```bash
   sudo yum install -y docker-ce docker-ce-cli containerd.io
   ```
4. Запустите и активируйте службу Docker:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```
5. Установите плагин Docker Compose:
   ```bash
   sudo yum install -y docker-compose-plugin
   ```
6. Проверьте работу Docker:
   ```bash
   docker --version
   ```

#### **Проверка Docker Compose**:

После завершения установки Docker проверьте, доступен ли Docker Compose, выполнив команду:
   ```bash
   docker compose version
   ```

Если команда возвращает версию, установка завершена успешно, и вы можете переходить к следующему этапу развёртывания бота.

### 2. Копирование репозитория

Для начала работы скопируйте репозиторий с исходным кодом проекта на ваш локальный компьютер. Выполните следующую команду:

```bash
git clone https://github.com/caribbean444/MusicBot_disnake.git
```

После завершения клонирования перейдите в папку с проектом:

```bash
cd MusicBot_disnake
```

### 3. Настройка переменных окружения

Для корректной работы бота требуется настроить переменные окружения. Эти переменные указываются в файле `.env`, который должен быть создан в корневой директории проекта.

Пример содержимого файла `.env`:

```env
YOUTUBE_API_KEY=your_youtube_api_key
DISCORD_TOKEN=your_discord_bot_token
OPENVPN_LOGIN=your_openvpn_login
OPENVPN_PASSWORD=your_openvpn_password
BOT_OWNER_IDS=comma_separated_list_of_discord_user_ids
LOG_LEVEL=info
```

#### Пояснения:

- `YOUTUBE_API_KEY`: API-ключ для работы с YouTube.
- `DISCORD_TOKEN`: Токен вашего бота Discord.
- `OPENVPN_LOGIN`: Логин для подключения к OpenVPN.
- `OPENVPN_PASSWORD`: Пароль для подключения к OpenVPN.
- `BOT_OWNER_IDS`: ID владельцев бота (через запятую).
- `LOG_LEVEL`: Уровень логирования (например, `info`, `debug`).

После настройки переменных окружения переходите к следующему этапу.

### 4. Настройка OpenVPN

Для работы бота через OpenVPN необходимо поместить в директорию [openvpn](./openvpn/) файл конфигурации с обязательным названием `client.ovpn`.
Файловая структура должна выглядеть так:
```
MusicBot_disnake/
├── data/
│   └── ignored_channels.json   # Файл с игнорируемыми каналам (может быть еще не создан)
├── openvpn/
│       └── client.ovpn         # Конфигурация OpenVPN
├── .env                        # Переменные окружения (API-ключи, токены)
├── docker-compose.yml          # Конфигурация Docker Compose для развёртывания
├── Dockerfile                  # Инструкции для сборки Docker-образа
├── entrypoint.sh               # Скрипт применения настроек при запуске (запускается автоматически)
├── LICENSE                     # Лицензия проекта
├── main.py                     # Основной файл с реализацией логики бота
├── README.md
├── requirements.txt            # Список Python-зависимостей
└── Youtube_API.py              # Функции для Youtube API
```
Если вы не планируете использовать OpenVPN, оставьте поля `OPENVPN_LOGIN` и `OPENVPN_PASSWORD` в файле `.env` пустыми. Например:
```
YOUTUBE_API_KEY=your_youtube_api_key
DISCORD_TOKEN=your_discord_bot_token
OPENVPN_LOGIN=
OPENVPN_PASSWORD=
BOT_OWNER_IDS=comma_separated_list_of_discord_user_ids
LOG_LEVEL=info
```

Для OpenVPN, который не использует логин или пароль для подключения, поля `OPENVPN_LOGIN` и `OPENVPN_PASSWORD` могут содержать произвольные значения. Например:
```
OPENVPN_LOGIN=none
OPENVPN_PASSWORD=none
```


### 5. Запуск проекта

Для запуска проекта выполните команду:

```bash
docker compose up
```

Эта команда запустит все контейнеры, описанные в файле `docker-compose.yml`. После успешного запуска бот будет готов к работе.

## Уточнения по использованию

**Ограничения:**
   - Бот не поддерживает прямое воспроизведение музыки из файлов (локальных или облачных) — только из YouTube и YouTube Music.
   - Бот поддерживает работу только на одном сервере одновременно.


## License
This project is licensed under the [MIT License](./LICENSE).

---

### Disclaimer

This project is provided for educational purposes only. The author of the code is not responsible for copyright violations or misuse of third-party services, such as YouTube, by third parties.

MusicBot_disnake uses yt-dlp to retrieve streams and the YouTube API for metadata (track titles and descriptions). Users must ensure that their use of the bot complies with applicable laws and platform terms of use.

By using this project, you agree that the author is released from any responsibility for potential consequences of its use.

---

This project includes the following third-party libraries with their respective licenses:

- [`disnake`](https://github.com/DisnakeDev/disnake) (MIT License)
- [`requests`](https://github.com/psf/requests) (Apache License, Version 2.0)
- [`pytube`](https://github.com/pytube/pytube) (MIT License)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) (Unlicense)
- [`requests-html`](https://github.com/psf/requests-html) (MIT License)
- [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) (Apache License, Version 2.0)
- [`urllib3`](https://github.com/urllib3/urllib3) (MIT License)
- [`python-dotenv`](https://github.com/theskumar/python-dotenv) (BSD-3-Clause License)
- [`pynacl`](https://github.com/pyca/pynacl) (Apache License, Version 2.0)
- [`colorlog`](https://github.com/borntyping/python-colorlog) (MIT License)

You may obtain a copy of the Apache License, Version 2.0 at:
    http://www.apache.org/licenses/LICENSE-2.0

You may obtain a copy of the Unlicense at:
   https://unlicense.org/

You may obtain a copy of the BSD-3-Clause Licensee at:
   https://opensource.org/licenses/BSD-3-Clause