/**
 * Development Environment Configuration
 */
export const environment = {
    production: true,
    apiBaseUrl: 'http://localhost:7860',
    apiVersion: 'v1',
    endpoints: {
        articles: '/articles',
        tweets: '/tweets/generate',
        cleanup: '/cleanup'
    }
};
