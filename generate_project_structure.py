import os

def generate_file_structure(startpath, output_file="file_structure.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, "").count(os.sep)
            indent = "│   " * level + "├── " if level else ""
            f.write(f"{indent}{os.path.basename(root)}/\n")

            sub_indent = "│   " * (level + 1) + "├── "
            for file in files:
                f.write(f"{sub_indent}{file}\n")
    
    print(f"✅ File structure saved to {output_file}")

# Run the function in the current directory
generate_file_structure(os.getcwd())
