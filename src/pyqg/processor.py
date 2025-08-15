#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import os
from typing import Dict, Optional
from contextlib import contextmanager

# ── デフォルト値 ─────────────────────────────────────────────
MIN_SLOPE = 0.1
THRESHOLD = 5
DEFAULT_QGIS_VERSION = "3.34.9"   # ← ここを明示（以前は未定義参照の可能性あり）

# ── qgis_process の解決 ─────────────────────────────────────
def resolve_qgis_process(
    qgis_process_path: Optional[str] = None,
    qgis_version: Optional[str] = None
) -> str:
    """
    優先順:
      1) 引数 qgis_process_path（存在必須）
      2) 環境変数 QGIS_PROCESS_PATH（存在必須）
      3) qgis_version から Windows 既定パスを組み立て（存在必須）
    """
    if qgis_process_path:
        p = Path(qgis_process_path)
        if p.exists():
            return str(p)
        raise FileNotFoundError(f"指定された qgis_process が見つかりません: {qgis_process_path}")

    env_p = os.getenv("QGIS_PROCESS_PATH")
    if env_p:
        p = Path(env_p)
        if p.exists():
            return str(p)
        raise FileNotFoundError(f"環境変数 QGIS_PROCESS_PATH のパスが見つかりません: {env_p}")

    qv = qgis_version or DEFAULT_QGIS_VERSION
    default_path = Path(rf"C:\Program Files\QGIS {qv}\bin\qgis_process-qgis-ltr.bat")
    if default_path.exists():
        return str(default_path)

    raise FileNotFoundError(
        "qgis_process 実行ファイルが見つかりませんでした。"
        " --qgis-process-path または --qgis-version を指定するか、"
        "環境変数 QGIS_PROCESS_PATH を設定してください。"
    )

