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
@click.option("--panel", type=click.Choice(['philosophy', 'technology', 'popular_science', 'science', 'general', 'ai', 'crypto']), help="Use a predefined panel")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.option("--max-turns", "-m", type=int, help="Maximum number of turns")
@click.option("--narrator/--no-narrator", default=None, help="Enable/disable narrator")
@click.option("--synthesis/--no-synthesis", default=None, help="Enable/disable synthesizer")
@click.option("--synthesis-style", type=click.Choice(['hegelian', 'socratic', 'pragmatic']), help="Synthesis style")
@click.option("--synthesis-freq", type=int, help="Synthesize every N turns")
@click.option("--rag-styling/--no-rag-styling", default=None, help="Enable/disable RAG style transfer")
@click.option("--coda/--no-coda", default=None, help="Enable/disable cognitive coda generation")
@click.option("--no-math-model", is_flag=True, help="Disable mathematical meaning model in coda")
@click.option("--redundancy-control/--no-redundancy-control", default=None, help="Enable/disable redundancy control")
@click.option("--dyad-limit", type=int, default=2, help="Max volleys per dyad (default: 2)")
@click.option("--similarity-threshold", type=float, default=0.85, help="Similarity threshold for redundancy (default: 0.85)")
@click.option("--progression-control/--no-progression-control", default=None, help="Enable/disable progression control")
@click.option("--cycles-threshold", type=int, default=2, help="Max cycles on same tension before test (default: 2)")
@click.option("--max-consequence-tests", type=int, default=2, help="Max consequence tests before pivot (default: 2)")
@click.option("--quotes/--no-quotes", default=None, help="Enable/disable philosophical quote enrichment")
@click.option("--quote-interval", type=int, default=8, help="Turns between quotes (default: 8)")
@click.option("--no-quote-adaptation", is_flag=True, help="Disable voice adaptation for quotes")
def main(topic: str, file: str, depth: int, participants: int, panel: str, config: str, max_turns: int, narrator: bool,
         synthesis: bool, synthesis_style: str, synthesis_freq: int, rag_styling: bool, coda: bool,
         no_math_model: bool, redundancy_control: bool, dyad_limit: int, similarity_threshold: float,
         progression_control: bool, cycles_threshold: int, max_consequence_tests: int,
         quotes: bool, quote_interval: int, no_quote_adaptation: bool):
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
    
    # Synthesis defaults
    if synthesis is None:
        synthesis = talks_config.get('synthesizer.enabled', True)
    if synthesis_style is None:
        synthesis_style = talks_config.get('synthesizer.style', 'hegelian')
    if synthesis_freq is None:
        synthesis_freq = talks_config.get('synthesizer.frequency', 8)
    
    # RAG styling default
    if rag_styling is None:
        rag_styling = talks_config.rag_style_transfer_enabled
    
    # Coda default
    if coda is None:
        coda = talks_config.coda_enabled
    
    # Redundancy control defaults
    if redundancy_control is None:
        redundancy_control = talks_config.get('redundancy_control.enabled', True)
    
    # Progression control defaults
    if progression_control is None:
        progression_control = talks_config.get('progression_engine.enabled', True)
    
    # Quote enrichment defaults  
    if quotes is None:
        quotes = talks_config.get('quotes.enabled', True)
    
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
    console.print(f"[bold]Narrator:[/bold] {'Enabled' if narrator else 'Disabled'}")
    console.print(f"[bold]Synthesizer:[/bold] {'Enabled' if synthesis else 'Disabled'} ({synthesis_style}, every {synthesis_freq} turns)")
    console.print(f"[bold]RAG Styling:[/bold] {'Enabled' if rag_styling else 'Disabled'}")
    console.print(f"[bold]Coda:[/bold] {'Enabled' if coda else 'Disabled'} (math model: {'Disabled' if no_math_model else 'Enabled'})")
    console.print(f"[bold]Redundancy Control:[/bold] {'Enabled' if redundancy_control else 'Disabled'} (dyad limit: {dyad_limit}, similarity: {similarity_threshold})")
    console.print(f"[bold]Progression Control:[/bold] {'Enabled' if progression_control else 'Disabled'} (cycles: {cycles_threshold}, tests: {max_consequence_tests})")
    console.print(f"[bold]Quote Enrichment:[/bold] {'Enabled' if quotes else 'Disabled'} (interval: {quote_interval}, adaptation: {'Disabled' if no_quote_adaptation else 'Enabled'})\n")
    
    # Display participants
    for p in participants_config:
        console.print(
            f"  • {p['name']} ({p['gender']}) - "
            f"{p['personality']} - {p['expertise']}"
        )
    
    console.print("\n" + "─" * 60 + "\n")
    
    # Run discussion
    asyncio.run(run_discussion(topic, depth, participants_config, max_turns, narrator,
                               synthesis, synthesis_style, synthesis_freq, rag_styling, coda,
                               not no_math_model, redundancy_control, dyad_limit, similarity_threshold,
                               progression_control, cycles_threshold, max_consequence_tests,
                               quotes, quote_interval, not no_quote_adaptation))


