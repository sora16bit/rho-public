"""Rho CLI。`rho analyze <file>` または `rho analyze -`(標準入力)。"""
import sys
import argparse
import rho

def main(argv=None):
    parser = argparse.ArgumentParser(prog="rho", description="文章解析エンジン Rho")
    sub = parser.add_subparsers(dest="cmd")
    pa = sub.add_parser("analyze", help="ファイル/標準入力を解析してレポート表示")
    pa.add_argument("file", help="解析するテキストファイル。'-' で標準入力")
    pa.add_argument("--raw", action="store_true", help="生数値表で出す(既定は語り直し)")
    args = parser.parse_args(argv)

    if args.cmd == "analyze":
        if args.file == "-":
            text = sys.stdin.read()
            doc = rho.analyze(text)
        else:
            doc = rho.load(args.file)
        print(doc.report(mode="raw" if args.raw else "narrate"))
        return 0
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
