"""Console script for boards."""

import json
import os
import subprocess
import sys
import time

import fire
import httpx

from boards.board import ConceptBoard


def _save_proc_info(port, proc):
    path = os.path.dirname(__file__)
    file = os.path.join(path, "config")
    with open(file, "w") as f:
        f.writelines(json.dumps({"port": port, "proc": proc}))


def _read_proc_info():
    path = os.path.dirname(__file__)
    file = os.path.join(path, "config")
    with open(file, "r") as f:
        info = json.load(f)
        return info


def status(port: int = None) -> bool:
    if port is None:
        info = _read_proc_info()
        if info is None:
            print("请指定服务器端口")
            return

        port = info["port"]

    try:
        resp = httpx.get(f"http://localhost:{port}/")
        if resp.status_code == 200:
            print("board服务正在运行")
            return True
        else:
            print("board服务已经运行，但无法访问", resp.status_code)
    except Exception as e:
        print("board服务没有正常运行，错误码", e)

    return False


def serve(port: int = 2308):
    if status(port):
        return

    proc = subprocess.Popen([sys.executable, "-m", "boards", "start", f"{port}"])

    for i in range(30):
        if status(port):
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
            print(results)
    except Exception as e:
        print(e)


def main():
    fire.Fire(
        {
            "new_members": new_members,
            "new_boards": new_boards,
            "serve": serve,
            "status": status,
        }
    )


if __name__ == "__main__":
    main()
