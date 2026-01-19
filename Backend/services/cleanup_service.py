import os
import shutil
import json
from datetime import datetime
from services.pinecone_service import PineconeService


class cleanup_service:
    def __init__(self, folder="NEWS_data"):
        self.folder = folder
    
    def cleanup_news_data(self):
        """
        Clean all files from NEWS_data folder
        
        Returns:
            dict: Statistics about cleanup operation
        """
        deleted_files = []
        errors = []
        
        if not os.path.exists(self.folder):
            return {
                "success": True,
                "deleted_count": 0,
                "deleted_files": [],
                "errors": [],
                "message": f"Folder '{self.folder}' does not exist"
            }
        
        for filename in os.listdir(self.folder):
            file_path = os.path.join(self.folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    deleted_files.append(filename)
                    print(f"✓ Deleted: {filename}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    deleted_files.append(filename)
                    print(f"✓ Deleted directory: {filename}")
            except Exception as e:
                error_msg = f"Failed to delete {filename}: {str(e)}"
                errors.append(error_msg)
                print(f"✗ {error_msg}")
        
        return {
            "success": len(errors) == 0,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }

    def cleanup_news_data_by_session(self, session_id):
        """
        Clean files from NEWS_data folder for a specific session
        
        Args:
            session_id (str): Session ID to clean
            
        Returns:
            dict: Statistics about cleanup operation
        """
        deleted_files = []
        errors = []
        
        if not os.path.exists(self.folder):
            return {
                "success": True,
                "deleted_count": 0,
                "deleted_files": [],
                "errors": [],
                "message": f"Folder '{self.folder}' does not exist"
            }
        
        for filename in os.listdir(self.folder):
            # Match files with session_id prefix (e.g., session_abc123_description_1.txt or session_abc123.json)
            if filename.startswith(f"session_{session_id}") or filename.startswith(f"{session_id}_"):
                file_path = os.path.join(self.folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        deleted_files.append(filename)
                        print(f"✓ Deleted session file: {filename}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        deleted_files.append(filename)
                        print(f"✓ Deleted session directory: {filename}")
                except Exception as e:
                    error_msg = f"Failed to delete {filename}: {str(e)}"
                    errors.append(error_msg)
                    print(f"✗ {error_msg}")
        
        return {
            "success": len(errors) == 0,
            "session_id": session_id,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }

    def cleanup_pinecone_all(self, pinecone_service: PineconeService):
        """
        Delete all vectors from Pinecone index
        
        Args:
            pinecone_service (PineconeService): Instance of PineconeService
            
        Returns:
            dict: Statistics about cleanup operation
        """
        try:
            stats_before = pinecone_service.get_stats()
            vector_count_before = stats_before.get('total_vector_count', 0)
            
            pinecone_service.delete_all()
            
            stats_after = pinecone_service.get_stats()
            vector_count_after = stats_after.get('total_vector_count', 0)
            
            print(f"✓ Deleted {vector_count_before - vector_count_after} vectors from Pinecone")
            
            return {
                "success": True,
                "vectors_deleted": vector_count_before - vector_count_after,
                "vectors_before": vector_count_before,
                "vectors_after": vector_count_after,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"Failed to delete Pinecone vectors: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }

    def cleanup_pinecone_by_session(self, pinecone_service: PineconeService, session_id: str):
        """
        Delete vectors from Pinecone for a specific session
        
        Args:
            pinecone_service (PineconeService): Instance of PineconeService
            session_id (str): Session ID to clean
            
        Returns:
            dict: Statistics about cleanup operation
        """
        try:
            stats_before = pinecone_service.get_stats()
            vector_count_before = stats_before.get('total_vector_count', 0)
            
            # Delete vectors by metadata filter (session_id)
            deleted_count = pinecone_service.delete_by_metadata_filter({"session_id": session_id})
            
            stats_after = pinecone_service.get_stats()
            vector_count_after = stats_after.get('total_vector_count', 0)
            
            print(f"✓ Deleted {deleted_count} vectors for session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "vectors_deleted": deleted_count,
                "vectors_before": vector_count_before,
                "vectors_after": vector_count_after,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"Failed to delete Pinecone vectors for session {session_id}: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "success": False,
                "session_id": session_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_all(self, pinecone_service: PineconeService):
        """
        Comprehensive cleanup of both NEWS_data folder and Pinecone vectors
        
        Args:
            pinecone_service (PineconeService): Instance of PineconeService
            
        Returns:
            dict: Combined statistics from both cleanup operations
        """
        print(f"\n{'='*60}")
        print("Starting comprehensive cleanup...")
        print(f"{'='*60}\n")
        
        # Clean NEWS_data folder
        print("[1/2] Cleaning NEWS_data folder...")
        folder_result = self.cleanup_news_data()
        
        # Clean Pinecone vectors
        print("\n[2/2] Cleaning Pinecone vectors...")
        pinecone_result = self.cleanup_pinecone_all(pinecone_service)
        
        print(f"\n{'='*60}")
        print("Cleanup completed!")
        print(f"{'='*60}\n")
        
        return {
            "success": folder_result["success"] and pinecone_result["success"],
            "folder_cleanup": folder_result,
            "pinecone_cleanup": pinecone_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup_session(self, pinecone_service: PineconeService, session_id: str):
        """
        Cleanup both NEWS_data and Pinecone for a specific session
        
        Args:
            pinecone_service (PineconeService): Instance of PineconeService
            session_id (str): Session ID to clean
            
        Returns:
            dict: Combined statistics from both cleanup operations
        """
        print(f"\n{'='*60}")
        print(f"Cleaning session: {session_id}")
        print(f"{'='*60}\n")
        
        # Clean NEWS_data folder for session
        print("[1/2] Cleaning NEWS_data files for session...")
        folder_result = self.cleanup_news_data_by_session(session_id)
        
        # Clean Pinecone vectors for session
        print("\n[2/2] Cleaning Pinecone vectors for session...")
        pinecone_result = self.cleanup_pinecone_by_session(pinecone_service, session_id)
        
        print(f"\n{'='*60}")
        print(f"Session cleanup completed!")
        print(f"{'='*60}\n")
        
        return {
            "success": folder_result["success"] and pinecone_result["success"],
            "session_id": session_id,
            "folder_cleanup": folder_result,
            "pinecone_cleanup": pinecone_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def list_sessions(self):
        """
        List all sessions by reading session manifest files
        
        Returns:
            list: List of session metadata
        """
        sessions = []
        
        if not os.path.exists(self.folder):
            return sessions
        
        for filename in os.listdir(self.folder):
            if filename.startswith("session_") and filename.endswith(".json"):
                file_path = os.path.join(self.folder, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except Exception as e:
                    print(f"⚠ Failed to read session file {filename}: {str(e)}")
        
        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return sessions
    
    def get_stats(self, pinecone_service: PineconeService = None):
        """
        Get statistics about current state (files and vectors)
        
        Args:
            pinecone_service (PineconeService, optional): Instance of PineconeService
            
        Returns:
            dict: Statistics about files and vectors
        """
        stats = {
            "folder": self.folder,
            "folder_exists": os.path.exists(self.folder),
            "file_count": 0,
            "files": [],
            "sessions": []
        }
        
        if os.path.exists(self.folder):
            files = os.listdir(self.folder)
            stats["file_count"] = len(files)
            stats["files"] = files
            stats["sessions"] = self.list_sessions()
        
        if pinecone_service:
            try:
                pinecone_stats = pinecone_service.get_stats()
                stats["pinecone"] = {
                    "total_vectors": pinecone_stats.get('total_vector_count', 0),
                    "index_fullness": pinecone_stats.get('index_fullness', 0),
                    "dimension": pinecone_stats.get('dimension', 0)
                }
            except Exception as e:
                stats["pinecone"] = {
                    "error": str(e)
                }
        
        return stats
