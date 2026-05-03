import json

def extract_json(text):
    try:
        # Remove markdown if present
        text = text.replace("```json", "").replace("```", "").strip()

        # Find JSON boundaries
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            json_text = text[start:end+1]
            data = json.loads(json_text)
            return data

        return None

    except Exception as e:
        print("Parsing error:", e)
        return None
    
if __name__ == "__main__":
    text = '''
    {
      "diet_plan": [
        {
          "day": "Day 1",
          "meals": [
            {
              "time": "7:30 AM",
              "meal": "Breakfast",
              "food": "Poha + Tea",
              "calories": 300
            }
          ]
        }
      ],
      "foods_to_avoid": [
        "example"
      ],
      "precautions": [
        "example"
      ]
    }
    '''
    df = extract_json(text)
    print(df)