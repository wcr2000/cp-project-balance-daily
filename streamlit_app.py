import io

import pandas as pd
import streamlit as st


# Function to process the files
def process_files(file1, file2):
    # Check the file type of the first file and read accordingly
    if file1.name.endswith(".csv"):
        df = pd.read_csv(file1, encoding="TIS-620", header=6, skipfooter=1)
    else:
        df = pd.read_excel(file1, header=6, skipfooter=1)

    # Process the batch daily data
    df_batch_daily = df.copy()
    df_batch_daily30000 = df.copy()

    # Clean daily nm
    df_batch_daily["รหัสร้าน"] = (
        df_batch_daily["สาขา"].str.split("-").str[0].astype(str).str.strip()
    )
    # Clean daily 30000
    df_batch_daily30000["รหัสร้าน"] = (
        df_batch_daily30000["สาขา"].str.split("-").str[0].astype(str).str.strip()
    )

    # Extract the shop code from the "สาขา" column and create a new column
    df_batch_daily30000["ชื่อร้าน"] = df_batch_daily30000["สาขา"].str.split("-").str[1]
    df_batch_daily30000["รหัสร้าน"] = df_batch_daily30000["รหัสร้าน"].astype(str)
    df_batch_daily30000["รหัสร้าน"] = df_batch_daily30000["รหัสร้าน"].str.strip()
    df_batch_daily30000["ชื่อร้าน"] = df_batch_daily30000["ชื่อร้าน"].str.strip()

    df_batch_daily30000["รหัสร้าน"] = df_batch_daily30000["รหัสร้าน"].astype(int)
    df_batch_daily30000 = df_batch_daily30000[df_batch_daily30000["รหัสร้าน"] >= 30000]
    df_batch_daily30000["รหัสร้าน"] = df_batch_daily30000["รหัสร้าน"].astype(str)

    df_batch_daily["เงินสดขาดเกิน"] = df_batch_daily[
        ["เงินสด(ขาด)เกิน#1", "เงินสด(ขาด)เกิน#2", "เงินสด(ขาด)เกิน#3", "เงินสด(ขาด)เกิน#4"]
    ].sum(axis=1)
    df_batch_daily30000["เงินสดขาดเกิน"] = df_batch_daily30000[
        ["เงินสด(ขาด)เกิน#1", "เงินสด(ขาด)เกิน#2", "เงินสด(ขาด)เกิน#3", "เงินสด(ขาด)เกิน#4"]
    ].sum(axis=1)

    # Read the second file
    df_user_branch_month = pd.read_excel(file2, skipfooter=1)
    df_user_branch_month["รหัสร้าน"] = (
        df_user_branch_month["รหัสร้าน"].astype(str).str.zfill(5)
    )

    # Merge the data
    merged_df = pd.merge(df_batch_daily, df_user_branch_month, on="รหัสร้าน", how="inner")
    final_df = merged_df[
        [
            "วันที่ตรวจนับ",
            "สาขา",
            "Area",
            "Zone",
            "เงินสำรอง",
            "เงินสดขาดเกิน",
            "เงินสด(ขาด)เกิน#1",
            "เงินสด(ขาด)เกิน#2",
            "เงินสด(ขาด)เกิน#3",
            "เงินสด(ขาด)เกิน#4",
            "DGM",
            "ชื่อฝ่าย",
            "GM_y",  # because is a monthly gm cann't empty
        ]
    ]
    final_df.rename(columns={"DGM": "OC ร้าน"}, inplace=True)
    final_df.rename(columns={"ชื่อฝ่าย": "ฝ่าย"}, inplace=True)
    final_df.rename(columns={"GM_y": "GM"}, inplace=True)

    # วันที่ตรวจนับ	รหัสร้าน	ชื่อร้าน	Zone	เงินสำรอง	เงินสดขาดเกิน	เงินสด(ขาด)เกิน#1	เงินสด(ขาด)เกิน#2	เงินสด(ขาด)เกิน#3	เงินสด(ขาด)เกิน#4	ผู้รับผิดชอบ
    final_df30000 = df_batch_daily30000[
        [
            "วันที่ตรวจนับ",
            "รหัสร้าน",
            "ชื่อร้าน",
            "Zone",
            "เงินสำรอง",
            "เงินสดขาดเกิน",
            "เงินสด(ขาด)เกิน#1",
            "เงินสด(ขาด)เกิน#2",
            "เงินสด(ขาด)เกิน#3",
            "เงินสด(ขาด)เกิน#4",
            "ผู้รับผิดชอบ",
        ]
    ]
    # final_df30000.rename(columns={"GM_y": "GM"}, inplace=True)

    # Create an Excel file for the output
    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, index=False)
    output_buffer.seek(0)

    # Create an Excel file for the output 30000
    output_buffer30000 = io.BytesIO()
    with pd.ExcelWriter(output_buffer30000, engine="xlsxwriter") as writer30000:
        final_df30000.to_excel(writer30000, index=False)
    output_buffer30000.seek(0)

    return output_buffer, output_buffer30000


# Streamlit app
logo_path = "logo.png"  # Path to the company logo

st.image(logo_path, width=200)

# Streamlit app
st.title("CP project File Processing App \nยอด (ขาดเกิน) by New🔥")

# File upload
uploaded_file1 = st.file_uploader("Upload batch daily 8130", type=["csv", "xlsx"])
uploaded_file2 = st.file_uploader("Upload user branch month", type=["xlsx"])

if uploaded_file1 and uploaded_file2:
    # Process files
    output_buffer, output_buffer30000 = process_files(uploaded_file1, uploaded_file2)
    # output_buffer, output_buffer30000 = process_files(uploaded_file1, uploaded_file2)

    # Download link for the final output file
    st.download_button(
        label="Download final reprot batch daily 8130",
        data=output_buffer,
        file_name="final_report_nm.xlsx",
    )

    # Download link for the final output file30000
    st.download_button(
        label="Download final report batch daily 8130 (30000)",
        data=output_buffer30000,
        file_name="final_report_30000.xlsx",
    )
