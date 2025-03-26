@echo off
:: Установка кодировки командной строки на UTF-8
chcp 65001

:: Запуск в режиме разработки
if "%1"=="prod" (
    docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d
    exit /b
)

:: Запуск в режиме разработки
if "%1"=="dev" (
    docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d
    exit /b
)

:: Остановка и удаление всех сервисов
if "%1"=="down" (
    docker-compose -f docker-compose.base.yml down
    exit /b
)

:: Остановка всех сервисов
if "%1"=="stop" (
    docker-compose -f docker-compose.base.yml stop
    exit /b
)
