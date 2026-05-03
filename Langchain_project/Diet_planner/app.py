import streamlit as st
import pandas as pd

from backend.calculator import calculate_calories
from backend.prompt_builder import build_prompt , fix_meal_structure
from backend.llm_client import generate_diet , modify_diet
from backend.parser import extract_json
from backend.pdf_generator import create_pdf

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
#session state to store conversation history

# ---------------- PLAN STORAGE ---------------- #
if "plans" not in st.session_state:
    st.session_state.plans = []
    # This will store all generated plans in the session. Each plan can be a dict with keys like:
    # { "version1": "original plan" ,{data},
    #   "version2": "modified plan after chat" ,{data} }

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="AI Diet Planner",
    page_icon="🥗",
    layout="wide"
)

# ---------------- PREMIUM CSS ---------------- #
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.main {
    background-color: #0f172a;
}
.block-container {
    padding: 2rem 3rem;
}
h1, h2, h3 {
    color: white;
}
p {
    color: #cbd5f5;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #020617;
}

/* Cards */
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #22c55e, #4ade80);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    border: none;
}
.stDownloadButton>button {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color: white;
    border-radius: 10px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown("<h1 style='text-align:center;'>🥗 AI Diet Planner</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;'>Smart AI-powered personalized nutrition plans</p>",
    unsafe_allow_html=True
)

# ---------------- SMALL IMAGE ---------------- #
st.image(
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
    width=250
)

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("⚙️ Settings")

goal = st.sidebar.selectbox("Goal", [
    "Weight Loss", "Weight Gain", "Muscle Gain",
    "Fat Loss", "Skin Health", "Collagen Production"
])

diet = st.sidebar.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
season = st.sidebar.selectbox("Season", ["Summer", "Winter", "Monsoon"])

# ---------------- MAIN INPUT ---------------- #
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👤 Personal Info")

    age = st.number_input("Age", 10, 100)
    weight = st.number_input("Weight (kg)")
    height = st.number_input("Height (cm)")

    gender = st.selectbox("Gender", ["Male", "Female"])
    activity = st.selectbox("Activity Level", ["Moderate", "Active"])

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⏰ Meal Timing")

    num_meals = st.slider("Meals per day", 3, 6, 4)

    meal_times = []

    for i in range(num_meals):
        colA, colB, colC = st.columns(3)

        with colA:
            hour = st.selectbox("Hour", list(range(1, 13)), key=f"h_{i}")

        with colB:
            minute = st.selectbox("Min", ["00", "15", "30", "45"], key=f"m_{i}")

        with colC:
            ampm = st.selectbox("AM/PM", ["AM", "PM"], key=f"ap_{i}")

        meal_times.append(f"{hour}:{minute} {ampm}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("## 📦 Diet Plan Versions")

for plan in st.session_state.plans:

    with st.expander(f"📄 {plan['label']}"):

        all_rows = []

        for day in plan["data"]["diet_plan"]:
            df = pd.DataFrame(day["meals"])
            st.write(f"### {day['day']}")
            st.dataframe(df, use_container_width=True)

            for meal in day["meals"]:
                all_rows.append([
                    day["day"],
                    meal["time"],
                    meal["meal"],
                    meal["food"],
                    meal["calories"]
                ])

        # ✅ Create PDF per version
        df_version = pd.DataFrame(all_rows, columns=[
            "Day", "Time", "Meal", "Food", "Calories"
        ])

        pdf_path = create_pdf(df_version, {
            "age": age,
            "goal": goal,
            "calories": st.session_state.get("calories", 0)
        })

        with open(pdf_path, "rb") as f:
            st.download_button(
                f"📄 Download {plan['label']}",
                f,
                file_name=f"{plan['label']}.pdf"
            )
    
# ---------------- PREFERENCES ---------------- #
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("⚠️ Food Preferences")

allergies = st.text_area(
    "Allergies (comma separated)",
    placeholder="e.g. peanuts, dairy"
)

dislikes = st.text_area(
    "Foods you dislike",
    placeholder="e.g. bitter gourd, brinjal"
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- GENERATE BUTTON ---------------- #
if  not weight or not height:
    st.error("Please fill all required fields  { weight and height }to generate diet plan.don't forget to press enter after filling the values.")
    st.stop()
if st.button("🚀 Generate Diet Plan"):

    user_data = {
    "goal": goal,
    "diet": diet,
    "allergies": allergies,
    "dislikes": dislikes
}

    # Calories
    calories = calculate_calories(weight, height, age, gender, activity, goal)
    st.success(f"🔥 Daily Calories Target: {calories}")

    # Prompt
    prompt = build_prompt(user_data, calories, meal_times, season)

    # Loading
    progress = st.progress(0)
    for i in range(30):
        progress.progress(i + 1)

    with st.spinner("AI is generating your plan..."):
        raw_output = generate_diet(prompt)

    progress.progress(70)

    # Parse JSON
    data = extract_json(raw_output)

    if data:
        data = fix_meal_structure(data, meal_times)

    if not data:
        raw_output = generate_diet(prompt + "\nFix JSON only.")
        data = extract_json(raw_output)

    progress.progress(100)

    # ---------------- OUTPUT ---------------- #
    if not data or "diet_plan" not in data:
        st.error("❌ Error parsing AI output")
        st.write(raw_output)

    else:
        st.success("✅ Your Diet Plan is Ready!")
        # Save as first version
        if len(st.session_state.plans) == 0:
    # First time → original plan
            st.session_state.plans.append({
                "version": 1,
                "label": "Original Plan",
                "data": data
            })
        else:
            # New version
            new_version = len(st.session_state.plans) + 1

            st.session_state.plans.append({
                "version": new_version,
                "label": f"Edited Plan {new_version}",
                "data": data
            })

        current_plan = st.session_state.plans[-1]["data"]
        diet_plan = current_plan["diet_plan"]

        # Display Days
        for day in diet_plan:
            with st.expander(f"📅 {day['day']}"):
                df = pd.DataFrame(day["meals"])

                if "calories" in df.columns:
                    df["calories"] = df["calories"].astype(str).str.replace(" kcal", "")

                st.dataframe(df, use_container_width=True)

        # Foods to avoid
        st.markdown("### 🚫 Foods to Avoid")
        for item in data.get("foods_to_avoid", []):
            st.write(f"- {item}")

        # Precautions
        st.markdown("### ⚠️ Precautions")
        for item in data.get("precautions", []):
            st.write(f"- {item}")

        # ---------------- PDF ---------------- #
        all_rows = []
        for day in diet_plan:
            for meal in day["meals"]:
                all_rows.append([
                    day["day"],
                    meal["time"],
                    meal["meal"],
                    meal["food"],
                    str(meal["calories"]).replace(" kcal", "")
                ])

        df_pdf = pd.DataFrame(all_rows, columns=[
            "Day", "Time", "Meal", "Food", "Calories"
        ])

        # SAVE in session
        st.session_state.df_pdf = df_pdf
        st.session_state.diet_plan = diet_plan
        st.session_state.calories = calories
        # st.session_state.data = data

        # ---------------- 📊 ANALYTICS ---------------- #
        st.markdown("## 📊 Analytics")

        df_analysis = df_pdf.copy()
        df_analysis["Calories"] = df_analysis["Calories"].astype(int)

        colA, colB, colC = st.columns(3)

        with colA:
            st.metric("Total Calories (Week)", df_analysis["Calories"].sum())

        with colB:
            st.metric("Avg Calories / Day", int(df_analysis.groupby("Day")["Calories"].sum().mean()))

        with colC:
            st.metric("Total Meals", len(df_analysis))

        # Charts
        st.markdown("### 📅 Calories per Day")
        st.line_chart(df_analysis.groupby("Day")["Calories"].sum())

        st.markdown("### 🍽️ Meal Distribution")
        st.bar_chart(df_analysis.groupby("Meal")["Calories"].sum())

        # PDF Download
        pdf_path = create_pdf(df_pdf, {
            "age": age,
            "goal": goal,
            "calories": calories
        })
        list_of_users=["user1","user2","user3","user4","user5","user6","user7","user8","user9","user10"]
        with open(pdf_path, "rb") as f:
            st.download_button(
            "📄 Download Printable PDF",
            f,
            file_name="diet_plan.pdf",
            key="download_main_pdf"
        )
            
            
        
# ---------------- 💬 CHAT ---------------- #
if "plans" in st.session_state and len(st.session_state.plans) > 0:

    st.markdown("## 💬 Diet Assistant Chat")

    user_msg = st.text_input("Ask to modify your diet...", key="chat_input")

    if st.button("Send") and user_msg:

        st.session_state.chat_history.append(("You", user_msg))

        # ✅ GET LAST PLAN
        base_plan = st.session_state.plans[-1]["data"]

        with st.spinner("Updating your diet plan..."):
            updated_output = modify_diet(base_plan, user_msg)

        updated_data = extract_json(updated_output)

        # ✅ VALIDATION
        valid = True
        expected_meals = len(meal_times)

        if not updated_data or "diet_plan" not in updated_data:
            valid = False
        else:
            for day in updated_data["diet_plan"]:
                if len(day["meals"]) != expected_meals:
                    valid = False
                    break

        if not valid:
            st.error("❌ AI returned invalid structure. Try again.")
            st.write(updated_output)

        else:
            # ✅ SAVE NEW VERSION
            new_version = len(st.session_state.plans) + 1

            def get_label(user_msg):
                short = user_msg.strip().capitalize()
                if len(short) > 30:
                    short = short[:30] + "..."
                return f"Edited Plan ({short})"

            st.session_state.plans.append({
                "version": new_version,
                "label": get_label(user_msg),
                "data": updated_data
            })

            # ✅ UPDATE PDF FOR NEW PLAN
            all_rows = []
            for day in updated_data["diet_plan"]:
                for meal in day["meals"]:
                    all_rows.append([
                        day["day"],
                        meal["time"],
                        meal["meal"],
                        meal["food"],
                        str(meal["calories"]).replace(" kcal", "")
                    ])

            df_pdf_new = pd.DataFrame(all_rows, columns=[
                "Day", "Time", "Meal", "Food", "Calories"
            ])

            st.session_state.df_pdf = df_pdf_new  # 🔥 IMPORTANT

            st.session_state.chat_history.append(("AI", "Plan updated successfully!"))

            st.success("✅ New version created!")

            st.rerun()   # ✅ NOW safe at end

    # 🔁 SHOW CHAT HISTORY
    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")
            
            
    
        