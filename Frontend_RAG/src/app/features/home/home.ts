import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NewsService } from '../../core/services/news.service';
import { NewsArticle } from '../../core/models/news.model';
import { Filters, SourceFilters } from '../../shared/components/filters/filters';

@Component({
  selector: 'app-home',
  imports: [FormsModule, Filters],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  query: string = '';
  numTweets: number = 3;
  sourceFilters: SourceFilters = { includeSources: [], excludeSources: [] };

  constructor(private NewsService: NewsService, private router: Router) { }

  shownews(): void {
    const queryParams: any = {
      query: this.query,
      limit: 10
    };
    if (this.sourceFilters.includeSources.length > 0) {
      queryParams.include_sources = this.sourceFilters.includeSources;
    }
    if (this.sourceFilters.excludeSources.length > 0) {
      queryParams.exclude_sources = this.sourceFilters.excludeSources;
    }
    this.router.navigate(['/articles'], { queryParams });
  }

  showTweets(): void {
    const queryParams: any = {
      query: this.query,
      count: this.numTweets
    };
    if (this.sourceFilters.includeSources.length > 0) {
      queryParams.include_sources = this.sourceFilters.includeSources;
    }
    if (this.sourceFilters.excludeSources.length > 0) {
      queryParams.exclude_sources = this.sourceFilters.excludeSources;
    }
    this.router.navigate(['/tweets'], { queryParams });
  }

  onFiltersChanged(filters: SourceFilters): void {
    this.sourceFilters = filters;
  }
}
