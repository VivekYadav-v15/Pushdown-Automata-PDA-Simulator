import streamlit as st
import graphviz

# Setup Page
st.set_page_config(page_title="PDA Simulator", layout="wide")

# --- Custom CSS for Glassmorphism & Faded Text ---
# --- Custom CSS for Premium Glassmorphism ---
st.markdown("""
<style>
/* Main top panel */
.glass-panel {
    background: linear-gradient(135deg, rgba(243, 244, 246, 0.6), rgba(255, 255, 255, 0.8));
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 15px;
    border: 1px solid rgba(200, 200, 200, 0.4);
    padding: 25px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05);
}
.fade-text { opacity: 0.5; font-size: 0.85em; font-weight: normal; }

/* The Big Section Headers (Indigo Tint) */
.glass-header {
    background: linear-gradient(135deg, rgba(224, 231, 255, 0.6), rgba(255, 255, 255, 0.4));
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 10px;
    border: 1px solid rgba(165, 180, 252, 0.5);
    border-left: 6px solid #6366f1; /* Premium Indigo Accent */
    padding: 10px 20px;
    margin-bottom: 15px;
    margin-top: 10px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
    display: block;
    color: #1e1e2f;
}

/* The Small Input Labels (Orange Tint to match stack) */
.glass-label {
    background: linear-gradient(135deg, rgba(255, 247, 237, 0.8), rgba(255, 255, 255, 0.5));
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 6px;
    border: 1px solid rgba(253, 186, 116, 0.6);
    border-left: 4px solid #f97316; /* Vibrant Orange Accent */
    padding: 6px 14px;
    margin-bottom: 5px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
    font-weight: 600;
    font-size: 0.9em;
    color: #431407;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# --- Top Center Premium Header ---
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0f172a 0%, #312e81 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 35px 25px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 20px 40px -15px rgba(49, 46, 129, 0.5);
    font-family: 'Inter', -apple-system, sans-serif;
">
    <h1 style="color: #ffffff; font-weight: 800; letter-spacing: -1px; margin-top: 0; margin-bottom: 8px; font-size: 2.6em;">Pushdown Automata (PDA) Simulator</h1>
    <h3 style="color: #e0e7ff; font-weight: 500; margin-top: 0; font-size: 1.2em;">
        Developed by Vivek Yadav <span style="color: #a5b4fc; font-weight: 400; font-size: 0.9em;">(2024UCS3098)</span>
    </h3>
</div>
""", unsafe_allow_html=True)

