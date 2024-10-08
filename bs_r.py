import numpy as np
import random

np.random.seed(42)
random.seed(42)

#percentage data
baseline_accuracy = 0.46
zeroshot_accuracy = 0.22  
clarification_accuracy = 0.28 
challenge_accuracy = 0.37
tipping_accuracy = 0.28     
persona_accuracy = 0.37  

n_problems = 35

# Resampling Function
def bootstrap_resample(data, n_iterations=1000):
    resampled_means = []
    for i in range(n_iterations):
        resample = np.random.choice(data, size=len(data), replace=True)  # Resample with replacement
        resampled_mean = np.mean(resample)
        resampled_means.append(resampled_mean)
    return resampled_means

# Simulating the correct/incorrect responses
baseline_data = [1 if random.random() < baseline_accuracy else 0 for _ in range(n_problems)]
zeroshot_data = [1 if random.random() < zeroshot_accuracy else 0 for _ in range(n_problems)]
clarification_data = [1 if random.random() < clarification_accuracy else 0 for _ in range(n_problems)]
challenge_data = [1 if random.random() < challenge_accuracy else 0 for _ in range(n_problems)]
tipping_data = [1 if random.random() < tipping_accuracy else 0 for _ in range(n_problems)]
persona_data = [1 if random.random() < persona_accuracy else 0 for _ in range(n_problems)]

# Perform bootstrapping (1,000 resamples)
baseline_resampled = bootstrap_resample(baseline_data)
zeroshot_resampled = bootstrap_resample(zeroshot_data)
clarification_resampled = bootstrap_resample(clarification_data)
challenge_resampled = bootstrap_resample(challenge_data)
tipping_resampled = bootstrap_resample(tipping_data)
persona_resampled = bootstrap_resample(persona_data)

# Calculate 95% confidence intervals
baseline_ci = np.percentile(baseline_resampled, [2.5, 97.5])
zeroshot_ci = np.percentile(zeroshot_resampled, [2.5, 97.5])
clarification_ci = np.percentile(clarification_resampled, [2.5, 97.5])
challenge_ci = np.percentile(challenge_resampled, [2.5, 97.5])
tipping_ci = np.percentile(tipping_resampled, [2.5, 97.5])
persona_ci = np.percentile(persona_resampled, [2.5, 97.5])

print(f"Baseline pattern: {baseline_ci}") 
print(f"Zero-Shot pattern: {zeroshot_ci}") 
print(f"Clarification pattern: {clarification_ci}")
print(f"Challenge pattern: {challenge_ci}")
print(f"Tipping pattern: {tipping_ci}")
print(f"Persona pattern: {persona_ci}")