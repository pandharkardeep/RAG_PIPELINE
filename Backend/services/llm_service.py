
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os


class LLMService:
    """
    Service for generating tweets using HuggingFace LLM models
    Uses on-demand loading for better resource management in deployed systems
    """
    def load_prompt(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def __init__(self, model_name: str = "LiquidAI/LFM2.5-1.2B-Instruct"):
        """
        Initialize the LLM service
        
        Args:
            model_name (str): HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"LLM Service initialized (device: {self.device})")
    
    def _load_model(self):
        """
        Load the model and tokenizer on-demand
        This approach saves memory when the service is not actively being used
        """
        if self.model is None or self.tokenizer is None:
            print(f"Loading model: {self.model_name}...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    trust_remote_code=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None,
                    trust_remote_code=True
                )
                
                if self.device == "cpu":
                    self.model = self.model.to(self.device)
                
                print(f"✓ Model loaded successfully on {self.device}")
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                raise
    
    def generate_tweets(self, query: str, count: int = 8, max_length: int = 280, context_articles: list = None) -> list:
        """
        Generate tweets based on a query, optionally using context from retrieved articles (RAG)
        
        Args:
            query (str): The topic or query to generate tweets about
            count (int): Number of tweets to generate (default: 3)
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
                article_text = article.get('text', '')[:10000]  # Limit each article to 1000 chars
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

Tweet 1:"""
        
        prompt = context_section
        
        try:
            # Tokenize the input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048  # Increased to accommodate more articles
            ).to(self.device)
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length * count + 150,  # Extra tokens for formatting
                    temperature=0.7,  # Slightly lower for more factual generation
                    top_p=0.9,
                    do_sample=True,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract tweets from generated text
            # Remove the prompt from the output
            generated_content = generated_text[len(prompt):].strip()
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
                        if tweet_text:
                            raw_tweets.append(tweet_text)
            else:
                # Fallback: split by newlines
                lines = generated_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 20:  # Only keep substantial lines
                        raw_tweets.append(line)
            
            # Clean and limit tweets to requested count
            for tweet in raw_tweets[:count]:
                # Limit to 280 characters
                cleaned_tweet = tweet[:280].strip()
                if cleaned_tweet:
                    tweets.append(cleaned_tweet)
            
            # If we didn't get enough tweets, generate simple fallback tweets
            while len(tweets) < count:
                if context_articles and len(context_articles) > 0:
                    fallback = f"Key insights from recent articles about {query}. #News #{query.replace(' ', '')[:20]}"
                else:
                    fallback = f"Interesting insights about {query}. Stay tuned for more updates! #{query.replace(' ', '')[:20]}"
                tweets.append(fallback[:280])
                
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
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print("✓ Model unloaded from memory")
