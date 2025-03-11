import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MaxNLocator
import time
import os
import subprocess
import re
import platform

def execute_traceroute(destination):
    try:
        # Use correct command based on OS
        traceroute_cmd = ["traceroute", "-I", destination]
        result = subprocess.run(traceroute_cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing traceroute: {e}"
    except FileNotFoundError:
        return "Traceroute command not found. Ensure it is installed on your system."

def parse_traceroute(traceroute_output):
    hops = []
    
    for line in traceroute_output.splitlines():
        line = line.strip()
        if not line or "traceroute to" in line:
            continue
        
        match = re.match(
            r"^\s*(\d+)\s+(?:\*+\s*)?(?:([\w\-.]+)\s*\(([\d\.]+)\)|([\d\.]+)|([\w\-.]+))?\s*(\*|\d+\.\d+ ms(?: !\w+)?)?\s*(\*|\d+\.\d+ ms(?: !\w+)?)?\s*(\*|\d+\.\d+ ms(?: !\w+)?)?",
            line
        )

        if match:
            hop_num = int(match.group(1))
            hostname = match.group(2) if match.group(2) else match.group(5) if match.group(5) else None
            ip = match.group(3) if match.group(3) else match.group(4) if match.group(4) else None

            rtt = []
            for i in range(6, 9):
                rtt_value = match.group(i)
                if rtt_value and rtt_value != '*':
                    rtt.append(float(re.sub(r" !\w+", "", rtt_value).split()[0]))  # Remove flags
                else:
                    rtt.append(None)

            if hostname == ip:
                hostname = None

            hops.append({
                "hop": hop_num,
                "ip": ip,
                "hostname": hostname,
                "rtt": rtt
            })

    # --- Visualization Part ---
    if not hops:
        print("No valid hops found.")
        return hops

    hop_numbers = [hop["hop"] for hop in hops]

    # Fix: Ensure only average non-None RTTs
    avg_rtts = []
    for hop in hops:
        valid_rtts = [r for r in hop["rtt"] if r is not None]
        avg_rtts.append(sum(valid_rtts) / len(valid_rtts) if valid_rtts else None)

    plt.figure(figsize=(10, 5))
    plt.plot(hop_numbers, avg_rtts, marker='o', linestyle='-', label="Traceroute RTT")
    
    plt.xlabel("Hop Number")
    plt.ylabel("Average Round Trip Time (ms)")
    plt.title("Traceroute Analysis")
    plt.xticks(hop_numbers)
    plt.legend()
    plt.grid(True)

    plt.show()

    return hops


# ============================================================================ #
#                    DO NOT MODIFY THE CODE BELOW THIS LINE                    #
# ============================================================================ #
def visualize_traceroute(destination, num_traces=3, interval=5, output_dir='output'):
    """
    Runs multiple traceroutes to a destination and visualizes the results.

    Args:
        destination (str): The hostname or IP address to trace
        num_traces (int): Number of traces to run
        interval (int): Interval between traces in seconds
        output_dir (str): Directory to save the output plot

    Returns:
        tuple: (DataFrame with trace data, path to the saved plot)
    """
    all_hops = []

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print(f"Running {num_traces} traceroutes to {destination}...")

    for i in range(num_traces):
        if i > 0:
            print(f"Waiting {interval} seconds before next trace...")
            time.sleep(interval)

        print(f"Trace {i+1}/{num_traces}...")
        output = execute_traceroute(destination)
        hops = parse_traceroute(output)

        # Add timestamp and trace number
        timestamp = time.strftime("%H:%M:%S")
        for hop in hops:
            hop['trace_num'] = i + 1
            hop['timestamp'] = timestamp
            all_hops.append(hop)

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(all_hops)

    # Calculate average RTT for each hop (excluding timeouts)
    df['avg_rtt'] = df['rtt'].apply(lambda x: np.mean([r for r in x if r is not None]) if any(r is not None for r in x) else None)

    # Plot the results
    plt.figure(figsize=(12, 6))

    # Create a subplot for RTT by hop
    ax1 = plt.subplot(1, 1, 1)

    # Group by trace number and hop number
    for trace_num in range(1, num_traces + 1):
        trace_data = df[df['trace_num'] == trace_num]

        # Plot each trace with a different color
        ax1.plot(trace_data['hop'], trace_data['avg_rtt'], 'o-',
                label=f'Trace {trace_num} ({trace_data.iloc[0]["timestamp"]})')

    # Add labels and legend
    ax1.set_xlabel('Hop Number')
    ax1.set_ylabel('Average Round Trip Time (ms)')
    ax1.set_title(f'Traceroute Analysis for {destination}')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Make sure hop numbers are integers
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    # Save the plot to a file instead of displaying it
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    safe_dest = destination.replace('.', '-')
    output_file = os.path.join(output_dir, f"trace_{safe_dest}_{timestamp}.png")
    plt.savefig(output_file)
    plt.close()

    print(f"Plot saved to: {output_file}")

    # Return the dataframe and the path to the saved plot
    return df, output_file

# Test the functions
if __name__ == "__main__":
    # Test destinations
    destinations = [
        "google.com",
        "amazon.com",
        "bbc.co.uk"  # International site
    ]

    for dest in destinations:
        df, plot_path = visualize_traceroute(dest, num_traces=3, interval=5)
        print(f"\nAverage RTT by hop for {dest}:")
        avg_by_hop = df.groupby('hop')['avg_rtt'].mean()
        print(avg_by_hop)
        print("\n" + "-"*50 + "\n")
