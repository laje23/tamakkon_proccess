from models.database_connection import get_connection


class PermissionTableManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        self.cursor.close()
        self.conn.close()

    # -------------------------
    # اجرای امن
    # -------------------------
    def _execute(self, query, params=None, fetchone=False, fetchall=False):
        params = params or ()
        self.cursor.execute(query, params)

        if fetchone:
            return self.cursor.fetchone()
        if fetchall:
            return self.cursor.fetchall()

    # -------------------------
    # ساخت جدول permissions
    # -------------------------
    def _create_table(self):
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS permissions (
                id SERIAL PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                description TEXT
            );
            """
        )

    # -------------------------
    # افزودن permission
    # -------------------------
    def _add_permission(self, code, description=None):
        return self._execute(
            """
            WITH inserted AS (
                INSERT INTO permissions (code, description)
                VALUES (%s, %s)
                ON CONFLICT (code) DO NOTHING
                RETURNING id
            )
            SELECT id FROM inserted
            UNION ALL
            SELECT id FROM permissions WHERE code = %s
            LIMIT 1;
            """,
            (code, description, code),
            fetchone=True,
        )

    # -------------------------
    # گرفتن permission با code
    # -------------------------
    def _get_permission(self, code):
        return self._execute(
            """
            SELECT id, code, description
            FROM permissions
            WHERE code = %s;
            """,
            (code,),
            fetchone=True,
        )

    # -------------------------
    # گرفتن همه permission ها
    # -------------------------
    def _get_all_permissions(self):
        return self._execute(
            """
            SELECT id, code, description
            FROM permissions
            ORDER BY id ASC;
            """,
            fetchall=True,
        )

    # -------------------------
    # حذف permission
    # -------------------------
    def _delete_permission(self, code):
        self._execute(
            """
            DELETE FROM permissions
            WHERE code = %s;
            """,
            (code,),
        )


def create_permission_table():
    with PermissionTableManager() as db:
        db._create_table()


def add_permission(code, description=None):
    with PermissionTableManager() as db:
        return db._add_permission(code, description)


def get_permission(code):
    with PermissionTableManager() as db:
        return db._get_permission(code)


def get_all_permissions():
    with PermissionTableManager() as db:
        return db._get_all_permissions()


def delete_permission(code):
    with PermissionTableManager() as db:
        db._delete_permission(code)


def insert_default_permissions():
    default_permissions = [
        ("view_bot_management_menu", "دیدن منوی مدیریت بات"),
        ("member_access_management", "مدیریت دسترسی اعضا"),
        ("send_to_channel", "ارسال پیام ها به کانال"),
        ("competition_Management", "مدیریت مسابقات"),
        ("save_and_edit_content", "نوشتن و ویرایش محتوای جدید"),
        ("manage_default_sounds", "مدیریت صوت های پیشفرض"),
        ("see_statistics", "دیدن آمار بات"),
        ("toggle_scheduling_mode", "تغییر وضعیت زمانبندی"),
    ]

    with PermissionTableManager() as db:
        for code, desc in default_permissions:
            db._add_permission(code, desc)

    return f"✅ {len(default_permissions)} permission اولیه اضافه شد"


def get_all_permission_ids():
    with PermissionTableManager() as db:
        rows = db._execute(
            """
            SELECT id FROM permissions
            ORDER BY id ASC;
            """,
            fetchall=True,
        )
    return [row[0] for row in rows]
