"""Multiple Cold-Start Benchmark Runner.

Executes multiple fresh process launches to test consistency,
measure process-start-to-visible time, responsiveness latency, and verify zero hangs.
"""

import subprocess
import sys
import time
import os

def run_single_launch(run_idx: int) -> dict:
    cmd = [sys.executable, "benchmark_startup.py"]
    t_start = time.perf_counter()

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    stdout, stderr = proc.communicate(timeout=30)
    t_total = time.perf_counter() - t_start

    # Parse stdout for timings
    t_visible = None
    t_responsive = None

    for line in stdout.splitlines():
        if "MainWindow shown:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    t_visible = float(parts[1].strip().split()[0])
                except ValueError:
                    pass
        elif "First event loop cycle completed:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    t_responsive = float(parts[1].strip().split()[0])
                except ValueError:
                    pass

    return {
        "run": run_idx,
        "t_visible": t_visible,
        "t_responsive": t_responsive,
        "t_process_wall": t_total,
        "exit_code": proc.returncode,
        "stderr": stderr,
    }

def main():
    print("=" * 65)
    print("RUNNING 5 INDEPENDENT COLD-START LAUNCH BENCHMARKS")
    print("=" * 65)

    results = []
    for i in range(1, 6):
        print(f"\n[LAUNCH #{i}] Spawning independent process...")
        res = run_single_launch(i)
        results.append(res)
        print(f"  Exit code: {res['exit_code']}")
        print(f"  Start -> MainWindow Visible:   {res['t_visible']:.4f} s" if res['t_visible'] else "  Visible: N/A")
        print(f"  Start -> Event Loop Ready:    {res['t_responsive']:.4f} s" if res['t_responsive'] else "  Responsive: N/A")
        print(f"  Total Process Wall Clock:     {res['t_process_wall']:.4f} s")

    print("\n" + "=" * 65)
    print("SUMMARY OF 5 COLD LAUNCHES:")
    print("=" * 65)
    vis_times = [r["t_visible"] for r in results if r["t_visible"] is not None]
    resp_times = [r["t_responsive"] for r in results if r["t_responsive"] is not None]

    if vis_times:
        avg_vis = sum(vis_times) / len(vis_times)
        min_vis = min(vis_times)
        max_vis = max(vis_times)
        print(f"Time to MainWindow Visible:  Avg: {avg_vis:.3f} s (Min: {min_vis:.3f} s, Max: {max_vis:.3f} s)")

    if resp_times:
        avg_resp = sum(resp_times) / len(resp_times)
        min_resp = min(resp_times)
        max_resp = max(resp_times)
        print(f"Time to UI Responsive:       Avg: {avg_resp:.3f} s (Min: {min_resp:.3f} s, Max: {max_resp:.3f} s)")

    all_ok = all(r["exit_code"] == 0 for r in results)
    print(f"\nAll launches successful without hangs: {all_ok}")
    print("=" * 65)

if __name__ == "__main__":
    main()
