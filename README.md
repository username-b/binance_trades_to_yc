# Binance trades -> Yandex Object Storage

Небольшой самостоятельный проект для загрузки **неагрегированных сделок**
(`trades`, не `aggTrades`) из публичного архива Binance Futures в
Yandex Object Storage.

Данные сохраняются по одной parquet-партиции на день:

```text
raw/trades/symbol=ADAUSDT/date=2026-01-01/data.parquet
```

## Запуск

1. Скопируйте `.env.example` в `.env` и задайте ключи сервисного аккаунта.
2. Измените `config.yaml`.
3. Установите зависимости и запустите загрузчик:

```powershell
python -m pip install -r requirements.txt
python run.py --config config.yaml
```

Уже существующие объекты пропускаются. Для повторной записи используйте
`overwrite: true` в конфигурации.

## Docker

```powershell
docker build -t binance-trades-to-yc .
docker run --rm --env-file .env binance-trades-to-yc
```

Архив берётся из `data.binance.vision/data/futures/um/daily/trades`.
Это поток отдельных USD-M Futures-сделок. Поле `is_buyer_maker` сохраняется
без изменения.
