#!/usr/bin/env python3
"""
Demo script for AccuDoc Data Management features:
- Memory Optimization
- Progress Resume
- Project Database
- Comparison History

This script demonstrates how to use the new data management features.
"""

import sys
import tempfile
import shutil
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.memory_optimizer import MemoryOptimizer, StreamingDataCollector, optimize_for_large_repo, get_system_resources
from accudoc.progress_manager import ProgressManager
from accudoc.project_database import ProjectDatabase
from accudoc.comparison_history import ComparisonHistory


def demo_memory_optimization():
    """Demonstrate memory optimization features."""
    print("=" * 60)
    print("DEMO: Memory Optimization")
    print("=" * 60)
    print()
    
    optimizer = MemoryOptimizer(max_memory_mb=512)
    
    print("1. Getting memory usage:")
    usage = optimizer.get_memory_usage()
    for key, value in usage.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    print()
    
    print("2. Optimizing memory:")
    result = optimizer.optimize()
    print(f"   Before: {result['before_mb']:.2f} MB")
    print(f"   After: {result['after_mb']:.2f} MB")
    print(f"   Freed: {result['freed_mb']:.2f} MB")
    print(f"   Objects collected: {result['objects_collected']}")
    print()
    
    print("3. Streaming file processing:")
    test_dir = tempfile.mkdtemp()
    try:
        test_file = Path(test_dir) / 'large.txt'
        test_file.write_text('\n'.join([f'Line {i}' for i in range(1000)]))
        
        line_count = 0
        for line in optimizer.stream_file_lines(test_file):
            line_count += 1
            if line_count > 5:
                break
            print(f"   {line}")
        
        print(f"   ... (streaming 1000 lines efficiently)")
        print()
    finally:
        shutil.rmtree(test_dir)
    
    print("4. System resources:")
    resources = get_system_resources()
    print(f"   CPU count: {resources.get('cpu_count', 'N/A')}")
    print(f"   CPU usage: {resources.get('cpu_percent', 0):.1f}%")
    if 'total_memory_mb' in resources and resources['total_memory_mb'] > 0:
        print(f"   Total memory: {resources['total_memory_mb']:.0f} MB")
        print(f"   Available: {resources['available_memory_mb']:.0f} MB")
    print()
    
    print("✅ Memory optimization demo completed!\n")


def demo_progress_resume():
    """Demonstrate progress resume features."""
    print("=" * 60)
    print("DEMO: Progress Resume")
    print("=" * 60)
    print()
    
    test_dir = tempfile.mkdtemp()
    try:
        checkpoint_dir = Path(test_dir) / 'checkpoints'
        manager = ProgressManager(checkpoint_dir)
        
        repo_path = '/demo/repository'
        
        print("1. Creating checkpoint for scan:")
        checkpoint = manager.create_checkpoint(repo_path, {
            'template': 'default',
            'output_format': 'markdown'
        })
        print(f"   Checkpoint ID: {checkpoint['checkpoint_id']}")
        print(f"   Status: {checkpoint['status']}")
        print()
        
        print("2. Simulating file processing:")
        checkpoint['statistics']['total_files'] = 100
        
        for i in range(10):
            manager.update_progress(f'/demo/file{i}.py', success=True)
        
        for i in range(2):
            manager.update_progress(f'/demo/error{i}.py', success=False)
        
        print(f"   Processed: {manager.current_checkpoint['statistics']['processed']}")
        print(f"   Failed: {manager.current_checkpoint['statistics']['failed']}")
        print(f"   Progress: {manager.get_progress_percentage():.1f}%")
        print()
        
        print("3. Can resume check:")
        can_resume = manager.can_resume(repo_path)
        print(f"   Can resume: {can_resume}")
        print()
        
        print("4. Progress report:")
        report = manager.generate_progress_report()
        print(report[:400] + "...")
        print()
        
        print("5. Marking checkpoint complete:")
        manager.mark_complete()
        print(f"   Status: {manager.current_checkpoint['status']}")
        print()
        
    finally:
        shutil.rmtree(test_dir)
    
    print("✅ Progress resume demo completed!\n")


def demo_project_database():
    """Demonstrate project database features."""
    print("=" * 60)
    print("DEMO: Project Database")
    print("=" * 60)
    print()
    
    test_dir = tempfile.mkdtemp()
    try:
        db_path = Path(test_dir) / 'accudoc.db'
        
        with ProjectDatabase(db_path) as db:
            print("1. Adding projects:")
            project1_id = db.add_project('/demo/project1', name='Demo Project 1')
            project2_id = db.add_project('/demo/project2', name='Demo Project 2')
            print(f"   Project 1 ID: {project1_id}")
            print(f"   Project 2 ID: {project2_id}")
            print()
            
            print("2. Adding scans:")
            for i in range(3):
                scan_data = {
                    'duration_seconds': 10.0 + i,
                    'files_scanned': 50 + i * 10,
                    'files_changed': 5 + i,
                    'status': 'complete',
                    'config': {'template': 'default'},
                    'results': {'loc': 1000 + i * 100}
                }
                scan_id = db.add_scan(project1_id, scan_data)
                print(f"   Scan {i+1}: {scan_id}")
                time.sleep(0.01)  # Small delay for different timestamps
            print()
            
            print("3. Listing projects:")
            projects = db.list_projects()
            for proj in projects:
                print(f"   - {proj['name']} (scans: {proj['scan_count']})")
            print()
            
            print("4. Getting scan history:")
            scans = db.get_scans(project1_id, limit=5)
            print(f"   Total scans: {len(scans)}")
            for scan in scans[:3]:
                print(f"   - {scan['scanned_at'][:19]}: {scan['files_scanned']} files")
            print()
            
            print("5. Adding comparison:")
            if len(scans) >= 2:
                changes = {
                    'files_added': 10,
                    'files_removed': 2,
                    'files_modified': 5
                }
                comparison_id = db.add_comparison(
                    project1_id,
                    scans[1]['scan_id'],
                    scans[0]['scan_id'],
                    changes
                )
                print(f"   Comparison ID: {comparison_id}")
            print()
            
            print("6. Exporting project data:")
            export_file = Path(test_dir) / 'export.json'
            db.export_project_data(project1_id, export_file)
            print(f"   Exported to: {export_file}")
            print(f"   File size: {export_file.stat().st_size} bytes")
            print()
        
    finally:
        shutil.rmtree(test_dir)
    
    print("✅ Project database demo completed!\n")


