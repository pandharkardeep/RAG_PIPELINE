import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NewsService } from '../../core/services/news.service';
import { NewsArticle } from '../../core/models/news.model';

@Component({
  selector: 'app-home',
  imports: [FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  query: string = '';
  limit: number = 10;

  constructor(private NewsService: NewsService, private router: Router) { }

  shownews(): void {
    this.router.navigate(['/articles'], {
      queryParams: {
        query: this.query,
        limit: this.limit
      }
    });
  }

  showTweets(): void {
    this.router.navigate(['/tweets'], {
      queryParams: {
        query: this.query,
        count: 3  // default count, can be made configurable
      }
    });
  }
}
