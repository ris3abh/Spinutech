"""
File monitoring system for automatic detection and processing of reference files.
This module provides a watchdog-based system to detect new files and 
automatically add them to the knowledge base.
"""

import os
import time
import json
from typing import Dict, List, Set
from pathlib import Path
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from SEOoptimization.utils.enhanced_knowledge_base import EnhancedKnowledgeBase

class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system changes."""
    
    def __init__(self, kb: EnhancedKnowledgeBase):
        self.kb = kb
        self.supported_extensions = {'.txt', '.pdf', '.docx', '.doc'}
        self.known_files = set()
        self.processing_lock = threading.Lock()
        self.load_known_files()
    
    def load_known_files(self):
        """Load the list of already processed files."""
        if os.path.exists('.processed_files.json'):
            try:
                with open('.processed_files.json', 'r') as f:
                    self.known_files = set(json.load(f))
                print(f"Loaded {len(self.known_files)} known files from cache")
            except Exception as e:
                print(f"Error loading known files: {e}")
                self.known_files = set()
    
    def save_known_files(self):
        """Save the list of processed files."""
        try:
            with open('.processed_files.json', 'w') as f:
                json.dump(list(self.known_files), f)
        except Exception as e:
            print(f"Error saving known files: {e}")
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Ignore unsupported files and already processed files
        if file_ext not in self.supported_extensions:
            return
            
        if file_path in self.known_files:
            return
        
        # Acquire lock to prevent concurrent processing
        with self.processing_lock:
            if file_path in self.known_files:  # Check again with lock
                return
                
            print(f"New file detected: {file_path}")
            
            # Wait a moment to ensure file is completely written
            time.sleep(1)
            
            # Determine file type and ownership
            try:
                if '/users/' in file_path and '/style_reference/' in file_path:
                    # Extract specialist ID from path
                    parts = file_path.split('/users/')
                    if len(parts) > 1:
                        specialist_path = parts[1].split('/')
                        if len(specialist_path) > 0:
                            specialist_id = specialist_path[0]
                            print(f"Adding specialist reference file for {specialist_id}")
                            self.kb.add_documents(
                                [file_path],
                                document_type="specialist_reference",
                                owner_id=specialist_id
                            )
                
                elif '/clients/' in file_path and '/reference_content/' in file_path:
                    # Extract client ID and specialist ID
                    parts = file_path.split('/users/')
                    if len(parts) > 1:
                        user_path = parts[1].split('/')
                        if len(user_path) > 2 and 'clients' in user_path:
                            specialist_id = user_path[0]
                            client_idx = user_path.index('clients')
                            if len(user_path) > client_idx + 1:
                                client_id = user_path[client_idx + 1]
                                print(f"Adding client reference file for {client_id} (owner: {specialist_id})")
                                self.kb.add_documents(
                                    [file_path],
                                    document_type="client_reference",
                                    owner_id=specialist_id,
                                    client_id=client_id
                                )
                else:
                    print(f"Skipping file {file_path}: Not in a recognized directory structure")
                    return
                    
                # Mark file as processed
                self.known_files.add(file_path)
                self.save_known_files()
                
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_extensions:
            return
            
        # Treat modified files as new files
        if file_path in self.known_files:
            with self.processing_lock:
                self.known_files.remove(file_path)
                print(f"File modified, will reprocess: {file_path}")
            
        # Process the file as if it's new
        self.on_created(event)

class FileMonitor:
    """Monitor file system for changes and update knowledge base."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.kb = EnhancedKnowledgeBase()
        self.event_handler = FileChangeHandler(self.kb)
        self.observer = Observer()
        self._running = False
        self._monitor_thread = None
    
    def _run_monitoring(self):
        """Run the monitoring loop."""
        try:
            print(f"Started monitoring {self.data_dir} for file changes")
            # Initially scan for existing files
            self.scan_existing_files()
            
            # Keep the observer running
            while self._running:
                time.sleep(1)
        except Exception as e:
            print(f"Error in file monitoring: {e}")
        finally:
            self.observer.stop()
            self.observer.join()
            print("File monitoring stopped")
    
    def start(self):
        """Start monitoring files in a background thread."""
        if self._running:
            print("File monitor is already running")
            return
            
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Schedule the observer
        self.observer.schedule(self.event_handler, self.data_dir, recursive=True)
        self.observer.start()
        
        # Set running flag
        self._running = True
        
        # Start monitoring in a background thread
        self._monitor_thread = threading.Thread(
            target=self._run_monitoring,
            daemon=True  # Daemon thread will exit when main program exits
        )
        self._monitor_thread.start()
    
    def scan_existing_files(self):
        """Scan existing files not yet processed."""
        print("Scanning for existing files...")
        
        count = 0
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in self.event_handler.supported_extensions:
                    file_path = os.path.join(root, file)
                    if file_path not in self.event_handler.known_files:
                        # Create a file created event
                        event = FileCreatedEvent(file_path)
                        # Process this file
                        self.event_handler.on_created(event)
                        count += 1
        
        print(f"Initial file scan complete. Processed {count} new files.")
    
    def stop(self):
        """Stop monitoring files."""
        if not self._running:
            print("File monitor is not running")
            return
            
        self._running = False
        
        if self._monitor_thread:
            # Wait for thread to finish
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
            
        self.observer.stop()
        self.observer.join()
        print("File monitoring stopped")
    
    @property
    def is_running(self):
        """Check if the file monitor is running."""
        return self._running

# Singleton instance
_file_monitor = None

def get_file_monitor(data_dir: str = "data") -> FileMonitor:
    """Get or create the file monitor singleton instance."""
    global _file_monitor
    
    if _file_monitor is None:
        _file_monitor = FileMonitor(data_dir)
        
    return _file_monitor