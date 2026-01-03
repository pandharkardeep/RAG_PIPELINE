from fastapi import FastAPI
from fastapi import APIRouter
from pydantic import BaseModel
import requests
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, RAPIDAPI_URL
from summarization.summarize_news import summarization
router = APIRouter()


@router.get("/articles")
def news_ingestion(query: str, limit: int):
    url = RAPIDAPI_URL

    querystring = {
        "query": query,
        "limit": limit
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    # response = requests.get(url, headers=headers, params=querystring)
    # api_data = response.json()
    # print(api_data)
    
    # Wrap the response in the format expected by the frontend
    # formatted_response = {
    #     "status": "OK",
    #     "data": api_data if isinstance(api_data, list) else []
    # }
    
    #summary = summarization.summarize_news(response.json()["data"][0]["snippet"])
    #print(summary)
    return {
  "success": True,
  "data": [
    {
      "title": 'Transport Canada / Transports Canada',
      "name": "",
      "url": 'https://tc.canada.ca',
      "language": 'en',
      "category": 'Politics',
      "description": '',
      "logo": 'https://tc.canada.ca/libraries/theme-gcweb/assets/sp-bg-2.jpg',
      "favicon": 'https://tc.canada.ca/libraries/theme-gcweb/assets/favicon.ico',
      "links": []
    },
    {
      "title": 'Athens Transport',
      "name": 'Athens Transport',
      "url": 'https://www.athenstransport.com',
      "language": 'en',
      "category": 'General',
      "description": 'Μέσα Μαζικής Μεταφοράς στην Αθήνα',
      "logo": 'https://s0.wp.com/i/blank.jpg',
      "favicon": 'https://www.athenstransport.com/wp-content/uploads/2018/12/athenstransport_logo_1.png',
      "links": []
    },
    {
      "title": 'Transport Topics',
      "name": 'Transport Topics',
      "url": 'https://www.ttnews.com',
      "language": 'en',
      "category": 'Business',
      "description": 'Transport Topics is the nation’s logistics and trucking news leader, with award-winning coverage of the regulatory, technology, business, and equipment sectors.',
      "logo": 'https://www.ttnews.com/sites/default/files/2023-10/Mack-Plant-1200.jpg',
      "favicon": 'https://www.ttnews.com/sites/default/files/pwa/TT%20Box%20App.pngcopy.png',
      "links": []
    },
    {
      "title": 'Auckland Transport',
      "name": 'Auckland Transport',
      "url": 'https://at.govt.nz',
      "language": 'en',
      "category": 'Entertainment',
      "description": 'Auckland Transport is responsible for Auckland’s transport services excluding state highways. From roads and footpaths to cycling parking and public transport.',
      "logo": 'https://at.govt.nz/media/1982515/at-logo-on-blue-background.png',
      "favicon": 'https://web-p-ae-website-cms-cdne.azureedge.net/public/2.1.1/images/at-logo-144.png', 
      "links": []
    },
    {
      "title": 'Transport & Environment - Campaigning for cleaner transport in Europe',
      "name": 'Transport & Environment',
      "url": 'https://www.transportenvironment.org',
      "language": 'en',
      "category": 'Politics',
      "description": 'Europe’s leading NGO campaigning for cleaner transport',
      "logo": 'https://www.transportenvironment.org/wp-content/uploads/2021/09/jenny-ueberberg-v_1k3vRX4kg-unsplash-1-scaled.jpg',
      "favicon": 'https://www.transportenvironment.org/wp-content/themes/tae/assets/images/apple-touch-icon.png',
      "links": []
    },
    {
      "title": 'Intelligent Transport',
      "name": 'Intelligent Transport',
      "url": 'https://www.intelligenttransport.com',
      "language": 'en',
      "category": 'Business',
      "description": 'Intelligent Transport provides news and business information for the world’s transport industry: magazines, newsletter, directory, and on-line services.',
      "logo": 'https://www.intelligenttransport.com/wp-content/uploads/IT-Logo@2x.png',
      "favicon": 'https://www.intelligenttransport.com/favicon.ico?v=2',
      "links": []
    },
    {
      "title": 'Motor Transport',
      "name": 'Motor Transport',
      "url": 'https://motortransport.co.uk',
      "language": 'en',
      "category": 'Business',
      "description": 'UK haulage, distribution and logistics news',
      "logo": 'http://motortransport.co.uk/wp-content/uploads/2017/09/motor-transport-logo-larger.png', 
      "favicon": 'https://motortransport.co.uk/favicon.ico',
      "links": []
    },
    {
      "title": 'Transport Info - Le site des professionnels du transport routier',
      "name": 'Transport Info',
      "url": 'https://www.transportinfo.fr',
      "language": 'en',
      "category": 'Business',
      "description": 'Le site des professionnels du transport routier',
      "logo": "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='678'%20height='381'%20viewBox='0%200%20678%20381'%3E%3C/svg%3E",
      "favicon": 'https://www.transportinfo.fr/wp-content/uploads/2018/07/cropped-ICO-TI-fr-270x270.png',
      "links": []
    },
    {
      "title": 'Tank Transport',
      "name": 'Tank Transport',
      "url": 'https://tanktransport.com',
      "language": 'en',
      "category": 'General',
      "description": '<font size=“6”>The National Newspaper for the Liquid and Dry Bulk Transportation Industry</font>',
      "logo": 'https://tanktransport.com/wp-content/uploads/2017/08/TTT-logo-1600x800-600x315-cropped.png',
      "favicon": 'https://tanktransport.com/wp-content/uploads/fbrfg/favicon.ico',
      "links": []
    },
    {
      "title": 'Home | Transport Designed',
      "name": 'Transport Designed',
      "url": 'https://transportdesigned.com',
      "language": 'en',
      "category": 'Entertainment',
      "description": 'Transport Designed showcases the best in branding, advertising, design and architecture from the world of public transport.',
      "logo": 'https://transportdesigned.com/wp-content/uploads/pexels-pixabay-373543-400x250.jpg',     
      "favicon": 'https://transportdesigned.com/wp-content/uploads/cropped-TD2021-Social-Media-Graphics-Template-v2_Profile-picture-270x270.png',
      "links": []
    },
    {
      "title": 'Accueil | Transport Magazine',
      "name": 'Transport Magazine',
      "url": 'https://transport-magazine.com',
      "language": 'fr',
      "category": 'General',
      "description": 'Transport Magazinetoujours plus près des gens! Lisez en ligne! Vous pouvez consulter gratuitement la version en cours du magazine. Annonceurs vedettes Actualités Voir toutes les nouvelles Annonceurs Transport Magazine est […]',
      "logo": 'https://transport-magazine.com/wp-content/uploads/2022/06/TransportMagazine_Logo480.png',
      "favicon": 'https://transport-magazine.com/wp-content/uploads/2022/06/cropped-Avatar-TM-270x270.png',
      "links": []
    },
    {
      "title": 'National Transport Authority',
      "name": 'National Transport',
      "url": 'https://www.nationaltransport.ie',
      "language": 'en',
      "category": 'General',
      "description": '',
      "logo": 'https://www.nationaltransport.ie/wp-content/themes/nationaltransport/assets/img/branding/national-transport-logo-colour.svg',
      "favicon": 'https://www.nationaltransport.ie/wp-content/uploads/fbrfg/apple-touch-icon.png',      
      "links": []
    },
    {
      "title": 'GRANDSPORT - O... επαγγελματίας του ερασιτεχνικού ποδοσφαίρου - GRANDSPORT',
      "name": 'GRANDSPORT',
      "url": 'https://grandsport.gr',
      "language": 'el',
      "category": 'Sports',
      "description": 'O... επαγγελματίας του ερασιτεχνικού ποδοσφαίρου',
      "logo": 'https://grandsport.gr/wp-content/uploads/2021/10/grandsport-logo-v3-2x.png',
      "favicon": 'https://grandsport.gr/wp-content/uploads/2020/10/favicon-144px.png',
      "links": []
    },
    {
      "title": 'Noticias de Transporte',
      "name": 'Transporte Profesional',
      "url": 'https://www.transporteprofesional.es',
      "language": 'es',
      "category": 'Business',
      "description": 'Noticias e información del Transporte de Mercancias por carretera y la Logística. Actualidad de CETM y CEFTRAL, Formación y cursos. La industria Auxiliar del camión',
      "logo": "",
      "favicon": 'https://www.transporteprofesional.es/templates/transporte-profesional/images/favicon.ico',
      "links": []
    },
    {
      "title": 'Home | Urban Transport News',
      "name": 'Urban Transport News',
      "url": 'https://urbantransportnews.com',
      "language": 'en',
      "category": 'General',
      "description": 'Urban Transport News brings updates from urban mobility, metro rail, high-speed rail, rapid rail, road transport, aviation and maritime industry in India.',
      "logo": 'https://urbantransportnews.com/assets/frontend/images/Urban%20Transport%20News%20Logo%202020.png',
      "favicon": 'https://urbantransportnews.com/assets/frontend/logo_500px.png',
      "links": []
    },
    {
      "title": 'Home',
      "name": 'American Cranes & Transport',
      "url": 'https://www.americancranesandtransport.com',
      "language": 'en',
      "category": 'Science',
      "description": 'The magazine for the crane, lifting and transport industry.',
      "logo": 'https://www.americancranesandtransport.com/Images/Original/20201221-112454-ACT.jpg',     
      "favicon": 'https://www.americancranesandtransport.com/Images/Original/20201216-144234-androidicon192x192.png',
      "links": []
    },
    {
      "title": 'ACCUEIL - Transport Routier',
      "name": 'Transport Routier Magazine',
      "url": 'https://www.transportroutier.ca',
      "language": 'fr',
      "category": 'Politics',
      "description": 'le site Internet de l’industrie québécoise du camionnage',
      "logo": 'https://www.transportroutier.ca/wp-content/uploads/2016/10/Transport-Rouitier-Logo.png', 
      "favicon": 'https://www.transportroutier.ca/wp-content/uploads/2019/07/cropped-TRANSPORT-ROUTIER-1-270x270.png',
      "links": []
    },
    {
      "title": 'Home',
      "name": 'Transport for Ireland',
      "url": 'https://www.transportforireland.ie',
      "language": 'en',
      "category": 'General',
      "description": 'We bring together information and services to help make public transport across Ireland a little easier for you to use. Plan your journey here.',
      "logo": 'https://www.transportforireland.ie/wp-content/themes/transportforireland/assets/img/branding/transport-for-ireland-logo.svg',
      "favicon": 'https://www.transportforireland.ie/wp-content/themes/transportforireland/assets/img/favicons/apple-touch-icon.png',
      "links": []
    },
    {
      "title": 'Trasporti-Italia Il portale italiano dei trasporti e della logistica- Trasporti-Italia.com',
      "name": 'Trasporti-Italia.com',
      "url": 'https://www.trasporti-italia.com',
      "language": 'it',
      "category": 'Politics',
      "description": 'Trasporti-Italia è la prima testata giornalistica on line dedicata a tutte le modalità di trasporto di merci e persone: dall’autotrasporto alle ferrovie, dalle autostrade del mare alla logistica urbana, alla sicurezza stradale',
      "logo": 'https://www.trasporti-italia.com/wp-content/uploads/2023/02/T-I-logo-new.png',
      "favicon": 'https://www.trasporti-italia.com/wp-content/themes/edi3_child/assets/img/favicons/android-chrome-512x512.png',
      "links": []
    },
    {
      "title": 'Home',
      "name": 'Transform magazine',
      "url": 'https://www.transformmagazine.net',
      "language": 'en',
      "category": 'Business',
      "description": 'Transform magazine, a global print magazine around brand strategy and development.',
      "logo": 'https://www.transformmagazine.net/images/logo.png',
      "favicon": 'https://www.transformmagazine.net/images/favicon/android-icon-192x192.png',
      "links": []
    }
  ]
}

    