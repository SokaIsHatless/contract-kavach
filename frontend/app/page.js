"use client";

import { useRef, useState } from "react";

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

  function handleDrop(e) {
    e.preventDefault();
    const dropped = [...e.dataTransfer.files].filter((f) => f.type.startsWith("image/"));
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

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors mb-4"
      >
        {files.length > 0 ? (
          <ul className="text-sm text-gray-700">
            {files.map((f) => <li key={f.name}>{f.name}</li>)}
          </ul>
        ) : (
          <p className="text-gray-400">Drop contract images here, or click to select</p>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept="image/*"
        className="hidden"
        onChange={(e) => setFiles([...e.target.files])}
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
          {flags.map((flag) => (
            <div key={flag.rule_id} className="border rounded-lg p-4 mb-3">
              <div className="flex items-center mb-2">
                <span className={SEVERITY_CLASS[flag.severity]}>{flag.severity.toUpperCase()}</span>
                <span className="font-semibold text-sm">{flag.title_en}</span>
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
