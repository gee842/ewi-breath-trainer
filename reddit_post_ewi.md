# Reddit Post for r/EWI

**Title:** I built a real-time breath consistency visualizer for EWI practice - free Python tool for long tones and runs

**Post:**

Hey EWI fam! 🎷

I've been struggling with breath consistency in my long tone practice (like many of us), so I decided to build a tool to help visualize what's actually happening with my breath control in real-time.

**What it does:**
- **Real-time velocity visualization** - see your breath pressure as a smooth line graph while you play
- **Multi-colored note tracking** - each note gets its own color so you can easily see transitions during runs and scales
- **Continuous line display** - no annoying drops to zero between notes, shows actual musical flow
- **Live statistics** - mean velocity, standard deviation, and a "consistency score" to gamify your practice
- **Musical run support** - perfect for visualizing scales, arpeggios, and technical passages
- **Debug mode** - helps identify which CC controller your EWI uses (great for troubleshooting)

**Why I built this:**
Traditional practice methods make it hard to know if you're actually improving breath consistency. This gives you immediate visual feedback - you can literally see when your breath wavers and work on smoothing it out. It's been a game-changer for my long tone practice and technical runs.

**The cool part:** Each note in a run gets its own color, so you can see exactly where your breath control breaks down during difficult passages. No more guessing!

**It's completely free and open source** - just needs Python and works with any MIDI-compatible EWI or wind controller.

Has anyone else tried visualizing their breath control practice? Would love to hear your thoughts or if you'd find something like this useful!

**Features I'm considering adding:**
- Recording/playback of practice sessions
- Target zones for breath levels
- Different visualization modes
- Export data for progress tracking

Let me know if you want to try it out - happy to share the code and help with setup!

---

*Technical notes: Uses MIDI CC data (default CC7) for breath tracking, written in Python with real-time graphing. Works on Windows/Mac/Linux.* 