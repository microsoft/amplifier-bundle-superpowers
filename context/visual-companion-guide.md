# Visual Companion Guide

Browser-based visual brainstorming companion for showing mockups, diagrams, and interactive option screens during conversations.

## When to Use

Make the decision per-question, not per-session. Ask: **would seeing this be more useful than reading it?**

**Use the browser** when the content is inherently visual:

- **UI mockups** — wireframes, layouts, navigation structures, component arrangements
- **Architecture diagrams** — system components, data flow, service relationships
- **Side-by-side visual comparisons** — two layouts, two color directions, two design approaches
- **Design polish questions** — when the answer is about look and feel, not concept
- **Spatial relationships** — state machines, flowcharts, entity relationships rendered visually

**Use the terminal** when the content is text or tabular:

- **Requirements and scope** — "what does X mean?", "which features should we include?"
- **Conceptual choices** — picking between approaches described in words
- **Tradeoff lists** — pros/cons, comparison tables
- **Technical decisions** — API design, data modeling, architectural approach selection
- **Clarifying questions** — anything where the answer is words, not a visual preference

A question *about* a UI topic is not automatically a visual question. "What kind of navigation do you want?" is conceptual — use the terminal. "Which of these navigation layouts feels right?" is visual — use the browser.

## Supplementary Visual Tools

The visual companion server handles interactive HTML content in the browser. Two additional Amplifier tools can complement it for specific visual needs:

- **`nano-banana`** — Generate images, UI mockups, or visual designs directly as PNG/JPG. Useful when you want a richer visual output than HTML allows, or when generating a reference image to iterate from. Can be used alongside the server (write the generated image into an `<img>` tag in your HTML content) or independently.

- **`dot_graph`** — Render DOT/Graphviz diagrams to SVG or PNG. When you have architectural relationships or system diagrams to show, use `dot_graph` to render the diagram, then display it via the browser server in an `<img>` tag or inline SVG.

Neither tool is required. Use them when they add value that pure HTML cannot provide easily.

## How It Works

The server watches a directory for HTML files and serves the newest one to the browser. You write HTML content to `screen_dir`, the user sees it and can click to select options. Selections are recorded to `state_dir/events` as JSONL, which you read on your next turn.

**Content fragments vs full documents:** If your HTML starts with `<!DOCTYPE` or `<html`, the server serves it as-is and injects only the helper script. Otherwise, the server wraps your content in the frame template — adding the header, CSS theme, selection indicator, and all interactive infrastructure. **Write content fragments by default.** Only write full documents when you need complete control over the page.

## Prerequisites

The brainstorm server requires **Node.js** to run. Before starting a session, verify Node.js is available:

```bash
node --version
```

If Node.js is not installed, the server cannot start. In that case, fall back to presenting choices in the terminal using markdown tables or numbered lists. The conversation can still proceed without the visual server — you simply lose the interactive browser component.

On most development machines and Amplifier container environments, Node.js will be available. If working in a custom environment, install it before attempting to use this guide.

## Starting a Session

Launch the server using the `bash` tool with `run_in_background=true` so it persists across conversation turns:

```
bash tool call:
  command: "scripts/start-server.sh --project-dir /path/to/project"
  run_in_background: true
```

The server writes startup JSON to `$STATE_DIR/server-info`. Read that file on the next turn to get the URL and port:

```json
{
  "type": "server-started",
  "port": 52341,
  "url": "http://localhost:52341/?key=9f2c...redacted...",
  "screen_dir": "/path/to/project/.superpowers/brainstorm/12345-1706000000/content",
  "state_dir": "/path/to/project/.superpowers/brainstorm/12345-1706000000/state",
  "idle_timeout_ms": 14400000
}
```

Save `screen_dir` and `state_dir`. Tell the user to open the URL **exactly as given, including the `?key=...` query string** — this is a per-session authentication token, not decoration. The server rejects every request (HTTP and WebSocket) that doesn't present it, so a truncated or reconstructed URL will show a "Session key required" page instead of the companion. The first load bounces through a bootstrap redirect that stashes the key in the browser tab's session storage and a cookie, so subsequent reloads and navigation within that tab don't need the key in the visible URL.

**Persistent sessions:** Pass `--project-dir` pointing to the project root so mockup files are saved to `.superpowers/brainstorm/` and survive server restarts. Without it, files go to `/tmp` and are cleaned up automatically. Remind the user to add `.superpowers/` to their `.gitignore` if it isn't already there — these are working files, not source artifacts.

**Remote and containerized environments:** If the URL is not reachable from the browser (common in remote or containerized setups), bind to a non-loopback host:

```
bash tool call:
  command: "scripts/start-server.sh --project-dir /path/to/project --host 0.0.0.0"
  run_in_background: true
```

Use `--url-host` to control what hostname appears in the returned URL JSON if the container hostname differs from what the browser should use.

## The Loop

1. **Check server is alive, then write HTML** to a new file in `screen_dir`:
   - Before each write, verify `$STATE_DIR/server-info` exists. If it doesn't (or `$STATE_DIR/server-stopped` exists), restart the server with `start-server.sh` before continuing. The server exits automatically after 4 hours of inactivity.
   - Use semantic filenames: `platform.html`, `layout.html`, `color-direction.html`
   - **Never reuse filenames** — each screen gets a fresh file
   - Write files with the `write_file` tool — never use shell heredoc (it dumps noise)
   - The server automatically serves the newest file by modification time

