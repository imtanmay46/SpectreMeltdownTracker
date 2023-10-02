import platform
import subprocess
import json
import datetime

def get_system_info():
    system_info = {
        'OS': platform.system(),
        'OS Version': platform.version(),
        'OS Release': platform.release(),
        'Architecture': platform.architecture(),
        'Machine': platform.machine(),
        'Processor': platform.processor(),
        'Python Version': platform.python_version(),
        'GCC Version': subprocess.getoutput('gcc --version | head -n 1').strip(),
        'LD Version': subprocess.getoutput('ld --version | head -n 1').strip(),
        'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return system_info

def get_cpu_info():
    try:
        cpu_info = {}
        command = 'lscpu'  # Linux specific command
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                cpu_info[key] = value
        return cpu_info
    except Exception as e:
        print(f"Error retrieving CPU information: {e}")
        return {}

def get_memory_info():
    try:
        memory_info = {}
        command = 'free -h'  # Linux specific command
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        lines = result.stdout.split('\n')
        keys = lines[0].split()
        values = lines[1].split()
        for key, value in zip(keys, values):
            memory_info[key] = value
        return memory_info
    except Exception as e:
        print(f"Error retrieving memory information: {e}")
        return {}

def run_shell_script():
    try:
        # Run the shell script with the specified command
        command = 'sudo ./spectre-meltdown-checker.sh -v --live --verbose --explain --arch-prefix PREFIX --batch json'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running the shell script: {e}")
        print(f"Command stderr: {e.stderr}")
        error_data = {
            "Error": "Failed to run the shell script",
            "Error Message": str(e),
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return json.dumps(error_data)

def process_shell_output(shell_output):
    if shell_output is None:
        return None

    try:
        # Parse the JSON output
        data = json.loads(shell_output)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def save_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")

def main():
    print("Gathering System Information...")

    system_info = get_system_info()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()

    system_info.update({"CPU Information": cpu_info, "Memory Information": memory_info})

    # Add a timestamp to the data
    system_info["Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save system information to a file
    save_to_file(system_info, "system_info.json")

    # Run the shell script
    shell_output = run_shell_script()

    # Process the shell script output
    vulnerabilities_data = process_shell_output(shell_output)

    # Merge system information and vulnerabilities data
    merged_data = {"System Information": system_info, "Vulnerabilities Data": vulnerabilities_data}

    # Save merged data to a file
    save_to_file(merged_data, "merged_output.json")

if __name__ == "__main__":
    main()
