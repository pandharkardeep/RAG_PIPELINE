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
    getNews(query: string, limit: number, includeSources?: string[], excludeSources?: string[]) {
        let params: any = {
            query: query,
            limit: limit
        };
        if (includeSources && includeSources.length > 0) {
            params.include_sources = includeSources;
        }
        if (excludeSources && excludeSources.length > 0) {
            params.exclude_sources = excludeSources;
        }
        return this.http.get<NewsResponse>(this.apiUrl, { params });
    }
    downloadNews() {
        return this.http.get(this.apiUrl + '/export/csv', {
            responseType: 'blob'
        })
    }
    getSources() {
        return this.http.get<{ sources: string[] }>(this.apiUrl + '/sources');
    }
}
