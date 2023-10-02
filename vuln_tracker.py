import subprocess
import json
import platform
import datetime

def get_system_info():
    try:
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
    except Exception as e:
        print(f"Error retrieving system information: {e}")
        return {}

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

def parse_attack_output(attack_output):
    lines = attack_output.split('\n')
    parsed_output = []

    for line in lines:
        parsed_output.append({'Line': line})

    return parsed_output

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

def run_attack_program():
    try:
        command = ['gcc', './lib/spectre.c', '-o', './lib/meltdown_test']
        subprocess.run(command, check=True)
        result = subprocess.run(['./lib/meltdown_test'], capture_output=True, check=True)
        return result.stdout.decode('utf-8')  # Decode bytes to string
    except subprocess.CalledProcessError as e:
        print(f"Error running the attack program: {e}")
        print(f"Command stderr: {e.stderr}")
        return None

def run_shell_script():
    try:
        # Run the shell script with the specified command
        command = 'sudo ./lib/spectre-meltdown-checker.sh -v --live --verbose --explain --arch-prefix PREFIX --batch json'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running the shell script: {e}")
        print(f"Command stderr: {e.stderr}")
        return None

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

def export_to_readable_json(data, output_filename='output.json'):
    if data is not None:
        # Convert the data to a readable JSON format
        with open(output_filename, 'w') as json_file:
            json.dump(data, json_file, indent=2)

def main():
    try:
        print("Gathering System Information...")
        system_info = get_system_info()
        cpu_info = get_cpu_info()
        memory_info = get_memory_info()

        system_info.update({"CPU Information": cpu_info, "Memory Information": memory_info})

        # Add a timestamp to the data
        system_info["Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        attack_output = run_attack_program()

        # Save all data to a single JSON file
        # filename = "output_data.json"
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"./data_exports/{current_timestamp}.json"


        with open(filename, "w") as file:
            json.dump(
                {
                    "System Information": system_info,
                    "Manufacturer Vulnerabilities Data": process_shell_output(run_shell_script()),
                    "Attack Output": parse_attack_output(attack_output)
                    
                },
                file,
                indent=4
            )
        print(f"Data saved to {filename}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
