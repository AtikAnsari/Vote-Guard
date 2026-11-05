"""
Inspect Vote-Guard MySQL database schema, records, and foreign keys.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine
from sqlalchemy import text

def inspect():
    with engine.connect() as conn:
        print("=== EXISTING TABLES ===")
        tables = [row[0] for row in conn.execute(text("SHOW TABLES")).fetchall()]
        print(tables)

        for table in ["admin_users", "audit_logs", "voter_credentials", "voters"]:
            print(f"\n==========================================")
            print(f"SCHEMA FOR TABLE: {table}")
            print(f"==========================================")
            cols = conn.execute(text(f"DESCRIBE {table}")).fetchall()
            for c in cols:
                print(f"  Field: {c[0]:<20} Type: {c[1]:<20} Null: {c[2]:<6} Key: {c[3]:<6} Default: {str(c[4]):<10} Extra: {c[5]}")

            print(f"\nIndexes & Unique Constraints on {table}:")
            idx = conn.execute(text(f"SHOW INDEXES FROM {table}")).fetchall()
            seen_idx = set()
            for i in idx:
                key_name = i[2]
                col_name = i[4]
                non_unique = i[1]
                uniq = "UNIQUE" if non_unique == 0 else "NON-UNIQUE"
                pair = (key_name, col_name, uniq)
                if pair not in seen_idx:
                    seen_idx.add(pair)
                    print(f"  - Key: {key_name:<25} Column: {col_name:<20} ({uniq})")

        print("\n==========================================")
        print("FOREIGN KEY RELATIONSHIPS (vote_guard)")
        print("==========================================")
        fk_sql = """
        SELECT 
            TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, 
            REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = 'vote_guard' AND REFERENCED_TABLE_NAME IS NOT NULL;
        """
        fks = conn.execute(text(fk_sql)).fetchall()
        for fk in fks:
            print(f"  {fk[0]}.{fk[1]} -> REFERENCES {fk[3]}.{fk[4]} (Constraint: {fk[2]})")

        # Check delete / update actions
        rc_sql = """
        SELECT 
            CONSTRAINT_NAME, TABLE_NAME, REFERENCED_TABLE_NAME, DELETE_RULE, UPDATE_RULE
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = 'vote_guard';
        """
        rcs = conn.execute(text(rc_sql)).fetchall()
        print("\nReferential Actions:")
        for r in rcs:
            print(f"  Constraint: {r[0]} on {r[1]} -> ON DELETE {r[3]}, ON UPDATE {r[4]}")

        print("\n==========================================")
        print("VOTERS TABLE RECORDS")
        print("==========================================")
        voters = conn.execute(text("SELECT * FROM voters")).fetchall()
        print(f"Total voters found: {len(voters)}")
        for v in voters:
            print(dict(v._mapping))

        print("\n==========================================")
        print("VOTER CREDENTIALS TABLE RECORDS")
        print("==========================================")
        creds = conn.execute(text("SELECT * FROM voter_credentials")).fetchall()
        print(f"Total voter_credentials found: {len(creds)}")
        for cr in creds:
            print(dict(cr._mapping))

        print("\n==========================================")
        print("AUDIT LOGS SUMMARY (Total count & recent)")
        print("==========================================")
        audit_count = conn.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar()
        print(f"Total audit logs: {audit_count}")
        recent_audits = conn.execute(text("SELECT id, event_type, rfid_uid, voter_id, status, details, timestamp FROM audit_logs ORDER BY id DESC LIMIT 5")).fetchall()
        for a in recent_audits:
            print(dict(a._mapping))

        print("\n==========================================")
        print("ADMIN USERS")
        print("==========================================")
        admin_users = conn.execute(text("SELECT id, username, full_name, role, is_active, created_at FROM admin_users")).fetchall()
        for u in admin_users:
            print(dict(u._mapping))

if __name__ == "__main__":
    inspect()

