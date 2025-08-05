"""Parallel processing utilities for advanced analytics."""

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, List

import numpy as np


def parallel_process(
    data: List[Any],
    process_func: Callable,
    n_workers: int = None,
    use_threads: bool = False,
    **kwargs,
) -> List[Any]:
    """
    Process data in parallel using either threads or processes.

    Args:
        data: List of data items to process
        process_func: Function to apply to each data item
        n_workers: Number of workers to use (defaults to CPU count)
        use_threads: Whether to use threads instead of processes
        **kwargs: Additional arguments to pass to process_func

    Returns:
        List of processed results
    """
    if n_workers is None:
        n_workers = mp.cpu_count()

    # Choose executor based on use_threads flag
    executor_class = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    with executor_class(max_workers=n_workers) as executor:
        # Process data in parallel
        results = list(executor.map(lambda x: process_func(x, **kwargs), data))

    return results


def chunk_data(data: np.ndarray, chunk_size: int, overlap: int = 0) -> List[np.ndarray]:
    """
    Split data into overlapping chunks for parallel processing.

    Args:
        data: Input data array
        chunk_size: Size of each chunk
        overlap: Number of overlapping samples between chunks

    Returns:
        List of data chunks
    """
    chunks = []
    start = 0

    while start < len(data):
        end = min(start + chunk_size, len(data))
        chunk = data[start:end]

        if len(chunk) >= chunk_size // 2:  # Only keep chunks of sufficient size
            chunks.append(chunk)

        start = end - overlap

    return chunks


def merge_results(results: List[Any], merge_func: Callable = None) -> Any:
    """
    Merge results from parallel processing.

    Args:
        results: List of results to merge
        merge_func: Optional custom function to merge results

    Returns:
        Merged result
    """
    if merge_func:
        return merge_func(results)

    # Default merging strategy
    if isinstance(results[0], (np.ndarray, list)):
        return np.concatenate(results)
    elif isinstance(results[0], dict):
        merged = {}
        for result in results:
            merged.update(result)
        return merged
    else:
        return results
        return results
