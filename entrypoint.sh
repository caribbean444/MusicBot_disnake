#!/bin/bash
set -e
# Создаём нужные директории
mkdir -p /etc/openvpn/client/

if [ -n "$OPENVPN_LOGIN" ] && [ -n "$OPENVPN_PASSWORD" ]; then
    # Перемещаем файл конфигурации (если он передан)
    if [ -f /openvpncfg/client.ovpn ]; then
        cp /openvpncfg/client.ovpn /etc/openvpn/client/client.ovpn
    else
        echo "Ошибка: Файл client.ovpn не найден. Убедитесь, что вы предоставили файл конфигурации."
        exit 1
    fi
    # Создаём файл auth.txt, если он отсутствует
    touch /etc/openvpn/auth.txt

    # Настраиваем auth-user-pass
    sed -i 's|^auth-user-pass.*|auth-user-pass /etc/openvpn/auth.txt|' /etc/openvpn/client/client.ovpn

    # Настраиваем перенаправление маршрутов
    if grep -q "^redirect-gateway" /etc/openvpn/client/client.ovpn; then
        sed -i 's/^redirect-gateway.*/redirect-gateway def1/' /etc/openvpn/client/client.ovpn
    else
        echo "redirect-gateway def1" >> /etc/openvpn/client/client.ovpn
    fi

    # Настраиваем DNS
    echo "dhcp-option DNS 8.8.8.8" >> /etc/openvpn/client/client.ovpn
    echo "dhcp-option DNS 8.8.4.4" >> /etc/openvpn/client/client.ovpn

    # Устанавливаем права доступа на auth.txt
    chmod 600 /etc/openvpn/auth.txt
fi

# Настройка пользователя для OpenVPN
echo "$OPENVPN_LOGIN" > /etc/openvpn/auth.txt
echo "$OPENVPN_PASSWORD" >> /etc/openvpn/auth.txt
echo "Параметры пользователя настроены."
cat /etc/openvpn/auth.txt

echo "Проверяем подключение к интернету через Docker-сеть..."

# Проверка доступа к Google DNS
if ! ping -c 4 8.8.8.8 > /dev/null 2>&1; then
    echo "Ошибка: Контейнер не имеет доступа к интернету. Проверьте сетевые настройки Docker."
    exit 1
fi

echo "Интернет доступен. Продолжаем настройку виртуальной сети..."

if [ -z "$OPENVPN_LOGIN" ] || [ -z "$OPENVPN_PASSWORD" ]; then
    # Проверка доступа к YouTube
    if ! wget --spider -q --timeout=5 https://www.youtube.com; then
        echo "Ошибка: Нет доступа к YouTube. Проверьте сетевые настройки или включите VPN."
        exit 1
    fi

    # Проверка доступа к Discord
    if ! wget --spider -q --timeout=5 https://discord.com; then
        echo "Ошибка: Нет доступа к Discord. Проверьте сетевые настройки или включите VPN."
        exit 1
    fi

    echo "Интернет, YouTube и Discord доступны. Продолжаем настройку виртуальной сети..."
fi


# Проверка и создание виртуального интерфейса
if ! ip link show veth0 > /dev/null 2>&1; then
    echo "Создаём интерфейс veth0..."
    ip link add veth0 type dummy
    ip addr add 192.168.100.2/24 dev veth0
    ip link set veth0 up
else
    echo "Интерфейс veth0 уже существует."
fi

# Проверка и настройка маршрутов
if ! ip route | grep -q "default via 172.17.0.1 dev eth0"; then
    echo "Настраиваем маршрут по умолчанию через eth0..."
    ip route del default || true
    ip route add default via 172.17.0.1 dev eth0
else
    echo "Маршрут по умолчанию уже настроен."
fi

if ! ip route | grep -q "192.168.100.0/24 dev veth0"; then
    echo "Настраиваем маршрут для подсети 192.168.100.0/24..."
    ip route add 192.168.100.0/24 dev veth0
else
    echo "Маршрут для подсети 192.168.100.0/24 уже настроен."
fi

# Настройка NAT для виртуальной сети
if ! iptables -t nat -C POSTROUTING -s 192.168.100.0/24 -o eth0 -j MASQUERADE 2>/dev/null; then
    echo "Настраиваем NAT для выхода в интернет через eth0..."
    iptables -t nat -A POSTROUTING -s 192.168.100.0/24 -o eth0 -j MASQUERADE
else
    echo "NAT уже настроен."
fi


