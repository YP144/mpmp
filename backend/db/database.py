"""
Database configuration & connection utilities for every database type
supported by ``dej_sdk.databases``:

    mariadb | postgres/postgresql | mongodb | redis | elasticsearch | milvus

Layout
------
1. Configuration      -> DB_CONFIGS (per-type tunables) + configure()
2. Handlers           -> one class per DB type (connect / ping / close)
3. Database manager   -> singleton per (server, database), retry + reconnect
4. Public helpers     -> get_dej_db_connection() and per-type async context
                         managers (mariadb_session, postgres_session, ...)
5. Local pool         -> get_db_connection() (LOCAL DB, kept for migration)

Selecting a server and a database
---------------------------------
``db``        -> which dej_sdk entry (index in databases.list() or its name)
``database``  -> optional database *inside* that server, e.g. "MasterMP_Data".
                 If omitted, the database from the SDK connection info is used.

    async with get_dej_db_connection(0, database="MasterMP_Data") as (conn, cur):
        cur.execute('SELECT * FROM public.summary_team')

Driver imports are lazy, so a service only needs the drivers for the
databases it actually uses.
"""
from __future__ import annotations

import asyncio
import copy
import logging
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Dict, Optional, Tuple, Type, Union

from dej_sdk import databases

logger = logging.getLogger(__name__)

DbRef = Union[int, str]


# =============================================================================
# 1. CONFIGURATION
# =============================================================================

# Shared retry policy (exponential backoff: retry_delay * 2**attempt)
RETRY_CONFIG: Dict[str, Any] = {
    "max_retries": 3,
    "retry_delay": 1.0,  # seconds
}

# Per-database-type configuration. Values here are applied on top of the
# connection info returned by dej_sdk (host/port/uri/username/password).
DB_CONFIGS: Dict[str, Dict[str, Any]] = {
    "mariadb": {
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
        "charset": "utf8mb4",
        "autocommit": False,
        "dict_cursor": True,          # use pymysql DictCursor
        "fallback_database": "mydb",  # same fallback as dej_sdk
    },
    "postgres": {
        "connect_timeout": 10,
        "autocommit": False,
        "dict_cursor": True,          # use psycopg2 RealDictCursor
        "application_name": "dej_app",
    },
    "mongodb": {
        "server_selection_timeout_ms": 5000,
        "connect_timeout_ms": 10000,
        "socket_timeout_ms": 30000,
        "max_pool_size": 50,
        "min_pool_size": 0,
        "default_port": 27017,
    },
    "redis": {
        "default_sentinel_port": 26379,
        "default_master_name": "mymaster",
        "sentinel_socket_timeout": 0.1,   # Sentinel discovery only
        "socket_timeout": 10,             # master connection
        "socket_connect_timeout": 5,
        "decode_responses": True,
        "health_check_interval": 30,
    },
    "elasticsearch": {
        "request_timeout": 30,
        "verify_certs": False,
        "max_retries": 3,
        "retry_on_timeout": True,
    },
    "milvus": {
        "timeout": 10,
        "default_db_name": "",            # "" -> server default
    },
}

# Aliases -> canonical type name
DB_TYPE_ALIASES = {
    "postgresql": "postgres",
    "mysql": "mariadb",
    "mongo": "mongodb",
    "es": "elasticsearch",
}

# SQL types yield (conn, cursor); client-based types yield (client, None)
SQL_DB_TYPES = {"mariadb", "postgres"}
CLIENT_BASED_DB_TYPES = {"mongodb", "redis", "elasticsearch", "milvus"}


def normalize_db_type(db_type: str) -> str:
    db_type = (db_type or "").strip().lower()
    return DB_TYPE_ALIASES.get(db_type, db_type)


def get_config(db_type: str) -> Dict[str, Any]:
    """Return a copy of the configuration for a database type."""
    return copy.deepcopy(DB_CONFIGS.get(normalize_db_type(db_type), {}))


def configure(db_type: str, **overrides: Any) -> Dict[str, Any]:
    """
    Override configuration for a database type at runtime (call at startup).

        configure("mariadb", read_timeout=60)
        configure("redis", decode_responses=False)
    """
    key = normalize_db_type(db_type)
    if key not in DB_CONFIGS:
        raise ValueError(f"Unsupported database type: {db_type}")
    DB_CONFIGS[key].update(overrides)
    return get_config(key)


