import streamlit as st
import graphviz

# Setup Page
st.set_page_config(page_title="PDA Simulator", layout="wide")

# --- Custom CSS for Glassmorphism & Faded Text ---
st.markdown("""
<style>
.glass-panel {
    background: rgba(128, 128, 128, 0.1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 15px;
    border: 1px solid rgba(128, 128, 128, 0.2);
    padding: 25px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}
.fade-text {
    opacity: 0.5;
    font-size: 0.85em;
    font-weight: normal;
}
</style>
""", unsafe_allow_html=True)

# --- Top Center Glassmorphism Header ---
st.markdown("""
<div class="glass-panel">
    <h1 style="margin-top: 0; padding-bottom: 0;">Pushdown Automata (PDA) Simulator</h1>
    <h3 style="margin-top: 0;">Developer by Vivek yadav <span class="fade-text">(2024UCS3098)</span></h3>
</div>
""", unsafe_allow_html=True)

# --- Project Explanation ---
st.markdown("### 📌 What this project does")
st.write("This tool simulates how a **Pushdown Automaton (PDA)** recognizes context-free languages. It reads an input string step-by-step, transitions between states, and performs stack operations (Push/Pop) based on the exact transition rules you define.")
st.divider()

# --- Initialize Session State ---
if 'current_state' not in st.session_state:
    st.session_state.current_state = "q0"
    st.session_state.stack = ["Z"]
    st.session_state.remaining_input = "aabb"
    st.session_state.status = "Waiting to load..."
    st.session_state.game_over = True

def parse_rules(text):
    rules = []
    for line in text.split('\n'):
        if not line.strip(): continue
        parts = line.split('->')
        if len(parts) == 2:
            left = [s.strip() for s in parts[0].split(',')]
            right = [s.strip() for s in parts[1].split(',')]
            if len(left) == 3 and len(right) == 2:
                rules.append({
                    'state': left[0], 'input': left[1], 'pop': left[2],
                    'nextState': right[0], 'push': right[1]
                })
    return rules

# --- Main Layout ---
col1, col2 = st.columns([1.2, 1.5]) # Widened the right column slightly for the graph

with col1:
    st.header("⚙️ Configuration")
    
    default_rules = "q0, a, Z -> q0, aZ\nq0, a, a -> q0, aa\nq0, b, a -> q1, e\nq1, b, a -> q1, e\nq1, e, Z -> q2, Z"
    
    rules_text = st.text_area(
        "1. Define Transitions", 
        default_rules, 
        height=140,
        help="Format: CurrentState, InputSymbol, PopSymbol -> NextState, PushSymbols."
    )
    
    # Parse rules immediately so the graph can use them
    current_rules = parse_rules(rules_text)

    c1, c2 = st.columns(2)
    with c1:
        start_state = st.text_input("Start State", "q0")
        start_stack = st.text_input("Start Stack Symbol", "Z")
    with c2:
        accept_state = st.text_input("Accept State", "q2")
        input_string = st.text_input("Input String", "aabb")

    if st.button("Load & Reset", type="primary", use_container_width=True):
        st.session_state.current_state = start_state
        st.session_state.stack = [start_stack]
        st.session_state.remaining_input = input_string
        st.session_state.status = "Loaded. Ready to step."
        st.session_state.game_over = False

with col2:
    st.header("▶️ Simulation Engine")
    
    # --- AUTOMATON DIAGRAM GENERATION ---
    st.subheader("State Machine Map")
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', bgcolor='transparent') # Left to Right layout
    
    # Collect all unique states
    all_states = set([r['state'] for r in current_rules] + [r['nextState'] for r in current_rules] + [start_state, accept_state])
    
    # Draw Nodes
    for state in all_states:
        # Highlight the current state in a bright color!
        if state == st.session_state.current_state:
            shape = 'doublecircle' if state == accept_state else 'circle'
            dot.node(state, state, shape=shape, style='filled', fillcolor='#ffaa00', fontcolor='black')
        else:
            shape = 'doublecircle' if state == accept_state else 'circle'
            dot.node(state, state, shape=shape, style='filled', fillcolor='#f4f4f9')

    # Draw Edges (Transitions)
    for r in current_rules:
        label = f"{r['input']}, {r['pop']} → {r['push']}"
        dot.edge(r['state'], r['nextState'], label=label, fontsize="10")

    # Render the graph
    st.graphviz_chart(dot)
    st.markdown("---")
    
    # Status Board
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(f"**Current State:** `{st.session_state.current_state}`")
        st.markdown(f"**Remaining Input:** `{st.session_state.remaining_input if st.session_state.remaining_input else 'ε (Empty)'}`")
    with col_stat2:
        # Stack visuals (moved here to save space)
        st.markdown("**Current Stack:**")
        if st.session_state.stack:
            stack_html = "".join([f"<div style='display: inline-block; background-color: #ffaa00; color: black; padding: 5px 10px; margin: 2px; border-radius: 5px; font-weight: bold;'>{item}</div>" for item in reversed(st.session_state.stack)])
            st.markdown(stack_html, unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: gray;'>Empty Stack</span>", unsafe_allow_html=True)
            
    st.info(f"**Status:** {st.session_state.status}")

    # Step Button
    if st.button("Step Forward", disabled=st.session_state.game_over, use_container_width=True):
        curr_in = st.session_state.remaining_input[0] if st.session_state.remaining_input else 'e'
        top_stack = st.session_state.stack[-1] if st.session_state.stack else 'e'

        matched = next((r for r in current_rules if r['state'] == st.session_state.current_state and 
                        (r['input'] == curr_in or r['input'] == 'e') and 
                        (r['pop'] == top_stack or r['pop'] == 'e')), None)

        if matched:
            st.session_state.current_state = matched['nextState']
            if matched['input'] != 'e':
                st.session_state.remaining_input = st.session_state.remaining_input[1:]
            if matched['pop'] != 'e' and st.session_state.stack:
                st.session_state.stack.pop()
            if matched['push'] != 'e':
                for char in reversed(matched['push']):
                    st.session_state.stack.append(char)
            
            st.session_state.status = f"Applied: {matched['state']}, {matched['input']}, {matched['pop']} -> {matched['nextState']}, {matched['push']}"
            
            if not st.session_state.remaining_input and st.session_state.current_state == accept_state:
                st.session_state.status = "✅ String Accepted! (Reached Accept State)"
                st.session_state.game_over = True
        else:
            st.session_state.status = "❌ String Rejected! (No valid transitions)"
            st.session_state.game_over = True
        
        st.rerun()