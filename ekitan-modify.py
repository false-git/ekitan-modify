#! env python3

import sys
import re
import datetime


class EkitanLog:
    """
    駅探の経路探索結果のテキストをごにょごにょする
    """

    STATE_NONE = 0
    STATE_START = 1
    STATE_END = 2

    def __init__(self):
        self.reserve_lines = []
        self.start_time = None
        self.end_time = None
        self.start_regex = re.compile(r"(\d\d:\d\d)発")
        self.end_regex = re.compile(r"(\d\d:\d\d)着")

    def timedelta2string(self, delta):
        """
        timedeltaを可読な文字列に変換する

        Parameters
        ----------
        delta : timedelta
            変換する時間差

        Returns
        -------
        text : str
            可読な文字列
        """
        ts = int(delta.total_seconds())
        mm = ts // 60
        hh = ts // 3600
        if hh == 0:
            return "{}分".format(mm)
        return "{}:{:02}分".format(hh, mm)

    def output_reserve_lines(self, delta):
        """
        保存していた行を出力する

        Parameters
        ----------
        delta : timedelta
            保存していた間の時間差
        """
        if len(self.reserve_lines) == 0:
            return
        if delta is not None:
            first_line = self.reserve_lines.pop(0)
            print("{}\t({})".format(first_line, self.timedelta2string(delta)))
        for line in self.reserve_lines:
            print(line)
        self.reserve_lines = []

    def read_ekitan(self, filename):
        """
        駅探の検索結果のテキストをちょっと整形する
        """
        with open(filename, "r") as f:
            self.state = EkitanLog.STATE_NONE
            headline = None
            for line in f:
                line = line.strip()
                if line.startswith("往復："):
                    continue
                if line.startswith("※大人"):
                    continue
                if line.find(" → ") > 0:
                    headline = line
                    continue
                if headline is not None:
                    line = headline + "\t" + line
                    headline = None
                m = self.start_regex.search(line)
                if m is not None:
                    self.start_time = datetime.datetime.strptime(m.group(1), "%H:%M")
                    if self.state == EkitanLog.STATE_END:
                        self.output_reserve_lines(self.start_time - self.end_time)
                    self.state = EkitanLog.STATE_START
                m = self.end_regex.search(line)
                if m is not None:
                    self.end_time = datetime.datetime.strptime(m.group(1), "%H:%M")
                    if self.state == EkitanLog.STATE_START:
                        self.output_reserve_lines(self.end_time - self.start_time)
                    self.state = EkitanLog.STATE_END
                if self.state == EkitanLog.STATE_NONE:
                    print(line)
                else:
                    self.reserve_lines.append(line)
            self.output_reserve_lines(None)


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Usage: {} inputfile".format(args[0]))
        exit(1)
    el = EkitanLog()
    el.read_ekitan(args[1])
