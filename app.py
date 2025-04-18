import requests

# List of important Indian law PDFs and their URLs
laws = {
    "Indian Penal Code (IPC)": "https://www.indiacode.nic.in/bitstream/123456789/2189/1/indian_penal_code.pdf",
    "Criminal Procedure Code (CrPC)": "https://www.indiacode.nic.in/bitstream/123456789/2188/1/criminal_procedure_code.pdf",
    "Indian Evidence Act": "https://www.indiacode.nic.in/bitstream/123456789/1566/1/the_indian_evidence_act.pdf",
    "Juvenile Justice Act": "https://www.indiacode.nic.in/bitstream/123456789/1998/1/the_juvenile_justice_act_2015.pdf",
    "The Information Technology Act (IT Act)": "https://www.indiacode.nic.in/bitstream/123456789/1997/1/it_act_2000.pdf"
}

# Download each PDF
for law, url in laws.items():
    pdf_filename = law.replace(" ", "_") + ".pdf"
    response = requests.get(url)

    if response.status_code == 200:
        with open(pdf_filename, "wb") as file:
            file.write(response.content)
        print(f"✅ Downloaded: {pdf_filename}")
    else:
        print(f"❌ Failed to download: {law}")