# --- Project Explanation ---
st.markdown("""
<div style="
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 12px;
    border: 1px solid rgba(200, 200, 200, 0.3);
    padding: 18px 25px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    border-left: 6px solid #ffaa00;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
">
    <h3 style="margin-top: 0; color: #111; font-weight: 800; letter-spacing: -0.5px; font-size: 1.35em;">Interactive PDA Simulator</h3>
    <p style="margin-bottom: 0; font-size: 1.1em; line-height: 1.6; color: #444; font-weight: 400;">
        A real-time engine for recognizing context-free languages. Define your transition rules, input a string, and watch the <span style="color: #cc7700; font-weight: 600; background: rgba(255, 170, 0, 0.15); padding: 2px 6px; border-radius: 4px;">state machine</span> and <span style="color: #cc7700; font-weight: 600; background: rgba(255, 170, 0, 0.15); padding: 2px 6px; border-radius: 4px;">LIFO stack memory</span> dynamically compute every step.
    </p>
</div>
""", unsafe_allow_html=True)

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
    # Glass Header for Configuration
    st.markdown('<div class="glass-header"><h2 style="margin: 0; font-size: 1.4em; color: #1e1e2f;">Configuration</h2></div>', unsafe_allow_html=True)
    
    default_rules = "q0, a, Z -> q0, aZ\nq0, a, a -> q0, aa\nq0, b, a -> q1, e\nq1, b, a -> q1, e\nq1, e, Z -> q2, Z"
    
    # Enlarged Glass Label for Define Transitions
    st.markdown('<div class="glass-label" style="font-size: 1.1em; padding: 6px 15px; border-left: 4px solid #ffaa00;">Define Transitions</div>', unsafe_allow_html=True)
    rules_text = st.text_area(
        "Transitions", 
        default_rules, 
        height=140,
        label_visibility="collapsed" # Hides the default Streamlit label
    )
    
    current_rules = parse_rules(rules_text)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-label">Start State</div>', unsafe_allow_html=True)
        start_state = st.text_input("Start State", "q0", label_visibility="collapsed")
        
        st.markdown('<div class="glass-label">Start Stack Symbol</div>', unsafe_allow_html=True)
        start_stack = st.text_input("Start Stack Symbol", "Z", label_visibility="collapsed")
    with c2:
        st.markdown('<div class="glass-label">Accept State</div>', unsafe_allow_html=True)
        accept_state = st.text_input("Accept State", "q2", label_visibility="collapsed")
        
        st.markdown('<div class="glass-label">Input String</div>', unsafe_allow_html=True)
        input_string = st.text_input("Input String", "aabb", label_visibility="collapsed")

    if st.button("Load & Reset", type="primary", use_container_width=True):
        st.session_state.current_state = start_state
        st.session_state.stack = [start_stack]
        st.session_state.remaining_input = input_string
        st.session_state.status = "Loaded. Ready to step."
        st.session_state.game_over = False

    # Glass Header for Transition Table
    st.markdown('<br><div class="glass-header"><h3 style="margin: 0; font-size: 1.2em; color: #1e1e2f;">Transition Table</h3></div>', unsafe_allow_html=True)
    if current_rules:
        # Build a custom premium HTML table WITHOUT indentation to fix Streamlit's markdown parser
        table_html = """<style>
.premium-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    font-family: 'Inter', -apple-system, sans-serif;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(200, 200, 200, 0.3);
    margin-top: 5px;
}
.premium-table thead {
    background: linear-gradient(135deg, #0f172a 0%, #312e81 100%);
    color: white;
    text-align: left;
}
.premium-table th {
    padding: 12px 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
    font-size: 0.9em;
}
.premium-table td {
    padding: 12px 15px;
    border-bottom: 1px solid rgba(200, 200, 200, 0.3);
    color: #333;
    font-size: 0.95em;
}
.premium-table tbody tr:last-of-type td {
    border-bottom: 2px solid #312e81;
}
.premium-table tbody tr:hover {
    background-color: rgba(99, 102, 241, 0.08);
}
</style>
<table class="premium-table">
    <thead>
        <tr>
            <th>Current State</th>
            <th>Input</th>
            <th>Pop</th>
            <th>Next State</th>
            <th>Push</th>
        </tr>
    </thead>
    <tbody>"""
        
        # Dynamically inject the rules into the table rows
        for r in current_rules:
            inp = 'ε' if r['input'] == 'e' else r['input']
            pop = 'ε' if r['pop'] == 'e' else r['pop']
            push = 'ε' if r['push'] == 'e' else r['push']
            
            table_html += f"""<tr>
    <td style="font-weight: 600; color: #431407;">{r['state']}</td>
    <td>{inp}</td>
    <td>{pop}</td>
    <td style="font-weight: 600; color: #431407;">{r['nextState']}</td>
    <td>{push}</td>
</tr>"""
            
        table_html += "</tbody></table>"
        
        # Render the custom table
        st.markdown(table_html, unsafe_allow_html=True)

