/**
 * Tweet Source Attribution Interface
 */
export interface TweetSource {
    filename: string;
    relevance_score: number;
}

/**
 * Pipeline Statistics Interface
 */
export interface PipelineStats {
    articles_fetched: number;
    articles_scraped: number;
    chunks_created: number;
    vectors_stored: number;
    search_results: number;
}

/**
 * Tweet Response Interface
 * Matches the backend /tweets/generate endpoint response structure
 */
export interface TweetResponse {
    success: boolean;
    query: string;
    count: number;
    results: string[];
    sources: TweetSource[];
    pipeline_stats?: PipelineStats;
    error?: string;
}
