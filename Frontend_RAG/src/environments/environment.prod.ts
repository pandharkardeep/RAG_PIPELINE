/**
 * Production Environment Configuration
 */
export const environment = {
    production: true,
    apiBaseUrl: 'https://pandharkrdeep-ai-news2social.hf.space',
    apiVersion: 'v1',
    endpoints: {
        articles: '/articles',
        tweets: '/tweets/generate',
        cleanup: '/cleanup'
    }
};
