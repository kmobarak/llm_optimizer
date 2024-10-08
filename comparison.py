from scipy.stats import fisher_exact

# Data: (correct, incorrect)
data = {
    "Baseline": (16, 19), 
    "Zero-Shot": (8, 27),
    "Clarification": (9, 26),
    "Challenge": (13, 22),
    "Tip": (10, 25),
    "Persona": (13, 22)
    
}

for pattern, results in data.items():
    if pattern != "Baseline":
        table = [
            data["Baseline"],  
            results            
        ]
        oddsratio, p_value = fisher_exact(table)
        print(f"Baseline vs. {pattern}: P-value = {p_value}")