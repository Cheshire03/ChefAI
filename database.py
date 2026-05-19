"""
database.py
-----------
Maneja toda la persistencia SQLite para ChefAI.
Tablas: perfiles, alergias_perfil, preferencias_perfil, recetas_favoritas
"""

import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv('DB_PATH', 'chefai.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────

def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS perfiles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            condiciones TEXT    DEFAULT '',
            cocina      TEXT    DEFAULT '',
            tiempo_max  TEXT    DEFAULT '',
            dificultad  TEXT    DEFAULT '',
            creado_en   DATETIME DEFAULT CURRENT_TIMESTAMP,
            actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alergias_perfil (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            perfil_id  INTEGER NOT NULL REFERENCES perfiles(id) ON DELETE CASCADE,
            alergia    TEXT    NOT NULL,
            UNIQUE(perfil_id, alergia)
        );

        CREATE TABLE IF NOT EXISTS recetas_favoritas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            perfil_id    INTEGER NOT NULL REFERENCES perfiles(id) ON DELETE CASCADE,
            receta_id    INTEGER NOT NULL,
            nombre       TEXT    NOT NULL,
            ingredientes TEXT    DEFAULT '',
            guardado_en  DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(perfil_id, receta_id)
        );
        """)
    print("✅ Base de datos inicializada")


# ─────────────────────────────────────────────
# PERFILES
# ─────────────────────────────────────────────

def get_all_perfiles():
    with db() as conn:
        rows = conn.execute("""
            SELECT p.*, GROUP_CONCAT(a.alergia) as alergias_list
            FROM perfiles p
            LEFT JOIN alergias_perfil a ON a.perfil_id = p.id
            GROUP BY p.id
            ORDER BY p.creado_en DESC
        """).fetchall()
        return [_perfil_to_dict(r) for r in rows]


def get_perfil(perfil_id: int):
    with db() as conn:
        row = conn.execute("""
            SELECT p.*, GROUP_CONCAT(a.alergia) as alergias_list
            FROM perfiles p
            LEFT JOIN alergias_perfil a ON a.perfil_id = p.id
            WHERE p.id = ?
            GROUP BY p.id
        """, (perfil_id,)).fetchone()
        return _perfil_to_dict(row) if row else None


def create_perfil(nombre: str, condiciones: str, alergias: list,
                  cocina: str, tiempo_max: str, dificultad: str) -> int:
    with db() as conn:
        cur = conn.execute("""
            INSERT INTO perfiles (nombre, condiciones, cocina, tiempo_max, dificultad)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, condiciones, cocina, tiempo_max, dificultad))
        perfil_id = cur.lastrowid
        _set_alergias(conn, perfil_id, alergias)
        return perfil_id


def update_perfil(perfil_id: int, nombre: str, condiciones: str, alergias: list,
                  cocina: str, tiempo_max: str, dificultad: str):
    with db() as conn:
        conn.execute("""
            UPDATE perfiles
            SET nombre=?, condiciones=?, cocina=?, tiempo_max=?, dificultad=?,
                actualizado_en=CURRENT_TIMESTAMP
            WHERE id=?
        """, (nombre, condiciones, cocina, tiempo_max, dificultad, perfil_id))
        _set_alergias(conn, perfil_id, alergias)


def delete_perfil(perfil_id: int):
    with db() as conn:
        conn.execute("DELETE FROM perfiles WHERE id=?", (perfil_id,))


def _set_alergias(conn, perfil_id: int, alergias: list):
    conn.execute("DELETE FROM alergias_perfil WHERE perfil_id=?", (perfil_id,))
    for a in alergias:
        if a.strip():
            conn.execute(
                "INSERT OR IGNORE INTO alergias_perfil (perfil_id, alergia) VALUES (?,?)",
                (perfil_id, a.strip())
            )


def _perfil_to_dict(row) -> dict:
    if not row:
        return {}
    d = dict(row)
    raw = d.pop('alergias_list', '') or ''
    d['alergias'] = [a for a in raw.split(',') if a]
    d['condiciones_lista'] = [c for c in d.get('condiciones', '').split(',') if c]
    return d


# ─────────────────────────────────────────────
# FAVORITOS / LIKES
# ─────────────────────────────────────────────

def add_like(perfil_id: int, receta_id: int, nombre: str, ingredientes: list):
    with db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO recetas_favoritas
                (perfil_id, receta_id, nombre, ingredientes)
            VALUES (?, ?, ?, ?)
        """, (perfil_id, receta_id, nombre, ','.join(ingredientes)))


def remove_like(perfil_id: int, receta_id: int):
    with db() as conn:
        conn.execute("""
            DELETE FROM recetas_favoritas
            WHERE perfil_id=? AND receta_id=?
        """, (perfil_id, receta_id))


def get_likes(perfil_id: int) -> list:
    with db() as conn:
        rows = conn.execute("""
            SELECT receta_id, nombre, ingredientes, guardado_en
            FROM recetas_favoritas
            WHERE perfil_id=?
            ORDER BY guardado_en DESC
        """, (perfil_id,)).fetchall()
        return [dict(r) for r in rows]


def is_liked(perfil_id: int, receta_id: int) -> bool:
    with db() as conn:
        row = conn.execute("""
            SELECT 1 FROM recetas_favoritas
            WHERE perfil_id=? AND receta_id=?
        """, (perfil_id, receta_id)).fetchone()
        return row is not None


def get_liked_ingredientes(perfil_id: int) -> list:
    """
    Devuelve lista plana de ingredientes de todas las recetas
    que le gustaron al perfil. Usado para personalizar recomendaciones.
    """
    with db() as conn:
        rows = conn.execute("""
            SELECT ingredientes FROM recetas_favoritas WHERE perfil_id=?
        """, (perfil_id,)).fetchall()
        todos = []
        for r in rows:
            todos.extend([i for i in r['ingredientes'].split(',') if i])
        return todos