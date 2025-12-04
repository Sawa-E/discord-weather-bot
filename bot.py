import requests
from datetime import datetime
import os
import config
import weather
import recommend


def create_embed_message(weather_info):
    """
    Discord Embed形式のメッセージを作成する
    
    Args:
        weather_info: 天気情報の辞書
        
    Returns:
        dict: Discord Embed形式のメッセージ
    """
    # 天気に応じた絵文字とカラーを取得
    weather_emoji = recommend.get_weather_emoji(weather_info['weather_main'])
    embed_color = recommend.get_embed_color(weather_info['weather_main'])
    
    # 服装と持ち物のアドバイスを生成
    clothing = recommend.recommend_clothing(
        weather_info['temp_max'],
        weather_info['temp_min']
    )
    
    items = recommend.recommend_items(
        weather_info['pop'],
        weather_info['temp_max']
    )
    
    # 天気アイコンのURL
    icon_url = f"https://openweathermap.org/img/wn/{weather_info['weather_icon']}@2x.png"
    
    # Embed本体を作成
    embed = {
        "title": f"{weather_emoji} 今日の天気予報 (東京)",
        "color": embed_color,
        "thumbnail": {
            "url": icon_url
        },
        "fields": [
            {
                "name": "📅 日付",
                "value": weather_info['date'],
                "inline": False
            },
            {
                "name": "🌡️ 気温",
                "value": (
                    f"朝{weather_info['morning_temp']}℃ "
                    f"昼{weather_info['noon_temp']}℃ "
                    f"夜{weather_info['night_temp']}℃\n"
                    f"最低: {weather_info['temp_min']}℃ / "
                    f"最高: {weather_info['temp_max']}℃"
                ),
                "inline": False
            },
            {
                "name": "☁️ 天気",
                "value": weather_info['weather_description'],
                "inline": True
            },
            {
                "name": "💧 降水確率",
                "value": f"{int(weather_info['pop'])}%",
                "inline": True
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
        "footer": {
            "text": f"更新時刻: {datetime.now().strftime('%H:%M')}"
        }
    }
    
    return embed


def send_to_discord(embed):
    """
    Discord WebhookにEmbedメッセージを送信する
    
    Args:
        embed: Embed形式のメッセージ
        
    Returns:
        bool: 送信成功ならTrue
    """
    try:
        # Webhookに送信するデータ
        payload = {
            "embeds": [embed]
        }
        
        # Webhookに送信
        response = requests.post(
            config.DISCORD_WEBHOOK_URL,
            json=payload
        )
        
        # ステータスコードをチェック
        response.raise_for_status()
        
        print("✅ Discordへの送信に成功しました")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Discordへの送信に失敗しました: {e}")
        return False


def post_weather_forecast():
    """
    天気予報を取得してDiscordに投稿するメイン処理
    """
    print("\n" + "="*50)
    print(f"🌤️  天気予報Bot実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 1. 天気データを取得
    raw_data = weather.get_weather_data()
    
    if not raw_data:
        print("❌ 処理を中断します")
        return False
    
    # 2. データを整形
    weather_info = weather.parse_weather_data(raw_data)
    
    if not weather_info:
        print("❌ 処理を中断します")
        return False
    
    # 3. Embedメッセージを作成
    embed = create_embed_message(weather_info)
    
    # 4. Discordに送信
    success = send_to_discord(embed)
    
    if success:
        print("🎉 天気予報の投稿が完了しました!")
    else:
        print("😞 天気予報の投稿に失敗しました")
    
    print("="*50 + "\n")
    return success


# 🆕 Render Cron Job用のエントリーポイント
if __name__ == '__main__':
    """
    Render Cron Jobでは、1回実行して終了すればOK
    Renderが毎日指定時刻に自動実行してくれる
    """
    print("\n🤖 Discord天気予報Bot (Render Cron Job)")
    print(f"🌍 タイムゾーン: {config.TIMEZONE}")
    print(f"📍 対象地域: 東京 (緯度: {config.LATITUDE}, 経度: {config.LONGITUDE})\n")
    
    # 1回だけ実行
    success = post_weather_forecast()
    
    # 終了コードを返す(Renderのログ用)
    if success:
        print("✅ 実行完了。プログラムを終了します。\n")
        exit(0)  # 成功
    else:
        print("❌ 実行失敗。プログラムを終了します。\n")
        exit(1)  # 失敗
