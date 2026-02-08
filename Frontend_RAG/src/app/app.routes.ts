import { Routes } from '@angular/router';
import { News } from './shared/components/news/news';
import { Tweets } from './shared/components/tweets/tweets';
import { Home } from './features/home/home';
import { ThreadFormatter } from './features/thread-formatter/thread-formatter';
import { ChartExtractor } from './features/chart-extractor/chart-extractor';
import { Research } from './features/research/research';
import { Landing } from './features/landing/landing';

export const routes: Routes = [
    {
        path: '',
        component: Landing
    },
    {
        path: 'home',
        component: Home
    },
    {
        path: 'articles',
        component: News
    },
    {
        path: 'tweets',
        component: Tweets
    },
    {
        path: 'thread-formatter',
        component: ThreadFormatter
    },
    {
        path: 'chart-extractor',
        component: ChartExtractor
    },
    {
        path: 'research',
        component: Research
    }
];
