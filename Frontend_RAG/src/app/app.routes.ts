import { Routes } from '@angular/router';
import { News } from './shared/components/news/news';
import { Tweets } from './shared/components/tweets/tweets';
import { Home } from './features/home/home';

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
    }
];
