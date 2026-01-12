import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { TweetResponse } from "../models/tweet.model";
import { environment } from "../../../environments/environment";

@Injectable({
    providedIn: 'root'
})
export class TweetService {
    private readonly apiUrl = `${environment.apiBaseUrl}${environment.endpoints.tweets}`;

    constructor(private http: HttpClient) { }

    /**
     * Get tweets from the backend API
     * @param query - Topic or query to generate tweets about
     * @param count - Number of tweets to generate (default: 3, max: 10)
     * @param top_k - Number of articles to retrieve for context (default: 5, max: 10)
     * @param fetch_limit - Number of fresh articles to fetch (default: 10, max: 20)
     * @returns Observable of TweetResponse
     */
    getTweets(
        query: string,
        count: number = 3,
        top_k: number = 5,
        fetch_limit: number = 10
    ): Observable<TweetResponse> {
        return this.http.get<TweetResponse>(this.apiUrl, {
            params: {
                query: query,
                count: count,
                top_k: top_k,
                fetch_limit: fetch_limit
            }
        });
    }
}
