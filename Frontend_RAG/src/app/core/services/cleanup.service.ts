import { HttpClient, HttpParams } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { CleanupResponse, FolderCleanupResult, PineconeCleanupResult, SessionsResponse, StatsResponse } from "../models/cleanup.model";
import { environment } from "../../../environments/environment";

@Injectable({
    providedIn: 'root'
})
export class CleanupService {
    private readonly apiUrl = `${environment.apiBaseUrl}${environment.endpoints.cleanup}`;

    constructor(private http: HttpClient) { }

    /**
     * Get cleanup statistics (files and vectors count)
     */
    getStats(): Observable<StatsResponse> {
        return this.http.get<StatsResponse>(`${this.apiUrl}/stats`);
    }

    /**
     * List all available sessions
     */
    getSessions(): Observable<SessionsResponse> {
        return this.http.get<SessionsResponse>(`${this.apiUrl}/sessions`);
    }

    /**
     * Clean all data (folder + Pinecone)
     * @param confirm - Must be true to perform cleanup
     */
    cleanupAll(confirm: boolean = true): Observable<CleanupResponse> {
        const params = new HttpParams().set('confirm', confirm.toString());
        return this.http.post<CleanupResponse>(this.apiUrl, null, { params });
    }

    /**
     * Clean data for a specific session
     * @param sessionId - Session ID to clean
     * @param confirm - Must be true to perform cleanup
     */
    cleanupSession(sessionId: string, confirm: boolean = true): Observable<CleanupResponse> {
        const params = new HttpParams().set('confirm', confirm.toString());
        return this.http.post<CleanupResponse>(`${this.apiUrl}/session/${sessionId}`, null, { params });
    }

    /**
     * Clean only NEWS_data folder
     * @param confirm - Must be true to perform cleanup
     */
    cleanupFolderOnly(confirm: boolean = true): Observable<FolderCleanupResult> {
        const params = new HttpParams().set('confirm', confirm.toString());
        return this.http.delete<FolderCleanupResult>(`${this.apiUrl}/folder`, { params });
    }

    /**
     * Clean only Pinecone vectors
     * @param confirm - Must be true to perform cleanup
     */
    cleanupPineconeOnly(confirm: boolean = true): Observable<PineconeCleanupResult> {
        const params = new HttpParams().set('confirm', confirm.toString());
        return this.http.delete<PineconeCleanupResult>(`${this.apiUrl}/pinecone`, { params });
    }
}
