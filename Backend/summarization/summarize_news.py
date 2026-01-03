from transformers import pipeline
class summarization:

    def summarize_news(news):
        pipe = pipeline("summarization", model="Falconsai/text_summarization")
        return pipe(news, max_length=5000, num_return_sequences=1)[0]
        # return {
        #     "summary_text":"Mamdani Sucks"
        # }
