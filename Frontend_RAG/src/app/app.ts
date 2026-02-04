import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { News } from './shared/components/news/news';
import { Navbar } from './shared/components/navbar/navbar';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, News, Navbar],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('Frontend_RAG');
  navCollapsed: boolean = false;

  onNavCollapse(collapsed: boolean): void {
    this.navCollapsed = collapsed;
  }
}
