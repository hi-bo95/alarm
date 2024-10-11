from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# データベース接続
def get_db_connection():
    conn = sqlite3.connect('sodateru.db')
    conn.row_factory = sqlite3.Row
    return conn

# アラームの自動削除関数
def delete_past_alarms():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn = get_db_connection()
    conn.execute("DELETE FROM alarms WHERE alarm_time <= ?", (current_time,))
    conn.commit()

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

    conn.close()
    #return render_template('index.html', next_alarm=next_alarm, alarms=alarms, tasks=tasks, points=user['points'])
    return render_template('index.html', next_alarm=next_alarm, alarms=alarms)


# 栽培期間設定ページ
@app.route('/set_cultivation_period', methods=['GET', 'POST'])
def set_cultivation_period():
    if request.method == 'POST':
        cultivation_period = request.form['cultivation_period']
        user_id = 1  # 仮にユーザーを設定
        today = datetime.now().date()
        conn = get_db_connection()
        conn.execute('UPDATE users SET cultivation_period = ? WHERE user_id = ?', (cultivation_period, alarm_id))
        conn.execute('UPDATE users SET start_date = ? WHERE user_id = ?', (today, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('set_cultivation_period.html')


@app.route('/add_alarm', methods=['GET','POST'])
def add_alarm():
    delete_past_alarms()        # アラームの自動削除関数
    conn = get_db_connection()
    alarms = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC').fetchall()
    conn.close()
    if request.method == 'POST':
        # フォームから日付と時間を取得
        alarm_date = request.form['date']
        alarm_time = request.form['time']
        alarm_day = request.form['day']
            
        # 日付と時間を結合して alarm_time を作成 (例: "2024-10-09 07:30")
        alarm_datetime = f"{alarm_date} {alarm_time}"
        print(alarm_datetime)

        user_id = 1  # 仮にユーザーを設定

        # データベースに挿入
        conn = get_db_connection()
        conn.execute('INSERT INTO alarms (alarm_time) VALUES (?)', (alarm_datetime,)) 
        conn.execute('UPDATE users SET day = ? WHERE user_id = ?', (alarm_day, user_id))
        conn.commit()
        alarms = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC').fetchall()
        conn.close()
        #return redirect(url_for('index'))
        return render_template('set_alarm.html', alarms=alarms)
    
    return render_template('set_alarm.html', alarms=alarms)
    #return render_template('index.html', next_alarm=next_alarm, alarms=alarms)



# アラームの削除
@app.route('/delete_alarm', methods=['POST'])
def delete_alarm():
    delete_past_alarms()        # アラームの自動削除関数
    alarm_id = request.form['alarm_id']
    conn = get_db_connection()
    conn.execute('DELETE FROM alarms WHERE alarm_id = ?', (alarm_id,))
    conn.commit()
    alarms = conn.execute('SELECT * FROM alarms ORDER BY alarm_time ASC').fetchall()
    conn.close()
    #return redirect(url_for('index'))
    return render_template('set_alarm.html', alarms=alarms)

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
@app.route('/alarm_page')
def alarm_page():
    delete_past_alarms()        # アラームの自動削除関数
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (1,)).fetchone()
    conn.close()
    print(user)
    days_since_start=user['day']
    print(days_since_start)

    if days_since_start:
        #alarm_time = datetime.strptime(alarm['alarm_time'], '%Y-%m-%d %H:%M')
        #start_date = alarm_time.date()
        #today = datetime.now().date()
        #days_since_start = (today - start_date).days
        print(days_since_start)

        # 経過日数に応じた手入れ内容
        if days_since_start <= 1:
            tasks = [
                "種をまく"
            ]
            img="grow01.png"
        elif 2 <= days_since_start <= 3:
            tasks = [
                "水をやる"
            ]
            img="grow02"
        elif 4 <= days_since_start <= 7:
            tasks = [
                "水をやる",
                "日光に当てる"
            ]
            img="grow03"
        elif 8 <= days_since_start <= 14:
            tasks = [
                "水をやる",
                "雑草を抜く"
            ]
            img="grow04"
        elif days_since_start == 15:
            tasks = [
                "水をやる",
                "肥料を与える"
            ]
            img="grow05"
        elif 16 <= days_since_start <= 29:
            tasks = [
                "水をやる",
                "雑草を抜く"
            ]
            img="grow06"
        else:
            tasks = ["花が咲きました！おめでとう！"]
            img="grow07"

    else:
        tasks = []

    return render_template('alarm_page.html', tasks=tasks, img=img)

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


if __name__ == '__main__':
    app.run(debug=True)
