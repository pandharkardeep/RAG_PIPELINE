import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ResearchService, ResearchReport, ContentIdea, TrendingTopic } from '../../core/services/research.service';

@Component({
    selector: 'app-research',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './research.html',
    styleUrl: './research.scss'
})
export class Research {
    // Input
    niche: string = '';
    subreddits: string = '';
    ideaCount: number = 20;

    // Results
    report: ResearchReport | null = null;

    // UI State
    isLoading: boolean = false;
    errorMessage: string = '';
    successMessage: string = '';
    activeTab: 'ideas' | 'trending' | 'painpoints' = 'ideas';

    constructor(private researchService: ResearchService) { }

    runResearch(): void {
        if (!this.niche.trim()) {
            this.errorMessage = 'Please enter a niche to research';
            return;
        }

        this.isLoading = true;
        this.errorMessage = '';
        this.successMessage = '';
        this.report = null;

        const subredditList = this.subreddits
            .split(',')
            .map(s => s.trim().replace(/^r\//, ''))
            .filter(s => s.length > 0);

        this.researchService.analyzeNiche({
            niche: this.niche,
            subreddits: subredditList.length > 0 ? subredditList : undefined,
            idea_count: this.ideaCount
        }).subscribe({
            next: (response) => {
                this.isLoading = false;
                if (response.success && response.report) {
                    this.report = response.report;
                    this.successMessage = `Generated ${response.report.content_ideas.length} content ideas!`;
                } else {
                    this.errorMessage = response.message || 'Research failed';
                }
            },
            error: (error) => {
                this.isLoading = false;
                this.errorMessage = error.message || 'An error occurred';
            }
        });
    }

    clearAll(): void {
        this.niche = '';
        this.subreddits = '';
        this.report = null;
        this.errorMessage = '';
        this.successMessage = '';
    }

    getConfidenceClass(score: number): string {
        if (score >= 0.8) return 'high';
        if (score >= 0.6) return 'medium';
        return 'low';
    }

    copyIdea(idea: ContentIdea): void {
        const text = `${idea.title}\n\n${idea.description}`;
        navigator.clipboard.writeText(text);
        this.successMessage = 'Copied to clipboard!';
        setTimeout(() => this.successMessage = '', 2000);
    }
}
