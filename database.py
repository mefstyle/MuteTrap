import sqlite3
from typing import Optional

DEFAULT_DB = "bot.db"

def init_db(db_path: str = DEFAULT_DB) -> None:
    """Initializes the SQLite database and creates the trap_channels table if it doesn't exist."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trap_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL
            )
            """
        )
        conn.commit()

def set_trap_channel(guild_id: int, channel_id: int, db_path: str = DEFAULT_DB) -> None:
    """Saves or updates the trap channel ID for a specific guild."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO trap_channels (guild_id, channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id
            """,
            (guild_id, channel_id)
        )
        conn.commit()

def get_trap_channel(guild_id: int, db_path: str = DEFAULT_DB) -> Optional[int]:
    """Retrieves the trap channel ID configured for a specific guild."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT channel_id FROM trap_channels WHERE guild_id = ?",
            (guild_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
