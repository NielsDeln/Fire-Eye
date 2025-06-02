import matplotlib.pyplot as plt
import numpy as np


def sensitivity_analysis(designs, criteria_weight, change_value):
    for design, init_scores in designs.items():
        for i in range(len(criteria_weight)):
            new_criteria_weight = criteria_weight.copy()
            new_criteria_weight[i] += change_value
            for j in range(len(criteria_weight)):
                if j != i:
                    new_criteria_weight[j] -= change_value
                    score = np.dot(init_scores, new_criteria_weight)
                    scores[design].append(score)
                    new_criteria_weight[j] += change_value
    return scores


def plot_sensitivity_analysis(scores):
    plt.figure(figsize=(10, 6)) 
    plt.boxplot(scores.values(), labels=scores.keys(), showmeans=True)
    # plt.title('Sensitivity Analysis of Design Scores')
    plt.xlabel('Designs', fontsize=18)
    plt.ylabel('Scores', fontsize=18)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    criteria_weight = [0.1, 0.2, 0.35, 0.2, 0.15]
    change_value = 0.05

    # Scores for each design in each criterion
    designs = {'C1': [90, 65, 50, 65, 90], 
            'C2': [90, 75, 50, 90, 50], 
            'C3': [90, 60, 75, 80, 75],
            'C4': [25, 75, 75, 75, 50],
            'C5': [75, 65, 0, 90, 50]}

    # Resulting score after sensitivity analysis
    scores = {'C1': [],
            'C2': [],
            'C3': [],
            'C4': [],
            'C5': []}
    result = sensitivity_analysis(designs, criteria_weight, change_value)
    plot_sensitivity_analysis(result)