2. **Tell the user what to expect, then end your turn:**
   - Remind them of the URL on every step, not just the first
   - Give a brief text summary: "Showing 3 layout options for the main navigation"
   - Ask them to respond in the terminal: "Take a look and let me know what you think. Click to select if you'd like."

3. **On your next turn** — after the user responds in the terminal:
   - Read `$STATE_DIR/events` if it exists — this contains browser interactions as JSONL
   - Merge with the user's terminal text to form a complete picture
   - Terminal feedback is primary; `events` provides structured interaction data

4. **Iterate or advance** — if feedback changes the current screen, write a new file (e.g., `layout-v2.html`). Only move to the next question once the current step is settled.

5. **Unload when returning to terminal** — when the next step doesn't need the browser (clarifying question, tradeoff discussion), push a waiting screen to clear stale content:

   ```html
   <!-- filename: waiting.html (or waiting-2.html) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```

   This prevents the user from staring at a resolved choice while the conversation has moved on.

6. **Repeat** until the brainstorm is complete, then clean up.

## Writing Content Fragments

Write just the HTML content that goes inside the page body. The server wraps it in the frame template automatically (header, theme CSS, selection indicator, and all interactive infrastructure). No `<html>`, no `<head>`, no `<script>` tags needed.

**Minimal example:**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content area</p>
    </div>
  </div>
</div>
```

That's it. The server provides everything else.

## CSS Classes Available

The frame template provides these CSS classes for content fragments:

### Options (A/B/C Choices)

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### Multi-Select Options

Add `data-multiselect` to the container to let users select multiple options. Each click toggles the item. The indicator bar shows the running count.

```html
<div class="options" data-multiselect>
  <!-- same option markup — users can select and deselect multiple items -->
</div>
```

### Cards (Visual Designs)

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup content --></div>
    <div class="card-body">
      <h3>Name</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### Mockup Container

```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup HTML --></div>
</div>
```

### Split View (Side-by-Side)

```html
<div class="split">
  <div class="mockup"><!-- left panel --></div>
  <div class="mockup"><!-- right panel --></div>
</div>
```

### Pros/Cons

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>Benefit</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>Drawback</li></ul></div>
</div>
```

### Mock Elements (Wireframe Building Blocks)

```html
<div class="mock-nav">Logo | Home | About | Contact</div>
<div style="display: flex;">
  <div class="mock-sidebar">Navigation</div>
  <div class="mock-content">Main content area</div>
</div>
<button class="mock-button">Action Button</button>
<input class="mock-input" placeholder="Input field">
<div class="placeholder">Placeholder area</div>
```

### Typography and Sections

- `h2` — page title
- `h3` — section heading
- `.subtitle` — secondary text below title
- `.section` — content block with bottom margin
- `.label` — small uppercase label text

## Browser Events Format

When the user clicks options in the browser, their interactions are recorded to `$STATE_DIR/events` as JSONL (one JSON object per line). The file is cleared automatically when you push a new screen.

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

The full event stream shows the user's exploration path — they may click multiple options before settling. The last `choice` event is typically the final selection, but patterns of clicks can reveal hesitation or preferences worth asking about.

If `$STATE_DIR/events` doesn't exist, the user didn't interact with the browser — use only their terminal response.

## Design Tips

- **Scale fidelity to the question** — wireframes for layout questions, polish for polish questions
- **Frame the question on every page** — "Which layout feels more professional?" not just "Pick one"
- **Iterate before advancing** — if feedback changes the current screen, write a new version before moving on
- **2–4 options max** per screen — more choices create decision fatigue
- **Use real content when it matters** — for a portfolio site, use actual content. Placeholder text obscures design issues.
- **Keep mockups simple** — focus on structure and layout, not pixel-perfect detail

## File Naming

- Use semantic names that describe the decision: `platform.html`, `visual-style.html`, `layout.html`
- **Never reuse filenames** — each screen must be a distinct file
- For iterations: append a version suffix — `layout-v2.html`, `layout-v3.html`
- The server always serves the newest file by modification time

## Cleaning Up

Stop the server when the session is complete:

```
bash tool call:
  command: "scripts/stop-server.sh $SESSION_DIR"
```

If the session used `--project-dir`, mockup files persist in `.superpowers/brainstorm/` for later reference. Sessions without `--project-dir` use `/tmp` and files are removed on stop.

## Reference

Inspect the server infrastructure files via `@superpowers:` bundle paths:

- **Frame template** (full CSS reference): `@superpowers:scripts/frame-template.html`
- **Helper script** (client-side interaction): `@superpowers:scripts/helper.js`
- **Server** (Node.js implementation): `@superpowers:scripts/server.cjs`
- **Start script**: `@superpowers:scripts/start-server.sh`
- **Stop script**: `@superpowers:scripts/stop-server.sh`

Use `read_file` with these `@superpowers:` paths to inspect the implementation when debugging or extending the server.
