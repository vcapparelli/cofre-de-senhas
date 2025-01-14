import sqlite3
from typing import Any, Callable, Sequence
from connection.conn import IntegrityViolationException, TransactionNotActiveException
from connection.trans import TransactedConnection
from pytest import raises
from dataclasses import dataclass
from validator import dataclass_validate
from .db_test_util import DbTestConfig

db: DbTestConfig = DbTestConfig("test/fruits-ok.db", "test/fruits.db")

create = """
CREATE TABLE IF NOT EXISTS fruit (
    pk_fruit        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;
INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE IF NOT EXISTS juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) STRICT;
""";

@db.decorator
def test_fetchone() -> None:
    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        one: tuple[Any, ...] | None = c.fetchone()
        assert one == (2, "strawberry")

@db.decorator
def test_fetchall() -> None:
    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@db.decorator
def test_fetchall_class() -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class Fruit:
        pk_fruit: int
        name: str

    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[Fruit] = c.fetchall_class(Fruit)
        assert len(all) == 3
        assert all[0].pk_fruit == 1
        assert all[0].name == "orange"
        assert all[1].pk_fruit == 2
        assert all[1].name == "strawberry"
        assert all[2].pk_fruit == 3
        assert all[2].name == "lemon"

@db.decorator
def test_commit() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@db.decorator
def test_rollback() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.rollback()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@db.decorator
def test_transact_1() -> None:
    conn: TransactedConnection = db.new_connection()

    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    conn.transact(x)()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@db.decorator
def test_transact_2() -> None:
    conn: TransactedConnection = db.new_connection()

    @conn.transact
    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    x()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@db.decorator
def test_no_transaction() -> None:
    conn: TransactedConnection = db.new_connection()
    with raises(TransactionNotActiveException):
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

@db.decorator
def test_check_constraint_1() -> None:
    conn: TransactedConnection = db.new_connection()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('abc')")
            c.commit()

@db.decorator
def test_check_constraint_2() -> None:
    conn: TransactedConnection = db.new_connection()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('123456789012345678901234567890123456789012345678901')")
            c.commit()

@db.decorator
def test_foreign_key_constraint_on_orphan_insert() -> None:
    conn: TransactedConnection = db.new_connection()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (666)")
            c.commit()

@db.decorator
def test_foreign_key_constraint_on_update_cascade() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (1)")
        c.commit()

    with conn as c:
        c.execute("UPDATE fruit SET pk_fruit = 777 WHERE pk_fruit = 1")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_1")
        t: tuple[Any, ...] | None = c.fetchone()
        assert t == (777, )

@db.decorator
def test_foreign_key_constraint_on_delete_cascade() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (1)")
        c.commit()

    with conn as c:
        c.execute("DELETE FROM fruit WHERE pk_fruit = 1")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_1 WHERE pk_fruit = 1")
        t: Sequence[tuple[Any, ...]] | None  = c.fetchone()
        assert t is None

@db.decorator
def test_foreign_key_constraint_on_update_restrict() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO juice_2 (pk_fruit) VALUES (1)")
        c.commit()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("UPDATE fruit SET pk_fruit = 777 WHERE pk_fruit = 1")
            c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_2")
        t: tuple[Any, ...] | None = c.fetchone()
        assert t == (1, )

@db.decorator
def test_foreign_key_constraint_on_delete_restrict() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO juice_2 (pk_fruit) VALUES (1)")
        c.commit()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("DELETE FROM fruit WHERE pk_fruit = 1")
            c.commit()

    with conn as c:
        c.execute("SELECT a.pk_fruit FROM juice_2 a INNER JOIN fruit b ON a.pk_fruit = b.pk_fruit WHERE a.pk_fruit = 1")
        t: tuple[Any, ...] | None = c.fetchone()
        assert t == (1, )