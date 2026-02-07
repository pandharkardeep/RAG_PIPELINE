
from llama_cpp import Llama
import os


class LLMService:
    """
    Service for generating tweets using local GGUF LLM models via llama-cpp-python
    Uses on-demand loading for better resource management in deployed systems
    """
    def load_prompt(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def __init__(self, model_path: str = None):
        """
        Initialize the LLM service
        
        Args:
            model_path (str): Path to the GGUF model file
        """
        if model_path is None:
            # Default to the Llama 3.2 model in the Backend directory
            model_path = os.path.join(os.path.dirname(__file__), "..", "Llama-3.2-3B-Instruct-Q4_K_M.gguf")
        
        self.model_path = os.path.abspath(model_path)
        self.model = None
        print(f"LLM Service initialized (model: {os.path.basename(self.model_path)})")
    
    def _load_model(self):
        """
        Load the model on-demand
        This approach saves memory when the service is not actively being used
        """
        if self.model is None:
            print(f"Loading model: {os.path.basename(self.model_path)}...")
            try:
                self.model = Llama(
                    model_path=self.model_path,
                    n_ctx=4096,  # Context window
                    n_threads=4,  # CPU threads
                    n_gpu_layers=0,  # Set > 0 if you have GPU support compiled
                    verbose=False
                )
                print(f"✓ Model loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                raise
    
    def generate_tweets(self, query: str, count: int = 8, max_length: int = 280, context_articles: list = None) -> list:
        """
        Generate tweets based on a query, optionally using context from retrieved articles (RAG)
        
        Args:
            query (str): The topic or query to generate tweets about
            count (int): Number of tweets to generate (default: 8)
            max_length (int): Maximum length per tweet in characters (default: 280)
            context_articles (list): Optional list of article dictionaries with 'text', 'filename', 'score'
        
        Returns:
            list: List of generated tweet strings
        """
        # Load model if not already loaded
        self._load_model()
        
        tweets = []
        
        # Build context section if articles are provided
        context_section = ""
        if context_articles and len(context_articles) > 0:
            context_section = "You are generating tweets based on the following news articles:\n\n"
            for i, article in enumerate(context_articles, 1):
                article_text = article.get('text', '')[:10000]  # Limit each article to 10000 chars
                filename = article.get('filename', 'Unknown')
                context_section += f"Article {i}:\n{article_text}\nSource: {filename}\n\n"
            
            context_section += f"\nWrite a Twitter thread consisting of exactly {count} tweets about the topic below.\n {query}"
            print(os.getcwd())
            context_section += self.load_prompt("D:\\Projects\\RAG_PIPELINE\\Backend\\services\\prompt.txt")
            context_section += f"Output rules:\n- Return EXACTLY {count} tweets\n- Each tweet must be under {max_length} characters\n- Do NOT number tweets"
        else:
            print("Fallback to original prompt")
            # Fallback to original prompt if no context
            context_section = f"""Generate {count} engaging tweets about: {query}
Each tweet should be:
- Informative and engaging
- Maximum 280 characters
- Professional but conversational tone
- Include relevant hashtags where appropriate
- Use proper grammar and spelling
- Each tweet should be seperated by two lines (basically \n\n )
- Only include tweets, nothing else. Do not include any additional text.
Format : 
Tweet 1 : Content \n\n
Tweet 2 : Content \n\n
Tweet 3 : Content \n\n and so on.
be strict with formatting.
Tweet 1:"""
        
        prompt = context_section
        
        try:
            # Generate text using llama-cpp
            output = self.model(
                prompt,
                max_tokens=max_length * count + 150,  # Extra tokens for formatting
                temperature=0.7,
                top_p=0.9,
                stop=["</s>", "<|eot_id|>", "<|end_of_text|>"],
                echo=False
            )
            
            # Extract generated text
            generated_content = output["choices"][0]["text"].strip()
            print(generated_content)
            
            # Split by "Tweet" markers and clean up
            raw_tweets = []
            
            # Try to parse structured output first
            if "Tweet" in generated_content:
                parts = generated_content.split("Tweet")
                for part in parts:
                    if part.strip():
                        # Remove tweet number and clean
                        tweet_text = part.strip()
                        # Remove leading numbers and colons
                        tweet_text = tweet_text.lstrip("0123456789:).").strip()
                        if tweet_text and len(tweet_text) > 50:
                            raw_tweets.append(tweet_text)
            else:
                # Primary fallback: split by double newlines (paragraph separation)
                paragraphs = generated_content.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    # Skip preamble content
                    if not para or len(para) < 50:
                        continue
                    # Skip instruction/planning lines
                    lower_para = para.lower()
                    if any(skip in lower_para for skip in [
                        'the thread should', 'the thread will', 'here is the thread',
                        'based on articles', 'brief introduction', 'key findings',
                        'future implications', 'output rules', 'tweet must be'
                    ]):
                        continue
                    # Skip numbered lists (1. 2. 3.)
                    if para[0].isdigit() and (para[1] == '.' or (len(para) > 2 and para[2] == '.')):
                        continue
                    raw_tweets.append(para)
            
            # Clean and limit tweets to requested count
            for tweet in raw_tweets[:count]:
                # Limit to 280 characters
                cleaned_tweet = tweet.strip()
                if cleaned_tweet:
                    tweets.append(cleaned_tweet)
            
            # If we didn't get enough tweets, generate simple fallback tweets
            while len(tweets) < count:
                if context_articles and len(context_articles) > 0:
                    fallback = f"Key insights from recent articles about {query}. #News #{query.replace(' ', '')[:20]}"
                else:
                    fallback = f"Interesting insights about {query}. Stay tuned for more updates! #{query.replace(' ', '')[:20]}"
                tweets.append(fallback)
                
        except Exception as e:
            print(f"❌ Error generating tweets: {e}")
            # Return fallback tweets on error
            for i in range(count):
                tweets.append(f"Tweet {i+1} about {query}. #AI #TweetGeneration")
        
        return tweets
    
    def unload_model(self):
        """
        Unload the model from memory to free up resources
        Useful for deployed systems with limited resources
        """
        if self.model is not None:
            del self.model
            self.model = None
            print("✓ Model unloaded from memory")