async def run_discussion(topic: str, depth: int, participants_config: list, max_turns: int, enable_narrator: bool,
                        enable_synthesis: bool, synthesis_style: str, synthesis_freq: int, use_rag_styling: bool,
                        enable_coda: bool, enable_mathematical_model: bool, enable_redundancy_control: bool, 
                        dyad_limit: int, similarity_threshold: float, enable_progression_control: bool,
                        cycles_threshold: int, max_consequence_tests: int,
                        enable_quotes: bool, quote_interval: int, enable_quote_adaptation: bool):
    """Run the discussion and display results"""
    
    # Create progression config
    progression_config = {
        "cycles_threshold": cycles_threshold,
        "max_consequence_tests": max_consequence_tests,
        "enable_progression": enable_progression_control
    }
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=depth,
        participants_config=participants_config,
        enable_narrator=enable_narrator,
        enable_synthesizer=enable_synthesis,
        synthesis_frequency=synthesis_freq,
        synthesis_style=synthesis_style,
        use_rag_styling=use_rag_styling,
        enable_coda=enable_coda,
        enable_mathematical_model=enable_mathematical_model,
        enable_redundancy_control=enable_redundancy_control,
        max_dyad_volleys=dyad_limit,
        similarity_threshold=similarity_threshold,
        enable_progression_control=enable_progression_control,
        progression_config=progression_config,
        enable_quote_enrichment=enable_quotes,
        quote_interval=quote_interval,
        enable_quote_voice_adaptation=enable_quote_adaptation
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
    
    # DISPLAY STRATEGIC METRICS
    if orchestrator.enable_strategic_scoring and hasattr(orchestrator, 'strategic_metrics') and orchestrator.strategic_metrics:
        metrics = orchestrator.strategic_metrics
        
        console.print("\n[bold]📊 Strategic Metrics:[/bold]")
        console.print(f"  Turns Evaluated: {metrics['total_turns_evaluated']}")
        console.print(f"  Average Alignment: {metrics['avg_alignment']:.1%}")
        console.print(f"  Average Originality: {metrics['avg_originality']:.1%}")
        console.print(f"  Average Quality: {metrics['avg_quality']:.1%}")
        console.print(f"  Dominant Theme: [cyan]{metrics['dominant_theme'].replace('_', ' ').title()}[/cyan]")
        
        if metrics.get('objective_distribution'):
            console.print(f"\n  [bold]Objective Pursuit:[/bold]")
            for obj, count in sorted(metrics['objective_distribution'].items(), key=lambda x: x[1], reverse=True):
                obj_name = obj.replace('_', ' ').title()
                percentage = (count / metrics['total_turns_evaluated']) * 100
                console.print(f"    - {obj_name}: {count} turns ({percentage:.0f}%)")
    
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