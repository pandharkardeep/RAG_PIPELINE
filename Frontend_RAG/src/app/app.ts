import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { News } from './shared/components/news/news';
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, News],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('Frontend_RAG');
}
