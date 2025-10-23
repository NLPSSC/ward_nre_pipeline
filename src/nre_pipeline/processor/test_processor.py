from multiprocessing import Manager
from typing import List, cast
from loguru import logger
from nre_pipeline.common import setup_logging
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document

from nre_pipeline.models._nlp_result_item import NLPResultFeature
from nre_pipeline.common.base._base_processor import ProcessorQueue
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
                note_id=(i + 1),
                text=doc_text(5),
                metadata={"source": "mock", "index": i},
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
    return NLPResultItem(
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
    setup_logging(verbose=False)
    import queue

    with Manager() as mgr:

        document_batch_inqueue = mgr.Queue()
        nlp_results_outqueue = mgr.Queue()
        halt_event = mgr.Event()

        processor = NoOpProcessor(
            processor_id=1,
            document_batch_inqueue=document_batch_inqueue,
            nlp_results_outqueue=nlp_results_outqueue,
            process_interrupt=halt_event,
        )

        test_doc_batch: DocumentBatch = generate_mock_document_batch(10)

        ###############################################################################
        # Manually load document batch into the input queue
        ###############################################################################
        assert (
            document_batch_inqueue.qsize() == 0
        ), "Input queue should be empty before processing."

        document_batch_inqueue.put(test_doc_batch)

        assert (
            document_batch_inqueue.qsize() == 1
        ), "Input queue should have one item after adding batch."
        logger.debug("Number of batches in queue: {}", document_batch_inqueue.qsize())

        logger.debug("Manually adding QUEUE_EMPTY...")
        document_batch_inqueue.put(QUEUE_EMPTY)
        assert (
            document_batch_inqueue.qsize() == 2
        ), "Input queue should have two items after adding batch and empty marker."

        ###############################################################################
        # Generate mock results to check
        ###############################################################################
        mock_documents: List[Document] = test_doc_batch._documents
        expected_results: List[NLPResultItem] = [
            create_nlp_result(i, mock_documents) for i in range(len(mock_documents))
        ]

        assert (
            nlp_results_outqueue.qsize() == 0
        ), "Output queue should be empty before processing."

        # Initiates direct call to processor, which will halt when complete.
        processor()

        nlp_results: List[NLPResultItem] = []

        try:
            while True:
                
                try:
                    outqueue_item = nlp_results_outqueue.get(block=True, timeout=5)
                except queue.Empty:
                    continue

                if outqueue_item == QUEUE_EMPTY:
                    break
                elif isinstance(outqueue_item, NLPResultItem):
                    nlp_result: NLPResultItem = cast(NLPResultItem, outqueue_item)
                    nlp_results.append(nlp_result)
                else:
                    raise RuntimeError("Unexpected item type in writer queue")

            assert (
                len(nlp_results) > 0
            ), "No results were returned by processor_queue.next_result()."

            note_ids = {n.note_id for n in nlp_results}

            assert len(mock_documents) == len(note_ids), "Mismatch in document count."

        except Exception as e:
            logger.error(f"Unexpected error during processor test: {e}")
            raise
        else:
            logger.success("Test Complete")
