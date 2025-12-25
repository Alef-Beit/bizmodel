import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. הגדרות עמוד ועיצוב ---
st.set_page_config(page_title="Economic Model Simulator", layout="wide")
st.title("📊 סימולטור מודל כלכלי: הקמה, תפעול ורישיונות")

# --- 2. סרגל צד: פרמטרים (Inputs) ---
st.sidebar.header("הגדרת מחירים ועלויות")

# צד ההכנסות
st.sidebar.subheader("הכנסות (Revenue Drivers)")
price_setup = st.sidebar.number_input("מחיר הקמה לבי''ס (₪)", value=150000, step=5000)
price_op = st.sidebar.number_input("מחיר תפעול שנתי לבי''ס (₪)", value=350000, step=5000)
price_license = st.sidebar.number_input("מחיר רישיון לתלמיד (₪)", value=200, step=10)

st.sidebar.markdown("---")

# הנחות יסוד
students_per_school = st.sidebar.slider("ממוצע תלמידים בבי''ס", 100, 1000, 400)

st.sidebar.markdown("---")

# צד ההוצאות
st.sidebar.subheader("הוצאות (Cost Drivers)")
fixed_cost = st.sidebar.number_input("עלות מטה שנתית קבועה (₪)", value=4000000, step=100000)
variable_cost = st.sidebar.number_input("עלות משתנה לבי''ס פעיל (₪)", value=100000, step=5000)

# --- 3. גוף האפליקציה: טבלת עריכה ---
st.header("1. תרחיש הגדילה (ניתן לעריכה)")
st.info("שנה את המספרים בטבלה למטה כדי לעדכן את התרחיש. כל שורה מייצגת שנה.")

# יצירת טבלה התחלתית
default_data = {
    'Year': [1, 2, 3, 4, 5],
    'Schools_Setup': [5, 4, 2, 2, 1],       
    'Schools_Operation': [0, 5, 9, 11, 13]  
}
df_input = pd.DataFrame(default_data)

# רכיב עריכת טבלה
edited_df = st.data_editor(df_input, num_rows="dynamic", hide_index=True)

# --- 4. מנוע החישוב (Logic) ---

# מילוי אפסים למניעת קריסות (התיקון החשוב)
edited_df = edited_df.fillna(0)

# חישובים תפעוליים
edited_df['Total_Active'] = edited_df['Schools_Setup'] + edited_df['Schools_Operation']
edited_df['Total_Students'] = edited_df['Total_Active'] * students_per_school

# חישוב הכנסות
edited_df['Rev_Setup'] = edited_df['Schools_Setup'] * price_setup
edited_df['Rev_Op'] = edited_df['Schools_Operation'] * price_op
edited_df['Rev_License'] = edited_df['Total_Students'] * price_license
edited_df['Total_Revenue'] = edited_df['Rev_Setup'] + edited_df['Rev_Op'] + edited_df['Rev_License']

# חישוב הוצאות
edited_df['Total_Cost'] = fixed_cost + (edited_df['Total_Active'] * variable_cost)

# שורה תחתונה
edited_df['Net_Profit'] = edited_df['Total_Revenue'] - edited_df['Total_Cost']
edited_df['Cumulative_Cash'] = edited_df['Net_Profit'].cumsum()

# --- 5. תצוגת מדדים (KPIs) ---
st.header("2. תוצאות עיקריות")

total_rev_5y = edited_df['Total_Revenue'].sum()
total_profit_5y = edited_df['Net_Profit'].sum()

# חישוב שנת איזון
break_even_rows = edited_df[edited_df['Cumulative_Cash'] > 0]
if not break_even_rows.empty:
    break_even_year = int(break_even_rows.iloc[0]['Year'])
    be_text = f"Year {break_even_year}"
else:
    be_text = "Not Reached"

col1, col2, col3 = st.columns(3)
col1.metric("סך הכנסות (5 שנים)", f"₪{total_rev_5y:,.0f}")
col2.metric("סך רווח נקי (5 שנים)", f"₪{total_profit_5y:,.0f}")
col3.metric("נקודת איזון (ROI)", be_text)

# --- 6. ויזואליזציה (Charts) ---
st.header("3. גרפים וויזואליזציה")

# יצירת הגרפים
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# הכנת ציר ה-X (שנים כטקסט)
years_str = edited_df['Year'].astype(int).astype(str)

# --- גרף שמאל: הכנסות מול הוצאות ---
# שכבות ההכנסה (Stacked Bar)
p1 = ax1.bar(years_str, edited_df['Rev_Setup'], label='Setup Fees', color='#4c72b0')
p2 = ax1.bar(years_str, edited_df['Rev_Op'], bottom=edited_df['Rev_Setup'], label='Operation Fees', color='#55a868')
bottom_license = edited_df['Rev_Setup'] + edited_df['Rev_Op']
p3 = ax1.bar(years_str, edited_df['Rev_License'], bottom=bottom_license, label='Student Licenses', color='#f1c40f')

# קו ההוצאות
ax1.plot(years_str, edited_df['Total_Cost'], color='red', linewidth=3, linestyle='--', label='Total Cost')

# כותרות באנגלית (למניעת בעיות עברית)
ax1.set_title('Revenue Structure vs. Costs', fontsize=14, fontweight='bold')
ax1.set_ylabel('Amount (NIS)', fontsize=12)
ax1.set_xlabel('Year', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(axis='y', alpha=0.3)

# --- גרף ימין: תזרים מזומנים ---
# צבעים: ירוק לרווח, אדום להפסד
colors = ['green' if x >= 0 else 'red' for x in edited_df['Cumulative_Cash']]
ax2.bar(years_str, edited_df['Cumulative_Cash'], color=colors, alpha=0.7)
ax2.plot(years_str, edited_df['Cumulative_Cash'], color='black', marker='o')
ax2.axhline(0, color='black', linewidth=1)

# כותרות באנגלית
ax2.set_title('Cumulative Cash Flow (ROI)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Profit / Loss (NIS)', fontsize=12)
ax2.set_xlabel('Year', fontsize=12)
ax2.grid(axis='y', alpha=0.3)

# הצגת הגרף בסטרים-ליט
st.pyplot(fig)

# --- 7. טבלת נתונים סופית ---
with st.expander("לחץ כאן לצפייה בטבלת הנתונים המלאה"):
    # עיצוב הטבלה עם פסיקים, תוך ווידוא שאין ערכים ריקים
    st.dataframe(edited_df.style.format("{:,.0f}"))