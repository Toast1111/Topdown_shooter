# Top-Down AI Shooter

A class-based top-down shooter game featuring two AI teams of 6 players each, with real machine learning capabilities and randomly generated battlefields.

## 🎮 Features

### **6 Unique Player Classes**
- **Assault:** Balanced fighter (HP:100, Speed:120, Damage:25, Range:200)
- **Sniper:** Long-range specialist (HP:75, Speed:90, Damage:80, Range:400) 
- **Heavy:** High-health tank with explosive abilities (HP:150, Speed:60, Damage:40)
- **Scout:** Fast flanker with high mobility (HP:70, Speed:180, Damage:20)
- **Support:** Suppression specialist (HP:90, Speed:100, Damage:30)
- **Medic:** Healer and team support (HP:85, Speed:110, Damage:15)

### **Real AI Learning System** 🤖
- **Neural Network Decision Making:** Each AI uses deep Q-learning with experience replay
- **Continuous Learning:** AI agents improve their strategies over time
- **Class-Specific Behaviors:** Each class has unique AI patterns and priorities
- **Team Coordination:** Dynamic strategy adaptation (aggressive/defensive/balanced)
- **Model Persistence:** AI progress is saved and loaded between sessions

### **Dynamic Battlefields** 🗺️
- **Random Map Generation:** Arena, maze, urban, bunker, and open field layouts
- **Collision Detection:** Cover mechanics and obstacle navigation
- **Strategic Positioning:** Spawn points optimized for balanced gameplay

### **Team Strategy System** ⚔️
- **Formation Keeping:** AI maintains tactical formations
- **Focus Fire:** Coordinated targeting of priority enemies  
- **Role-Based Positioning:** Medics stay back, heavies take point, scouts flank
- **Adaptive Tactics:** Teams adjust strategy based on current situation

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required packages:
- `pygame>=2.5.0` - Game engine and graphics
- `numpy>=1.21.0` - Neural network computations
- `torch>=1.9.0` - Deep learning framework (optional, for advanced AI)
- `scikit-learn>=1.0.0` - Machine learning utilities
- `matplotlib>=3.5.0` - Performance visualization

## 🎯 Usage

### Run the Game
```bash
python main.py
```

### Game Controls
- **Arrow Keys:** Navigate class selection
- **Tab:** Switch between teams
- **Up/Down:** Change class for selected slot
- **Number Keys (1-6):** Quick select class type
- **Enter:** Start battle
- **ESC:** Pause game or exit

### Class Selection
1. Choose composition for Team 1 (6 players)
2. Choose composition for Team 2 (6 players)  
3. Press Enter to start the battle
4. Watch AI teams fight and learn!

## 🧠 AI Learning Details

### How It Works
The AI system uses **Deep Q-Learning** with the following components:

- **State Representation:** 10-dimensional state vector including health, position, enemy distances, team status
- **Action Space:** 12 discrete actions (movement directions, shooting, special abilities)
- **Neural Network:** 3-layer network (64→32→12 neurons) with ReLU activation
- **Experience Replay:** Stores and replays past experiences for improved learning
- **Epsilon-Greedy Exploration:** Balances exploration vs exploitation

### Learning Metrics
Each AI agent tracks:
- Win rate over episodes
- Average reward per episode
- Exploration rate (epsilon)
- Memory buffer size
- Class-specific performance statistics

### Model Persistence
AI models are automatically saved to `models/` directory:
- `{class_type}_{agent_id}.json` - Contains network weights and training state
- Models are loaded on startup for continuous learning across sessions

## 📊 Performance Analysis

### Combat Statistics
- Damage dealt/taken ratios
- Shot accuracy by class
- Survival rates
- Kill/death ratios
- Team coordination effectiveness

### AI Adaptation
- Strategy preference evolution
- Class synergy discovery  
- Map-specific tactical learning
- Counter-strategy development

## 🏗️ Project Structure

```
Topdown_shooter/
├── main.py                 # Game entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── game.py            # Main game controller
│   ├── entities/
│   │   ├── player_class.py    # Base player class definitions
│   │   ├── ai_player.py       # AI-enhanced player with learning
│   │   └── team.py            # Team management and coordination
│   ├── ai/
│   │   └── learning_agent.py  # Neural network and Q-learning implementation
│   ├── ui/
│   │   └── class_selector.py  # Class selection interface
│   └── utils/
│       └── map_generator.py   # Random battlefield generation
└── models/                # AI model storage (created automatically)
```

## 🎨 Customization

### Adding New Classes
1. Add new `ClassType` in `player_class.py`
2. Define stats in `CLASS_STATS` dictionary
3. Add color in `CLASS_COLORS`
4. Implement class-specific AI behavior in `ai_player.py`

### Modifying AI Learning
- Adjust learning rate in `LearningAgent.__init__()`
- Change network architecture in `SimpleQNetwork`
- Modify reward function in `calculate_reward()`
- Add new state features in `get_state()`

### Map Customization  
- Add new map types in `MapGenerator.generate_map()`
- Modify obstacle generation algorithms
- Adjust spawn point strategies

## 🐛 Troubleshooting

### Common Issues

**"No module named 'pygame'"**
```bash
pip install pygame
```

**"ImportError: numpy"**
```bash 
pip install numpy
```

**Poor AI Performance**
- AI needs time to learn - run multiple battles
- Check epsilon value (should decrease over time)
- Verify model files are being saved/loaded

**Game Runs Too Fast/Slow**
- Adjust `FPS` constant in `Game` class
- Modify `dt` (delta time) values for slower/faster learning

## 📈 Future Enhancements

### Planned Features
- [ ] Tournament mode with bracket elimination
- [ ] Real-time strategy adjustment interface
- [ ] Advanced neural network architectures (CNN, LSTM)
- [ ] Genetic algorithm for team composition optimization
- [ ] Multiplayer support with human players
- [ ] 3D graphics upgrade
- [ ] Map editor for custom battlefields

### AI Improvements
- [ ] Multi-agent reinforcement learning
- [ ] Hierarchical decision making
- [ ] Communication between team members
- [ ] Meta-learning across different games
- [ ] Adversarial training between teams

## 🤝 Contributing

This game demonstrates real machine learning in action. The AI learning is **not faked** - each agent uses genuine neural networks and reinforcement learning algorithms.

Feel free to contribute improvements to:
- AI learning algorithms
- New player classes
- Map generation
- UI enhancements
- Performance optimizations

## 📜 License

This project is open source. Feel free to modify and distribute.

---

**Note:** This implementation features genuine AI learning through neural networks and reinforcement learning. The AI agents will actually improve their performance over time through experience, making each battle unique and educational!