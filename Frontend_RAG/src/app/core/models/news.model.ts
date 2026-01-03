export interface NewsArticle {
    title: string;
    url: string;
    category: string;
}

export interface NewsResponse {
    status: boolean;
    request_id?: string;
    data: NewsArticle[];
}

export interface NewsSummary {
    summary_text: string;
}
