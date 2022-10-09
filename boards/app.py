"""Main module."""
import logging
import os

import pkg_resources
from apscheduler.schedulers.background import BackgroundScheduler
from sanic import Sanic, response

from boards.board import ConceptBoard, IndustryBoard, sync_board

application = Sanic("boards")
logger = logging.getLogger(__name__)
ver = pkg_resources.get_distribution("zillionare-ths-boards").parsed_version


@application.route("/")
async def root(request):
    return response.json(
        {"greetings": "Welcome OnBoard!本服务提供了同花顺板块数据同步", "endpoint": f"/boards/{ver}"}
    )


def start(port: int = 2308, log_file="/var/log/boards/server.log"):
    log_dir = os.path.dirname(log_file)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    formatter = logging.Formatter(format)
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=7
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception:
        print(
            "failed to create log dir. logging messages will be output to console instead"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    scheduler = BackgroundScheduler()
    run_at = int(os.environ.get("boards_run_at", "5"))
    scheduler.add_job(sync_board, trigger="cron", hour=run_at)
    scheduler.add_job(ConceptBoard.init, "date")
    scheduler.add_job(IndustryBoard.init, "date")
    scheduler.start()

    application.run(
        host="0.0.0.0",
        port=port,
        register_sys_signals=True,
        workers=1,
        single_process=True,
    )
    logger.info("boards serve stopped")
