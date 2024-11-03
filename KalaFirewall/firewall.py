import subprocess
import atexit
import readline  # For handling up/down arrow keys in command history
import os
# ANSI escape codes for colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
CLEAR_SCREEN = "\033[H\033[J"

# Banner for the firewall
def show_banner():
    banner = f"""
    {CYAN}======================================
    |           {RED}KalaFireWall{CYAN}           |
    |   {GREEN}Simple Network Monitor{CYAN}       |
    | {BLUE}Developed for Traffic Control{CYAN}   |
    ======================================{RESET}

    {CYAN}+++++++++++++++++++++++++++++++++++++++++++++++
    {GREEN} By {BLUE} N V R K Sai Kamesh{CYAN}
    {CYAN}+++++++++++++++++++++++++++++++++++++++++++++++
    """
    print(banner)

class SimpleNetworkMonitor:
    def __init__(self, rules_file=None):
        self.allowed_ips = set()
        self.command_history = []  # Store command history
        self.reset_rules()

        if rules_file:
            self.load_rules(rules_file)

        # Register cleanup on exit
        atexit.register(self.cleanup_rules)

    def reset_rules(self):
        """Reset iptables rules to default, dropping all traffic by default."""
        try:
            subprocess.run(['sudo', 'iptables', '-F'], check=True)
            subprocess.run(['sudo', 'iptables', '-X'], check=True)
            subprocess.run(['sudo', 'iptables', '-P', 'INPUT', 'DROP'], check=True)
            subprocess.run(['sudo', 'iptables', '-P', 'OUTPUT', 'DROP'], check=True)
            print(f"{YELLOW}Default policy set to DROP for all IPs.{RESET}")
        except subprocess.CalledProcessError:
            print(f"{RED}Error: Could not reset iptables rules. Check permissions.{RESET}")

    def add_allowed_ip(self, ip):
        """Allow traffic for a specific IP."""
        if ip not in self.allowed_ips:
            self.allowed_ips.add(ip)
            try:
                subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'ACCEPT'], check=True)
                subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-d', ip, '-j', 'ACCEPT'], check=True)
                print(f"{GREEN}Allowed IP: {ip}{RESET}")
            except subprocess.CalledProcessError:
                print(f"{RED}Error: Could not allow IP: {ip}. Check permissions.{RESET}")

    def load_rules(self, rules_file):
        """Load allowed IP rules from a file."""
        try:
            with open(rules_file, 'r') as f:
                for line in f:
                    ip = line.strip()
                    if ip:
                        self.add_allowed_ip(ip)
            print(f"{GREEN}Loaded rules from {rules_file}{RESET}")
        except FileNotFoundError:
            print(f"{RED}Error: Rules file not found: {rules_file}{RESET}")

    def cleanup_rules(self):
        """Cleanup iptables rules to allow all traffic on exit."""
        try:
            subprocess.run(['sudo', 'iptables', '-P', 'INPUT', 'ACCEPT'], check=True)
            subprocess.run(['sudo', 'iptables', '-P', 'FORWARD', 'ACCEPT'], check=True)
            subprocess.run(['sudo', 'iptables', '-P', 'OUTPUT', 'ACCEPT'], check=True)
            print(f"{GREEN}\niptables rules reset to allow all traffic on exit.{RESET}")
        except subprocess.CalledProcessError:
            print(f"{RED}Error: Could not reset iptables rules on exit. Check permissions.{RESET}")

    def show_history(self):
        """Display command history."""
        print(f"{CYAN}Command History:{RESET}")
        for index, command in enumerate(self.command_history, start=1):
            print(f"{YELLOW}{index}. {command}{RESET}")

    def show_help(self):
        """Display help for commands."""
        print(f"{CYAN}Available Commands:{RESET}")
        print(f"  {GREEN}allow <IP>{RESET}      - Allow traffic for a specific IP")
        print(f"  {YELLOW}reset{RESET}           - Reset all iptables rules")
        print(f"  {CYAN}clear{RESET}           - Clear the screen")
        print(f"  {CYAN}history{RESET}         - Show command history")
        print(f"  {RED}exit{RESET}            - Exit the program")

def main():
    show_banner()
    monitor = SimpleNetworkMonitor()
    print(f"{CYAN}KalaFireWall CLI{RESET}")
    print("Commands:")
    print(f"  {GREEN}allow <IP>{RESET}      - Allow traffic for a specific IP")
    print(f"  {YELLOW}reset{RESET}           - Reset all iptables rules")
    print(f"  {CYAN}clear{RESET}           - Clear the screen")
    print(f"  {CYAN}history{RESET}         - Show command history")
    print(f"  {RED}exit{RESET}            - Exit the program")

    history_file = "kalaFirewall.txt"

    # Load previous command history if the file exists
    if os.path.exists(history_file):
        readline.read_history_file(history_file)

    try:
        while True:
            cmd = input(f"{CYAN}kala@firewall $ {RESET}").strip()
            if not cmd:
                continue

            monitor.command_history.append(cmd)  # Save command in history
            readline.add_history(cmd)  # Add to readline history

            command_parts = cmd.split()
            command = command_parts[0]
            ip = command_parts[1] if len(command_parts) > 1 else None

            if command == "allow" and ip:
                monitor.add_allowed_ip(ip)
            elif command == "reset":
                monitor.reset_rules()
                print(f"{YELLOW}All IPs unblocked.{RESET}")
            elif command == "clear":
                print(CLEAR_SCREEN, end="")
                show_banner()
            elif command == "history":
                monitor.show_history()
            elif command == "exit":
                # Save command history to a file
                readline.write_history_file(history_file)
                break
            else:
                print(f"{RED}Invalid command or missing IP. Please try again.{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted. Exiting and resetting iptables rules.{RESET}")
    finally:
        monitor.cleanup_rules()  # Ensure cleanup on exit

if __name__ == "__main__":
    main()
