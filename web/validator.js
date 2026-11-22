const browserMode = document.querySelector('meta[name="draft-validator"]').content === "browser";
const runtimeUrl = "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/";
let pythonReady;

async function browserValidator() {
  const [{ loadPyodide }, ...sources] = await Promise.all([
    import(`${runtimeUrl}pyodide.mjs`),
    ...["draft.py", "run.py"].map(async file => {
      const response = await fetch(`./${file}`);
      if (!response.ok) throw new Error(`Could not load ${file}.`);
      return [file, await response.text()];
    }),
  ]);
  const python = await loadPyodide({ indexURL: runtimeUrl });
  for (const [file, source] of sources) python.FS.writeFile(`/home/pyodide/${file}`, source);
  return python.runPython(`
import json
import sys
sys.path.insert(0, "/home/pyodide")
from run import board_for

def validate(raw):
    if len(raw.encode()) > 64000:
        return json.dumps({"error": "Choose a series JSON file under 64 KB."})
    try:
        return json.dumps(board_for(json.loads(raw)))
    except (KeyError, ValueError) as error:
        return json.dumps({"error": str(error)})

validate
`);
}

export async function validateDraft(draft) {
  const body = JSON.stringify(draft);
  let result;
  if (browserMode) {
    pythonReady ??= browserValidator().catch(error => {
      pythonReady = undefined;
      throw error;
    });
    const validate = await pythonReady;
    result = JSON.parse(validate(body));
  } else {
    const response = await fetch("./draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    if (!response.ok && !response.headers.get("Content-Type")?.startsWith("application/json")) {
      throw new Error(`Cannot validate the draft (HTTP ${response.status}).`);
    }
    result = await response.json();
  }
  if (result.error) throw new Error(result.error);
  return result;
}
