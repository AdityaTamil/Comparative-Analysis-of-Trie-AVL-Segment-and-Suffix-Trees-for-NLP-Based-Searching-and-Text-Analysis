from utils import (
    load_corpus, calculate_accuracy, save_results_to_csv, rank_structures,
    get_prefixes_for_testing, validate_implementations, initialize_structure,
    benchmark_build_time, benchmark_search_time, simulate_scalability
)
from suffix_tree import SuffixTree
from segment_tree import SegmentTree
from avl_tree import AVLTree
from trie import Trie
import time
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict
import statistics


class DataStructureComparator:
    def __init__(self):
        self.structures = {
            'Trie': Trie(),
            'AVLTree': AVLTree(),
            'SegmentTree': SegmentTree(),
            'SuffixTree': SuffixTree()
        }

        if not validate_implementations(self.structures):
            print("Implementation validation failed!")
            return
        self.corpus = load_corpus()
        self.structures = initialize_structure(self.structures)

    def benchmark_operation(self, operation, *args, **kwargs):
        results = {}
        for name, ds in self.structures.items():
            start_time = time.time()
            result = getattr(ds, operation)(*args, **kwargs)
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000
            memory_kb = ds.mem_usage()

            results[name] = {
                'time': elapsed_ms,
                'result': result,
                'memory': memory_kb
            }

        return results

    def run_single_test(self, prefix):
        bench_results = self.benchmark_operation('search', prefix)

        results = {}
        for ds_name, data in bench_results.items():
            unique_results = list(dict.fromkeys(data['result']))
            accuracy, correct_count, total_gt = calculate_accuracy(
                unique_results, prefix, self.corpus)
            results[ds_name] = {
                'time': data['time'],
                'accuracy': accuracy,
                'memory': data['memory'],
                'suggestions': len(unique_results),
                'suggestion_list': unique_results[:10]
            }

        print(f"Suggestions for prefix '{prefix}'")
        for ds_name, data in results.items():
            suggestions_str = ', '.join(data['suggestion_list'])
            if len(data['suggestion_list']) < len(bench_results[ds_name]['result']):
                suggestions_str += '...'
            print(f"{ds_name}: {suggestions_str}")

        print(
            f"\n============================================================\nPerformance Summary for '{prefix}'\n============================================================\nStructure       Time (ms)  Accuracy (%) Memory (KB)  Suggestions \n------------------------------------------------------------")
        for ds_name, data in results.items():
            print(
                f"{ds_name:<15} {data['time']:<15.6f} {data['accuracy']:<12.1f} {data['memory']:<12.1f} {data['suggestions']:<12.0f}")
        print("============================================================")

        return results

    def run_benchmark(self, prefixes=None, runs=3):
        if prefixes is None:
            prefixes = get_prefixes_for_testing(self.corpus)

        results = defaultdict(lambda: defaultdict(list))

        for prefix in prefixes:
            for run in range(runs):
                bench_results = self.benchmark_operation('search', prefix)

                for ds_name, data in bench_results.items():
                    unique_results = list(dict.fromkeys(data['result']))

                    accuracy, _, _ = calculate_accuracy(
                        unique_results, prefix, self.corpus)

                    results[ds_name]['time'].append(data['time'])
                    results[ds_name]['accuracy'].append(accuracy)
                    results[ds_name]['memory'].append(data['memory'])
                    results[ds_name]['suggestions'].append(len(unique_results))

        # Benchmark build time
        build_times = benchmark_build_time(self.structures, self.corpus)

        # Benchmark search time
        search_times = benchmark_search_time(self.structures, prefixes, runs)

        # Simulate scalability
        corpus_sizes = [100, 500, 1000, 2000, len(self.corpus)]
        scalability = simulate_scalability(self.structures, corpus_sizes)

        summary = {}
        for ds_name, metrics in results.items():
            summary[ds_name] = {
                'avg_time': sum(metrics['time']) / len(metrics['time']),
                'avg_accuracy': sum(metrics['accuracy']) / len(metrics['accuracy']),
                'avg_memory': sum(metrics['memory']) / len(metrics['memory']),
                'avg_suggestions': sum(metrics['suggestions']) / len(metrics['suggestions']),
                'build_time': build_times[ds_name],
                'search_time': search_times[ds_name],
                'scalability': scalability[ds_name],
                'time_complexity': self.structures[ds_name].complexity()['time'],
                'space_complexity': self.structures[ds_name].complexity()['space']
            }

        return summary

    def plot_results(self, summary, title="Data Structure Comparison"):
        ds_names = list(summary.keys())
        metrics = ['avg_accuracy', 'build_time',
                   'search_time', 'avg_memory', 'avg_suggestions']
        metric_labels = ['Accuracy (%)', 'Build Time (ms)', 'Search Time (ms)',
                         'Memory (KB)', 'Suggestions Count']

        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c',
                  '#d62728']  # Blue, Orange, Green, Red

        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[i//2, i % 2]
            values = [summary[ds][metric] for ds in ds_names]
            bars = ax.bar(ds_names, values, color=colors[:len(ds_names)])

            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_ylabel(label, fontsize=10)
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height(),
                        f'{value:.3f}', ha='center', va='bottom', fontsize=9)

            if metric == 'build_time':
                for j, ds in enumerate(ds_names):
                    complexity = summary[ds]['time_complexity']
                    ax.text(j, values[j] + max(values) * 0.05, complexity,
                            ha='center', va='bottom', fontsize=10, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
            elif metric == 'avg_memory':
                for j, ds in enumerate(ds_names):
                    complexity = summary[ds]['space_complexity']
                    ax.text(j, values[j] + max(values) * 0.05, complexity,
                            ha='center', va='bottom', fontsize=10, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

        # Add scalability plot
        ax_scal = axes[2, 1]
        ax_scal.set_title('Scalability: Build Time vs Corpus Size',
                          fontsize=12, fontweight='bold')
        ax_scal.set_xlabel('Corpus Size')
        ax_scal.set_ylabel('Build Time (ms)')
        for name, data in summary.items():
            sizes = [d['size'] for d in data['scalability']]
            times = [d['build_time'] for d in data['scalability']]
            ax_scal.plot(sizes, times, marker='o', label=name)
        ax_scal.legend()

        plt.tight_layout()
        plt.savefig('comparison_results.png', dpi=300, bbox_inches='tight')

        show_plots = input("Display graphs? (y/n): ").lower().strip()
        if show_plots == 'y':
            plt.show()
        else:
            plt.close()

    def interactive_mode(self):
        """Run interactive mode for testing individual prefixes."""
        while True:
            try:
                prefix = input("Enter prefix: ").strip()

                if prefix.lower() in ['quit', 'exit', 'q']:
                    break
                elif prefix.lower() == 'benchmark':
                    summary = self.run_benchmark()
                    print(f"\n============================================================\nPerformance Summary for 'Benchmark Results'\n============================================================\nStructure       Time (ms)  Accuracy (%) Memory (KB)  Suggestions  Build (ms)  Search (ms)\n------------------------------------------------------------")
                    for ds_name, data in summary.items():
                        print(
                            f"{ds_name:<15} {data['avg_time']:<10.2f} {data['avg_accuracy']:<12.2f} {data['avg_memory']:<12.2f} {data['avg_suggestions']:<12.2f} {data['build_time']:<10.2f} {data['search_time']:<10.2f}")
                    print(
                        "============================================================")
                    ranked = rank_structures(summary)
                    print("Efficiency Ranking:")
                    for i, ds in enumerate(ranked, 1):
                        print(f"  {i}. {ds}")
                    save_results_to_csv(summary)
                    self.plot_results(summary, "Automated Benchmark Results")
                    break
                elif prefix:
                    results = self.run_single_test(prefix)

                    ranked = rank_structures(results)
                    print("Efficiency Ranking for this test:")
                    for i, ds in enumerate(ranked, 1):
                        print(f"  {i}. {ds}")

                    cont = input("Continue testing? (y/n): ").lower().strip()
                    if cont != 'y':
                        break
                else:
                    print("Please enter a valid prefix.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                continue


def main():
    parser = argparse.ArgumentParser(
        description="Compare data structures for NLP autocomplete")
    parser.add_argument('--benchmark', action='store_true')
    parser.add_argument('--prefix', type=str)

    args = parser.parse_args()

    comparator = DataStructureComparator()

    if args.benchmark:
        summary = comparator.run_benchmark()
        print(f"\n============================================================\nPerformance Summary for 'Benchmark Results'\n============================================================\nStructure       Time (ms)  Accuracy (%) Memory (KB)  Suggestions  Build (ms)  Search (ms)\n------------------------------------------------------------")
        for ds_name, data in summary.items():
            print(
                f"{ds_name:<15} {data['avg_time']:<10.3f} {data['avg_accuracy']:<12.1f} {data['avg_memory']:<12.1f} {data['avg_suggestions']:<12.0f} {data['build_time']:<10.3f} {data['search_time']:<10.3f}")
        print("============================================================")
        ranked = rank_structures(summary)
        print("Efficiency Ranking:")
        for i, ds in enumerate(ranked, 1):
            print(f"  {i}. {ds}")
        save_results_to_csv(summary)
        comparator.plot_results(summary, "Automated Benchmark Results")
    elif args.prefix:
        results = comparator.run_single_test(args.prefix)
        ranked = rank_structures(results)
        print("Efficiency Ranking:")
        for i, ds in enumerate(ranked, 1):
            print(f"  {i}. {ds}")
    else:
        comparator.interactive_mode()


if __name__ == "__main__":
    main()
