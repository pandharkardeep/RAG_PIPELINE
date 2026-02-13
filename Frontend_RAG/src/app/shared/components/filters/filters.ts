import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NewsService } from '../../../core/services/news.service';

export interface SourceFilters {
    includeSources: string[];
    excludeSources: string[];
}

@Component({
    selector: 'app-filters',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './filters.html',
    styleUrl: './filters.scss',
})
export class Filters implements OnInit {
    @Output() filtersChanged = new EventEmitter<SourceFilters>();

    isExpanded = false;

    includeDropdownOpen = false;
    excludeDropdownOpen = false;

    includeSearch = '';
    excludeSearch = '';

    selectedInclude: string[] = [];
    selectedExclude: string[] = [];

    mediaSources: string[] = [];
    isLoadingSources = false;

    constructor(private newsService: NewsService) { }

    ngOnInit(): void {
        this.loadSources();
    }

    private loadSources(): void {
        this.isLoadingSources = true;
        this.newsService.getSources().subscribe({
            next: (res) => {
                this.mediaSources = res.sources || [];
                this.isLoadingSources = false;
            },
            error: (err) => {
                console.error('Failed to load sources:', err);
                this.isLoadingSources = false;
            }
        });
    }

    /** Call this to merge in newly discovered sources from article responses */
    addDiscoveredSources(sources: string[]): void {
        for (const source of sources) {
            if (source && !this.mediaSources.includes(source) && !source.startsWith('http')) {
                this.mediaSources.push(source);
            }
        }
        this.mediaSources.sort();
    }

    get filteredIncludeSources(): string[] {
        return this.mediaSources.filter(
            (s) =>
                !this.selectedInclude.includes(s) &&
                !this.selectedExclude.includes(s) &&
                s.toLowerCase().includes(this.includeSearch.toLowerCase())
        );
    }

    get filteredExcludeSources(): string[] {
        return this.mediaSources.filter(
            (s) =>
                !this.selectedExclude.includes(s) &&
                !this.selectedInclude.includes(s) &&
                s.toLowerCase().includes(this.excludeSearch.toLowerCase())
        );
    }

    get activeFilterCount(): number {
        return this.selectedInclude.length + this.selectedExclude.length;
    }

    togglePanel(): void {
        this.isExpanded = !this.isExpanded;
        if (!this.isExpanded) {
            this.includeDropdownOpen = false;
            this.excludeDropdownOpen = false;
        }
    }

    toggleIncludeDropdown(): void {
        this.includeDropdownOpen = !this.includeDropdownOpen;
        this.excludeDropdownOpen = false;
        this.includeSearch = '';
    }

    toggleExcludeDropdown(): void {
        this.excludeDropdownOpen = !this.excludeDropdownOpen;
        this.includeDropdownOpen = false;
        this.excludeSearch = '';
    }

    addInclude(source: string): void {
        if (!this.selectedInclude.includes(source)) {
            this.selectedInclude.push(source);
            this.emitFilters();
        }
    }

    removeInclude(source: string): void {
        this.selectedInclude = this.selectedInclude.filter((s) => s !== source);
        this.emitFilters();
    }

    addExclude(source: string): void {
        if (!this.selectedExclude.includes(source)) {
            this.selectedExclude.push(source);
            this.emitFilters();
        }
    }

    removeExclude(source: string): void {
        this.selectedExclude = this.selectedExclude.filter((s) => s !== source);
        this.emitFilters();
    }

    clearAll(): void {
        this.selectedInclude = [];
        this.selectedExclude = [];
        this.emitFilters();
    }

    private emitFilters(): void {
        this.filtersChanged.emit({
            includeSources: [...this.selectedInclude],
            excludeSources: [...this.selectedExclude],
        });
    }
}

