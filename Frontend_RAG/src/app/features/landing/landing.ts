import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TopNavbar } from '../../shared/components/top-navbar/top-navbar';

@Component({
    selector: 'app-landing',
    standalone: true,
    imports: [CommonModule, RouterLink, TopNavbar],
    templateUrl: './landing.html',
    styleUrl: './landing.scss'
})
export class Landing {
    features = [
        {
            icon: 'twitter',
            title: 'Tweet Generator',
            description: 'Viral-ready tweets crafted from any article instantly.',
            color: '#1DA1F2',
            position: 'top'
        },
        {
            icon: 'thread',
            title: 'Thread Formatter',
            description: 'Long-form content into captivating Twitter threads.',
            color: '#A855F7',
            position: 'right'
        },
        {
            icon: 'chart',
            title: 'Chart Extractor',
            description: 'Auto-generate publication-ready charts from data.',
            color: '#22C55E',
            position: 'left'
        },
        {
            icon: 'search',
            title: 'Research Assistant',
            description: 'AI-powered summaries and comprehensive reports.',
            color: '#3B82F6',
            position: 'bottom'
        }
    ];

    steps = [
        {
            number: '01',
            icon: '📋',
            title: 'Paste Your Content',
            description: 'Drop in any article URL or paste your text directly'
        },
        {
            number: '02',
            icon: '⚡',
            title: 'AI Magic Happens',
            description: 'Our AI analyzes, extracts key insights, and generates content'
        },
        {
            number: '03',
            icon: '🚀',
            title: 'Share & Shine',
            description: 'Get polished, ready-to-post content in multiple formats'
        }
    ];
}
