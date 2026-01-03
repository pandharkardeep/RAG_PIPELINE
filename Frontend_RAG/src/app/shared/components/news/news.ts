import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NewsService } from '../../../core/services/newservice';
import { NewsSummary, NewsResponse } from '../../../core/models/news.model';
import { CommonModule, NgFor, NgForOf } from '@angular/common';

@Component({
    selector: 'app-news',
    imports: [NgFor, NgForOf, CommonModule],
    templateUrl: './news.html',
    styleUrl: './news.scss',
})
export class News implements OnInit {
    newsData?: NewsResponse;
    query: string = '';
    limit: number = -1;

    constructor(private news: NewsService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.route.queryParams.subscribe((params: any) =>{
            this.query = params.query;
            this.limit = params.limit;
       
            this.news.getNews(this.query, this.limit).subscribe({
                next: (res: NewsResponse) => {
                    this.newsData = res;
                },
                error: (error) => {
                    console.error('Error fetching news:', error);
                }
            });
        })
    }
}

/*
{
    "status": "OK",
    "request_id": "4c5cc4f1-498b-4f88-9a24-a6dc14cf2ea9",
    "data": [
        {
            "article_id": "CBMimwFBVV95cUxOV3dxeDFoTVdkT01MWUp2cy03NXJYajlhQzd0cmRvUnRrRXVTR2dnWDNFb0ViYXBkd2RHMlhYdk5hZFk1QW84QXN3bkl2d2N3VHBWNjViUjhudi1SbzVURGdVc2ZlV1hSaFgzdzgtWGxtMTBUNjZrWHJ4RTB5S1VKX2I4VDM4STdXeDlfNzE0aUEzWTZ3ZS1nX2xQcw",
            "title": "Mamdani Names Transportation Chief With Job of Making Buses Fast and Free",
            "link": "https://www.nytimes.com/2026/01/01/nyregion/mamdani-transportation-commissioner-mike-flynn.html",
            "snippet": "Zohran Mamdani, more than any recent New York City mayoral candidate, made improving the city's embarrassingly slow bus system central to ...",
            "photo_url": "https://static01.nyt.com/images/2026/01/01/multimedia/01met-dot-flynn-new-qwvm/01met-dot-flynn-new-qwvm-articleLarge.jpg?quality=75&auto=webp&disable=upscale",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNXZUWGxpTUhCV01GWnpZalZ5VFJDUUF4allCQ2dLTWdZRmtJaUx2UVE=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-01T06:55:19.000Z",
            "authors": [
                "Stefanos Chen",
                "Dana Rubinstein"
            ],
            "source_url": "https://www.nytimes.com",
            "source_name": "The New York Times",
            "source_logo_url": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://www.nytimes.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://www.nytimes.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqJQgKIh9DQklTRVFnTWFnMEtDMjU1ZEdsdFpYTXVZMjl0S0FBUAE",
            "related_topics": [
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZtZVhoeGFEVmpheElDWlc0b0FBUAE",
                    "topic_name": "Stefanos Chen"
                },
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZtTUhrMWN6VnhYeElDWlc0b0FBUAE",
                    "topic_name": "Dana Rubinstein"
                }
            ]
        },
        {
            "article_id": "CBMiugFBVV95cUxNNnBnOF9sM21jTHU3ZHZBYW5jM1JPLU8zeU8yVUtlUTZEckRtZmNkZFUzUGZRYWo3R2Y0TF9RR1FDcHZvdzFFQ0lHa3N2YkdxUTBRUHZmY09paEtlTXh0UjBOM1VxdUd1X3lvcW91NGtFbFU4cm1kZ2diSmY0eFhKSk1LM2puX1lhZG9DZWh4YUNYdE5OSTJRZmZnWGdvQW05czJ4b0ZuZ2planVuakFIdEtFekxGWVNoY3c",
            "title": "Racial and religious hate crime on UK public transport is growing, data shows",
            "link": "https://www.theguardian.com/society/2026/jan/02/racial-and-religious-hate-on-uk-public-transport-is-growing-data-shows",
            "snippet": "Anti-racism groups warn some people are avoiding public transport or limiting their use of it for fear of abuse.",
            "photo_url": "https://i.guim.co.uk/img/media/a817266ab3d1b6a1ecfc41446c34eb8c209e2f20/960_0_4800_3840/master/4800.jpg?width=465&dpr=1&s=none&crop=none",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNDJaemxDTFhGUFZrUk9ORVoyVFJEMEFoalJBeWdLTWdZNW9venlQQVU=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-02T10:03:00.000Z",
            "authors": [
                "Libby Brooks"
            ],
            "source_url": "https://www.theguardian.com",
            "source_name": "The Guardian",
            "source_logo_url": "https://encrypted-tbn0.gstatic.com/faviconV2?url=https://www.theguardian.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn0.gstatic.com/faviconV2?url=https://www.theguardian.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqKggKIiRDQklTRlFnTWFoRUtEM1JvWldkMVlYSmthV0Z1TG1OdmJTZ0FQAQ",
            "related_topics": [
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZtZVhod05UTTRlQklDWlc0b0FBUAE",
                    "topic_name": "Libby Brooks"
                }
            ]
        },
        {
            "article_id": "CBMikAFBVV95cUxPYTNXS3FHc1N5ajFZTThSeEVUY09WWWd1RWpBRVVMN0doYkIxX3dod3VPaVBqSzk0TXB0VFQtVHlOYXpXd20zZXRLaElZeXVUNXoxVmw1ZVVkNFNvSmowc2ZhUWVaNUhkSGdLRVBtU0o1SnQ5SjhTdUxQcE4wUGZIdzZoR0EtVHptelduSGZLUW8",
            "title": "Yemeni transport ministry says Saudi Arabia mandated inspections of flights between Aden and UAE",
            "link": "https://www.yahoo.com/news/articles/yemeni-transport-ministry-says-saudi-191202154.html",
            "snippet": "In its statement, the ministry demanded “an end to the air blockade imposed on the Yemeni people, a reversal of these measures, and a ...",
            "photo_url": "https://s.yimg.com/ny/api/res/1.2/okH6thVyS7O4XP3ibY0e4A--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyNDI7aD04Mjg7Y2Y9d2VicA--/https://media.zenfs.com/en/ap.org/f862aee619ab0e9925792b0393ac19fb",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNXlkVXBuVUhkVFNGZ3RjVlZ6VFJERUF4aW1CU2dLTWdZQk1JUkNHd2s=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-01T19:12:02.000Z",
            "authors": [
                "Fatma Khaled"
            ],
            "source_url": "https://www.yahoo.com",
            "source_name": "Yahoo",
            "source_logo_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.yahoo.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.yahoo.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqIggKIhxDQklTRHdnTWFnc0tDWGxoYUc5dkxtTnZiU2dBUAE",
            "related_topics": [
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZ1TUdaeU9XcHRheElDWlc0b0FBUAE",
                    "topic_name": "Fatma Khaled"
                }
            ]
        },
        {
            "article_id": "CBMihwJBVV95cUxOZmZESWJ3WUs5R3dMQkl1T0MxbW9qNmxobHZDRE0wbXlJNnpZakt3TGdTeF9kRmtOWVlhVmdNVTdRZGZ5eE52QXh1ZHhaRUVpSWI4MUhBaDQ5a3VmcEctTkVacXdRT2tXYTZ2MHF2WVhtcEpvNWwtejJrX0pGRFVBdVJ2TlJwU0FiQkgwT2o5WmtGWjhyUjVSYzJDWHZ6bUxvb2VIQmZReFFfcUJwWFh5WDJzc2M1eGp2a3BnbFBCSFdJdUdvMklGN1l3RUhnYzBzaGJQbU85Y2htU3huZXVJRnNGQW10cHVKeWpCQnNPRjBZb25QRVVubnZZa2JqM3VjOVlJYVY3VQ",
            "title": "Israeli medics refuse to transport Palestinian patient over permit issue",
            "link": "https://www.haaretz.com/israel-news/2026-01-02/ty-article/.premium/israeli-medics-refuse-to-transport-palestinian-patient-over-permit-issue/0000019b-7ddd-d379-a3bb-fffddd870000",
            "snippet": "Israeli ambulance staff refused to transport a Palestinian man from an East Jerusalem clinic on Wednesday despite concerns that he was suffering ...",
            "photo_url": "https://img.haarets.co.il/bs/0000019b-7dee-d487-a3bf-fdefbd400000/83/d4/f1d8a48e4987bcccdcd2d1eb1c03/740818.jpg?precrop=2400,1395,x0,y208&width=420&height=244&cmsprod",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNWtObHBZY1RCQ1lVTnJhSEpJVFJEMEFSaWtBeWdLTWdZTmxKTEtPUWM=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-02T09:39:00.000Z",
            "authors": [
                "Nir Hasson"
            ],
            "source_url": "https://www.haaretz.com",
            "source_name": "Haaretz",
            "source_logo_url": "https://encrypted-tbn3.gstatic.com/faviconV2?url=https://www.haaretz.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn3.gstatic.com/faviconV2?url=https://www.haaretz.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqJQgKIh9DQklTRVFnTWFnMEtDMmhoWVhKbGRIb3VZMjl0S0FBUAE",
            "related_topics": [
                {
                    "topic_id": "CAAqJggKIiBDQkFTRWdvTUwyY3ZNV2htWDJOaVpHUmtFZ0psYmlnQVAB",
                    "topic_name": "Nir Hasson"
                }
            ]
        },
        {
            "article_id": "CBMirwFBVV95cUxNSllpc2lYelc1TC11a1VYSUY1UlVwc2d3LUpvdWZrVW9KY21GU00xOWhvRjgwOVpXcjBDQ0R6QkNOUW92WjFlWWh2UDNfb3FidEhkUGdSZ0xJZkRFWm9FT3BIOEFWWDc2WTRZS3B2N1l0djcxQy1HX1ZrOFpEYzVWVC1SOC1RTUZMYzdFd19qdE9DMGVFMUE2M2lzY3JBUU1JNGdQU0I4eDNFT0lTcmZ30gGvAUFVX3lxTE1KWWlzaVh6VzVMLXVrVVhJRjVSVXBzZ3ctSm91ZmtVb0pjbUZTTTE5aG9GODA5WldyMENDRHpCQ05Rb3ZaMWVZaHZQM19vcWJ0SGRQZ1JnTElmREVab0VPcEg4QVZYNzZZNFlLcHY3WXR2NzFDLUdfVms4WkRjNVZULVI4LVFNRkxjN0V3X2p0T0MwZUUxQTYzaXNjckFRTUk0Z1BTQjh4M0VPSVNyZnc",
            "title": "Crews rescue trapped driver after snowy crash, transport to New Bedford hospital",
            "link": "https://fallriverreporter.com/crews-rescue-trapped-driver-after-snowy-crash-transport-to-new-bedford-hospital/",
            "snippet": "Local crews responded to a collision Thursday morning that trapped a driver as snow accumulated on area roads. According to Berkley Fire and ...",
            "photo_url": "https://fallriverreporter.com/wp-content/uploads/2026/01/berkley-fire-and-rescue-1-1-26.jpg",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iL0NnNUVlVGRTY1ZwT1dWQmxlSGhOVFJEZkFoaXBCQ2dLTWdtQm80NXR3U1hva0FF=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-01T21:22:30.000Z",
            "authors": [
                "Ken Paiva"
            ],
            "source_url": "https://fallriverreporter.com",
            "source_name": "Fall River Reporter",
            "source_logo_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://fallriverreporter.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://fallriverreporter.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqMggKIixDQklTR3dnTWFoY0tGV1poYkd4eWFYWmxjbkpsY0c5eWRHVnlMbU52YlNnQVAB",
            "related_topics": [
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZ3ZVdSb2NXNTBPQklDWlc0b0FBUAE",
                    "topic_name": "Ken Paiva"
                }
            ]
        },
        {
            "article_id": "CBMirwFBVV95cUxNaHJJRzg3b2s0TzAxNUxBbFVQNWl6Z2lyaDhYd0o0VWVBd3dzcThBOHVJTzhfYWl3c3l2MzVqUjhfNFNlWW1pVEdRbk9oQlBkaS1PNmRDTVlQek4tX00zTEN6VWF1bDhoYTBybERneUFqQ1Zua2w2M2MzSWxrbXlIeTRGdnNMR3l0NjFFMWxST0lvTDFjbTBFUFlNOEdHV2Z4VlAtMnJLaUJXcUxOMk1J0gG0AUFVX3lxTE5LNzRmZVBJZURqUVNYWlUtZm5ZUWVVTXN0N0lDUHkyQW5sSzRsVTdUcmZGRUowWFpOdFZhTXc1NmY0NG1QSGRmSEFsb1Q4NVZiYzJ3aFk5UTNMclZlVmNzankzNlRHbGtleDIzTVVwODlfWUxWMnlZMEN0VW5pZWI5d3ExX1FyT3ZLY0pLSV9rNm13OHV5VkJfN3JLZG5aQVIyN0xxM0VqVmRDU25Pa29tODdPYg",
            "title": "Transport Canada warns Air India on drinking rules after pilot's Vancouver arrest",
            "link": "https://abcnews.go.com/International/wireStory/transport-canada-warns-air-india-drinking-rules-after-128857541",
            "snippet": "The statement said Canadian aviation regulations prohibited pilots or any other crew members from acting within 12 hours of drinking alcohol or ...",
            "photo_url": "https://i.abcnewsfe.com/a/5335fa78-6c85-4816-a1e9-ace3c99058a2/weekday_headlines_hpMain_16x9.jpg?w=992",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNDViekJMUVZReVJVWktWRlZ1VFJDZkF4ampCU2dLTWdZUllaYkxNQWc=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-03T02:14:27.000Z",
            "authors": [],
            "source_url": "https://abcnews.go.com",
            "source_name": "ABC News",
            "source_logo_url": "https://encrypted-tbn3.gstatic.com/faviconV2?url=https://abcnews.go.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn3.gstatic.com/faviconV2?url=https://abcnews.go.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqKQgKIiNDQklTRkFnTWFoQUtEbUZpWTI1bGQzTXVaMjh1WTI5dEtBQVAB",
            "related_topics": []
        },
        {
            "article_id": "CBMikgJBVV95cUxQdFdoTFRSR2tqWGpPdmx5SnRsTFRkaHlaNkEzdFM5V0k4MFdaaThsWEkyS0t5M0hiUGpJZFpVSTM1cl9ISWJGYXRVVDF2T2h1UnpBbjJhaWp0dDFvR0o4RGo4YXBRdVZ2ODdYN1V3aHFWT1V6T3FkZ3JMVW9FeXhGc2l2VHZMTklxMUNlZi1iZi0wSkNIdGxrN1laYW9hYlFIb0pIRm9Ucm9VX0ZNUmNfRVFrOU5FRUtkS1Rtd3lVcktsNERTLXg0RDV6cWllZndNOFZhX25ocnlod0NVRmNmWWhDTGNVM21uaXpLVm92aEpxN0xCOTNidE9SVE13VENlTG9yM1FOUVFZd0JyUTdRYk1B",
            "title": "Warren Transport driver an Angel for extinguishing Dallas car fire",
            "link": "https://www.truckersnews.com/life/article/15775049/warren-transport-driver-an-angel-for-extinguishing-dallas-care-firewarren-transport-driver-an-angel-for-extinguishing-dallas-car-fire",
            "snippet": "A trucker is being honored for his actions that most likely averted what could have been a catastrophic vehicle fire.",
            "photo_url": "https://img.truckersnews.com/mindful/rr-talent/workspaces/default/uploads/2026/01/screenshot-2026-01-02-at-111558-am.FiiicXvtgi.png?auto=format%2Ccompress&q=70&w=400",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNHdNbk5UWjNoSk1IUkdOVzFuVFJDaEFSaTVBaWdCTWdhdGRJQ3Z0UU0=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-03T08:28:34.000Z",
            "authors": [],
            "source_url": "https://www.truckersnews.com",
            "source_name": "Truckers News",
            "source_logo_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.truckersnews.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.truckersnews.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqLAgKIiZDQklTRmdnTWFoSUtFSFJ5ZFdOclpYSnpibVYzY3k1amIyMG9BQVAB",
            "related_topics": []
        },
        {
            "article_id": "CBMiowFBVV95cUxNMGFMVElyMnlpdEhXNThPQ016cmhDakd5MGJCa3dmNlhiNDN0MjdyRzh4R1JsUktJTUkwNDNYeUp4R19Od1hfVVAyRlVISVBHZTVxVG13WERZRzBkVWlnbE9XSUp5U2dpUGlxdFIxQng0OFV0TnRtNEt0Zk1ENEgzUVJUTE1GdGdEZ3FJLWF6NmJ0bFpGaGFnV09FTFk5MHVXUzZB",
            "title": "Alternatives proposed for Gorst transportation improvements",
            "link": "https://www.kitsapdailynews.com/news/gorst-project-receives-82-5-million-for-initial-planning-design/",
            "snippet": "An $82.5 million project for transportation improvements in the Gorst area is currently in the planning and design process.",
            "photo_url": "https://www.kitsapdailynews.com/wp-content/uploads/2026/01/41236349_web1_260109-POI-Gorst-Project-Alternatives_1.jpg",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNVplWFpVUjI5eWNtNXlRMnhoVFJEVEF4aVJCU2dLTWdZQkVJNEREd3M=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-02T09:30:00.000Z",
            "authors": [
                "Katherine Bouma"
            ],
            "source_url": "https://www.kitsapdailynews.com",
            "source_name": "Kitsap Daily News",
            "source_logo_url": "https://encrypted-tbn0.gstatic.com/faviconV2?url=https://www.kitsapdailynews.com&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn0.gstatic.com/faviconV2?url=https://www.kitsapdailynews.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqMAgKIipDQklTR1FnTWFoVUtFMnRwZEhOaGNHUmhhV3g1Ym1WM2N5NWpiMjBvQUFQAQ",
            "related_topics": [
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZ4TXpOdE4yd3lZaElDWlc0b0FBUAE",
                    "topic_name": "Katherine Bouma"
                }
            ]
        },
        {
            "article_id": "CBMiwgFBVV95cUxOdEc3VFkwTmN1WVRuUjFNZDVpcXNWci1Nbnk1T1BHZjRyZGh5YktXV3dIWU5fclZxeTZMNmk2b291aE1pdWhoa1pPM183Q252N3RXVjZsY0tsV3BLdUVRaXBJT1RPLUlidnQwXzgwVF81MThyaDNVQ2dabFk0MV9zcEI2ZmFYWlhzREx2ZEZyRkxZZUZHUXNzeEZJWU0tSmkxZmZoMlVwMEpmX0xrbUJHV2RBR3F4OEVYT1o5djhOTVdnZw",
            "title": "Lyon County Sheriff: Suspect dies in patrol car during transport, CCSO, NHP to investigate",
            "link": "https://www.carsonnow.org/12/31/2025/lyon-county-sheriff-suspect-dies-in-patrol-car-during-transport-ccso-nhp-to-investigate",
            "snippet": "The Lyon County Sheriff's Office issued the following statement regarding a death that occurred New Years Eve: On December 31, 2025, ...",
            "photo_url": "https://i0.wp.com/www.carsonnow.org/wp-content/uploads/2025/02/lcsofficecar.jpg?fit=706%2C434&ssl=1",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNUhOM0Y0UTBwSVptcFhMVE5CVFJDeUF4akNCU2dLTWdZQlVJNm5OQVk=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-01T04:50:45.000Z",
            "authors": [],
            "source_url": "https://www.carsonnow.org",
            "source_name": "Carson Now",
            "source_logo_url": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://www.carsonnow.org&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://www.carsonnow.org&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqKAgKIiJDQklTRXdnTWFnOEtEV05oY25OdmJtNXZkeTV2Y21jb0FBUAE",
            "related_topics": []
        },
        {
            "article_id": "CBMirgFBVV95cUxNdlQ1MmRsZEltVDhHaWxFNnZheU16RDVFRmxRTVg3alRKbi1NTHR2MllQYXRvaTFoYXJReWpFQXNQd0ktRTAxMk1HTzAtZFkzMjJLdjhLTXo0d01DM1NoY0RGRmVNbWRXQ0ljQ0lDcTEwOFRzcGw3dEtFRnUzTUZxSnN5WUdtVUpGT0VDVnVlTm1QdE92cVNRekYtdXFBQ1VITnJxWUYwbDVxbkhiQ3c",
            "title": "Tacoma Turns to Builder Impact Fees to Bolster Transportation Funding",
            "link": "https://www.theurbanist.org/2026/01/02/tacoma-turns-to-builder-impact-fees-to-bolster-transportation-funding/",
            "snippet": "Tacoma's new impact fee regime, which goes into effect next summer, will charge developers based on expected generation of car trips.",
            "photo_url": "https://www.theurbanist.org/wp-content/uploads/2023/01/Tacoma-I-705-The-Urbanist-IMG_20191020.jpg",
            "thumbnail_url": "https://news.google.com/api/attachments/CC8iK0NnNTRURVpUY1VjNFRrNHhWRkJSVFJEZ0F4aUFCU2dLTWdZQm9JU2t3UVk=-w200-h200-p-df-rw",
            "published_datetime_utc": "2026-01-02T14:00:00.000Z",
            "authors": [
                "Ryan Packer"
            ],
            "source_url": "https://www.theurbanist.org",
            "source_name": "The Urbanist",
            "source_logo_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.theurbanist.org&client=NEWS_360&size=256&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_favicon_url": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.theurbanist.org&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "source_publication_id": "CAAqKggKIiRDQklTRlFnTWFoRUtEM1JvWlhWeVltRnVhWE4wTG05eVp5Z0FQAQ",
            "related_topics": [
                {
                    "topic_id": "CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZ3ZEhObmVXd3hlUklDWlc0b0FBUAE",
                    "topic_name": "Ryan Packer"
                }
            ]
        }
    ]
}
*/