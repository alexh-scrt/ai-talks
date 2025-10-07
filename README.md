# Talks: Multi-Agent Philosophical Discussion System

<­ An AI-powered system that orchestrates rich philosophical discussions using game theory and emergent social dynamics.

## Features

- **Game-Theoretic Turn-Taking**: Mathematical model determines who speaks next
- **Depth-Aware Exploration**: Configure conversation depth (1-5 levels)
- **Personality Diversity**: 6 distinct personality archetypes
- **Gender Representation**: Male, female, and non-binary participants
- **Emergent Dynamics**: Relationships and coalitions form naturally
- **Smart Termination**: Multi-criteria conversation completion

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- NVIDIA GPU (optional, for GPU acceleration)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/talks.git
cd talks

# Install dependencies with conda
conda activate musequill
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Pull LLM model
docker exec talks-ollama ollama pull mistral
```

### Basic Usage

```bash
# Simple 2-person dialogue
python src/main.py --topic "What is consciousness?" --depth 3 --participants 2

# Use config file
python src/main.py --config configs/academic_panel.yaml

# Deep philosophical exploration
python src/main.py --topic "Ethics of AI" --depth 5 --participants 4 --max-turns 40
```

## Configuration

Create YAML configs to customize participants:

```yaml
topic: "Your question here"
depth: 3

participants:
  - name: Sophia
    gender: female
    personality: collaborative
    expertise: ethics
```

### Personality Types

- **Analytical**: Methodical, asks probing questions
- **Collaborative**: Seeks consensus, builds bridges
- **Assertive**: Confident, dominates discussion
- **Cautious**: Careful claims, hedges statements
- **Creative**: Novel perspectives, metaphorical
- **Skeptical**: Challenges assumptions, devil's advocate

## Architecture

The system uses a sophisticated game-theoretic approach to orchestrate multi-agent discussions:

### Core Components

1. **ParticipantState**: Tracks individual agent states including personality, expertise, relationships, and conversation metrics
2. **GroupDiscussionState**: Manages global discussion state, tracking progress, convergence, and group dynamics
3. **TurnSelector**: Uses game theory to determine speaking order based on urgency calculations
4. **PayoffCalculator**: Evaluates utility of different dialogue moves (DEEPEN, CHALLENGE, SUPPORT, etc.)
5. **ParticipantAgent**: Individual AI agents with distinct personalities and expertise
6. **Orchestrator**: Manages the overall discussion flow and coordination
7. **TerminationSystem**: Determines when discussions have reached natural conclusions

### Dialogue Moves

- **DEEPEN**: Introduce more nuanced aspects
- **CHALLENGE**: Present counterarguments
- **SUPPORT**: Build on others' insights
- **QUESTION**: Seek clarification
- **SYNTHESIZE**: Find common ground
- **CONCLUDE**: Summarize and wrap up

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_game_theory.py

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/
```

## Examples

### Simple Discussion

```bash
python src/main.py --topic "What makes art meaningful?" --depth 2 --participants 2
```

### Academic Panel

```bash
python src/main.py --config configs/academic_panel.yaml
```

### Custom Configuration

Create your own configuration file:

```yaml
topic: "Is free will an illusion?"
depth: 4

participants:
  - name: Dr Sarah Mitchell
    gender: female
    personality: analytical
    expertise: neuroscience
    
  - name: Prof Thomas Lee
    gender: male
    personality: skeptical
    expertise: philosophy
    
  - name: Dr Alex Rivera
    gender: non_binary
    personality: creative
    expertise: quantum_physics
```

## Depth Levels

1. **Surface (1)**: Basic exploration of the topic
2. **Principles (2)**: Underlying concepts and foundations
3. **Applications (3)**: Practical implications and examples
4. **Challenges (4)**: Edge cases and counterarguments
5. **Philosophy (5)**: Deep metaphysical and epistemological questions

## Troubleshooting

### Ollama Connection Issues
- Ensure Docker is running: `docker-compose ps`
- Check Ollama status: `docker logs talks-ollama`
- Verify port availability: `netstat -an | grep 11434`

### Model Not Found
- Pull the model: `docker exec talks-ollama ollama pull mistral`
- List available models: `docker exec talks-ollama ollama list`

### Slow Response Times
- Use smaller model: `mistral` instead of `mixtral`
- Reduce temperature in agent configuration
- Check system resources: `docker stats`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with LangChain and Ollama
- Uses ChromaDB for vector storage
- Redis for state management
- Rich for beautiful terminal output

---

## Next Steps

Future enhancements planned:
- Web API for programmatic access
- Real-time visualization of discussion dynamics
- Long-term memory across sessions
- Debate mode for competitive discussions
- Integration with more LLM providers

Enjoy watching AI agents engage in genuine philosophical discourse! <­# ai-talks
