import io
import csv
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

def convert_zoominfo_to_crm(reader):
    field_mapping = {
        '_ID': '',  # Leave empty or generate your own ID
        'Salutation': 'Salutation',
        'First Name': 'First Name',
        'Last Name': 'Last Name',
        'Company': 'Company Name',
        'Title': 'Job Title',
        'Phone': 'Direct Phone Number',
        'Mobile': 'Mobile phone',
        'Fax': 'Fax',
        'Email': 'Email Address',
        'Website': 'Website',
        'Street': 'Company Street Address',
        'City': 'Company City',
        'State': 'Company State',
        'ZipCode': 'Company Zip Code',
        'Country': 'Company Country',
        'Anniversary Date': '',  # No direct equivalent
        'Lead Source': 'ZoomInfo',  # Static value
        'Square Footage': '',  # No direct equivalent
        'Competitor': '',  # No direct equivalent
        'Disqualify Archive Reason': '',  # No direct equivalent
        'Rating': 'Contact Accuracy Grade',
        'Industry': 'Primary Industry',
        'No Of Employees': 'Employees',
        'Annual Revenue': 'Revenue (in 000s USD)',
        'Organization': 'Company Name',  # Duplicate of Company
        'Latitude': '',  # No direct equivalent
        'Longitude': '',  # No direct equivalent
        'Is Note': '',  # No direct equivalent
        'Parent_ID': '',  # No direct equivalent
        'NoteTopic': '',  # No direct equivalent
        'NoteSubject': '',  # No direct equivalent
        'Note': '',  # No direct equivalent
        'Activity Date': 'Job Start Date'
    }
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=field_mapping.keys())
    writer.writeheader()
    
    for row in reader:
        crm_row = {}
        for crm_field, zoominfo_field in field_mapping.items():
            if crm_field == 'Annual Revenue' and zoominfo_field:
                # Convert revenue from thousands to actual value
                revenue = row.get(zoominfo_field, '0').replace(',', '')
                crm_row[crm_field] = str(float(revenue) * 1000) if revenue.isdigit() else ''
            elif crm_field == 'Lead Source':
                crm_row[crm_field] = 'ZoomInfo'
            elif isinstance(zoominfo_field, str) and zoominfo_field in row:
                crm_row[crm_field] = row[zoominfo_field]
            else:
                crm_row[crm_field] = ''
        writer.writerow(crm_row)
    
    return output.getvalue()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
        
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
        
    if not file.filename.lower().endswith('.csv'):
        return 'Invalid file type', 400

    try:
        # Read and process in memory
        stream = io.TextIOWrapper(file.stream, encoding='utf-8-sig')
        reader = csv.DictReader(stream)
        converted = convert_zoominfo_to_crm(reader)
        
        # Return as downloadable file
        return send_file(
            io.BytesIO(converted.encode('utf-8')),
            mimetype='text/csv',
            download_name='crm_import_ready.csv',
            as_attachment=True
        )
    except Exception as e:
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
