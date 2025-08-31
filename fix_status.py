#!/usr/bin/env python3

from models.database import Database

def fix_status_values():
    db = Database()
    cursor = db.conn.cursor()
    
    print("Current status distribution:")
    cursor.execute('SELECT status, COUNT(*) FROM students GROUP BY status')
    status_counts = cursor.fetchall()
    for status, count in status_counts:
        print(f'  {status}: {count} records')
    
    print("\nUpdating status values...")
    
    # Update lowercase 'active' to 'Active'
    cursor.execute("UPDATE students SET status = 'Active' WHERE status = 'active'")
    active_updated = cursor.rowcount
    print(f"Updated {active_updated} records from 'active' to 'Active'")
    
    # Update 'inactive' to 'Drop' (since there's no 'Inactive' in the CHECK constraint)
    cursor.execute("UPDATE students SET status = 'Drop' WHERE status = 'inactive'")
    inactive_updated = cursor.rowcount
    print(f"Updated {inactive_updated} records from 'inactive' to 'Drop'")
    
    # Commit changes
    db.conn.commit()
    
    print("\nUpdated status distribution:")
    cursor.execute('SELECT status, COUNT(*) FROM students GROUP BY status')
    status_counts = cursor.fetchall()
    for status, count in status_counts:
        print(f'  {status}: {count} records')

if __name__ == "__main__":
    fix_status_values()
