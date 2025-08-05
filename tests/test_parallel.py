"""Tests for parallel processing utilities."""

import numpy as np
import pytest

from ..advanced_analytics.parallel import chunk_data, merge_results, parallel_process


def test_process_func(x):
    """Test function for parallel processing."""
    return x * 2


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return list(range(100))


@pytest.fixture
def sample_array():
    """Create sample numpy array for testing."""
    return np.arange(1000)


class TestParallelProcessing:
    """Test cases for parallel processing utilities."""

    def test_parallel_process_processes(self, sample_data):
        """Test parallel processing using processes."""
        results = parallel_process(sample_data, test_process_func, n_workers=2)

        assert len(results) == len(sample_data)
        assert all(r == x * 2 for r, x in zip(results, sample_data))

    def test_parallel_process_threads(self, sample_data):
        """Test parallel processing using threads."""
        results = parallel_process(
            sample_data, test_process_func, n_workers=2, use_threads=True
        )

        assert len(results) == len(sample_data)
        assert all(r == x * 2 for r, x in zip(results, sample_data))

    def test_chunk_data_no_overlap(self, sample_array):
        """Test data chunking without overlap."""
        chunk_size = 100
        chunks = chunk_data(sample_array, chunk_size)

        assert all(len(chunk) >= chunk_size // 2 for chunk in chunks)
        assert sum(len(chunk) for chunk in chunks) >= len(sample_array)

    def test_chunk_data_with_overlap(self, sample_array):
        """Test data chunking with overlap."""
        chunk_size = 100
        overlap = 10
        chunks = chunk_data(sample_array, chunk_size, overlap)

        assert all(len(chunk) >= chunk_size // 2 for chunk in chunks)
        assert len(chunks) > len(sample_array) // chunk_size

    def test_merge_results_arrays(self):
        """Test merging array results."""
        arrays = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        merged = merge_results(arrays)

        assert isinstance(merged, np.ndarray)
        assert len(merged) == sum(len(arr) for arr in arrays)

    def test_merge_results_dicts(self):
        """Test merging dictionary results."""
        dicts = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        merged = merge_results(dicts)

        assert isinstance(merged, dict)
        assert len(merged) == sum(len(d) for d in dicts)
        assert all(k in merged for d in dicts for k in d)
