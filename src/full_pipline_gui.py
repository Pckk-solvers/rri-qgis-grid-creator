#!/usr/bin/env python3
"""
Tkinter GUI フロントエンド
フルパイプライン（メッシュ生成 → 標高付与 → ASCII 変換 → PyQGIS処理）を
GUI 上で実行するためのスクリプト
"""

from __future__ import annotations

import sys
import threading
import queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from src.make_shp.zcol_list import get_zcol_list
from src.common.help_txt_read import load_help_text
from src.run_full_pipeline import run_full_pipeline


def get_base_dir() -> Path:
    """
    実行環境に応じた“プロジェクトルート”を返す。
      - 通常の Python 実行時: スクリプトの一つ上のディレクトリをプロジェクトルートとみなす
      - PyInstaller --onedir 時: 実行ファイルのあるディレクトリ
      - PyInstaller --onefile 時: sys._MEIPASS の一時展開先
    """
    if getattr(sys, "frozen", False):
        # PyInstaller でバンドルされた環境
        return Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(sys.executable).parent
    # 普通にスクリプト実行しているときは src/ の一つ上をルートに
    return Path(__file__).resolve().parent.parent

# 関数を使って一括設定
BASE_DIR   = get_base_dir()
CONFIG_DIR = BASE_DIR / "config"

def find_default_stdmesh() -> str | None:
    """config フォルダ内部の最初の .shp ファイルを返す"""
    if CONFIG_DIR.is_dir():
        for shp in CONFIG_DIR.glob("*.shp"):
            return str(shp)
    return None



