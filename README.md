# PERSONAL_ASSISTANT

Fully-offline, Siri-like voice assistant for macOS.

---

## Overview

PERSONAL_ASSISTANT is a desktop voice assistant that runs entirely on the local
machine. There are no cloud APIs, no telemetry, and no network calls in the hot
path of speech recognition, language modelling, or speech synthesis. Audio is
captured locally, transcribed locally, reasoned about locally, and the spoken
reply is generated locally. Once the dependencies and models are installed,
the assistant works with the network turned off.

The assistant is built around three local engines: [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
for speech-to-text, [Ollama](https://ollama.com) (default model: Mistral 7B)
for the language model, and macOS' built-in `say` command for text-to-speech
(with hooks ready for [Piper TTS](https://github.com/rhasspy/piper) if a more
natural voice is preferred). A short-term conversation memory in
`core/memory.py` keeps the last six turns so follow-up questions like "and the
second one?" resolve correctly.

The user-facing surface is a small floating window built with PySide6
(`ui/assistant_ui.py`). It pins itself to the top-right corner of the screen,
fades in while the assistant is listening / thinking / speaking, and fades out
when the conversation goes idle. The whole experience is deliberately minimal:
no menu bars, no settings panes, just a quiet rounded panel that appears,
shows the current state, and disappears.

---

## Key Features

- **Fully offline.** No cloud calls. STT, LLM, and TTS are all local
  subprocesses (`stt/transcribe.py`, `llm/ollama_client.py`, `tts/speak.py`).
- **Multi-turn context memory.** `core/memory.py` keeps a sliding window of
  the last six user/assistant turns and prepends them to each prompt
  (`core/memory.py:23`).
- **Conversational session model.** A session opens on the first user
  utterance, stays alive while the user keeps talking, and closes after
  ~25 seconds of silence or on an exit phrase
  (`core/assistant_worker.py:36`).
- **Exit-intent detection.** Phrases like "stop", "go to sleep", "bye",
  "thank you", or "shut down" end the session cleanly
  (`core/conversation.py:1`).
- **Floating macOS-native UI.** Frameless, translucent, always-on-top panel
  with fade-in / fade-out animation (`ui/assistant_ui.py:10`).
- **State signals.** The worker emits `listening`, `thinking`, `speaking`,
  and `session_ended` Qt signals so the UI can reflect the current phase
  (`core/assistant_worker.py:13`).
- **Action plugins.** A small router (`actions/router.py`) and JSON-intent
  parser (`core/intent_parser.py`) let the LLM emit structured commands such
  as `open_app` to launch macOS applications via `open -a`
  (`actions/open_app.py:3`).
- **Double-clickable launcher.** `RunAssistant.command` activates the venv
  and starts the GUI; chmod-it once and run from Finder.

---

## Architecture

```
                +--------------------+
                |    Microphone      |
                +--------------------+
                          |
                          v
              +-------------------------+
              |  stt/record.py          |
              |  (sounddevice + scipy)  |
              |  4-second WAV @ 16 kHz  |
              +-------------------------+
                          |
                          v
              +-------------------------+
              |  stt/transcribe.py      |
              |  whisper.cpp CLI        |
              |  ggml-base.en model     |
              +-------------------------+
                          |
                          v
              +-------------------------+
              |  core/conversation.py   |
              |  exit-intent check      |
              +-------------------------+
                          |
                          v
              +-------------------------+
              |  core/memory.py         |
              |  prepend last N turns   |
              +-------------------------+
                          |
                          v
              +-------------------------+        +---------------------+
              |  core/intent_parser.py  | -----> |  actions/router.py  |
              |  (optional JSON intent) |        |  open_app, sysinfo  |
              +-------------------------+        +---------------------+
                          |                                |
                          v                                |
              +-------------------------+                  |
              |  llm/ollama_client.py   | <----------------+
              |  ollama run mistral     |
              +-------------------------+
                          |
                          v
              +-------------------------+
              |  tts/speak.py           |
              |  macOS `say` (or Piper) |
              +-------------------------+
                          |
                          v
                +--------------------+
                |     Speaker        |
                +--------------------+

UI thread:  ui/assistant_ui.py  <--Qt signals--  core/assistant_worker.py
```

The worker thread (`core/assistant_worker.py`) is the orchestrator: it owns
the recording loop, the memory, and the session timer, and it emits Qt
signals that the floating UI reacts to.

---

## Tech Stack

| Layer        | Technology                              | Purpose                                                |
|--------------|------------------------------------------|--------------------------------------------------------|
| Audio input  | sounddevice + scipy.io.wavfile           | Capture 4-second 16 kHz mono WAVs from the system mic  |
| STT          | whisper.cpp + ggml-base.en               | Offline speech-to-text via the `whisper-cli` binary    |
| LLM          | Ollama (Mistral 7B by default)           | Local large language model invoked via `ollama run`    |
| Intent       | JSON prompt template                     | Optional structured-output path for action plugins     |
| Action layer | Python `subprocess` + `open -a`          | Launch macOS apps and run system queries               |
| TTS          | macOS `say` (Piper TTS-ready)            | Speak the assistant's reply                            |
| UI           | PySide6 (Qt 6)                           | Frameless, translucent, always-on-top floating panel   |
| Concurrency  | `threading.Thread` + Qt signals          | Decouple the audio loop from the GUI event loop        |
| Launcher     | `RunAssistant.command` (bash)            | Double-clickable starter that activates venv and runs  |

---

## Project Structure

```
PERSONAL_ASSISTANT/
|-- app.py                       # PySide6 entry point (floating UI)
|-- main.py                      # Minimal CLI loop (record -> STT -> LLM -> TTS)
|-- RunAssistant.command         # Double-clickable macOS launcher
|-- requirements.txt             # Python dependencies
|-- .gitignore
|-- README.md
|
|-- core/
|   |-- assistant_worker.py      # Main orchestrator (QObject + signals)
|   |-- conversation.py          # Exit-intent detection
|   |-- intent_parser.py         # JSON intent parser (LLM -> dict)
|   |-- intent_prompt.txt        # Few-shot prompt for the intent parser
|   `-- memory.py                # Sliding-window conversation memory
|
|-- stt/
|   |-- record.py                # sounddevice -> WAV
|   `-- transcribe.py            # whisper.cpp wrapper
|
|-- llm/
|   `-- ollama_client.py         # `ollama run mistral` wrapper
|
|-- tts/
|   `-- speak.py                 # macOS `say` wrapper
|
|-- actions/
|   |-- router.py                # Dispatch parsed intents
|   `-- open_app.py              # `open -a <App>` action
|
`-- ui/
    `-- assistant_ui.py          # Frameless floating QWidget
```

User-generated runtime artefacts (the `audio/` directory, the venv, downloaded
model files) are intentionally not committed; see `.gitignore` and the
**Model Setup** section below.

---

## Prerequisites

- **macOS 12+** (Apple Silicon M1 / M2 / M3 strongly recommended; whisper.cpp
  uses Apple Metal for GPU acceleration on these chips).
- **Python 3.10 or newer.**
- **Homebrew** (used for `cmake` and friends if whisper.cpp needs them).
- **Ollama** installed locally with at least one model pulled
  (`ollama pull mistral` for the default).
- **Microphone permission** granted to the terminal (or to `RunAssistant.command`)
  in `System Settings > Privacy & Security > Microphone`.

---

## Installation

```bash
git clone https://github.com/AYON-ARYAN/PERSONAL_ASSISTANT.git
cd PERSONAL_ASSISTANT

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Folder for the WAV that gets re-written each turn
mkdir -p audio
```

If you plan to launch the assistant from Finder, also run:

```bash
chmod +x RunAssistant.command
```

---

## Model Setup

The model files are deliberately **not** committed to the repo. They are
several hundred megabytes each, and the user is expected to download them
once.

### 1. Whisper.cpp (speech-to-text)

`stt/transcribe.py` expects the binary at
`whisper/whisper.cpp/build/bin/whisper-cli` and the model at
`whisper/whisper.cpp/models/ggml-base.en.bin`.

```bash
# From the project root:
mkdir -p whisper && cd whisper
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

# Download the English base model (~140 MB)
bash ./models/download-ggml-model.sh base.en

# Build (uses Metal on Apple Silicon automatically)
cmake -B build
cmake --build build --config Release

cd ../..
```

After this, `ls whisper/whisper.cpp/build/bin/whisper-cli` and
`ls whisper/whisper.cpp/models/ggml-base.en.bin` should both succeed.

### 2. Ollama (large language model)

Install Ollama from <https://ollama.com>, then pull the default model:

```bash
ollama pull mistral
```

`llm/ollama_client.py:5` shells out to `ollama run mistral`. To switch models,
change the model name there (or parameterise it). Any Ollama-served model
works as long as the binary is on `PATH`.

### 3. Piper TTS (optional, higher-quality voice)

The default `tts/speak.py` uses macOS' built-in `say`, which works out of the
box and needs no setup. If you prefer a more natural-sounding voice, download
a Piper voice model and replace `tts/speak.py` with a Piper subprocess call:

```bash
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json
```

Place both files at the project root (the `.gitignore` already excludes
`*.onnx`).

---

## Running

### From the command line (GUI)

```bash
source venv/bin/activate
python app.py
```

A small dark panel will fade in at the top-right of the screen showing
"Listening..." Speak, then wait. The panel will switch to "Thinking..." and
then to the assistant's reply while the audio plays.

### From the command line (headless / debugging)

```bash
source venv/bin/activate
python main.py
```

`main.py` runs an infinite record-transcribe-LLM-speak loop with no GUI.
Useful when iterating on the STT or LLM layer.

### From Finder

Double-click `RunAssistant.command`. The script `cd`s to its own directory,
activates `venv/`, and launches `python app.py`.

---

## Usage

The assistant is push-to-record by default: every iteration of the worker
loop captures a fixed 4-second clip (`stt/record.py:5`). There is no wake
word; you initiate a session simply by running the app and speaking. A
session stays open as long as you keep talking and closes after about
25 seconds of silence (`core/assistant_worker.py:46`) or when you say one of
the exit phrases (`core/conversation.py:1`):

> "exit", "stop", "go to sleep", "bye", "goodbye", "thank you",
> "that's all", "shut down"

Example exchanges:

```
You:        What is the time complexity of quicksort?
Assistant:  Average O(n log n), worst case O(n^2)...

You:        And the space complexity?
Assistant:  O(log n) on average due to the recursion stack...

You:        Thank you.
Assistant:  Alright, I'll stop listening.
```

The "and the space complexity?" follow-up resolves correctly because the
previous turn is in the conversation memory (`core/memory.py:23`).

---

## Module Reference

### `app.py`

PySide6 entry point. Constructs a `QApplication`, an `AssistantUI` widget,
and an `AssistantWorker`. Wires the worker's `listening` / `thinking` /
`speaking` / `session_ended` signals to the UI's state methods, then runs
the worker on a background daemon thread so the Qt event loop stays
responsive (`app.py:9`).

### `main.py`

A 21-line CLI loop with no GUI. Useful for quick smoke tests of the
STT-LLM-TTS pipeline without touching Qt.

### `core/`

- `assistant_worker.py` — the orchestrator. A `QObject` that emits Qt
  signals while running the record-transcribe-think-speak loop on its own
  thread. Owns the session lifecycle (open on first utterance, close on
  silence or exit intent) and the conversation memory.
- `conversation.py` — exit-intent detection. Pure-Python, no model
  required; just a set of trigger phrases.
- `memory.py` — `ConversationMemory`, a sliding-window of the last
  `max_turns * 2` history entries. Renders them into a system-style prompt
  that prefixes every LLM call.
- `intent_parser.py` + `intent_prompt.txt` — optional structured-output
  path. Sends a few-shot prompt that asks the LLM to emit JSON like
  `{"intent": "open_app", "app": "Safari"}`. Falls back to
  `{"intent": "chat"}` if the model returns prose.

### `stt/`

- `record.py` — captures a 4-second 16 kHz mono WAV with `sounddevice` and
  writes it via `scipy.io.wavfile`.
- `transcribe.py` — calls the whisper.cpp `whisper-cli` binary as a
  subprocess with `-nt` (no timestamps) and returns the raw transcript.

### `llm/`

- `ollama_client.py` — five-line wrapper around `ollama run mistral`. The
  prompt is piped in on stdin; the reply is read off stdout.

### `tts/`

- `speak.py` — one-line wrapper around macOS' `say` command. Synchronous;
  blocks until the audio has finished playing. Swap in Piper TTS here for a
  more natural voice.

### `actions/`

- `router.py` — dispatches a parsed intent dict to a handler. Currently
  knows `open_app`, `system_info`, and falls through to `chat`.
- `open_app.py` — `subprocess.run(["open", "-a", app_name])`.

### `ui/`

- `assistant_ui.py` — the floating panel. A frameless, translucent,
  always-on-top `QWidget` pinned to the top-right of the active screen.
  Three states (`show_listening`, `show_thinking`, `show_speaking`) drive
  the icon and the label. Fade-in / fade-out animations are 220 ms.

---

## Troubleshooting

**"command not found: ollama"** — install Ollama from <https://ollama.com>
and confirm `which ollama` returns a path. The Python wrapper
(`llm/ollama_client.py`) shells out to it directly.

**"model 'mistral' not found, try pulling it first"** — run
`ollama pull mistral`. To use a different model, edit the model name in
`llm/ollama_client.py:5`.

**Microphone permission denied** — open
`System Settings > Privacy & Security > Microphone` and tick the box next
to your terminal app (Terminal, iTerm, VS Code, or whichever you launched
the assistant from). If you launched via `RunAssistant.command`, the
permission is requested for `RunAssistant.command` itself the first time.

**`FileNotFoundError: whisper/whisper.cpp/build/bin/whisper-cli`** — the
whisper.cpp build did not run or did not finish. Re-do the steps in
**Model Setup -> Whisper.cpp**. On older macOS / x86 Macs you may need to
`brew install cmake` first.

**No audio plays** — `tts/speak.py` uses `say`. Test it standalone:
`say "hello"`. If that is silent, check the system output device.

**`ModuleNotFoundError: PySide6`** — the venv was not activated, or
`pip install -r requirements.txt` failed. Re-run both.

**Empty transcripts every time** — the audio file is being recorded but is
silent. Check the input device: `python -c "import sounddevice as sd;
print(sd.query_devices())"` and verify the default input is your
microphone.

**The UI never appears** — `ui/assistant_ui.py` deliberately does **not**
call `show()` until the first signal arrives. Speak, and it will fade in.

---

## Limitations and Future Work

- **Fixed-length recording.** Every turn is exactly 4 seconds. A real
  voice-activity-detector (VAD) would let the user talk as long as they
  need.
- **No wake word.** The app starts listening as soon as it launches.
  Integrating something like [openWakeWord](https://github.com/dscripka/openWakeWord)
  would make it always-on without burning cycles on every silent buffer.
- **Single hardcoded model name** in `llm/ollama_client.py`. Worth
  promoting to a config file or environment variable.
- **Action plugins are minimal.** `open_app` is the only real action; the
  intent parser already supports an extensible JSON schema, so adding
  things like calendar, reminders, or shell commands is mostly a matter of
  writing the handler.
- **macOS-only** by design (uses `say` and `open -a`). Porting to Linux
  would mean swapping the TTS layer (Piper or `espeak`) and the action
  layer (`xdg-open`).
- **No streaming.** The pipeline is strictly sequential: record fully,
  then transcribe fully, then LLM-generate fully, then speak fully.
  Streaming the LLM tokens into TTS would noticeably reduce perceived
  latency.

---

## License

MIT. See `LICENSE` if present, otherwise the MIT terms apply by default
for personal and educational use.
