import logging
from pathlib import Path
from typing import Self
from operator import attrgetter
from scipy.stats import spearmanr

from matplotlib import pyplot as plt
import pandas as pd
from scipy.stats import pearsonr
from sklearn import linear_model

from type import FileName, Problem, Pair, Category, PromptType, DataFileName, EvalFileName

class PreprocessData:
    def __init__(self, path: Path):
        self.path = path
    
    def load(self):
        logging.info(f"PreprocessData(preprocess_path={self.path}).load()")
        self.pairs =    {category: {pair   .pair_id   : pair    for pair    in Pair   .load(category=category, json_path=self.path / category.value / DataFileName.PAIRS_JSON   .value)} for category in Category.all_eval_categories()}
        self.problems = {category: {problem.problem_id: problem for problem in Problem.load(category=category, json_path=self.path / category.value / DataFileName.PROBLEMS_JSON.value)} for category in Category.all_eval_categories()}

class EvalData:
    def __init__(self, eval_path: Path):
        self.eval_path = eval_path
        self.zero_only_path = eval_path / "zero-prompt-type-only"
        self.four_all_path = eval_path / "four-prompt-types"

        zero_only_model_families = [path.name for path in self.zero_only_path.iterdir() if path.is_dir()]
        self.zero_only_model_names_dict = {model_platform: [path.name for path in (self.zero_only_path / model_platform).iterdir() if path.is_dir()] for model_platform in zero_only_model_families}
    
        four_all_model_families = [path.name for path in self.four_all_path.iterdir() if path.is_dir()]
        self.four_all_model_names_dict = {model_platform: [path.name for path in (self.four_all_path / model_platform).iterdir() if path.is_dir()] for model_platform in four_all_model_families}
    
    def zero_only_group(self, model_family: str, model_names: list[str] = None, categories: list[Category] = None):        
        if categories is None:
            categories = Category.all_eval_categories()
        
        if model_names is None:
            model_names = self.zero_only_model_names_dict[model_family]

        paths = [self.zero_only_path / model_family / model_name / category.value / EvalFileName.PAIR_JSON.value for model_name in model_names for category in categories]
        return EvalDataGroup(paths=paths)
    
    def zero_only_group_families(self, model_families: list[str] = None, categories: list[Category] = None):
        if model_families is None:
            model_families = self.zero_only_model_names_dict.keys()

        if categories is None:
            categories = Category.all_eval_categories()

        paths = [self.zero_only_path / model_family / model_name / category.value / EvalFileName.PAIR_JSON.value for model_family in model_families for model_name in self.zero_only_model_names_dict[model_family] for category in categories]
        return EvalDataGroup(paths=paths)
    
    def four_all_group(self, model_family: str, model_names: list[str] = None, prompt_types: list[PromptType] = None, categories: list[Category] = None):        
        if prompt_types is None:
            prompt_types = PromptType.all_prompt_types()

        if categories is None:
            categories = Category.all_eval_categories()
        
        if model_names is None:
            model_names = self.four_all_model_names_dict[model_family]

        paths = [self.four_all_path / model_family / model_name / prompt_type.value / category.value / EvalFileName.PAIR_JSON.value for model_name in model_names for prompt_type in prompt_types for category in categories]
        return EvalDataGroup(paths=paths)

    def four_all_group_families(self, model_families: list[str] = None, prompt_types: list[PromptType] = None, categories: list[Category] = None):
        if model_families is None:
            model_families = self.four_all_model_families

        if prompt_types is None:
            prompt_types = PromptType.all_prompt_types()

        if categories is None:
            categories = Category.all_eval_categories()

        paths = [self.four_all_path / model_family / model_name / prompt_type.value / category.value / EvalFileName.PAIR_JSON.value for model_family in model_families for model_name in self.four_all_model_names_dict[model_family] for prompt_type in prompt_types for category in categories]
        return EvalDataGroup(paths=paths)

