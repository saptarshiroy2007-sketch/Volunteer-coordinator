import json
import os
import math
from datetime import datetime

SKILL_MAP = {
    "Healthcare": ["Medical", "Counseling"],
    "Education": ["Teaching", "IT"],
    "Food & Nutrition": ["Cooking", "Logistics", "Driving"],
    "Disaster Relief": ["Construction", "Logistics", "Driving", "Medical"],
    "Environment": ["Logistics"],
    "Women Empowerment": ["Counseling", "Legal", "Teaching"],
}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_data():
    with open(os.path.join(BASE_DIR, "data", "needs.json")) as f:
        needs = json.load(f)
    with open(os.path.join(BASE_DIR, "data", "volunteers.json")) as f:
        volunteers = json.load(f)
    return needs, volunteers

def save_data(needs, volunteers):
    with open(os.path.join(BASE_DIR, "data", "needs.json"), "w") as f:
        json.dump(needs, f, indent=2)
    with open(os.path.join(BASE_DIR, "data", "volunteers.json"), "w") as f:
        json.dump(volunteers, f, indent=2)
def compute_urgency_score(need):
    """
    Urgency = weighted combo of severity, mention frequency, recency, and gap in volunteers.
    Scale: 0–100
    """
    severity_score = need["severity"] * 5  # max 50
    mention_score = min(need["mentions"] / 25 * 20, 20)  # max 20

    # Recency: reported recently = higher score
    days_old = (datetime.now() - datetime.strptime(need["date_reported"], "%Y-%m-%d")).days
    recency_score = max(0, 10 - days_old * 0.3)  # max 10

    # Volunteer gap
    gap = need["volunteers_needed"] - need["volunteers_assigned"]
    gap_score = min(gap / need["volunteers_needed"] * 20, 20)  # max 20

    total = severity_score + mention_score + recency_score + gap_score
    return round(min(total, 100), 1)

def get_urgency_label(score):
    if score >= 75:
        return "🔴 Critical"
    elif score >= 50:
        return "🟠 High"
    elif score >= 25:
        return "🟡 Medium"
    else:
        return "🟢 Low"

def rank_needs(needs):
    active = [n for n in needs if n["status"] != "Resolved"]
    for n in active:
        n["urgency_score"] = compute_urgency_score(n)
        n["urgency_label"] = get_urgency_label(n["urgency_score"])
    return sorted(active, key=lambda x: x["urgency_score"], reverse=True)

def match_volunteers_to_need(need, volunteers, top_k=5):
    """
    Match volunteers based on: skill fit, area match, availability, experience, rating.
    """
    required_skills = SKILL_MAP.get(need["category"], [])
    available_vols = [v for v in volunteers if v["status"] == "Available"]

    scored = []
    for v in available_vols:
        score = 0

        # Skill match (most important)
        skill_overlap = len(set(v["skills"]) & set(required_skills))
        score += skill_overlap * 30  # max ~60

        # Area match
        if v["area"] == need["area"]:
            score += 25

        # Experience
        score += min(v["experience_years"] * 2, 10)

        # Rating
        score += (v["rating"] - 3.5) * 10  # 0–15

        # Tasks completed (track record)
        score += min(v["tasks_completed"] * 0.5, 10)

        scored.append((v, round(score, 1)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

def add_need(description, category, area, severity, mentions, volunteers_needed, source="Manual Entry"):
    needs, volunteers = load_data()
    new_id = f"NEED-{len(needs)+1:03d}"
    new_need = {
        "id": new_id,
        "category": category,
        "description": description,
        "area": area,
        "severity": severity,
        "mentions": mentions,
        "volunteers_needed": volunteers_needed,
        "volunteers_assigned": 0,
        "date_reported": datetime.now().strftime("%Y-%m-%d"),
        "status": "Open",
        "source": source,
    }
    needs.append(new_need)
    save_data(needs, volunteers)
    return new_need

def add_volunteer(name, skills, area, availability, experience_years, contact):
    needs, volunteers = load_data()
    new_id = f"VOL-{len(volunteers)+1:03d}"
    new_vol = {
        "id": new_id,
        "name": name,
        "skills": skills,
        "area": area,
        "availability": availability,
        "experience_years": experience_years,
        "tasks_completed": 0,
        "rating": 4.0,
        "status": "Available",
        "contact": contact,
    }
    volunteers.append(new_vol)
    save_data(needs, volunteers)
    return new_vol

def assign_volunteer(need_id, volunteer_id):
    needs, volunteers = load_data()
    need = next((n for n in needs if n["id"] == need_id), None)
    vol = next((v for v in volunteers if v["id"] == volunteer_id), None)
    if not need or not vol:
        return False, "Need or Volunteer not found"
    need["volunteers_assigned"] = min(need["volunteers_assigned"] + 1, need["volunteers_needed"])
    if need["volunteers_assigned"] >= need["volunteers_needed"]:
        need["status"] = "In Progress"
    vol["status"] = "Busy"
    vol["tasks_completed"] += 1
    save_data(needs, volunteers)
    return True, f"Assigned {vol['name']} to {need['id']}"

def get_stats(needs, volunteers):
    active_needs = [n for n in needs if n["status"] != "Resolved"]
    resolved = [n for n in needs if n["status"] == "Resolved"]
    available_vols = [v for v in volunteers if v["status"] == "Available"]
    
    category_counts = {}
    for n in active_needs:
        category_counts[n["category"]] = category_counts.get(n["category"], 0) + 1

    area_scores = {}
    for n in active_needs:
        score = compute_urgency_score(n)
        area_scores[n["area"]] = area_scores.get(n["area"], 0) + score

    return {
        "total_needs": len(needs),
        "active_needs": len(active_needs),
        "resolved_needs": len(resolved),
        "total_volunteers": len(volunteers),
        "available_volunteers": len(available_vols),
        "category_breakdown": category_counts,
        "area_urgency": area_scores,
    }
