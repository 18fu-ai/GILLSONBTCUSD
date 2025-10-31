import typer
from rich.console import Console
from rich.table import Table
import datetime
import time
import math
import random

# --- System Constants ---
GENESIS_TIMESTAMP_STR = "2025-10-31 07:05:48.763177"
GENESIS_TIMESTAMP = datetime.datetime.fromisoformat(GENESIS_TIMESTAMP_STR)
TOKEN_NAME = "$EPIC25"
POBW_RATE_PER_SECOND = 0.001  # Rate of token generation per GB/s of bandwidth
STAKING_APY = 0.25  # 25% Annual Percentage Yield

# --- Simulation State ---
class VirtualGMU:
    def __init__(self):
        self.active = True
        self.total_bandwidth_gb_s = 1_000_000_000  # 1 TB/s
        self.utilized_bandwidth_gb_s = 0

    def get_status(self):
        return {
            "active": self.active,
            "total_bandwidth": f"{self.total_bandwidth_gb_s / 1_000_000_000:.1f} TB/s",
            "utilized_bandwidth": f"{self.utilized_bandwidth_gb_s:.2f} GB/s",
        }

class Tokenomics:
    def __init__(self):
        self.total_supply = 0.0
        self.balances = {}  # user -> { "tokens": float, "staked": float, "last_stake_update": datetime }
        self.pobw_contributions = {} # user -> { "bandwidth_gb_s": float, "last_claim_timestamp": datetime }

    def _get_current_time(self):
        """Gets the current simulated time."""
        # In a real scenario, this would be the actual current time.
        # For this simulation, we'll just use the system clock.
        return datetime.datetime.now()

    def _update_staking_rewards(self, user: str):
        """Calculates and adds staking rewards for a user."""
        if user not in self.balances or self.balances[user]["staked"] == 0:
            return

        now = self._get_current_time()
        last_update = self.balances[user]["last_stake_update"]
        time_staked_seconds = (now - last_update).total_seconds()

        # APY to per-second interest rate
        per_second_rate = STAKING_APY / (365 * 24 * 60 * 60)

        # Calculate rewards
        rewards = self.balances[user]["staked"] * per_second_rate * time_staked_seconds

        self.balances[user]["tokens"] += rewards
        self.total_supply += rewards
        self.balances[user]["last_stake_update"] = now

    def get_balance(self, user: str):
        self._update_staking_rewards(user)
        return self.balances.get(user, {"tokens": 0.0, "staked": 0.0})

    def _ensure_user_exists(self, user: str):
        if user not in self.balances:
            self.balances[user] = {"tokens": 0.0, "staked": 0.0, "last_stake_update": self._get_current_time()}
        if user not in self.pobw_contributions:
            self.pobw_contributions[user] = {"bandwidth_gb_s": 0.0, "last_claim_timestamp": self._get_current_time()}

    def contribute_pobw(self, user: str, bandwidth_gb_s: float):
        self._ensure_user_exists(user)
        self.pobw_contributions[user]["bandwidth_gb_s"] = bandwidth_gb_s
        # Reset the claim timestamp when contribution changes
        self.pobw_contributions[user]["last_claim_timestamp"] = self._get_current_time()

    def claim_pobw_rewards(self, user: str):
        self._ensure_user_exists(user)

        now = self._get_current_time()
        last_claim = self.pobw_contributions[user]["last_claim_timestamp"]
        bandwidth = self.pobw_contributions[user]["bandwidth_gb_s"]

        if bandwidth == 0:
            return 0.0

        seconds_passed = (now - last_claim).total_seconds()
        rewards = seconds_passed * bandwidth * POBW_RATE_PER_SECOND

        self.balances[user]["tokens"] += rewards
        self.total_supply += rewards
        self.pobw_contributions[user]["last_claim_timestamp"] = now

        return rewards

    def stake_tokens(self, user: str, amount: float):
        self._ensure_user_exists(user)
        self._update_staking_rewards(user)

        if self.balances[user]["tokens"] < amount:
            return False, "Insufficient token balance."

        self.balances[user]["tokens"] -= amount
        self.balances[user]["staked"] += amount
        return True, f"Successfully staked {amount} {TOKEN_NAME}."

    def unstake_tokens(self, user: str, amount: float):
        self._ensure_user_exists(user)
        self._update_staking_rewards(user)

        if self.balances[user]["staked"] < amount:
            return False, "Insufficient staked balance."

        self.balances[user]["staked"] -= amount
        self.balances[user]["tokens"] += amount
        return True, f"Successfully unstaked {amount} {TOKEN_NAME}."

