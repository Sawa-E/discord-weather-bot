import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

import config
import weather
import recommend

# 解説:
# 必要なモジュールをインポート
# - requests: Webhook送信用
# - apscheduler: スケジュール実行用
# - pytz: タイムゾーン処理用
# - 自作モジュール: config, weather, recommend


def create_embed_message(weather_info):
    """
    Discord Embed形式のメッセージを作成する
    
    Args:
        weather_info: 天気情報の辞書
        
    Returns:
        dict: Discord Embed形式のメッセージ
    """
    # 解説:
    # Discord Embedは見栄えの良いメッセージ形式
    # カラー、画像、フィールドなどを設定できます
    
    # 天気に応じた絵文字とカラーを取得
    weather_emoji = recommend.get_weather_emoji(weather_info['weather_main'])
    embed_color = recommend.get_embed_color(weather_info['weather_main'])
    
    # 解説:
    # weather_main(例: 'Clear', 'Rain')から絵文字と色を取得
    
    # 服装と持ち物のアドバイスを生成
    clothing = recommend.recommend_clothing(
        weather_info['temp_max'],
        weather_info['temp_min']
    )
    
    items = recommend.recommend_items(
        weather_info['pop'],
        weather_info['temp_max']
    )
    
    # 解説:
    # recommend.pyの関数を呼び出して、アドバイスを取得
    
    # 天気アイコンのURL
    icon_url = f"https://openweathermap.org/img/wn/{weather_info['weather_icon']}@2x.png"
    
    # 解説:
    # OpenWeatherMapは天気アイコンを提供しています
    # 例: '01d' → 晴れのアイコン
    
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
    
    # 解説:
    # Embed形式は辞書で定義します
    # - title: タイトル
    # - color: 色(16進数)
    # - thumbnail: サムネイル画像
    # - fields: 情報のフィールド(配列)
    # - footer: フッター
    # 
    # inline: True → 横に並べる
    # inline: False → 縦に並べる
    
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
        
        # 解説:
        # "embeds"は配列形式で、複数のEmbedを送れます
        # 今回は1つだけ
        
        # Webhookに送信
        response = requests.post(
            config.DISCORD_WEBHOOK_URL,
            json=payload
        )
        
        # 解説:
        # requests.post()でWebhookにデータを送信
        # json=payloadで、辞書をJSON形式で送る
        
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
    
    # 解説:
    # 実行ログを見やすく表示
    
    # 1. 天気データを取得
    raw_data = weather.get_weather_data()
    
    if not raw_data:
        print("❌ 処理を中断します")
        return
    
    # 解説:
    # データ取得に失敗したら、ここで終了
    
    # 2. データを整形
    weather_info = weather.parse_weather_data(raw_data)
    
    if not weather_info:
        print("❌ 処理を中断します")
        return
    
    # 3. Embedメッセージを作成
    embed = create_embed_message(weather_info)
    
    # 4. Discordに送信
    success = send_to_discord(embed)
    
    if success:
        print("🎉 天気予報の投稿が完了しました!")
    else:
        print("😞 天気予報の投稿に失敗しました")
    
    print("="*50 + "\n")


def main():
    """
    メイン関数: スケジューラーを設定してBotを起動
    """
    print("\n" + "🤖 Discord天気予報Botを起動します")
    print(f"⏰ 毎日 {config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d} に実行します")
    print(f"🌍 タイムゾーン: {config.TIMEZONE}")
    print(f"📍 対象地域: 東京 (緯度: {config.LATITUDE}, 経度: {config.LONGITUDE})")
    print("\n💡 Ctrl+C で終了できます\n")
    
    # 解説:
    # 起動時の情報を表示
    # :02dは「2桁で0埋め」の意味(例: 6 → 06)
    
    # スケジューラーを作成
    scheduler = BlockingScheduler(timezone=pytz.timezone(config.TIMEZONE))
    
    # 解説:
    # BlockingScheduler: プログラムをずっと動かし続けるスケジューラー
    # timezone: 日本時間(Asia/Tokyo)を設定
    
    # スケジュールを登録
    scheduler.add_job(
        post_weather_forecast,              # 実行する関数
        trigger=CronTrigger(
            hour=config.SCHEDULE_HOUR,      # 時(6)
            minute=config.SCHEDULE_MINUTE,  # 分(0)
            timezone=pytz.timezone(config.TIMEZONE)
        ),
        id='weather_forecast',              # ジョブのID
        name='天気予報投稿',                # ジョブの名前
        replace_existing=True               # 既存のジョブを置き換え
    )
    
    # 解説:
    # CronTrigger: 指定した時刻に実行するトリガー
    # hour=6, minute=0 → 毎日6:00に実行
    
    # 起動時に1回テスト実行(任意)
    print("📢 起動テスト: 天気予報を1回実行します...\n")
    post_weather_forecast()
    
    # 解説:
    # 起動直後に1回実行して、動作確認
    # この行を削除すれば、指定時刻まで待機します
    
    print("✅ スケジューラーを開始しました。次回実行を待機中...\n")
    
    try:
        # スケジューラーを起動(ここでプログラムが待機状態になる)
        scheduler.start()
        
    except (KeyboardInterrupt, SystemExit):
        # Ctrl+Cで終了した場合
        print("\n\n👋 Bot を終了します...")
        scheduler.shutdown()
        print("✅ 正常に終了しました\n")


# プログラムのエントリーポイント
if __name__ == '__main__':
    """
    このファイルを直接実行した時のみ動く
    python bot.py で実行
    """
    main()
