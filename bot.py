import requests
from datetime import datetime
import config
import weather
import recommend
import pytz


def create_embed_message(weather_info, clothing, items):
    """
    天気情報からDiscord Embed形式のメッセージを作成
    
    Args:
        weather_info: 天気情報の辞書
        clothing: 服装の推奨
        items: 持ち物の推奨
        
    Returns:
        dict: Discord Embed形式のメッセージ
    """
    weather_emoji = recommend.get_weather_emoji(weather_info['weather_main'])
    embed_color = recommend.get_embed_color(weather_info['weather_main'])
    
    # 天気アイコンのURL
    icon_url = f"https://openweathermap.org/img/wn/{weather_info['weather_icon']}@2x.png"

    # 現在時刻（JST）
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    
    embed = {
        "embeds": [{
            "title": f"{weather_emoji} 今日の天気予報 (東京)",
            "description": f"📅 {weather_info['date']}",
            "color": embed_color,
            "fields": [
                {
                    "name": "🌡️ 気温",
                    "value": (
                        f"朝{weather_info['morning_temp']}℃ "
                        f"昼{weather_info['noon_temp']}℃ "
                        f"夜{weather_info['night_temp']}℃\n"
                        f"**最低**: {weather_info['temp_min']}°C / "
                        f"**最高**: {weather_info['temp_max']}°C"
                    ),
                    "inline": False
                },
                {
                    "name": "☁️ 天気",
                    "value": weather_info['weather_description'],
                    "inline": False
                },
                {
                    "name": "💧 降水確率",
                    "value": f"{weather_info['pop']}%",
                    "inline": False
                },
                {
                    "name": "👕 服装",
                    "value": clothing,
                    "inline": False
                },
                {
                    "name": "🎒 持ち物",
                    "value": items,
                    "inline": False
                }
            ],
            "thumbnail": {
                "url": icon_url
            },
            "footer": {
                "text": f"更新: {now.strftime('%Y-%m-%d %H:%M')}"
            }
        }]
    }
    
    return embed


def send_to_discord(embed_data):
    """
    Discord WebhookにEmbedメッセージを送信
    
    Args:
        embed_data: Discord Embed形式のデータ
        
    Returns:
        bool: 送信成功時True、失敗時False
    """
    try:
        response = requests.post(
            config.DISCORD_WEBHOOK_URL,
            json=embed_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        print("✅ Discordへの送信に成功しました")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Discordへの送信に失敗しました: {e}")
        return False


def post_weather_forecast():
    """
    天気予報を取得してDiscordに投稿する
    """
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    print("=" * 60)
    print(f"Discord天気予報Bot (GitHub Actions)")
    print(f"実行時刻(JST): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"対象地域: 東京 (緯度: {config.LATITUDE}, 経度: {config.LONGITUDE})")
    print("=" * 60)
    
    # 天気データ取得
    raw_data = weather.get_weather_data()
    
    if not raw_data:
        print("❌ 天気データの取得に失敗しました")
        return
    
    # データ解析
    weather_info = weather.parse_weather_data(raw_data)
    
    if not weather_info:
        print("❌ 天気データの解析に失敗しました")
        return
    
    # 服装と持ち物の判定
    clothing = recommend.recommend_clothing(
        weather_info['temp_max'],
        weather_info['temp_min']
    )
    
    items = recommend.recommend_items(
        weather_info['pop'],
        weather_info['temp_max']
    )
    
    # Embedメッセージ作成
    embed_message = create_embed_message(weather_info, clothing, items)
    
    # Discordに送信
    send_to_discord(embed_message)
    
    print("=" * 60)
    print("✅ 処理完了")
    print("=" * 60)


if __name__ == '__main__':
    # 🆕 GitHub Actions用: 1回だけ実行
    post_weather_forecast()