class EvalDataGroup:
    def __init__(self, paths: list[Path]):
        self.pair_json_paths = paths

    @property
    def pairs(self):
        if  hasattr(self, "_pairs"):
            return self._pairs
        
        logging.info(f"EvalDataForModelPromptTypeCategory(pair_json_paths={self.pair_json_paths}).pairs")
        pair_groups = [Pair.load(category=None, json_path=pair_json_path) for pair_json_path in self.pair_json_paths]
        self._pairs = [pair for pair_group in pair_groups for pair in pair_group]
        return self._pairs

    def stat(self):
        paths = self.pair_json_paths
        pairs = self.pairs
        type(self).stat_pairs(paths=paths, pairs=pairs)
    
    def similarity_graph(self, path: Path, category: Category, preprocess_data: PreprocessData, seperator_count: int):
        paths = self.pair_json_paths
        pairs = self.pairs
        type(self).similarity_graph_pairs(path=path, category=category, paths=paths, pairs=pairs, preprocess_data=preprocess_data, seperator_count=seperator_count)
    
    def length_graph(self, path: Path, category: Category, preprocess_data: PreprocessData, seperator_count: int):
        paths = self.pair_json_paths
        pairs = self.pairs
        type(self).length_graph_pairs(path=path, category=category, paths=paths, pairs=pairs, preprocess_data=preprocess_data, seperator_count=seperator_count)
    
    @classmethod
    def stat_groups(cls, eval_data_groups: list[Self]):
        paths = [path for eval_data_group in eval_data_groups for path in eval_data_group.pair_json_paths]
        pairs = [pair for eval_data_group in eval_data_groups for pair in eval_data_group.pairs]
        cls.stat_pairs(paths=paths, pairs=pairs)
    
    @classmethod
    def stat_pairs(cls, paths: list[Path], pairs: list[Pair]):
        if not pairs:
            return

        # Calculate metrics
        TP = sum([1 for pair in pairs if pair.truth_label == pair.eval_pred_fixed_label and pair.eval_pred_fixed_label == True ])
        TN = sum([1 for pair in pairs if pair.truth_label == pair.eval_pred_fixed_label and pair.eval_pred_fixed_label == False])
        FP = sum([1 for pair in pairs if pair.truth_label != pair.eval_pred_fixed_label and pair.eval_pred_fixed_label == True ])
        FN = sum([1 for pair in pairs if pair.truth_label != pair.eval_pred_fixed_label and pair.eval_pred_fixed_label == False])

        # Total counts
        total = TP + TN + FP + FN

        # Metrics calculations
        total_accuracy = (TP + TN) / total if total > 0 else -1
        accuracy_true  = TP / (TP + FN) if (TP + FN) > 0 else -1  # For truth_label = True
        accuracy_false = TN / (TN + FP) if (TN + FP) > 0 else -1  # For truth_label = False
        precision      = TP / (TP + FP) if (TP + FP) > 0 else -1
        recall         = TP / (TP + FN) if (TP + FN) > 0 else -1
        f1_score       = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Print the results
        print(f"===========stat===========[Start]")
        for path in paths:
            print(path)
        print(f"total: {total}")
        print(f"TP: {TP}")
        print(f"TN: {TN}")
        print(f"FP: {FP}")
        print(f"FN: {FN}")
        print(f"Total Accuracy: {total_accuracy:.4f}")
        print(f"Accuracy (truth_label=True): {accuracy_true:.4f}")
        print(f"Accuracy (truth_label=False): {accuracy_false:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1_score:.4f}")
        print(f"===========stat===========[End]")
    
    @classmethod
    def similarity_graph_pairs(cls, path: Path, pairs_dict: dict[Category, list[Pair]], preprocess_data: PreprocessData, seperator_count: int):

        # Calculate metrics

        def similarity(pair: Pair):
            pair_data = preprocess_data.pairs[pair.category][pair.pair_id]
            value = (pair_data.program_1_similarity + pair_data.program_2_similarity) / 2
            return value

        eq_counts           = {category: [0] * seperator_count for category in pairs_dict.keys()}
        neq_counts          = {category: [0] * seperator_count for category in pairs_dict.keys()}
        eq_accurate_counts  = {category: [0] * seperator_count for category in pairs_dict.keys()}
        neq_accurate_counts = {category: [0] * seperator_count for category in pairs_dict.keys()}
        eq_accuracies       = [None] * seperator_count
        neq_accuracies      = [None] * seperator_count

        each_category_count = len(pairs_dict[Category.DCE])

        for category in pairs_dict.keys():
            pairs = pairs_dict[category]
            eq_count  = sum([1 for pair in pairs_dict[category] if pair.truth_label == True])
            neq_count = sum([1 for pair in pairs_dict[category] if pair.truth_label == False])
            assert(eq_count == each_category_count / 2 and neq_count == each_category_count / 2)

            for pair in pairs:
                pair.similarity = similarity(pair=pair)
            sorted_pairs = sorted(pairs, key=attrgetter("similarity"))
            max_count = each_category_count / 2 / seperator_count # count / 2 / seperator_count

            eq_index = 0
            neq_index = 0
            for pair in sorted_pairs:
                if pair.truth_label == True:
                    eq_counts[category][eq_index] += 1
                    if pair.truth_label == pair.eval_pred_fixed_label:
                        eq_accurate_counts[category][eq_index] += 1
                    if eq_counts[category][eq_index] >= max_count:
                        eq_index += 1
                else:
                    neq_counts[category][neq_index] += 1
                    if pair.truth_label == pair.eval_pred_fixed_label:
                        neq_accurate_counts[category][neq_index] += 1
                    if neq_counts[category][neq_index] >= max_count:
                        neq_index += 1

        for i in range(seperator_count):
            eq_accurate_count = 0
            eq_count = 0
            neq_accurate_count = 0
            neq_count = 0
            for category in pairs_dict.keys():
                eq_accurate_count  += eq_accurate_counts[category][i]
                eq_count           += neq_counts[category][i]
                neq_accurate_count += neq_accurate_counts[category][i]
                neq_count          += neq_counts[category][i]
            
            eq_accuracies[i] = eq_accurate_count / eq_count
            neq_accuracies[i] = neq_accurate_count / neq_count
        
        # Create the plot
        plt.figure(figsize=(8, 5))   
        
        print(eq_counts)     
        x_values =  list(range(seperator_count))
        plt.plot(x_values, eq_accuracies, marker='o', linestyle='-', color='r', label='EQ Accuracy')
        
        print(neq_counts)     
        x_values =  list(range(seperator_count))
        plt.plot(x_values, neq_accuracies, marker='o', linestyle='-', color='b', label='NEQ Accuracy')

        # Labels and title
        plt.xlabel('Similarity Index')
        plt.ylabel('Accuracy')
        plt.title(f'Accuracy vs Similarity All Categories')
        plt.xticks(x_values)
        plt.ylim(0, 1)  # Assuming accuracy is between 0 and 1
        plt.grid(True)
        plt.legend()

        # Show the plot
        path.mkdir(parents=True, exist_ok=True)
        plt.savefig(path / f"similarity_plot_all.png" , format="png", bbox_inches="tight")

    @classmethod
    def length_graph_pairs(cls, path: Path, category: Category, paths: list[Path], pairs: list[Pair], preprocess_data: PreprocessData, seperator_count: int):
        if not pairs:
            return

        # Calculate metrics
        count        = len(pairs)
        eq_count     = sum([1 for pair in pairs if pair.truth_label == True])
        neq_count    = sum([1 for pair in pairs if pair.truth_label == False])

        assert(eq_count == count / 2 and neq_count == count / 2)

        def length(pair: Pair):
            pair_data = preprocess_data.pairs[pair.category][pair.pair_id]
            value = pair_data.program_1_length + pair_data.program_2_length
            return value

        for pair in pairs:
            pair.length = length(pair=pair)
        
        sorted_pairs = sorted(pairs, key=attrgetter("length"))

        max_count = count / 2 / seperator_count

        eq_counts          = [0] * seperator_count
        neq_counts         = [0] * seperator_count
        eq_accurate_count  = [0] * seperator_count
        neq_accurate_count = [0] * seperator_count
        eq_accuracies      = [None] * seperator_count
        neq_accuracies     = [None] * seperator_count
        
        eq_index = 0
        neq_index = 0
        for pair in sorted_pairs:
            if pair.truth_label == True:
                eq_counts[eq_index] += 1
                if pair.truth_label == pair.eval_pred_fixed_label:
                    eq_accurate_count[eq_index] += 1
                if eq_counts[eq_index] >= max_count:
                    eq_index += 1
            else:
                neq_counts[neq_index] += 1
                if pair.truth_label == pair.eval_pred_fixed_label:
                    neq_accurate_count[neq_index] += 1
                if neq_counts[neq_index] >= max_count:
                    neq_index += 1

        for i in range(seperator_count):
            eq_accuracies[i]  =  eq_accurate_count[i] /  eq_counts[i] if  eq_counts[i] > 0 else None
            neq_accuracies[i] = neq_accurate_count[i] / neq_counts[i] if neq_counts[i] > 0 else None

        # Create the plot
        plt.figure(figsize=(8, 5))   
        
        print(eq_counts)     
        x_values =  [i/seperator_count for i in range(seperator_count)]
        plt.plot(x_values, eq_accuracies, marker='o', linestyle='-', color='r', label='EQ Accuracy')
        
        print(neq_counts)     
        x_values =  [i/seperator_count for i in range(seperator_count)]
        plt.plot(x_values, neq_accuracies, marker='o', linestyle='-', color='b', label='NEQ Accuracy')

        # Labels and title
        plt.xlabel('Length Index')
        plt.ylabel('Accuracy')
        plt.title(f'Accuracy vs Length {category.name}')
        plt.ylim(0, 1)  # Assuming accuracy is between 0 and 1
        plt.grid(True)
        plt.legend()

        # Show the plot
        path.mkdir(parents=True, exist_ok=True)
        plt.savefig(path / f"length_plot_{category.name}.png" , format="png", bbox_inches="tight")


