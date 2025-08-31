#!/usr/bin/env python3

from models.database import Database

def fix_database_schema():
    """Update the database schema to allow your exact status values."""
    db = Database()
    cursor = db.conn.cursor()
    
    print("Current database status constraint allows: 'active', 'inactive', 'transferred', 'graduated'")
    print("Updating to allow your exact status values: 'Active', 'Drop', 'Duplicate', 'Fail', 'Graduated'")
    
    try:
        # Since SQLite doesn't support ALTER TABLE to modify CHECK constraints easily,
        # we need to recreate the table. First, let's create a backup and recreate the table
        
        print("Creating new table with updated status constraints...")
        
        # Create a backup table
        cursor.execute("CREATE TABLE students_backup AS SELECT * FROM students")
        
        # Drop the original table
        cursor.execute("DROP TABLE students")
        
        # Recreate table with your status values
        cursor.execute('''CREATE TABLE students (
            -- Primary and System Fields
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Drop', 'Duplicate', 'Fail', 'Graduated')) NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            final_unique_codes TEXT NOT NULL,
            
            -- Organization and Location IDs
            org_id INTEGER NOT NULL,
            school_id INTEGER NOT NULL,
            province_id INTEGER NOT NULL,
            district_id INTEGER NOT NULL,
            union_council_id INTEGER NOT NULL,
            nationality_id INTEGER NOT NULL,
            
            -- School Information
            registration_number TEXT NOT NULL,
            class_teacher_name TEXT NOT NULL,
            
            -- Student Basic Information
            student_name TEXT NOT NULL,
            gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
            date_of_birth DATE NOT NULL,
            students_bform_number TEXT NOT NULL,
            year_of_admission DATE NOT NULL,
            year_of_admission_alt DATE NOT NULL,
            class TEXT CHECK(class IN ('Kachi', 'Paki', '1', '2', '3', '4', '5')) NOT NULL,
            section TEXT CHECK(section IN ('A', 'B', 'C', 'D', 'E', 'F')) NOT NULL,
            address TEXT NOT NULL,
            
            -- Father Information
            father_name TEXT NOT NULL,
            father_cnic TEXT NOT NULL,
            father_phone TEXT NOT NULL,
            
            -- Household Information
            household_size INTEGER NOT NULL,
            
            -- Mother Information
            mother_name TEXT NOT NULL,
            mother_date_of_birth DATE NOT NULL,
            mother_marital_status TEXT CHECK(mother_marital_status IN ('Single', 'Married', 'Divorced', 'Widowed', 'Free union', 'Separated', 'Engaged')) NOT NULL,
            mother_id_type TEXT NOT NULL,
            mother_cnic TEXT NOT NULL,
            mother_cnic_doi DATE NOT NULL,
            mother_cnic_exp DATE NOT NULL,
            mother_mwa INTEGER NOT NULL,
            
            -- Household Head Information
            household_role TEXT CHECK(household_role IN ('Head', 'Son', 'Daughter', 'Wife', 'Husband', 'Brother', 'Sister', 'Mother', 'Father', 'Aunt', 'Uncle', 'Grand Mother', 'Grand Father', 'Mother-in-Law', 'Father-in-Law', 'Daughter-in-Law', 'Son-in-Law', 'Sister-in-Law', 'Brother-in-Law', 'Grand Daughter', 'Grand Son', 'Nephew', 'Niece', 'Cousin', 'Other', 'Not Member')) NOT NULL,
            household_name TEXT NOT NULL,
            hh_gender TEXT CHECK(hh_gender IN ('Male', 'Female', 'Other')) NOT NULL,
            hh_date_of_birth DATE NOT NULL,
            recipient_type TEXT CHECK(recipient_type IN ('Principal', 'Alternate')) NOT NULL,
            
            -- Alternate/Guardian Information (Optional fields)
            alternate_name TEXT,
            alternate_date_of_birth DATE,
            alternate_marital_status TEXT CHECK(alternate_marital_status IN ('Single', 'Married', 'Divorced', 'Widowed', 'Free union', 'Separated', 'Engaged')),
            alternate_id_type TEXT,
            alternate_cnic TEXT,
            alternate_cnic_doi DATE,
            alternate_cnic_exp DATE,
            alternate_mwa INTEGER,
            alternate_relationship_with_mother TEXT CHECK(alternate_relationship_with_mother IN ('Head', 'Son', 'Daughter', 'Wife', 'Husband', 'Brother', 'Sister', 'Mother', 'Father', 'Aunt', 'Uncle', 'Grand Mother', 'Grand Father', 'Mother-in-Law', 'Father-in-Law', 'Daughter-in-Law', 'Son-in-Law', 'Sister-in-Law', 'Brother-in-Law', 'Grand Daughter', 'Grand Son', 'Nephew', 'Niece', 'Cousin', 'Other', 'Not Member')),
            
            -- Enhanced Audit and System Fields
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            created_by_username TEXT,
            updated_by_username TEXT,
            created_by_phone TEXT,
            updated_by_phone TEXT,
            version INTEGER DEFAULT 1,
            is_deleted INTEGER DEFAULT 0 NOT NULL,
            deleted_at TIMESTAMP,
            deleted_by TEXT,
            deleted_by_username TEXT,
            deleted_by_phone TEXT,
            class_name TEXT
        )''')
        
        # Copy data back from backup, converting status values
        cursor.execute("""
            INSERT INTO students 
            SELECT 
                id, 
                CASE 
                    WHEN status = 'active' THEN 'Active'
                    WHEN status = 'inactive' THEN 'Duplicate'
                    WHEN status = 'transferred' THEN 'Drop'
                    WHEN status = 'graduated' THEN 'Graduated'
                    ELSE 'Active'
                END as status,
                student_id, final_unique_codes, org_id, school_id, province_id, district_id, union_council_id, nationality_id,
                registration_number, class_teacher_name, student_name, gender, date_of_birth, students_bform_number,
                year_of_admission, year_of_admission_alt, class, section, address, father_name, father_cnic, father_phone,
                household_size, mother_name, mother_date_of_birth, mother_marital_status, mother_id_type, mother_cnic,
                mother_cnic_doi, mother_cnic_exp, mother_mwa, household_role, household_name, hh_gender, hh_date_of_birth,
                recipient_type, alternate_name, alternate_date_of_birth, alternate_marital_status, alternate_id_type,
                alternate_cnic, alternate_cnic_doi, alternate_cnic_exp, alternate_mwa, alternate_relationship_with_mother,
                created_at, updated_at, created_by, updated_by, created_by_username, updated_by_username,
                created_by_phone, updated_by_phone, version, is_deleted, deleted_at, deleted_by, deleted_by_username,
                deleted_by_phone, class_name
            FROM students_backup
        """)
        
        # Drop backup table
        cursor.execute("DROP TABLE students_backup")
        
        # Commit changes
        db.conn.commit()
        
        print("✅ Database schema updated successfully!")
        print("Status constraint now allows: 'Active', 'Drop', 'Duplicate', 'Fail', 'Graduated'")
        
        # Show current status distribution
        cursor.execute('SELECT status, COUNT(*) FROM students GROUP BY status')
        status_counts = cursor.fetchall()
        print("\nCurrent status distribution:")
        for status, count in status_counts:
            print(f'  {status}: {count} records')
            
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        db.conn.rollback()

if __name__ == "__main__":
    fix_database_schema()