def demo_comparison_history():
    """Demonstrate comparison history features."""
    print("=" * 60)
    print("DEMO: Comparison History")
    print("=" * 60)
    print()
    
    test_dir = tempfile.mkdtemp()
    try:
        db_path = Path(test_dir) / 'accudoc.db'
        
        with ProjectDatabase(db_path) as db:
            history = ComparisonHistory(db)
            
            print("1. Setting up project with scan history:")
            project_id = db.add_project('/demo/evolving-repo', name='Evolving Project')
            
            # Add multiple scans showing evolution
            for i in range(5):
                scan_data = {
                    'duration_seconds': 8.0 + i * 0.5,
                    'files_scanned': 100 + i * 15,
                    'files_changed': 5 + i * 2,
                    'status': 'complete',
                    'results': {
                        'loc': 5000 + i * 500,
                        'complexity': 100 + i * 10
                    }
                }
                db.add_scan(project_id, scan_data)
                time.sleep(0.01)
            
            print(f"   Created 5 scans for tracking evolution")
            print()
            
            print("2. Tracking evolution of files_scanned:")
            evolution = history.track_evolution(project_id, 'files_scanned')
            print(f"   Metric: {evolution['metric']}")
            print(f"   Data points: {len(evolution['data_points'])}")
            print(f"   Trend: {evolution.get('trend', 'unknown')}")
            print(f"   First value: {evolution['data_points'][0]['value']}")
            print(f"   Last value: {evolution['data_points'][-1]['value']}")
            print()
            
            print("3. Comparing first and last scan:")
            scans = db.get_scans(project_id)
            if len(scans) >= 2:
                comparison = history.compare_scans(scans[-1], scans[0])
                print("   Changes detected:")
                for metric, data in comparison['changes'].items():
                    print(f"   - {metric}:")
                    print(f"     Before: {data['before']}")
                    print(f"     After: {data['after']}")
                    print(f"     Change: {data['delta']:+} ({data['percent_change']:+.1f}%)")
            print()
            
            print("4. Statistics summary:")
            summary = history.get_statistics_summary(project_id)
            if 'total_scans' in summary:
                print(f"   Total scans: {summary['total_scans']}")
                print(f"   Files scanned (avg): {summary['files_scanned']['avg']:.1f}")
                print(f"   Scan duration (avg): {summary['scan_duration']['avg']:.1f}s")
            print()
            
            print("5. Evolution report:")
            report = history.generate_evolution_report(project_id)
            print(report[:500] + "...")
            print()
            
            print("6. Detecting regressions:")
            # Add a scan with regression
            regression_scan = {
                'duration_seconds': 15.0,  # Much longer
                'files_scanned': 80,  # Fewer files
                'status': 'complete'
            }
            db.add_scan(project_id, regression_scan)
            
            regressions = history.find_regressions(project_id, threshold=10.0)
            if regressions:
                print(f"   Found {len(regressions)} regression(s):")
                for reg in regressions[:3]:
                    print(f"   - {reg['metric']}: {reg['change_percent']:+.1f}%")
            else:
                print("   No significant regressions detected")
            print()
        
    finally:
        shutil.rmtree(test_dir)
    
    print("✅ Comparison history demo completed!\n")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("AccuDoc Data Management Features Demonstration")
    print("=" * 60)
    print()
    
    try:
        demo_memory_optimization()
        demo_progress_resume()
        demo_project_database()
        demo_comparison_history()
        
        print("=" * 60)
        print("All Demonstrations Completed Successfully! ✅")
        print("=" * 60)
        print()
        print("Summary of new features:")
        print("  1. ✅ Memory Optimization - Efficient handling of large repositories")
        print("  2. ✅ Progress Resume - Continue interrupted scans from checkpoints")
        print("  3. ✅ Project Database - SQLite storage for scan results")
        print("  4. ✅ Comparison History - Track repository evolution over time")
        print()
        print("For more details, see:")
        print("  - accudoc/memory_optimizer.py (memory management)")
        print("  - accudoc/progress_manager.py (checkpoint management)")
        print("  - accudoc/project_database.py (SQLite database)")
        print("  - accudoc/comparison_history.py (evolution tracking)")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
