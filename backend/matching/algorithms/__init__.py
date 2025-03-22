# backend/matching/algorithms/__init__.py
from .preference_priority import PreferencePriorityAlgorithm
from .weighted_preference import WeightedPreferenceAlgorithm


def get_algorithm(algorithm_type, settings=None):
    """
    Factory function to get the appropriate algorithm based on type

    Args:
        algorithm_type: The type of algorithm to use
        settings: Optional dictionary of algorithm settings

    Returns:
        An initialized matching algorithm
    """
    algorithms = {
        "weighted_preference": WeightedPreferenceAlgorithm,
        "preference_priority": PreferencePriorityAlgorithm,
    }

    if algorithm_type not in algorithms:
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")

    return algorithms[algorithm_type](settings)
