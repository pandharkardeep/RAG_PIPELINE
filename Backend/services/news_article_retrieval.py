import requests
from bs4 import BeautifulSoup
import re, os
import time, random
import io
from contextlib import redirect_stderr
import pandas as pd
from GoogleNews import GoogleNews
class news_article_retrieval:
    
    def __init__(self, query:str, limit:int):
        self.query = query
        self.df = None
        self.news_ingest = self.news_ingestion(limit)

    def get_data(self):
        return self.df

    def get_ingestion(self):
        return self.news_ingest

    def news_ingestion(self, limit: int = 10):
        """
        Fetch news articles with fallback to cached CSV data
        """
        
        try:
            # Suppress HTTP error messages from GoogleNews library
            f = io.StringIO()
            
            with redirect_stderr(f):
                googleNews = GoogleNews(period='7d', lang='en')
                googleNews.search(self.query)
                all_results = []
                seen_titles = set()
                # Try to get multiple pages, but stop if we hit rate limit
                for i in range(1, 30):  # Reduced from 50 to 10 to avoid rate limits
                    try:
                        googleNews.getpage(i)
                        result = googleNews.results()
                        if not result:
                            break
                        for item in result:
                            if item['title'] not in seen_titles:
                                seen_titles.add(item['title'])
                                all_results.append(item)
                            if len(all_results) >= limit:
                                break
                        else:
                            break 
                     # Stop if no more results
                        if len(all_results) >= limit:
                            break
                    except Exception:
                        break  # Stop on any error (including rate limit)
            
            # If we got results, process them
            if all_results:
                self.df = pd.DataFrame(all_results).drop_duplicates(subset=['title'], keep='last').head(limit)
                self.df.reset_index(drop=True, inplace=True)
                self.df['link'] = [re.split("&ved", link)[0] for link in self.df['link']]
                self.df.drop(columns = ['media', 'date', 'datetime', 'img'], inplace = True)
                articles = self.df.to_dict('records')
                
                return {
                    "success": True,
                    "data": articles,
                    "count": len(articles),
                    "source": "GoogleNews"
                }
            else:
                # No results from GoogleNews, fall back to CSV
                raise Exception("No results from GoogleNews")
                
        except Exception as e:
            # Fallback to cached CSV data
            print(f"Falling back to CSV data. Reason: {str(e)}")
            try:
                self.df = pd.read_csv('D:/Projects/RAG_PIPELINE/Backend/ignores/NewsArticles.csv')
                
                # Filter by query if possible (simple text search in title/description)
                if 'title' in self.df.columns:
                    df_filtered = self.df[self.df['title'].str.contains(self.query, case=False, na=False)]
                    if len(df_filtered) > 0:
                        self.df = df_filtered
                
                # Limit results
                self.df = self.df.head(limit)
                
                # Convert to list of dicts
                if 'link' in self.df.columns:
                    self.df.loc[:, 'link'] = [re.split("&ved", str(link))[0] for link in self.df['link']]
                self.df.drop(columns = ['media', 'date', 'datetime', 'img'], inplace = True)
                articles = self.df.to_dict('records')
                # print(self.df.to_json())
                
                return {
                    "success": True,
                    "data": articles,
                    "count": len(articles),
                    "source": "Cached CSV"
                }
            except Exception as csv_error:
                # If CSV also fails, return empty result
                print(f"CSV fallback also failed: {str(csv_error)}")
                return {
                    "success": False,
                    "data": [],
                    "count": 0,
                    "error": "No data available",
                    "source": "None"
                }
    
    def retrieve(self):
        try:
            latest_link = self.df['link']
        except:
            print(self.df)
            raise Exception("LINK Column not found")
        description = []
        for i in latest_link:

            try:
                response = requests.get(i, timeout=10)

                if response.status_code == 200:
                    html_content = response.text
                else:
                    print(f"Failed to retrieve: {i} (Status code: {response.status_code})")
                    description.append("Failed to retrieve the webpage.")
                    continue  
            
                soup = BeautifulSoup(html_content, "html.parser")
                paragraphs = soup.find_all("p")

                page_description = " ".join([p.get_text() for p in paragraphs])
                description.append(page_description)

            except requests.exceptions.RequestException as e:
                print(f"Error retrieving {i}: {e}")
                description.append("Failed to retrieve the webpage.")
                continue 
            
            time.sleep(random.uniform(1, 3))
        self.df['description'] = description

        folder_name = "NEWS_data"
        os.makedirs(folder_name, exist_ok=True)

        for index, row in self.df.iterrows():
            #print("o", end = "")
            with open(os.path.join(folder_name, f"description_{index + 1}.txt"), "w", encoding="utf-8") as f:
                f.write(row['description'])

        print("Descriptions have been saved in the 'NEWS_data' folder.")

