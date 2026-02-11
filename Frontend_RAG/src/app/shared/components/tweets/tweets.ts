import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TweetService } from '../../../core/services/tweet.service';
import { CleanupService } from '../../../core/services/cleanup.service';
import { TweetResponse } from '../../../core/models/tweet.model';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';

@Component({
    selector: 'app-tweets',
    imports: [CommonModule, MatCardModule, MatProgressSpinnerModule, MatChipsModule, MatExpansionModule],
    templateUrl: './tweets.html',
    styleUrl: './tweets.scss',
})
export class Tweets implements OnInit {
    tweetData?: TweetResponse;
    query: string = '';
    count: number = 3;
    top_k: number = 5;
    fetch_limit: number = 10;
    isLoading: boolean = false;
    errorMessage: string = '';
    cleanupStatus: string = '';

    constructor(
        private tweetService: TweetService,
        private cleanupService: CleanupService,
        private route: ActivatedRoute
    ) { }

    ngOnInit(): void {
        this.route.queryParams.subscribe((params: any) => {
            this.query = params.query || '';
            this.count = parseInt(params.count) || 3;
            this.top_k = parseInt(params.top_k) || 5;
            this.fetch_limit = parseInt(params.fetch_limit) || 10;

            if (this.query) {
                this.loadTweets();
            }
        });
    }

    loadTweets(): void {
        this.isLoading = true;
        this.errorMessage = '';
        this.cleanupStatus = '';

        this.tweetService.getTweets(
            this.query,
            this.count,
            this.top_k,
            this.fetch_limit
        ).subscribe({
            next: (res: TweetResponse) => {
                this.tweetData = res;
                this.isLoading = false;
                if (!res.success) {
                    this.errorMessage = res.error || 'Failed to generate tweets';
                } else {
                    // Auto-cleanup after successful tweet generation
                    this.performAutoCleanup(res.session_id);
                }
            },
            error: (error) => {
                console.error('Error fetching tweets:', error);
                this.errorMessage = 'Failed to connect to the server. Please try again.';
                this.isLoading = false;
            }
        });
    }

    /**
     * Automatically clean up Pinecone vectors and DATA folder after tweet generation
     */
    private performAutoCleanup(sessionId?: string): void {
        this.cleanupStatus = 'Cleaning up...';

        // Clean everything (folder + Pinecone)
        this.cleanupService.cleanupAll(true).subscribe({
            next: (res) => {
                if (res.success) {
                    const filesDeleted = res.folder_cleanup?.deleted_count || 0;
                    const vectorsDeleted = res.pinecone_cleanup?.vectors_deleted || 0;
                    this.cleanupStatus = `✓ Cleaned: ${filesDeleted} files, ${vectorsDeleted} vectors`;
                    console.log('Auto-cleanup completed:', res);
                } else {
                    this.cleanupStatus = '⚠ Cleanup partially completed';
                    console.warn('Cleanup had issues:', res);
                }
            },
            error: (error) => {
                this.cleanupStatus = '✗ Cleanup failed';
                console.error('Auto-cleanup failed:', error);
            }
        });
    }
}
