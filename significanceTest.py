import numpy as np
import scipy.stats as stats

# Example accuracy data from the four batches
baseline_accuracy = [56, 69, 51, 75]  
initial_accuracy = [22, 24, 22, 28]  

t_stat, p_value = stats.ttest_rel(baseline_accuracy, initial_accuracy)

print(f"T-statistic: {t_stat}")
print(f"P-value: {p_value}")

if p_value < 0.05:
    print("There is a statistically significant difference.")
else:
    print("There is no statistically significant difference.")