# ── qgis_process 実行（★空stdout検出を追加）──────────────────
def run_qgis(alg_id: str, params: dict, qgis_process_path: str) -> str:
    """
    qgis_process を実行（--json）。戻りコード≠0 ならエラー。
    ★ 追記: 標準出力が空 or 空白のみならエラーとして停止。
    """
    cmd = [qgis_process_path, "run", alg_id, "--json"]
    for k, v in params.items():
        if isinstance(v, bool):
            v_str = "true" if v else "false"
        else:
            v_str = str(v)
        cmd.append(f"{k}={v_str}")
    print(">>>", " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # qgis_process の stderr を詳細に出す
        raise RuntimeError(f"qgis_process failed (rc={result.returncode}):\n{result.stderr.strip()}")

    out = (result.stdout or "").strip()
    if not out:
        # ★ ここが今回の要点: “無出力”を異常として扱う
        raise RuntimeError(f"qgis_process returned no output for {alg_id}\nCommand: {' '.join(cmd)}")

    return out

# ── 生成物の存在チェック（★新規）────────────────────────────
def _must_exist(path: str | Path, label: str):
    """
    生成物の存在と非ゼロサイズを確認。満たさなければ例外。
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{label} が生成されませんでした: {p}")
    if p.is_file() and p.stat().st_size == 0:
        raise FileNotFoundError(f"{label} が空ファイルとして生成されました: {p}")

# ── 一時 SDAT 管理 ───────────────────────────────────────────
@contextmanager
def temp_sdat_files(*filenames: str) -> Dict[str, str]:
    """一時的なSDATファイルを作成し、処理後に削除するコンテキストマネージャー"""
    temp_dir = tempfile.mkdtemp()
    temp_files = {}
    try:
        for filename in filenames:
            base_name = Path(filename).stem
            temp_files[base_name] = str(Path(temp_dir) / f"{base_name}.sdat")
        yield temp_files
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# ── メイン処理 ───────────────────────────────────────────────
def process_dem(
    input_path: str | Path,
    output_dir: str | Path,
    min_slope: float = MIN_SLOPE,
    threshold: int = THRESHOLD,
    keep_temp_files: bool = False,
    *,
    qgis_version: Optional[str] = None,
    qgis_process_path: Optional[str] = None
) -> dict:
    """
    DEMデータを処理（窪地 → 流向 → ASC 変換）。
    重要: qgis_process の“無出力”や成果物未生成を検知して停止。
    """
    try:
        qgis_exec = resolve_qgis_process(
            qgis_process_path=qgis_process_path, qgis_version=qgis_version
        )
    except Exception as e:
        return {'success': False, 'error': str(e), 'error_type': type(e).__name__}

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = {
        'filled_asc': output_dir / 'filled.asc',
        'direction_asc': output_dir / 'direction.asc'
    }

    temp_sdat_files_map = {
        'filled': 'filled.sdat',
        'direction': 'direction.sdat',
        'segments': 'segments.sdat',
        'basins': 'basins.sdat'
    }

    try:
        with temp_sdat_files(*temp_sdat_files_map.values()) as temp_files:
            # 1) 窪地処理
            print("\n[1/4] 窪地処理を開始しています...")
            print(f"  入力ファイル: {input_path}")
            print(f"  一時ファイル: {temp_files['filled']}" if not keep_temp_files else f"  出力先: {temp_files['filled']}")
            print(f"  最小勾配: {min_slope}")

            run_qgis(
                "sagang:fillsinksxxlwangliu",
                {
                    "ELEV": str(input_path),
                    "FILLED": temp_files['filled'],
                    "MINSLOPE": min_slope
                },
                qgis_exec
            )
            # ★ 成果物の存在チェック
            _must_exist(temp_files['filled'], "窪地処理の出力 (filled.sdat)")
            print("  ✅ 窪地処理が完了しました")

            # 2) 流向・流域解析
            print("\n[2/4] 流向・流域解析を開始しています...")
            print(f"  閾値: {threshold}")
            print(f"  流向データ一時ファイル: {temp_files['direction']}" if not keep_temp_files else f"  流向データ出力先: {temp_files['direction']}")

            run_qgis(
                "sagang:channelnetworkanddrainagebasins",
                {
                    "DEM": temp_files['filled'],
                    "DIRECTION": temp_files['direction'],
                    "SEGMENTS": temp_files['segments'],
                    "BASINS": temp_files['basins'],
                    "THRESHOLD": threshold,
                    "SUBBASINS": True
                },
                qgis_exec
            )
            # ★ DIRECTION だけは必須なので確実にチェック（SEGMENTS/BASINS は用途に応じて）
            _must_exist(temp_files['direction'], "流向の出力 (direction.sdat)")
            print("  ✅ 流向・流域解析が完了しました")

            # 3) ラスタ変換 (filled.sdat → filled.asc)
            print("\n[3/4] ラスタ変換を実行しています (filled.sdat → filled.asc)...")
            run_qgis(
                "gdal:translate",
                {
                    "INPUT": temp_files['filled'],
                    "OUTPUT": str(output_files['filled_asc'])
                },
                qgis_exec
            )
            # ★ 生成 ASC の存在チェック
            _must_exist(output_files['filled_asc'], "ラスタ変換の出力 (filled.asc)")
            print("  ✅ ラスタ変換が完了しました (filled)")

            # 4) ラスタ変換 (direction.sdat → direction.asc)
            print("\n[4/4] ラスタ変換を実行しています (direction.sdat → direction.asc)...")
            run_qgis(
                "gdal:translate",
                {
                    "INPUT": temp_files['direction'],
                    "OUTPUT": str(output_files['direction_asc'])
                },
                qgis_exec
            )
            _must_exist(output_files['direction_asc'], "ラスタ変換の出力 (direction.asc)")
            print("  ✅ ラスタ変換が完了しました (direction)")

            # 必要なら一時ファイルを保持
            if keep_temp_files:
                for key, temp_path in temp_files.items():
                    if Path(temp_path).exists():
                        dest_path = output_dir / f"{key}.sdat"
                        shutil.copy2(temp_path, dest_path)
                        output_files[f"{key}_sdat"] = dest_path
                        print(f"  ✅ 一時ファイルを保持: {dest_path}")

        print("\n=======================================")
        print("✅ すべての処理が正常に完了しました！")
        print("=======================================")
        print("\n【出力ファイル一覧】")
        for name, path in output_files.items():
            print(f"- {name}: {path}")
        print(f"\n出力先ディレクトリ: {output_dir.absolute()}")

        return {
            'success': True,
            'output_files': {k: str(v) for k, v in output_files.items()}
        }

    except Exception as e:
        print("\n❌ エラーが発生しました")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラーメッセージ: {str(e)}")
        print("\n処理を中断します。")
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
