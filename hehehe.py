#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path
from bf import Brainfuck  # 前に作ったインタプリタ


def load_mapping(mapping_file: Path) -> dict:
    with open(mapping_file, "r", encoding="utf-8") as f:
        return json.load(f)


def invert_mapping(mapping: dict) -> dict:
    """
    JSON の { '>' : 'へへへ', ... } を逆引き用 { 'へへへ': '>' } に変換
    """
    return {v: k for k, v in mapping.items()}


def convert_he_to_bf(src: str, inv_map: dict) -> str:
    """
    へ/ヘ羅列を3文字ずつ切り出して Brainfuck コードに変換
    """
    text = "".join(c for c in src if c in ("へ", "ヘ"))
    if len(text) % 3 != 0:
        raise ValueError("入力が3文字単位で揃ってへんわ")
    bf_code = []
    for i in range(0, len(text), 3):
        token = text[i:i+3]
        if token not in inv_map:
            raise ValueError(f"未知のトークン: {token}")
        bf_code.append(inv_map[token])
    return "".join(bf_code)


def run_file(mapping_file: Path, src_file: Path, input_str: str = "") -> str:
    mapping = load_mapping(mapping_file)
    inv_map = invert_mapping(mapping)
    src = src_file.read_text(encoding="utf-8")
    bf_code = convert_he_to_bf(src, inv_map)
    bf = Brainfuck(bf_code, input_stream=input_str)
    return bf.run()


def main(argv):
    if len(argv) < 3:
        print("使い方: python3 he_bf.py mapping.json program.he [input_string]")
        return 1

    mapping_file = Path(argv[1])
    src_file = Path(argv[2])
    input_str = argv[3] if len(argv) > 3 else ""

    try:
        out = run_file(mapping_file, src_file, input_str=input_str)
        sys.stdout.write(out)
    except Exception as e:
        print(f"実行エラー: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
