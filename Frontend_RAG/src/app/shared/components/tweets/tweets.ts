import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TweetService } from '../../../core/services/tweet.service';
import { TweetResponse } from '../../../core/models/tweet.model';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';

@Component({
    selector: 'app-tweets',
    imports: [CommonModule, MatCardModule, MatProgressSpinnerModule, MatChipsModule],
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

    constructor(
        private tweetService: TweetService,
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
                }
            },
            error: (error) => {
                console.error('Error fetching tweets:', error);
                this.errorMessage = 'Failed to connect to the server. Please try again.';
                this.isLoading = false;
            }
        });
    }
}
