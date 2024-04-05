from datetime import datetime
from enum import Enum
from sqlalchemy import Column,String, Integer,TIMESTAMP,text, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from sqlalchemy.orm import relationship ,DeclarativeBase, Mapped,mapped_column
from app.db.base import Base
from typing import List

class StatusReset(Enum):
    done = "done"
    send = "send"

StatusResetType = pgEnum(StatusReset, name='status_reset', metadata=Base.metadata)


class UserModel(Base):
    __tablename__ = 'user'

    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True,nullable=False)
    email :Mapped[str] = mapped_column(nullable=False,unique =True)
    name : Mapped[str] = mapped_column(nullable=False)
    created_at : Mapped[datetime] = mapped_column(server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    auth : Mapped["AuthModel"]= relationship( back_populates="user")
    link_short: Mapped["LinkShortModel"] =  relationship( back_populates="user")
    reset_passwords : Mapped[List["ResetPasswordModel"]] = relationship( back_populates="user")

class AuthModel(Base):
    __tablename__ = 'auth'
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), primary_key=True,nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    user : Mapped["UserModel"] = relationship (back_populates="auth")

class LinkShortModel(Base):
    __tablename__ = 'link_short'
    
    user_id : Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)
    link_long : Mapped[str]= mapped_column(nullable=False)
    short_link: Mapped[str]= mapped_column(primary_key=True,nullable=False,unique=True)

    user : Mapped["UserModel"] = relationship (back_populates="link_short")
    clicks:Mapped["ClickModel"] = relationship(back_populates="link_short")

class ResetPasswordModel(Base):
    __tablename__ = 'reset_password'

    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True,nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id',ondelete='CASCADE'),nullable=False)
    status : Mapped[StatusReset]= mapped_column(StatusResetType,nullable=False)
    code : Mapped[str]= mapped_column(nullable=False)
    new_password: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["UserModel"] = relationship(back_populates="reset_passwords")


class ClickModel(Base):
    __tablename__ =  'click'

    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True,nullable=False)
    link_short_id: Mapped[str] = mapped_column(ForeignKey('link_short.short_link', ondelete='CASCADE'),nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)
    ip: Mapped[str] = mapped_column(nullable=False)
    localization: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    link_short: Mapped["LinkShortModel"] = relationship(back_populates="clicks")

