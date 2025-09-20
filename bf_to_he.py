#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path


def bf_to_he(src: str, mapping: dict) -> str:
    """
    Brainfuck コードを mapping.json の対応に基づいてへ/ヘ列に変換する
    出力はスペース・改行なしでひたすら連結する
    """
    out = []
    for c in src:
        if c in mapping:
            out.append(mapping[c])
        else:
            # コメントとか無視
            continue
    return "".join(out)


def main(argv):
    if len(argv) < 3:
        print("使い方: python3 bf_to_he.py mapping.json input.bf [output.he]")
        return 1

    mapping_file = Path(argv[1])
    input_file = Path(argv[2])
    output_file = Path(argv[3]) if len(argv) > 3 else None

    # マッピングを JSON からロード
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)
    except Exception as e:
        print(f"マッピングファイルの読み込み失敗: {e}", file=sys.stderr)
        return 2

    # Brainfuck ソース読み込み
    try:
        src = input_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"入力ファイルの読み込み失敗: {e}", file=sys.stderr)
        return 3

    # 変換
    converted = bf_to_he(src, mapping)

    # 出力
    if output_file:
        output_file.write_text(converted, encoding="utf-8")
    else:
        # 標準出力に垂れ流す
        sys.stdout.write(converted)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
