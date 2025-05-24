# EWI Long Tone Practice Visualizer

A real-time visualization tool for EWI (Electronic Wind Instrument) players to practice long tones and musical runs with consistent velocity/breath pressure.

## Features

- **Real-time MIDI input visualization** with smooth, continuous velocity tracking
- **Continuous line graphing** that connects musical phrases without drops to zero
- **Multi-colored note tracking** - each note gets its own color for easy identification
- **Musical run support** - visualizes scales, arpeggios, and runs as flowing continuous lines
- **Real-time statistics** including mean, standard deviation, and consistency score
- **Note legend** showing which colors represent which notes
- **Debug mode** for MIDI troubleshooting and CC controller identification
- **Customizable CC controller** support (defaults to CC7 for breath control)
- **Gap-filling algorithm** that maintains visual continuity during note transitions

## Requirements

- Python 3.7+
- MIDI-compatible EWI or wind controller
- The required Python packages (see Installation)

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Connect your EWI or MIDI wind controller to your computer
2. Run the application:

```bash
python main.py
```

3. The application will automatically detect available MIDI input devices and use the first one
4. Play notes on your EWI and observe the visualization:
   - Each note is displayed with a unique color
   - The velocity graph shows your breath consistency over time
   - Musical runs appear as smooth, continuous lines that change color with each note
   - Statistics update in real-time for the currently playing note
   - A consistency score helps track your progress

## Controls

- **ESC**: Quit the application
- **D**: Toggle debug mode (shows all MIDI messages and CC values)
- **C**: Clear history and start fresh
- **1-9**: Select which CC controller to use for velocity tracking (default is CC7)

## Debug Mode

Press 'D' to enter debug mode, which displays:
- All incoming MIDI messages with timestamps
- Current CC controller values in real-time
- Ability to identify which CC your EWI uses for breath control
- MIDI channel and message type information

This is especially useful for identifying the correct CC controller if your EWI doesn't use the standard CC7 for breath control.

## Features for Different Practice Types

### Long Tones
- Hold single notes and watch the consistency line
- Aim for minimal standard deviation
- Work on maintaining steady breath pressure

### Musical Runs
- Play scales, arpeggios, or technical passages
- See continuous flow of breath control across note changes
- Each note gets its own color for easy identification
- No gaps or drops to zero during normal note transitions

### Dynamic Practice
- Practice crescendos and diminuendos
- Visual feedback on breath control smoothness
- Statistics help quantify improvement

## Practice Tips

1. **Focus on consistency**: Try to minimize the standard deviation value
2. **Aim for high scores**: Work toward consistency scores close to 100%
3. **Practice runs**: Use scales and arpeggios to work on breath continuity
4. **Use the legend**: The color-coded notes help identify problem areas
5. **Experiment with dynamics**: Practice different volume levels (pp, mp, mf, f, ff)
6. **Long tone goals**: Hold each note for at least 8-10 seconds
7. **Clear regularly**: Use 'C' to clear history when switching practice exercises

## Troubleshooting

- **No MIDI input**: Check that your EWI is connected and recognized by your system
- **Breath not responding**: Use debug mode (D) to identify the correct CC controller
- **Choppy visualization**: Try different CC controllers (1-9 keys) to find the smoothest response
- **No notes showing**: Verify your EWI is sending MIDI note data, not just CC data 