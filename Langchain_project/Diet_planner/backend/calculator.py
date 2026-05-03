def calculate_calories(weight, height, age, gender, activity, goal):
    gender = gender.lower()
    goal = goal.lower()

    # BMR
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_map = {
        "moderate": 1.55,
        "active": 1.725
    }

    calories = bmr * activity_map[activity.lower()]

    if goal == "weight loss":
        calories -= 300
    elif goal == "weight gain":
        calories += 300
    elif goal == "muscle gain":
        calories += 500
    elif goal == "fat loss":
        calories -= 500
    elif goal in ["skin health", "collagen production"]:
        pass  # no calorie change

    return int(calories)



if __name__ == "__main__":
    weight = 57
    height = 170
    age =20
    gender="male"
    activity="Moderate"
    goal="skin health"
    calories = calculate_calories(weight, height, age, gender, activity, goal)
    print(f"Calories needed: {calories}")
    
    
    