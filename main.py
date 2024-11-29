import paramiko
import time
from config import *

def connect_to_hosts(host): #  Подключение к нодам
    try:
        key = paramiko.RSAKey.from_private_key_file(path_pkey) #  Указываем что вместо пароля используем ключ и путь к приватному ключу
        ssh = paramiko.client.SSHClient() #  Создание ssh клиента
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Параметры удаленного сервера. Если подключение по паролю то вместо pkey=key вставить password=password
        ssh.connect(host, port=port, username=username, pkey=key)
        return ssh
    except Exception:
        return None

def check_ssh_connect(hosts): # Проверка подключения
    print(f"Check connecting to hosts...")
    for host in hosts:
        connect = connect_to_hosts(host)
        if connect:
            print(f"\033[42mConnect to {host} is succesful!\033[0m")
        else:
            print(f"\033[41mError connecting to {host}\033[0m")
            return False
        connect.close()
    return True

def execute_sudo_command(function_connect, command): #  Выполнения комманд под sudo
    # Подключаемся к root сессии и выполняем команды по root
    stdin, stdout, stderr = function_connect.exec_command(f"sudo {command}")
    # stdin.write(f'{password}\n') #  Используем если в /etc/sudoers не отключена проверка пароля
    # stdin.flush() #  Используем если в /etc/sudoers не отключена проверка пароля

    # Построчно читаем вывод в реальном времени. Если вывода слишком много можно просто закомментить
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            output = stdout.channel.recv(1024).decode('utf-8')
            print(f"OUTPUT: {output}", end='')

    # Вывод результата выполнения команд
    output = stdout.read().decode()
    error = stderr.read().decode()
    if output:
        print(f"OUTPUT: {output}")
    if error:
        print(f"ERROR: {error}")
    return output

def sftp_copy(host, local_path, remote_path):  # копирование на ноды указанных в переменных файлов
    try:
        # Устанавливаем SSH-соединение
        key = paramiko.RSAKey.from_private_key_file(path_pkey)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, pkey=key)

        # Используем SFTP для передачи файла
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
    except Exception as error:
        print(f"Error connecting to {host}: {error}")
    finally:
        sftp.close()

def docker_ps(function_coonect):
    commands = [
        'docker ps | grep front'
    ]

    for command in commands:
        print(f"Executing as sudo {command}")
        execute_sudo_command(function_coonect, command)
        time.sleep(2)

if check_ssh_connect(tests):
    for host in tests:
        print(f"\033[44m Check host {host}\033[0m")
        connect = connect_to_hosts(host)
        docker_ps(connect)
    connect.close()