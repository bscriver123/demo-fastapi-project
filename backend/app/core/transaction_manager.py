from contextlib import contextmanager
from typing import Callable, List, Any
from sqlmodel import Session


@contextmanager
def transaction_context(session: Session):
    """
    A context manager for handling database transactions.
    """
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def handle_transaction(
    session: Session, operations: List[Callable[[Session], Any]]
) -> List[Any]:
    """
    Execute a list of operations within a single transaction.
    Each operation is a function that takes a Session as an argument.
    """
    results = []
    with transaction_context(session) as tx_session:
        for operation in operations:
            result = operation(tx_session)
            tx_session.flush()
            results.append(result)
    return results
