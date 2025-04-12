import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Load the dataset
df = pd.read_csv('dataset.csv')

st.set_page_config(layout="wide")

# Function to call the webhook for LLM improvement
def improve_with_llm(data):
    """
    Sends data to the LLM webhook and returns the improved response.
    Adjust the payload and response handling based on your webhook's API.
    """
    try:
        response = requests.post('http://your-webhook-url.com/improve', json=data)
        response.raise_for_status()
        return response.json()  # Expecting {'improved_question': '...'} or similar
    except Exception as e:
        st.error(f"Webhook error: {e}")
        return None

# --- Main Interface ---
st.header("Benchmarking Dataset")

# Configure AgGrid options for the table
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
gb.configure_pagination(enabled=True, paginationPageSize=20)  # Increased page size
gb.configure_grid_options(domLayout='normal')

# Configure columns to show all data
gb.configure_default_column(resizable=True, sortable=True, filter=True, wrapText=True, autoHeight=True)
# Set specific widths for key columns to ensure readability
gb.configure_column('dataset_id', width=100)
gb.configure_column('dataset_name', width=150)
gb.configure_column('document_id', width=100)
gb.configure_column('document_name', width=150)
gb.configure_column('chunk_id', width=100)
gb.configure_column('chunk_keyword', width=150)
gb.configure_column('question', width=250, wrapText=True)
gb.configure_column('direct_answer', width=250, wrapText=True)
gb.configure_column('context', width=250, wrapText=True)
gb.configure_column('retrieved_chunks_1', width=100)
gb.configure_column('retrieved_chunks_2', width=100)
gb.configure_column('retrieved_chunks_3', width=100)
gb.configure_column('retrieved_chunks_4', width=100)
gb.configure_column('retrieved_chunks_5', width=100)
gb.configure_column('augmented_answer', width=300, wrapText=True)

grid_options = gb.build()

# Custom CSS to adjust table width
st.markdown("""
    <style>
    .ag-root-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto;
    }
    .ag-header {
        width: 100% !important;
    }
    .ag-body-viewport {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# Display the interactive table
st.write("Select rows to edit:")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    height=600,
    fit_columns_on_grid_load=False,
    theme='streamlit'
)

# Get selected rows
selected_rows = []
if grid_response is not None:  # Added check for None
    selected_rows = grid_response['selected_rows']
    if selected_rows is None:
        selected_rows = []
selected_indices = []
if len(selected_rows) > 0:
    selected_df = pd.DataFrame(selected_rows)
    selected_indices = df[df['chunk_id'].isin(selected_df['chunk_id'])].index.tolist()

# --- Handle Selected Rows ---
if selected_indices:
    st.header("Edit Selected Rows")
    selected_df = df.loc[selected_indices]
    
    for idx in selected_indices:
        row = df.loc[idx]
        st.subheader(f"Row {idx}")
        
        # Manual editing for the question
        new_question = st.text_area(
            "Question",
            value=row['question'],
            key=f"question_{idx}"
        )
        
        # Button to improve with LLM
        if st.button("Improve with LLM", key=f"llm_{idx}"):
            data_to_improve = {
                "question": row['question'],
                "context": row['context'],
                "chunk_id": row['chunk_id']
            }
            improved_data = improve_with_llm(data_to_improve)
            if improved_data and 'improved_question' in improved_data:
                df.at[idx, 'question'] = improved_data['improved_question']
                st.success(f"Row {idx} updated with LLM response")
        
        st.write("---")

    # Apply manual changes to all selected rows
    if st.button("Apply Manual Changes"):
        for idx in selected_indices:
            df.at[idx, 'question'] = st.session_state[f"question_{idx}"]
        st.success("Manual changes applied to selected rows")

# --- Save the Updated Dataset ---
if st.button("Save Dataset"):
    df.to_csv('dataset.csv', index=False)
    st.success("Dataset saved successfully")

# Display the full dataset (optional)
with st.expander("View Full Dataset"):
    st.dataframe(df)