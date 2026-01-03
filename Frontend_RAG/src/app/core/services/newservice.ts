import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { NewsResponse, NewsSummary } from "../models/news.model";
import { environment } from "../../../environments/environment";

@Injectable({
    providedIn: 'root'
})
export class NewsService {
    private readonly apiUrl = `${environment.apiBaseUrl}${environment.endpoints.articles}`;

    constructor(private http: HttpClient) { }
    getNews(query: string, limit: number) {
        return this.http.get<NewsResponse>(this.apiUrl, {
            params: {
                query: query,
                limit: limit
            }
        })
    }
}
