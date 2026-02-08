import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
    selector: 'app-top-navbar',
    standalone: true,
    imports: [CommonModule, RouterLink, RouterLinkActive],
    templateUrl: './top-navbar.html',
    styleUrls: ['./top-navbar.scss']
})
export class TopNavbar {
    servicesOpen: boolean = false;

    services = [
        {
            route: '/home',
            icon: '🐦',
            title: 'Tweet Generator',
            subtitle: 'Create viral tweets from articles'
        },
        {
            route: '/thread-formatter',
            icon: '🧵',
            title: 'Thread Formatter',
            subtitle: 'Convert content into threads'
        },
        {
            route: '/chart-extractor',
            icon: '📊',
            title: 'Chart Extractor',
            subtitle: 'Generate charts from data'
        },
        {
            route: '/research',
            icon: '🔍',
            title: 'Research Assistant',
            subtitle: 'AI-powered research summaries'
        }
    ];

    toggleServices(): void {
        this.servicesOpen = !this.servicesOpen;
    }

    closeServices(): void {
        this.servicesOpen = false;
    }
}