# --- CLI App ---
app = typer.Typer()
console = Console()
gmu = VirtualGMU()
tokenomics = Tokenomics()

# Dummy users for simulation
SIM_USERS = ["Donny", "Jules", "VALOR_DAO"]

@app.command()
def status():
    """Display the current status of the Virtual GMU and Tokenomics."""
    console.print("[bold cyan]ValorAiChip++ virtual-GMU Status[/bold cyan]")

    gmu_status = gmu.get_status()
    table = Table(title="vGMU Core")
    table.add_column("Parameter", style="magenta")
    table.add_column("Value", style="green")
    table.add_row("Activation Time", str(GENESIS_TIMESTAMP))
    table.add_row("Status", "Active" if gmu_status["active"] else "Inactive", style="green" if gmu_status["active"] else "red")
    table.add_row("Total Bandwidth", gmu_status["total_bandwidth"])
    console.print(table)

    console.print(f"\n[bold cyan]{TOKEN_NAME} Tokenomics[/bold cyan]")
    table = Table(title="Economy")
    table.add_column("Parameter", style="magenta")
    table.add_column("Value", style="green")
    table.add_row("Total Supply", f"{tokenomics.total_supply:.4f} {TOKEN_NAME}")
    table.add_row("Staking APY", f"{STAKING_APY * 100:.2f}%")
    console.print(table)

@app.command()
def balances():
    """Show the token balances for all simulated users."""
    console.print(f"[bold yellow]User Balances ({TOKEN_NAME})[/bold yellow]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("User")
    table.add_column("Liquid Tokens", justify="right")
    table.add_column("Staked Tokens", justify="right")
    table.add_column("Total", justify="right")

    for user in SIM_USERS:
        balance = tokenomics.get_balance(user)
        liquid = balance['tokens']
        staked = balance['staked']
        total = liquid + staked
        table.add_row(user, f"{liquid:.4f}", f"{staked:.4f}", f"{total:.4f}")

    console.print(table)


@app.command()
def contribute(
    user: str = typer.Option("Donny", help="The user contributing bandwidth."),
    bandwidth: float = typer.Option(lambda: random.uniform(100, 5000), help="Bandwidth in GB/s.")
):
    """Simulate a user contributing bandwidth to the network."""
    if user not in SIM_USERS:
        SIM_USERS.append(user)
    tokenomics.contribute_pobw(user, bandwidth)
    console.print(f"[green]✅ {user} is now contributing {bandwidth:.2f} GB/s to the network.[/green]")
    console.print("Run 'claim-rewards' to mint PoBW tokens.")

@app.command()
def claim_rewards(user: str = typer.Argument("Donny", help="The user claiming rewards.")):
    """Claim Proof-of-Bandwidth rewards for a user."""
    rewards = tokenomics.claim_pobw_rewards(user)
    if rewards > 0:
        console.print(f"[green]✅ {user} claimed {rewards:.4f} {TOKEN_NAME} in PoBW rewards.[/green]")
    else:
        console.print(f"[yellow]⚠️ No rewards to claim for {user}. Have they contributed bandwidth?[/yellow]")

@app.command()
def stake(
    user: str = typer.Argument("Donny", help="The user staking tokens."),
    amount: float = typer.Argument(..., help=f"The amount of {TOKEN_NAME} to stake.")
):
    """Stake tokens to earn yield."""
    success, message = tokenomics.stake_tokens(user, amount)
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ Error: {message}[/red]")

@app.command()
def unstake(
    user: str = typer.Argument("Donny", help="The user unstaking tokens."),
    amount: float = typer.Argument(..., help=f"The amount of {TOKEN_NAME} to unstake.")
):
    """Unstake tokens."""
    success, message = tokenomics.unstake_tokens(user, amount)
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ Error: {message}[/red]")

def initialize_state():
    """Sets up the initial state for the simulation."""
    # Donny is a big contributor
    donny_initial_pobw = 15000.0
    tokenomics.contribute_pobw("Donny", donny_initial_pobw)

    # Simulate a short passage of time for initial rewards
    time.sleep(1)

    # Give Donny some initial tokens to stake
    initial_claim = tokenomics.claim_pobw_rewards("Donny")
    if initial_claim > 0:
        tokenomics.stake_tokens("Donny", initial_claim / 2)

    # VALOR_DAO starts with some staked tokens
    valor_dao_initial = 1000000.0
    tokenomics.balances["VALOR_DAO"] = {"tokens": 0, "staked": valor_dao_initial, "last_stake_update": tokenomics._get_current_time()}
    tokenomics.total_supply += valor_dao_initial


if __name__ == "__main__":
    initialize_state()
    app()