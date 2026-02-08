import { Component, signal, OnInit, OnDestroy } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { News } from './shared/components/news/news';
import { Navbar } from './shared/components/navbar/navbar';
import { Subscription, filter } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, News, Navbar, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit, OnDestroy {
  protected readonly title = signal('Frontend_RAG');
  navCollapsed: boolean = false;
  isLandingPage: boolean = false;
  private routerSubscription?: Subscription;

  constructor(private router: Router) { }

  ngOnInit(): void {
    // Check initial route
    this.checkLandingPage(this.router.url);

    // Subscribe to route changes
    this.routerSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.checkLandingPage(event.urlAfterRedirects);
      });
  }

  ngOnDestroy(): void {
    this.routerSubscription?.unsubscribe();
  }

  private checkLandingPage(url: string): void {
    // Remove hash fragments and query params for comparison
    const basePath = url.split('#')[0].split('?')[0];
    this.isLandingPage = basePath === '/' || basePath === '';
  }

  onNavCollapse(collapsed: boolean): void {
    this.navCollapsed = collapsed;
  }
}
