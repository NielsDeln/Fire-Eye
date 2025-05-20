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
    plt.title('Sensitivity Analysis of Design Scores')
    plt.xlabel('Designs')
    plt.ylabel('Scores')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    criteria_weight = [0.1, 0.2, 0.35, 0.2, 0.15]
    change_value = 0.05

    # Scores for each design in each criterion
    designs = {'design1': [ 4, 4, 4, 4, 4], 
            'design2': [ 1, 1, 1, 1, 1], 
            'design3': [ 4, 3, 1, 3, 4],
            'design4': [ 1, 2, 4, 3, 1],}

    # Resulting score after sensitivity analysis
    scores = {'design1': [],
            'design2': [],
            'design3': [],
            'design4': []}
    result = sensitivity_analysis(designs, criteria_weight, change_value)
    plot_sensitivity_analysis(result)