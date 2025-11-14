import json
import os
from urllib.parse import quote

def replace_urls_in_content(md_content, mappings):
    """
    Replaces URLs in a markdown content string based on a list of mapping objects.

    Args:
        md_content (str): The markdown content to process.
        mappings (list): A list of mapping dictionaries.

    Returns:
        str: The markdown content with URLs replaced.
    """
    for item in mappings:
        url = item.get("url")
        filename = item.get("filename")
        main_section = item.get("main_section")
        parent_sections = item.get("parent_sections", [])

        if not url or not filename or not main_section:
            continue

        # Construct the local path
        local_path = os.path.join(".", main_section, *parent_sections, filename)
        # Normalize path for consistency (e.g., using forward slashes)
        local_path = local_path.replace("\\", "/")

        # URL-encode the path, keeping slashes and the initial './' safe
        encoded_path = quote(local_path, safe='./')

        # Replace the URL in the markdown content
        md_content = md_content.replace(url, encoded_path)
    return md_content

def process_file_pair(json_path, md_path):
    """
    Processes a single pair of JSON and Markdown files, updates the links,
    and saves the result to a new file.

    Args:
        json_path (str): Path to the JSON file with mappings.
        md_path (str): Path to the markdown file to update.

    Returns:
        list: The loaded mappings if successful, otherwise None.
    """
    output_path = md_path
    print(f"Processing {md_path} -> {output_path}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"  - Error reading or parsing JSON file {json_path}: {e}")
        return None

    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except IOError as e:
        print(f"  - Error reading markdown file {md_path}: {e}")
        return None

    updated_content = replace_urls_in_content(md_content, mappings)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"  - Successfully saved to {output_path}")
    except IOError as e:
        print(f"  - Error writing to output file {output_path}: {e}")
    
    return mappings

if __name__ == "__main__":
    # List of file pairs to process
    file_sets = [
        {'json': '算子开发工具.json', 'md': '算子开发工具.md'},
        {'json': 'Ascend C算子开发.json', 'md': 'Ascend C算子开发.md'},
        {'json': 'Ascend C算子开发接口.json', 'md': 'Ascend C算子开发接口.md'},
        {'json': 'Ascend C最佳实践.json', 'md': 'Ascend C最佳实践.md'},
    ]

    all_mappings = []
    for file_set in file_sets:
        # Check if both files exist before processing
        if os.path.exists(file_set['json']) and os.path.exists(file_set['md']):
            mappings = process_file_pair(file_set['json'], file_set['md'])
            if mappings:
                all_mappings.extend(mappings)
        else:
            print(f"Skipping pair {file_set['json']}/{file_set['md']} - one or both files not found.")

    # Process README.md using all collected mappings
    readme_path = 'README.md'
    readme_output_path = readme_path
    if os.path.exists(readme_path):
        print(f"Processing {readme_path} -> {readme_output_path}")
        if all_mappings:
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()

                updated_readme = replace_urls_in_content(readme_content, all_mappings)

                with open(readme_output_path, 'w', encoding='utf-8') as f:
                    f.write(updated_readme)
                print(f"  - Successfully saved to {readme_output_path}")

            except IOError as e:
                print(f"  - Error processing {readme_path}: {e}")
        else:
            print("  - Skipping README.md because no mappings were loaded.")
    else:
        print(f"Skipping {readme_path} - file not found.")