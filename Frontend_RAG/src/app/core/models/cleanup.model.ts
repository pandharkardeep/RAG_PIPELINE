/**
 * Cleanup Response Models
 */

export interface CleanupStats {
    folder: string;
    folder_exists: boolean;
    file_count: number;
    files: string[];
    sessions: SessionInfo[];
    pinecone?: {
        total_vectors: number;
        index_fullness: number;
        dimension: number;
        error?: string;
    };
}

export interface SessionInfo {
    session_id: string;
    query: string;
    timestamp: number;
    article_count: number;
    files: string[];
}

export interface FolderCleanupResult {
    success: boolean;
    deleted_count: number;
    deleted_files: string[];
    errors: string[];
    session_id?: string;
    message?: string;
    timestamp: string;
}

export interface PineconeCleanupResult {
    success: boolean;
    vectors_deleted: number;
    vectors_before: number;
    vectors_after: number;
    session_id?: string;
    error?: string;
    timestamp: string;
}

export interface CleanupResponse {
    success: boolean;
    folder_cleanup: FolderCleanupResult;
    pinecone_cleanup: PineconeCleanupResult;
    session_id?: string;
    timestamp: string;
    warning?: string;
}

export interface StatsResponse {
    success: boolean;
    stats: CleanupStats;
}

export interface SessionsResponse {
    success: boolean;
    count: number;
    sessions: SessionInfo[];
}
