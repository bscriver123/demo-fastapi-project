import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
from app.core.transaction_manager import handle_transaction


def create_user(*, session: Session, user_create: UserCreate) -> User:
    def create_user_operation(tx_session: Session) -> User:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        tx_session.add(db_obj)
        return db_obj

    return handle_transaction(session, [create_user_operation])[0]


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    def update_user_operation(tx_session: Session) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        tx_session.add(db_user)
        return db_user

    return handle_transaction(session, [update_user_operation])[0]


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    def create_item_operation(tx_session: Session) -> Item:
        db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
        tx_session.add(db_item)
        return db_item

    return handle_transaction(session, [create_item_operation])[0]
