def recommend_clothing(temp_max, temp_min):
    """
    気温から服装をおすすめする関数
    
    Args:
        temp_max: 最高気温
        temp_min: 最低気温
        
    Returns:
        str: おすすめの服装メッセージ
    """
    # 解説:
    # この関数は気温を受け取って、服装のアドバイスを返します
    
    # 気温差を計算
    temp_diff = temp_max - temp_min
    
    # 解説:
    # 最高気温と最低気温の差を計算
    # 例: 最高20℃、最低10℃ → 差は10℃
    
    # 基本の服装を決める(最高気温ベース)
    if temp_max >= 28:
        clothing = "半袖で大丈夫です。暑がりの人は1日半袖で過ごせます。"
    elif temp_max >= 25:
        clothing = "半袖／薄手の長袖で大丈夫です。"
    elif temp_max >= 20:
        clothing = "半袖＋長袖シャツで大丈夫です。昼間は半袖で過ごせます。"
    elif temp_max >= 15:
        clothing = "長袖シャツ＋薄手のカーディガン／ナイロンパーカーで大丈夫です。"
    elif temp_max >= 10:
        clothing = "長袖シャツ＋薄手のカーディガン／Tシャツ＋スウェット／トレンチコートで大丈夫です。"
    elif temp_max >= 5:
        clothing = "長袖＋厚手のコート／ダウンジャケットで大丈夫です。"
    else:
        clothing = "冬服＋ダウン・厚手コートで大丈夫です。"
    
    # 解説:
    # if-elif-else構文で条件分岐
    # 上から順に条件をチェックして、最初に当てはまったものを実行
    # 
    # 例: temp_max = 22℃の場合
    # - 28以上? → No
    # - 25以上? → No
    # - 20以上? → Yes! → "半袖＋長袖シャツ..."を選択
    
    # 追加のアドバイス
    additional_advice = []
    
    # 解説:
    # additional_advice = [] は空のリスト
    # 後で追加アドバイスを入れていきます
    
    # 最低気温が低い場合
    if temp_min < 10:
        additional_advice.append("朝晩は冷えます。")
    
    # 解説:
    # append()はリストに要素を追加するメソッド
    # 例: [] → ["朝晩は冷えます。"]
    
    # 気温差が大きい場合
    if temp_diff >= 10:
        additional_advice.append("脱ぎ着しやすい服を。")
    
    # 解説:
    # 気温差が10℃以上なら、調整しやすい服を勧める
    # 例: 朝10℃、昼25℃ → 差15℃ → アドバイス追加
    
    # 追加アドバイスを服装メッセージに結合
    if additional_advice:
        clothing += "\n" + "".join(additional_advice)
    
    # 解説:
    # if additional_advice: は「リストが空でなければ」という意味
    # "\n"は改行
    # "".join(リスト)はリストの要素を結合
    # 例: ["朝晩は冷えます。", "脱ぎ着しやすい服を。"]
    #   → "朝晩は冷えます。脱ぎ着しやすい服を。"
    
    return clothing


def recommend_items(pop, temp_max):
    """
    降水確率と気温から持ち物をおすすめする関数
    
    Args:
        pop: 降水確率(%)
        temp_max: 最高気温
        
    Returns:
        str: おすすめの持ち物メッセージ
    """
    items = []
    
    # 解説:
    # items = [] も空のリスト
    # 持ち物を入れていきます
    
    # 降水確率で傘の判定
    if pop >= 50:
        items.append("傘必須です。")
    elif pop >= 30:
        items.append("折りたたみ傘があると安心です。")
    else:
        items.append("傘は不要です。")
    
    # 解説:
    # 降水確率が50%以上なら傘必須
    # 30%〜49%なら折りたたみ傘推奨
    # 30%未満なら不要
    
    # 最高気温が高い場合
    if temp_max >= 30:
        items.append("帽子・飲み物も忘れずに。")
    
    # 解説:
    # 30℃以上の猛暑日は熱中症対策
    
    # リストを改行で結合して返す
    return "\n".join(items)
    
    # 解説:
    # "\n".join(リスト)は各要素を改行で繋げる
    # 例: ["傘必須です。", "帽子・飲み物も忘れずに。"]
    #   → "傘必須です。\n帽子・飲み物も忘れずに。"


def get_weather_emoji(weather_main):
    """
    天気の種類から絵文字を返す関数
    
    Args:
        weather_main: 天気の種類(Clear, Rain, Cloudsなど)
        
    Returns:
        str: 天気に対応する絵文字
    """
    # 解説:
    # weather_mainはAPIから返される天気の大分類
    
    # 天気と絵文字の対応表(辞書)
    emoji_map = {
        'Clear': '☀️',      # 晴れ
        'Clouds': '☁️',     # 曇り
        'Rain': '🌧️',      # 雨
        'Drizzle': '🌦️',   # 小雨
        'Thunderstorm': '⛈️',  # 雷雨
        'Snow': '⛄',       # 雪
        'Mist': '🌫️',      # 霧
        'Fog': '🌫️',       # 霧
    }
    
    # 解説:
    # 辞書(dictionary)は{キー: 値}の形式
    # 天気の名前(キー)から絵文字(値)を取得できる
    
    # 対応する絵文字を返す(なければデフォルト🌤️)
    return emoji_map.get(weather_main, '🌤️')
    
    # 解説:
    # .get(キー, デフォルト値)
    # - キーが辞書にあれば、その値を返す
    # - キーがなければ、デフォルト値を返す
    # 例: emoji_map.get('Clear', '🌤️') → '☀️'
    # 例: emoji_map.get('Unknown', '🌤️') → '🌤️'


def get_embed_color(weather_main):
    """
    天気の種類からDiscord Embedの色を返す関数
    
    Args:
        weather_main: 天気の種類
        
    Returns:
        int: 16進数カラーコード
    """
    # 解説:
    # Discord Embedは色を16進数で指定します
    # 0xFFD700 のような形式
    
    color_map = {
        'Clear': 0xFFD700,      # ゴールド(晴れ)
        'Clouds': 0x808080,     # グレー(曇り)
        'Rain': 0x4682B4,       # スティールブルー(雨)
        'Drizzle': 0x87CEEB,    # スカイブルー(小雨)
        'Thunderstorm': 0x483D8B,  # ダークスレートブルー(雷雨)
        'Snow': 0xFFFFFF,       # ホワイト(雪)
        'Mist': 0xD3D3D3,       # ライトグレー(霧)
        'Fog': 0xD3D3D3,        # ライトグレー(霧)
    }
    
    return color_map.get(weather_main, 0x3498db)
    
    # 解説:
    # デフォルトは0x3498db(青色)
