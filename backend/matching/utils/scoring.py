def score_match(candidate, role):
    """
    Score how well a candidate matches a role based on skills and interests.
    
    Args:
        candidate: CandidateProfile instance with skills and interests
        role: InternshipRole instance with required_skills and ideal_traits
    
    Returns:
        dict with:
            - score (0-100)
            - list of matched skills
            - list of missing required skills
    """
    candidate_skills = set(candidate.skills)
    role_skills = set(role.required_skills)

    skill_overlap = candidate_skills.intersection(role_skills)
    overlap_pct = len(skill_overlap) / max(1, len(role_skills)) * 100

    interest_match = len(set(candidate.interests).intersection(set(role.ideal_traits))) * 5

    score = min(100, int(overlap_pct + interest_match))
    return {
        "score": score,
        "skills_matched": list(skill_overlap),
        "missing_skills": list(role_skills - candidate_skills)
    }