with col2:
    # Glass Header for Simulation Engine
    st.markdown('<div class="glass-header"><h2 style="margin: 0; font-size: 1.4em; color: #1e1e2f;">Simulation Engine</h2></div>', unsafe_allow_html=True)
    
    map_col, stack_col = st.columns([1.6, 1]) 

    with map_col:
        # Glass Label for State Machine Map
        st.markdown('<div class="glass-label" style="font-size: 1.05em; margin-bottom: 10px;">State Machine Map</div>', unsafe_allow_html=True)
        
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR', bgcolor='transparent', size="4,4") 
        
        all_states = set([r['state'] for r in current_rules] + [r['nextState'] for r in current_rules] + [start_state, accept_state])
        
        for state in all_states:
            if state == st.session_state.current_state:
                shape = 'doublecircle' if state == accept_state else 'circle'
                dot.node(state, state, shape=shape, style='filled', fillcolor='#ffaa00', fontcolor='black')
            else:
                shape = 'doublecircle' if state == accept_state else 'circle'
                dot.node(state, state, shape=shape, style='filled', fillcolor='#f4f4f9')

        for r in current_rules:
            label = f"{r['input']}, {r['pop']} → {r['push']}"
            dot.edge(r['state'], r['nextState'], label=label, fontsize="10")

        st.graphviz_chart(dot)
        
        st.markdown(f"**Current State:** `{st.session_state.current_state}`")
        st.markdown(f"**Remaining Input:** `{st.session_state.remaining_input if st.session_state.remaining_input else 'ε (Empty)'}`")

    with stack_col:
        if st.session_state.stack:
            stack_container_css = """
            <style>
            .stack-wrapper {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .stack-anchor {
                display: flex;
                align-items: flex-end; 
                justify-content: center;
                height: 250px; 
                width: 100%;
            }
            .stack-bucket {
                display: flex;
                flex-direction: column;
                width: 100px;
                border-left: 3px solid #333;
                border-right: 3px solid #333;
                border-bottom: 3px solid #333;
                border-radius: 0 0 8px 8px;
                padding: 5px;
                background-color: #fafafa;
                min-height: 40px; 
                transition: height 0.3s ease;
            }
            .stack-item {
                background-color: #ffaa00;
                color: black;
                padding: 8px;
                margin: 2px 0;
                text-align: center;
                border-radius: 4px;
                font-weight: bold;
                animation: slideDown 0.3s ease-out;
            }
            @keyframes slideDown {
                0% { opacity: 0; transform: translateY(-20px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            </style>
            """
            
            items_html = "".join([f"<div class='stack-item'>{item}</div>" for item in reversed(st.session_state.stack)])
            stack_html = f"{stack_container_css}<div class='stack-wrapper'><div class='stack-anchor'><div class='stack-bucket'>{items_html}</div></div><div class='glass-label' style='margin-top: 15px;'>Current Stack</div></div>"
            st.markdown(stack_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center;'>
                <div style='display: flex; align-items: flex-end; justify-content: center; height: 250px; width: 100%;'>
                    <div style='width: 100px; min-height: 40px; border-left: 3px solid #ccc; border-right: 3px solid #ccc; border-bottom: 3px solid #ccc; border-radius: 0 0 8px 8px; display: flex; align-items: center; justify-content: center;'>
                        <span style='color: gray; font-size: 0.9em;'>Empty</span>
                    </div>
                </div>
                <div class='glass-label' style='margin-top: 15px;'>Current Stack</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- Dynamic Premium Status Bar ---
    # Strip any old emojis if they exist in memory
    status_text = st.session_state.status.replace('✅ ', '').replace('❌ ', '')
    
    # Determine color based on the status text
    if "Accepted" in status_text:
        status_color = "#16a34a" # Premium Green
    elif "Rejected" in status_text:
        status_color = "#dc2626" # Premium Red
    else:
        status_color = "#6366f1" # Premium Indigo for normal steps

    # Custom Glassmorphism Status Box
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 8px;
        border: 1px solid rgba(200, 200, 200, 0.3);
        border-left: 5px solid {status_color};
        padding: 12px 20px;
        margin-bottom: 15px;
        font-weight: 600;
        color: {status_color};
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
    ">
        Status: {status_text}
    </div>
    """, unsafe_allow_html=True)

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
                st.session_state.status = "String Accepted! (Reached Accept State)" # Removed Emoji
                st.session_state.game_over = True
        else:
            st.session_state.status = "String Rejected! (No valid transitions)" # Removed Emoji
            st.session_state.game_over = True
        
        st.rerun()
