# auto-click
Auto left click using pyautogui until press Esc.

# 内容

* PC画面の所定位置を一定時間間隔で自動クリックするPythonのプログラム例を示す
    * 最初にクリックする座標とウィンドウを取得
    * クリックはEscボタンを押すまで継続
    * 記載プログラムではマウス動作などで多少時間間隔は前後するため、改善の余地あり
* Pythonの構築やモジュールのインストール方法は未記載


# プログラム概要

* 以下のモジュールを使用
    * pyautogui
        * 画面位置(座標)取得とマウス操作に使用
    * pygetwindow
        * 所定の画面をアクティブ化するために使用
    * pynput
        * マウス、キーボードの動作検知に使用
    * time
        * 動作時間の確認に使用。任意
    * csv
        * 動作時間の結果のテキスト出力に使用。任意
        
<br>

* プログラムの流れは以下
    1. モジュールのインポート
    1. クリック座標の取得
        * クリック座標の取得
        * クリックする画面ウィンドウの取得
        * （任意）クリック座標の出力
        * （任意）クリック座業の読込み
    1. 自動クリックの実行
        * ウィンドウ・クリック座標のチェック
        * クリック開始
        * （任意）自動クリック時間の出力


# プログラム詳細
最後にまとめたプログラムを記載する。

## モジュールのインポート
time, csvは任意。

```python
import pyautogui
import pygetwindow as gw
from pynput import mouse, keyboard
import time 
import csv
```


## クリック座標の取得
get_cursor_positonで左クリックの座標を取得する。クリックの検知にはpynputを使用
クリックしてアクティブ化されたウィンドウも取得し、後からアクティブ化できるようにする。
```python

def on_click_for_pos(x, y, button, pressed):
    if pressed:
        return False


def get_cursor_position():
    # マウスのクリック検知
    with mouse.Listener(on_click=on_click_for_pos) as listener:
        listener.join()
    # ---
    x, y = pyautogui.position()  # カーソルの位置を取得
    print('カーソルの位置: x = {}, y = {}'.format(x, y))
    # --- ウィンドウの取得 ---
    time.sleep(1)
    active_window = gw.getActiveWindow()
    if not active_window is None:
        print('対象ウィンドウ: {}'.format(active_window.title))
    else:
        print('対象ウィンドウ: なし')
    print('\n --- END: Get Cursor Position ---')
    return x, y, active_window


tposx, tposy, window = get_cursor_position()
```

### (任意）クリック座標の出力、読み込み
座標取得とクリック実行プログラムを分ける場合は、取得したクリック座標とウィンドウをファイル出力する。

```python
def get_window(window_title):
    window = gw.getWindowsWithTitle(window_title)
    nwindow = len(window)
    if nwindow == 0:
        print('ウィンドウが見つかりませんでした')
        return None
    elif nwindow == 1:
        return window[0]
    elif nwindow > 1:
        print('複数のウィンドウが見つかりました: {}'.format(window))
        return None

def save_pos(tposx, tposy, window):
    if window is None:
        windowname = ''
    else:
        windowname = window.title
    with open('target_pos.txt', 'w') as f:
        f.write('{}\n{}\n{}'.format(tposx, tposy, windowname))

def load_pos(fname='target_pos.txt'):
    with open(fname, 'r') as f:
        data = f.read().splitlines()
        ndata = len(data)
        if ndata == 2:
            tposx, tposy = data[0], data[1]
            window = None
        elif ndata == 3:
            tposx, tposy, windowname = data[0], data[1], data[2]
            window = get_window(windowname)
        else:
            print('Read Error')
            return None
    return int(tposx), int(tposy), window

save_pos(tposx, tposy, window)  # 保存時
tposx, tposy, window = load_pos()  # 読込み時
```

## クリックの開始
* Escを押すまで、取得した座標位置を左クリックするプログラム
    pynputのkeyboard.Listener(on_press=on_press_key)でEscが押されたかを判定
* check_window_pos関数で、実行前にウィンドウやクリック座標に誤った値が入っていないかを確認
* ウィンドウのアクティブ化は、window.activate()ではエラーが生じる場合があるため、最小化後、復元することで強制的にアクティブ化。詳細は以下を参照。
    * https://github.com/asweigart/PyGetWindow/issues/31
    * http://blawat2015.no-ip.com/~mieki256/diary/20220424.html
* waittimeで設定プログラム簡略化のため、クリック間隔はsleep関数でwaittimeの間待機させるプログラムとしている。そのため、pyautoguiのマウス動作等の時間で少なくとも0.数秒は長くなり、時間間隔の精度が必要な場合は要改善。
    * pyautoguiの設定(引数)で調整できるかは未確認。
* 以下のプログラムは、クリックの時間間隔を出力も含む
    * waittime：クリックのおおよその時間間隔（sec）
    * cnt：クリック回数
    * totol_time：最初のクリックからの経過時間（sec）
    * dtime：前のクリックからの経過時間（sec）

