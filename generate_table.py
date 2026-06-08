import os
import re

def get_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(1000) # Read first 1000 chars
        
    name = re.search(r'\*\*Name:\*\*\s*(.*)', content)
    platform = re.search(r'\*\*Platform:\*\*\s*(.*)', content)
    category = re.search(r'\*\*Category:\*\*\s*(.*)', content)
    difficulty = re.search(r'\*\*Difficulty:\*\*\s*(.*)', content)
    
    # Fallbacks for different formats
    if not name:
        title = re.search(r'^#\s*(.*?)(?:\s*CTF|\s*-|\s*Walkthrough|$)', content, re.MULTILINE)
        name_val = title.group(1).strip() if title else os.path.basename(filepath).replace('.md', '')
    else:
        name_val = name.group(1).strip()
        
    platform_val = platform.group(1).strip() if platform else "TryHackMe"
    category_val = category.group(1).strip() if category else "Boot2Root"
    difficulty_val = difficulty.group(1).strip() if difficulty else "TBD"
    
    return {
        "name": name_val,
        "platform": platform_val,
        "category": category_val,
        "difficulty": difficulty_val,
        "path": f"./{os.path.basename(filepath)}"
    }

def main():
    files = [f for f in os.listdir('.') if f.endswith('.md') and f != 'README.md']
    files.sort()
    
    rows = []
    for f in files:
        data = get_metadata(f)
        rows.append(f"| [{data['name']}]({data['path']}) | {data['platform']} | {data['category']} | {data['difficulty']} |")
    
    table_content = "\n".join([
        "| Challenge | Platform | Category | Difficulty |",
        "| :--- | :--- | :--- | :--- |",
        *rows
    ])
    
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
        
    pattern = r'<!-- START_TABLE -->.*?<!-- END_TABLE -->'
    replacement = f'<!-- START_TABLE -->\n{table_content}\n<!-- END_TABLE -->'
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_readme)

if __name__ == "__main__":
    main()
