from fastapi import APIRouter, HTTPException, Query
from services.cleanup_service import cleanup_service
from services.pinecone_service import PineconeService
from services.emb_service import emb_service

router = APIRouter(prefix='/cleanup')

# Initialize services
embedder = None
pinecone_service = None
cleaner = None

try:
    # Initialize embedding service
    embedder = emb_service()
    print("✓ Embedding service initialized for cleanup")
    
    # Initialize Pinecone service
    pinecone_service = PineconeService(
        index_name="news-articles",
        dimension=embedder.get_dimension()
    )
    pinecone_service.get_index()
    print("✓ Pinecone service initialized for cleanup")
    
    # Initialize cleanup service
    cleaner = cleanup_service(folder="NEWS_data")
    print("✓ Cleanup service initialized")
    
except Exception as e:
    print(f"⚠ Warning: Could not initialize cleanup services: {e}")


@router.post("/")
def cleanup_all_data(confirm: bool = Query(False, description="Confirmation flag to prevent accidental deletion")):
    """
    Clean all data (NEWS_data folder and Pinecone vectors)
    
    Args:
        confirm (bool): Must be True to perform cleanup
        
    Returns:
        dict: Cleanup statistics
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Cleanup requires confirmation. Set confirm=true query parameter."
        )
    
    if cleaner is None or pinecone_service is None:
        raise HTTPException(
            status_code=503,
            detail="Cleanup services not available"
        )
    
    try:
        result = cleaner.cleanup_all(pinecone_service)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.post("/session/{session_id}")
def cleanup_session_data(
    session_id: str,
    confirm: bool = Query(False, description="Confirmation flag to prevent accidental deletion")
):
    """
    Clean data for a specific session
    
    Args:
        session_id (str): Session ID to clean
        confirm (bool): Must be True to perform cleanup
        
    Returns:
        dict: Cleanup statistics
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Cleanup requires confirmation. Set confirm=true query parameter."
        )
    
    if cleaner is None or pinecone_service is None:
        raise HTTPException(
            status_code=503,
            detail="Cleanup services not available"
        )
    
    try:
        result = cleaner.cleanup_session(pinecone_service, session_id)
        
        if result["folder_cleanup"]["deleted_count"] == 0 and result["pinecone_cleanup"].get("vectors_deleted", 0) == 0:
            return {
                **result,
                "warning": f"No data found for session '{session_id}'. It may have been already cleaned or doesn't exist."
            }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session cleanup failed: {str(e)}")


@router.get("/sessions")
def list_sessions():
    """
    List all available sessions
    
    Returns:
        dict: List of sessions with metadata
    """
    if cleaner is None:
        raise HTTPException(
            status_code=503,
            detail="Cleanup service not available"
        )
    
    try:
        sessions = cleaner.list_sessions()
        return {
            "success": True,
            "count": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/stats")
def get_cleanup_stats():
    """
    Get statistics about current state (files and vectors)
    
    Returns:
        dict: Statistics about files and Pinecone vectors
    """
    if cleaner is None:
        raise HTTPException(
            status_code=503,
            detail="Cleanup service not available"
        )
    
    try:
        stats = cleaner.get_stats(pinecone_service)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/folder")
def cleanup_folder_only(confirm: bool = Query(False, description="Confirmation flag")):
    """
    Clean only NEWS_data folder (keep Pinecone vectors)
    
    Args:
        confirm (bool): Must be True to perform cleanup
        
    Returns:
        dict: Cleanup statistics
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Cleanup requires confirmation. Set confirm=true query parameter."
        )
    
    if cleaner is None:
        raise HTTPException(
            status_code=503,
            detail="Cleanup service not available"
        )
    
    try:
        result = cleaner.cleanup_news_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Folder cleanup failed: {str(e)}")


@router.delete("/pinecone")
def cleanup_pinecone_only(confirm: bool = Query(False, description="Confirmation flag")):
    """
    Clean only Pinecone vectors (keep NEWS_data folder)
    
    Args:
        confirm (bool): Must be True to perform cleanup
        
    Returns:
        dict: Cleanup statistics
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Cleanup requires confirmation. Set confirm=true query parameter."
        )
    
    if cleaner is None or pinecone_service is None:
        raise HTTPException(
            status_code=503,
            detail="Cleanup services not available"
        )
    
    try:
        result = cleaner.cleanup_pinecone_all(pinecone_service)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone cleanup failed: {str(e)}")
