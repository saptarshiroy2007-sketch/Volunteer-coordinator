import json
import random
from datetime import datetime, timedelta

AREAS = ["Salt Lake", "Park Street", "Jadavpur", "Howrah", "Barasat", "Dum Dum", "Behala", "Tollygunge"]

NEED_CATEGORIES = {
    "Healthcare": ["Medical camp needed", "Vaccination drive required", "Mental health support needed", "First aid training"],
    "Education": ["Tutoring for underprivileged kids", "Digital literacy training", "Scholarship guidance", "Study material distribution"],
    "Food & Nutrition": ["Midday meal program short-staffed", "Food distribution drive", "Nutrition awareness camp", "Ration support needed"],
    "Disaster Relief": ["Flood relief coordination", "Emergency shelter setup", "Debris clearance needed", "Relief material distribution"],
    "Environment": ["Tree plantation drive", "Garbage segregation awareness", "Pond cleanup", "Plastic-free campaign"],
    "Women Empowerment": ["Self-defense training", "Skill development workshop", "Legal awareness session", "Microfinance guidance"],
}

VOLUNTEER_SKILLS = ["Medical", "Teaching", "Logistics", "Counseling", "IT", "Cooking", "Construction", "Legal", "Photography", "Driving"]

def generate_needs(n=40):
    needs = []
    base_date = datetime.now() - timedelta(days=30)
    for i in range(n):
        category = random.choice(list(NEED_CATEGORIES.keys()))
        description = random.choice(NEED_CATEGORIES[category])
        severity = random.randint(1, 10)
        mentions = random.randint(1, 25)
        area = random.choice(AREAS)
        date_reported = base_date + timedelta(days=random.randint(0, 30))
        needs.append({
            "id": f"NEED-{i+1:03d}",
            "category": category,
            "description": description,
            "area": area,
            "severity": severity,
            "mentions": mentions,
            "volunteers_needed": random.randint(2, 15),
            "volunteers_assigned": 0,
            "date_reported": date_reported.strftime("%Y-%m-%d"),
            "status": random.choice(["Open", "Open", "Open", "In Progress", "Resolved"]),
            "source": random.choice(["Paper Survey", "Field Report", "WhatsApp Group", "Direct Call", "NGO Partner"]),
        })
    return needs

def generate_volunteers(n=30):
    first_names = ["Arjun", "Priya", "Rahul", "Sneha", "Amit", "Riya", "Sourav", "Tanya", "Debashis", "Ananya",
                   "Rohan", "Ishita", "Vikram", "Pooja", "Nikhil", "Sohini", "Aditya", "Meghna", "Subham", "Ritika"]
    last_names = ["Das", "Chatterjee", "Banerjee", "Sen", "Ghosh", "Roy", "Mukherjee", "Bose", "Dey", "Paul"]
    volunteers = []
    for i in range(n):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        skills = random.sample(VOLUNTEER_SKILLS, random.randint(1, 4))
        area = random.choice(AREAS)
        volunteers.append({
            "id": f"VOL-{i+1:03d}",
            "name": name,
            "skills": skills,
            "area": area,
            "availability": random.choice(["Weekdays", "Weekends", "Both", "Flexible"]),
            "experience_years": random.randint(0, 10),
            "tasks_completed": random.randint(0, 20),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "status": random.choice(["Available", "Available", "Busy", "On Leave"]),
            "contact": f"9{random.randint(100000000, 999999999)}",
        })
    return volunteers

def save_seed_data():
    needs = generate_needs()
    volunteers = generate_volunteers()
    with open("/home/claude/volunteer_coord/data/needs.json", "w") as f:
        json.dump(needs, f, indent=2)
    with open("/home/claude/volunteer_coord/data/volunteers.json", "w") as f:
        json.dump(volunteers, f, indent=2)
    print(f"Generated {len(needs)} needs and {len(volunteers)} volunteers.")

if __name__ == "__main__":
    save_seed_data()