"""
class EvalDataUnit:
    def __init__(self, eval_path: Path, model_platform: str, model_name: str, prompt_type: PromptType, category: Category):
        self.model_platform = model_platform
        self.model_name     = model_name
        self.prompt_type    = prompt_type
        self.category       = category
        self.pair_json_path = eval_path / model_platform / model_name / prompt_type.value / category.value / EvalFileName.PAIR_JSON.value
    
    @property
    def pairs(self):
        if  hasattr(self, "_pairs"):
            return self._pairs
        
        logging.info(f"EvalDataForModelPromptTypeCategory(pair_json_path={self.pair_json_path}).pairs")
        self._pairs = Pair.load(category=self.category, json_path=self.pair_json_path)
        return self._pairs
"""

class StatGroup:
    def __init__(self, label: str, pairs: list[Pair], output_path: Path, output_correlation_txt_path: Path):
        self.label        = label
        self.pairs        = pairs
        self.output_path  = output_path
        self.lengths      = [pair.length for pair in self.pairs] 
        self.similarities = [pair.similarity for pair in self.pairs]
        self.accuracies   = [pair.eval_pred_fixed_label == pair.truth_label for pair in self.pairs] 

        self.output_correlation_txt_path = output_correlation_txt_path

    def plot_and_write(self):
        self.plot()
        self.write()

    def plot(self):
        # plot_relationship(x_data=self.lengths     , y_data=self.accuracies, x_label=f"Code Length ({self.label})"    , path=self.output_path /  FileName.STAT_FIG_LENGTH_PNG    .value.format(label=self.label))
        plot_relationship(x_data=self.similarities, y_data=self.accuracies, x_label=f"Code Similarity ({self.label})", path=self.output_path /  FileName.STAT_FIG_SIMILARITY_PNG.value.format(label=self.label))
    
    def write(self):
        # write_correlation(result=pearsonr(self.lengths     , self.accuracies), x_label=f"Code Length ({self.label})"    , path=self.output_correlation_txt_path)
        # write_correlation(result=pearsonr(self.similarities, self.accuracies), x_label=f"Code Similarity ({self.label})", path=self.output_correlation_txt_path)

        # Compute Spearman correlation for all pairs
        spearman_all = spearmanr(self.similarities, self.accuracies)

        # Filter out pairs where self.similarities == 0
        nonzero_similarities = [sim for sim, acc in zip(self.similarities, self.accuracies) if sim != 0]
        nonzero_accuracies = [acc for sim, acc in zip(self.similarities, self.accuracies) if sim != 0]
        # print(f"{self.output_correlation_txt_path}: {len(nonzero_similarities)} nonzero similarities out of {len(self.similarities)} total pairs")

        # Compute Spearman correlation for nonzero similarity pairs
        spearman_nonzero = spearmanr(nonzero_similarities, nonzero_accuracies)

        # Write both results
        write_correlation(result=spearman_all, x_label=f"Code Similarity ({self.label}) - All", path=self.output_correlation_txt_path)
        write_correlation(result=spearman_nonzero, x_label=f"Code Similarity ({self.label}) - Nonzero Only", path=self.output_correlation_txt_path)


