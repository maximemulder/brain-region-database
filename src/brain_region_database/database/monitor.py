import time
from typing import Any

from sqlalchemy import event
from sqlalchemy.orm import Session


class DatabaseMonitor:
    def __init__(self, session: Session):
        @event.listens_for(session.bind, 'before_cursor_execute')
        def before_execute(conn: Any, cursor: Any, statement: Any, params: Any, context: Any, executemany: Any):  # type: ignore
            context._timer_start = time.perf_counter()

        @event.listens_for(session.bind, 'after_cursor_execute')
        def after_execute(conn: Any, cursor: Any, statement: Any, params: Any, context: Any, executemany: Any):  # type: ignore
            elapsed = time.perf_counter() - context._timer_start
            print(f'Query: {elapsed * 1000:.2f} ms')
