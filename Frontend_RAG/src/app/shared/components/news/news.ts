import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { NewsService } from '../../../core/services/news.service';
import { NewsSummary, NewsResponse } from '../../../core/models/news.model';


@Component({
    selector: 'app-news',
    imports: [CommonModule],
    templateUrl: './news.html',
    styleUrl: './news.scss',
})
export class News implements OnInit {
    newsData?: NewsResponse;
    query: string = '';
    limit: number = -1;
    isLoading: boolean = false;
    exportStatus: string = '';

    constructor(private news: NewsService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.route.queryParams.subscribe((params: any) => {
            this.query = params.query;
            this.limit = params.limit;
            this.isLoading = true;

            this.news.getNews(this.query, this.limit).subscribe({
                next: (res: NewsResponse) => {
                    this.newsData = res;
                    this.isLoading = false;
                },
                error: (error) => {
                    console.error('Error fetching news:', error);
                    this.isLoading = false;
                }
            });
        })
    }

    exportToCsv(): void {
        this.exportStatus = 'Exporting...';

        this.news.downloadNews().subscribe({
            next: (blob: Blob) => {
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;

                // Generate filename with timestamp
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
                link.download = `articles_${this.query.replace(/\s+/g, '_')}_${timestamp}.csv`;

                // Trigger download
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                this.exportStatus = '✓ Export complete!';
                setTimeout(() => this.exportStatus = '', 3000);
            },
            error: (error) => {
                console.error('Export failed:', error);
                this.exportStatus = '✗ Export failed. Please try again.';
                setTimeout(() => this.exportStatus = '', 5000);
            }
        });
    }
}

