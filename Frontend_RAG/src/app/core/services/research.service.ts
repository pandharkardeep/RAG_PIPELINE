import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface TrendingTopic {
    topic: string;
    source: string;
    score: number;
    context?: string;
}

export interface ContentIdea {
    title: string;
    description: string;
    pain_point?: string;
    target_audience?: string;
    content_type: string;
    confidence_score: number;
    sources: string[];
}

export interface ResearchReport {
    niche: string;
    trending_topics: TrendingTopic[];
    content_ideas: ContentIdea[];
    pain_points: string[];
    questions: string[];
    stats: { [key: string]: any };
}

export interface ResearchResponse {
    success: boolean;
    report?: ResearchReport;
    message: string;
}

export interface ResearchRequest {
    niche: string;
    subreddits?: string[];
    days?: number;
    idea_count?: number;
}

@Injectable({
    providedIn: 'root'
})
export class ResearchService {
    private baseUrl = `${environment.apiBaseUrl}/research`;

    constructor(private http: HttpClient) { }

    /**
     * Run full research pipeline for a niche
     */
    analyzeNiche(request: ResearchRequest): Observable<ResearchResponse> {
        return this.http.post<ResearchResponse>(`${this.baseUrl}/analyze`, request);
    }

    /**
     * Get trending topics for a niche (quick)
     */
    getTrending(niche: string, limit: number = 20): Observable<{ success: boolean; trending: TrendingTopic[] }> {
        return this.http.get<{ success: boolean; trending: TrendingTopic[] }>(
            `${this.baseUrl}/trending/${encodeURIComponent(niche)}?limit=${limit}`
        );
    }

    /**
     * Get quick content ideas based on trends
     */
    getQuickIdeas(niche: string, count: number = 10): Observable<{ success: boolean; ideas: ContentIdea[] }> {
        return this.http.get<{ success: boolean; ideas: ContentIdea[] }>(
            `${this.baseUrl}/quick-ideas/${encodeURIComponent(niche)}?count=${count}`
        );
    }
}
