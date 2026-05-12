# Example Review Calibration

Input: A Streamlit app loads a dataframe at top level, edits it with `st.data_editor`, and writes to the database whenever the dataframe differs.

Expected review:

- High: database write is not behind explicit submit and can repeat on rerun.
- Medium: data loading should be cached with a freshness policy.
- Medium: edited rows need validation and a diff preview.
- Low: add empty state when query returns no rows.

Smallest fix: keep source data immutable, compute diff, show preview, and save only after `st.form_submit_button` or explicit `st.button` confirmation.
