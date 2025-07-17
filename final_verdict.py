import streamlit as st


def render_final_verdict(fair_value, current_price):
    verdict = ""
    badge_color = ""

    if fair_value > current_price * 1.15:
        verdict = "Undervalued"
        badge_color = "green"
    elif fair_value < current_price * 0.85:
        verdict = "Overvalued"
        badge_color = "red"
    else:
        verdict = "Fairly Valued"
        badge_color = "gray"

    st.markdown("""
    <div style='padding: 1rem; border-radius: 8px; border: 1px solid #ccc; background-color: #f9f9f9;'>
        <h4 style='margin-bottom: 0.5rem;'>📍 Final Verdict</h4>
        <span style='font-size: 1.2rem;'>Based on the DCF fair value:</span><br>
        <span style='display: inline-block; margin-top: 0.5rem; padding: 0.3rem 0.7rem; 
                     background-color: {color}; color: white; border-radius: 6px; font-weight: bold;'>
            {verdict}
        </span>
    </div>
    """.format(color=badge_color, verdict=verdict), unsafe_allow_html=True)
