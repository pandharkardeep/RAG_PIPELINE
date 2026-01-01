export interface NewsArticle {
    title: string;
    link: string;
    snippet?: string;
    photo_url?: string;
    published_datetime_utc?: string;
    source_name?: string;
    source_logo_url?: string;
}

export interface NewsResponse {
    status: string;
    request_id?: string;
    data: NewsArticle[];
}
