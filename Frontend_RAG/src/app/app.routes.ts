import { Routes } from '@angular/router';
import { News } from './shared/components/news/news';
import { Home } from './features/home/home';

export const routes: Routes = [
    {
        path: '',
        component: Home
    },
    {
        path: 'articles',
        component: News
    }
];
