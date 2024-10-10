# %%
import os
import pyautogui
import pygetwindow as gw
from pynput import mouse, keyboard
import time
import csv
import argparse



# %%
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
    print('\nEND: Get Cursor Position\n')
    return x, y, active_window


def save_pos(tposx, tposy, window, fname='target_pos_window.txt'):
    if window is None:
        windowname = ''
    else:
        windowname = window.title
    with open(fname, 'w') as f:
        f.write('{}\n{}\n{}'.format(tposx, tposy, windowname))


def load_pos(fname='target_pos_window.txt'):
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
        time.sleep(1)  # ウィンドウ操作の待機


def auto_click(tposx, tposy, window, waittime=1, printstep=1):
    colname = ['cnt', 'total_time', 'dtime']
    # ---
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
    outlist.append(colname)
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
        if cnt%printstep == 0:
            print('cnt: {}, time: {:g}'.format(cnt, dtime))
    # ---
    listener.stop()  # キーボード検知を停止
    print('\n---\nEnd: Auto Click')
    return outlist


def main(args):
    if args.pos:
        print('To get cursor position and window, left click the target position and the target window.')
        tposx, tposy, window = get_cursor_position()
        save_pos(tposx, tposy, window, fname=args.fname_tpos_window)
    if args.click:
        if args.pos:
            time.sleep(1)  # ファイルの作成を待つため
        print('Start Auto Click. To stop, press Esc.')
        print('Wait time: {} sec,  Print: per {} step'.format(args.waittime, args.printstep))
        print('---')
        tposx, tposy, window = load_pos(fname=args.fname_tpos_window)
        outlist = auto_click(tposx, tposy, window, waittime=args.waittime, printstep=args.printstep)
        save_csv(args.fname_outcsv, outlist)


def get_args_using_argparse():
    parser = argparse.ArgumentParser(description='To get cursor position and window, use "-p" option.\nTo start autoclick, use "-c" option.')
    parser.add_argument('-p', '--pos', action='store_true', help='get cursor position and window')
    parser.add_argument('-c', '--click', action='store_true', help='start autoclick')
    parser.add_argument('-t', '--time', action='store', type=float,  dest='waittime', default=1.0, help='wait time for click and wait')
    parser.add_argument('-s', '--printstep', action='store', type=int,  dest='printstep', default=1, help='print step')
    parser.add_argument('-f', '--fname', action='store', dest='fname_tpos_window', default='target_pos_window.txt', help='filename of target pos and windows')
    parser.add_argument('-o', '--outfname', action='store', dest='fname_outcsv', default='out_autoclick.csv', help='filename of output csv')
    args = parser.parse_args()
    args.is_pause_console = False
    args.is_exe_main = True
    return args


class ReadArgs():
    def __init__(self, fname='setting.txt'):
        vs = self.get_args_from_file(fname)
        if vs is None:
            self.is_exe_main = False
            self.is_pause_console = True
        else:
            self.is_exe_main = True
            self.pos = bool(int(vs[0]))
            self.click = bool(int(vs[1]))
            self.waittime = float(vs[2])
            self.printstep = int(vs[3])
            self.fname_tpos_window = str(vs[4])
            self.fname_outcsv = str(vs[5])
            self.is_pause_console = bool(int(vs[6]))


    def get_args_from_file(self, fname):
        if os.path.exists(fname) is False:
            print('Error: No file: {}'.format(fname))
            return None
        with open(fname, 'r') as f:
            data = f.read().splitlines()
        vs = []
        for i, d0 in enumerate(data):
            if i == 0:
                continue
            d = d0.split('#')
            v = d[0].strip()
            vs.append(v)
        return vs


# %%
if __name__ == '__main__':
    # args = get_args_using_argparse()
    args = ReadArgs()
    # ---
    if args.is_exe_main:
        main(args)
    # ---
    print('\n--- Completed! ---')
    if args.is_pause_console:
        print('\nClose console...')
        os.system('pause')

# %%

# %%