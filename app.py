
import streamlit as st
from fixed_refactored_CLR import run_clr
import firstfollow  # ensure production_list sync

st.title("CLR(1) Parser Generator")
st.markdown("Upload a grammar file with productions (e.g., `E->E+T`) one per line. `Leave it blank` to represent epsilon (ε).")

grammar_file = st.file_uploader("Upload Grammar File", type=["txt"])

if grammar_file:
    grammar_lines = grammar_file.read().decode("utf-8").strip().split("\n")
    productions = [line.replace("#", "") for line in grammar_lines if line.strip()]

    st.success("Grammar successfully loaded.")
    st.subheader("Productions:")
    st.code("\n".join(grammar_lines))

    # 🔁 Sync with firstfollow
    firstfollow.production_list.clear()
    firstfollow.production_list.extend(productions)

    # 🔁 Run CLR logic
    result = run_clr(productions)

    # FIRST & FOLLOW sets
    st.header("FIRST and FOLLOW Sets")
    for nt, data in result["first_follow"].items():
        st.write(f"**{nt}**")
        st.write(f"- FIRST: `{data['FIRST']}`")
        st.write(f"- FOLLOW: `{data['FOLLOW']}`")

    # CLR(1) Items
    st.header("CLR(1) Items")
    for idx, state in enumerate(result["states"]):
        st.subheader(f"Item {idx}")
        for item in state.closure:
            st.code(str(item))

    # Parsing Table
    st.header("CLR(1) Parsing Table")
    sym_list = result["non_terminals"] + result["terminals"]
    table = result["parsing_table"]

    rows = []
    for state_num, entries in table.items():
        row = {"State": state_num}
        for sym in sym_list:
            val = entries.get(sym, "")
            row[sym] = ", ".join(val) if isinstance(val, set) else val
        rows.append(row)

    st.dataframe(rows, use_container_width=True)

    # Conflict check
    sr, rr = 0, 0
    for entry in table.values():
        for val in entry.values():
            if isinstance(val, set) and len(val) > 1:
                r = sum(1 for x in val if x.startswith("r"))
                s = sum(1 for x in val if x.startswith("s"))
                if r and s: sr += 1
                elif r > 1: rr += 1

    st.warning(f"{sr} Shift/Reduce conflicts | {rr} Reduce/Reduce conflicts")
