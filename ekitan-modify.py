#! env python3

import sys
import re
import datetime


class EkitanLog:
    """
    駅探の経路探索結果のテキストをごにょごにょする
    """

    def __init__(self):
        self.reserve_lines = []
        self.prev_index = None
        self.prev_time = None
        self.start_regex = re.compile(r"(\d\d:\d\d)発")
        self.end_regex = re.compile(r"(\d\d:\d\d)着")
        self.plan_regex = re.compile(r"^Plan ([^ ]+)$")
        self.plan_name = None
        self.plans = set()
        self.plan_prev_index = None
        self.plan_prev_time = None
        self.plan_ends = {}
        self.outlines = []

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
        mm = ts // 60 % 60
        hh = ts // 3600
        if hh == 0:
            return "{}分".format(mm)
        return "{}:{:02}分".format(hh, mm)

    def output_time(self, current_time):
        """
        所要時間を出力する

        Parameters
        ----------
        current_time : datetime
            現在の時間
        """
        if self.prev_index is None:
            return
        if self.plan_name is not None:
            if self.plan_name in self.plans:
                delta = current_time - self.plan_prev_time
                self.outlines[self.plan_prev_index] += " Plan {}: {}".format(
                    self.plan_name, self.timedelta2string(delta)
                )
                self.plans.remove(self.plan_name)
                return
        elif len(self.plan_ends) > 0:
            for plan, d in self.plan_ends.items():
                delta = current_time - d[1]
                self.outlines[d[0]] += " {}".format(self.timedelta2string(delta))
            self.plan_ends = {}
        delta = current_time - self.prev_time
        self.outlines[self.prev_index] += " {}".format(self.timedelta2string(delta))

    def read_ekitan(self, filename):
        """
        駅探の検索結果のテキストをちょっと整形する
        """
        with open(filename, "r") as f:
            headline = None
            for line in f:
                line = line.rstrip()
                if line.startswith("往復："):
                    continue
                if line.startswith("※大人"):
                    continue
                if line.find(" → ") > 0:
                    headline = line
                    continue
                if headline is not None:
                    line = line + "\t" + headline
                    headline = None
                # plan
                m = self.plan_regex.search(line)
                if m is not None:
                    plan = m.group(1)
                    if self.plan_name is None:
                        self.plan_prev_index = self.prev_index
                        self.plan_prev_time = self.prev_time
                    elif self.prev_index is not None:
                        self.plan_ends[self.plan_name] = (
                            self.prev_index,
                            self.prev_time,
                        )
                    if plan == "End":
                        self.plan_name = None
                        self.plans = set()
                    else:
                        self.plan_name = plan
                        self.plans.add(plan)

                # start
                m = self.start_regex.search(line)
                if m is not None:
                    current_time = datetime.datetime.strptime(m.group(1), "%H:%M")
                    self.output_time(current_time)
                    self.prev_index = len(self.outlines)
                    self.prev_time = current_time

                # end
                m = self.end_regex.search(line)
                if m is not None:
                    current_time = datetime.datetime.strptime(m.group(1), "%H:%M")
                    self.output_time(current_time)
                    self.prev_index = len(self.outlines) + 1
                    self.prev_time = current_time

                self.outlines.append(line)
        for line in self.outlines:
            print(line)


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Usage: {} inputfile".format(args[0]))
        exit(1)
    el = EkitanLog()
    el.read_ekitan(args[1])
