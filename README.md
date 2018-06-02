# Start.ru
TasksDistributor

Создать виртуальное окружение:
```
python3 -m venv /path/to/new/virtual/environment
```

Активировать виртуальное окружение:
```
source venv/bin/activate
cd TasksDistributor/
```

Установить необходимые библиотеки:
```
pip install -r requirements.txt
```

Создать файл config.json и указать настройки подключения для базы данных (MySQL)
```
{
	"MYSQL_DATABASE_USER": "username",
	"MYSQL_DATABASE_PASSWORD": "password",
	"MYSQL_DATABASE_HOST": "localhost",
	"MYSQL_DATABASE_DB": "TasksDistributor"
}
```

Создать базу данных с названием 'TasksDistributor' для username'а:
```
CREATE DATABASE TasksDistributor;
```

Запустить скрипт populate_db.py для создания структуры базы данных, а также для ее заполнения:
```
python populate_db.py
```

Выполнить следующую команду для запуска локального сервера:
```
python index.py
```

В браузере по адресу 'http://localhost:5000/' должно отобразиться задание.
