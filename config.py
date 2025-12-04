import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 解説:
# load_dotenv()は.envファイルの内容を読み込んで、
# プログラムから使えるようにします

# OpenWeatherMap API設定
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
LATITUDE = float(os.getenv('LATITUDE', '35.6762'))
LONGITUDE = float(os.getenv('LONGITUDE', '139.6503'))

# 解説:
# os.getenv('キー名')で.envファイルの値を取得します
# float()は文字列を数値(小数)に変換します
# '35.6762'はデフォルト値(もし.envに値がない場合に使われる)

# Discord Webhook設定
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# スケジュール設定
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tokyo')
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', '0'))
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', '0'))

# 解説:
# int()は文字列を整数に変換します
# 毎朝6時0分に実行される設定になっています

# OpenWeatherMap API URL
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# 解説:
# これは天気予報を取得するためのAPIのアドレスです
