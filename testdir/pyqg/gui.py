#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import queue
import sys
import os

# 自作モジュールのインポート
try:
    from .processor import process_dem, MIN_SLOPE, THRESHOLD
except (ImportError, ValueError):
    # 直接実行時用
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from pyqg.processor import process_dem, MIN_SLOPE, THRESHOLD

class DEMProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DEM処理ツール")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # 処理中フラグ
        self.processing = False
        
        # メッセージ用キュー
        self.message_queue = queue.Queue()
        
        # スタイル設定
        self.setup_styles()
        
        # UIの作成
        self.create_widgets()
        
        # 定期的にメッセージキューをチェック
        self.check_queue()
    
    def setup_styles(self):
        """スタイルの設定"""
        style = ttk.Style()
        style.configure('TFrame', padding=10)
        style.configure('TLabel', padding=5)
        style.configure('TButton', padding=5)
        style.configure('TEntry', padding=5)
        style.configure('TRadiobutton', padding=5)
        
        # 見出しのスタイル
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        
        # ログのスタイル
        style.configure('Log.TFrame', background='white')
    
    def create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 入力ファイル選択
        ttk.Label(main_frame, text="入力DEMファイル:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.input_file = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Button(main_frame, text="参照...", command=self.browse_input_file).grid(row=0, column=2, padx=(0, 5))
        
        # 出力ディレクトリ選択
        ttk.Label(main_frame, text="出力ディレクトリ:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.output_dir = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Button(main_frame, text="参照...", command=self.browse_output_dir).grid(row=1, column=2, padx=(0, 5))
        
        # パラメータ設定
        params_frame = ttk.LabelFrame(main_frame, text="処理パラメータ", padding=10)
        params_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=(15, 10))
        
        # 最小勾配
        ttk.Label(params_frame, text="最小勾配:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.min_slope = tk.DoubleVar(value=MIN_SLOPE)
        ttk.Spinbox(params_frame, from_=0.01, to=10.0, increment=0.1, textvariable=self.min_slope, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 閾値
        ttk.Label(params_frame, text="チャネルネットワーク閾値:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.threshold = tk.IntVar(value=THRESHOLD)
        ttk.Spinbox(params_frame, from_=1, to=100, textvariable=self.threshold, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="処理ログ", padding=5)
        log_frame.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW, pady=(10, 5))
        
        # スクロールバー付きテキストエリア
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, font=('Courier New', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # 処理開始ボタン
        self.process_button = ttk.Button(button_frame, text="処理を開始", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        # クリアボタン
        ttk.Button(button_frame, text="ログをクリア", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # 終了ボタン
        ttk.Button(button_frame, text="終了", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # グリッドの設定
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def browse_input_file(self):
        """入力ファイルを選択"""
        file_path = filedialog.askopenfilename(
            title="入力DEMファイルを選択",
            filetypes=[("ASC files", "*.asc"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file.set(file_path)
            
            # 出力ディレクトリが未設定の場合は、入力ファイルと同じディレクトリをデフォルト値に設定
            if not self.output_dir.get():
                default_output = str(Path(file_path).parent / "output")
                self.output_dir.set(default_output)
    
    def browse_output_dir(self):
        """出力ディレクトリを選択"""
        dir_path = filedialog.askdirectory(title="出力ディレクトリを選択")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def log(self, message: str):
        """ログにメッセージを追加"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """ログをクリア"""
        self.log_text.delete(1.0, tk.END)
    
    def check_queue(self):
        """メッセージキューをチェックしてログに表示"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log(message)
        except queue.Empty:
            pass
        
        # 100ms後に再度チェック
        self.root.after(100, self.check_queue)
    
    def process_dem_thread(self):
        """バックグラウンドでDEM処理を実行"""
        try:
            # パラメータを取得
            input_path = self.input_file.get()
            output_dir = self.output_dir.get()
            
            # バリデーション
            if not input_path:
                self.message_queue.put("❌ 入力ファイルを指定してください")
                return
                
            if not output_dir:
                self.message_queue.put("❌ 出力ディレクトリを指定してください")
                return
            
            # 出力ディレクトリが存在しない場合は作成
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 処理を開始
            self.message_queue.put("処理を開始します...")
            
            # 処理を実行
            result = process_dem(
                input_path=input_path,
                output_dir=output_path,
                min_slope=self.min_slope.get(),
                threshold=self.threshold.get()
            )
            
            # 結果を表示
            if result['success']:
                self.message_queue.put("\n✅ 処理が正常に完了しました！")
                self.message_queue.put("\n【出力ファイル一覧】")
                for name, path in result.get('output_files', {}).items():
                    self.message_queue.put(f"- {name}: {path}")
            else:
                self.message_queue.put(f"\n❌ エラーが発生しました: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.message_queue.put(f"\n❌ 予期せぬエラーが発生しました: {str(e)}")
        finally:
            # 処理完了
            self.processing = False
            self.root.after(100, self.update_ui_state)
    
    def start_processing(self):
        """処理を開始"""
        if self.processing:
            return
            
        # UIを無効化
        self.processing = True
        self.update_ui_state()
        
        # ログをクリア
        self.clear_log()
        
        # バックグラウンドで処理を実行
        thread = threading.Thread(target=self.process_dem_thread, daemon=True)
        thread.start()
    
    def update_ui_state(self):
        """UIの状態を更新"""
        if self.processing:
            self.process_button.config(text="処理中...", state=tk.DISABLED)
        else:
            self.process_button.config(text="処理を開始", state=tk.NORMAL)

def main():
    """メイン関数"""
    root = tk.Tk()
    app = DEMProcessorApp(root)
    
    # ウィンドウを閉じる前の確認
    def on_closing():
        if app.processing:
            if messagebox.askokcancel("確認", "処理中です。終了してもよろしいですか？"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # メインループを開始
    root.mainloop()

if __name__ == "__main__":
    main()
