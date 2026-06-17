import requests
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.box import ROUNDED

console = Console()
URL = "http://x140az9ml49yv8vkhbcaabm3.72.60.200.169.sslip.io/v1/chat/completions"

def main():
    console.clear()
    console.print(
        Panel(
            Text("🧮 Hisab AI Terminal Chat Client v1.0\nType 'exit' or 'quit' to close.", justify="center", style="bold cyan"),
            box=ROUNDED,
            border_style="blue"
        )
    )

    messages = []

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold red]Goodbye![/bold red]")
                break
                
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})
            
            with console.status("[bold yellow]Hisab AI is thinking...[/bold yellow]", spinner="dots"):
                payload = {
                    "model": "Qwen3.5-2B-Q4_K_M.gguf",
                    "messages": messages,
                    "temperature": 0.1
                }
                r = requests.post(URL, json=payload, timeout=60)
                r.raise_for_status()
                response_data = r.json()
                
            reply = response_data["choices"][0]["message"]["content"]
            
            # clean up thinking tags if any remain
            if "</think>" in reply:
                reply = reply.split("</think>")[-1].strip()
            elif "<think>" in reply:
                reply = reply.replace("<think>", "").strip()

            messages.append({"role": "assistant", "content": reply})

            console.print()
            console.print(
                Panel(
                    Text(reply, style="white"),
                    title="[bold magenta]Hisab AI[/bold magenta]",
                    title_align="left",
                    box=ROUNDED,
                    border_style="magenta",
                    padding=(1, 2)
                )
            )

        except KeyboardInterrupt:
            console.print("\n[bold red]Session ended.[/bold red]")
            break
        except Exception as e:
            console.print(Panel(f"[bold red]Error:[/bold red] {str(e)}", border_style="red"))

if __name__ == "__main__":
    main()