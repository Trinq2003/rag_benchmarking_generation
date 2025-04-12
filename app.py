import streamlit as st
import pandas as pd
import requests  # For calling webhooks

# Load the dataset (replace 'dataset.csv' with your file path)
df = pd.read_csv('dataset.csv')

# Function to call the webhook for LLM improvement
def improve_with_llm(data):
    """
    Sends data to the LLM webhook and returns the improved response.
    Adjust the payload and response handling based on your webhook's API.
    """
    try:
        response = requests.post('http://your-webhook-url.com/improve', json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Expecting {'improved_question': '...'} or similar
    except Exception as e:
        st.error(f"Webhook error: {e}")
        return None

# --- Sidebar for Filters ---
st.sidebar.header("Filters")

# Filter by dataset_id
dataset_ids = df['dataset_id'].unique()
selected_dataset_ids = st.sidebar.multiselect("Dataset ID", dataset_ids, default=dataset_ids)

# Filter by dataset_name
dataset_names = df['dataset_name'].unique()
selected_dataset_names = st.sidebar.multiselect("Dataset Name", dataset_names, default=dataset_names)

# Filter by document_id
document_ids = df['document_id'].unique()
selected_document_ids = st.sidebar.multiselect("Document ID", document_ids, default=document_ids)

# Filter by document_name
document_names = df['document_name'].unique()
selected_document_names = st.sidebar.multiselect("Document Name", document_names, default=document_names)

# Filter by chunk_id
chunk_ids = df['chunk_id'].unique()
selected_chunk_ids = st.sidebar.multiselect("Chunk ID", chunk_ids, default=chunk_ids)

# Filter by chunk_keyword (keyword search)
chunk_keyword_filter = st.sidebar.text_input("Chunk Keyword Search", "")

# Apply filters to the dataframe
filtered_df = df[
    (df['dataset_id'].isin(selected_dataset_ids)) &
    (df['dataset_name'].isin(selected_dataset_names)) &
    (df['document_id'].isin(selected_document_ids)) &
    (df['document_name'].isin(selected_document_names)) &
    (df['chunk_id'].isin(selected_chunk_ids)) &
    (df['chunk_keyword'].str.contains(chunk_keyword_filter, case=False, na=False))
]

# --- Main Interface ---
st.header("Benchmarking Dataset")

# Display the filtered dataframe with multi-row selection
# Note: 'selection_mode' is experimental; adjust if unstable in your Streamlit version
selected_rows = st.dataframe(
    filtered_df,
    use_container_width=True,
    selection_mode="multi-row",
    key="data_table"
).selection["rows"]  # Returns indices of selected rows

# --- Handle Selected Rows ---
if selected_rows:
    st.header("Edit Selected Rows")
    selected_df = filtered_df.iloc[selected_rows]  # Subset of selected rows
    
    for idx in selected_rows:
        row = filtered_df.iloc[idx - selected_rows[0]]  # Adjust index for display
        st.subheader(f"Row {idx}")
        
        # Manual editing for the question
        new_question = st.text_area(
            "Question",
            value=row['question'],
            key=f"question_{idx}"
        )
        
        # Button to improve with LLM
        if st.button("Improve with LLM", key=f"llm_{idx}"):
            # Prepare data for webhook (customize based on your needs)
            data_to_improve = {
                "question": row['question'],
                "context": row['context'],
                "chunk_id": row['chunk_id']
            }
            improved_data = improve_with_llm(data_to_improve)
            if improved_data and 'improved_question' in improved_data:
                df.at[idx, 'question'] = improved_data['improved_question']
                st.success(f"Row {idx} updated with LLM response")
        
        st.write("---")  # Separator between rows

    # Apply manual changes to all selected rows
    if st.button("Apply Manual Changes"):
        for idx in selected_rows:
            df.at[idx, 'question'] = st.session_state[f"question_{idx}"]
        st.success("Manual changes applied to selected rows")

# --- Save the Updated Dataset ---
if st.button("Save Dataset"):
    df.to_csv('dataset.csv', index=False)
    st.success("Dataset saved successfully")

# Display the full dataset (optional, for reference)
with st.expander("View Full Dataset"):
    st.dataframe(df)