import { Routes } from '@angular/router';
import { News } from './shared/components/news/news';
import { Tweets } from './shared/components/tweets/tweets';
import { Home } from './features/home/home';
import { ThreadFormatter } from './features/thread-formatter/thread-formatter';
import { ChartExtractor } from './features/chart-extractor/chart-extractor';

export const routes: Routes = [
    {
        path: '',
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
    }
];