class FullPipelineApp(ttk.Frame):
    """メインアプリケーションフレーム"""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        master.title("フルパイプライン実行 GUI")
        master.geometry("920x480")
        master.minsize(920, 480)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # 初期値設定
        default_std = find_default_stdmesh()
        self.default_stdmesh = default_std if default_std else None

        self.queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._build_widgets()
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.after(100, self._poll_queue)

    def _build_widgets(self) -> None:
        """UI ウィジェットの構築"""
        paddings = dict(padx=4, pady=4)
        paddings2 = dict(padx=4, pady=20)
        lbl_w = 22
        ent_w = 70

        # 左右分割ペインの作成
        paned = ttk.PanedWindow(self, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)

        # 左ペイン：入力フォーム用フレーム
        form = ttk.Frame(paned)
        paned.add(form)  # 左ペインを伸縮可能に

        # 右ペイン：ヘルプガイド用フレーム
        help_frame = ttk.LabelFrame(paned, text='使い方ガイド', padding=10)
        paned.add(help_frame, weight=1)

        help_text_widget = scrolledtext.ScrolledText(
            help_frame,
            wrap="none",
            width=40,
            height=20,
            font=('Meiryo UI', 10),
            padx=10,
            pady=10
        )

        # フォールバック用の現行テキスト
        _DEFAULT_HELP = (
            "使い方ガイド（デフォルトヘルプテキスト）\n\n"
            "1. 計算領域のSHPファイルを選択\n"
            "2. 流域界のSHPファイルを選択\n"
            "3. 点群CSVファイルを選択\n"
            "4. オプションを設定\n"
            "5. [実行]ボタンをクリック\n\n"
        )

        def _set_help_text():
            body = load_help_text(
                "full_pipline_gui",                # ← ベース名
                config_dir=CONFIG_DIR,             # 明示指定（任意）
                default_text=_DEFAULT_HELP,
            )

            help_text_widget.config(state='normal')
            help_text_widget.delete('1.0', 'end')
            help_text_widget.insert('1.0', body)
            help_text_widget.config(state='disabled')

        _set_help_text()
        help_text_widget.pack(fill='both', expand=True, padx=5, pady=5)

        # （任意）再読込ボタン
        ttk.Button(help_frame, text="ヘルプを再読込", command=_set_help_text).pack(anchor="ne", pady=(5, 0))
        
        # QGIS-LTRのバージョンを入力デフォルトは3.34.9
        ttk.Label(form, text="QGIS-LTRのバージョン", width=lbl_w, anchor="e").grid(row=0, column=0, **paddings)
        self.qgis_version_var = tk.StringVar(value="3.34.9")
        ttk.Entry(form, textvariable=self.qgis_version_var, width=20,).grid(row=0, column=1,sticky="w", **paddings)

        # 計算領域 (.shp) 入力
        ttk.Label(form, text="計算領域 (.shp)", width=lbl_w, anchor="e").grid(row=1, column=0, **paddings)
        self.domain_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.domain_var, width=ent_w, state="readonly").grid(row=1, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_domain).grid(row=1, column=2, **paddings)

        # 流域界 (.shp) 入力
        ttk.Label(form, text="流域界 (.shp)", width=lbl_w, anchor="e").grid(row=2, column=0, **paddings)
        self.basin_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.basin_var, width=ent_w, state="readonly").grid(row=2, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_basin).grid(row=2, column=2, **paddings)

        # 点群CSV（複数可）入力
        ttk.Label(form, text="点群CSV (複数可)", width=lbl_w, anchor="e").grid(row=3, column=0, **paddings)
        self.points_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.points_var, width=ent_w, state="readonly").grid(row=3, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_points).grid(row=3, column=2, **paddings)

        # 標準メッシュ (.shp) 入力 (デフォルト設定済み)
        ttk.Label(form, text="標準メッシュ (.shp)", width=lbl_w, anchor="e").grid(row=4, column=0, **paddings)
        init_std = self.default_stdmesh if self.default_stdmesh else ""
        self.stdmesh_var = tk.StringVar(value=init_std)
        ttk.Entry(form, textvariable=self.stdmesh_var, width=ent_w, state="readonly").grid(row=4, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_stdmesh).grid(row=4, column=2, **paddings)

        # メッシュ分割数（IntVar に変更）  <-- 変更点
        ttk.Label(form, text="メッシュ分割数", width=lbl_w, anchor='e').grid(row=5, column=0, **paddings)
        self.cells_var = tk.IntVar(value=20)  # 文字列から IntVar に変更してキャスト問題を防ぐ
        ttk.Spinbox(form, from_=1, to=1000, textvariable=self.cells_var, width=10).grid(
            row=5, column=1, **paddings, sticky='w')

        # 標高列名
        ttk.Label(form, text="標高列名", width=lbl_w, anchor="e").grid(row=6, column=0, **paddings)
        self.zcol_var = ttk.Combobox(form, width=20, state="readonly")
        self.zcol_var.grid(row=6, column=1, sticky="w", **paddings)
        
        # NoData 値
        ttk.Label(form, text="NoData 値", width=lbl_w, anchor="e").grid(row=7, column=0, **paddings)
        self.nodata_var = tk.DoubleVar(value=-9999)
        ttk.Entry(form, textvariable=self.nodata_var, width=20).grid(row=7, column=1, sticky="w", **paddings)

        # 最小勾配（MINSLOPE）
        ttk.Label(form, text="最小勾配 (MINSLOPE)", width=lbl_w, anchor="e").grid(row=8, column=0, **paddings)
        self.minslope_var = tk.DoubleVar(value=0.1)
        ttk.Entry(form, textvariable=self.minslope_var, width=20).grid(row=8, column=1, sticky="w", **paddings)

        # 閾値（THRESHOLD）
        ttk.Label(form, text="閾値 (THRESHOLD)", width=lbl_w, anchor="e").grid(row=9, column=0, **paddings)
        self.threshold_var = tk.IntVar(value=5)
        ttk.Entry(form, textvariable=self.threshold_var, width=20).grid(row=9, column=1, sticky="w", **paddings)

        # 出力フォルダ
        ttk.Label(form, text="出力フォルダ", width=lbl_w, anchor="e").grid(row=10, column=0, **paddings)
        default_output = str(BASE_DIR / "outputs")
        self.outdir_var = tk.StringVar(value=default_output)
        ttk.Entry(form, textvariable=self.outdir_var, width=ent_w, state="readonly").grid(row=10, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_outdir).grid(row=10, column=2, **paddings)

        # ステータスバー
        self.status_var = tk.StringVar()
        ttk.Label(form, textvariable=self.status_var).grid(row=11, column=1, **paddings2)

        # 実行ボタン（参照できるようにインスタンス化しておく） <-- 変更点: self.run_button を保持
        self.run_button = ttk.Button(form, text="実行", command=self._run, style="Accent.TButton")
        self.run_button.grid(row=11, column=2, **paddings2)

    def _browse_domain(self) -> None:
        """計算領域ファイルを選択"""
        p = filedialog.askopenfilename(filetypes=[("Shapefile", "*.shp")])
        if p:
            self.domain_var.set(p)

    def _browse_basin(self) -> None:
        """流域界ファイルを選択"""
        p = filedialog.askopenfilename(filetypes=[("Shapefile", "*.shp")])
        if p:
            self.basin_var.set(p)

    def _browse_points(self) -> None:
        """点群CSVを複数選択し、標高列を自動検出"""
        paths = filedialog.askopenfilenames(
            filetypes=[("CSV", "*.csv")], 
            title="点群CSVを選択（複数可）"
        )
        if paths:
            self.points_var.set(";".join(paths))
            # 選択されたCSVファイルから標高列を自動検出
            self._update_zcol_list(paths)

    def _update_zcol_list(self, file_paths):
        """指定されたCSVファイルから標高列を検出してComboboxを更新する"""
        if not file_paths:
            return
            
        try:
            # 共通の標高列を取得
            zcols = get_zcol_list(file_paths)
            
            # Comboboxの値を更新
            if zcols:
                self.zcol_var['values'] = zcols
                self.zcol_var.current(0)  # 最初の項目を選択
            else:
                self.zcol_var['values'] = []
                self.zcol_var.set('')
                messagebox.showwarning("警告", "標高列が見つかりませんでした")
            
        except Exception as e:
            self.zcol_var['values'] = []
            self.zcol_var.set('')
            messagebox.showerror("エラー", f"標高列の取得中にエラーが発生しました:\n{str(e)}")

    def _browse_stdmesh(self):
        """標準メッシュファイルを選択する"""
        file_path = filedialog.askopenfilename(
            title="標準メッシュファイルを選択",
            filetypes=[("Shapefile", "*.shp")]
        )
        if file_path:
            self.stdmesh_var.set(file_path)

    def _browse_outdir(self) -> None:
        """出力フォルダを選択し、絶対パスで設定"""
        d = filedialog.askdirectory()
        if d:
            # 絶対パスに正規化して設定
            abs_path = Path(d).resolve()
            self.outdir_var.set(str(abs_path))

    def _run(self) -> None:
        """入力チェックとバックグラウンド実行"""
        # 標準メッシュが空の場合は default_stdmesh を使用
        if not self.stdmesh_var.get() and self.default_stdmesh:
            self.stdmesh_var.set(self.default_stdmesh)
            
        # 必須項目のチェック
        if not all([self.domain_var.get(), self.basin_var.get(), self.points_var.get(), self.stdmesh_var.get()]):
            messagebox.showerror("エラー", "必須項目が入力されていません。")
            return
            
        # 標高列が選択されているかチェック
        selected_zcol = self.zcol_var.get()
        if not selected_zcol:
            messagebox.showerror("エラー", "標高列が選択されていません。CSVを選択して標高列を選択してください。")
            return

        # UI の保護: 実行中は押せないようにする
        self.run_button.config(state="disabled")
        self.status_var.set("実行中…")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        """バックグラウンドワーカー（型キャスト・戻り値チェックを含む）"""
        try:
            # ファイルリスト
            points = [p for p in self.points_var.get().split(";") if p]
            selected_zcol = self.zcol_var.get()

            # 型キャスト
            try:
                num_cells = int(self.cells_var.get())
            except Exception:
                raise ValueError("メッシュ分割数は整数で指定してください。")

            try:
                min_slope = float(self.minslope_var.get())
            except Exception:
                raise ValueError("最小勾配は数値で指定してください。")

            try:
                threshold = int(self.threshold_var.get())
            except Exception:
                raise ValueError("閾値は整数で指定してください。")

            # nodata: 0 を None 扱い（必要に応じて調整）
            nodata_raw = self.nodata_var.get()
            nodata = None if nodata_raw == 0 else nodata_raw

            # QGIS バージョン（空文字は None）
            qgis_version = self.qgis_version_var.get().strip() or None

            # 実行
            result = run_full_pipeline(
                domain_shp=self.domain_var.get(),
                basin_shp=self.basin_var.get(),
                num_cells_x=num_cells,
                num_cells_y=num_cells,  # 片側指定方式のまま
                points_path=points,
                standard_mesh=self.stdmesh_var.get(),
                output_dir=self.outdir_var.get(),
                zcol=selected_zcol,
                nodata=nodata,
                min_slope=min_slope,
                threshold=threshold,
                qgis_version=qgis_version,
                qgis_process_path=None
            )

            # --- 成否のみ判定（簡潔版） ---
            success = True
            error_msg = None

            if isinstance(result, dict):
                success = bool(result.get("success", True))
                if not success:
                    # 失敗時だけ最低限の情報をまとめる（任意）
                    et  = result.get("error_type")
                    st  = result.get("stage")
                    em  = result.get("error") or "処理に失敗しました。"
                    parts = []
                    if et: parts.append(et)
                    if st: parts.append(f"stage={st}")
                    header = " / ".join(parts)
                    error_msg = f"{header}\n{em}" if header else em

            elif isinstance(result, bool):
                success = result

            # 表示
            if success:
                self.queue.put(("info", "処理が完了しました。"))
            else:
                self.queue.put(("error", error_msg or "処理に失敗しました。"))
            # ------------------------------

        except Exception as e:
            self.queue.put(("error", str(e)))
        finally:
            self.queue.put(("enable_run_button", ""))


    def _poll_queue(self) -> None:
        """キューをポーリングしてUI更新"""
        try:
            while True:
                kind, msg = self.queue.get_nowait()
                if kind == "info":
                    messagebox.showinfo("完了", msg)
                    self.status_var.set("完了")
                elif kind == "error":
                    messagebox.showerror("エラー", msg)
                    self.status_var.set("エラー発生")
                elif kind == "enable_run_button":
                    # 常に run_button を再有効化
                    self.run_button.config(state="normal")
                else:
                    # 未知のメッセージはステータスに表示
                    self.status_var.set(msg or "")
                self.queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.after(100, self._poll_queue)


def main() -> None:
    """エントリポイント"""
    root = tk.Tk()
    ttk.Style().theme_use("vista")
    FullPipelineApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
