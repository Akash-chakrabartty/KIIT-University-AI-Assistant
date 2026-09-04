import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge.ingest import make_chunks


def test_make_chunks_respects_max_chars():
    text = ("Students may apply for a grade-improvement examination once per "
             "academic year, subject to eligibility under clause 4.2.\n\n"
             "A student is eligible if their CGPA is at least 6.0 and they "
             "have no more than 2 active backlogs.\n\n") * 5
    chunks = make_chunks(text, max_chars=200)
    assert len(chunks) > 1
    for c in chunks:
        # allow a little slack since we don't split mid-paragraph
        assert len(c) <= 400


def test_make_chunks_drops_near_empty():
    assert make_chunks("   \n\n  ") == []


def test_make_chunks_single_short_paragraph():
    text = "This is a short page with one paragraph only."
    chunks = make_chunks(text, max_chars=1200)
    assert chunks == [text]


def test_make_chunks_splits_huge_blob_with_no_blank_lines():
    sentence = "This is one regulation sentence about examinations. "
    text = (sentence * 60).strip()
    chunks = make_chunks(text, max_chars=200)
    assert len(chunks) > 1
