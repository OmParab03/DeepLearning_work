import json
def get_goal_rules(goal):
    goal = goal.lower()

    if goal == "weight gain":
        return """
Focus on calorie-dense foods.
Priority foods: rice, paneer, banana, peanut butter, potatoes.
Include these foods multiple times across the 7 days.
"""

    elif goal in ["weight loss", "fat loss"]:
        return """
Focus on low-calorie, high-fiber foods.
Priority foods: oats, dal, vegetables, salads, fruits.
Repeat these foods frequently in different forms.
"""

    elif goal == "muscle gain":
        return """
Focus on high-protein foods.
Priority foods: eggs, chicken, paneer, soy chunks, dal.
Ensure these appear multiple times across the plan.
"""

    elif goal == "skin health":
        return """
Focus on skin-friendly nutrients.
Priority foods: citrus fruits, carrot, cucumber, almonds, leafy greens.
Include these foods repeatedly for better results.
"""

    elif goal == "collagen production":
        return """
Focus on collagen-supporting foods.
Priority foods: lemon, orange, amla, eggs, paneer, nuts, seeds.
Avoid foods that are not seasonal or rarely available in the market.
Ensure these foods appear multiple times across 7 days.
"""

    else:
        return "Keep meals balanced with a variety of foods, ensuring all food groups are included."
    
    
def get_season_rules(season):
    season = season.lower()

    if season == "summer":
        return "Use cooling foods like buttermilk, coconut water, cucumber, watermelon. Avoid heavy oily food."

    elif season == "winter":
        return "Include warming foods like ghee, dry fruits, soups, bajra, jaggery."

    elif season == "monsoon":
        return "Avoid street food, use light and hygienic meals. Prefer soups, steamed food."

    else:
        return "okay for all seasons, eat balanced meals with seasonal fruits and vegetables."
    

def build_prompt(user_data, calories, meal_times, season):

    goal_rules = get_goal_rules(user_data["goal"])
    season_rules = get_season_rules(season)

    # Safe handling
    allergies = user_data.get("allergies") or []
    dislikes = user_data.get("dislikes") or []

    meal_times_text = json.dumps(meal_times, indent=2)
    allergies_text = json.dumps(allergies)
    dislikes_text = json.dumps(dislikes)

    return f"""
Generate a STRICT 7-day personalized Indian diet plan.

================= USER PROFILE =================
- Goal: {user_data["goal"]}
- Diet: {user_data["diet"]}
- Total Daily Calories: {calories}
- Season: {season}
- Meal times: {meal_times_text}
- Allergies: {allergies_text}
- Disliked Foods: {dislikes_text}

================= CORE RULES =================

- Number of meals per day MUST EXACTLY equal the number of meal_times.
- DO NOT add extra meals.
- DO NOT skip any meal.
- Each meal time must have EXACTLY one meal.
- Meal times must be used EXACTLY as provided (no modification).
- Meals must map 1-to-1 with meal_times in the SAME ORDER.
- The "meals" array MUST be same length as meal_times.

- STRICTLY avoid:
  Allergies: {allergies_text}
  Disliked foods: {dislikes_text}

- If any restricted food appears → REPLACE it.

================= MEAL NAMING =================

Follow naming based on number of meals:

- 3 meals → Breakfast, Lunch, Dinner
- 4 meals → Breakfast, Lunch, Evening Snack, Dinner
- 5 meals → Breakfast, Mid Meal, Lunch, Evening Snack, Dinner
- 6 meals → Breakfast, Mid Meal, Lunch, Snack, Evening Snack, Dinner

Do NOT invent extra meal types.

================= FOOD RULES =================

- Use only Indian home-style foods
- Match user's diet preference
- Maintain variety across 7 days
- Do NOT repeat identical meals on consecutive days
- Distribute calories properly across meals
- Include priority foods multiple times
- Follow both goal and season rules
- Avoid non-seasonal or rare foods

================= CONTEXT =================

Goal Rules:
{goal_rules}

Season Rules:
{season_rules}

================= EXTRA GUIDELINES =================

- Prefer evening snacks around 6–7 PM when relevant
- Prefer dinner around 8:30–9:30 PM when relevant
- Warm foods should not appear on consecutive days


================= OUTPUT =================

Return ONLY valid JSON.
No explanation. No markdown. No comments.
eg: 
{{
  "diet_plan": [
    {{
      "day": "sunday/monday/.../saturday (max 7 days)",
      "meals": [
        {{
          "time": "7:30 AM",
          "meal": "Breakfast",
          "food": "Poha + Tea",
          "calories": 300
        }}
      ]
    }}
  ],
  "foods_to_avoid": [],
  "precautions": []
}}

================= VALIDATION =================

- "diet_plan" must contain EXACTLY 7 days (Day 1 to Day 7)
- Each day must contain EXACTLY len(meal_times) meals
- Each meal must map to one meal_time
- No extra or missing meals allowed
- "calories" must be integer
- Meal "time" field MUST exactly match provided meal_times values

================= HARD CONSTRAINT (DO NOT BREAK) =================

You MUST follow this EXACT structure:

- Number of meals per day = {len(meal_times)}
- Meal times MUST be EXACTLY:
{meal_times_text}

For EACH day:
- Create EXACTLY {len(meal_times)} meals
- Each meal MUST use ONE of the above times
- Use each time EXACTLY ONCE per day

Example mapping (STRICT):

{{
  "meals": [
    {{"time": "{meal_times[0]}", "meal": "..."}},
    {{"time": "{meal_times[1]}", "meal": "..."}},
    ...
  ]
}}

If you generate:
- More meals ❌
- Less meals ❌
- Duplicate time ❌

→ REGENERATE BEFORE OUTPUT

DO NOT CONTINUE UNTIL VALID



If ANY rule is violated → fix internally before returning output
"""

def fix_meal_structure(plan, meal_times):
    for day in plan.get("diet_plan", []):
        meals = day.get("meals", [])

        # 🔴 If too many meals → trim
        if len(meals) > len(meal_times):
            meals = meals[:len(meal_times)]

        # 🔴 If too few → fill dummy
        while len(meals) < len(meal_times):
            meals.append({
                "time": meal_times[len(meals)],
                "meal": "Meal",
                "food": "Simple home food",
                "calories": 200
            })

        # ✅ Fix times EXACTLY
        for i in range(len(meal_times)):
            meals[i]["time"] = meal_times[i]

        day["meals"] = meals

    return plan


if __name__ == "__main__":
    user_data = {
        "goal": "collagen production",
        "diet": "vegetarian"
    }
    calories = 2000
    meal_times = ["8:59 AM", "1:50 PM", "6:30 PM","9:30 PM"]
    season = "summer"

    prompt = build_prompt(user_data, calories, meal_times, season)
    print(prompt)
