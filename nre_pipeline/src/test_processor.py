from typing import List

from loguru import logger
from nre_pipeline import setup_logging
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document
from nre_pipeline.models._nlp_result import NLPResult, NLPResultItem
from nre_pipeline.processor._noop import NoOpProcessor


def doc_text(num_sentences: int):
    from wonderwords import RandomSentence

    s = RandomSentence()
    sentences = "  ".join([s.sentence() for _ in range(num_sentences)])
    return sentences


def generate_mock_document_batch(n):
    """Generate a batch of n mock documents for testing."""
    return DocumentBatch(
        [
            Document(
                note_id=1, text=doc_text(5), metadata={"source": "mock", "index": i}
            )
            for i in range(n)
        ]
    )


def create_nlp_result(index, docs):
    doc = docs[index]
    tokens = doc.text.split()
    first_token = tokens[0]
    last_token = tokens[-1]
    token_count = len(tokens)
    the_count = sum(1 for token in tokens if token.lower() == "the")
    fraction_of_thes = the_count / len(tokens) if len(tokens) > 0 else 0
    return NLPResult(
        note_id=doc.note_id,
        results=[
            NLPResultItem(key="first_word", value=first_token),
            NLPResultItem(key="last_word", value=last_token),
            NLPResultItem(key="token_count", value=token_count),
            NLPResultItem(key="the_count", value=the_count),
            NLPResultItem(key="fraction_of_thes", value=fraction_of_thes),
        ],
    )


if __name__ == "__main__":
    setup_logging(False)
    processor = NoOpProcessor(processor_id=1)

    test_doc_batch: DocumentBatch = generate_mock_document_batch(10)
    mock_documents: List[Document] = test_doc_batch._documents
    expected_results: List[NLPResult] = [
        create_nlp_result(i, mock_documents) for i in range(len(mock_documents))
    ]
    doc_index = 0

    for idx, result in enumerate(processor(test_doc_batch)):
        assert result == expected_results[idx]

    logger.success("Test Complete")
