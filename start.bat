@echo off

rem Установка зависимостей
echo Установка зависимостей...
python -m pip install -r requirements.txt

rem Запуск бота
echo Запуск бота...
python bot.py
