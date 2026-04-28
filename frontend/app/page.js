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
  const [sourceId, setSourceId] = useState(null);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedFlag, setSelectedFlag] = useState(null);

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
    setSelectedFlag(null);
    setSampleLabel(label);
    const res = await fetch(`/api/samples/${name}`);
    if (!res.ok) {
      setError(`Server error: ${res.status}`);
      setLoading(false);
      return;
    }
    const data = await res.json();
    setFlags(data.flags);
    setSourceId(data.source_id);
    setTotalPages(data.total_pages);
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
    setSelectedFlag(null);
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    const res = await fetch("/api/analyze", { method: "POST", body: form });
    if (!res.ok) {
      setError(`Server error: ${res.status}`);
      setLoading(false);
      return;
    }
    const data = await res.json();
    setFlags(data.flags);
    setSourceId(data.source_id);
    setTotalPages(data.total_pages);
    setLoading(false);
  }

  const pageNum = selectedFlag?.evidence_page || 1;

  return (
    <main className="max-w-6xl mx-auto p-6">
      <div className="h-1 bg-gradient-to-r from-orange-500 via-white to-green-600 -mx-6 -mt-6 mb-6"></div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-1">Contract<span className="text-orange-600">Kavach</span></h1>
        <p className="text-gray-600 text-sm italic">कांट्रैक्ट कवच — Your contract, decoded.</p>
        <p className="text-gray-500 text-xs mt-1">For Indian migrant workers signing Gulf employment contracts. AI reads what they can't.</p>
      </div>

      <p className="text-sm text-gray-500 mb-2">Try a sample contract:</p>
      <div className="flex gap-2 mb-4">
        <button onClick={() => loadSample("worst_case", "worst_case.pdf")} className="flex-1 py-2 bg-red-50 border-2 border-red-200 rounded text-sm hover:bg-red-100 hover:border-red-300 transition-colors font-medium text-red-900">
          🔴 Worst Case <span className="text-xs font-normal text-red-700">(UAE domestic)</span>
        </button>
        <button onClick={() => loadSample("sneaky", "sneaky.pdf")} className="flex-1 py-2 bg-amber-50 border-2 border-amber-200 rounded text-sm hover:bg-amber-100 hover:border-amber-300 transition-colors font-medium text-amber-900">
          🟡 Sneaky <span className="text-xs font-normal text-amber-700">(Saudi construction)</span>
        </button>
        <button onClick={() => loadSample("mostly_fair", "mostly_fair.pdf")} className="flex-1 py-2 bg-green-50 border-2 border-green-200 rounded text-sm hover:bg-green-100 hover:border-green-300 transition-colors font-medium text-green-900">
          🟢 Mostly Fair <span className="text-xs font-normal text-green-700">(Qatar domestic)</span>
        </button>
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

      {!flags && !loading && !error && (
        <div className="text-center text-gray-400 text-sm mt-8">
          Click a sample contract above, or drop your own to begin.
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center bg-gray-50 border rounded-lg min-h-[400px] mt-4">
          <div className="text-center">
            <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-gray-600 text-sm">AI is reading your contract...</p>
            <p className="text-gray-400 text-xs mt-1">Usually takes 5–10 seconds</p>
          </div>
        </div>
      )}

      {flags && flags.length === 0 && (
        <p className="text-green-600 font-medium">No red flags detected.</p>
      )}

      {flags && flags.length > 0 && (
        <div className="flex flex-col md:flex-row gap-6">

          {/* Left column — flag list */}
          <div className="md:max-w-md w-full">
            <h2 className="font-semibold text-lg mb-3">{flags.length} Red Flag{flags.length > 1 ? "s" : ""} Found</h2>

            <button
              onClick={() => {
                const critical = flags.filter((f) => f.severity === "critical");
                if (!critical.length) return;
                const combined = critical.map((f) => `${f.title_hi}. ${f.explanation_hi}`).join(". ");
                speakHindi(combined);
              }}
              className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 text-white py-2 rounded mb-4 hover:from-indigo-700 hover:to-blue-700 transition-all shadow-sm font-semibold"
            >
              🔊 Listen to top critical flags in Hindi
            </button>

            {flags.map((flag) => (
              <div
                key={flag.rule_id}
                onClick={() => setSelectedFlag(flag)}
                className={`border rounded-lg p-4 mb-3 cursor-pointer hover:bg-gray-50 transition-colors border-l-4 ${
                  flag.severity === "critical" ? "border-l-red-500" :
                  flag.severity === "high" ? "border-l-orange-500" :
                  "border-l-yellow-500"
                } ${flag.rule_id === selectedFlag?.rule_id ? "ring-2 ring-blue-400" : ""}`}
              >
                <div className="flex items-center mb-2">
                  <span className={SEVERITY_CLASS[flag.severity]}>{flag.severity.toUpperCase()}</span>
                  <span className="font-semibold text-sm">{flag.title_en}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); speakHindi(`${flag.title_hi}. ${flag.explanation_hi}`); }}
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

          {/* Right column — contract viewer */}
          {sourceId && (
            <div className="flex-1">
              <div className="sticky top-4">
                <div className="bg-gray-50 border rounded px-3 py-2 text-sm text-gray-600 mb-3">
                  📄 Page {pageNum} of {totalPages}
                  {!selectedFlag && <span className="ml-2 text-gray-400">(click a flag to jump to its page)</span>}
                </div>

                {selectedFlag?.evidence_quote && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1">Found on this page:</p>
                    <blockquote className="bg-yellow-100 border-l-4 border-yellow-500 px-3 py-2 italic text-sm text-gray-800">
                      {selectedFlag.evidence_quote}
                    </blockquote>
                  </div>
                )}

                <img
                  src={`/api/page-image/${sourceId}/${pageNum}`}
                  alt={`Contract page ${pageNum}`}
                  className="w-full border rounded shadow"
                />
              </div>
            </div>
          )}
        </div>
      )}

      <footer className="mt-12 pt-6 border-t text-xs text-gray-400 text-center">
        Built with Claude Sonnet 4.5 vision · Rules sourced from Indian Emigration Act &amp; ILO frameworks
      </footer>
    </main>
  );
}
