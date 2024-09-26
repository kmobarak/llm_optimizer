import docx
import re

# Load the Word document
def load_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

# Function to classify the analysis
def classify_analysis(text):
    both_correct = 0
    initial_correct = 0
    modified_correct = 0
    both_wrong = 0

    # Split into sections
    sections = re.split(r'- Difficulty level:', text)

    # Iterate through each section and classify
    for section in sections:
        if 'Both answers are correct' in section:
            both_correct += 1
        elif 'Initial correct, modified wrong' in section or 'The initial is correct while the modified is wrong' in section:
            initial_correct += 1
        elif 'Initial wrong, modified correct' in section or 'The initial was wrong while the modified was correct' in section:
            modified_correct += 1
        elif 'Both are wrong' in section or 'The two answers are wrong' in section:
            both_wrong += 1

    return both_correct, initial_correct, modified_correct, both_wrong

# Display the results
def display_results(both_correct, initial_correct, modified_correct, both_wrong):
    print(f"Both answers correct: {both_correct}")
    print(f"Initial correct, Modified wrong: {initial_correct}")
    print(f"Modified correct, Initial wrong: {modified_correct}")
    print(f"Both answers wrong: {both_wrong}")

# Main logic to process the file and classify
def analyze_docx(file_path):
    content = load_docx(file_path)
    both_correct, initial_correct, modified_correct, both_wrong = classify_analysis(content)
    display_results(both_correct, initial_correct, modified_correct, both_wrong)

# Example file path
word_file_path = '/Users/khaled/myThesis/thesis/analysis.docx'
analyze_docx(word_file_path)