# =============================================================================
# 2. HANDLERS (one per database type)
# =============================================================================

class BaseHandler:
    """Common interface for every database type."""

    db_type: str = ""
    supports_database: bool = True   # can `database` be selected?

    def __init__(self, db_name: str, db_info: Dict[str, Any], database: Optional[str] = None):
        self.db_name = db_name
        self.db_info = db_info
        self.database = database
        self.config = get_config(self.db_type)
        if database and not self.supports_database:
            raise ValueError(f"[{db_name}] '{self.db_type}' does not support selecting a database")

    # --- to implement -------------------------------------------------------
    def connect(self) -> Any:
        raise NotImplementedError

    def ping(self, conn: Any) -> None:
        """Raise if the connection is not alive (sync drivers)."""
        raise NotImplementedError

    def close(self, conn: Any) -> None:
        conn.close()

    def session_object(self, conn: Any) -> Any:
        """Object yielded to the caller (default: the connection itself)."""
        return conn

    # --- async wrappers (sync drivers run off the event loop) --------------
    async def aping(self, conn: Any) -> None:
        await asyncio.to_thread(self.ping, conn)

    async def aclose(self, conn: Any) -> None:
        await asyncio.to_thread(self.close, conn)

    # --- helpers ------------------------------------------------------------
    def _require(self, *keys: str) -> None:
        missing = [k for k in keys if not self.db_info.get(k)]
        if missing:
            raise ValueError(f"[{self.db_name}] missing connection field(s): {', '.join(missing)}")


class MariaDBHandler(BaseHandler):
    db_type = "mariadb"

    def _connect_to(self, database: str):
        import pymysql
        from pymysql.cursors import Cursor, DictCursor

        cfg = self.config
        return pymysql.connect(
            host=self.db_info["host"],
            user=self.db_info["username"],
            password=self.db_info["password"],
            port=int(self.db_info.get("port", 3306)),
            database=database,
            connect_timeout=cfg["connect_timeout"],
            read_timeout=cfg["read_timeout"],
            write_timeout=cfg["write_timeout"],
            charset=cfg["charset"],
            autocommit=cfg["autocommit"],
            cursorclass=DictCursor if cfg["dict_cursor"] else Cursor,
        )

    def connect(self):
        self._require("host", "username", "password")
        if self.database:
            # Explicit database -> no silent fallback
            return self._connect_to(self.database)
        try:
            return self._connect_to(self.db_name)
        except Exception as e:
            fallback = self.config.get("fallback_database")
            if not fallback:
                raise
            logger.warning("[%s] MariaDB connect failed (%s). Falling back to '%s'.",
                           self.db_name, e, fallback)
            return self._connect_to(fallback)

    def ping(self, conn):
        conn.ping(reconnect=False)


class PostgresHandler(BaseHandler):
    db_type = "postgres"

    def connect(self):
        import psycopg2
        import psycopg2.extras

        cfg = self.config
        kwargs: Dict[str, Any] = {
            "connect_timeout": cfg["connect_timeout"],
            "application_name": cfg["application_name"],
        }
        if cfg["dict_cursor"]:
            kwargs["cursor_factory"] = psycopg2.extras.RealDictCursor
        if self.database:
            kwargs["dbname"] = self.database   # keyword args override the URI

        uri = self.db_info.get("uri")
        if uri:
            conn = psycopg2.connect(uri, **kwargs)
        else:
            self._require("host", "username", "password")
            kwargs.setdefault("dbname", self.db_info.get("database", self.db_name))
            conn = psycopg2.connect(
                host=self.db_info["host"],
                port=int(self.db_info.get("port", 5432)),
                user=self.db_info["username"],
                password=self.db_info["password"],
                **kwargs,
            )
        conn.autocommit = cfg["autocommit"]
        return conn

    def ping(self, conn):
        if conn.closed:
            raise ConnectionError("PostgreSQL connection is closed")
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        if not conn.autocommit:
            conn.rollback()  # don't leave the ping transaction open


