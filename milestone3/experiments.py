import subprocess
import re
import csv

trace_files = [
    "A-10_new_1.5_a.pdf.trc",
    "A-9_new_trunk1.trc",
    "Corruption2.trc",
    "A-9_new_1.5.pdf.trc",
    "A-9_new_trunk2.trc"
]

# Experiment Matrix
cache_sizes = [8, 64, 256, 1024]
block_sizes = [8, 16, 64]
policies = ["RR", "RND"]
associativity = 4  # 4-way for the main comparison

output_csv = "results.csv"

def run_simulation():
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Trace File", "Cache Size (KB)", "Block Size (B)", "Policy", "Hit Rate (%)", "CPI"])

        print(f"Starting soon... Output will be saved to {output_csv}")

        for trace in trace_files:
            for size in cache_sizes:
                for block in block_sizes:
                    for policy in policies:
                        print(f"Running: {trace} | {size}KB | {block}B | {policy}...")

                        # Note: Uses -n -1 to run the whole file
                        cmd = [
                            "python", "main.py",
                            "-s", str(size),
                            "-b", str(block),
                            "-a", str(associativity),
                            "-r", policy,
                            "-p", "1024", 
                            "-u", "0",
                            "-n", "-1",
                            "-f", trace
                        ]

                        try:
                            # Run the simulator and capture output
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            output = result.stdout

                            # Regex to find Hit Rate and CPI in output
                            # Looks for "Hit Rate:      97.9658%"
                            hit_match = re.search(r"Hit Rate:\s+([\d\.]+)", output)
                            # Looks for "CPI:           4.02"
                            cpi_match = re.search(r"CPI:\s+([\d\.]+)", output)

                            hit_rate = hit_match.group(1) if hit_match else "Error"
                            cpi = cpi_match.group(1) if cpi_match else "Error"

                            # Write
                            writer.writerow([trace, size, block, policy, hit_rate, cpi])

                        except Exception as e:
                            print(f"Failed on {trace}: {e}")

    print("Done! written to results.csv")

if __name__ == "__main__":
    run_simulation()
