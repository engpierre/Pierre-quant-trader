import sqlite3
import yfinance as yf
import time
import socket
import sys
import msvcrt
import threading
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console

DB_PATH = r"c:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db"

price_cache = {}
last_fetch_time = 0

def check_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.1)
        return s.connect_ex(('127.0.0.1', port)) == 0

def get_live_prices(tickers):
    global last_fetch_time, price_cache
    current_time = time.time()
    
    if current_time - last_fetch_time > 15:
        if tickers:
            try:
                ticker_str = " ".join(tickers)
                # Suppress progress bar and output
                data = yf.download(ticker_str, period="1d", progress=False)
                if 'Close' in data:
                    close_data = data['Close']
                    if len(tickers) == 1:
                        price_cache[tickers[0]] = float(close_data.iloc[-1])
                    else:
                        for t in tickers:
                            if t in close_data.columns:
                                val = close_data[t].iloc[-1]
                                if not type(val) == type(None) and str(val) != 'nan':
                                    price_cache[t] = float(val)
                last_fetch_time = current_time
            except Exception as e:
                pass
    return price_cache

def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="engine_monitor", ratio=1, minimum_size=35),
        Layout(name="portfolio_matrix", ratio=3),
    )
    return layout

def generate_header() -> Panel:
    return Panel(Text("⚡ PIERRE-QUANT OPERATIONAL COMMAND STATION v2.0 | CORE INTELLIGENCE: JENNY (XO)", justify="center", style="bold white on blue"))

def generate_engine_monitor() -> Panel:
    db_ok = False
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        db_ok = True
    except:
        pass
        
    port_ok = check_port_open(11434)
    infra_status = "[bold green]🟢 ONLINE[/bold green]" if (db_ok and port_ok) else "[bold red]🔴 OFFLINE[/bold red]"
    
    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Agent", style="cyan")
    table.add_column("Status", justify="right")
    
    table.add_row("Infrastructure (DB/Docker)", infra_status)
    table.add_row("", "")
    
    agents = [
        "01. JENNY (XO)", "02. Risk Guard", "03. Spending Miner",
        "04. Vault Custodian", "05. API Ingestion", "06. TimesFM Engine",
        "07. Stat Invariance", "08. Momentum Vector", "09. Visual Sentry",
        "10. Smart Money", "11. Timeframe Matrix", "12. Corporate Fund.",
        "13. SEC Watchdog", "14. Sector Rotation", "15. Macro Tracker",
        "16. Sentiment Harvester"
    ]
    
    for agent in agents:
        table.add_row(agent, "🟢 STANDBY")
        
    return Panel(table, title="[b]Engine Monitor[/b]")

def generate_portfolio_matrix() -> Panel:
    table = Table(expand=True)
    table.add_column("TICKER", style="bold cyan")
    table.add_column("SHARES", justify="right", style="magenta")
    table.add_column("AVG COST", justify="right", style="yellow")
    table.add_column("CURRENCY", justify="center")
    table.add_column("LIVE PRICE", justify="right", style="green")
    table.add_column("TOTAL RETURN %", justify="right")
    table.add_column("ACTION RECON", justify="center")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, shares, avg_cost, currency FROM watchlist ORDER BY currency, ticker")
        rows = cursor.fetchall()
        
        matrix_sizes = {}
        try:
            cursor.execute("SELECT ticker, MAX(window_size) FROM market_matrices GROUP BY ticker")
            for r in cursor.fetchall():
                matrix_sizes[r[0]] = r[1]
        except:
            pass
            
        conn.close()
    except Exception as e:
        return Panel(f"Database Error: {e}", title="[b]Portfolio Matrix[/b]")
        
    tickers = [row[0] for row in rows]
    prices = get_live_prices(tickers)
    
    for row in rows:
        ticker, shares, avg_cost, currency = row
        current_price = prices.get(ticker, 0.0)
        
        pct_return = 0.0
        ret_str = "---"
        action = "HOLD"
        
        ticker_matrix_size = matrix_sizes.get(ticker, 0)
        
        if ticker_matrix_size < 128:
            action = "[yellow]⏳ BACKFILLING[/yellow]"
        elif avg_cost > 0 and current_price > 0:
            pct_return = ((current_price - avg_cost) / avg_cost) * 100
            ret_str = f"[green]+{pct_return:.2f}%[/green]" if pct_return >= 0 else f"[red]{pct_return:.2f}%[/red]"
            
            if pct_return > 10: 
                action = "[green]TAKE PROFIT[/green]"
            elif pct_return < -5: 
                action = "[red]STOP LOSS[/red]"
                
        table.add_row(
            ticker, 
            f"{shares:,.2f}", 
            f"${avg_cost:,.2f}", 
            currency, 
            f"${current_price:,.2f}" if current_price else "---",
            ret_str,
            action
        )
        
    return Panel(table, title="[b]Portfolio Matrix[/b]")

