from aar_interface import get_agent_performance

def calculate_dynamic_weights():
    performance = get_agent_performance()
    overall_accuracy = sum(performance.values()) / len(performance) if performance else 1.0
    
    # If accuracy is low, we boost the Adversarial Critic
    critic_boost = 1.0 - overall_accuracy
    weights = {
        "Technical": 0.15,
        "Whale": 0.25,
        "Critic": min(0.60, 0.25 + critic_boost) 
    }
    
    return weights, performance
