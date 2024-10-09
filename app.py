from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# データベース接続
def get_db_connection():
    conn = sqlite3.connect('sodateru.db')
    conn.row_factory = sqlite3.Row
    return conn

# ホームページ
@app.route('/')
def index():
    conn = get_db_connection()
    alarms = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC').fetchall()
    user = conn.execute('SELECT * FROM users WHERE user_id = 1').fetchone()  # ユーザーIDを仮定
 
    # 直近のアラームを取得
    alarms = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC').fetchall()
    if alarms:
        next_alarm = alarms[0]['alarm_time']
    else:
        next_alarm = "アラームは設定されていません"

    # 栽培開始日と期間を取得
    cultivation = conn.execute('SELECT * FROM cultivation ORDER BY id DESC LIMIT 1').fetchone()
    tasks = []
    if cultivation:
        start_date = datetime.strptime(cultivation['start_date'], '%Y-%m-%d')
        days_passed = (datetime.now() - start_date).days
        tasks = get_cultivation_tasks(days_passed, cultivation['duration'])

    conn.close()
    return render_template('index.html', next_alarm=next_alarm, alarms=alarms, tasks=tasks, points=user['points'])

# アラームページ（アラームが鳴ったときに表示するページ）
@app.route('/alarm_page')
def alarm_page():
    conn = get_db_connection()
    alarm = conn.execute('SELECT * FROM alarms WHERE id = ?', (1,)).fetchone()  # 仮に1つのアラームのみ取得
    conn.close()

    if alarm:
        alarm_time = datetime.strptime(alarm['alarm_time'], '%Y-%m-%d %H:%M')
        start_date = alarm_time.date()
        today = datetime.now().date()
        days_since_start = (today - start_date).days

        # 経過日数に応じた手入れ内容
        if days_since_start <= 7:
            tasks = [
                "種を準備する",
                "土を耕す",
                "種をまく"
            ]
        elif 8 <= days_since_start <= 14:
            tasks = [
                "水をやる",
                "雑草を抜く"
            ]
        elif 15 <= days_since_start <= 30:
            tasks = [
                "肥料を与える",
                "日光に当てる"
            ]
        else:
            tasks = ["花が咲きました！おめでとう！"]

    else:
        tasks = []

    return render_template('alarm_page.html', tasks=tasks)

# 手入れ終了ボタン
@app.route('/complete_task', methods=['POST'])
def complete_task():
    today = datetime.now().date()
    weekday = today.weekday()  # Monday is 0 and Sunday is 6
    points_to_add = 2 if weekday < 5 else 1  # 平日は2ポイント、週末は1ポイント

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()  # ユーザーIDを仮定
    new_points = user['points'] + points_to_add

    conn.execute('UPDATE users SET points = ? WHERE id = ?', (new_points, 1))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# 栽培期間設定ページ
@app.route('/set_cultivation_period', methods=['GET', 'POST'])
def set_cultivation_period():
    if request.method == 'POST':
        cultivation_period = request.form['cultivation_period']
        alarm_id = 1  # 仮に1つのアラームに設定
        conn = get_db_connection()
        conn.execute('UPDATE alarms SET cultivation_period = ? WHERE id = ?', (cultivation_period, alarm_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('set_cultivation_period.html')

# アラームの追加
@app.route('/add_alarm', methods=['POST'])
def add_alarm():
    alarm_time = request.form['alarm_time']
    conn = get_db_connection()
    conn.execute('INSERT INTO alarms (alarm_time, cultivation_period) VALUES (?, ?)', (alarm_time, 1))  # デフォルト1ヶ月
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# アラームの削除
@app.route('/delete_alarm', methods=['POST'])
def delete_alarm():
    alarm_id = request.form['alarm_id']
    conn = get_db_connection()
    conn.execute('DELETE FROM alarms WHERE id = ?', (alarm_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
