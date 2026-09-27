import { useEffect, useId, useState } from "react";

import { getPanchayats } from "../services/api";

export default function PanchayatSelector({
  value,
  onChange,
  label = "Panchayat",
  placeholder = "Search Panchayat",
  inputClassName = "",
}) {
  const listId = useId();
  const [query, setQuery] = useState(value || "");
  const [result, setResult] = useState({
    query: null,
    names: [],
    error: false,
    offset: 0,
    hasMore: false,
    loadingMore: false,
    loadMoreError: false,
  });
  const [open, setOpen] = useState(false);

  const matches = result.query === query ? result.names : [];
  const loading = result.query !== query;

  useEffect(() => {
    let cancelled = false;
    const timer = setTimeout(() => {
      getPanchayats(query, 50, 0)
        .then((names) => {
          if (cancelled) return;
          setResult({
            query,
            names,
            error: false,
            offset: names.length,
            hasMore: names.length === 50,
            loadingMore: false,
            loadMoreError: false,
          });
        })
        .catch(() => {
          if (!cancelled) {
            setResult({
              query,
              names: [],
              error: true,
              offset: 0,
              hasMore: false,
              loadingMore: false,
              loadMoreError: false,
            });
          }
        });
    }, 180);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query]);

  const selectPanchayat = (name) => {
    setQuery(name);
    setOpen(false);
    onChange(name);
  };

  const handleChange = (event) => {
    const nextValue = event.target.value;
    setQuery(nextValue);
  };

  const loadMore = async () => {
    const offset = result.offset;
    setResult((current) => ({ ...current, loadingMore: true, loadMoreError: false }));
    try {
      const names = await getPanchayats(query, 50, offset);
      setResult((current) => current.query !== query ? current : ({
        ...current,
        names: [...current.names, ...names],
        offset: offset + names.length,
        hasMore: names.length === 50,
        loadingMore: false,
      }));
    } catch {
      setResult((current) => current.query !== query ? current : ({
        ...current,
        loadingMore: false,
        loadMoreError: true,
      }));
    }
  };

  return (
    <div className="relative w-full">
      {label && (
        <label
          htmlFor={listId}
          className="mb-1.5 flex items-center gap-1 text-[11px] font-medium text-slate-500"
        >
          {label}
        </label>
      )}
      <input
        id={listId}
        type="search"
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls={`${listId}-options`}
        value={query}
        onChange={handleChange}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 120)}
        onKeyDown={(event) => {
          if (event.key === "Escape") setOpen(false);
        }}
        placeholder={placeholder}
        autoComplete="off"
        className={`w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 outline-none transition placeholder:font-normal placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 ${inputClassName}`}
      />
      {open && (
        <div
          id={`${listId}-options`}
          role="listbox"
          aria-label="Panchayat search results"
          className="absolute left-0 right-0 top-full z-50 mt-1 max-h-72 overflow-y-auto rounded-xl border border-slate-200 bg-white py-1 shadow-xl"
        >
          {loading ? (
            <p className="px-3 py-2.5 text-xs text-slate-500">Searching Panchayats...</p>
          ) : result.error ? (
            <p className="px-3 py-2.5 text-xs text-red-600">Panchayat search is unavailable.</p>
          ) : matches.length === 0 ? (
            <p className="px-3 py-2.5 text-xs text-slate-500">No matching Panchayats.</p>
          ) : (
            <>
              {matches.map((name) => (
                <button
                  key={name}
                  type="button"
                  role="option"
                  aria-selected={name === value}
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => selectPanchayat(name)}
                  className={`block w-full px-3 py-2 text-left text-xs transition hover:bg-emerald-50 ${name === value ? "font-semibold text-emerald-800" : "text-slate-700"}`}
                >
                  {name}
                </button>
              ))}
              {result.query === query && result.hasMore && (
                <div className="border-t border-slate-100 p-2">
                  <button
                    type="button"
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={loadMore}
                    disabled={result.loadingMore}
                    className="w-full rounded-lg px-3 py-2 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-50 disabled:text-slate-400"
                  >
                    {result.loadingMore ? "Loading Panchayats..." : `Load 50 more (${matches.length} shown)`}
                  </button>
                  {result.loadMoreError && (
                    <p className="px-2 pb-1 text-[10px] text-red-600">Could not load more results. Try again.</p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}