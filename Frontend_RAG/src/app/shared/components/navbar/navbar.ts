import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
    selector: 'app-navbar',
    standalone: true,
    imports: [CommonModule, RouterLink, RouterLinkActive],
    templateUrl: './navbar.html',
    styleUrl: './navbar.scss'
})
export class Navbar {
    isCollapsed: boolean = false;
    @Output() collapsedChange = new EventEmitter<boolean>();

    navItems = [
        { route: '/home', label: 'Home', icon: 'home' },
        { route: '/thread-formatter', label: 'Thread Formatter', icon: 'subject' },
        { route: '/chart-extractor', label: 'Chart Extractor', icon: 'bar_chart' },
        { route: '/research', label: 'Research', icon: 'travel_explore' }
    ];

    toggleNavbar(): void {
        this.isCollapsed = !this.isCollapsed;
        this.collapsedChange.emit(this.isCollapsed);
    }
}
