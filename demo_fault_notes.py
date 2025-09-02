"""
Demo script to test fault search and notes functionality
This simulates the key functionality without requiring the GUI
"""

import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_notes_manager import FaultNotesManager
from unified_parser import UnifiedParser


def demo_fault_search_with_notes():
    """Demonstrate the fault search and notes functionality"""
    print("🔍 HAL Fault Search and Notes Demo")
    print("=" * 50)
    
    try:
        # Initialize components
        print("📊 Initializing components...")
        fault_parser = UnifiedParser()
        notes_manager = FaultNotesManager()
        
        # Load fault codes (simulate what the application does)
        print("📋 Loading fault code databases...")
        hal_fault_path = os.path.join(os.path.dirname(__file__), 'data', 'HALfault.txt')
        tb_fault_path = os.path.join(os.path.dirname(__file__), 'data', 'TBFault.txt')
        
        hal_loaded = False
        tb_loaded = False
        
        if os.path.exists(hal_fault_path):
            hal_loaded = fault_parser.load_fault_codes_from_file(hal_fault_path, 'hal')
            print(f"  ✓ HAL fault codes: {'loaded' if hal_loaded else 'failed'}")
        else:
            print(f"  ⚠️ HAL fault file not found: {hal_fault_path}")
            
        if os.path.exists(tb_fault_path):
            tb_loaded = fault_parser.load_fault_codes_from_file(tb_fault_path, 'tb')
            print(f"  ✓ TB fault codes: {'loaded' if tb_loaded else 'failed'}")
        else:
            print(f"  ⚠️ TB fault file not found: {tb_fault_path}")
        
        # Get statistics
        stats = fault_parser.get_fault_code_statistics()
        print(f"  📈 Total fault codes loaded: {stats['total_codes']}")
        print(f"  📂 Sources: {', '.join(stats['sources'])}")
        
        # Test fault code search functionality
        print("\n🔍 Testing Fault Code Search...")
        test_codes = ["400027", "251330", "313211", "999999"]  # Last one doesn't exist
        
        for code in test_codes:
            print(f"\n🔍 Searching for fault code: {code}")
            result = fault_parser.search_fault_code(code)
            
            if result['found']:
                print(f"  ✅ Found: {result['code']}")
                print(f"  📋 Database: {result.get('database_description', 'Unknown')}")
                print(f"  📝 Description: {result['description'][:100]}...")
                
                # Test notes functionality
                print(f"  📝 Checking existing note...")
                existing_note = notes_manager.get_note(code)
                if existing_note:
                    print(f"    📌 Existing note: {existing_note['note'][:50]}...")
                    print(f"    👤 Author: {existing_note.get('author', 'Unknown')}")
                else:
                    print(f"    📌 No existing note")
                    # Add a demo note
                    demo_note = f"Demo note for fault code {code} - automatically added during testing"
                    success = notes_manager.save_note(code, demo_note, "DemoUser")
                    if success:
                        print(f"    ✅ Demo note added successfully")
                    else:
                        print(f"    ❌ Failed to add demo note")
            else:
                print(f"  ❌ Fault code {code} not found")
        
        # Test description search
        print(f"\n🔍 Testing Description Search...")
        search_terms = ["COL", "temperature", "voltage"]
        
        for term in search_terms:
            print(f"\n🔍 Searching descriptions for: '{term}'")
            results = fault_parser.search_description(term)
            print(f"  📊 Found {len(results)} matching fault codes")
            
            # Show first few results
            for i, (fault_code, fault_data) in enumerate(results[:3]):
                source = fault_data.get('source', 'unknown')
                db_name = 'HAL' if source == 'uploaded' else 'TB' if source == 'tb' else source.upper()
                description = fault_data.get('description', 'No description')[:60]
                print(f"    {i+1}. {fault_code} ({db_name}): {description}...")
        
        # Show notes summary
        print(f"\n📋 Notes Summary:")
        all_notes = notes_manager.get_all_notes()
        print(f"  📊 Total notes: {len(all_notes)}")
        
        for fault_code, note_data in all_notes.items():
            note_preview = note_data['note'][:40] + "..." if len(note_data['note']) > 40 else note_data['note']
            print(f"    📌 {fault_code}: {note_preview}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"   💾 Notes are saved to: {notes_manager.notes_file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_fault_search_with_notes()
    print(f"\n{'✅ Demo completed successfully!' if success else '❌ Demo failed'}")
    sys.exit(0 if success else 1)