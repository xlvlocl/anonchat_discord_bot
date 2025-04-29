from datetime import datetime as dt
import sys


class Logger:
    def __init__(
            self,
            level=5,
            message="[{time}] {color}{tag}{c} : {text}",
            time="%H:%M:%S",
            ):
        self.time = time
        self.message = message
        self.colors = {
            "red": "\033[91m",
            "yellow": "\033[93m",
            "red_bg": "\033[41m",
            "green": "\033[32m",
            "blue": "\033[34m",
            }
        self.critical = lambda msg: level > 0 and self.send(
            "CRITICAL", msg, "red_bg", True
            )
        self.error = lambda msg: level > 1 and self.send("|ERROR|", msg, "red", True)
        self.warning = lambda msg: level > 2 and self.send("|WARNING|", msg, "yellow")
        self.info = lambda msg: level > 3 and self.send("|INFO|", msg, "green")
        self.debug = lambda msg: level > 4 and self.send("|DEBUG|", msg, "blue")
        self.crirical = lambda msg: level > 5 and self.send("|CRITICAL|", msg, "red_bg")

    def send(self, tag, text, color, err=False):
        ts = dt.now()
        time = ts.strftime(self.time)
        formatmap = {
            "time": time,
            "tag": tag,
            "text": text,
            "color": self.colors[color],
            "c": "\033[0m",
            }
        s = sys.stderr if err else sys.stdout
        s.write(self.message.format(**formatmap) + "\n")


if __name__ == "__main__":
    logger = Logger()
    logger.info("Это информационное сообщение")
    logger.error("Это сообщение ошибки")
    logger.warning("Это сообщение предупреждения")
    logger.debug("Это сообщение дебагга")
    logger.critical("Это критическое сообщение")
