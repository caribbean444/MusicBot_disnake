FROM python:3.11-bullseye

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . .

RUN chmod -R 777 *
# Обновляем систему и устанавливаем зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libopus-dev \
        ffmpeg \
        wget \
        grep \
        gnupg \
        python3 \
        python3-dev \
        python3-pip \
        openssl \
        iproute2 \
        iptables \
        iputils-ping \
        aria2
# Настройка репозитория OpenVPN
RUN apt-get update && \
    apt-get install -y --no-install-recommends openvpn

# Устанавливаем зависимости Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade certifi


# Указываем команду для запуска контейнера
CMD ["sh", "-c", "./entrypoint.sh && ([ -n \"$OPENVPN_LOGIN\" ] && [ -n \"$OPENVPN_PASSWORD\" ] && openvpn --config /etc/openvpn/client/client.ovpn --auth-user-pass /etc/openvpn/auth.txt --daemon && while ! ip a | grep -q tun0; do sleep 1; done || echo 'OpenVPN не используется') && python -u ./main.py"]


