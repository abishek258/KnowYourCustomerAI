import { useEffect, useMemo, useRef, useState } from 'react'
import HgsLogo from './assets/HgsLogo.svg'
import { Document, Page, pdfjs } from 'react-pdf'
import { processDocument } from './api'

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`

export default function App() {
  const [file, setFile] = useState(null)
  const [results, setResults] = useState(null)
  const [pageNumber, setPageNumber] = useState(1)
  const [numPages, setNumPages] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fileUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])
  const containerRef = useRef(null)

  const onFileChange = (e) => {
    const f = e.target.files?.[0]
    setFile(f || null)
    setResults(null)
    setPageNumber(1)
    setError('')
  }

  const onProcess = async () => {
    if (!file) return
    try {
      setLoading(true)
      setError('')
      const data = await processDocument(file, 'custom')
      
      // Convert new API response to old format for UI compatibility
      const convertedResults = {
        pages: [
          {
            page_number: 0,
            classification: 'ncb-kyc-form',
            confidence: data.summary.average_confidence,
            extractor_used: data.summary.extractor_used,
            entities: convertFieldsToEntities(data.extracted_information.page_one || {}),
            dimension: null
          },
          {
            page_number: 1,
            classification: 'ncb-kyc-form',
            confidence: data.summary.average_confidence,
            extractor_used: data.summary.extractor_used,
            entities: convertFieldsToEntities(data.extracted_information.page_two || {}),
            dimension: null
          }
        ]
      }
      
      setResults(convertedResults)
    } catch (e) {
      setError(e?.response?.data?.error?.message || e.message)
    } finally {
      setLoading(false)
    }
  }

  const convertFieldsToEntities = (fields) => {
    return Object.entries(fields)
      .filter(([key, value]) => value && value.value)
      .map(([fieldName, fieldData]) => ({
        type: fieldName,
        value: fieldData.value,
        raw_value: fieldData.value,
        confidence: fieldData.confidence,
        bounding_boxes: fieldData.bounding_box ? [{
          page: fieldData.page,
          x: fieldData.bounding_box.x,
          y: fieldData.bounding_box.y,
          width: fieldData.bounding_box.width,
          height: fieldData.bounding_box.height,
          vertices: [
            { x: fieldData.bounding_box.x, y: fieldData.bounding_box.y },
            { x: fieldData.bounding_box.x + fieldData.bounding_box.width, y: fieldData.bounding_box.y + fieldData.bounding_box.height }
          ]
        }] : []
      }))
  }

  const entitiesForPage = () => {
    if (!results?.pages) return []
    const idx = pageNumber - 1
    const page = results.pages.find(p => p.page_number === idx)
    return page?.entities || []
  }

  const boxesForPage = () => {
    const ents = entitiesForPage()
    const boxes = []
    ents.forEach(ent => {
      if (ent.bounding_boxes) {
        ent.bounding_boxes.forEach(b => {
          if (b.page === (pageNumber - 1)) boxes.push({ ...b, __label: ent.type, __value: ent.value || ent.raw_value })
        })
      }
    })
    return boxes
  }

  const pageDim = () => {
    const idx = pageNumber - 1
    return results?.pages?.find(p => p.page_number === idx)?.dimension || null
  }

  // Basic design tokens
  const colors = { 
    bg: '#0f172a', // dark blue
    panel: '#0b1220',
    border: '#1f2b46',
    text: '#e5e7eb',
    accent: '#3b82f6',
  }

  const cardStyle = { background: colors.panel, border: `1px solid ${colors.border}`, borderRadius: 12, padding: 12 }
  const tableStyle = { width: '100%', borderCollapse: 'separate', borderSpacing: '0 6px' }
  const thStyle = { textAlign: 'left', padding: '8px 12px', color: '#aab3c5', borderBottom: `1px solid ${colors.border}` }
  const tdStyle = { padding: '10px 12px', background: '#0d162a', borderTop: `1px solid ${colors.border}`, borderBottom: `1px solid ${colors.border}` }
  const buttonStyle = {
    borderRadius: 10,
    padding: '10px 14px',
    background: colors.accent,
    border: 'none',
    color: 'white',
    cursor: 'pointer',
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: colors.bg, color: colors.text }}>
      {/* Sidebar */}
      <aside style={{ width: 280, borderRight: `1px solid ${colors.border}`, padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <img src={HgsLogo} alt="Logo" style={{ width: 140, height: 'auto' }} />
        </div>
        {/* Files title removed per request */}
        <div style={{ ...cardStyle }}>
          <label htmlFor="file-input" style={{ display: 'block', fontSize: 12, color: '#aab3c5', marginBottom: 8 }}>Upload document</label>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', width: '100%' }}>
            <input id="file-input" type="file" accept=".pdf,.png,.jpg,.jpeg,.tiff" onChange={onFileChange} style={{ width: '100%', padding: 10, borderRadius: 10, border: `1px solid ${colors.border}`, background: '#0b1324', color: colors.text }} />
          </div>
          <div style={{ marginTop: 12 }}>
            <button onClick={onProcess} disabled={!file || loading} style={{ ...buttonStyle, width: '100%' }}>
              {loading ? 'Processing…' : 'Process'}
            </button>
            {loading && (
              <div style={{ marginTop: 8, height: 8, background: '#0b1324', borderRadius: 8, overflow: 'hidden' }}>
                <div style={{ width: '60%', height: '100%', background: colors.accent, animation: 'progress 1.2s infinite ease-in-out' }} />
              </div>
            )}
          </div>
        </div>
        {error && <div style={{ color: '#ef4444', marginTop: 8, wordBreak: 'break-word' }}>{error}</div>}
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, padding: 20, display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 20 }}>
        {/* Left: Document Visualization */}
        <section style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <h3 style={{ margin: 0 }}>Document Visualization</h3>
            {numPages > 0 && (
              <div>
                <button style={{ ...buttonStyle, background: '#1f2b46' }} disabled={pageNumber <= 1} onClick={() => setPageNumber(p => Math.max(1, p - 1))}>Prev</button>
                <span style={{ margin: '0 8px' }}>Page {pageNumber} of {numPages}</span>
                <button style={{ ...buttonStyle, background: '#1f2b46' }} disabled={pageNumber >= numPages} onClick={() => setPageNumber(p => Math.min(numPages, p + 1))}>Next</button>
              </div>
            )}
          </div>

          <div ref={containerRef} style={{ position: 'relative', width: '100%', border: `1px solid ${colors.border}`, background: '#0b1324', borderRadius: 10 }}>
            {fileUrl && (
              <Document file={fileUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)} loading={<div>Loading PDF...</div>}>
                <Page pageNumber={pageNumber} renderTextLayer={false} renderAnnotationLayer={false} />
              </Document>
            )}
            {fileUrl && <OverlayHost pageNumber={pageNumber} boxes={boxesForPage()} pageDim={pageDim()} />}
          </div>
        </section>

        {/* Right: tables stacked like the reference UI */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={cardStyle}>
            <h3 style={{ marginTop: 0 }}>Document Classification</h3>
          <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
              <thead>
                <tr>
                    <th style={thStyle}>Page</th>
                    <th style={thStyle}>Document Type</th>
                    <th style={thStyle}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {results?.pages?.map((p) => (
                  <tr key={p.page_number}>
                      <td style={tdStyle}>{p.page_number + 1}</td>
                      <td style={tdStyle}>{p.classification}</td>
                      <td style={tdStyle}>{p.confidence?.toFixed?.(2) ?? ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>

          <div style={{ ...cardStyle, flex: 1 }}>
            <h3 style={{ marginTop: 0 }}>Extracted Information</h3>
            <div style={{ overflowX: 'auto', maxHeight: 420 }}>
              <table style={tableStyle}>
              <thead>
                <tr>
                    <th style={thStyle}>Page</th>
                    <th style={thStyle}>Extractor</th>
                    <th style={thStyle}>Entity Type</th>
                    <th style={thStyle}>Entity Value</th>
                </tr>
              </thead>
              <tbody>
                {results?.pages?.flatMap((p) => (
                  (p.entities || []).map((e, idx) => (
                    <tr key={`${p.page_number}-${idx}`}>
                        <td style={tdStyle}>{p.page_number + 1}</td>
                        <td style={tdStyle}>{p.extractor_used || ''}</td>
                        <td style={tdStyle}>{(e.type || '').replaceAll('-', ' ').replaceAll('_',' ')}</td>
                        <td style={tdStyle}>{e.value || e.raw_value || ''}</td>
                    </tr>
                  ))
                ))}
              </tbody>
            </table>
          </div>
        </div>
        </section>
      </main>
      <style>
        {`
        @keyframes progress { 0%{transform: translateX(-60%)} 100%{transform: translateX(140%)} }
        html, body, #root { margin: 0; }
        /* Custom scrollbars for panels */
        div::-webkit-scrollbar { width: 10px; height: 10px; }
        div::-webkit-scrollbar-track { background: #0b1324; border-radius: 8px; }
        div::-webkit-scrollbar-thumb { background: #1f2b46; border-radius: 8px; }
        div::-webkit-scrollbar-thumb:hover { background: #2a3a62; }
        `}
      </style>
    </div>
  )
}

function OverlayHost({ pageNumber, boxes, pageDim }) {
  // Find the canvas for the current react-pdf page and align SVG on top
  const [dims, setDims] = useState({ w: 0, h: 0 })

  useEffect(() => {
    const updateDims = () => {
      // Prefer selecting by react-pdf structure to avoid aria-label differences
      const selector = `div.react-pdf__Page[data-page-number="${pageNumber}"] canvas.react-pdf__Page__canvas`
      const canv = document.querySelector(selector) || document.querySelector('.react-pdf__Page__canvas')
      if (canv) {
        const w = canv.clientWidth || canv.width
        const h = canv.clientHeight || canv.height
        if (w && h && (w !== dims.w || h !== dims.h)) setDims({ w, h })
      }
    }
    updateDims()
    const id = setInterval(updateDims, 150)
    return () => clearInterval(id)
  }, [pageNumber])

  if (!dims.w || !dims.h) return null

  return (
    <svg width={dims.w} height={dims.h} style={{ position: 'absolute', top: 0, left: 0, zIndex: 2, pointerEvents: 'none' }}>
      {boxes.map((b, i) => {
        // Support two shapes:
        // 1) absolute pixel coords (page coordinate space), optionally with page dimensions
        // 2) normalized 0..1 coords (x,y,width,height) or vertices
        let x = 0, y = 0, w = 0, h = 0
        if (Array.isArray(b.vertices) && b.vertices.length >= 2) {
          const xs = b.vertices.map(v => v.x)
          const ys = b.vertices.map(v => v.y)
          let x0 = Math.min(...xs), y0 = Math.min(...ys)
          let x1 = Math.max(...xs), y1 = Math.max(...ys)
          // If coordinates look like page-pixels and we have pageDim, scale to canvas pixels
          if (pageDim && Math.max(x1, y1) > 1.5) {
            const sx = dims.w / Math.max(1, pageDim.width)
            const sy = dims.h / Math.max(1, pageDim.height)
            x0 *= sx; x1 *= sx
            y0 *= sy; y1 *= sy
          } else if (Math.max(x1, y1) <= 1.5) {
            // normalized 0..1
            x0 *= dims.w; x1 *= dims.w
            y0 *= dims.h; y1 *= dims.h
          }
          x = x0; y = y0; w = x1 - x0; h = y1 - y0
        } else if (typeof b.x === 'number' && typeof b.y === 'number') {
          if (pageDim && Math.max(b.x + (b.width||0), b.y + (b.height||0)) > 1.5) {
            // absolute page pixels → canvas pixels
            const sx = dims.w / Math.max(1, pageDim.width)
            const sy = dims.h / Math.max(1, pageDim.height)
            x = b.x * sx
            y = b.y * sy
            w = (b.width || 0) * sx
            h = (b.height || 0) * sy
          } else {
            // normalized 0..1
            const norm = (v) => Math.max(0, Math.min(1, v))
            x = norm(b.x) * dims.w
            y = norm(b.y) * dims.h
            w = norm(b.width || 0) * dims.w
            h = norm(b.height || 0) * dims.h
          }
        } else {
          return null
        }
        return (
          <g key={i}>
            <rect x={x} y={y} width={w} height={h} stroke="#ff6b6b" fill="none" strokeWidth={2} />
            {b.__label && (
              <text x={x} y={Math.max(10, y - 4)} fill="#ff6b6b" fontSize="5" fontFamily="sans-serif" paintOrder="stroke">
                {b.__label}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}