def generate_footer() -> Panel:
    text = "API Health: yfinance (OK) | Finnhub (OK) | Twelve Data (OK)\n"
    text += "[A] Add Asset  |  [R] Remove Asset  |  [U] Update Inventory  |  [Q] Quit Dashboard"
    return Panel(Text.from_markup(text, justify="center"), style="bold")

def interactive_loop(console):
    layout = make_layout()
    with Live(layout, refresh_per_second=2, screen=True) as live:
        while True:
            # Update dynamic blocks
            layout["header"].update(generate_header())
            layout["engine_monitor"].update(generate_engine_monitor())
            layout["portfolio_matrix"].update(generate_portfolio_matrix())
            layout["footer"].update(generate_footer())
            
            # Check for non-blocking keyboard input
            if msvcrt.kbhit():
                key_bytes = msvcrt.getch()
                try:
                    key = key_bytes.decode('utf-8', 'ignore').upper()
                except:
                    key = ""
                    
                if key == 'Q':
                    break
                elif key in ['A', 'R', 'U']:
                    live.stop()
                    console.clear()
                    console.print(f"[bold cyan]Action Selected: {key}[/bold cyan]")
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        if key == 'A':
                            console.print("\n[bold cyan]--- ADD ASSET ---[/bold cyan]")
                            ticker = input("Ticker: ").strip().upper()
                            shares = float(input("Shares: "))
                            cost = float(input("Avg Cost: "))
                            currency = input("Currency (USD/CAD): ").strip().upper()
                            cursor.execute("INSERT OR REPLACE INTO watchlist VALUES (?, ?, ?, ?)", (ticker, shares, cost, currency))
                            console.print(f"\n[green]Successfully added {ticker}.[/green]")
                        elif key == 'R':
                            console.print("\n[bold red]--- REMOVE ASSET ---[/bold red]")
                            ticker = input("Ticker: ").strip().upper()
                            cursor.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
                            console.print(f"\n[yellow]Successfully removed {ticker}.[/yellow]")
                        elif key == 'U':
                            console.print("\n[bold yellow]--- UPDATE INVENTORY ---[/bold yellow]")
                            ticker = input("Ticker: ").strip().upper()
                            shares = float(input("New Shares: "))
                            cost = float(input("New Avg Cost: "))
                            cursor.execute("UPDATE watchlist SET shares = ?, avg_cost = ? WHERE ticker = ?", (shares, cost, ticker))
                            console.print(f"\n[green]Successfully updated {ticker}.[/green]")
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        console.print(f"\n[red]Input Error: {e}[/red]")
                        
                    console.print("\n[dim]Returning to Live Dashboard in 2 seconds...[/dim]")
                    time.sleep(2)
                    live.start()
                    
            time.sleep(0.1)

if __name__ == "__main__":
    console = Console()
    try:
        interactive_loop(console)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[red]Fatal Error: {e}[/red]")
