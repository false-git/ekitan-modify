#! env python3

import sys


def read_ekitan(filename):
    """
    駅探の検索結果のテキストをちょっと整形する
    """
    with open(filename, "r") as f:
        for line in f:
            print(line.strip())


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Usage: {} inputfile".format(args[0]))
        exit(1)
    read_ekitan(args[1])
