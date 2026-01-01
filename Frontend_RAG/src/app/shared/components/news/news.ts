import { Component } from '@angular/core';
import { NewsService } from '../../../core/services/newservice';
import { NewsResponse } from '../../../core/models/news.model';

@Component({
  selector: 'app-news',
  imports: [],
  templateUrl: './news.html',
  styleUrl: './news.scss',
})
export class News {
  constructor(private news: NewsService) { }
  newsData?: NewsResponse;

  ngOnInit(): void {
    this.news.getNews('Transport', 10).subscribe({
      next: (res: NewsResponse) => {
        this.newsData = res;
      },
      error: (error) => {
        console.error('Error fetching news:', error);
      }
    });
    console.log(this.newsData);
  }
}