class MongoDBHandler(BaseHandler):
    db_type = "mongodb"

    def _build_uri(self) -> str:
        uri = (self.db_info.get("uri") or "").strip()
        if uri:
            return uri
        # Same in-cluster URI that dej_sdk generates when 'uri' is empty
        self._require("username", "password", "name")
        name = self.db_info["name"]
        host = f"{name}-0.{name}-svc.mongodb.svc.cluster.local"
        port = self.config["default_port"]
        return (f"mongodb://{self.db_info['username']}:{self.db_info['password']}@"
                f"{host}:{port}/admin?replicaSet={name}&ssl=false")

    def connect(self):
        import pymongo

        cfg = self.config
        return pymongo.MongoClient(
            self._build_uri(),
            serverSelectionTimeoutMS=cfg["server_selection_timeout_ms"],
            connectTimeoutMS=cfg["connect_timeout_ms"],
            socketTimeoutMS=cfg["socket_timeout_ms"],
            maxPoolSize=cfg["max_pool_size"],
            minPoolSize=cfg["min_pool_size"],
        )

    def ping(self, conn):
        # Never use hasattr() on pymongo objects (__getattr__ always succeeds)
        client = getattr(conn, "client", conn)
        client.admin.command("ping")

    def session_object(self, conn):
        # database given -> yield pymongo Database, otherwise the MongoClient
        return conn[self.database] if self.database else conn


class RedisHandler(BaseHandler):
    """Async Redis via Sentinel (redis.asyncio). `database` = logical DB number."""
    db_type = "redis"

    def connect(self):
        from redis.asyncio.sentinel import Sentinel as AsyncSentinel

        self._require("host")
        cfg = self.config
        sentinel = AsyncSentinel(
            [(self.db_info["host"],
              int(self.db_info.get("port", cfg["default_sentinel_port"])))],
            # sentinel_kwargs -> Sentinel discovery connections only
            sentinel_kwargs={"socket_timeout": cfg["sentinel_socket_timeout"]},
            # remaining kwargs -> inherited by the master connection
            socket_timeout=cfg["socket_timeout"],
            socket_connect_timeout=cfg["socket_connect_timeout"],
            health_check_interval=cfg["health_check_interval"],
        )
        master_kwargs: Dict[str, Any] = {
            "password": self.db_info.get("password"),
            "decode_responses": cfg["decode_responses"],
        }
        if self.database:
            try:
                master_kwargs["db"] = int(self.database)
            except ValueError:
                raise ValueError(f"[{self.db_name}] Redis database must be a number, "
                                 f"got '{self.database}'") from None
        client = sentinel.master_for(
            self.db_info.get("master_name", cfg["default_master_name"]),
            **master_kwargs,
        )
        pool_kwargs = client.connection_pool.connection_kwargs
        logger.debug("[%s] Redis master kwargs: socket_timeout=%s, socket_connect_timeout=%s",
                     self.db_name, pool_kwargs.get("socket_timeout"),
                     pool_kwargs.get("socket_connect_timeout"))
        return client

    def ping(self, conn):  # pragma: no cover - async client, use aping()
        raise RuntimeError("Use aping() for async Redis client")

    async def aping(self, conn):
        await conn.ping()

    async def aclose(self, conn):
        closer = getattr(conn, "aclose", None) or conn.close  # redis>=5 / <5
        await closer()


class ElasticsearchHandler(BaseHandler):
    db_type = "elasticsearch"
    supports_database = False   # indices are chosen per request

    def connect(self):
        from elasticsearch import Elasticsearch

        self._require("uri")
        cfg = self.config
        auth = None
        if self.db_info.get("username"):
            auth = (self.db_info["username"], self.db_info.get("password", ""))

        common = {
            "hosts": [self.db_info["uri"]],
            "verify_certs": cfg["verify_certs"],
            "request_timeout": cfg["request_timeout"],
            "max_retries": cfg["max_retries"],
            "retry_on_timeout": cfg["retry_on_timeout"],
        }
        if not cfg["verify_certs"]:
            common["ssl_show_warn"] = False
        try:
            return Elasticsearch(basic_auth=auth, **common)   # elasticsearch-py >= 8
        except TypeError:
            common.pop("ssl_show_warn", None)
            common["timeout"] = common.pop("request_timeout")
            return Elasticsearch(http_auth=auth, **common)    # elasticsearch-py 7.x

    def ping(self, conn):
        if not conn.ping():
            raise ConnectionError("Elasticsearch ping failed")


class MilvusHandler(BaseHandler):
    db_type = "milvus"

    def connect(self):
        from pymilvus import MilvusClient

        self._require("uri")
        cfg = self.config
        kwargs: Dict[str, Any] = {"uri": self.db_info["uri"], "timeout": cfg["timeout"]}
        token = self.db_info.get("token")
        if not token and self.db_info.get("username"):
            token = f"{self.db_info['username']}:{self.db_info.get('password', '')}"
        if token:
            kwargs["token"] = token
        db_name = self.database or self.db_info.get("db_name", cfg["default_db_name"])
        if db_name:
            kwargs["db_name"] = db_name
        return MilvusClient(**kwargs)

    def ping(self, conn):
        conn.list_collections()


