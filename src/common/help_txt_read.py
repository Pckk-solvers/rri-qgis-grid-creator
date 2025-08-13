# src/common/help_txt_read.py
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional
import sys
import locale


def resolve_base_dir() -> Path:
    """
    アプリのベースディレクトリ（= config がある場所）を解決する。
    - PyInstaller(onefile/onedir)対応
    - 通常実行時はこのファイルから2階層上（src/common -> src -> プロジェクトルート）を基準にする
    """
    if getattr(sys, "frozen", False):
        # PyInstaller
        meipass = getattr(sys, "_MEIPASS", None)
        return Path(meipass) if meipass else Path(sys.executable).parent
    # src/common/help_txt_read.py から 2つ上 = プロジェクトルート想定
    return Path(__file__).resolve().parents[2]


def _preferred_lang(lang: Optional[str] = None) -> str:
    """
    'ja_JP' -> 'ja' のように 2文字言語コードへ。
    """
    if lang:
        return lang.split("_")[0]
    loc = locale.getdefaultlocale()[0] or "ja"
    return str(loc).split("_")[0]


def _candidate_paths(
    name: str,
    lang: str,
    config_dir: Path,
) -> Iterable[Path]:
    """
    読み込み候補ファイルの優先順を生成する。
    .txt / .md の両方をサポート（表示はテキストのまま）
    """
    help_dir = config_dir / "help"
    stems = [
        f"{name}_{lang}",
        f"{name}",
        f"help_{lang}",
        "help",
    ]
    for stem in stems:
        yield help_dir / f"{stem}.txt"
        yield help_dir / f"{stem}.md"


def load_help_text(
    name: str,
    *,
    lang: Optional[str] = None,
    base_dir: Optional[Path] = None,
    config_dir: Optional[Path] = None,
    default_text: str = "ヘルプが見つかりませんでした。",
    normalize_newlines: bool = True,
) -> str:
    """
    config/help 配下からヘルプテキストを読み込む。

    優先順:
      <name>_<lang>.txt → <name>_<lang>.md →
      <name>.txt → <name>.md →
      help_<lang>.txt → help_<lang>.md →
      help.txt → help.md → default_text

    Args:
        name: GUI/機能ごとのベース名（例: 'full_pipline_gui'）
        lang: 'ja' / 'en' など。未指定なら OS ロケールから推定
        base_dir: config があるベースディレクトリ
        config_dir: 明示的に config ディレクトリを渡す場合に使用（base_dir より優先）
        default_text: 見つからない場合のフォールバック文字列
        normalize_newlines: 改行を '\n' に正規化するか

    Returns:
        str: 読み取った（またはフォールバック）テキスト
    """
    lang = _preferred_lang(lang)
    if config_dir is None:
        b = base_dir or resolve_base_dir()
        config_dir = b / "config"

    for p in _candidate_paths(name, lang, config_dir):
        try:
            text = p.read_text(encoding="utf-8-sig")
            if normalize_newlines:
                text = text.replace("\r\n", "\n").replace("\r", "\n")
            return text
        except FileNotFoundError:
            continue

    return default_text


def apply_tokens(text: str, tokens: dict[str, object] | None = None) -> str:
    """
    ヘルプ内の {TOKEN} を差し替える簡易テンプレート。
    例: apply_tokens("NODATA={NODATA_DEFAULT}", {"NODATA_DEFAULT": -9999})
    """
    if not tokens:
        return text
    for k, v in tokens.items():
        text = text.replace("{" + k + "}", str(v))
    return text
