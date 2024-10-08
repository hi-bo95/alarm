from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのためのキー

# データベース接続
def get_db_connection():
    conn = sqlite3.connect('sodateru.db')
    conn.row_factory = sqlite3.Row
    return conn

# ホームページ（トップページ）
@app.route('/')
def index():
    conn = get_db_connection()
    alarms = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC').fetchall()
    conn.close()

    # 直近のアラームを取得
    if alarms:
        next_alarm = alarms[0]['alarm_time']  # 直近のアラーム時刻
    else:
        next_alarm = "アラームは設定されていません"

    return render_template('index.html', next_alarm=next_alarm, alarms=alarms)

# アラームの確認（API）
@app.route('/check_alarm')
def check_alarm():
    conn = get_db_connection()
    # 直近のアラームを取得
    alarm = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC LIMIT 1').fetchone()
    conn.close()

    if alarm:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        alarm_time = alarm['alarm_time']

        if current_time >= alarm_time:
            return 'redirect'
    
    return 'wait'

# アラームページ（アラームが鳴ったときに表示するページ）
@app.route('/alarm_page', methods=['GET', 'POST'])
def alarm_page():
    # 花の種をまいてから花が咲くまでの手順
    tasks = [
        "1. 花の種を準備する",
        "2. 土を用意して耕す",
        "3. 種をまく",
        "4. 水をやる",
        "5. 日光に当てる",
        "6. 毎日水をやる",
        "7. 花が咲くのを待つ"
    ]
    
    # 作業完了の確認ボタンが押された場合
    if request.method == 'POST':
        user_id = 1  # ユーザーIDを設定（実際のアプリでは適切に管理）
        add_points(user_id, 10)  # 例えば、10ポイントを加算
        message = "ポイントが加算されました！"
        return render_template('alarm_page.html', tasks=tasks, message=message)

    return render_template('alarm_page.html', tasks=tasks)

# アラーム設定ページ（別ページにする場合の例）
@app.route('/set_alarm_page')
def set_alarm_page():
    return render_template('set_alarm.html')

# アラームの追加
@app.route('/add_alarm', methods=['POST'])
def add_alarm():
    date = request.form['date']
    time = request.form['time']
    alarm_time = f"{date} {time}"

    conn = get_db_connection()
    conn.execute('INSERT INTO alarms (alarm_time) VALUES (?)', (alarm_time,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# アラームの削除
@app.route('/delete_alarm', methods=['POST'])
def delete_alarm():
    alarm_id = request.form['alarm_id']

    conn = get_db_connection()
    conn.execute('DELETE FROM alarms WHERE alarm_id = ?', (alarm_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# すべてのアラームを削除
@app.route('/delete_all_alarms', methods=['POST'])
def delete_all_alarms():
    conn = get_db_connection()
    conn.execute('DELETE FROM alarms')
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# ポイントを加算する関数
def add_points(user_id, points):
    conn = get_db_connection()
    conn.execute('UPDATE users SET points = points + ? WHERE id = ?', (points, user_id))
    conn.commit()
    conn.close()

# タイマーによる自動リダイレクト
@app.route('/auto_redirect')
def auto_redirect():
    session['alarm_active'] = False  # アラームが非アクティブになる
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