HANDLERS: Dict[str, Type[BaseHandler]] = {
    "mariadb": MariaDBHandler,
    "postgres": PostgresHandler,
    "mongodb": MongoDBHandler,
    "redis": RedisHandler,
    "elasticsearch": ElasticsearchHandler,
    "milvus": MilvusHandler,
}


def get_handler(db_name: str, db_info: Dict[str, Any],
                database: Optional[str] = None) -> BaseHandler:
    db_type = normalize_db_type(db_info.get("type", ""))
    handler_cls = HANDLERS.get(db_type)
    if handler_cls is None:
        raise ValueError(f"[{db_name}] unsupported database type: '{db_info.get('type')}'")
    return handler_cls(db_name, db_info, database)


# =============================================================================
# 3. DATABASE MANAGER
# =============================================================================

def resolve_db_name(db: DbRef) -> str:
    """Resolve an index (position in databases.list()) or a name to a db name."""
    if isinstance(db, str):
        return db
    db_list = databases.list()
    try:
        return db_list[db]["name"]
    except IndexError:
        raise ConnectionError(
            f"db_index {db} out of range (found {len(db_list)} database(s))") from None


def list_databases(db_type: Optional[str] = None):
    """List databases from dej_sdk, optionally filtered by type."""
    items = databases.list()
    if db_type:
        wanted = normalize_db_type(db_type)
        items = [d for d in items if normalize_db_type(d["type"]) == wanted]
    return items


class Database:
    """
    Connection manager for one dej_sdk server + optional database
    (singleton per (server name, database)).

        Database(0)                              # index 0, default database
        Database("pg-main", "MasterMP_Data")     # by name, specific database
    """
    _instances: Dict[Tuple[str, Optional[str]], "Database"] = {}
    _lock = threading.Lock()

    def __new__(cls, db: DbRef, database: Optional[str] = None):
        db_name = resolve_db_name(db)
        key = (db_name, database or None)
        with cls._lock:
            if key not in cls._instances:
                instance = super().__new__(cls)
                instance.db_name = db_name
                instance.database = database or None
                instance.conn = None
                instance.handler = None
                instance.db_type = None
                instance._last_used = 0.0
                cls._instances[key] = instance
            return cls._instances[key]

    def __init__(self, db: DbRef, database: Optional[str] = None):
        if self.conn is None:
            self.connect()

    @property
    def label(self) -> str:
        return f"{self.db_name}/{self.database}" if self.database else self.db_name

    # -- lifecycle -----------------------------------------------------------
    def connect(self):
        last_error: Optional[Exception] = None
        retries = RETRY_CONFIG["max_retries"]
        for attempt in range(retries):
            try:
                db_info = databases.get(self.db_name)
                if not isinstance(db_info, dict) or "error" in db_info:
                    raise LookupError((db_info or {}).get("error", f"No info for '{self.db_name}'"))
                self.handler = get_handler(self.db_name, db_info, self.database)
                self.db_type = self.handler.db_type
                self.conn = self.handler.connect()
                self._last_used = time.time()
                logger.debug("Connected to '%s' (type=%s, attempt=%d)",
                             self.label, self.db_type, attempt + 1)
                return self.conn
            except (LookupError, ValueError) as e:
                # Configuration problems will not fix themselves -> no retry
                raise ConnectionError(f"[{self.label}] {e}") from e
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    delay = RETRY_CONFIG["retry_delay"] * (2 ** attempt)
                    logger.warning("[%s] connect attempt %d failed: %s. Retrying in %.1fs...",
                                   self.label, attempt + 1, e, delay)
                    time.sleep(delay)
        logger.error("[%s] all %d connection attempts failed: %s", self.label, retries, last_error)
        raise ConnectionError(
            f"[{self.label}] failed to connect after {retries} attempts: {last_error}")

    async def aconnect(self):
        """Non-blocking connect (runs retry/backoff in a worker thread)."""
        return await asyncio.to_thread(self.connect)

    async def aclose(self):
        if self.conn is None:
            return
        try:
            await self.handler.aclose(self.conn)
            logger.debug("[%s] connection closed", self.label)
        except Exception as e:
            logger.warning("[%s] error closing connection: %s", self.label, e)
        finally:
            self.conn = None
            self._last_used = 0.0

    async def ais_connected(self) -> bool:
        if self.conn is None or self.handler is None:
            return False
        try:
            await self.handler.aping(self.conn)
            return True
        except Exception:
            return False

    async def areconnect_if_needed(self):
        if not await self.ais_connected():
            await self.aclose()
            await self.aconnect()

    @classmethod
    async def aclose_all(cls):
        """Close every managed connection (call on application shutdown)."""
        for instance in list(cls._instances.values()):
            await instance.aclose()
        cls._instances.clear()


