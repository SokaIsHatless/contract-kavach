"use client";

import { useEffect, useRef, useState } from "react";

const SEVERITY_CLASS = {
  critical: "bg-red-100 text-red-800 px-2 py-0.5 rounded text-xs font-bold mr-2",
  high: "bg-orange-100 text-orange-800 px-2 py-0.5 rounded text-xs font-bold mr-2",
  medium: "bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded text-xs font-bold mr-2",
};

export default function Home() {
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [flags, setFlags] = useState(null);
  const [error, setError] = useState(null);
  const [voices, setVoices] = useState([]);
  const [sampleLabel, setSampleLabel] = useState(null);

  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    function loadVoices() {
      setVoices(window.speechSynthesis.getVoices());
    }
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  function speakHindi(text) {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "hi-IN";
    const hindiVoice = voices.find((v) => v.lang.startsWith("hi"));
    if (hindiVoice) utterance.voice = hindiVoice;
    window.speechSynthesis.speak(utterance);
  }

  async function loadSample(name, label) {
    setLoading(true);
    setFlags(null);
    setError(null);
    setFiles([]);
    setSampleLabel(label);
    const res = await fetch(`http://localhost:8000/api/samples/${name}`);
    if (!res.ok) {
      setError(`Server error: ${res.status}`);
      setLoading(false);
      return;
    }
    const data = await res.json();
    setFlags(data.flags);
    setLoading(false);
  }

  function handleDrop(e) {
    e.preventDefault();
    const dropped = [...e.dataTransfer.files].filter((f) => f.type.startsWith("image/") || f.type === "application/pdf");
    if (dropped.length) setFiles(dropped);
  }

  async function submit() {
    setLoading(true);
    setFlags(null);
    setError(null);
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    const res = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: form });
    if (!res.ok) {
      setError(`Server error: ${res.status}`);
      setLoading(false);
      return;
    }
    const data = await res.json();
    setFlags(data.flags);
    setLoading(false);
  }

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-1">ContractKavach</h1>
      <p className="text-gray-500 text-sm mb-6">Upload your contract images to check for red flags.</p>

      <p className="text-sm text-gray-500 mb-2">Try a sample contract:</p>
      <div className="flex gap-2 mb-4">
        <button onClick={() => loadSample("worst_case", "worst_case.pdf")} className="flex-1 py-2 border rounded text-sm hover:bg-gray-50">🔴 Worst Case (UAE domestic)</button>
        <button onClick={() => loadSample("sneaky", "sneaky.pdf")} className="flex-1 py-2 border rounded text-sm hover:bg-gray-50">🟡 Sneaky (Saudi construction)</button>
        <button onClick={() => loadSample("mostly_fair", "mostly_fair.pdf")} className="flex-1 py-2 border rounded text-sm hover:bg-gray-50">🟢 Mostly Fair (Qatar domestic)</button>
      </div>

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { setSampleLabel(null); handleDrop(e); }}
        onClick={() => inputRef.current.click()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors mb-4"
      >
        {sampleLabel && !files.length ? (
          <p className="text-sm text-gray-700">Sample: {sampleLabel}</p>
        ) : files.length > 0 ? (
          <ul className="text-sm text-gray-700">
            {files.map((f) => <li key={f.name}>{f.name}</li>)}
          </ul>
        ) : (
          <p className="text-gray-400">Drop contract files here (images or PDFs), or click to select</p>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept="image/*,application/pdf"
        className="hidden"
        onChange={(e) => { setSampleLabel(null); setFiles([...e.target.files]); }}
      />

      <button
        onClick={submit}
        disabled={!files.length || loading}
        className="w-full bg-blue-600 text-white py-2 rounded font-semibold disabled:opacity-40 hover:bg-blue-700 transition-colors mb-6"
      >
        {loading ? "Analyzing…" : "Analyze Contract"}
      </button>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      {flags && flags.length === 0 && (
        <p className="text-green-600 font-medium">No red flags detected.</p>
      )}

      {flags && flags.length > 0 && (
        <div>
          <h2 className="font-semibold text-lg mb-3">{flags.length} Red Flag{flags.length > 1 ? "s" : ""} Found</h2>

          <button
            onClick={() => {
              const critical = flags.filter((f) => f.severity === "critical");
              if (!critical.length) return;
              const combined = critical.map((f) => `${f.title_hi}. ${f.explanation_hi}`).join(". ");
              speakHindi(combined);
            }}
            className="w-full bg-indigo-600 text-white py-2 rounded mb-4 hover:bg-indigo-700 transition-colors"
          >
            🔊 Listen to top critical flags in Hindi
          </button>

          {flags.map((flag) => (
            <div key={flag.rule_id} className="border rounded-lg p-4 mb-3">
              <div className="flex items-center mb-2">
                <span className={SEVERITY_CLASS[flag.severity]}>{flag.severity.toUpperCase()}</span>
                <span className="font-semibold text-sm">{flag.title_en}</span>
                <button
                  onClick={() => speakHindi(`${flag.title_hi}. ${flag.explanation_hi}`)}
                  className="ml-auto text-xs border border-gray-300 rounded px-2 py-0.5 hover:bg-gray-100"
                >
                  🔊 Listen
                </button>
              </div>
              <p className="text-gray-500 text-sm mb-2">{flag.title_hi}</p>
              <p className="text-sm text-gray-700">{flag.explanation_en}</p>
              <p className="text-sm text-gray-500 mt-1">{flag.explanation_hi}</p>
              {flag.evidence_quote && (
                <blockquote className="mt-2 border-l-2 border-gray-300 pl-3 text-xs text-gray-500 italic">
                  {flag.evidence_quote} {flag.evidence_page ? `(p.${flag.evidence_page})` : ""}
                </blockquote>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
