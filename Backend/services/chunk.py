from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
class chunk:
    def __init__(self ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

    def textsplit(self):
        """
        Split text files into chunks
        
        Returns:
            list: List of dictionaries with chunk text and metadata
        """
        documents = []
        filenames = []
        
        for filename in os.listdir("NEWS_data"):
            if filename.endswith(".txt"):
                with open(os.path.join("NEWS_data", filename), 'r', encoding='utf-8') as file:
                    documents.append(file.read())
                    filenames.append(filename)

        all_chunks = []
        print(f"Processing {len(documents)} documents...")
        
        for doc_idx, doc in enumerate(documents):
            chunks = self.text_splitter.split_text(doc)
            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'filename': filenames[doc_idx],
                    'chunk_id': chunk_idx,
                    'doc_id': doc_idx
                })
        
        print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    