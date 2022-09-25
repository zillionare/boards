"""Main module."""
import logging
from threading import Thread

import pkg_resources
from apscheduler.schedulers.background import BackgroundScheduler
from sanic import Sanic, response

from boards.board import ConceptBoard, IndustryBoard, sync_board

application = Sanic("boards")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ver = pkg_resources.get_distribution("zillionare-ths-boards").parsed_version


@application.route("/")
async def root(request):
    return response.json(
        {"greetings": "Welcome OnBoard!本服务提供了同花顺板块数据同步", "endpoint": f"/boards/{ver}"}
    )


def start(port: int = 2308):
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_board, trigger="cron", hour=5)
    scheduler.add_job(ConceptBoard.init, "date")
    scheduler.add_job(IndustryBoard.init, "date")
    scheduler.start()

    application.run(host="0.0.0.0", port=port, register_sys_signals=True)
    logger.info("boards serve stopped")