# =============================================================================
# 4. PUBLIC HELPERS
# =============================================================================

async def _get_ready_db(db: DbRef, database: Optional[str] = None,
                        expected_type: Optional[str] = None) -> Database:
    instance = await asyncio.to_thread(Database, db, database)
    await instance.areconnect_if_needed()
    if instance.conn is None:
        raise ConnectionError(f"Failed to establish connection to '{instance.label}'")
    if expected_type and instance.db_type != normalize_db_type(expected_type):
        raise TypeError(f"'{instance.label}' is '{instance.db_type}', not '{expected_type}'")
    return instance


@asynccontextmanager
async def _sql_session(instance: Database):
    conn = instance.conn
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        instance._last_used = time.time()


@asynccontextmanager
async def get_dej_db_connection(db: DbRef = 0, database: Optional[str] = None):  # DEJ DB (async)
    """
    Generic async context manager.

    db        : index in databases.list() or the SDK database name
    database  : optional database inside that server
                  postgres / mariadb -> database name   (e.g. "MasterMP_Data")
                  mongodb            -> yields that pymongo Database instead of the client
                  redis              -> logical DB number ("0".."15")
                  milvus             -> db_name
                  elasticsearch      -> not supported (raises ConnectionError)

    SQL (mariadb, postgres) -> yields (conn, cursor); commit on success, rollback on error
        async with get_dej_db_connection(0, database="MasterMP_Data") as (conn, cursor):
            cursor.execute("SELECT * FROM public.summary_team")

    Client-based (mongodb, redis, elasticsearch, milvus) -> yields (client, None)
        Redis is async:        await client.get("k")
        Others are sync, offload them:
            await asyncio.to_thread(client.mycol.find_one, {"_id": 1})
    """
    instance = await _get_ready_db(db, database)
    if instance.db_type in SQL_DB_TYPES:
        async with _sql_session(instance) as session:
            yield session
    else:
        try:
            yield instance.handler.session_object(instance.conn), None
        finally:
            instance._last_used = time.time()


# ---- per-type helpers (type-checked) ----------------------------------------

@asynccontextmanager
async def mariadb_session(db: DbRef, database: Optional[str] = None):
    """async with mariadb_session("name", "mydb") as (conn, cursor): ..."""
    instance = await _get_ready_db(db, database, "mariadb")
    async with _sql_session(instance) as session:
        yield session


@asynccontextmanager
async def postgres_session(db: DbRef, database: Optional[str] = None):
    """async with postgres_session(0, "MasterMP_Data") as (conn, cursor): ..."""
    instance = await _get_ready_db(db, database, "postgres")
    async with _sql_session(instance) as session:
        yield session


@asynccontextmanager
async def mongo_database(db: DbRef, database: Optional[str] = None):
    """
    Yields a pymongo Database (sync API -> use asyncio.to_thread for calls).
        async with mongo_database("name", "mydb") as mdb:
            doc = await asyncio.to_thread(mdb.users.find_one, {"_id": 1})
    If database is omitted, the default DB from the URI is used.
    """
    instance = await _get_ready_db(db, database, "mongodb")
    client = instance.conn
    yield client[database] if database else client.get_default_database()


@asynccontextmanager
async def redis_client(db: DbRef, database: Optional[str] = None):
    """async with redis_client("name") as r: await r.set("k", "v")"""
    instance = await _get_ready_db(db, database, "redis")
    yield instance.conn


@asynccontextmanager
async def es_client(db: DbRef):
    """async with es_client("name") as es: await asyncio.to_thread(es.search, index="i", query=...)"""
    instance = await _get_ready_db(db, None, "elasticsearch")
    yield instance.conn


