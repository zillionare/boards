import asyncio
import datetime
import os
import shutil

import arrow
import pandas as pd

from boards.board import ConceptBoard, IndustryBoard

async def list_all_boards():
    cons = ConceptBoard()
    cons.init()

    try:
        cons.fetch_board_list()
    except Exception as e:
        print(e)

    boards = cons._store[f"{cons.category}/boards"]
    total_boars = len(boards)
    for i, name in enumerate(boards["name"]):
        code = cons.get_code(name)
        print(code, name)



asyncio.run(list_all_boards())