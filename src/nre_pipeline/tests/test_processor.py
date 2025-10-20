from multiprocessing import Manager
from typing import List
from loguru import logger
from nre_pipeline.common import setup_logging
from nre_pipeline.models._nlp_result import NLPResultFeatures
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document

from nre_pipeline.models._nlp_result_item import NLPResultFeature
from nre_pipeline.processor._noop import NoOpProcessor
from nre_pipeline.processor.consts import TQueueItem


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
    return NLPResultFeatures(
        note_id=doc.note_id,
        result_features=[
            NLPResultFeature(key="first_word", value=first_token),
            NLPResultFeature(key="last_word", value=last_token),
            NLPResultFeature(key="token_count", value=token_count),
            NLPResultFeature(key="the_count", value=the_count),
            NLPResultFeature(key="fraction_of_thes", value=fraction_of_thes),
        ],
    )


if __name__ == "__main__":
    setup_logging(False)
    import queue

    with Manager() as mgr:

        processing_queue = mgr.Queue()
        halt_event = mgr.Event()
        processor = NoOpProcessor(
            processor_id=1, writer_queue=processing_queue, process_interrupt=halt_event
        )

        test_doc_batch: DocumentBatch = generate_mock_document_batch(10)
        mock_documents: List[Document] = test_doc_batch._documents
        expected_results: List[NLPResultFeatures] = [
            create_nlp_result(i, mock_documents) for i in range(len(mock_documents))
        ]
        doc_index = 0

        try:
            results_found = False
            result: TQueueItem
            for result in processor(test_doc_batch).next_result():
                results_found = True
                assert (
                    result == expected_results[doc_index]
                ), f"Mismatch at document index {doc_index}"
                doc_index += 1

            assert (
                results_found
            ), "No results were returned by processor_queue.next_result()."
            assert len(mock_documents) == len(
                expected_results
            ), "Mismatch in document count."
        except AssertionError as e:
            logger.error(f"Test failed at document index {doc_index}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during processor test: {e}")
            raise
        else:
            logger.success("Test Complete")
