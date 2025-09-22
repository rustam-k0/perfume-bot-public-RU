import sqlite3

DATABASE_PATH = 'data/perfumes.db'

def get_db_connection():
    """Создает и возвращает соединение с базой данных."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Позволяет получать строки как словари
    return conn

def get_all_original_perfumes() -> list:
    """Извлекает все оригинальные парфюмы из базы данных."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OriginalPerfume")
        perfumes = [dict(row) for row in cursor.fetchall()]
        return perfumes
    finally:
        conn.close()

def find_perfume_and_clones(original_brand: str, original_name: str) -> tuple:
    """
    Ищет оригинальный парфюм и его клоны по бренду и названию.
    
    Возвращает:
    - кортеж (original_perfume, list_of_clones).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Поиск оригинала
        cursor.execute(
            "SELECT * FROM OriginalPerfume WHERE brand = ? AND name = ?",
            (original_brand, original_name)
        )
        original = cursor.fetchone()
        
        if original:
            # Если оригинал найден, ищем его клоны
            cursor.execute(
                "SELECT * FROM CopyPerfume WHERE original_id = ?",
                (original['id'],)
            )
            clones = [dict(row) for row in cursor.fetchall()]
            return dict(original), clones
            
    finally:
        conn.close()
    
    return None, []

def find_by_name_or_brand(query: str, is_brand_only: bool = False) -> list:
    """
    Ищет парфюмы по названию или бренду, используя нечеткий поиск.
    Если is_brand_only=True, ищет только по бренду.
    
    Возвращает:
    - список найденных словарей-парфюмов.
    """
    conn = get_db_connection()
    results = []
    try:
        cursor = conn.cursor()
        normalized_query = "%" + query.lower() + "%"
        
        # Поиск в оригинальных парфюмах
        if not is_brand_only:
            cursor.execute(
                "SELECT id, brand, name FROM OriginalPerfume WHERE LOWER(name) LIKE ? OR LOWER(brand) LIKE ?",
                (normalized_query, normalized_query)
            )
        else:
            cursor.execute(
                "SELECT id, brand, name FROM OriginalPerfume WHERE LOWER(brand) LIKE ?",
                (normalized_query,)
            )
            
        results = [dict(row) for row in cursor.fetchall()]
            
    finally:
        conn.close()
        
    return results