def plot_relationship(x_data: list, y_data: list, x_label: str, path: Path):
    """Helper function to plot and save graphs for given x and y data."""
    # Create DataFrame
    data = pd.DataFrame({
        "x_data": x_data,
        "accuracy": y_data,
    })

    """
    # Step 1: Filter Outliers
    if "code_length" in filename_suffix.lower():
        data = data[data['x_data'] <= 6000]  # Remove code lengths > 6000
    """

    # Step 2: Fit Linear Regression
    X = data['x_data'].values.reshape(-1, 1)
    y = data['accuracy']
    lin_model = linear_model.LinearRegression()
    lin_model.fit(X, y)
    y_pred = lin_model.predict(X)

    """
    # Step 3: Bin Data for Aggregated Means
    if "moss" in filename_suffix.lower():
        def return_bin():
            # Fixed range for Moss similarity: 0 to 2
            bins = np.linspace(0, 2, 21)  # 20 equally spaced bins between 0 and 2
            bin_width = 0.08
            return bins, bin_width
    else:
        def return_bin():
            range_x_data = data['x_data'].max() - data['x_data'].min()
            num_bins = 10  # Aim for 20 bins
            
            # Use at least 200 as bin width
            bin_width = max(200, range_x_data / num_bins)
            bins = np.arange(data['x_data'].min(), data['x_data'].max() + bin_width, bin_width)
            bin_width = 200
            return bins, bin_width
    bins, bin_width = return_bin()

    data['binned_data'] = pd.cut(data['x_data'], bins)
    binned_means = data.groupby('binned_data')['accuracy'].mean()
    bin_centers = [interval.mid for interval in binned_means.index]
    """

    # Step 4: Plot
    plt.figure(figsize=(10, 6))

    # Scatter plot for raw data points
    plt.scatter(data['x_data'], data['accuracy'], alpha=0.5, s=50,
                color="grey", label="Raw Data Points")

    # Bar plot for binned means
    #plt.bar(bin_centers, binned_means, width=bin_width, alpha=0.7, color="blue", label="Binned Mean Accuracy")

    # Linear regression line
    plt.plot(data['x_data'], y_pred,
            color="red", label="Linear Regression")

    # Labels and legends
    plt.xlabel(x_label)
    plt.ylabel("Accuracy")
    plt.title(f"Accuracy v.s. {x_label}")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path)
    plt.close()
    logging.info(f"[StatGroup] Plot {x_label} plot to \"{path}\"")

def write_correlation(result: tuple[float, float], x_label: str, path: Path):
    r, p = result
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as file:
        file.write(f"Accuracy v.s. {x_label}:\n")
        file.write(f"Spearman correlation coefficient: {r:.4f}\n")
        file.write(f"p-value: {p:.4e}\n")
        if p <= 0.05:
            file.write("Result: Statistically significant relationship at alpha=0.05\n")
        else:
            file.write("Result: No statistically significant relationship at alpha=0.05\n")
        file.write("\n")

    logging.info(f"[StatGroup] Write {x_label} Spearman correlation to \"{path}\"")
