import asyncio
import click
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.config import TalksConfig
from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator

console = Console()


@click.command()
@click.option("--topic", "-t", help="Discussion topic")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read topic from file")
@click.option("--depth", "-d", type=int, help="Depth level (1-5)")
@click.option("--participants", "-p", default=2, type=int, help="Number of participants")
@click.option("--panel", type=click.Choice(['philosophy', 'technology', 'popular_science', 'science', 'general', 'ai']), help="Use a predefined panel")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.option("--max-turns", "-m", type=int, help="Maximum number of turns")
@click.option("--narrator/--no-narrator", default=None, help="Enable/disable narrator")
def main(topic: str, file: str, depth: int, participants: int, panel: str, config: str, max_turns: int, narrator: bool):
    """Talks: Multi-Agent Philosophical Discussion System"""
    
    # Load system configuration
    talks_config = TalksConfig()
    
    # Read topic from file if provided
    if file and not topic:
        try:
            with open(file, 'r') as f:
                topic = f.read().strip()
                if not topic:
                    console.print("[red]Error: File is empty[/red]")
                    return
                console.print(f"[cyan]Topic loaded from file: {file}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return
    elif file and topic:
        console.print("[yellow]Warning: Both --topic and --file provided, using --topic[/yellow]")
    
    # Use config defaults if not specified
    if depth is None:
        depth = talks_config.default_depth
    if max_turns is None:
        max_turns = talks_config.max_turns
    if narrator is None:
        narrator = talks_config.narrator_enabled
    
    console.print(Panel.fit(
        "[bold cyan]🎭  Talks: Multi-Agent Discussion System[/bold cyan]",
        border_style="cyan"
    ))
    
    # Load config or use defaults
    if panel:
        # Load panel configuration
        panel_file = Path(__file__).parent.parent / "config" / "panels" / f"{panel}.yml"
        if panel_file.exists():
            with open(panel_file) as f:
                panel_data = yaml.safe_load(f)
            participants_config = panel_data["participants"]
            console.print(f"[cyan]Using {panel_data['panel_name']}[/cyan]")
            console.print(f"[dim]{panel_data['description']}[/dim]")
            
            # Show recommended topics if no topic provided
            if not topic and panel_data.get("recommended_topics"):
                console.print("\n[yellow]Recommended topics for this panel:[/yellow]")
                for t in panel_data["recommended_topics"][:5]:
                    console.print(f"  • {t}")
                console.print("\n[red]Please provide a topic with --topic[/red]")
                return
        else:
            console.print(f"[red]Panel configuration not found: {panel}[/red]")
            return
    elif config:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        participants_config = config_data["participants"]
        if not topic:
            topic = config_data.get("topic", "What is the meaning of life?")
        if config_data.get("depth"):
            depth = config_data["depth"]
    else:
        if not topic:
            console.print("[red]Error: Please provide a topic with --topic, --file, use a --panel, or a config file with --config[/red]")
            console.print("\nAvailable panels: philosophy, technology, popular_science, science, general, ai")
            console.print("\nExample usage:")
            console.print("  python main.py --topic 'What is consciousness?'")
            console.print("  python main.py --file question.txt")
            console.print("  python main.py --panel philosophy --topic 'Free will'")
            return
        participants_config = get_default_participants(participants)
    
    console.print(f"\n[bold]Topic:[/bold] {topic}")
    console.print(f"[bold]Depth:[/bold] {depth}/5")
    console.print(f"[bold]Participants:[/bold] {len(participants_config)}")
    console.print(f"[bold]Max Turns:[/bold] {max_turns}")
    console.print(f"[bold]Narrator:[/bold] {'Enabled' if narrator else 'Disabled'}\n")
    
    # Display participants
    for p in participants_config:
        console.print(
            f"  • {p['name']} ({p['gender']}) - "
            f"{p['personality']} - {p['expertise']}"
        )
    
    console.print("\n" + "─" * 60 + "\n")
    
    # Run discussion
    asyncio.run(run_discussion(topic, depth, participants_config, max_turns, narrator))


async def run_discussion(topic: str, depth: int, participants_config: list, max_turns: int, enable_narrator: bool):
    """Run the discussion and display results"""
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=depth,
        participants_config=participants_config,
        enable_narrator=enable_narrator
    )
    
    # Show forbidden topics from config
    if orchestrator.forbidden_topics:
        console.print(f"[dim]Forbidden topics: {', '.join(orchestrator.forbidden_topics)}[/dim]")
    
    # Generate and display narrator introduction if enabled
    if enable_narrator:
        introduction_segments = await orchestrator.run_introduction()
        if introduction_segments:
            console.print("\n[bold yellow]🎙️  Opening Introduction[/bold yellow]\n")
            
            for segment in introduction_segments:
                console.print(f"[bold yellow]{segment['speaker']}:[/bold yellow]")
                console.print(Panel(
                    segment['content'],
                    border_style="yellow",
                    padding=(1, 2),
                    title=f"[dim]{segment['type'].replace('_', ' ').title()}[/dim]"
                ))
                console.print()
            
            console.print("─" * 60 + "\n")
            console.print("[bold cyan]🎭  Discussion Begins[/bold cyan]\n")
    
    exchanges = await orchestrator.run_discussion(max_iterations=max_turns)
    
    # Display exchanges
    for exchange in exchanges:
        speaker = exchange["speaker"]
        content = exchange["content"]
        move = exchange["move"]
        turn = exchange["turn"]
        
        # Color code by move type
        move_colors = {
            "DEEPEN": "blue",
            "CHALLENGE": "red",
            "SUPPORT": "green",
            "QUESTION": "yellow",
            "SYNTHESIZE": "magenta",
            "CONCLUDE": "cyan"
        }
        move_color = move_colors.get(move, "white")
        
        console.print(f"\n[bold cyan]Turn {turn + 1}: {speaker}[/bold cyan] [dim {move_color}]({move})[/dim {move_color}]")
        
        # Handle target mentions
        if exchange.get("target"):
            target_name = orchestrator.group_state.get_participant(exchange["target"]).name
            console.print(f"[dim]→ addressing {target_name}[/dim]")
        
        console.print(Panel(content, border_style="cyan", padding=(1, 2)))
    
    # Display summary
    console.print("\n" + "─" * 60)
    console.print(f"\n[bold green]✅ Discussion Complete[/bold green]")
    console.print(f"Total Exchanges: {len(exchanges)}")
    console.print(f"Aspects Explored: {len(orchestrator.group_state.aspects_explored)}")
    console.print(f"Max Depth Reached: {orchestrator.group_state.max_depth_reached}/{depth}")
    console.print(f"Convergence Level: {orchestrator.group_state.convergence_level:.0%}")
    console.print(f"Novelty Score: {orchestrator.group_state.novelty_score:.0%}")
    
    # Show participant statistics
    console.print(f"\n[bold]Participant Statistics:[/bold]")
    for pid, agent in orchestrator.participants.items():
        state = agent.state
        console.print(f"  • {state.name}: {state.speaking_turns} turns, {state.words_spoken} words")
    
    # Display narrator closing if enabled
    if enable_narrator and orchestrator.closing_segments:
        console.print("\n" + "─" * 60 + "\n")
        console.print("[bold yellow]🎙️  Closing Remarks[/bold yellow]\n")
        
        for segment in orchestrator.closing_segments:
            console.print(f"[bold yellow]{segment['speaker']}:[/bold yellow]")
            console.print(Panel(
                segment['content'],
                border_style="yellow",
                padding=(1, 2),
                title=f"[dim]{segment['type'].replace('_', ' ').title()}[/dim]"
            ))
            console.print()
        
        console.print("[dim italic]Thank you for joining AI Talks![/dim italic]")


def get_default_participants(count: int) -> list:
    """Get default participant configurations"""
    
    defaults = [
        {
            "name": "Sophia",
            "gender": "female",
            "personality": "collaborative",
            "expertise": "ethics"
        },
        {
            "name": "Marcus",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "logic"
        },
        {
            "name": "Aisha",
            "gender": "female",
            "personality": "analytical",
            "expertise": "science"
        },
        {
            "name": "James",
            "gender": "male",
            "personality": "creative",
            "expertise": "philosophy"
        },
        {
            "name": "Elena",
            "gender": "female",
            "personality": "assertive",
            "expertise": "psychology"
        }
    ]
    
    return defaults[:count]


if __name__ == "__main__":
    main()