@asynccontextmanager
async def milvus_client(db: DbRef, database: Optional[str] = None):
    """async with milvus_client("name") as mc: await asyncio.to_thread(mc.search, ...)"""
    instance = await _get_ready_db(db, database, "milvus")
    yield instance.conn


async def health_check() -> Dict[str, Dict[str, Any]]:
    """Ping every database registered in dej_sdk. Useful for /health endpoints."""
    results: Dict[str, Dict[str, Any]] = {}
    for item in databases.list():
        name = item["name"]
        try:
            instance = await _get_ready_db(name)
            ok = await instance.ais_connected()
            results[name] = {"type": instance.db_type, "ok": ok}
        except Exception as e:
            results[name] = {"type": normalize_db_type(item.get("type", "")), "ok": False,
                             "error": str(e)}
    return results


# =============================================================================
# 5. LOCAL DB POOL (will be removed after migration)
# =============================================================================

POOL_CONFIG = {
    "min_connections": 2,
    "max_connections": 10,
    "connection_timeout": 10,  # seconds
    "max_retries": RETRY_CONFIG["max_retries"],
    "retry_delay": RETRY_CONFIG["retry_delay"],
}

LOCAL_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "dashboard",
    "port": 3306,
}


class ConnectionPool:
    """Thread-safe pymysql connection pool for the local database."""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self._params = dict(host=host, user=user, password=password, database=database, port=port)
        self._pool = []
        self._in_use = set()
        self._lock = threading.Lock()
        self._min_size = POOL_CONFIG["min_connections"]
        self._max_size = POOL_CONFIG["max_connections"]
        self._timeout = POOL_CONFIG["connection_timeout"]
        for _ in range(self._min_size):
            conn = self._create_connection()
            if conn:
                self._pool.append(conn)
        logger.info("Local connection pool initialized with %d connections", len(self._pool))

    def _create_connection(self):
        import pymysql
        from pymysql.cursors import DictCursor
        try:
            return pymysql.connect(
                **self._params,
                connect_timeout=self._timeout,
                read_timeout=self._timeout,
                write_timeout=self._timeout,
                cursorclass=DictCursor,
                autocommit=False,
            )
        except Exception as e:
            logger.error("Failed to create local DB connection: %s", e)
            return None

    @staticmethod
    def _is_alive(conn) -> bool:
        try:
            conn.ping(reconnect=False)
            return True
        except Exception:
            return False

    @staticmethod
    def _safe_close(conn):
        try:
            conn.close()
        except Exception:
            pass

    def get_connection(self):
        last_error = None
        for attempt in range(POOL_CONFIG["max_retries"]):
            with self._lock:
                while self._pool:
                    conn = self._pool.pop()
                    if self._is_alive(conn):
                        self._in_use.add(conn)
                        return conn
                    self._safe_close(conn)
                can_create = len(self._in_use) < self._max_size
            if can_create:
                conn = self._create_connection()
                if conn:
                    with self._lock:
                        self._in_use.add(conn)
                    return conn
                last_error = ConnectionError("could not create connection")
            else:
                last_error = ConnectionError("pool exhausted")
            if attempt < POOL_CONFIG["max_retries"] - 1:
                delay = POOL_CONFIG["retry_delay"] * (2 ** attempt)
                logger.warning("Get connection attempt %d failed: %s. Retrying in %.1fs...",
                               attempt + 1, last_error, delay)
                time.sleep(delay)
        raise ConnectionError(
            f"Failed to get local DB connection after {POOL_CONFIG['max_retries']} attempts: {last_error}")

    def release_connection(self, conn):
        with self._lock:
            self._in_use.discard(conn)
            if self._is_alive(conn) and len(self._pool) < self._max_size:
                self._pool.append(conn)
                return
        self._safe_close(conn)

    def close_all(self):
        with self._lock:
            for conn in self._pool + list(self._in_use):
                self._safe_close(conn)
            self._pool.clear()
            self._in_use.clear()
        logger.info("All local pool connections closed")


_pool_instance: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_connection_pool() -> ConnectionPool:
    global _pool_instance
    with _pool_lock:
        if _pool_instance is None:
            _pool_instance = ConnectionPool(**LOCAL_DB_CONFIG)
    return _pool_instance


@contextmanager
def get_db_connection():  # LOCAL DB (will be removed due to migration)
    """
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM table")
    """
    pool = get_connection_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        pool.release_connection(conn)