```python
def on_press_key(key):
    # Escが押されると終了
    global esc_pressed
    if key == keyboard.Key.esc:
        esc_pressed = True


def check_window_pos(tposx, tposy, window):
    is_click_ok = True
    if window is None:
        is_click_ok = False
    if (not isinstance(tposx, int)) or (not isinstance(tposy, int)):
        is_click_ok = False
    return is_click_ok


def activate_window(window):
    # window.activate()ではエラーが生じる可能性があるため、最小化、復元で強制的にアクティブ化
    if not window is None:
        window.minimize()
        window.restore()


def auto_click(tposx, tposy, window, waittime=1):
    is_click_ok = check_window_pos(tposx, tposy, window)
    if not is_click_ok:
        print('ウィンドウもしくはクリック座標が不適切なため未実行')
        return ['Error']
    # ---
    global esc_pressed
    esc_pressed = False
    # window.activate()  # 対象の画面をアクティブ化 
    activate_window(window)
    # --- 出力リスト ---
    outlist = []
    outlist.append(['cnt', 'total_time', 'dtime'])
    # ---　ループを抜けるためのキーボード検知用 ---
    listener = keyboard.Listener(on_press=on_press_key)
    listener.start()
    # ---
    cnt = 0
    time0 = time.time()  # 初期時間
    while True:
        time1 = time.time()   
        # --- メイン処理 ---
        pyautogui.click(x=tposx, y=tposy)  # 所定の位置に移動してクリック。クリック内容を変える場合は、本行を変更。
        if  esc_pressed: # Escが押されたらループを抜ける
            break
        time.sleep(waittime)  # 所定の時間待機
        # --- 出力用 ---
        cnt += 1
        time2 = time.time()
        dtime = time2 - time1
        totaltime = time2 - time0
        outlist.append([cnt, totaltime, dtime])
        if cnt%2 == 0:
            print('cnt: {}, time: {:g}'.format(cnt, dtime))
    # ---
    listener.stop()  # キーボード検知を停止
    print('\n --- End: Auto Click ---')
    return outlist


outlist = auto_click(tposx, tposy, window, waittime=0.9)
```


### (任意)　クリックの時間間隔の出力
クリックの時間間隔を把握したい場合は出力。

```python
def save_csv(fname, outlist):
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(outlist)

save_csv('out_autoclick.csv', outlist)
```


#　プログラムのまとめ
上記のプログラムをまとめて記載する

```python
import pyautogui
import pygetwindow as gw
from pynput import mouse, keyboard
import time
import csv


def get_window(window_title):
    window = gw.getWindowsWithTitle(window_title)
    nwindow = len(window)
    if nwindow == 0:
        print('ウィンドウが見つかりませんでした')
        return None
    elif nwindow == 1:
        return window[0]
    elif nwindow > 1:
        print('複数のウィンドウが見つかりました: {}'.format(window))
        return None


def on_click_for_pos(x, y, button, pressed):
    if pressed:
        return False


def get_cursor_position():
    # マウスのクリック検知
    with mouse.Listener(on_click=on_click_for_pos) as listener:
        listener.join()
    # ---
    x, y = pyautogui.position()  # カーソルの位置を取得
    print('カーソルの位置: x = {}, y = {}'.format(x, y))
    # --- ウィンドウの取得 ---
    time.sleep(1)
    active_window = gw.getActiveWindow()
    if not active_window is None:
        print('対象ウィンドウ: {}'.format(active_window.title))
    else:
        print('対象ウィンドウ: なし')
    print('\n --- END: Get Cursor Position ---')
    return x, y, active_window


def save_pos(tposx, tposy, window):
    if window is None:
        windowname = ''
    else:
        windowname = window.title
    with open('target_pos.txt', 'w') as f:
        f.write('{}\n{}\n{}'.format(tposx, tposy, windowname))


def load_pos(fname='target_pos.txt'):
    with open(fname, 'r') as f:
        data = f.read().splitlines()
        ndata = len(data)
        if ndata == 2:
            tposx, tposy = data[0], data[1]
            window = None
        elif ndata == 3:
            tposx, tposy, windowname = data[0], data[1], data[2]
            window = get_window(windowname)
        else:
            print('Read Error')
            return None
    return int(tposx), int(tposy), window


def save_csv(fname, outlist):
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(outlist)


def on_press_key(key):
    # Escが押されると終了
    global esc_pressed
    if key == keyboard.Key.esc:
        esc_pressed = True


def check_window_pos(tposx, tposy, window):
    is_click_ok = True
    if window is None:
        is_click_ok = False
    if (not isinstance(tposx, int)) or (not isinstance(tposy, int)):
        is_click_ok = False
    return is_click_ok


def activate_window(window):
    # window.activate()ではエラーが生じる可能性があるため、ネットを参考に最小化、復元で強制的にアクティブ化
    if not window is None:
        window.minimize()
        window.restore()


def auto_click(tposx, tposy, window, waittime=1):
    is_click_ok = check_window_pos(tposx, tposy, window)
    if not is_click_ok:
        print('ウィンドウもしくはクリック座標が不適切なため未実行')
        return ['Error']
    # ---
    global esc_pressed
    esc_pressed = False
    # window.activate()  # 対象の画面をアクティブ化 
    activate_window(window)
    # --- 出力リスト ---
    outlist = []
    outlist.append(['cnt', 'total_time', 'dtime'])
    # ---　ループを抜けるためのキーボード検知用 ---
    listener = keyboard.Listener(on_press=on_press_key)
    listener.start()
    # ---
    cnt = 0
    time0 = time.time()  # 初期時間
    while True:
        time1 = time.time()   
        # --- メイン処理 ---
        pyautogui.click(x=tposx, y=tposy)  # 所定の位置に移動してクリック。クリック内容を変える場合は、本行を変更。
        if  esc_pressed: # Escが押されたらループを抜ける
            break
        time.sleep(waittime)  # 所定の時間待機
        # --- 出力用 ---
        cnt += 1
        time2 = time.time()
        dtime = time2 - time1
        totaltime = time2 - time0
        outlist.append([cnt, totaltime, dtime])
        if cnt%2 == 0:
            print('cnt: {}, time: {:g}'.format(cnt, dtime))
    # ---
    listener.stop()  # キーボード検知を停止
    print('\n --- End: Auto Click ---')
    return outlist



tposx, tposy, window = get_cursor_position()
save_pos(tposx, tposy, window)

tposx, tposy, window = load_pos()
outlist = auto_click(tposx, tposy, window, waittime=0.9)

save_csv('out_autoclick.csv', outlist)

```
