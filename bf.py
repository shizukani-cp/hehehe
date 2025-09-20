#!/usr/bin/env python3
"""
Simple Brainfuck interpreter in Python.

使い方:
    # 1) モジュールとして
    from bf import Brainfuck
    bf = Brainfuck(code, input_stream="Hello")
    output = bf.run()  # 実行して出力文字列を返す

    # 2) CLI としてファイル実行
    $ python3 bf.py program.bf [optional_input_string]

仕様:
 - メモリは必要に応じて右に拡張（左は0番地から動かさない）
 - 各セルは 0..255 を繰り返す（byte ラップ）
 - 無効な文字は無視
 - 入力が尽きたら EOF -> 0 を返す
"""
from typing import Dict, List, Optional


class Brainfuck:
    def __init__(self, code: str, input_stream: Optional[str] = None, tape_size: int = 30000):
        self.raw_code = code
        self.code = self._clean_code(code)
        self.input_stream = list(input_stream or "")
        self.input_pos = 0
        self.tape: List[int] = [0] * tape_size
        self.dp = 0  # data pointer
        self.ip = 0  # instruction pointer
        self.output_chars: List[str] = []
        self.bracket_map = self._build_bracket_map(self.code)

    @staticmethod
    def _clean_code(code: str) -> str:
        # Brainfuck のコマンドだけ残す
        return "".join(c for c in code if c in "<>+-.,[]")

    @staticmethod
    def _build_bracket_map(code: str) -> Dict[int, int]:
        stack: List[int] = []
        match: Dict[int, int] = {}
        for i, c in enumerate(code):
            if c == "[":
                stack.append(i)
            elif c == "]":
                if not stack:
                    raise SyntaxError(f"Unmatched ']' at position {i}")
                j = stack.pop()
                match[i] = j
                match[j] = i
        if stack:
            raise SyntaxError(f"Unmatched '[' at position {stack[-1]}")
        return match

    def _read_input_byte(self) -> int:
        if self.input_pos < len(self.input_stream):
            ch = self.input_stream[self.input_pos]
            self.input_pos += 1
            return ord(ch) % 256
        else:
            # EOF -> 0
            return 0

    def run(self, max_steps: Optional[int] = None) -> str:
        steps = 0
        code = self.code
        L = len(code)
        tape = self.tape

        while self.ip < L:
            if max_steps is not None and steps >= max_steps:
                break
            cmd = code[self.ip]

            if cmd == ">":
                self.dp += 1
                if self.dp >= len(tape):
                    tape.append(0)  # 右に拡張
            elif cmd == "<":
                if self.dp == 0:
                    # 左端では0に留める（古い実装との互換性のため）
                    # 必要ならここで例外にすることもできる
                    pass
                else:
                    self.dp -= 1
            elif cmd == "+":
                tape[self.dp] = (tape[self.dp] + 1) % 256
            elif cmd == "-":
                tape[self.dp] = (tape[self.dp] - 1) % 256
            elif cmd == ".":
                self.output_chars.append(chr(tape[self.dp]))
            elif cmd == ",":
                tape[self.dp] = self._read_input_byte()
            elif cmd == "[":
                if tape[self.dp] == 0:
                    # jump forward to matching ]
                    self.ip = self.bracket_map[self.ip]
            elif cmd == "]":
                if tape[self.dp] != 0:
                    # jump back to matching [
                    self.ip = self.bracket_map[self.ip]
            # advance
            self.ip += 1
            steps += 1

        return "".join(self.output_chars)


# --- CLI サポート ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 bf.py <file.bf> [input_string]")
        sys.exit(1)

    path = sys.argv[1]
    input_str = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Failed to read {path}: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        bf = Brainfuck(code, input_stream=input_str)
        out = bf.run()
        # 出力はバイナリ的な値もあり得るけど、通常はテキストやね
        sys.stdout.write(out)
    except SyntaxError as e:
        print(f"Syntax error in Brainfuck code: {e}", file=sys.stderr)
        sys.exit(3)
