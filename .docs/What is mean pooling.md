# Review Notes for Mean Pooling

Mean pooling is a technique used in Natural Language Processing (NLP) to convert a sequence of vector embeddings
into a single fixed-size vector. In the context of transformer models like BERT, mean pooling aggregates the
individual token embeddings for a sentence by averaging them to create a single sentence-level embedding. 

How it works 

When a transformer model processes a sentence, it produces a vector embedding for each token (word or subword). For example, 
if the sentence "The cat sat" is tokenized as ["The", "cat", "sat"], the model would produce three corresponding token embeddings:
- $\text{embedding}_{\text{"The"}}$
- $\text{embedding}_{\text{"cat"}}$
- $\text{embedding}_{\text{"sat"}}$

The raw output for a sentence of \(N\) tokens is a matrix with a shape of [sequence_length, hidden_size], where hidden_size is the dimension of the embedding vectors. Mean pooling takes these \(N\) vectors and averages them to produce a single vector of shape [hidden_size]. The process typically involves these steps: 

1. **Get token embeddings:** Feed the tokenized sentence into the model to get the sequence of output embeddings.
2. **Handle padding:** During batch processing, sentences are padded to have the same length. The mean pooling operation uses an attention_mask to identify and ignore these padding tokens so they don't skew the average.
3. **Calculate the average:** The embeddings of all non-padding tokens are summed, and the result is divided by the number of non-padding tokens. 

Mean pooling vs. CLS token 

Another common way to get a sentence embedding is to use the final hidden state of the special [CLS] token. However, mean pooling is often preferred for generating general-purpose sentence embeddings for a few key reasons: 
- Captures overall meaning: Mean pooling, by averaging across all tokens, creates a balanced representation that incorporates information from the entire sentence. This can better represent the full semantic context than relying on a single token.
- Superior performance: For tasks like semantic similarity, mean pooling has often been shown to produce more comprehensive and robust sentence representations than relying solely on the [CLS] token's embedding.
- Pre-training objective: The [CLS] token was originally used in BERT for the Next Sentence Prediction (NSP) pre-training task. This means its embedding is biased towards a specific classification task, while mean pooling provides a more neutral, general-purpose representation. 

Implementing mean pooling

For practical implementation, libraries like sentence-transformers automatically handle the mean pooling process, providing a simple way to encode sentences. For more granular control using the transformers library, you would follow the manual steps of masking and averaging the token embeddings, as shown in the previous answer. 
