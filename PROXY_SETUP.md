#### Инструкци по настройке прокси-сервера squid на Ubuntu
- Установка squid
```bash
sudo apt update
sudo apt-get -y install squid
```

- Преднастройка сети
```bash
sudo ufw allow squid
sudo iptables -P INPUT ACCEPT
```

- Активация демона squid
```bash
sudo systemctl enable squid
```

- Настройка squid
Для начала создаём бекап конфигурации squid и удаляем из оригинального файла всё !8000 строк комментариев
```bash
sudo cp /etc/squid/squid.conf /etc/squid/squid_back.conf
sudo  grep -v '^ *#\|^ *$' /etc/squid/squid.conf > /etc/squid/squid.conf
```

Далее изменяем конфигурацию squid
```bash
sudo apt-get -y install nano
sudo nano /etc/squid/squid.conf
```
Файл squid.conf нужно изменить таким образом:
```config
...
http_access allow localhost
acl whitelist src 111.111.111.111   # Добавляем IP адрес нашего основного сервера (нужно указать реальный IP) в список доступа
http_access allow whitelist         # Разрешаем основному серверу использовать наш прокси
http_access deny all
...
```

- Перезапуск squid
```bash
sudo systemctl restart squid
```
