import csv
import os
import pickle
import time


def load_corpus(filename='sample_corpus.txt'):
    corpus = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                word = line.strip()
                if word:
                    corpus.append(word)
    except FileNotFoundError:
        corpus = ['apple', 'application', 'apply', 'aptitude']
    return corpus


def save_structure(ds, filename: str):
    with open(filename, 'wb') as f:
        pickle.dump(ds, f)


def load_structure(cls, filename: str):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        return None


def initialize_structure(structures, corpus_file='sample_corpus.txt'):
    corpus = load_corpus(corpus_file)
    for name, ds in structures.items():
        filename = f"{name.lower()}_structure.pkl"

        loaded_ds = load_structure(type(ds), filename)
        if loaded_ds is not None:
            structures[name] = loaded_ds
            continue
        ds.bulk_insert(corpus)
        save_structure(ds, filename)

    return structures


def calculate_accuracy(suggestions, prefix, corpus):
    ground_truth = set(word for word in corpus if word.startswith(prefix))

    if not ground_truth:
        return 0.0, 0, 0
    correct = len(set(suggestions) & ground_truth)
    accuracy = (correct / len(ground_truth)) * 100

    return accuracy, correct, len(ground_truth)


def save_results_to_csv(results, filename='benchmark_results.csv'):
    headers = ['Data Structure', 'Avg Time (ms)', 'Avg Accuracy (%)', 'Avg Memory (KB)',
               'Avg Suggestions', 'Build Time (ms)', 'Search Time (ms)', 'Time Complexity', 'Space Complexity']

    rows = []
    for ds_name, metrics in results.items():
        row = [
            ds_name,
            f"{metrics['avg_time']:.3f}",
            f"{metrics['avg_accuracy']:.1f}",
            f"{metrics['avg_memory']:.1f}",
            f"{metrics['avg_suggestions']:.1f}",
            f"{metrics.get('build_time', 0):.3f}",
            f"{metrics.get('search_time', 0):.3f}",
            metrics.get('time_complexity', 'N/A'),
            metrics.get('space_complexity', 'N/A')
        ]
        rows.append(row)

    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def print_performance_table(results, prefix="Overall"):
    print(f"\n{'='*60}")
    print(f"Performance Summary for '{prefix}'")
    print(f"{'='*60}")
    print(f"{'Structure':<15} {'Time (ms)':<10} {'Accuracy (%)':<12} {'Memory (KB)':<12} {'Suggestions':<12}")
    print("-" * 60)

    for ds_name, metrics in results.items():
        time_val = metrics.get('avg_time', metrics.get('time', 0))
        accuracy_val = metrics.get('avg_accuracy', metrics.get('accuracy', 0))
        memory_val = metrics.get('avg_memory', metrics.get('memory', 0))
        suggestions_val = metrics.get(
            'avg_suggestions', metrics.get('suggestions', 0))

        print(f"{ds_name:<15} {time_val:<10.2f} {accuracy_val:<12.2f} {memory_val:<12.2f} {suggestions_val:<12.2f}")

    print(f"{'='*60}")


def rank_structures(results):
    def score(ds):
        time_val = results[ds].get('avg_time', results[ds].get('time', 0))
        accuracy_val = results[ds].get(
            'avg_accuracy', results[ds].get('accuracy', 0))
        memory_val = results[ds].get(
            'avg_memory', results[ds].get('memory', 0))

        # Higher accuracy -> higher score, lower time & memory -> higher score
        return (
            accuracy_val,
            -time_val,           # lower time is better
            -memory_val          # lower memory is better
        )

    weights = {'accuracy': 0.5, 'time': 0.3, 'memory': 0.1, 'suggestions': 0.1}
    scores = {}
    for ds, vals in results.items():
        accuracy_score = vals.get('avg_accuracy', vals.get('accuracy', 0))
        time_val = vals.get('avg_time', vals.get('time', 0))
        memory_val = vals.get('avg_memory', vals.get('memory', 0))
        suggestions_score = vals.get(
            'avg_suggestions', vals.get('suggestions', 0))

        time_score = 1 / (time_val + 1e-6)
        memory_score = 1 / (memory_val + 1e-6)

        scores[ds] = (weights['accuracy'] * accuracy_score +
                      weights['time'] * time_score * 100 +
                      weights['memory'] * memory_score * 100 +
                      weights['suggestions'] * suggestions_score)

    ranked = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return ranked


def get_prefixes_for_testing(corpus, count=6):
    common_prefixes = ['pro', 'com', 'sta', 'int', 'app', 'dat']

    valid_prefixes = []
    for prefix in common_prefixes:
        if any(word.startswith(prefix) for word in corpus):
            valid_prefixes.append(prefix)
        if len(valid_prefixes) >= count:
            break

    return valid_prefixes[:count]


def validate_implementations(structures):
    required_methods = ['insert', 'search',
                        'bulk_insert', 'mem_usage', 'complexity']
    all_valid = True
    for name, ds in structures.items():
        for method in required_methods:
            if not hasattr(ds, method):
                all_valid = False

    return all_valid


def benchmark_build_time(structures, corpus):
    build_times = {}
    for name, ds in structures.items():
        start_time = time.time()
        ds.bulk_insert(corpus)
        end_time = time.time()
        build_times[name] = (end_time - start_time) * 1000  # in ms
    return build_times


def benchmark_search_time(structures, prefixes, runs=3):
    search_times = {name: [] for name in structures.keys()}
    for prefix in prefixes:
        for run in range(runs):
            for name, ds in structures.items():
                start_time = time.time()
                ds.search(prefix)
                end_time = time.time()
                search_times[name].append(
                    (end_time - start_time) * 1000)  # in ms
    avg_search_times = {name: sum(times) / len(times)
                        for name, times in search_times.items()}
    return avg_search_times


def simulate_scalability(structures, corpus_sizes):
    scalability_results = {name: [] for name in structures.keys()}
    for size in corpus_sizes:
        subset_corpus = load_corpus()[:size]
        for name, ds in structures.items():
            ds_copy = type(ds)()
            start_time = time.time()
            ds_copy.bulk_insert(subset_corpus)
            end_time = time.time()
            build_time = (end_time - start_time) * 1000
            memory = ds_copy.mem_usage()
            scalability_results[name].append(
                {'size': size, 'build_time': build_time, 'memory': memory})
    return scalability_results
