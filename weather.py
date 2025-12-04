import requests
from datetime import datetime, timedelta
import config


def get_weather_data():
    """
    OpenWeatherMap APIから天気データを取得する関数
    
    Returns:
        dict: 天気データの辞書、エラー時はNone
    """
    try:
        # APIリクエストのパラメータ
        params = {
            'lat': config.LATITUDE,
            'lon': config.LONGITUDE,
            'appid': config.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'ja'
        }
        
        print("🌐 天気データを取得中...")
        response = requests.get(config.WEATHER_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        print("✅ 天気データの取得に成功しました")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 天気データの取得に失敗しました: {e}")
        return None


def simplify_weather_description(description):
    """
    APIの詳細な天気説明をシンプルな表現に変換する
    
    Args:
        description: APIから取得した天気説明
        
    Returns:
        str: シンプルな天気表現
    """
    # 天気の変換テーブル
    weather_map = {
        # 晴れ系
        '快晴': '晴れ',
        '晴天': '晴れ',
        '晴': '晴れ',
        
        # 曇り系
        '薄い雲': '晴れ',
        '曇りがち': '曇り',
        '厚い雲': '曇り',
        '雲': '曇り',
        
        # 雨系
        '小雨': '小雨',
        '適度な雨': '雨',
        '強い雨': '雨',
        '大雨': '大雨',
        '霧雨': '小雨',
        '弱い雨': '小雨',
        
        # 雪系
        '小雪': '雪',
        '雪': '雪',
        '大雪': '大雪',
        
        # その他
        '霧': '霧',
        'もや': '霧',
        '雷雨': '雷雨',
    }
    
    # 変換テーブルで探す
    for key, simple in weather_map.items():
        if key in description:
            return simple
    
    # 該当なければそのまま返す
    return description


def analyze_weather_changes(forecasts):
    """
    1日の天気変化を分析して「雨のち晴れ」のような文字列を作る
    
    Args:
        forecasts: 予報データのリスト
        
    Returns:
        str: 天気の変化を表す文字列
    """
    # 各時間帯の天気を取得してシンプルに変換
    weather_list = []
    for item in forecasts:
        weather = item['weather'][0]['description']
        simple_weather = simplify_weather_description(weather)
        weather_list.append(simple_weather)
    
    # 天気の変化を検出(連続する同じ天気を1つにまとめる)
    unique_weathers = []
    previous_weather = None
    
    for weather in weather_list:
        if weather != previous_weather:
            unique_weathers.append(weather)
            previous_weather = weather
    
    # 天気が1種類だけの場合
    if len(unique_weathers) == 1:
        return unique_weathers[0]
    
    # 天気が2種類の場合: 「AのちB」
    elif len(unique_weathers) == 2:
        return f"{unique_weathers[0]}のち{unique_weathers[1]}"
    
    # 天気が3種類の場合: 「AのちB一時C」
    elif len(unique_weathers) == 3:
        return f"{unique_weathers[0]}のち{unique_weathers[1]}一時{unique_weathers[2]}"
    
    # 天気が4種類以上の場合: 最初の2つだけ使う
    else:
        return f"{unique_weathers[0]}のち{unique_weathers[1]}"


def parse_weather_data(data):
    """
    APIから取得した生データを、使いやすい形に整形する
    実行した日の0時から24時間分のデータを取得
    
    Args:
        data: get_weather_data()で取得したデータ
        
    Returns:
        dict: 整形された天気情報
    """
    if not data:
        return None
    
    try:
        now = datetime.now()
        print(f"\n⏰ 実行時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 🆕 実行した日の0時から24時間の範囲を設定
        target_date_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        target_date_end = target_date_start + timedelta(hours=24)
        
        # 解説:
        # target_date_start = 2025-12-04 00:00:00
        # target_date_end   = 2025-12-05 00:00:00
        # つまり12月4日の0時から24時間(12月5日0時まで)
        
        print(f"📅 対象日: {target_date_start.strftime('%Y年%m月%d日')}")
        print(f"🔍 検索範囲: {target_date_start.strftime('%m/%d %H:%M')} 〜 {target_date_end.strftime('%m/%d %H:%M')}")
        
        # 🆕 24時間分のデータを抽出
        target_forecasts = []
        
        for item in data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'])
            
            # 解説:
            # target_date_start <= forecast_time < target_date_end
            # 例: 12/04 00:00 <= データ時刻 < 12/05 00:00
            
            if target_date_start <= forecast_time < target_date_end:
                target_forecasts.append(item)
        
        print(f"📊 取得データ: {len(target_forecasts)}件")
        
        # データの時刻を表示
        if target_forecasts:
            times = [datetime.fromtimestamp(item['dt']).strftime('%H:%M') for item in target_forecasts]
            print(f"   時刻: {', '.join(times)}")
        else:
            print("❌ データが取得できませんでした")
            return None
        
        forecasts = target_forecasts
        
        # 🆕 気温データを集める
        temps = [item['main']['temp'] for item in forecasts]
        temp_min = min(temps)
        temp_max = max(temps)
        
        print(f"🌡️  気温範囲: {round(temp_min, 1)}℃ 〜 {round(temp_max, 1)}℃")
        
        # 🆕 時間帯別の気温を取得
        morning_temp = None   # 6時〜8時
        noon_temp = None      # 12時〜14時
        evening_temp = None   # 15時〜17時
        night_temp = None     # 18時〜20時
        
        for item in forecasts:
            forecast_time = datetime.fromtimestamp(item['dt'])
            hour = forecast_time.hour
            temp = item['main']['temp']
            
            # 朝(6時〜8時)
            if 6 <= hour <= 8 and morning_temp is None:
                morning_temp = temp
                print(f"   朝の気温: {round(temp, 1)}℃ ({hour}時)")
            
            # 昼(12時〜14時)
            if 12 <= hour <= 14 and noon_temp is None:
                noon_temp = temp
                print(f"   昼の気温: {round(temp, 1)}℃ ({hour}時)")
            
            # 夕方(15時〜17時)
            if 15 <= hour <= 17 and evening_temp is None:
                evening_temp = temp
                print(f"   夕方の気温: {round(temp, 1)}℃ ({hour}時)")
            
            # 夜(18時〜20時)
            if 18 <= hour <= 20 and night_temp is None:
                night_temp = temp
                print(f"   夜の気温: {round(temp, 1)}℃ ({hour}時)")
        
        # 🆕 データがない時間帯の補完
        # 各時間帯に最も近いデータを探す
        
        if morning_temp is None:
            # 朝のデータがない場合、0時〜11時の範囲で最も近いものを探す
            morning_candidates = []
            for item in forecasts:
                forecast_time = datetime.fromtimestamp(item['dt'])
                hour = forecast_time.hour
                if 0 <= hour < 12:
                    morning_candidates.append(item['main']['temp'])
            
            if morning_candidates:
                morning_temp = min(morning_candidates)  # 午前中の最低気温
                print(f"⚠️  朝のデータがないため午前中の最低気温を使用: {round(morning_temp, 1)}℃")
            else:
                morning_temp = temp_min
                print(f"⚠️  朝のデータがないため1日の最低気温を使用: {round(morning_temp, 1)}℃")
        
        if noon_temp is None:
            # 昼のデータがない場合、11時〜15時の範囲で探す
            noon_candidates = []
            for item in forecasts:
                forecast_time = datetime.fromtimestamp(item['dt'])
                hour = forecast_time.hour
                if 11 <= hour < 16:
                    noon_candidates.append(item['main']['temp'])
            
            if noon_candidates:
                noon_temp = max(noon_candidates)  # 昼間の最高気温
                print(f"⚠️  昼のデータがないため昼間の最高気温を使用: {round(noon_temp, 1)}℃")
            else:
                noon_temp = temp_max
                print(f"⚠️  昼のデータがないため1日の最高気温を使用: {round(noon_temp, 1)}℃")
        
        if night_temp is None:
            # 夜のデータがない場合、17時〜23時の範囲で探す
            night_candidates = []
            for item in forecasts:
                forecast_time = datetime.fromtimestamp(item['dt'])
                hour = forecast_time.hour
                if 17 <= hour <= 23:
                    night_candidates.append(item['main']['temp'])
            
            if night_candidates:
                night_temp = sum(night_candidates) / len(night_candidates)  # 夜の平均気温
                print(f"⚠️  夜のデータがないため夜間の平均気温を使用: {round(night_temp, 1)}℃")
            else:
                # 朝と昼の中間値
                night_temp = (morning_temp + noon_temp) / 2
                print(f"⚠️  夜のデータがないため推定値を使用: {round(night_temp, 1)}℃")
        
        # 天気変化を分析
        weather_description = analyze_weather_changes(forecasts)
        print(f"☁️  天気: {weather_description}")
        
        # アイコンと天気情報(最初のデータから取得)
        weather_main = forecasts[0]['weather'][0]['main']
        weather_icon = forecasts[0]['weather'][0]['icon']
        weather_icon = weather_icon.replace('n', 'd')  # 昼版に統一
        
        # 降水確率(24時間の最大値)
        pops = [item.get('pop', 0) for item in forecasts]
        pop = max(pops) * 100
        print(f"💧 降水確率: {round(pop, 0)}%")
        
        # 日付表示
        date_str = target_date_start.strftime('%Y年%m月%d日(%a)')
        weekday_dict = {
            'Mon': '月', 'Tue': '火', 'Wed': '水',
            'Thu': '木', 'Fri': '金', 'Sat': '土', 'Sun': '日'
        }
        for eng, jpn in weekday_dict.items():
            date_str = date_str.replace(eng, jpn)
        
        return {
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'morning_temp': round(morning_temp, 1),
            'noon_temp': round(noon_temp, 1),
            'night_temp': round(night_temp, 1),
            'weather_main': weather_main,
            'weather_description': weather_description,
            'weather_icon': weather_icon,
            'pop': round(pop, 0),
            'date': date_str
        }
        
    except (KeyError, IndexError) as e:
        print(f"❌ 天気データの解析に失敗しました: {e}")
        return None
