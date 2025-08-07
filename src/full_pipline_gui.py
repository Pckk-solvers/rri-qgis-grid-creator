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
from tkinter import ttk, filedialog, messagebox

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


# run_full_pipeline モジュール読み込み
sys.path.append(str(BASE_DIR))
try:
    from run_full_pipeline import run_full_pipeline
except ImportError as e:
    message = (
        "run_full_pipeline モジュールが見つかりませんでした。\n"
        "full_pipeline_gui.py と同じ階層、または PYTHONPATH に追加してください。"
    )
    raise SystemExit(message) from e


class FullPipelineApp(ttk.Frame):
    """メインアプリケーションフレーム"""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        master.title("フルパイプライン実行 GUI")
        master.geometry("920x480")
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
        lbl_w = 18
        ent_w = 70

        form = ttk.Frame(self)
        form.pack(side="top", fill="x", expand=False)

        # 計算領域 (.shp) 入力
        ttk.Label(form, text="計算領域 (.shp)", width=lbl_w, anchor="e").grid(row=0, column=0, **paddings)
        self.domain_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.domain_var, width=ent_w, state="readonly").grid(row=0, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_domain).grid(row=0, column=2, **paddings)

        # 流域界 (.shp) 入力
        ttk.Label(form, text="流域界 (.shp)", width=lbl_w, anchor="e").grid(row=1, column=0, **paddings)
        self.basin_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.basin_var, width=ent_w, state="readonly").grid(row=1, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_basin).grid(row=1, column=2, **paddings)

        # 点群CSV（複数可）入力
        ttk.Label(form, text="点群CSV（複数可）", width=lbl_w, anchor="e").grid(row=2, column=0, **paddings)
        self.points_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.points_var, width=ent_w, state="readonly").grid(row=2, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_points).grid(row=2, column=2, **paddings)

        # 標準メッシュ (.shp) 入力 (デフォルト設定済み)
        ttk.Label(form, text="標準メッシュ (.shp)", width=lbl_w, anchor="e").grid(row=3, column=0, **paddings)
        init_std = self.default_stdmesh if self.default_stdmesh else ""
        self.stdmesh_var = tk.StringVar(value=init_std)
        ttk.Entry(form, textvariable=self.stdmesh_var, width=ent_w, state="readonly").grid(row=3, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_stdmesh).grid(row=3, column=2, **paddings)

        # セル数（X=Y）
        ttk.Label(form, text="セル数", width=lbl_w, anchor="e").grid(row=4, column=0, **paddings)
        self.cells_var = tk.IntVar(value=100)
        ttk.Entry(form, textvariable=self.cells_var, width=20).grid(row=4, column=1, sticky="w", **paddings)

        # 標高列名（任意）
        ttk.Label(form, text="標高列名（任意）", width=lbl_w, anchor="e").grid(row=5, column=0, **paddings)
        self.zcol_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.zcol_var, width=20).grid(row=5, column=1, sticky="w", **paddings)

        # NoData 値（任意）
        ttk.Label(form, text="NoData 値（任意）", width=lbl_w, anchor="e").grid(row=6, column=0, **paddings)
        self.nodata_var = tk.DoubleVar(value=-9999)
        ttk.Entry(form, textvariable=self.nodata_var, width=20).grid(row=6, column=1, sticky="w", **paddings)

        # 最小勾配（pyqg）
        ttk.Label(form, text="最小勾配（pyqg）", width=lbl_w, anchor="e").grid(row=7, column=0, **paddings)
        self.minslope_var = tk.DoubleVar(value=0.1)
        ttk.Entry(form, textvariable=self.minslope_var, width=20).grid(row=7, column=1, sticky="w", **paddings)

        # 閾値（pyqg）
        ttk.Label(form, text="閾値（pyqg）", width=lbl_w, anchor="e").grid(row=8, column=0, **paddings)
        self.threshold_var = tk.IntVar(value=5)
        ttk.Entry(form, textvariable=self.threshold_var, width=20).grid(row=8, column=1, sticky="w", **paddings)

        # 出力フォルダ
        ttk.Label(form, text="出力フォルダ", width=lbl_w, anchor="e").grid(row=9, column=0, **paddings)
        self.outdir_var = tk.StringVar(value="outputs")
        ttk.Entry(form, textvariable=self.outdir_var, width=ent_w, state="readonly").grid(row=9, column=1, **paddings)
        ttk.Button(form, text="参照", command=self._browse_outdir).grid(row=9, column=2, **paddings)

        # ステータスバー
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(side="bottom", fill="x", pady=(8, 0))

        # 実行ボタン
        ttk.Button(self, text="実行", command=self._run, style="Accent.TButton").pack(side="bottom", pady=8)

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
        """点群CSVを複数選択"""
        paths = filedialog.askopenfilenames(filetypes=[("CSV", "*.csv")], title="点群CSVを選択（複数可）")
        if paths:
            self.points_var.set(";".join(paths))

    def _browse_stdmesh(self) -> None:
        """標準メッシュファイルを選択"""
        p = filedialog.askopenfilename(filetypes=[("Shapefile", "*.shp")])
        if p:
            self.stdmesh_var.set(p)

    def _browse_outdir(self) -> None:
        """出力フォルダを選択"""
        d = filedialog.askdirectory()
        if d:
            self.outdir_var.set(d)

    def _run(self) -> None:
        """入力チェックとバックグラウンド実行"""
        # 標準メッシュが空の場合は default_stdmesh を使用
        if not self.stdmesh_var.get() and self.default_stdmesh:
            self.stdmesh_var.set(self.default_stdmesh)
        if not all([self.domain_var.get(), self.basin_var.get(), self.points_var.get(), self.stdmesh_var.get()]):
            messagebox.showerror("エラー", "必須項目が入力されていません。")
            return

        self.status_var.set("実行中…")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        """バックグラウンドワーカー"""
        try:
            points = self.points_var.get().split(";")
            run_full_pipeline(
                domain_shp=self.domain_var.get(),
                basin_shp=self.basin_var.get(),
                num_cells_x=self.cells_var.get(),
                num_cells_y=self.cells_var.get(),
                points_path=points,
                standard_mesh=self.stdmesh_var.get(),
                output_dir=self.outdir_var.get(),
                zcol=(self.zcol_var.get() or None),
                nodata=(None if self.nodata_var.get() == 0 else self.nodata_var.get()),
                min_slope=self.minslope_var.get(),
                threshold=self.threshold_var.get(),
            )
            self.queue.put(("info", "処理が完了しました！"))
        except Exception as e:
            self.queue.put(("error", str(e)))

    def _poll_queue(self) -> None:
        """キューをポーリングしてUI更新"""
        try:
            kind, msg = self.queue.get_nowait()
            if kind == "info":
                messagebox.showinfo("完了", msg)
                self.status_var.set("完了")
            else:
                messagebox.showerror("エラー", msg)
                self.status_var.set("エラー発生")
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
