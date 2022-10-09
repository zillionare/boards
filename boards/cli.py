"""Console script for boards."""

import json
import logging
import os
import signal
import subprocess
import sys
import time

import fire
import httpx

from boards.board import ConceptBoard, IndustryBoard, sync_board

logger = logging.getLogger(__name__)


def _save_proc_info(port, proc):
    path = os.path.dirname(__file__)
    file = os.path.join(path, "config")
    with open(file, "w") as f:
        f.writelines(json.dumps({"port": port, "proc": proc}))


def _read_proc_info():
    path = os.path.dirname(__file__)
    file = os.path.join(path, "config")
    try:
        with open(file, "r") as f:
            info = json.load(f)
            return info
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)

    return None


def is_service_alive(port: int = None) -> bool:
    if port is None:
        info = _read_proc_info()
        if info is None:
            raise ValueError("请指定端口")

        port = info["port"]

    try:
        resp = httpx.get(f"http://localhost:{port}/", trust_env=False)
    except httpx.NetworkError:
        return False

    return resp.status_code == 200


def status(port: int = None) -> bool:
    if is_service_alive(port):
        print("------ board服务正在运行 ------")
    else:
        print("------ board服务未运行 ------")

    ib = IndustryBoard()
    cb = ConceptBoard()
    ib.init()
    cb.init()

    try:
        info = ib.info()
        print(f"行业板块已更新至: {info['last_sync_date']},共{len(info['history'])}天数据。")
    except KeyError:
        print("行业板块数据还从未同步过。")

    try:
        info = cb.info()
        print(f"概念板块已更新至: {info['last_sync_date']},共{len(info['history'])}天数据。")
    except KeyError:
        print("概念板块数据还从未同步过。")


def stop():
    info = _read_proc_info()
    if info is None:
        print("未发现正在运行的boards服务")
        return

    proc = info["proc"]
    try:
        os.kill(proc, signal.SIGKILL)
    except ProcessLookupError:
        sys.exit()
    if not is_service_alive():
        print("boards已停止运行")
    else:
        print("停止boards服务失败，请手工停止。")


def serve(port: int = 2308):
    if is_service_alive(port):
        print("boards正在运行中，忽略此命令。")
        return

    proc = subprocess.Popen([sys.executable, "-m", "boards", "serve", f"{port}"])

    for _ in range(30):
        if is_service_alive(port):
            _save_proc_info(port=port, proc=proc.pid)
            break
        else:
            time.sleep(1)


def new_boards(days: int = 10):
    cb = ConceptBoard()
    cb.init()
    result = cb.find_new_concept_boards(days)
    if result is None or len(result) == 0:
        print(f"近{days}天内没有新的概念板块")
    else:
        print(result)


def new_members(days: int = 10, prot: int = None):
    cb = ConceptBoard()
    cb.init()
    try:
        results = cb.new_members_in_board(days)
        if len(results) == 0:
            print(f"近{days}天内没有板块有新增成员")
        else:
            for board, stocks in results.items():
                print(cb.get_name(board) + ":")
                aliases = [cb.get_stock_alias(stock) for stock in stocks]
                print(" ".join(aliases))
    except Exception as e:
        print(e)


def sync():
    sync_board()


def main():
    fire.Fire(
        {
            "new_members": new_members,
            "new_boards": new_boards,
            "serve": serve,
            "status": status,
            "sync": sync,
            "stop": stop,
        }
    )


if __name__ == "__main__":
    main()
