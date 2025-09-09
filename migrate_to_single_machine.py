#!/usr/bin/env python3
"""
Data Migration Utility for Single-Machine Database Architecture
Converts existing combined database to separate per-machine databases.

Usage:
    python3 migrate_to_single_machine.py [--source-db PATH] [--dry-run]

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from single_machine_database import SingleMachineDatabaseManager


def main():
    parser = argparse.ArgumentParser(description='Migrate HALog data to single-machine architecture')
    parser.add_argument('--source-db', help='Path to source combined database', 
                       default='data/database/halog_water.db')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be migrated without actually doing it')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing machine databases')
    
    args = parser.parse_args()
    
    print("🚀 HALog Single-Machine Database Migration Utility")
    print("=" * 60)
    
    # Check if source database exists
    if not os.path.exists(args.source_db):
        print(f"❌ Source database not found: {args.source_db}")
        return 1
    
    # Initialize managers
    print(f"📂 Source database: {args.source_db}")
    source_db = DatabaseManager(args.source_db)
    single_machine_db = SingleMachineDatabaseManager()
    
    # Discover machines in source database
    print("\n🔍 Discovering machines in source database...")
    try:
        with source_db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT DISTINCT serial_number, COUNT(*) as record_count
                FROM water_logs 
                WHERE serial_number IS NOT NULL 
                AND serial_number != ''
                AND serial_number != 'Unknown'
                GROUP BY serial_number
                ORDER BY serial_number
            """)
            machines_data = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error reading source database: {e}")
        return 1
    
    if not machines_data:
        print("⚠️  No machines found in source database")
        return 0
    
    print(f"✅ Found {len(machines_data)} machines:")
    for machine_id, record_count in machines_data:
        print(f"  - {machine_id}: {record_count:,} records")
    
    # Check for existing machine databases
    print("\n📋 Checking for existing machine databases...")
    existing_machines = single_machine_db.discover_available_machines()
    if existing_machines and not args.force:
        print(f"⚠️  Found {len(existing_machines)} existing machine databases:")
        for machine_id in existing_machines:
            print(f"  - {machine_id}")
        print("Use --force to overwrite existing databases")
        if not args.dry_run:
            return 1
    
    # Migration plan
    print(f"\n📋 Migration Plan:")
    if args.dry_run:
        print("   (DRY RUN - no changes will be made)")
    
    total_records = sum(count for _, count in machines_data)
    print(f"   Total records to migrate: {total_records:,}")
    
    for machine_id, record_count in machines_data:
        db_path = single_machine_db.get_machine_database_path(machine_id)
        exists = os.path.exists(db_path)
        status = "EXISTS" if exists else "NEW"
        if exists and args.force:
            status = "OVERWRITE"
        print(f"   - {machine_id}: {record_count:,} records → {status}")
    
    if args.dry_run:
        print("\n✅ Dry run completed. Use without --dry-run to perform migration.")
        return 0
    
    # Confirm migration
    print(f"\n❓ Proceed with migration? (y/N): ", end="")
    try:
        response = input().strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return 0
    except KeyboardInterrupt:
        print("\nMigration cancelled.")
        return 0
    
    # Perform migration
    print("\n🔄 Starting migration...")
    migration_results = single_machine_db.migrate_all_machines(args.source_db)
    
    # Summary
    successful = sum(1 for success in migration_results.values() if success)
    failed = len(migration_results) - successful
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    
    if failed > 0:
        print(f"\n❌ Failed migrations:")
        for machine_id, success in migration_results.items():
            if not success:
                print(f"   - {machine_id}")
    
    if successful > 0:
        print(f"\n🎉 Successfully migrated {successful} machines to single-machine architecture!")
        print(f"   Machine databases created in: data/database/machines/")
        
        # Recommend backup of original
        print(f"\n💡 Recommendation:")
        print(f"   Consider backing up original database: {args.source_db}")
        print(f"   You can now use the new single-machine architecture for faster loading.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)